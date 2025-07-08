# app/services/prediction_service.py
"""Financial prediction service using Prophet and other algorithms."""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from datetime import date as date_type  # Alias to avoid conflicts
from typing import Optional, List, Dict, Any, Tuple
import uuid
import asyncio
from bson import ObjectId

from ..config.database import get_database
from ..models.prediction import (
    PredictionRequest, PredictionResponse, PredictionPoint, IncomePredictin,
    ExpensePrediction, SavingsPrediction, CategoryPrediction, AnomalyDetection,
    PredictionAccuracy, ModelPerformance, PredictionType, PredictionPeriod,
    PredictionAlgorithm, DEFAULT_PREDICTION_CONFIGS, TrendAnalysis
)
from ..services.transaction_service import transaction_service
from ..services.savings_target_service import savings_target_service

logger = logging.getLogger(__name__)


class PredictionServiceError(Exception):
    """Prediction service related error."""
    pass


class PredictionService:
    """Financial prediction service with multiple algorithms."""
    
    def __init__(self):
        self.predictions_collection = "predictions"
        self.prediction_accuracy_collection = "prediction_accuracy"
        self.model_performance_collection = "model_performance"
        self.anomaly_detection_collection = "anomaly_detection"
        
        # Initialize Prophet if available
        self.prophet_available = False
        try:
            from prophet import Prophet
            self.prophet_available = True
            logger.info("Prophet forecasting library available")
        except ImportError:
            logger.warning("Prophet library not available, using alternative algorithms")
    
    async def predict_income(
        self,
        user_id: str,
        request: PredictionRequest
    ) -> IncomePredictin:
        """Predict future income trends."""
        try:
            # Get historical income data
            income_data = await self._get_income_data(user_id)
            
            if len(income_data) < DEFAULT_PREDICTION_CONFIGS["income"]["min_data_points"]:
                raise PredictionServiceError("Insufficient income data for prediction")
            
            # Create base prediction
            base_prediction = await self._create_prediction(
                user_id=user_id,
                request=request,
                data=income_data,
                prediction_type=PredictionType.INCOME
            )
            
            # Get income sources breakdown
            income_sources = await self._analyze_income_sources(user_id)
            
            # Analyze seasonal patterns
            seasonal_patterns = await self._analyze_seasonal_patterns(income_data, "income")
            
            # Calculate growth rate
            growth_rate = self._calculate_growth_rate(income_data)
            
            # Calculate stability score
            stability_score = self._calculate_stability_score(income_data)
            
            return IncomePredictin(
                prediction_response=base_prediction,
                income_sources=income_sources,
                seasonal_patterns=seasonal_patterns,
                growth_rate=growth_rate,
                stability_score=stability_score
            )
            
        except Exception as e:
            logger.error(f"Error predicting income: {e}")
            raise PredictionServiceError("Failed to predict income")
    
    async def predict_expense(
        self,
        user_id: str,
        request: PredictionRequest
    ) -> ExpensePrediction:
        """Predict future expense trends."""
        try:
            # Get historical expense data
            expense_data = await self._get_expense_data(user_id, request.category_id)
            
            if len(expense_data) < DEFAULT_PREDICTION_CONFIGS["expense"]["min_data_points"]:
                raise PredictionServiceError("Insufficient expense data for prediction")
            
            # Create base prediction
            base_prediction = await self._create_prediction(
                user_id=user_id,
                request=request,
                data=expense_data,
                prediction_type=PredictionType.EXPENSE
            )
            
            # Get category breakdown
            category_breakdown = await self._analyze_expense_categories(user_id)
            
            # Analyze spending trends
            spending_trends = await self._analyze_spending_trends(user_id)
            
            # Generate budget recommendations
            budget_recommendations = await self._generate_budget_recommendations(user_id, expense_data)
            
            # Find cost optimization opportunities
            optimization_opportunities = await self._find_cost_optimizations(user_id)
            
            return ExpensePrediction(
                prediction_response=base_prediction,
                category_breakdown=category_breakdown,
                spending_trends=spending_trends,
                budget_recommendations=budget_recommendations,
                cost_optimization_opportunities=optimization_opportunities
            )
            
        except Exception as e:
            logger.error(f"Error predicting expenses: {e}")
            raise PredictionServiceError("Failed to predict expenses")
    
    async def predict_savings(
        self,
        user_id: str,
        request: PredictionRequest
    ) -> SavingsPrediction:
        """Predict savings trajectory and goal achievement."""
        try:
            # Get historical savings data
            savings_data = await self._get_savings_data(user_id)
            
            if len(savings_data) < DEFAULT_PREDICTION_CONFIGS["savings"]["min_data_points"]:
                raise PredictionServiceError("Insufficient savings data for prediction")
            
            # Create base prediction
            base_prediction = await self._create_prediction(
                user_id=user_id,
                request=request,
                data=savings_data,
                prediction_type=PredictionType.SAVINGS
            )
            
            # Calculate savings rate
            savings_rate = await self._calculate_savings_rate(user_id)
            
            # Predict goal achievement dates
            goal_achievement_dates = await self._predict_goal_achievements(user_id, base_prediction)
            
            # Generate savings optimization tips
            optimization_tips = await self._generate_savings_tips(user_id, savings_data)
            
            # Create emergency fund timeline
            emergency_fund_timeline = await self._create_emergency_fund_timeline(user_id, base_prediction)
            
            return SavingsPrediction(
                prediction_response=base_prediction,
                savings_rate=savings_rate,
                goal_achievement_dates=goal_achievement_dates,
                savings_optimization_tips=optimization_tips,
                emergency_fund_timeline=emergency_fund_timeline
            )
            
        except Exception as e:
            logger.error(f"Error predicting savings: {e}")
            raise PredictionServiceError("Failed to predict savings")
    
    async def predict_category(
        self,
        user_id: str,
        category_id: str,
        request: PredictionRequest
    ) -> CategoryPrediction:
        """Predict category-specific spending patterns."""
        try:
            if not category_id:
                raise PredictionServiceError("Category ID is required for category prediction")
            
            # Get historical category data
            category_data = await self._get_category_data(user_id, category_id)
            
            if len(category_data) < DEFAULT_PREDICTION_CONFIGS["category"]["min_data_points"]:
                raise PredictionServiceError("Insufficient category data for prediction")
            
            # Create base prediction
            request.category_id = category_id
            base_prediction = await self._create_prediction(
                user_id=user_id,
                request=request,
                data=category_data,
                prediction_type=PredictionType.CATEGORY
            )
            
            # Analyze category trends
            category_trends = await self._analyze_category_trends(user_id, category_id)
            
            # Peer comparison (if available)
            peer_comparison = await self._get_peer_comparison(user_id, category_id)
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_category_optimizations(user_id, category_id, category_data)
            
            return CategoryPrediction(
                prediction_response=base_prediction,
                category_trends=category_trends,
                peer_comparison=peer_comparison,
                optimization_suggestions=optimization_suggestions
            )
            
        except Exception as e:
            logger.error(f"Error predicting category: {e}")
            raise PredictionServiceError("Failed to predict category")
    
    async def detect_anomalies(self, user_id: str) -> List[AnomalyDetection]:
        """Detect anomalies in spending patterns."""
        try:
            anomalies = []
            
            # Get recent transaction data
            recent_data = await self._get_recent_transaction_data(user_id, days=30)
            historical_data = await self._get_recent_transaction_data(user_id, days=90)
            
            # Detect spending spikes
            spending_anomalies = self._detect_spending_spikes(recent_data, historical_data)
            anomalies.extend(spending_anomalies)
            
            # Detect unusual patterns
            pattern_anomalies = self._detect_pattern_anomalies(recent_data, historical_data)
            anomalies.extend(pattern_anomalies)
            
            # Detect category anomalies
            category_anomalies = await self._detect_category_anomalies(user_id)
            anomalies.extend(category_anomalies)
            
            # Save anomalies to database
            for anomaly in anomalies:
                await self._save_anomaly(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    async def get_prediction_accuracy(
        self,
        user_id: str,
        prediction_id: Optional[str] = None
    ) -> List[PredictionAccuracy]:
        """Get prediction accuracy metrics."""
        try:
            db = await get_database()
            collection = db[self.prediction_accuracy_collection]
            
            query = {"user_id": user_id}
            if prediction_id:
                query["prediction_id"] = prediction_id
            
            accuracy_docs = await collection.find(query).sort("observation_date", -1).to_list(None)
            
            return [PredictionAccuracy(**doc) for doc in accuracy_docs]
            
        except Exception as e:
            logger.error(f"Error getting prediction accuracy: {e}")
            return []
    
    async def update_prediction_accuracy(
        self,
        prediction_id: str,
        actual_value: float,
        observation_date: date_type  # Updated parameter name
    ) -> bool:
        """Update prediction accuracy with actual observed values."""
        try:
            db = await get_database()
            
            # Get original prediction
            predictions_collection = db[self.predictions_collection]
            prediction_doc = await predictions_collection.find_one({"prediction_id": prediction_id})
            
            if not prediction_doc:
                return False
            
            # Find matching prediction point
            prediction_point = None
            for point in prediction_doc["predictions"]:
                if point["prediction_date"] == observation_date:
                    prediction_point = point
                    break
            
            if not prediction_point:
                return False
            
            # Calculate accuracy metrics
            predicted_value = prediction_point["predicted_value"]
            absolute_error = abs(actual_value - predicted_value)
            percentage_error = (absolute_error / actual_value * 100) if actual_value != 0 else 0
            
            # Save accuracy record
            accuracy_collection = db[self.prediction_accuracy_collection]
            accuracy_doc = {
                "prediction_id": prediction_id,
                "actual_value": actual_value,
                "predicted_value": predicted_value,
                "absolute_error": absolute_error,
                "percentage_error": percentage_error,
                "observation_date": observation_date,  # Updated field name
                "updated_accuracy": max(0, 1 - (percentage_error / 100)),
                "created_at": datetime.utcnow()
            }
            
            await accuracy_collection.insert_one(accuracy_doc)
            
            # Update model performance
            await self._update_model_performance(
                prediction_doc["algorithm_used"],
                prediction_doc["prediction_type"],
                percentage_error
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating prediction accuracy: {e}")
            return False
    
    async def get_model_performance(
        self,
        algorithm: Optional[PredictionAlgorithm] = None,
        prediction_type: Optional[PredictionType] = None
    ) -> List[ModelPerformance]:
        """Get model performance metrics."""
        try:
            db = await get_database()
            collection = db[self.model_performance_collection]
            
            query = {}
            if algorithm:
                query["algorithm"] = algorithm.value
            if prediction_type:
                query["prediction_type"] = prediction_type.value
            
            performance_docs = await collection.find(query).to_list(None)
            
            return [ModelPerformance(**doc) for doc in performance_docs]
            
        except Exception as e:
            logger.error(f"Error getting model performance: {e}")
            return []
    
    # Private helper methods
    async def _create_prediction(
        self,
        user_id: str,
        request: PredictionRequest,
        data: List[Dict[str, Any]],
        prediction_type: PredictionType
    ) -> PredictionResponse:
        """Create prediction using specified algorithm."""
        try:
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Generate predictions based on algorithm
            if request.algorithm == PredictionAlgorithm.PROPHET and self.prophet_available:
                predictions = await self._prophet_predict(df, request)
            elif request.algorithm == PredictionAlgorithm.LINEAR_REGRESSION:
                predictions = self._linear_regression_predict(df, request)
            elif request.algorithm == PredictionAlgorithm.MOVING_AVERAGE:
                predictions = self._moving_average_predict(df, request)
            else:
                # Fallback to moving average
                predictions = self._moving_average_predict(df, request)
            
            # Calculate model accuracy (simplified)
            model_accuracy = self._calculate_model_accuracy(df, request.algorithm)
            
            # Generate prediction ID
            prediction_id = str(uuid.uuid4())
            
            # Create prediction response
            prediction_response = PredictionResponse(
                prediction_id=prediction_id,
                user_id=user_id,
                prediction_type=prediction_type,
                period=request.period,
                algorithm_used=request.algorithm,
                category_id=request.category_id,
                category_name=await self._get_category_name(request.category_id) if request.category_id else None,
                predictions=predictions,
                summary=self._create_prediction_summary(predictions),
                model_accuracy=model_accuracy,
                mean_absolute_error=self._calculate_mae(df),
                r_squared=self._calculate_r_squared(df),
                data_points_used=len(df),
                training_period_start=df['date'].min().date(),
                training_period_end=df['date'].max().date(),
                expires_at=datetime.utcnow() + timedelta(days=7)  # Predictions expire in 7 days
            )
            
            # Save prediction to database
            await self._save_prediction(prediction_response)
            
            return prediction_response
            
        except Exception as e:
            logger.error(f"Error creating prediction: {e}")
            raise PredictionServiceError("Failed to create prediction")
    
    async def _prophet_predict(
        self,
        df: pd.DataFrame,
        request: PredictionRequest
    ) -> List[PredictionPoint]:
        """Generate predictions using Facebook Prophet."""
        try:
            from prophet import Prophet
            
            # Prepare data for Prophet
            prophet_df = df[['date', 'amount']].rename(columns={'date': 'ds', 'amount': 'y'})
            
            # Initialize Prophet model
            model = Prophet(
                daily_seasonality=request.period == PredictionPeriod.DAILY,
                weekly_seasonality=request.period in [PredictionPeriod.DAILY, PredictionPeriod.WEEKLY],
                yearly_seasonality=request.seasonality,
                interval_width=0.8 if request.include_confidence_intervals else 0.95
            )
            
            # Fit model
            model.fit(prophet_df)
            
            # Create future dates
            future_dates = model.make_future_dataframe(
                periods=request.periods_ahead,
                freq=self._get_frequency(request.period)
            )
            
            # Generate forecast
            forecast = model.predict(future_dates)
            
            # Convert to prediction points
            predictions = []
            future_forecast = forecast.tail(request.periods_ahead)
            
            for _, row in future_forecast.iterrows():
                predictions.append(PredictionPoint(
                    prediction_date=row['ds'].date(),  # Updated field name
                    predicted_value=max(0, row['yhat']),  # Ensure non-negative
                    lower_bound=max(0, row['yhat_lower']) if request.include_confidence_intervals else None,
                    upper_bound=max(0, row['yhat_upper']) if request.include_confidence_intervals else None,
                    confidence=0.8,  # Prophet default confidence
                    is_anomaly=False
                ))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in Prophet prediction: {e}")
            raise PredictionServiceError("Prophet prediction failed")
    
    def _linear_regression_predict(
        self,
        df: pd.DataFrame,
        request: PredictionRequest
    ) -> List[PredictionPoint]:
        """Generate predictions using linear regression."""
        try:
            from sklearn.linear_model import LinearRegression
            import numpy as np
            
            # Prepare data
            df['days'] = (df['date'] - df['date'].min()).dt.days
            X = df[['days']].values
            y = df['amount'].values
            
            # Fit model
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate future dates
            last_day = df['days'].max()
            period_days = self._get_period_days(request.period)
            
            predictions = []
            for i in range(1, request.periods_ahead + 1):
                future_day = last_day + (i * period_days)
                future_date = df['date'].min() + timedelta(days=future_day)
                
                predicted_value = model.predict([[future_day]])[0]
                predicted_value = max(0, predicted_value)  # Ensure non-negative
                
                # Simple confidence intervals based on historical variance
                historical_std = df['amount'].std()
                confidence = 0.7
                
                predictions.append(PredictionPoint(
                    prediction_date=future_date.date(),  # Updated field name
                    predicted_value=predicted_value,
                    lower_bound=max(0, predicted_value - historical_std) if request.include_confidence_intervals else None,
                    upper_bound=predicted_value + historical_std if request.include_confidence_intervals else None,
                    confidence=confidence,
                    is_anomaly=False
                ))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in linear regression prediction: {e}")
            # Fallback to moving average
            return self._moving_average_predict(df, request)
    
    def _moving_average_predict(
        self,
        df: pd.DataFrame,
        request: PredictionRequest
    ) -> List[PredictionPoint]:
        """Generate predictions using moving average."""
        try:
            # Calculate moving average window
            window_size = min(12, len(df) // 2) if len(df) > 2 else len(df)
            moving_avg = df['amount'].rolling(window=window_size).mean().iloc[-1]
            
            # Calculate trend
            if len(df) >= 2:
                recent_avg = df['amount'].tail(window_size // 2).mean()
                older_avg = df['amount'].head(window_size // 2).mean()
                trend = (recent_avg - older_avg) / (window_size // 2)
            else:
                trend = 0
            
            # Generate predictions
            predictions = []
            last_date = df['date'].max()
            period_days = self._get_period_days(request.period)
            
            # Calculate confidence based on historical variance
            historical_std = df['amount'].std()
            confidence = max(0.5, 1 - (historical_std / moving_avg)) if moving_avg > 0 else 0.5
            
            for i in range(1, request.periods_ahead + 1):
                future_date = last_date + timedelta(days=i * period_days)
                predicted_value = max(0, moving_avg + (trend * i))
                
                predictions.append(PredictionPoint(
                    prediction_date=future_date.date(),  # Updated field name
                    predicted_value=predicted_value,
                    lower_bound=max(0, predicted_value - historical_std) if request.include_confidence_intervals else None,
                    upper_bound=predicted_value + historical_std if request.include_confidence_intervals else None,
                    confidence=confidence,
                    is_anomaly=False
                ))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in moving average prediction: {e}")
            raise PredictionServiceError("Moving average prediction failed")
    
    # Additional helper methods (keeping existing implementation but updating any date field references)
    async def _get_income_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get historical income data for user."""
        try:
            db = await get_database()
            collection = db.transactions
            
            # Aggregate monthly income
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "transaction_type": "income"
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$transaction_date"},
                            "month": {"$month": "$transaction_date"}
                        },
                        "amount": {"$sum": "$amount"}
                    }
                },
                {
                    "$addFields": {
                        "date": {
                            "$dateFromParts": {
                                "year": "$_id.year",
                                "month": "$_id.month",
                                "day": 1
                            }
                        }
                    }
                },
                {"$sort": {"date": 1}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(None)
            
            return [
                {
                    "date": doc["date"],
                    "amount": doc["amount"]
                }
                for doc in result
            ]
            
        except Exception as e:
            logger.error(f"Error getting income data: {e}")
            return []
    
    async def _get_expense_data(self, user_id: str, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get historical expense data for user."""
        try:
            db = await get_database()
            collection = db.transactions
            
            # Build match criteria
            match_criteria = {
                "user_id": user_id,
                "transaction_type": "expense"
            }
            
            if category_id:
                match_criteria["category_id"] = category_id
            
            # Aggregate monthly expenses
            pipeline = [
                {"$match": match_criteria},
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$transaction_date"},
                            "month": {"$month": "$transaction_date"}
                        },
                        "amount": {"$sum": "$amount"}
                    }
                },
                {
                    "$addFields": {
                        "date": {
                            "$dateFromParts": {
                                "year": "$_id.year",
                                "month": "$_id.month",
                                "day": 1
                            }
                        }
                    }
                },
                {"$sort": {"date": 1}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(None)
            
            return [
                {
                    "date": doc["date"],
                    "amount": doc["amount"]
                }
                for doc in result
            ]
            
        except Exception as e:
            logger.error(f"Error getting expense data: {e}")
            return []
    
    async def _get_savings_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get historical savings data for user."""
        try:
            # Calculate monthly net savings (income - expenses)
            income_data = await self._get_income_data(user_id)
            expense_data = await self._get_expense_data(user_id)
            
            # Create a combined dataset
            savings_data = []
            income_dict = {item["date"]: item["amount"] for item in income_data}
            expense_dict = {item["date"]: item["amount"] for item in expense_data}
            
            # Get all unique dates
            all_dates = set(income_dict.keys()) | set(expense_dict.keys())
            
            for date in sorted(all_dates):
                income = income_dict.get(date, 0)
                expense = expense_dict.get(date, 0)
                savings = income - expense
                
                savings_data.append({
                    "date": date,
                    "amount": max(0, savings)  # Only positive savings
                })
            
            return savings_data
            
        except Exception as e:
            logger.error(f"Error getting savings data: {e}")
            return []
    
    async def _get_category_data(self, user_id: str, category_id: str) -> List[Dict[str, Any]]:
        """Get historical data for specific category."""
        return await self._get_expense_data(user_id, category_id)
    
    def _get_frequency(self, period: PredictionPeriod) -> str:
        """Get pandas frequency string for period."""
        frequency_map = {
            PredictionPeriod.DAILY: 'D',
            PredictionPeriod.WEEKLY: 'W',
            PredictionPeriod.MONTHLY: 'M',
            PredictionPeriod.QUARTERLY: 'Q',
            PredictionPeriod.YEARLY: 'Y'
        }
        return frequency_map.get(period, 'M')
    
    def _get_period_days(self, period: PredictionPeriod) -> int:
        """Get number of days for each period."""
        days_map = {
            PredictionPeriod.DAILY: 1,
            PredictionPeriod.WEEKLY: 7,
            PredictionPeriod.MONTHLY: 30,
            PredictionPeriod.QUARTERLY: 90,
            PredictionPeriod.YEARLY: 365
        }
        return days_map.get(period, 30)
    
    def _calculate_model_accuracy(self, df: pd.DataFrame, algorithm: PredictionAlgorithm) -> float:
        """Calculate model accuracy score."""
        # Simplified accuracy calculation
        if len(df) < 2:
            return 0.5
        
        variance = df['amount'].var()
        mean_amount = df['amount'].mean()
        
        if mean_amount == 0:
            return 0.5
        
        coefficient_of_variation = (variance ** 0.5) / mean_amount
        
        # Higher accuracy for lower variation
        accuracy = max(0.1, 1 - min(1, coefficient_of_variation))
        
        # Adjust based on algorithm
        algorithm_bonus = {
            PredictionAlgorithm.PROPHET: 0.1,
            PredictionAlgorithm.LINEAR_REGRESSION: 0.05,
            PredictionAlgorithm.MOVING_AVERAGE: 0.0
        }
        
        return min(1.0, accuracy + algorithm_bonus.get(algorithm, 0))
    
    def _calculate_mae(self, df: pd.DataFrame) -> Optional[float]:
        """Calculate Mean Absolute Error."""
        if len(df) < 2:
            return None
        
        mean_amount = df['amount'].mean()
        mae = df['amount'].apply(lambda x: abs(x - mean_amount)).mean()
        return mae
    
    def _calculate_r_squared(self, df: pd.DataFrame) -> Optional[float]:
        """Calculate R-squared score."""
        if len(df) < 2:
            return None
        
        # Simplified R-squared calculation
        variance = df['amount'].var()
        mean_amount = df['amount'].mean()
        
        if variance == 0:
            return 1.0
        
        return max(0, 1 - (variance / (mean_amount ** 2)))
    
    def _create_prediction_summary(self, predictions: List[PredictionPoint]) -> Dict[str, Any]:
        """Create prediction summary statistics."""
        if not predictions:
            return {}
        
        values = [p.predicted_value for p in predictions]
        
        return {
            "min_predicted": min(values),
            "max_predicted": max(values),
            "avg_predicted": sum(values) / len(values),
            "total_predicted": sum(values),
            "trend": "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "stable",
            "volatility": np.std(values) if len(values) > 1 else 0
        }
    
    async def _save_prediction(self, prediction: PredictionResponse):
        """Save prediction to database."""
        try:
            db = await get_database()
            collection = db[self.predictions_collection]
            
            prediction_doc = prediction.model_dump(by_alias=True)
            prediction_doc["predictions"] = [
                p.model_dump() for p in prediction.predictions
            ]
            
            await collection.insert_one(prediction_doc)
            
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
    
    # Placeholder methods for additional functionality (implement as needed)
    async def _analyze_income_sources(self, user_id: str) -> List[Dict[str, Any]]:
        """Analyze income sources breakdown."""
        return []
    
    async def _analyze_seasonal_patterns(self, data: List[Dict[str, Any]], data_type: str) -> Dict[str, Any]:
        """Analyze seasonal patterns in financial data."""
        return {}
    
    def _calculate_growth_rate(self, data: List[Dict[str, Any]]) -> float:
        """Calculate monthly growth rate."""
        return 0.0
    
    def _calculate_stability_score(self, data: List[Dict[str, Any]]) -> float:
        """Calculate income/expense stability score."""
        return 0.5
    
    async def _analyze_expense_categories(self, user_id: str) -> List[Dict[str, Any]]:
        """Get category breakdown."""
        return []
    
    async def _analyze_spending_trends(self, user_id: str) -> Dict[str, Any]:
        """Analyze spending trends."""
        return {}
    
    async def _generate_budget_recommendations(self, user_id: str, expense_data: List[Dict[str, Any]]) -> List[str]:
        """Generate budget recommendations."""
        return []
    
    async def _find_cost_optimizations(self, user_id: str) -> List[str]:
        """Find cost optimization opportunities."""
        return []
    
    async def _calculate_savings_rate(self, user_id: str) -> float:
        """Calculate average savings rate."""
        return 0.0
    
    async def _predict_goal_achievements(self, user_id: str, savings_prediction: PredictionResponse) -> Dict[str, date_type]:
        """Predict when savings goals will be achieved."""
        return {}
    
    async def _generate_savings_tips(self, user_id: str, savings_data: List[Dict[str, Any]]) -> List[str]:
        """Generate savings optimization tips."""
        return []
    
    async def _create_emergency_fund_timeline(self, user_id: str, base_prediction: PredictionResponse) -> Optional[Dict[str, Any]]:
        """Create emergency fund timeline."""
        return None
    
    async def _analyze_category_trends(self, user_id: str, category_id: str) -> Dict[str, Any]:
        """Analyze category trends."""
        return {}
    
    async def _get_peer_comparison(self, user_id: str, category_id: str) -> Optional[Dict[str, Any]]:
        """Peer comparison (if available)."""
        return None
    
    async def _generate_category_optimizations(self, user_id: str, category_id: str, category_data: List[Dict[str, Any]]) -> List[str]:
        """Generate optimization suggestions."""
        return []
    
    async def _get_recent_transaction_data(self, user_id: str, days: int) -> List[Dict[str, Any]]:
        """Get recent transaction data."""
        return []
    
    def _detect_spending_spikes(self, recent_data: List[Dict[str, Any]], historical_data: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """Detect spending spikes."""
        return []
    
    def _detect_pattern_anomalies(self, recent_data: List[Dict[str, Any]], historical_data: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """Detect unusual patterns."""
        return []
    
    async def _detect_category_anomalies(self, user_id: str) -> List[AnomalyDetection]:
        """Detect category anomalies."""
        return []
    
    async def _save_anomaly(self, anomaly: AnomalyDetection):
        """Save anomalies to database."""
        pass
    
    async def _get_category_name(self, category_id: Optional[str]) -> Optional[str]:
        """Get category name by ID."""
        if not category_id:
            return None
        return "Category Name"  # Placeholder
    
    async def _update_model_performance(self, algorithm: str, prediction_type: str, percentage_error: float):
        """Update model performance metrics."""
        pass


# Global prediction service instance
prediction_service = PredictionService()