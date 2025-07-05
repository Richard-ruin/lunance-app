# app/services/financial_predictor.py
import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Dict, List, Any, Optional
import asyncio
import logging

from ..database import get_database
from ..models.financial_prediction import FinancialPrediction, PredictionData
from ..models.transaction import Transaction

logger = logging.getLogger(__name__)

class FinancialPredictor:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = None
    
    async def get_database(self):
        if not self.db:
            self.db = await get_database()
        return self.db
    
    async def get_historical_data(self, data_type: str, days_back: int = 365) -> Dict[str, List]:
        """Get historical financial data for prediction"""
        db = await self.get_database()
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        if data_type == "expense":
            pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(self.user_id),
                        "type": "expense",
                        "date": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"},
                            "day": {"$dayOfMonth": "$date"}
                        },
                        "total": {"$sum": "$amount"}
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}
                }
            ]
        elif data_type == "income":
            pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(self.user_id),
                        "type": "income",
                        "date": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"},
                            "day": {"$dayOfMonth": "$date"}
                        },
                        "total": {"$sum": "$amount"}
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}
                }
            ]
        
        results = await db.transactions.aggregate(pipeline).to_list(None)
        
        dates = []
        amounts = []
        
        for result in results:
            date_obj = datetime(
                result["_id"]["year"],
                result["_id"]["month"],
                result["_id"]["day"]
            )
            dates.append(date_obj)
            amounts.append(result["total"])
        
        return {"dates": dates, "amounts": amounts}
    
    def prepare_prophet_data(self, historical_data: Dict[str, List]) -> pd.DataFrame:
        """Prepare data for Prophet model"""
        df = pd.DataFrame({
            'ds': historical_data['dates'],
            'y': historical_data['amounts']
        })
        
        # Fill missing dates with 0
        df['ds'] = pd.to_datetime(df['ds'])
        df = df.set_index('ds').resample('D').sum().fillna(0).reset_index()
        
        return df
    
    async def predict_expenses(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Predict future expenses using Prophet"""
        try:
            # Get historical data
            historical_data = await self.get_historical_data("expense", 365)
            
            if len(historical_data['dates']) < 10:
                raise ValueError("Insufficient historical data for prediction")
            
            # Prepare data for Prophet
            df = self.prepare_prophet_data(historical_data)
            
            # Create and configure Prophet model
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False,  # Not enough data for yearly
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0
            )
            
            # Fit model
            model.fit(df)
            
            # Make future dataframe
            future = model.make_future_dataframe(periods=days_ahead)
            forecast = model.predict(future)
            
            # Calculate accuracy on historical data
            accuracy = self.calculate_accuracy(df['y'].values, forecast['yhat'][:len(df)].values)
            
            # Extract prediction data
            prediction_start_idx = len(df)
            prediction_data = PredictionData(
                dates=forecast['ds'][prediction_start_idx:].dt.to_pydatetime().tolist(),
                predicted_values=forecast['yhat'][prediction_start_idx:].tolist(),
                confidence_intervals={
                    'lower': forecast['yhat_lower'][prediction_start_idx:].tolist(),
                    'upper': forecast['yhat_upper'][prediction_start_idx:].tolist()
                }
            )
            
            return {
                'prediction_data': prediction_data,
                'accuracy': accuracy,
                'training_points': len(df)
            }
            
        except Exception as e:
            logger.error(f"Error in expense prediction: {str(e)}")
            raise
    
    async def predict_income(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Predict future income using Prophet"""
        try:
            # Get historical data
            historical_data = await self.get_historical_data("income", 365)
            
            if len(historical_data['dates']) < 10:
                raise ValueError("Insufficient historical data for prediction")
            
            # Prepare data for Prophet
            df = self.prepare_prophet_data(historical_data)
            
            # Create and configure Prophet model
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0
            )
            
            # Fit model
            model.fit(df)
            
            # Make future dataframe
            future = model.make_future_dataframe(periods=days_ahead)
            forecast = model.predict(future)
            
            # Calculate accuracy
            accuracy = self.calculate_accuracy(df['y'].values, forecast['yhat'][:len(df)].values)
            
            # Extract prediction data
            prediction_start_idx = len(df)
            prediction_data = PredictionData(
                dates=forecast['ds'][prediction_start_idx:].dt.to_pydatetime().tolist(),
                predicted_values=forecast['yhat'][prediction_start_idx:].tolist(),
                confidence_intervals={
                    'lower': forecast['yhat_lower'][prediction_start_idx:].tolist(),
                    'upper': forecast['yhat_upper'][prediction_start_idx:].tolist()
                }
            )
            
            return {
                'prediction_data': prediction_data,
                'accuracy': accuracy,
                'training_points': len(df)
            }
            
        except Exception as e:
            logger.error(f"Error in income prediction: {str(e)}")
            raise
    
    async def predict_balance(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Predict future account balance"""
        try:
            # Get both income and expense predictions
            income_pred = await self.predict_income(days_ahead)
            expense_pred = await self.predict_expenses(days_ahead)
            
            # Calculate current balance
            db = await self.get_database()
            pipeline = [
                {"$match": {"user_id": ObjectId(self.user_id)}},
                {"$group": {
                    "_id": None,
                    "total_income": {
                        "$sum": {"$cond": [{"$eq": ["$type", "income"]}, "$amount", 0]}
                    },
                    "total_expense": {
                        "$sum": {"$cond": [{"$eq": ["$type", "expense"]}, "$amount", 0]}
                    }
                }}
            ]
            
            result = await db.transactions.aggregate(pipeline).to_list(1)
            current_balance = 0
            if result:
                current_balance = result[0]["total_income"] - result[0]["total_expense"]
            
            # Calculate predicted balance
            predicted_income = income_pred['prediction_data'].predicted_values
            predicted_expense = expense_pred['prediction_data'].predicted_values
            
            # Calculate cumulative balance
            balance_predictions = [current_balance]
            for i in range(len(predicted_income)):
                daily_net = predicted_income[i] - predicted_expense[i]
                balance_predictions.append(balance_predictions[-1] + daily_net)
            
            # Remove the initial balance from predictions
            balance_predictions = balance_predictions[1:]
            
            # Calculate confidence intervals
            income_lower = income_pred['prediction_data'].confidence_intervals['lower']
            income_upper = income_pred['prediction_data'].confidence_intervals['upper']
            expense_lower = expense_pred['prediction_data'].confidence_intervals['lower']
            expense_upper = expense_pred['prediction_data'].confidence_intervals['upper']
            
            balance_lower = [current_balance]
            balance_upper = [current_balance]
            
            for i in range(len(predicted_income)):
                # Conservative estimate: lower income, higher expense
                daily_net_lower = income_lower[i] - expense_upper[i]
                # Optimistic estimate: higher income, lower expense
                daily_net_upper = income_upper[i] - expense_lower[i]
                
                balance_lower.append(balance_lower[-1] + daily_net_lower)
                balance_upper.append(balance_upper[-1] + daily_net_upper)
            
            balance_lower = balance_lower[1:]
            balance_upper = balance_upper[1:]
            
            prediction_data = PredictionData(
                dates=income_pred['prediction_data'].dates,
                predicted_values=balance_predictions,
                confidence_intervals={
                    'lower': balance_lower,
                    'upper': balance_upper
                }
            )
            
            # Average accuracy from both models
            avg_accuracy = (income_pred['accuracy'] + expense_pred['accuracy']) / 2
            
            return {
                'prediction_data': prediction_data,
                'accuracy': avg_accuracy,
                'training_points': min(income_pred['training_points'], expense_pred['training_points']),
                'current_balance': current_balance
            }
            
        except Exception as e:
            logger.error(f"Error in balance prediction: {str(e)}")
            raise
    
    async def predict_category_spending(self, category_id: str, days_ahead: int = 30) -> Dict[str, Any]:
        """Predict spending for a specific category"""
        try:
            db = await self.get_database()
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=365)
            
            # Get historical category data
            pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(self.user_id),
                        "category_id": ObjectId(category_id),
                        "type": "expense",
                        "date": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"},
                            "day": {"$dayOfMonth": "$date"}
                        },
                        "total": {"$sum": "$amount"}
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}
                }
            ]
            
            results = await db.transactions.aggregate(pipeline).to_list(None)
            
            if len(results) < 10:
                raise ValueError("Insufficient historical data for category prediction")
            
            # Prepare data
            dates = []
            amounts = []
            for result in results:
                date_obj = datetime(
                    result["_id"]["year"],
                    result["_id"]["month"],
                    result["_id"]["day"]
                )
                dates.append(date_obj)
                amounts.append(result["total"])
            
            df = pd.DataFrame({'ds': dates, 'y': amounts})
            df['ds'] = pd.to_datetime(df['ds'])
            df = df.set_index('ds').resample('D').sum().fillna(0).reset_index()
            
            # Create Prophet model
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False,
                changepoint_prior_scale=0.05
            )
            
            # Fit and predict
            model.fit(df)
            future = model.make_future_dataframe(periods=days_ahead)
            forecast = model.predict(future)
            
            # Calculate accuracy
            accuracy = self.calculate_accuracy(df['y'].values, forecast['yhat'][:len(df)].values)
            
            # Extract predictions
            prediction_start_idx = len(df)
            prediction_data = PredictionData(
                dates=forecast['ds'][prediction_start_idx:].dt.to_pydatetime().tolist(),
                predicted_values=forecast['yhat'][prediction_start_idx:].tolist(),
                confidence_intervals={
                    'lower': forecast['yhat_lower'][prediction_start_idx:].tolist(),
                    'upper': forecast['yhat_upper'][prediction_start_idx:].tolist()
                }
            )
            
            return {
                'prediction_data': prediction_data,
                'accuracy': accuracy,
                'training_points': len(df)
            }
            
        except Exception as e:
            logger.error(f"Error in category prediction: {str(e)}")
            raise
    
    def calculate_accuracy(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calculate prediction accuracy using MAPE"""
        try:
            # Avoid division by zero
            mask = actual != 0
            if not mask.any():
                return 0.0
            
            mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
            accuracy = max(0, 100 - mape)
            return round(accuracy, 2)
        except Exception:
            return 0.0
    
    async def save_prediction(self, prediction_type: str, prediction_result: Dict[str, Any]) -> str:
        """Save prediction to database"""
        try:
            db = await self.get_database()
            
            # Create expiry date (7 days from now)
            expires_at = datetime.utcnow() + timedelta(days=7)
            
            prediction = FinancialPrediction(
                user_id=ObjectId(self.user_id),
                prediction_type=prediction_type,
                period="daily",
                prediction_data=prediction_result['prediction_data'],
                model_accuracy=prediction_result['accuracy'],
                training_data_points=prediction_result['training_points'],
                expires_at=expires_at
            )
            
            result = await db.financial_predictions.insert_one(prediction.dict(by_alias=True))
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving prediction: {str(e)}")
            raise