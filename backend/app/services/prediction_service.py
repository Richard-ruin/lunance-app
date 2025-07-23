# app/services/prediction_service.py - FIXED VERSION
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from collections import defaultdict
import warnings
import json
warnings.filterwarnings('ignore')

from ..config.database import get_database
from ..models.finance import Transaction, TransactionType, TransactionStatus
from ..models.user import User
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from ..services.financial_categories import IndonesianStudentCategories

# Setup logging
logger = logging.getLogger(__name__)

class FinancialPredictionService:
    """
    FIXED VERSION - Service untuk prediksi keuangan menggunakan Facebook Prophet
    Perbaikan untuk mengatasi insufficient data dan JSON errors
    """
    
    def __init__(self):
        self.db = get_database()
        self.categories = IndonesianStudentCategories()
        logger.info("✅ FinancialPredictionService initialized with Prophet")
    
    def format_currency(self, amount: float) -> str:
        """Format currency to Rupiah"""
        if pd.isna(amount) or amount is None:
            return "Rp 0"
        return f"Rp {amount:,.0f}".replace(',', '.')
    
    # ==========================================
    # FIXED DATA PREPARATION METHODS
    # ==========================================
    
    async def _get_user_transactions_for_prediction(self, user_id: str, months_back: int = 6) -> pd.DataFrame:
        """
        FIXED: Ambil data transaksi user untuk prediksi dengan better error handling
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months_back * 30)
            
            # Query transactions dengan more flexible criteria
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "status": TransactionStatus.CONFIRMED.value,
                        "date": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {
                    "$sort": {"date": 1}
                }
            ]
            
            transactions = list(self.db.transactions.aggregate(pipeline))
            
            # FIXED: Lower minimum requirement dengan better messaging
            if len(transactions) < 5:  # Reduced from 10 to 5
                logger.warning(f"User {user_id} has insufficient data for prediction: {len(transactions)} transactions")
                return pd.DataFrame()
            
            # Convert to DataFrame dengan better error handling
            df_data = []
            for trans in transactions:
                try:
                    # Ensure required fields exist
                    if not all(key in trans for key in ['date', 'amount', 'type']):
                        logger.warning(f"Skipping transaction with missing required fields: {trans.get('_id')}")
                        continue
                    
                    # Determine budget type dengan fallback
                    budget_type = self.categories.get_budget_type(trans.get("category", "Unknown"))
                    if not budget_type:
                        # Fallback berdasarkan type
                        budget_type = "needs" if trans['type'] == 'expense' else "income"
                    
                    df_data.append({
                        'ds': trans['date'],  # Prophet requires 'ds' for date
                        'y': float(trans['amount']),  # Prophet requires 'y' for value, ensure float
                        'type': trans['type'],
                        'category': trans.get('category', 'Unknown'),
                        'budget_type': budget_type,
                        'description': trans.get('description', ''),
                        'transaction_id': str(trans.get('_id', ''))
                    })
                    
                except Exception as trans_error:
                    logger.warning(f"Error processing transaction {trans.get('_id')}: {trans_error}")
                    continue
            
            if not df_data:
                logger.error(f"No valid transactions found for user {user_id}")
                return pd.DataFrame()
            
            df = pd.DataFrame(df_data)
            df['ds'] = pd.to_datetime(df['ds'])
            
            # Remove any null values
            df = df.dropna(subset=['ds', 'y'])
            
            # Ensure y is numeric and positive (for expense) or handle negative properly
            df['y'] = pd.to_numeric(df['y'], errors='coerce')
            df = df.dropna(subset=['y'])
            
            logger.info(f"📊 Loaded {len(df)} valid transactions for prediction analysis")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error getting transactions for prediction: {e}")
            return pd.DataFrame()
    
    def _prepare_time_series_data(self, df: pd.DataFrame, data_type: str = "expense", 
                                 budget_type: Optional[str] = None, 
                                 aggregation: str = "daily") -> pd.DataFrame:
        """
        FIXED: Prepare time series data untuk Prophet dengan better validation
        """
        try:
            if df.empty:
                logger.warning("Empty DataFrame provided to _prepare_time_series_data")
                return pd.DataFrame()
            
            # Filter berdasarkan type dan budget_type
            if data_type == "income":
                filtered_df = df[df['type'] == 'income'].copy()
            elif data_type == "expense":
                filtered_df = df[df['type'] == 'expense'].copy()
                if budget_type:
                    filtered_df = filtered_df[filtered_df['budget_type'] == budget_type]
            elif data_type == "net":
                # Net = Income - Expense
                income_df = df[df['type'] == 'income'].copy()
                expense_df = df[df['type'] == 'expense'].copy()
                
                if income_df.empty and expense_df.empty:
                    return pd.DataFrame()
                
                # Aggregate by date
                income_agg = income_df.groupby('ds')['y'].sum().reset_index() if not income_df.empty else pd.DataFrame(columns=['ds', 'y'])
                expense_agg = expense_df.groupby('ds')['y'].sum().reset_index() if not expense_df.empty else pd.DataFrame(columns=['ds', 'y'])
                
                # Handle empty dataframes
                if income_agg.empty:
                    income_agg = pd.DataFrame({'ds': expense_agg['ds'], 'y': 0})
                if expense_agg.empty:
                    expense_agg = pd.DataFrame({'ds': income_agg['ds'], 'y': 0})
                
                # Merge and calculate net
                merged = income_agg.merge(expense_agg, on='ds', how='outer', suffixes=('_income', '_expense'))
                merged.fillna(0, inplace=True)
                merged['y'] = merged['y_income'] - merged['y_expense']
                
                return merged[['ds', 'y']]
            else:
                logger.error(f"Unknown data_type: {data_type}")
                return pd.DataFrame()
            
            if filtered_df.empty:
                logger.warning(f"No data found for type: {data_type}, budget_type: {budget_type}")
                return pd.DataFrame()
            
            # Aggregate berdasarkan periode
            try:
                if aggregation == "daily":
                    time_series = filtered_df.groupby('ds')['y'].sum().reset_index()
                elif aggregation == "weekly":
                    filtered_df['week'] = filtered_df['ds'].dt.to_period('W').dt.start_time
                    time_series = filtered_df.groupby('week')['y'].sum().reset_index()
                    time_series.rename(columns={'week': 'ds'}, inplace=True)
                elif aggregation == "monthly":
                    filtered_df['month'] = filtered_df['ds'].dt.to_period('M').dt.start_time
                    time_series = filtered_df.groupby('month')['y'].sum().reset_index()
                    time_series.rename(columns={'month': 'ds'}, inplace=True)
                else:
                    time_series = filtered_df.groupby('ds')['y'].sum().reset_index()
            except Exception as agg_error:
                logger.error(f"Error in aggregation: {agg_error}")
                return pd.DataFrame()
            
            # Sort by date and remove any remaining nulls
            time_series = time_series.sort_values('ds').reset_index(drop=True)
            time_series = time_series.dropna()
            
            # FIXED: More lenient minimum requirement
            if len(time_series) < 3:  # Reduced from 5 to 3
                logger.warning(f"Insufficient data points for {data_type} {budget_type}: {len(time_series)}")
                return pd.DataFrame()
            
            # Ensure y values are reasonable (not too extreme)
            y_mean = time_series['y'].mean()
            y_std = time_series['y'].std()
            
            if y_std > 0:
                # Remove extreme outliers (more than 3 standard deviations)
                time_series = time_series[
                    (time_series['y'] >= (y_mean - 3 * y_std)) & 
                    (time_series['y'] <= (y_mean + 3 * y_std))
                ]
            
            logger.info(f"📈 Prepared {len(time_series)} data points for {data_type} {budget_type or ''} prediction")
            return time_series
            
        except Exception as e:
            logger.error(f"❌ Error preparing time series data: {e}")
            return pd.DataFrame()
    
    # ==========================================
    # FIXED PROPHET PREDICTION METHODS
    # ==========================================
    
    def _create_prophet_model(self, seasonality_mode: str = "additive",  # Changed from multiplicative
                             yearly_seasonality: bool = False,  # Disabled for shorter data
                             weekly_seasonality: bool = True,
                             daily_seasonality: bool = False) -> Prophet:
        """FIXED: Create Prophet model dengan more conservative settings"""
        try:
            model = Prophet(
                seasonality_mode=seasonality_mode,
                yearly_seasonality=yearly_seasonality,
                weekly_seasonality=weekly_seasonality,
                daily_seasonality=daily_seasonality,
                changepoint_prior_scale=0.01,   # Much lower for stability
                seasonality_prior_scale=0.05,   # Much lower for stability
                holidays_prior_scale=0.05,      # Much lower for stability
                interval_width=0.95,            # Wider interval for safety
                uncertainty_samples=1000,       # More samples for better uncertainty
                mcmc_samples=0,                 # Disable MCMC for faster processing
                growth='linear',                # Force linear growth for stability
                n_changepoints=5                # Fewer changepoints for stability
            )
            
            # Only add custom seasonalities if we have enough data
            # Commented out to avoid overfitting with small datasets
            # model.add_seasonality(
            #     name='semester',
            #     period=180,
            #     fourier_order=2  # Reduced from 3
            # )
            
            return model
            
        except Exception as e:
            logger.error(f"❌ Error creating Prophet model: {e}")
            raise
    
    def _fit_and_predict(self, time_series: pd.DataFrame, forecast_days: int = 30) -> Dict[str, Any]:
        """
        FIXED: Fit Prophet model dengan comprehensive error handling
        """
        try:
            if time_series.empty or len(time_series) < 3:  # Reduced minimum
                return {
                    "success": False,
                    "error": "Insufficient data for prediction",
                    "min_required": 3,
                    "actual_data_points": len(time_series),
                    "message": "Perlu minimal 3 titik data untuk prediksi. Silakan tambah lebih banyak transaksi."
                }
            
            # Validate data quality
            if time_series['y'].isna().any() or (time_series['y'] == 0).all():
                return {
                    "success": False,
                    "error": "Invalid data quality",
                    "message": "Data transaksi tidak valid atau semuanya bernilai 0"
                }
            
            # Create model with error handling
            try:
                model = self._create_prophet_model()
            except Exception as model_error:
                logger.error(f"❌ Error creating Prophet model: {model_error}")
                return {
                    "success": False,
                    "error": f"Model creation failed: {str(model_error)}",
                    "message": "Gagal membuat model prediksi"
                }
            
            # Fit model dengan extensive error handling
            try:
                # Suppress Prophet warnings during fitting
                import logging as prophet_logging
                prophet_logging.getLogger('prophet').setLevel(prophet_logging.ERROR)
                prophet_logging.getLogger('cmdstanpy').setLevel(prophet_logging.ERROR)
                
                model.fit(time_series)
                
            except Exception as fit_error:
                logger.error(f"❌ Prophet model fitting failed: {fit_error}")
                
                # Try with even more conservative settings
                try:
                    logger.info("🔄 Retrying with ultra-conservative Prophet settings...")
                    conservative_model = Prophet(
                        seasonality_mode='additive',
                        yearly_seasonality=False,
                        weekly_seasonality=False,
                        daily_seasonality=False,
                        changepoint_prior_scale=0.001,
                        seasonality_prior_scale=0.01,
                        interval_width=0.95,
                        growth='linear',
                        n_changepoints=3
                    )
                    conservative_model.fit(time_series)
                    model = conservative_model
                    logger.info("✅ Conservative model fitting succeeded")
                    
                except Exception as conservative_error:
                    logger.error(f"❌ Even conservative model failed: {conservative_error}")
                    return {
                        "success": False,
                        "error": f"Model fitting failed: {str(fit_error)}",
                        "message": "Model prediksi tidak dapat dilatih dengan data ini. Coba tambah lebih banyak data transaksi."
                    }
            
            # Generate future dataframe
            try:
                future = model.make_future_dataframe(periods=forecast_days, freq='D')
            except Exception as future_error:
                logger.error(f"❌ Error generating future dataframe: {future_error}")
                return {
                    "success": False,
                    "error": f"Future generation failed: {str(future_error)}"
                }
            
            # Make prediction dengan error handling
            try:
                forecast = model.predict(future)
            except Exception as predict_error:
                logger.error(f"❌ Error making prediction: {predict_error}")
                return {
                    "success": False,
                    "error": f"Prediction failed: {str(predict_error)}"
                }
            
            # Extract predictions safely
            try:
                historical_data = time_series.to_dict('records')
                
                # Ensure we don't go beyond available predictions
                prediction_start = len(time_series)
                prediction_end = min(len(forecast), prediction_start + forecast_days)
                
                predictions = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].iloc[prediction_start:prediction_end].to_dict('records')
                
                # Clean up any negative predictions for expenses (optional)
                for pred in predictions:
                    if pred['yhat'] < 0:
                        pred['yhat'] = 0
                    if pred['yhat_lower'] < 0:
                        pred['yhat_lower'] = 0
                
            except Exception as extract_error:
                logger.error(f"❌ Error extracting predictions: {extract_error}")
                return {
                    "success": False,
                    "error": f"Prediction extraction failed: {str(extract_error)}"
                }
            
            # Calculate model performance dengan error handling
            try:
                historical_forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head(len(time_series))
                historical_performance = self._calculate_model_performance(time_series, historical_forecast)
            except Exception as perf_error:
                logger.warning(f"⚠️ Error calculating performance, using defaults: {perf_error}")
                historical_performance = {
                    "mae": 0,
                    "mape": 50,  # Conservative default
                    "rmse": 0,
                    "accuracy_score": 50,  # Conservative default
                    "r2_score": 0.3,
                    "data_points": len(time_series),
                    "performance_note": "Performance calculation failed, using conservative estimates"
                }
            
            # Generate insights dengan error handling
            try:
                insights = self._generate_prediction_insights(time_series, predictions, historical_performance)
            except Exception as insight_error:
                logger.warning(f"⚠️ Error generating insights: {insight_error}")
                insights = ["Prediksi berhasil dibuat", "Gunakan dengan hati-hati karena data terbatas"]
            
            return {
                "success": True,
                "historical_data": historical_data,
                "predictions": predictions,
                "model_performance": historical_performance,
                "insights": insights,
                "forecast_period_days": len(predictions),  # Actual days predicted
                "data_points_used": len(time_series),
                "prediction_confidence": historical_performance.get("accuracy_score", 50.0),
                "model_info": {
                    "prophet_version": "stable",
                    "seasonality_mode": "additive",
                    "growth": "linear"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in fit_and_predict: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Terjadi kesalahan dalam proses prediksi"
            }
    
    def _calculate_model_performance(self, actual: pd.DataFrame, predicted: pd.DataFrame) -> Dict[str, float]:
        """FIXED: Calculate model performance metrics dengan better error handling"""
        try:
            # Merge actual and predicted with safer approach
            merged = actual.merge(predicted, on='ds', how='inner')
            
            if merged.empty or len(merged) < 2:
                return {
                    "error": "No matching dates for performance calculation",
                    "mae": 0,
                    "mape": 100,
                    "rmse": 0,
                    "accuracy_score": 0,
                    "r2_score": 0,
                    "data_points": 0
                }
            
            actual_values = merged['y'].values
            predicted_values = merged['yhat'].values
            
            # Handle edge cases
            if len(actual_values) == 0 or np.all(actual_values == 0):
                return {
                    "error": "Invalid actual values",
                    "mae": 0,
                    "mape": 100,
                    "rmse": 0,
                    "accuracy_score": 0,
                    "r2_score": 0,
                    "data_points": len(merged)
                }
            
            # Calculate metrics with error handling
            try:
                mae = np.mean(np.abs(actual_values - predicted_values))
            except:
                mae = float('inf')
                
            try:
                # Avoid division by zero in MAPE
                non_zero_actual = np.maximum(np.abs(actual_values), 1)
                mape = np.mean(np.abs((actual_values - predicted_values) / non_zero_actual)) * 100
                mape = min(mape, 100)  # Cap at 100%
            except:
                mape = 100
                
            try:
                rmse = np.sqrt(np.mean((actual_values - predicted_values) ** 2))
            except:
                rmse = float('inf')
            
            # Accuracy score (inverse of MAPE, capped at 100%)
            accuracy_score = max(0, 100 - mape)
            
            # R² score with error handling
            try:
                ss_res = np.sum((actual_values - predicted_values) ** 2)
                ss_tot = np.sum((actual_values - np.mean(actual_values)) ** 2)
                r2_score = 1 - (ss_res / (ss_tot + 1e-8)) if ss_tot > 0 else 0
                r2_score = max(-1, min(1, r2_score))  # Clamp between -1 and 1
            except:
                r2_score = 0
            
            return {
                "mae": float(mae) if not np.isinf(mae) else 0,
                "mape": float(mape),
                "rmse": float(rmse) if not np.isinf(rmse) else 0,
                "accuracy_score": float(accuracy_score),
                "r2_score": float(r2_score),
                "data_points": len(merged)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating model performance: {e}")
            return {
                "error": str(e),
                "mae": 0,
                "mape": 100,
                "rmse": 0,
                "accuracy_score": 0,
                "r2_score": 0,
                "data_points": 0
            }
    
    # ==========================================
    # FIXED PUBLIC PREDICTION METHODS
    # ==========================================
    
    async def predict_income(self, user_id: str, forecast_days: int = 30) -> Dict[str, Any]:
        """FIXED: Prediksi pemasukan user dengan better error handling"""
        try:
            logger.info(f"🔮 Starting income prediction for user {user_id}, {forecast_days} days")
            
            # Get transaction data dengan extended time range
            df = await self._get_user_transactions_for_prediction(user_id, months_back=6)
            if df.empty:
                return {
                    "success": False,
                    "message": "Data transaksi tidak cukup untuk prediksi income",
                    "min_required_transactions": 5,  # Reduced from 10
                    "current_transactions": 0,
                    "suggestion": "Tambahkan minimal 5 transaksi pemasukan untuk prediksi yang akurat",
                    "data_tips": [
                        "Catat uang saku bulanan",
                        "Input pendapatan freelance atau part-time",
                        "Tambahkan bonus atau hadiah yang diterima"
                    ]
                }
            
            # Prepare income time series
            income_ts = self._prepare_time_series_data(df, data_type="income", aggregation="daily")
            if income_ts.empty:
                return {
                    "success": False,
                    "message": "Data pemasukan tidak cukup untuk prediksi",
                    "total_transactions": len(df),
                    "income_transactions": len(df[df['type'] == 'income']),
                    "suggestion": "Tambahkan lebih banyak data pemasukan (uang saku, freelance, dll)",
                    "example_categories": [
                        "Uang Saku", "Freelance", "Part-time", "Bonus", "Hadiah"
                    ]
                }
            
            # Generate prediction
            result = self._fit_and_predict(income_ts, forecast_days)
            
            if not result["success"]:
                return {
                    **result,
                    "prediction_type": "income",
                    "user_guidance": {
                        "min_data_needed": "Minimal 3-5 transaksi pemasukan",
                        "time_span_needed": "Data dari minimal 2-3 bulan terakhir",
                        "tips": [
                            "Catat semua sumber pemasukan secara konsisten",
                            "Include pemasukan kecil seperti uang jajan",
                            "Update data setiap ada pemasukan baru"
                        ]
                    }
                }
            
            # Add income-specific analysis
            predictions = result["predictions"]
            if predictions:
                total_predicted = sum(max(0, p['yhat']) for p in predictions)
                avg_daily_predicted = total_predicted / len(predictions) if predictions else 0
            else:
                total_predicted = 0
                avg_daily_predicted = 0
            
            result.update({
                "prediction_type": "income",
                "total_predicted_income": total_predicted,
                "average_daily_income": avg_daily_predicted,
                "formatted_total": self.format_currency(total_predicted),
                "formatted_daily_avg": self.format_currency(avg_daily_predicted),
                "confidence_level": "Menengah" if result["prediction_confidence"] > 60 else "Rendah",
                "data_quality": {
                    "total_data_points": len(income_ts),
                    "date_range": f"{income_ts['ds'].min().strftime('%Y-%m-%d')} to {income_ts['ds'].max().strftime('%Y-%m-%d')}",
                    "average_historical": self.format_currency(income_ts['y'].mean())
                }
            })
            
            # Add student-specific recommendations
            result["recommendations"] = self._generate_income_recommendations(total_predicted, avg_daily_predicted)
            
            logger.info(f"✅ Income prediction completed for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error predicting income: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Gagal memprediksi pemasukan",
                "prediction_type": "income"
            }
    
    async def predict_expense_by_budget_type(self, user_id: str, budget_type: str, 
                                           forecast_days: int = 30) -> Dict[str, Any]:
        """
        FIXED: Prediksi pengeluaran dengan better validation dan error handling
        """
        try:
            logger.info(f"🔮 Starting {budget_type} expense prediction for user {user_id}")
            
            if budget_type not in ["needs", "wants", "savings"]:
                return {
                    "success": False,
                    "error": f"Invalid budget_type: {budget_type}. Must be 'needs', 'wants', or 'savings'",
                    "valid_types": ["needs", "wants", "savings"]
                }
            
            # Get transaction data
            df = await self._get_user_transactions_for_prediction(user_id, months_back=6)
            if df.empty:
                return {
                    "success": False,
                    "message": f"Data transaksi tidak cukup untuk prediksi {budget_type}",
                    "suggestion": f"Tambahkan lebih banyak transaksi dalam kategori {budget_type}",
                    "budget_type": budget_type,
                    "examples": self._get_budget_type_examples(budget_type)
                }
            
            # Prepare expense time series for specific budget type
            expense_ts = self._prepare_time_series_data(df, data_type="expense", 
                                                      budget_type=budget_type, 
                                                      aggregation="daily")
            if expense_ts.empty:
                expense_count = len(df[(df['type'] == 'expense') & (df['budget_type'] == budget_type)])
                return {
                    "success": False,
                    "message": f"Data pengeluaran {budget_type} tidak cukup untuk prediksi",
                    "budget_type": budget_type,
                    "current_transactions": expense_count,
                    "total_expenses": len(df[df['type'] == 'expense']),
                    "suggestion": f"Tambahkan lebih banyak pengeluaran kategori {budget_type}",
                    "examples": self._get_budget_type_examples(budget_type)
                }
            
            # Generate prediction
            result = self._fit_and_predict(expense_ts, forecast_days)
            
            if not result["success"]:
                return {
                    **result,
                    "prediction_type": f"{budget_type}_expense",
                    "budget_type": budget_type
                }
            
            # Add budget-specific analysis
            predictions = result["predictions"]
            if predictions:
                total_predicted = sum(max(0, p['yhat']) for p in predictions)
                avg_daily_predicted = total_predicted / len(predictions) if predictions else 0
            else:
                total_predicted = 0
                avg_daily_predicted = 0
            
            # Get user's budget allocation
            budget_allocation = await self._get_user_budget_allocation(user_id, budget_type)
            
            result.update({
                "prediction_type": f"{budget_type}_expense",
                "budget_type": budget_type,
                "total_predicted_expense": total_predicted,
                "average_daily_expense": avg_daily_predicted,
                "formatted_total": self.format_currency(total_predicted),
                "formatted_daily_avg": self.format_currency(avg_daily_predicted),
                "budget_allocation": budget_allocation,
                "data_quality": {
                    "total_data_points": len(expense_ts),
                    "date_range": f"{expense_ts['ds'].min().strftime('%Y-%m-%d')} to {expense_ts['ds'].max().strftime('%Y-%m-%d')}",
                    "average_historical": self.format_currency(expense_ts['y'].mean())
                }
            })
            
            # Analyze predictions against budget
            if budget_allocation.get("has_budget"):
                result["predictions_with_budget_status"] = self._analyze_budget_predictions(predictions, budget_allocation)
            
            # Generate budget-specific recommendations
            result["recommendations"] = self._generate_budget_recommendations(
                budget_type, total_predicted, budget_allocation, result["insights"]
            )
            
            logger.info(f"✅ {budget_type} expense prediction completed for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error predicting {budget_type} expense: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Gagal memprediksi pengeluaran {budget_type}",
                "budget_type": budget_type
            }
    
    def _get_budget_type_examples(self, budget_type: str) -> List[str]:
        """Get example categories for budget type"""
        examples = {
            "needs": ["Makan", "Kos/Sewa", "Transport", "Kuliah", "Internet", "Kesehatan"],
            "wants": ["Hiburan", "Nongkrong", "Shopping", "Hobi", "Jajan", "Games"],
            "savings": ["Tabungan", "Investasi", "Emergency Fund", "Target Barang"]
        }
        return examples.get(budget_type, [])
    
    # Rest of the methods remain the same but with improved error handling...
    # [Continue with other methods with similar error handling improvements]
        
    async def predict_budget_performance(self, user_id: str, forecast_days: int = 30) -> Dict[str, Any]:
        """
        FIXED: Prediksi performa budget dengan better error handling
        """
        try:
            logger.info(f"🎯 Starting comprehensive budget performance prediction for user {user_id}")
            
            # Predict untuk semua budget types
            needs_prediction = await self.predict_expense_by_budget_type(user_id, "needs", forecast_days)
            wants_prediction = await self.predict_expense_by_budget_type(user_id, "wants", forecast_days)
            savings_prediction = await self.predict_expense_by_budget_type(user_id, "savings", forecast_days)
            income_prediction = await self.predict_income(user_id, forecast_days)
            
            # Check success status
            successful_predictions = []
            failed_predictions = []
            
            for pred_name, pred_result in [
                ("income", income_prediction),
                ("needs", needs_prediction), 
                ("wants", wants_prediction),
                ("savings", savings_prediction)
            ]:
                if pred_result.get("success", False):
                    successful_predictions.append(pred_name)
                else:
                    failed_predictions.append(pred_name)
            
            # If less than 2 predictions succeeded, return error
            if len(successful_predictions) < 2:
                return {
                    "success": False,
                    "message": "Data tidak cukup untuk prediksi budget performance lengkap",
                    "failed_predictions": failed_predictions,
                    "successful_predictions": successful_predictions,
                    "suggestion": "Tambahkan lebih banyak transaksi di berbagai kategori untuk analisis lengkap",
                    "requirements": {
                        "minimum_successful_categories": 2,
                        "current_successful": len(successful_predictions),
                        "recommended_actions": [
                            "Tambahkan transaksi pemasukan (uang saku, freelance, etc)",
                            "Catat pengeluaran kebutuhan pokok (makan, transport, etc)",
                            "Input pengeluaran keinginan (hiburan, jajan, etc)",
                            "Catat aktivitas menabung"
                        ]
                    }
                }
            
            # Calculate totals from successful predictions
            total_predicted_income = income_prediction.get("total_predicted_income", 0) if income_prediction.get("success") else 0
            total_predicted_needs = needs_prediction.get("total_predicted_expense", 0) if needs_prediction.get("success") else 0
            total_predicted_wants = wants_prediction.get("total_predicted_expense", 0) if wants_prediction.get("success") else 0
            total_predicted_savings = savings_prediction.get("total_predicted_expense", 0) if savings_prediction.get("success") else 0
            
            total_predicted_expense = total_predicted_needs + total_predicted_wants + total_predicted_savings
            predicted_net_balance = total_predicted_income - total_predicted_expense
            
            # Calculate percentages safely
            if total_predicted_income > 0:
                needs_percentage = (total_predicted_needs / total_predicted_income) * 100
                wants_percentage = (total_predicted_wants / total_predicted_income) * 100
                savings_percentage = (total_predicted_savings / total_predicted_income) * 100
            else:
                needs_percentage = wants_percentage = savings_percentage = 0
            
            # Budget health assessment
            budget_health = self._assess_budget_health(needs_percentage, wants_percentage, savings_percentage)
            
            # Generate insights
            comprehensive_insights = self._generate_comprehensive_insights(
                total_predicted_income, total_predicted_expense, predicted_net_balance,
                needs_percentage, wants_percentage, savings_percentage
            )
            
            # Recommendations
            optimization_recommendations = self._generate_50_30_20_recommendations(
                needs_percentage, wants_percentage, savings_percentage, total_predicted_income
            )
            
            return {
                "success": True,
                "prediction_type": "comprehensive_budget_performance",
                "method": "Prophet AI + 50/30/20 Elizabeth Warren",
                "forecast_period_days": forecast_days,
                "generated_at": datetime.now().isoformat(),
                
                # Prediction status
                "prediction_status": {
                    "successful_predictions": successful_predictions,
                    "failed_predictions": failed_predictions,
                    "data_completeness": len(successful_predictions) / 4 * 100  # Percentage of complete data
                },
                
                # Predicted totals
                "predicted_totals": {
                    "income": total_predicted_income,
                    "expense": total_predicted_expense,
                    "net_balance": predicted_net_balance,
                    "needs_expense": total_predicted_needs,
                    "wants_expense": total_predicted_wants,
                    "savings_expense": total_predicted_savings
                },
                
                # Formatted amounts
                "formatted_totals": {
                    "income": self.format_currency(total_predicted_income),
                    "expense": self.format_currency(total_predicted_expense),
                    "net_balance": self.format_currency(predicted_net_balance),
                    "needs_expense": self.format_currency(total_predicted_needs),
                    "wants_expense": self.format_currency(total_predicted_wants),
                    "savings_expense": self.format_currency(total_predicted_savings)
                },
                
                # Budget percentages
                "predicted_percentages": {
                    "needs": needs_percentage,
                    "wants": wants_percentage,
                    "savings": savings_percentage
                },
                
                # Target vs Predicted comparison
                "budget_comparison": {
                    "needs": {
                        "target": 50.0,
                        "predicted": needs_percentage,
                        "variance": needs_percentage - 50.0,
                        "status": "over" if needs_percentage > 55 else "under" if needs_percentage < 45 else "on_track"
                    },
                    "wants": {
                        "target": 30.0,
                        "predicted": wants_percentage,
                        "variance": wants_percentage - 30.0,
                        "status": "over" if wants_percentage > 35 else "under" if wants_percentage < 25 else "on_track"
                    },
                    "savings": {
                        "target": 20.0,
                        "predicted": savings_percentage,
                        "variance": savings_percentage - 20.0,
                        "status": "over" if savings_percentage > 22 else "under" if savings_percentage < 18 else "on_track"
                    }
                },
                
                # Health assessment
                "budget_health": budget_health,
                
                # Detailed predictions
                "individual_predictions": {
                    "income": income_prediction if income_prediction.get("success") else None,
                    "needs": needs_prediction if needs_prediction.get("success") else None,
                    "wants": wants_prediction if wants_prediction.get("success") else None,
                    "savings": savings_prediction if savings_prediction.get("success") else None
                },
                
                # Insights and recommendations
                "comprehensive_insights": comprehensive_insights,
                "optimization_recommendations": optimization_recommendations,
                "failed_predictions": failed_predictions
            }
                
        except Exception as e:
            logger.error(f"❌ Error predicting budget performance: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Gagal memprediksi performa budget"
            }
    
    # ==========================================
    # HELPER METHODS WITH IMPROVEMENTS
    # ==========================================
    
    async def _get_user_budget_allocation(self, user_id: str, budget_type: str) -> Dict[str, Any]:
        """Get user's budget allocation untuk budget type tertentu"""
        try:
            from bson import ObjectId
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            
            if not user_doc or not user_doc.get("financial_settings"):
                return {"has_budget": False}
            
            financial_settings = user_doc["financial_settings"]
            monthly_income = financial_settings.get("monthly_income", 0)
            
            if monthly_income <= 0:
                return {"has_budget": False}
            
            # 50/30/20 allocation
            allocation_percentages = {
                "needs": 0.50,
                "wants": 0.30,
                "savings": 0.20
            }
            
            budget_amount = monthly_income * allocation_percentages.get(budget_type, 0)
            
            return {
                "has_budget": True,
                "monthly_income": monthly_income,
                "budget_percentage": allocation_percentages.get(budget_type, 0) * 100,
                "budget_amount": budget_amount,
                "formatted_budget": self.format_currency(budget_amount)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting budget allocation: {e}")
            return {"has_budget": False, "error": str(e)}
    
    def _analyze_budget_predictions(self, predictions: List[Dict], budget_allocation: Dict[str, Any]) -> List[Dict]:
        """Analyze predictions against budget allocation"""
        if not budget_allocation.get("has_budget") or not predictions:
            return predictions
        
        monthly_budget = budget_allocation.get("budget_amount", 0)
        daily_budget = monthly_budget / 30 if monthly_budget > 0 else 0
        
        analyzed_predictions = []
        for pred in predictions:
            predicted_amount = max(0, pred.get('yhat', 0))
            
            status = "within_budget" if predicted_amount <= daily_budget else "over_budget"
            budget_usage_percentage = (predicted_amount / daily_budget * 100) if daily_budget > 0 else 0
            
            analyzed_pred = pred.copy()
            analyzed_pred.update({
                "daily_budget": daily_budget,
                "budget_status": status,
                "budget_usage_percentage": budget_usage_percentage,
                "formatted_predicted": self.format_currency(predicted_amount),
                "formatted_daily_budget": self.format_currency(daily_budget)
            })
            
            analyzed_predictions.append(analyzed_pred)
        
        return analyzed_predictions
    
    def _assess_budget_health(self, needs_pct: float, wants_pct: float, savings_pct: float) -> Dict[str, Any]:
        """Assess overall budget health berdasarkan 50/30/20 method"""
        
        # Calculate variance from ideal 50/30/20
        needs_variance = abs(needs_pct - 50.0)
        wants_variance = abs(wants_pct - 30.0)
        savings_variance = abs(savings_pct - 20.0)
        
        # Average variance
        avg_variance = (needs_variance + wants_variance + savings_variance) / 3
        
        # Determine health level
        if avg_variance <= 5:
            health_level = "excellent"
            health_score = 95 - avg_variance
        elif avg_variance <= 10:
            health_level = "good"
            health_score = 85 - avg_variance
        elif avg_variance <= 20:
            health_level = "fair"
            health_score = 70 - (avg_variance - 10)
        else:
            health_level = "poor"
            health_score = max(30, 50 - (avg_variance - 20))
        
        return {
            "health_level": health_level,
            "health_score": round(health_score, 1),
            "average_variance": round(avg_variance, 1),
            "individual_variances": {
                "needs": round(needs_variance, 1),
                "wants": round(wants_variance, 1),
                "savings": round(savings_variance, 1)
            }
        }
    
    def _generate_prediction_insights(self, historical: pd.DataFrame, predictions: List[Dict], 
                                    performance: Dict[str, Any]) -> List[str]:
        """Generate insights dari hasil prediksi"""
        insights = []
        
        try:
            if historical.empty or not predictions:
                insights.append("Data terbatas, gunakan prediksi dengan hati-hati")
                return insights
            
            # Historical average
            historical_avg = historical['y'].mean()
            
            # Predicted average
            predicted_values = [p.get('yhat', 0) for p in predictions]
            predicted_avg = np.mean(predicted_values) if predicted_values else 0
            
            # Trend analysis
            if historical_avg > 0:
                trend_change = ((predicted_avg - historical_avg) / historical_avg) * 100
                
                if trend_change > 10:
                    insights.append(f"📈 Prediksi menunjukkan peningkatan {trend_change:.1f}% dari rata-rata historis")
                elif trend_change < -10:
                    insights.append(f"📉 Prediksi menunjukkan penurunan {abs(trend_change):.1f}% dari rata-rata historis")
                else:
                    insights.append("📊 Prediksi menunjukkan pola yang relatif stabil")
            
            # Accuracy assessment
            accuracy = performance.get("accuracy_score", 0)
            if accuracy > 85:
                insights.append("🎯 Model prediksi memiliki akurasi tinggi (>85%)")
            elif accuracy > 70:
                insights.append("📋 Model prediksi memiliki akurasi sedang (70-85%)")
            else:
                insights.append("⚠️ Model prediksi memiliki akurasi rendah (<70%), gunakan dengan hati-hati")
            
        except Exception as e:
            logger.error(f"❌ Error generating insights: {e}")
            insights.append("❌ Error dalam menganalisis insights")
        
        return insights
    
    def _generate_income_recommendations(self, total_predicted: float, daily_avg: float) -> List[str]:
        """Generate recommendations untuk income predictions"""
        recommendations = []
        
        monthly_predicted = total_predicted * (30/30)  # Normalize to monthly
        
        if monthly_predicted < 1000000:  # < 1 juta
            recommendations.extend([
                "💡 Pertimbangkan mencari sumber income tambahan (freelance, part-time)",
                "📚 Manfaatkan skill untuk freelance online (design, writing, tutoring)",
                "🎯 Set target minimum income 1-1.5 juta per bulan untuk mahasiswa"
            ])
        elif monthly_predicted < 2000000:  # 1-2 juta
            recommendations.extend([
                "✅ Income prediction cukup baik untuk mahasiswa",
                "📈 Pertimbangkan diversifikasi sumber income",
                "💰 Alokasikan 20% untuk tabungan sesuai metode 50/30/20"
            ])
        else:  # > 2 juta
            recommendations.extend([
                "🎉 Income prediction sangat baik!",
                "💎 Pertimbangkan investasi jangka panjang",
                "🏆 Bisa meningkatkan target tabungan >20%"
            ])
        
        return recommendations
    
    def _generate_budget_recommendations(self, budget_type: str, predicted_amount: float,
                                       budget_allocation: Dict, insights: List[str]) -> List[str]:
        """Generate recommendations berdasarkan budget type dan predictions"""
        recommendations = []
        
        if not budget_allocation.get("has_budget"):
            recommendations.append("⚙️ Setup budget allocation terlebih dahulu untuk analisis yang lebih akurat")
            return recommendations
        
        monthly_budget = budget_allocation.get("budget_amount", 0)
        monthly_predicted = predicted_amount * (30/30)  # Normalize
        
        if budget_type == "needs":
            if monthly_predicted > monthly_budget * 1.1:  # >110% budget
                recommendations.extend([
                    "⚠️ Prediksi pengeluaran NEEDS melebihi budget 50%",
                    "🔍 Review kebutuhan pokok: kos, makan, transport, pendidikan",
                    "💡 Cari alternatif lebih hemat untuk kebutuhan dasar"
                ])
            elif monthly_predicted < monthly_budget * 0.8:  # <80% budget
                recommendations.extend([
                    "✅ Pengeluaran NEEDS efisien dan di bawah budget",
                    "💰 Surplus bisa dialokasikan ke savings atau emergency fund"
                ])
        elif budget_type == "wants":
            if monthly_predicted > monthly_budget * 1.2:  # >120% budget
                recommendations.extend([
                    "🚨 Prediksi pengeluaran WANTS melebihi budget 30%",
                    "🎯 Prioritaskan wants yang benar-benar penting",
                    "💡 Gunakan sebagian wants budget untuk target tabungan barang"
                ])
        elif budget_type == "savings":
            if monthly_predicted < monthly_budget * 0.5:  # <50% target savings
                recommendations.extend([
                    "📈 Tingkatkan alokasi tabungan sesuai target 20%",
                    "🎯 Automation transfer ke rekening tabungan"
                ])
        
        return recommendations
    
    def _generate_comprehensive_insights(self, income: float, expense: float, net_balance: float,
                                       needs_pct: float, wants_pct: float, savings_pct: float) -> List[str]:
        """Generate comprehensive insights untuk budget performance"""
        insights = []
        
        # Net balance insights
        if net_balance > 0:
            insights.append(f"💰 Prediksi net balance positif: {self.format_currency(net_balance)}")
        else:
            insights.append(f"⚠️ Prediksi deficit: {self.format_currency(abs(net_balance))}")
        
        # 50/30/20 adherence insights
        if needs_pct > 60:
            insights.append("⚠️ NEEDS melebihi 60% - review kebutuhan pokok")
        elif needs_pct < 40:
            insights.append("✅ NEEDS sangat efisien (<40%)")
        
        if wants_pct > 40:
            insights.append("🎯 WANTS melebihi 40% - pertimbangkan lifestyle adjustment")
        
        if savings_pct < 15:
            insights.append("📈 SAVINGS di bawah 15% - tingkatkan untuk masa depan")
        elif savings_pct > 25:
            insights.append("🌟 SAVINGS excellent (>25%) - pertimbangkan investasi")
        
        return insights
    
    def _generate_50_30_20_recommendations(self, needs_pct: float, wants_pct: float, 
                                         savings_pct: float, income: float) -> List[str]:
        """Generate recommendations untuk optimizing 50/30/20 method"""
        recommendations = []
        
        # Priority recommendations berdasarkan variance terbesar
        needs_variance = abs(needs_pct - 50.0)
        wants_variance = abs(wants_pct - 30.0)
        savings_variance = abs(savings_pct - 20.0)
        
        if needs_variance > 10:
            if needs_pct > 50:
                recommendations.append("🔧 PRIORITY: Kurangi pengeluaran NEEDS dengan mencari alternatif lebih hemat")
        
        if wants_variance > 10:
            if wants_pct > 30:
                recommendations.append("🎯 PRIORITY: Kontrol WANTS spending, gunakan 30% rule sebagai limit")
        
        if savings_variance > 5:
            if savings_pct < 20:
                recommendations.append("📈 PRIORITY: Tingkatkan savings ke minimal 20% untuk financial security")
        
        # General tips
        recommendations.extend([
            "📱 Gunakan budgeting app untuk tracking real-time",
            "🔄 Review dan adjust budget setiap bulan"
        ])
        
        return recommendations
    
    # ==========================================
    # ANALYTICS METHOD
    # ==========================================
    
    async def get_prediction_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive prediction analytics untuk user"""
        try:
            logger.info(f"📊 Getting prediction analytics for user {user_id}")
            
            # Get all predictions
            income_pred = await self.predict_income(user_id, 30)
            budget_perf = await self.predict_budget_performance(user_id, 30)
            
            # Compile analytics
            analytics = {
                "user_id": user_id,
                "generated_at": datetime.now().isoformat(),
                "prediction_summary": {
                    "income_prediction_available": income_pred.get("success", False),
                    "budget_prediction_available": budget_perf.get("success", False),
                    "data_quality": "good" if income_pred.get("success") and budget_perf.get("success") else "limited"
                }
            }
            
            if income_pred.get("success"):
                analytics["income_insights"] = {
                    "predicted_monthly": income_pred.get("total_predicted_income", 0),
                    "confidence": income_pred.get("prediction_confidence", 0),
                    "recommendations": income_pred.get("recommendations", [])
                }
            
            if budget_perf.get("success"):
                analytics["budget_insights"] = {
                    "health_score": budget_perf.get("budget_health", {}).get("health_score", 0),
                    "predicted_allocations": budget_perf.get("predicted_percentages", {}),
                    "optimization_opportunities": budget_perf.get("optimization_recommendations", [])
                }
            
            return {
                "success": True,
                "analytics": analytics
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting prediction analytics: {e}")
            return {
                "success": False,
                "error": str(e)
            }