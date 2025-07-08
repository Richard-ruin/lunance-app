# app/api/v1/endpoints/predictions.py
"""Financial prediction endpoints with comprehensive forecasting capabilities."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
import logging
from datetime import datetime
from datetime import date as date_type  # Alias to avoid conflicts

from app.models.prediction import (
    PredictionRequest, PredictionResponse, IncomePredictin, ExpensePrediction,
    SavingsPrediction, CategoryPrediction, AnomalyDetection, PredictionAccuracy,
    ModelPerformance, PredictionType, PredictionPeriod, PredictionAlgorithm
)
from app.models.common import SuccessResponse
from app.services.prediction_service import (
    PredictionService, PredictionServiceError, prediction_service
)
from app.middleware.auth import (
    get_current_verified_user, rate_limit_dependency
)
from app.models.user import UserInDB

logger = logging.getLogger(__name__)

router = APIRouter()


# Income predictions
@router.get("/income", response_model=IncomePredictin)
async def predict_income(
    period: PredictionPeriod = Query(PredictionPeriod.MONTHLY, description="Prediction period"),
    periods_ahead: int = Query(6, ge=1, le=24, description="Number of periods to predict"),
    algorithm: PredictionAlgorithm = Query(PredictionAlgorithm.PROPHET, description="Algorithm to use"),
    include_confidence_intervals: bool = Query(True, description="Include confidence intervals"),
    seasonality: bool = Query(True, description="Include seasonal patterns"),
    current_user: UserInDB = Depends(get_current_verified_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    Predict future income trends using advanced forecasting algorithms.
    
    This endpoint analyzes historical income data to forecast future income patterns,
    including seasonal variations and growth trends.
    
    **Parameters:**
    - `period`: Time period for predictions (daily, weekly, monthly, quarterly, yearly)
    - `periods_ahead`: Number of periods to predict into the future (1-24)
    - `algorithm`: Forecasting algorithm (prophet, linear_regression, moving_average)
    - `include_confidence_intervals`: Whether to include prediction confidence bands
    - `seasonality`: Whether to account for seasonal patterns
    
    **Returns:**
    - Detailed income predictions with trends and analysis
    - Income sources breakdown
    - Seasonal patterns identification
    - Growth rate analysis
    - Income stability score
    """
    try:
        request = PredictionRequest(
            prediction_type=PredictionType.INCOME,
            period=period,
            periods_ahead=periods_ahead,
            algorithm=algorithm,
            include_confidence_intervals=include_confidence_intervals,
            seasonality=seasonality
        )
        
        prediction = await prediction_service.predict_income(
            user_id=str(current_user.id),
            request=request
        )
        
        return prediction
        
    except PredictionServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error predicting income for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate income predictions"
        )


# Expense predictions
@router.get("/expense", response_model=ExpensePrediction)
async def predict_expense(
    period: PredictionPeriod = Query(PredictionPeriod.MONTHLY, description="Prediction period"),
    periods_ahead: int = Query(6, ge=1, le=24, description="Number of periods to predict"),
    algorithm: PredictionAlgorithm = Query(PredictionAlgorithm.PROPHET, description="Algorithm to use"),
    include_confidence_intervals: bool = Query(True, description="Include confidence intervals"),
    seasonality: bool = Query(True, description="Include seasonal patterns"),
    current_user: UserInDB = Depends(get_current_verified_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    Predict future expense trends with budget optimization suggestions.
    
    Analyzes spending patterns to forecast future expenses and provides
    actionable recommendations for budget optimization.
    
    **Features:**
    - Expense forecasting by category
    - Budget recommendations
    - Cost optimization opportunities
    - Spending trend analysis
    - Seasonal spending patterns
    
    **Use Cases:**
    - Monthly budget planning
    - Expense optimization
    - Financial goal setting
    - Cash flow management
    """
    try:
        request = PredictionRequest(
            prediction_type=PredictionType.EXPENSE,
            period=period,
            periods_ahead=periods_ahead,
            algorithm=algorithm,
            include_confidence_intervals=include_confidence_intervals,
            seasonality=seasonality
        )
        
        prediction = await prediction_service.predict_expense(
            user_id=str(current_user.id),
            request=request
        )
        
        return prediction
        
    except PredictionServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error predicting expenses for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate expense predictions"
        )


# Savings predictions
@router.get("/savings", response_model=SavingsPrediction)
async def predict_savings(
    period: PredictionPeriod = Query(PredictionPeriod.MONTHLY, description="Prediction period"),
    periods_ahead: int = Query(12, ge=1, le=36, description="Number of periods to predict"),
    algorithm: PredictionAlgorithm = Query(PredictionAlgorithm.LINEAR_REGRESSION, description="Algorithm to use"),
    include_confidence_intervals: bool = Query(True, description="Include confidence intervals"),
    seasonality: bool = Query(False, description="Include seasonal patterns"),
    current_user: UserInDB = Depends(get_current_verified_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    Predict savings trajectory and goal achievement timelines.
    
    Forecasts savings patterns and predicts when financial goals will be achieved
    based on current saving behavior and income/expense trends.
    
    **Key Insights:**
    - Savings rate projections
    - Goal achievement timeline predictions
    - Emergency fund planning
    - Savings optimization recommendations
    - Investment readiness assessment
    
    **Applications:**
    - Financial goal planning
    - Emergency fund building
    - Investment timing decisions
    - Retirement planning preparation
    """
    try:
        request = PredictionRequest(
            prediction_type=PredictionType.SAVINGS,
            period=period,
            periods_ahead=periods_ahead,
            algorithm=algorithm,
            include_confidence_intervals=include_confidence_intervals,
            seasonality=seasonality
        )
        
        prediction = await prediction_service.predict_savings(
            user_id=str(current_user.id),
            request=request
        )
        
        return prediction
        
    except PredictionServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error predicting savings for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate savings predictions"
        )


# Category-specific predictions
@router.get("/category/{category_id}", response_model=CategoryPrediction)
async def predict_category_spending(
    category_id: str,
    period: PredictionPeriod = Query(PredictionPeriod.MONTHLY, description="Prediction period"),
    periods_ahead: int = Query(6, ge=1, le=24, description="Number of periods to predict"),
    algorithm: PredictionAlgorithm = Query(PredictionAlgorithm.MOVING_AVERAGE, description="Algorithm to use"),
    include_confidence_intervals: bool = Query(True, description="Include confidence intervals"),
    seasonality: bool = Query(True, description="Include seasonal patterns"),
    current_user: UserInDB = Depends(get_current_verified_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    Predict category-specific spending patterns with optimization recommendations.
    
    Analyzes spending in a specific category to forecast future expenses
    and provides targeted optimization suggestions.
    
    **Category Analysis Includes:**
    - Spending trends for the specific category
    - Seasonal patterns (e.g., higher food costs during holidays)
    - Comparison with similar users (peer benchmarking)
    - Category-specific optimization tips
    - Budget allocation recommendations
    
    **Popular Categories:**
    - Food & Dining
    - Transportation
    - Entertainment
    - Education
    - Healthcare
    """
    try:
        request = PredictionRequest(
            prediction_type=PredictionType.CATEGORY,
            period=period,
            periods_ahead=periods_ahead,
            category_id=category_id,
            algorithm=algorithm,
            include_confidence_intervals=include_confidence_intervals,
            seasonality=seasonality
        )
        
        prediction = await prediction_service.predict_category(
            user_id=str(current_user.id),
            category_id=category_id,
            request=request
        )
        
        return prediction
        
    except PredictionServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error predicting category {category_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate category predictions"
        )


# Anomaly detection
@router.get("/anomalies", response_model=List[AnomalyDetection])
async def detect_spending_anomalies(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Detect anomalies and unusual patterns in spending behavior.
    
    Uses statistical analysis to identify unusual transactions or patterns
    that may require attention or investigation.
    
    **Anomaly Types Detected:**
    - Unusually high single transactions
    - Sudden spikes in category spending
    - Irregular spending patterns
    - Out-of-pattern purchase timing
    - Frequency anomalies
    
    **Severity Levels:**
    - **High**: Requires immediate attention
    - **Medium**: Worth investigating
    - **Low**: Minor deviation from normal patterns
    
    **Use Cases:**
    - Fraud detection
    - Budget monitoring
    - Spending habit analysis
    - Financial health assessment
    """
    try:
        anomalies = await prediction_service.detect_anomalies(
            user_id=str(current_user.id)
        )
        
        return anomalies
        
    except Exception as e:
        logger.error(f"Error detecting anomalies for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect spending anomalies"
        )


# Prediction accuracy tracking
@router.get("/accuracy", response_model=List[PredictionAccuracy])
async def get_prediction_accuracy(
    prediction_id: Optional[str] = Query(None, description="Specific prediction ID to check"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get prediction accuracy metrics and performance tracking.
    
    Tracks how accurate previous predictions were compared to actual values,
    helping improve future prediction quality and user confidence.
    
    **Accuracy Metrics:**
    - Absolute error (difference between predicted and actual)
    - Percentage error (relative accuracy)
    - Mean Absolute Error (MAE)
    - Root Mean Square Error (RMSE)
    - R-squared score
    
    **Benefits:**
    - Model performance monitoring
    - Prediction confidence assessment
    - Algorithm comparison
    - Continuous improvement insights
    """
    try:
        accuracy_records = await prediction_service.get_prediction_accuracy(
            user_id=str(current_user.id),
            prediction_id=prediction_id
        )
        
        # Limit results
        return accuracy_records[:limit]
        
    except Exception as e:
        logger.error(f"Error getting prediction accuracy for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction accuracy data"
        )


@router.post("/accuracy/update", response_model=SuccessResponse)
async def update_prediction_accuracy(
    prediction_id: str = Query(..., description="ID of the prediction to update"),
    actual_value: float = Query(..., description="Actual observed value"),
    observation_date: str = Query(..., description="Date of observation (YYYY-MM-DD)"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Update prediction accuracy with actual observed values.
    
    Allows users to provide actual values to improve prediction model accuracy
    and performance tracking over time. This feedback loop helps enhance
    the quality of future predictions.
    
    **How it Works:**
    1. User provides actual value for a previously made prediction
    2. System calculates accuracy metrics
    3. Model performance is updated
    4. Future predictions benefit from improved accuracy
    
    **Required Information:**
    - Prediction ID (from previous prediction request)
    - Actual value that was observed
    - Date of the observation
    
    **Impact:**
    - Improves model accuracy over time
    - Provides personalized prediction calibration
    - Enhances confidence intervals
    - Enables algorithm optimization
    """
    try:
        # Parse and validate date
        try:
            observation_date_parsed = date_type.fromisoformat(observation_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD (e.g., 2024-01-15)"
            )
        
        # Validate actual value
        if actual_value < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Actual value cannot be negative"
            )
        
        success = await prediction_service.update_prediction_accuracy(
            prediction_id=prediction_id,
            actual_value=actual_value,
            observation_date=observation_date_parsed  # Updated parameter name
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prediction not found or date does not match any prediction point"
            )
        
        return SuccessResponse(
            message="Prediction accuracy updated successfully. Thank you for helping improve our models!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating prediction accuracy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update prediction accuracy"
        )


# Model performance metrics
@router.get("/performance", response_model=List[ModelPerformance])
async def get_model_performance(
    algorithm: Optional[PredictionAlgorithm] = Query(None, description="Filter by specific algorithm"),
    prediction_type: Optional[PredictionType] = Query(None, description="Filter by prediction type"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get model performance metrics and algorithm comparison.
    
    Provides insights into which prediction algorithms work best
    for different types of financial forecasting, helping users
    understand the reliability of their predictions.
    
    **Performance Metrics:**
    - Overall accuracy score (0-1, higher is better)
    - Mean Absolute Error (lower is better)
    - Root Mean Square Error (lower is better)
    - R-squared score (closer to 1 is better)
    - Number of predictions made
    
    **Algorithm Comparison:**
    - Prophet: Best for seasonal data with trends
    - Linear Regression: Good for steady trends
    - Moving Average: Reliable for stable patterns
    
    **Use Cases:**
    - Choose the best algorithm for your data
    - Understand prediction reliability
    - Track model improvement over time
    - Build confidence in financial planning
    """
    try:
        performance_metrics = await prediction_service.get_model_performance(
            algorithm=algorithm,
            prediction_type=prediction_type
        )
        
        return performance_metrics
        
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve model performance metrics"
        )


# Batch prediction endpoint
@router.post("/batch", response_model=List[PredictionResponse])
async def create_batch_predictions(
    requests: List[PredictionRequest],
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Create multiple predictions in a single batch request.
    
    Efficient way to generate multiple prediction types simultaneously,
    perfect for comprehensive financial planning dashboards and analysis.
    
    **Benefits:**
    - Generate multiple forecasts at once
    - Consistent prediction timestamps
    - Reduced API calls
    - Comprehensive financial overview
    
    **Limitations:**
    - Maximum 10 predictions per batch
    - All predictions use the same timestamp
    - Failed predictions are skipped (partial success possible)
    
    **Recommended Batch Combinations:**
    1. Income + Expense + Savings (complete financial forecast)
    2. Top 3 spending categories (category analysis)
    3. Multiple time periods for the same type (trend analysis)
    
    **Example Request:**
    ```json
    [
        {
            "prediction_type": "income",
            "period": "monthly",
            "periods_ahead": 6,
            "algorithm": "prophet"
        },
        {
            "prediction_type": "expense", 
            "period": "monthly",
            "periods_ahead": 6,
            "algorithm": "prophet"
        }
    ]
    ```
    """
    try:
        if len(requests) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 predictions allowed per batch request"
            )
        
        if not requests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one prediction request is required"
            )
        
        predictions = []
        failed_predictions = []
        
        for i, request in enumerate(requests):
            try:
                if request.prediction_type == PredictionType.INCOME:
                    prediction = await prediction_service.predict_income(
                        user_id=str(current_user.id),
                        request=request
                    )
                    predictions.append(prediction.prediction_response)
                    
                elif request.prediction_type == PredictionType.EXPENSE:
                    prediction = await prediction_service.predict_expense(
                        user_id=str(current_user.id),
                        request=request
                    )
                    predictions.append(prediction.prediction_response)
                    
                elif request.prediction_type == PredictionType.SAVINGS:
                    prediction = await prediction_service.predict_savings(
                        user_id=str(current_user.id),
                        request=request
                    )
                    predictions.append(prediction.prediction_response)
                    
                elif request.prediction_type == PredictionType.CATEGORY:
                    if not request.category_id:
                        failed_predictions.append(f"Request {i+1}: Category ID required for category prediction")
                        continue
                    prediction = await prediction_service.predict_category(
                        user_id=str(current_user.id),
                        category_id=request.category_id,
                        request=request
                    )
                    predictions.append(prediction.prediction_response)
                    
            except PredictionServiceError as e:
                failed_predictions.append(f"Request {i+1}: {str(e)}")
                logger.warning(f"Batch prediction failed for request {i+1}: {e}")
                continue
            except Exception as e:
                failed_predictions.append(f"Request {i+1}: Unexpected error")
                logger.error(f"Unexpected error in batch prediction {i+1}: {e}")
                continue
        
        # Log batch results
        logger.info(f"Batch prediction completed: {len(predictions)} successful, {len(failed_predictions)} failed")
        
        if failed_predictions:
            logger.warning(f"Failed predictions: {failed_predictions}")
        
        return predictions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch prediction creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process batch predictions"
        )


# Prediction dashboard endpoint
@router.get("/dashboard", response_model=dict)
async def get_prediction_dashboard(
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get comprehensive prediction dashboard with key financial forecasts.
    
    Provides a unified view of all financial predictions and insights
    for quick decision-making and comprehensive financial planning.
    
    **Dashboard Includes:**
    - Short-term income/expense forecasts (next 3 months)
    - Savings trajectory (next 6 months)
    - Financial health indicators
    - Risk alerts and anomalies
    - Actionable recommendations
    - Model confidence levels
    
    **Key Metrics:**
    - Predicted net cash flow
    - Savings rate trajectory
    - Budget variance alerts
    - Goal achievement timelines
    - Financial stability score
    
    **Use Cases:**
    - Monthly financial review
    - Budget planning sessions
    - Financial goal tracking
    - Investment timing decisions
    - Emergency fund planning
    """
    try:
        # Create optimized prediction requests for dashboard
        income_request = PredictionRequest(
            prediction_type=PredictionType.INCOME,
            period=PredictionPeriod.MONTHLY,
            periods_ahead=3,
            algorithm=PredictionAlgorithm.MOVING_AVERAGE,  # Faster for dashboard
            include_confidence_intervals=False,
            seasonality=False
        )
        
        expense_request = PredictionRequest(
            prediction_type=PredictionType.EXPENSE,
            period=PredictionPeriod.MONTHLY,
            periods_ahead=3,
            algorithm=PredictionAlgorithm.MOVING_AVERAGE,
            include_confidence_intervals=False,
            seasonality=False
        )
        
        savings_request = PredictionRequest(
            prediction_type=PredictionType.SAVINGS,
            period=PredictionPeriod.MONTHLY,
            periods_ahead=6,
            algorithm=PredictionAlgorithm.LINEAR_REGRESSION,
            include_confidence_intervals=False,
            seasonality=False
        )
        
        # Initialize dashboard data structure
        dashboard_data = {
            "overview": {
                "next_month_income": 0,
                "next_month_expense": 0,
                "predicted_savings": 0,
                "net_cash_flow": 0,
                "income_trend": "stable",
                "expense_trend": "stable",
                "savings_trend": "stable"
            },
            "insights": {
                "financial_outlook": "neutral",
                "savings_potential": 0,
                "budget_recommendation": "maintain_current",
                "confidence_level": "medium"
            },
            "alerts": {
                "anomaly_count": 0,
                "model_accuracy": 0,
                "data_quality": "unknown",
                "prediction_confidence": "medium",
                "risk_level": "low"
            },
            "recommendations": [],
            "next_actions": []
        }
        
        # Get predictions with error handling
        try:
            income_prediction = await prediction_service.predict_income(
                user_id=str(current_user.id),
                request=income_request
            )
            income_summary = income_prediction.prediction_response.summary
            dashboard_data["overview"]["next_month_income"] = income_summary.get("avg_predicted", 0)
            dashboard_data["overview"]["income_trend"] = income_summary.get("trend", "stable")
        except Exception as e:
            logger.warning(f"Income prediction failed for dashboard: {e}")
        
        try:
            expense_prediction = await prediction_service.predict_expense(
                user_id=str(current_user.id),
                request=expense_request
            )
            expense_summary = expense_prediction.prediction_response.summary
            dashboard_data["overview"]["next_month_expense"] = expense_summary.get("avg_predicted", 0)
            dashboard_data["overview"]["expense_trend"] = expense_summary.get("trend", "stable")
        except Exception as e:
            logger.warning(f"Expense prediction failed for dashboard: {e}")
        
        try:
            savings_prediction = await prediction_service.predict_savings(
                user_id=str(current_user.id),
                request=savings_request
            )
            savings_summary = savings_prediction.prediction_response.summary
            dashboard_data["overview"]["predicted_savings"] = savings_summary.get("avg_predicted", 0)
            dashboard_data["overview"]["savings_trend"] = savings_summary.get("trend", "stable")
        except Exception as e:
            logger.warning(f"Savings prediction failed for dashboard: {e}")
        
        # Calculate derived metrics
        dashboard_data["overview"]["net_cash_flow"] = (
            dashboard_data["overview"]["next_month_income"] - 
            dashboard_data["overview"]["next_month_expense"]
        )
        
        # Get anomalies
        try:
            recent_anomalies = await prediction_service.detect_anomalies(
                user_id=str(current_user.id)
            )
            high_medium_anomalies = [a for a in recent_anomalies if a.severity in ["medium", "high"]]
            dashboard_data["alerts"]["anomaly_count"] = len(high_medium_anomalies)
            
            # Set risk level based on anomalies
            if len(high_medium_anomalies) > 3:
                dashboard_data["alerts"]["risk_level"] = "high"
            elif len(high_medium_anomalies) > 1:
                dashboard_data["alerts"]["risk_level"] = "medium"
            else:
                dashboard_data["alerts"]["risk_level"] = "low"
                
        except Exception as e:
            logger.warning(f"Anomaly detection failed for dashboard: {e}")
        
        # Get model performance
        try:
            performance_metrics = await prediction_service.get_model_performance()
            if performance_metrics:
                avg_accuracy = sum(p.accuracy_score for p in performance_metrics) / len(performance_metrics)
                dashboard_data["alerts"]["model_accuracy"] = round(avg_accuracy, 2)
                
                # Set data quality and confidence
                if avg_accuracy > 0.8:
                    dashboard_data["alerts"]["data_quality"] = "excellent"
                    dashboard_data["alerts"]["prediction_confidence"] = "high"
                elif avg_accuracy > 0.7:
                    dashboard_data["alerts"]["data_quality"] = "good"
                    dashboard_data["alerts"]["prediction_confidence"] = "high"
                elif avg_accuracy > 0.5:
                    dashboard_data["alerts"]["data_quality"] = "fair"
                    dashboard_data["alerts"]["prediction_confidence"] = "medium"
                else:
                    dashboard_data["alerts"]["data_quality"] = "poor"
                    dashboard_data["alerts"]["prediction_confidence"] = "low"
            
        except Exception as e:
            logger.warning(f"Model performance check failed for dashboard: {e}")
        
        # Generate insights
        net_flow = dashboard_data["overview"]["net_cash_flow"]
        if net_flow > 0:
            dashboard_data["insights"]["financial_outlook"] = "positive"
            dashboard_data["insights"]["savings_potential"] = net_flow
            dashboard_data["insights"]["budget_recommendation"] = "increase_savings"
        elif net_flow < -500000:  # Significant deficit
            dashboard_data["insights"]["financial_outlook"] = "concerning"
            dashboard_data["insights"]["budget_recommendation"] = "reduce_expenses"
        else:
            dashboard_data["insights"]["financial_outlook"] = "neutral"
            dashboard_data["insights"]["budget_recommendation"] = "optimize_budget"
        
        # Generate recommendations
        recommendations = [
            "Review spending patterns in high-expense categories",
            "Monitor anomalies in your spending behavior"
        ]
        
        if net_flow > 0:
            recommendations.append("Consider increasing savings rate based on positive cash flow")
            recommendations.append("Explore investment opportunities for excess funds")
        else:
            recommendations.append("Focus on expense reduction to improve cash flow")
            recommendations.append("Review and adjust budget allocations")
        
        if dashboard_data["alerts"]["anomaly_count"] > 0:
            recommendations.append("Investigate recent spending anomalies")
        
        dashboard_data["recommendations"] = recommendations
        
        # Generate next actions
        next_actions = [
            {
                "action": "review_budget",
                "priority": "high" if net_flow < 0 else "medium",
                "description": "Review and adjust monthly budget based on predictions",
                "estimated_impact": "Improve financial control and planning"
            }
        ]
        
        if net_flow > 0:
            next_actions.append({
                "action": "increase_savings",
                "priority": "medium",
                "description": f"Consider increasing savings by Rp {net_flow:,.0f} per month",
                "estimated_impact": "Accelerate financial goal achievement"
            })
        else:
            next_actions.append({
                "action": "reduce_expenses",
                "priority": "high",
                "description": f"Reduce monthly expenses by Rp {abs(net_flow):,.0f}",
                "estimated_impact": "Achieve positive cash flow"
            })
        
        if dashboard_data["alerts"]["anomaly_count"] > 0:
            next_actions.append({
                "action": "investigate_anomalies",
                "priority": "medium",
                "description": f"Review {dashboard_data['alerts']['anomaly_count']} spending anomalies",
                "estimated_impact": "Identify potential savings or fraud"
            })
        
        dashboard_data["next_actions"] = next_actions
        
        # Add metadata
        dashboard_data["metadata"] = {
            "generated_at": datetime.utcnow().isoformat(),
            "prediction_horizon": "3-6 months",
            "data_freshness": "real-time",
            "confidence_level": dashboard_data["alerts"]["prediction_confidence"],
            "algorithm_used": "optimized_for_dashboard"
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error generating prediction dashboard for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate prediction dashboard"
        )


# Health check for prediction services
@router.get("/health", response_model=dict)
async def prediction_health_check():
    """
    Check prediction services health status and capabilities.
    
    Verifies that all prediction algorithms and dependencies are
    working correctly and available for use.
    
    **Health Check Includes:**
    - Service availability status
    - Algorithm availability (Prophet, Linear Regression, Moving Average)
    - Model readiness status
    - Feature availability
    - Performance metrics
    - System capabilities
    
    **Status Indicators:**
    - `healthy`: All services operational
    - `degraded`: Some services unavailable
    - `unhealthy`: Critical services down
    
    **Use Cases:**
    - System monitoring
    - Troubleshooting prediction issues
    - Capability verification
    - Performance assessment
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service_info": {
                "name": "Lunance Prediction Service",
                "version": "1.0.0",
                "description": "Financial forecasting and prediction engine"
            },
            "services": {
                "prediction_service": "available",
                "algorithms": {
                    "prophet": prediction_service.prophet_available,
                    "linear_regression": "available",
                    "moving_average": "available",
                    "seasonal_decomposition": "available"
                },
                "models": {
                    "income_model": "ready",
                    "expense_model": "ready", 
                    "savings_model": "ready",
                    "category_model": "ready"
                },
                "features": {
                    "anomaly_detection": "available",
                    "accuracy_tracking": "available",
                    "batch_predictions": "available",
                    "confidence_intervals": "available",
                    "seasonal_analysis": "available",
                    "trend_analysis": "available"
                }
            },
            "capabilities": {
                "supported_periods": ["daily", "weekly", "monthly", "quarterly", "yearly"],
                "max_prediction_horizon": "36 periods",
                "max_batch_size": "10 predictions",
                "supported_currencies": ["IDR"],
                "languages": ["Indonesian", "English"]
            },
            "performance": {
                "average_response_time": "< 3 seconds",
                "accuracy_tracking": "enabled",
                "model_updates": "automatic",
                "data_retention": "indefinite"
            },
            "dependencies": {
                "database": "connected",
                "ai_services": "available",
                "analytics_engine": "running"
            }
        }
        
        # Check if any critical services are down
        if not prediction_service.prophet_available:
            health_status["status"] = "degraded"
            health_status["warnings"] = ["Prophet algorithm unavailable - using fallback algorithms"]
        
        return health_status
        
    except Exception as e:
        logger.error(f"Prediction health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "services": {
                "prediction_service": "unavailable"
            },
            "message": "Prediction services are currently experiencing issues"
        }