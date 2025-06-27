# app/services/ml/prophet_predictor.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from prophet import Prophet
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import logging

from app.models.prediction import (
    ProphetPrediction, PredictionRequest, ForecastDataPoint,
    ModelMetrics, PredictionInsight, TrainingData, PredictionAdjustment
)

logger = logging.getLogger(__name__)

class ProphetPredictorService:
    """Service for generating financial predictions using Facebook Prophet"""
    
    def __init__(self):
        self.min_training_days = 30  # Minimum days of data needed
        self.default_confidence_interval = 0.95
    
    async def generate_prediction(
        self,
        db: AsyncIOMotorDatabase,
        student_id: ObjectId,
        request: PredictionRequest
    ) -> Optional[ProphetPrediction]:
        """Generate financial prediction using Prophet"""
        
        try:
            # 1. Validate and get training data
            training_data = await self._get_training_data(db, student_id, request.prediction_type)
            
            if not training_data or len(training_data) < self.min_training_days:
                logger.warning(f"Insufficient training data for student {student_id}")
                return None
            
            # 2. Prepare data for Prophet
            df = self._prepare_prophet_data(training_data)
            
            # 3. Train Prophet model
            model = self._train_prophet_model(df, request.prediction_type)
            
            # 4. Generate forecast
            future_df = self._create_future_dataframe(
                model, 
                request.prediction_start, 
                request.prediction_end
            )
            forecast = model.predict(future_df)
            
            # 5. Convert forecast to our format
            forecast_data = self._format_forecast_data(forecast, request.prediction_start)
            
            # 6. Apply business rule adjustments
            adjustments = await self._apply_business_adjustments(
                db, student_id, forecast_data, request
            )
            
            # 7. Generate insights
            insights = await self._generate_insights(
                db, student_id, forecast_data, training_data
            )
            
            # 8. Calculate model metrics
            model_metrics = self._calculate_model_metrics(model, df)
            
            # 9. Create prediction object
            prediction = ProphetPrediction(
                student_id=student_id,
                prediction_type=request.prediction_type,
                model_version="prophet_v1.0",
                prediction_start=request.prediction_start,
                prediction_end=request.prediction_end,
                confidence_interval=request.confidence_interval,
                training_data=TrainingData(
                    start_date=min(d["date"] for d in training_data),
                    end_date=max(d["date"] for d in training_data),
                    transaction_count=len(training_data),
                    data_quality_score=self._calculate_data_quality_score(training_data)
                ),
                forecast_data=forecast_data,
                adjustments=adjustments if request.include_adjustments else [],
                model_metrics=model_metrics,
                insights=insights,
                cache_until=datetime.utcnow() + timedelta(hours=6),
                prediction_hash=self._generate_prediction_hash(request)
            )
            
            # 10. Save prediction to database
            await self._save_prediction(db, prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error generating prediction: {str(e)}")
            return None
    
    async def _get_training_data(
        self, 
        db: AsyncIOMotorDatabase, 
        student_id: ObjectId, 
        prediction_type: str
    ) -> List[Dict]:
        """Get historical transaction data for training"""
        
        # Get data from the last 90 days (or more if available)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        
        if prediction_type in ["income", "expense"]:
            match_filter = {
                "student_id": student_id,
                "type": prediction_type,
                "transaction_date": {"$gte": start_date, "$lte": end_date}
            }
        else:  # balance
            match_filter = {
                "student_id": student_id,
                "transaction_date": {"$gte": start_date, "$lte": end_date}
            }
        
        # Aggregate daily data
        pipeline = [
            {"$match": match_filter},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$transaction_date"},
                        "month": {"$month": "$transaction_date"},
                        "day": {"$dayOfMonth": "$transaction_date"}
                    },
                    "daily_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        if prediction_type == "balance":
            # For balance, we need to calculate cumulative sum
            pipeline = [
                {"$match": {"student_id": student_id, "transaction_date": {"$gte": start_date}}},
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$transaction_date"},
                            "month": {"$month": "$transaction_date"},
                            "day": {"$dayOfMonth": "$transaction_date"}
                        },
                        "daily_income": {
                            "$sum": {"$cond": [{"$eq": ["$type", "income"]}, "$amount", 0]}
                        },
                        "daily_expense": {
                            "$sum": {"$cond": [{"$eq": ["$type", "expense"]}, "$amount", 0]}
                        }
                    }
                },
                {
                    "$addFields": {
                        "daily_balance": {"$subtract": ["$daily_income", "$daily_expense"]}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
        
        results = await db.transactions.aggregate(pipeline).to_list(length=None)
        
        # Convert to list of dictionaries with proper dates
        training_data = []
        for result in results:
            date = datetime(
                year=result["_id"]["year"],
                month=result["_id"]["month"],
                day=result["_id"]["day"]
            )
            
            if prediction_type == "balance":
                amount = result["daily_balance"]
            else:
                amount = result["daily_amount"]
            
            training_data.append({
                "date": date,
                "amount": amount,
                "transaction_count": result.get("transaction_count", 0)
            })
        
        return training_data
    
    def _prepare_prophet_data(self, training_data: List[Dict]) -> pd.DataFrame:
        """Prepare data in Prophet format (ds, y columns)"""
        
        data = []
        for item in training_data:
            data.append({
                "ds": item["date"],
                "y": item["amount"]
            })
        
        df = pd.DataFrame(data)
        df["ds"] = pd.to_datetime(df["ds"])
        
        # Fill missing dates with 0 values
        df = df.set_index("ds").resample("D").sum().fillna(0).reset_index()
        
        return df
    
    def _train_prophet_model(self, df: pd.DataFrame, prediction_type: str) -> Prophet:
        """Train Prophet model with appropriate parameters"""
        
        # Configure Prophet based on prediction type
        if prediction_type == "expense":
            # Expenses typically have weekly seasonality and some yearly patterns
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,  # More flexible for student spending
                seasonality_prior_scale=10,
                interval_width=self.default_confidence_interval
            )
            
            # Add monthly seasonality (important for students)
            model.add_seasonality(name="monthly", period=30.5, fourier_order=5)
            
        elif prediction_type == "income":
            # Income is usually more regular (monthly allowance)
            model = Prophet(
                yearly_seasonality=False,
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.01,  # Less flexible for regular income
                seasonality_prior_scale=5,
                interval_width=self.default_confidence_interval
            )
            
            # Add monthly seasonality for allowance
            model.add_seasonality(name="monthly", period=30.5, fourier_order=3)
            
        else:  # balance
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10,
                interval_width=self.default_confidence_interval
            )
        
        # Fit the model
        model.fit(df)
        
        return model
    
    def _create_future_dataframe(
        self, 
        model: Prophet, 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        """Create future dataframe for prediction"""
        
        periods = (end_date - start_date).days
        future = model.make_future_dataframe(periods=periods)
        
        # Filter to only future dates we want
        future = future[future["ds"] >= start_date]
        
        return future
    
    def _format_forecast_data(
        self, 
        forecast: pd.DataFrame, 
        start_date: datetime
    ) -> List[ForecastDataPoint]:
        """Convert Prophet forecast to our format"""
        
        forecast_data = []
        
        # Filter to only future predictions
        future_forecast = forecast[forecast["ds"] >= start_date]
        
        for _, row in future_forecast.iterrows():
            forecast_data.append(ForecastDataPoint(
                date=row["ds"].to_pydatetime(),
                predicted_value=max(0, row["yhat"]),  # Ensure non-negative
                lower_bound=max(0, row["yhat_lower"]),
                upper_bound=max(0, row["yhat_upper"]),
                trend=row.get("trend", 0),
                seasonal=row.get("seasonal", 0),
                yearly=row.get("yearly", 0),
                weekly=row.get("weekly", 0)
            ))
        
        return forecast_data
    
    async def _apply_business_adjustments(
        self,
        db: AsyncIOMotorDatabase,
        student_id: ObjectId,
        forecast_data: List[ForecastDataPoint],
        request: PredictionRequest
    ) -> List[PredictionAdjustment]:
        """Apply business rule adjustments to predictions"""
        
        adjustments = []
        
        # Get student info for context
        student = await db.students.find_one({"_id": student_id})
        if not student:
            return adjustments
        
        # Get prediction rules that apply to this student
        rules = await db.prediction_rules.find({
            "is_active": True,
            "rule_type": {"$in": ["academic_event", "seasonal", "behavioral"]}
        }).sort("priority", -1).to_list(length=None)
        
        for rule in rules:
            if self._rule_applies_to_student(rule, student):
                # Apply rule adjustments
                rule_adjustments = self._apply_rule_to_forecast(
                    rule, forecast_data, request.prediction_type
                )
                adjustments.extend(rule_adjustments)
        
        return adjustments
    
    def _rule_applies_to_student(self, rule: Dict, student: Dict) -> bool:
        """Check if prediction rule applies to student"""
        
        conditions = rule.get("conditions", {})
        
        # Check student criteria
        student_criteria = conditions.get("student_criteria", {})
        if student_criteria:
            profile = student.get("profile", {})
            
            if "semester" in student_criteria:
                if profile.get("semester") not in student_criteria["semester"]:
                    return False
            
            if "university" in student_criteria:
                if profile.get("university") != student_criteria["university"]:
                    return False
        
        # Check financial criteria
        financial_criteria = conditions.get("financial_criteria", {})
        if financial_criteria:
            if "monthly_allowance_min" in financial_criteria:
                allowance = student.get("profile", {}).get("monthly_allowance", 0)
                if allowance < financial_criteria["monthly_allowance_min"]:
                    return False
        
        return True
    
    def _apply_rule_to_forecast(
        self, 
        rule: Dict, 
        forecast_data: List[ForecastDataPoint], 
        prediction_type: str
    ) -> List[PredictionAdjustment]:
        """Apply specific rule to forecast data"""
        
        adjustments = []
        rule_adjustments = rule.get("prediction_adjustments", {})
        
        if prediction_type == "expense":
            expense_adjustments = rule_adjustments.get("expense_adjustments", [])
            
            for adj in expense_adjustments:
                if adj["period"] == "next_month":
                    # Apply to first 30 days
                    for i, point in enumerate(forecast_data[:30]):
                        original_value = point.predicted_value
                        
                        if adj["adjustment_type"] == "multiply":
                            adjusted_value = original_value * adj["value"]
                        elif adj["adjustment_type"] == "add":
                            adjusted_value = original_value + adj["value"]
                        elif adj["adjustment_type"] == "subtract":
                            adjusted_value = max(0, original_value - adj["value"])
                        else:
                            continue
                        
                        point.predicted_value = adjusted_value
                        
                        adjustments.append(PredictionAdjustment(
                            date=point.date,
                            original_prediction=original_value,
                            adjusted_prediction=adjusted_value,
                            adjustment_reason=adj["reason"],
                            adjustment_type=rule["rule_type"],
                            confidence=rule.get("confidence_impact", 0.8)
                        ))
        
        return adjustments
    
    async def _generate_insights(
        self,
        db: AsyncIOMotorDatabase,
        student_id: ObjectId,
        forecast_data: List[ForecastDataPoint],
        training_data: List[Dict]
    ) -> List[PredictionInsight]:
        """Generate actionable insights from predictions"""
        
        insights = []
        
        # Calculate average predictions
        weekly_avg = np.mean([point.predicted_value for point in forecast_data[:7]])
        monthly_avg = np.mean([point.predicted_value for point in forecast_data[:30]])
        historical_avg = np.mean([item["amount"] for item in training_data[-30:]])
        
        # Trend analysis
        if monthly_avg > historical_avg * 1.1:
            insights.append(PredictionInsight(
                type="trend",
                message=f"Spending diperkirakan meningkat {((monthly_avg/historical_avg - 1) * 100):.1f}% bulan depan",
                importance="high",
                actionable=True,
                suggested_action="Pertimbangkan untuk mengurangi pengeluaran tidak penting"
            ))
        elif monthly_avg < historical_avg * 0.9:
            insights.append(PredictionInsight(
                type="trend",
                message=f"Spending diperkirakan menurun {((1 - monthly_avg/historical_avg) * 100):.1f}% bulan depan",
                importance="medium",
                actionable=True,
                suggested_action="Kesempatan bagus untuk menambah tabungan"
            ))
        
        # Weekly pattern analysis
        weekly_variance = np.var([point.predicted_value for point in forecast_data[:7]])
        if weekly_variance > historical_avg * 0.5:
            insights.append(PredictionInsight(
                type="seasonality",
                message="Pola pengeluaran mingguan sangat bervariasi",
                importance="medium",
                actionable=True,
                suggested_action="Buat budget harian untuk mengontrol pengeluaran"
            ))
        
        # Budget recommendation
        student = await db.students.find_one({"_id": student_id})
        if student:
            monthly_allowance = student.get("profile", {}).get("monthly_allowance", 0)
            if monthly_allowance > 0 and monthly_avg > monthly_allowance * 0.8:
                insights.append(PredictionInsight(
                    type="recommendation",
                    message="Prediksi pengeluaran mendekati batas budget bulanan",
                    importance="high",
                    actionable=True,
                    suggested_action="Batasi pengeluaran untuk kategori hiburan dan makanan"
                ))
        
        return insights
    
    def _calculate_model_metrics(self, model: Prophet, df: pd.DataFrame) -> ModelMetrics:
        """Calculate model performance metrics"""
        
        # Simple cross-validation metrics
        try:
            # Use last 20% of data for validation
            split_idx = int(len(df) * 0.8)
            train_df = df[:split_idx]
            test_df = df[split_idx:]
            
            # Retrain model on training data
            temp_model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False
            )
            temp_model.fit(train_df)
            
            # Predict on test data
            future = temp_model.make_future_dataframe(periods=len(test_df))
            forecast = temp_model.predict(future)
            
            # Calculate metrics
            actual = test_df["y"].values
            predicted = forecast["yhat"].iloc[-len(actual):].values
            
            mae = np.mean(np.abs(actual - predicted))
            mape = np.mean(np.abs((actual - predicted) / (actual + 1e-8))) * 100
            rmse = np.sqrt(np.mean((actual - predicted) ** 2))
            
            # Custom accuracy score (inverse of normalized RMSE)
            accuracy_score = max(0, 1 - (rmse / (np.mean(actual) + 1e-8)))
            
        except Exception as e:
            logger.warning(f"Error calculating metrics: {e}")
            mae = mape = rmse = 0.0
            accuracy_score = 0.5
        
        return ModelMetrics(
            mae=mae,
            mape=mape,
            rmse=rmse,
            accuracy_score=accuracy_score
        )
    
    def _calculate_data_quality_score(self, training_data: List[Dict]) -> float:
        """Calculate data quality score based on completeness and consistency"""
        
        if not training_data:
            return 0.0
        
        # Check for data completeness (consistent daily data)
        dates = [item["date"] for item in training_data]
        date_range = (max(dates) - min(dates)).days + 1
        completeness = len(training_data) / date_range
        
        # Check for data consistency (not too many zero values)
        non_zero_count = sum(1 for item in training_data if item["amount"] > 0)
        consistency = non_zero_count / len(training_data)
        
        # Overall quality score
        quality_score = (completeness * 0.6 + consistency * 0.4)
        return min(1.0, quality_score)
    
    def _generate_prediction_hash(self, request: PredictionRequest) -> str:
        """Generate hash for caching similar predictions"""
        import hashlib
        
        hash_string = f"{request.prediction_type}_{request.prediction_start}_{request.prediction_end}_{request.confidence_interval}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    async def _save_prediction(self, db: AsyncIOMotorDatabase, prediction: ProphetPrediction):
        """Save prediction to database"""
        
        try:
            prediction_dict = prediction.model_dump(by_alias=True)
            await db.predictions.insert_one(prediction_dict)
            logger.info(f"Saved prediction {prediction.id} for student {prediction.student_id}")
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")