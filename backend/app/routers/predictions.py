# app/routers/predictions.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId

from ..middleware.auth_middleware import get_current_verified_user
from ..services.financial_predictor import FinancialPredictor
from ..database import get_database
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/predictions", tags=["Financial Predictions"])

@router.get("/income")
async def predict_income(
    days_ahead: int = Query(30, ge=7, le=365, description="Number of days to predict"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Predict future income using Facebook Prophet"""
    try:
        predictor = FinancialPredictor(current_user["id"])
        prediction_result = await predictor.predict_income(days_ahead)
        
        # Save prediction to database
        prediction_id = await predictor.save_prediction("income", prediction_result)
        
        return {
            "status": "success",
            "prediction_id": prediction_id,
            "prediction_type": "income",
            "days_ahead": days_ahead,
            "model_accuracy": prediction_result["accuracy"],
            "training_data_points": prediction_result["training_points"],
            "predictions": {
                "dates": [date.isoformat() for date in prediction_result["prediction_data"].dates],
                "predicted_values": prediction_result["prediction_data"].predicted_values,
                "confidence_intervals": prediction_result["prediction_data"].confidence_intervals
            },
            "summary": {
                "total_predicted_income": sum(prediction_result["prediction_data"].predicted_values),
                "avg_daily_income": sum(prediction_result["prediction_data"].predicted_values) / len(prediction_result["prediction_data"].predicted_values),
                "max_predicted": max(prediction_result["prediction_data"].predicted_values),
                "min_predicted": min(prediction_result["prediction_data"].predicted_values)
            }
        }
        
    except ValueError as e:
        raise CustomHTTPException(
            status_code=400,
            detail=str(e),
            error_code="INSUFFICIENT_DATA"
        )
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal membuat prediksi income: {str(e)}",
            error_code="PREDICTION_ERROR"
        )

@router.get("/expenses")
async def predict_expenses(
    days_ahead: int = Query(30, ge=7, le=365, description="Number of days to predict"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Predict future expenses using Facebook Prophet"""
    try:
        predictor = FinancialPredictor(current_user["id"])
        prediction_result = await predictor.predict_expenses(days_ahead)
        
        # Save prediction to database
        prediction_id = await predictor.save_prediction("expense", prediction_result)
        
        return {
            "status": "success",
            "prediction_id": prediction_id,
            "prediction_type": "expense",
            "days_ahead": days_ahead,
            "model_accuracy": prediction_result["accuracy"],
            "training_data_points": prediction_result["training_points"],
            "predictions": {
                "dates": [date.isoformat() for date in prediction_result["prediction_data"].dates],
                "predicted_values": prediction_result["prediction_data"].predicted_values,
                "confidence_intervals": prediction_result["prediction_data"].confidence_intervals
            },
            "summary": {
                "total_predicted_expense": sum(prediction_result["prediction_data"].predicted_values),
                "avg_daily_expense": sum(prediction_result["prediction_data"].predicted_values) / len(prediction_result["prediction_data"].predicted_values),
                "max_predicted": max(prediction_result["prediction_data"].predicted_values),
                "min_predicted": min(prediction_result["prediction_data"].predicted_values)
            }
        }
        
    except ValueError as e:
        raise CustomHTTPException(
            status_code=400,
            detail=str(e),
            error_code="INSUFFICIENT_DATA"
        )
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal membuat prediksi expense: {str(e)}",
            error_code="PREDICTION_ERROR"
        )

@router.get("/balance")
async def predict_balance(
    days_ahead: int = Query(30, ge=7, le=365, description="Number of days to predict"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Predict future account balance"""
    try:
        predictor = FinancialPredictor(current_user["id"])
        prediction_result = await predictor.predict_balance(days_ahead)
        
        # Save prediction to database
        prediction_id = await predictor.save_prediction("balance", prediction_result)
        
        return {
            "status": "success",
            "prediction_id": prediction_id,
            "prediction_type": "balance",
            "days_ahead": days_ahead,
            "current_balance": prediction_result["current_balance"],
            "model_accuracy": prediction_result["accuracy"],
            "training_data_points": prediction_result["training_points"],
            "predictions": {
                "dates": [date.isoformat() for date in prediction_result["prediction_data"].dates],
                "predicted_values": prediction_result["prediction_data"].predicted_values,
                "confidence_intervals": prediction_result["prediction_data"].confidence_intervals
            },
            "analysis": {
                "final_predicted_balance": prediction_result["prediction_data"].predicted_values[-1],
                "balance_change": prediction_result["prediction_data"].predicted_values[-1] - prediction_result["current_balance"],
                "lowest_predicted_balance": min(prediction_result["prediction_data"].predicted_values),
                "highest_predicted_balance": max(prediction_result["prediction_data"].predicted_values),
                "days_until_negative": self._calculate_days_until_negative(prediction_result["prediction_data"])
            }
        }
        
    except ValueError as e:
        raise CustomHTTPException(
            status_code=400,
            detail=str(e),
            error_code="INSUFFICIENT_DATA"
        )
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal membuat prediksi balance: {str(e)}",
            error_code="PREDICTION_ERROR"
        )

@router.get("/category/{category_id}")
async def predict_category_spending(
    category_id: str,
    days_ahead: int = Query(30, ge=7, le=365, description="Number of days to predict"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Predict spending for a specific category"""
    try:
        # Verify category exists and belongs to user or is global
        category = await db.categories.find_one({"_id": ObjectId(category_id)})
        if not category:
            raise CustomHTTPException(
                status_code=404,
                detail="Category not found",
                error_code="CATEGORY_NOT_FOUND"
            )
        
        # Check if user has access to this category
        if category.get("user_id") and str(category["user_id"]) != current_user["id"]:
            raise CustomHTTPException(
                status_code=403,
                detail="Access denied to this category",
                error_code="CATEGORY_ACCESS_DENIED"
            )
        
        predictor = FinancialPredictor(current_user["id"])
        prediction_result = await predictor.predict_category_spending(category_id, days_ahead)
        
        # Save prediction to database
        prediction_id = await predictor.save_prediction("category_spending", prediction_result)
        
        return {
            "status": "success",
            "prediction_id": prediction_id,
            "prediction_type": "category_spending",
            "category": {
                "id": str(category["_id"]),
                "nama": category["nama_kategori"],
                "icon": category["icon"],
                "color": category["color"]
            },
            "days_ahead": days_ahead,
            "model_accuracy": prediction_result["accuracy"],
            "training_data_points": prediction_result["training_points"],
            "predictions": {
                "dates": [date.isoformat() for date in prediction_result["prediction_data"].dates],
                "predicted_values": prediction_result["prediction_data"].predicted_values,
                "confidence_intervals": prediction_result["prediction_data"].confidence_intervals
            },
            "summary": {
                "total_predicted_spending": sum(prediction_result["prediction_data"].predicted_values),
                "avg_daily_spending": sum(prediction_result["prediction_data"].predicted_values) / len(prediction_result["prediction_data"].predicted_values),
                "max_predicted": max(prediction_result["prediction_data"].predicted_values),
                "min_predicted": min(prediction_result["prediction_data"].predicted_values)
            }
        }
        
    except ValueError as e:
        raise CustomHTTPException(
            status_code=400,
            detail=str(e),
            error_code="INSUFFICIENT_DATA"
        )
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal membuat prediksi category: {str(e)}",
            error_code="PREDICTION_ERROR"
        )

@router.post("/generate")
async def generate_all_predictions(
    days_ahead: int = Query(30, ge=7, le=365, description="Number of days to predict"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Generate all types of predictions at once"""
    try:
        predictor = FinancialPredictor(current_user["id"])
        
        results = {}
        errors = {}
        
        # Generate income prediction
        try:
            income_result = await predictor.predict_income(days_ahead)
            income_id = await predictor.save_prediction("income", income_result)
            results["income"] = {
                "prediction_id": income_id,
                "accuracy": income_result["accuracy"],
                "total_predicted": sum(income_result["prediction_data"].predicted_values)
            }
        except Exception as e:
            errors["income"] = str(e)
        
        # Generate expense prediction
        try:
            expense_result = await predictor.predict_expenses(days_ahead)
            expense_id = await predictor.save_prediction("expense", expense_result)
            results["expense"] = {
                "prediction_id": expense_id,
                "accuracy": expense_result["accuracy"],
                "total_predicted": sum(expense_result["prediction_data"].predicted_values)
            }
        except Exception as e:
            errors["expense"] = str(e)
        
        # Generate balance prediction if both income and expense succeeded
        if "income" in results and "expense" in results:
            try:
                balance_result = await predictor.predict_balance(days_ahead)
                balance_id = await predictor.save_prediction("balance", balance_result)
                results["balance"] = {
                    "prediction_id": balance_id,
                    "accuracy": balance_result["accuracy"],
                    "current_balance": balance_result["current_balance"],
                    "final_predicted_balance": balance_result["prediction_data"].predicted_values[-1]
                }
            except Exception as e:
                errors["balance"] = str(e)
        
        return {
            "status": "success" if results else "failed",
            "days_ahead": days_ahead,
            "generated_predictions": results,
            "errors": errors,
            "summary": {
                "successful_predictions": len(results),
                "failed_predictions": len(errors),
                "total_attempted": 3
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal generate predictions: {str(e)}",
            error_code="BATCH_PREDICTION_ERROR"
        )

@router.get("/accuracy")
async def get_prediction_accuracy_metrics(
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Get prediction accuracy metrics and model performance"""
    try:
        # Get recent predictions
        recent_predictions = await db.financial_predictions.find({
            "user_id": ObjectId(current_user["id"]),
            "created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
        }).to_list(None)
        
        if not recent_predictions:
            return {
                "status": "no_data",
                "message": "Belum ada prediksi dalam 30 hari terakhir",
                "accuracy_metrics": {}
            }
        
        # Calculate accuracy by prediction type
        accuracy_by_type = {}
        for prediction in recent_predictions:
            pred_type = prediction["prediction_type"]
            if pred_type not in accuracy_by_type:
                accuracy_by_type[pred_type] = []
            accuracy_by_type[pred_type].append(prediction["model_accuracy"])
        
        # Calculate summary statistics
        summary_metrics = {}
        for pred_type, accuracies in accuracy_by_type.items():
            summary_metrics[pred_type] = {
                "avg_accuracy": round(sum(accuracies) / len(accuracies), 2),
                "best_accuracy": max(accuracies),
                "worst_accuracy": min(accuracies),
                "prediction_count": len(accuracies),
                "latest_accuracy": accuracies[-1] if accuracies else 0
            }
        
        # Overall metrics
        all_accuracies = [acc for accs in accuracy_by_type.values() for acc in accs]
        overall_accuracy = sum(all_accuracies) / len(all_accuracies) if all_accuracies else 0
        
        return {
            "status": "success",
            "overall_accuracy": round(overall_accuracy, 2),
            "accuracy_by_type": summary_metrics,
            "total_predictions": len(recent_predictions),
            "analysis_period": "30 days",
            "model_performance": {
                "rating": self._get_performance_rating(overall_accuracy),
                "recommendations": self._get_accuracy_recommendations(summary_metrics)
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan accuracy metrics: {str(e)}",
            error_code="ACCURACY_METRICS_ERROR"
        )

def _calculate_days_until_negative(prediction_data) -> Optional[int]:
    """Calculate how many days until balance goes negative"""
    for i, balance in enumerate(prediction_data.predicted_values):
        if balance < 0:
            return i + 1
    return None

def _get_performance_rating(accuracy: float) -> str:
    """Get performance rating based on accuracy"""
    if accuracy >= 90:
        return "Excellent"
    elif accuracy >= 80:
        return "Good"
    elif accuracy >= 70:
        return "Fair"
    elif accuracy >= 60:
        return "Poor"
    else:
        return "Very Poor"

def _get_accuracy_recommendations(metrics: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on accuracy metrics"""
    recommendations = []
    
    for pred_type, data in metrics.items():
        if data["avg_accuracy"] < 70:
            recommendations.append(f"Accuracy {pred_type} masih rendah, tambahkan lebih banyak data transaksi")
        elif data["prediction_count"] < 5:
            recommendations.append(f"Generate lebih banyak prediksi {pred_type} untuk meningkatkan akurasi model")
    
    if not recommendations:
        recommendations.append("Model prediksi sudah cukup akurat, lanjutkan penggunaan rutin")
    
    return recommendations