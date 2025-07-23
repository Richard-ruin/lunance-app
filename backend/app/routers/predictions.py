# app/routers/predictions.py - Financial Predictions Router menggunakan Prophet
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import traceback
import warnings
warnings.filterwarnings('ignore')

from ..services.auth_dependency import get_current_user
from ..services.prediction_service import FinancialPredictionService
from ..models.user import User
from ..utils.timezone_utils import IndonesiaDatetime

router = APIRouter(prefix="/predictions", tags=["Financial Predictions - Prophet AI"])

def safe_json_response(status_code: int, content: dict):
    """Safe JSONResponse dengan error handling"""
    try:
        return JSONResponse(
            status_code=status_code,
            content=content
        )
    except Exception as e:
        print(f"JSON serialization error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Error dalam serialisasi data",
                "error": str(e)
            }
        )

# ==========================================
# INCOME PREDICTIONS
# ==========================================

@router.get("/income")
async def predict_income(
    forecast_days: int = Query(30, ge=7, le=90, description="Jumlah hari untuk prediksi (7-90)"),
    current_user: User = Depends(get_current_user)
):
    """
    Prediksi pemasukan user untuk periode kedepan menggunakan Prophet AI
    
    - **forecast_days**: Periode prediksi dalam hari (7-90 hari)
    - Menganalisis pola pemasukan historis
    - Memberikan confidence interval dan insights
    - Cocok untuk prediksi uang saku, freelance, dll
    """
    try:
        print(f"Income prediction request: user {current_user.id}, {forecast_days} days")
        
        # Check financial setup
        if not current_user.financial_setup_completed:
            return safe_json_response(400, {
                "success": False,
                "message": "Setup keuangan belum dilengkapi",
                "data": {
                    "setup_required": True,
                    "setup_url": "/api/v1/auth/setup-financial-50-30-20"
                }
            })
        
        # Initialize prediction service
        prediction_service = FinancialPredictionService()
        
        # Generate income prediction
        result = await prediction_service.predict_income(current_user.id, forecast_days)
        
        if not result.get("success", False):
            return safe_json_response(400, {
                "success": False,
                "message": result.get("message", "Gagal memprediksi pemasukan"),
                "error": result.get("error"),
                "suggestion": result.get("suggestion"),
                "data": {
                    "prediction_type": "income",
                    "forecast_days": forecast_days,
                    "min_required_transactions": result.get("min_required_transactions", 10)
                }
            })
        
        # Format successful response
        response_data = {
            "method": "Prophet AI Time Series Forecasting",
            "prediction_type": "income",
            "forecast_period": f"{forecast_days} hari",
            "generated_at": IndonesiaDatetime.now().isoformat(),
            
            # Prediction results
            "prediction_summary": {
                "total_predicted_income": result.get("total_predicted_income", 0),
                "average_daily_income": result.get("average_daily_income", 0),
                "formatted_total": result.get("formatted_total"),
                "formatted_daily_avg": result.get("formatted_daily_avg"),
                "confidence_level": result.get("confidence_level")
            },
            
            # Historical data used
            "historical_analysis": {
                "data_points_used": result.get("data_points_used", 0),
                "historical_data": result.get("historical_data", [])
            },
            
            # Daily predictions
            "daily_predictions": result.get("predictions", []),
            
            # Model performance
            "model_performance": result.get("model_performance", {}),
            
            # AI Insights
            "ai_insights": result.get("insights", []),
            "recommendations": result.get("recommendations", []),
            
            # Student context
            "student_context": {
                "target_audience": "Mahasiswa Indonesia",
                "common_income_sources": [
                    "Uang saku/kiriman orang tua",
                    "Part-time job",
                    "Freelance online",
                    "Beasiswa",
                    "Hasil jualan"
                ]
            }
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": f"Prediksi pemasukan {forecast_days} hari berhasil dibuat",
            "data": response_data
        })
        
    except Exception as e:
        print(f"Error in predict_income: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": "Gagal membuat prediksi pemasukan",
            "error": str(e),
            "data": {"prediction_type": "income", "forecast_days": forecast_days}
        })

# ==========================================
# EXPENSE PREDICTIONS BY BUDGET TYPE
# ==========================================

@router.get("/expense/{budget_type}")
async def predict_expense_by_budget_type(
    budget_type: str,
    forecast_days: int = Query(30, ge=7, le=90, description="Jumlah hari untuk prediksi"),
    current_user: User = Depends(get_current_user)
):
    """
    Prediksi pengeluaran berdasarkan budget type metode 50/30/20
    
    - **budget_type**: needs (50%), wants (30%), atau savings (20%)
    - **forecast_days**: Periode prediksi dalam hari
    - Menganalisis pola spending per kategori budget
    - Membandingkan dengan alokasi budget yang ideal
    """
    try:
        print(f"Expense prediction request: user {current_user.id}, {budget_type}, {forecast_days} days")
        
        # Validate budget_type
        if budget_type not in ["needs", "wants", "savings"]:
            return safe_json_response(400, {
                "success": False,
                "message": f"Budget type tidak valid: {budget_type}",
                "valid_types": ["needs", "wants", "savings"],
                "budget_explanation": {
                    "needs": "50% - Kebutuhan pokok (kos, makan, transport, pendidikan)",
                    "wants": "30% - Keinginan (hiburan, jajan, fashion, target tabungan)",
                    "savings": "20% - Tabungan masa depan (dana darurat, investasi)"
                }
            })
        
        # Check financial setup
        if not current_user.financial_setup_completed:
            return safe_json_response(400, {
                "success": False,
                "message": "Setup keuangan belum dilengkapi",
                "data": {"setup_required": True}
            })
        
        # Initialize prediction service
        prediction_service = FinancialPredictionService()
        
        # Generate expense prediction
        result = await prediction_service.predict_expense_by_budget_type(
            current_user.id, budget_type, forecast_days
        )
        
        if not result.get("success", False):
            return safe_json_response(400, {
                "success": False,
                "message": result.get("message", f"Gagal memprediksi pengeluaran {budget_type}"),
                "error": result.get("error"),
                "suggestion": result.get("suggestion"),
                "data": {
                    "prediction_type": f"{budget_type}_expense",
                    "budget_type": budget_type,
                    "forecast_days": forecast_days
                }
            })
        
        # Format successful response
        response_data = {
            "method": "Prophet AI + 50/30/20 Budget Analysis",
            "prediction_type": f"{budget_type}_expense",
            "budget_type": budget_type,
            "forecast_period": f"{forecast_days} hari",
            "generated_at": IndonesiaDatetime.now().isoformat(),
            
            # Prediction results
            "prediction_summary": {
                "total_predicted_expense": result.get("total_predicted_expense", 0),
                "average_daily_expense": result.get("average_daily_expense", 0),
                "formatted_total": result.get("formatted_total"),
                "formatted_daily_avg": result.get("formatted_daily_avg")
            },
            
            # Budget analysis
            "budget_analysis": {
                "budget_allocation": result.get("budget_allocation", {}),
                "predictions_with_budget_status": result.get("predictions_with_budget_status", [])
            },
            
            # Historical data
            "historical_analysis": {
                "data_points_used": result.get("data_points_used", 0),
                "historical_data": result.get("historical_data", [])
            },
            
            # Daily predictions with budget status
            "daily_predictions": result.get("predictions", []),
            
            # Model performance
            "model_performance": result.get("model_performance", {}),
            
            # AI Insights
            "ai_insights": result.get("insights", []),
            "budget_recommendations": result.get("recommendations", []),
            
            # Category context
            "category_context": _get_budget_type_context(budget_type)
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": f"Prediksi pengeluaran {budget_type} berhasil dibuat",
            "data": response_data
        })
        
    except Exception as e:
        print(f"Error in predict_expense_by_budget_type: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": f"Gagal membuat prediksi pengeluaran {budget_type}",
            "error": str(e),
            "data": {"prediction_type": f"{budget_type}_expense", "forecast_days": forecast_days}
        })

# ==========================================
# COMPREHENSIVE BUDGET PERFORMANCE PREDICTION
# ==========================================

@router.get("/budget-performance")
async def predict_budget_performance(
    forecast_days: int = Query(30, ge=7, le=90, description="Periode prediksi"),
    current_user: User = Depends(get_current_user)
):
    """
    Prediksi performa budget 50/30/20 secara komprehensif
    
    - Menganalisis semua kategori: income, needs, wants, savings
    - Prediksi adherence terhadap metode 50/30/20
    - AI recommendations untuk optimasi budget
    - Health score dan trend analysis
    """
    try:
        print(f"Budget performance prediction request: user {current_user.id}, {forecast_days} days")
        
        # Check financial setup
        if not current_user.financial_setup_completed:
            return safe_json_response(400, {
                "success": False,
                "message": "Setup keuangan belum dilengkapi untuk analisis budget",
                "data": {"setup_required": True}
            })
        
        # Initialize prediction service
        prediction_service = FinancialPredictionService()
        
        # Generate comprehensive budget performance prediction
        result = await prediction_service.predict_budget_performance(current_user.id, forecast_days)
        
        if not result.get("success", False):
            return safe_json_response(400, {
                "success": False,
                "message": result.get("message", "Gagal memprediksi performa budget"),
                "error": result.get("error"),
                "failed_predictions": result.get("failed_predictions", []),
                "suggestion": result.get("suggestion"),
                "data": {
                    "prediction_type": "comprehensive_budget_performance",
                    "forecast_days": forecast_days
                }
            })
        
        # Format successful response
        response_data = {
            "method": "Prophet AI + 50/30/20 Elizabeth Warren Analysis",
            "prediction_type": "comprehensive_budget_performance",
            "forecast_period": f"{forecast_days} hari",
            "generated_at": IndonesiaDatetime.now().isoformat(),
            
            # Overall prediction summary
            "prediction_summary": {
                "predicted_totals": result.get("predicted_totals", {}),
                "formatted_totals": result.get("formatted_totals", {}),
                "predicted_percentages": result.get("predicted_percentages", {}),
                "budget_health": result.get("budget_health", {})
            },
            
            # 50/30/20 Analysis
            "budget_analysis_50_30_20": {
                "target_allocation": {
                    "needs": 50.0,
                    "wants": 30.0,
                    "savings": 20.0
                },
                "predicted_allocation": result.get("predicted_percentages", {}),
                "variance_analysis": result.get("budget_comparison", {}),
                "adherence_score": result.get("budget_health", {}).get("health_score", 0)
            },
            
            # Individual predictions detail
            "detailed_predictions": {
                "income": _format_individual_prediction(result.get("individual_predictions", {}).get("income")),
                "needs_expense": _format_individual_prediction(result.get("individual_predictions", {}).get("needs")),
                "wants_expense": _format_individual_prediction(result.get("individual_predictions", {}).get("wants")),
                "savings_expense": _format_individual_prediction(result.get("individual_predictions", {}).get("savings"))
            },
            
            # AI Insights dan Recommendations
            "ai_analysis": {
                "comprehensive_insights": result.get("comprehensive_insights", []),
                "optimization_recommendations": result.get("optimization_recommendations", []),
                "budget_health_assessment": result.get("budget_health", {}),
                "failed_predictions": result.get("failed_predictions", [])
            },
            
            # Student context
            "student_guidance": {
                "budget_method": "50/30/20 Elizabeth Warren untuk Mahasiswa Indonesia",
                "explanation": {
                    "needs_50": "Kebutuhan pokok: kos, makan, transport, pendidikan",
                    "wants_30": "Keinginan: hiburan, jajan, fashion, target tabungan barang",
                    "savings_20": "Tabungan masa depan: dana darurat, investasi"
                },
                "success_indicators": [
                    "Needs tidak lebih dari 55%",
                    "Wants tidak lebih dari 35%", 
                    "Savings minimal 15-20%",
                    "Net balance positif setiap bulan"
                ]
            }
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": f"Prediksi performa budget {forecast_days} hari berhasil dibuat",
            "data": response_data
        })
        
    except Exception as e:
        print(f"Error in predict_budget_performance: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": "Gagal membuat prediksi performa budget",
            "error": str(e),
            "data": {"prediction_type": "budget_performance", "forecast_days": forecast_days}
        })

# ==========================================
# SAVINGS GOAL ACHIEVEMENT PREDICTION
# ==========================================

@router.get("/savings-goal/{goal_id}")
async def predict_savings_goal_achievement(
    goal_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Prediksi kapan target tabungan akan tercapai berdasarkan pola saving
    
    - **goal_id**: ID target tabungan yang ingin diprediksi
    - Menganalisis pola tabungan historis
    - Prediksi timeline achievement
    - Multiple scenarios (current, faster, aggressive)
    - Tips untuk mempercepat pencapaian
    """
    try:
        print(f"Savings goal prediction request: user {current_user.id}, goal {goal_id}")
        
        # Validate goal_id format
        try:
            from bson import ObjectId
            ObjectId(goal_id)
        except:
            return safe_json_response(400, {
                "success": False,
                "message": "Format goal ID tidak valid",
                "data": {"goal_id": goal_id}
            })
        
        # Check financial setup
        if not current_user.financial_setup_completed:
            return safe_json_response(400, {
                "success": False,
                "message": "Setup keuangan belum dilengkapi",
                "data": {"setup_required": True}
            })
        
        # Initialize prediction service
        prediction_service = FinancialPredictionService()
        
        # Generate savings goal prediction
        result = await prediction_service.predict_savings_goal_achievement(current_user.id, goal_id)
        
        if not result.get("success", False):
            return safe_json_response(400, {
                "success": False,
                "message": result.get("message", "Gagal memprediksi pencapaian target"),
                "error": result.get("error"),
                "suggestion": result.get("suggestion"),
                "data": {
                    "prediction_type": "savings_goal_achievement",
                    "goal_id": goal_id
                }
            })
        
        # Format successful response
        response_data = {
            "method": "Prophet AI Savings Pattern Analysis",
            "prediction_type": "savings_goal_achievement",
            "generated_at": IndonesiaDatetime.now().isoformat(),
            
            # Goal information
            "goal_info": result.get("goal_info", {}),
            "formatted_amounts": result.get("formatted_amounts", {}),
            "achievement_status": result.get("achievement_status"),
            
            # Prediction results
            "achievement_prediction": result.get("prediction", {}),
            
            # Multiple scenarios
            "achievement_scenarios": result.get("scenarios", {}),
            
            # Acceleration strategies
            "acceleration_strategies": {
                "tips": result.get("acceleration_tips", []),
                "wants_optimization": "Kurangi 20% budget WANTS untuk target ini",
                "income_boost": "Cari income tambahan dari freelance/part-time",
                "automation": "Set auto-transfer harian ke tabungan target"
            },
            
            # Student context
            "student_guidance": {
                "common_targets": [
                    "Laptop untuk kuliah (5-15 juta)",
                    "Smartphone baru (3-8 juta)",
                    "Motor untuk transport (15-25 juta)",
                    "Dana travelling (2-5 juta)",
                    "Modal usaha kecil (5-10 juta)"
                ],
                "saving_tips": [
                    "Gunakan 30% WANTS budget untuk target tabungan",
                    "Manfaatkan bonus/hadiah langsung untuk target",
                    "Jual barang tidak terpakai",
                    "Freelance skill yang dimiliki",
                    "Set milestone kecil untuk motivasi"
                ]
            }
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": "Prediksi pencapaian target tabungan berhasil dibuat",
            "data": response_data
        })
        
    except Exception as e:
        print(f"Error in predict_savings_goal_achievement: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": "Gagal membuat prediksi pencapaian target",
            "error": str(e),
            "data": {"prediction_type": "savings_goal", "goal_id": goal_id}
        })

# ==========================================
# PREDICTION ANALYTICS & INSIGHTS
# ==========================================

@router.get("/analytics")
async def get_prediction_analytics(
    current_user: User = Depends(get_current_user)
):
    """
    Comprehensive analytics dari semua prediksi keuangan user
    
    - Summary dari semua jenis prediksi
    - Data quality assessment
    - Prediction confidence scores
    - Actionable insights dan recommendations
    """
    try:
        print(f"Prediction analytics request: user {current_user.id}")
        
        # Check financial setup
        if not current_user.financial_setup_completed:
            return safe_json_response(400, {
                "success": False,
                "message": "Setup keuangan belum dilengkapi untuk analytics",
                "data": {"setup_required": True}
            })
        
        # Initialize prediction service
        prediction_service = FinancialPredictionService()
        
        # Get comprehensive analytics
        result = await prediction_service.get_prediction_analytics(current_user.id)
        
        if not result.get("success", False):
            return safe_json_response(400, {
                "success": False,
                "message": "Gagal mengambil analytics prediksi",
                "error": result.get("error"),
                "data": {"analytics_type": "comprehensive"}
            })
        
        analytics = result.get("analytics", {})
        
        # Format response
        response_data = {
            "method": "Prophet AI Comprehensive Analytics",
            "analytics_type": "comprehensive_prediction_analytics",
            "generated_at": IndonesiaDatetime.now().isoformat(),
            
            # User info
            "user_info": {
                "user_id": current_user.id,
                "username": current_user.username,
                "financial_setup_completed": current_user.financial_setup_completed,
                "budget_method": "50/30/20 Elizabeth Warren"
            },
            
            # Prediction availability
            "prediction_summary": analytics.get("prediction_summary", {}),
            
            # Income insights
            "income_analytics": analytics.get("income_insights", {}),
            
            # Budget insights
            "budget_analytics": analytics.get("budget_insights", {}),
            
            # Overall recommendations
            "ai_recommendations": {
                "data_improvement": [
                    "Catat lebih banyak transaksi untuk prediksi akurat",
                    "Konsisten input transaksi minimal 3 bulan",
                    "Kategorisasi transaksi dengan benar"
                ],
                "prediction_optimization": [
                    "Review prediksi setiap 2 minggu",
                    "Bandingkan actual vs predicted untuk learning",
                    "Adjust budget berdasarkan insights AI"
                ],
                "financial_health": [
                    "Maintain 50/30/20 allocation sebisa mungkin",
                    "Build emergency fund minimal 3 bulan expense",
                    "Diversifikasi income sources untuk stabilitas"
                ]
            },
            
            # Student guidance
            "student_guidance": {
                "prediction_benefits": [
                    "Planning budget bulanan lebih akurat",
                    "Prediksi kapan bisa beli barang yang diinginkan",
                    "Early warning untuk overspending",
                    "Optimasi allocation 50/30/20"
                ],
                "next_steps": [
                    "Review prediksi income untuk planning",
                    "Set budget berdasarkan expense predictions",
                    "Monitor actual vs predicted weekly",
                    "Adjust lifestyle berdasarkan insights"
                ]
            }
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": "Analytics prediksi berhasil diambil",
            "data": response_data
        })
        
    except Exception as e:
        print(f"Error in get_prediction_analytics: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": "Gagal mengambil analytics prediksi",
            "error": str(e),
            "data": {"analytics_type": "comprehensive"}
        })

# ==========================================
# PREDICTION HISTORY & COMPARISON
# ==========================================

@router.get("/history")
async def get_prediction_history(
    prediction_type: Optional[str] = Query(None, description="Filter by prediction type"),
    limit: int = Query(10, ge=1, le=50, description="Jumlah prediksi yang diambil"),
    current_user: User = Depends(get_current_user)
):
    """
    History prediksi yang pernah dibuat user dengan perbandingan akurasi
    
    - **prediction_type**: Filter berdasarkan jenis prediksi
    - **limit**: Jumlah history yang diambil
    - Menampilkan akurasi prediksi vs actual
    - Learning insights dari prediksi sebelumnya
    """
    try:
        print(f"Prediction history request: user {current_user.id}")
        
        # For now, return placeholder response since we haven't implemented prediction storage
        # In production, this would query stored predictions and compare with actual data
        
        response_data = {
            "method": "Prediction History Analysis",
            "history_type": "prediction_accuracy_tracking",
            "generated_at": IndonesiaDatetime.now().isoformat(),
            
            # Placeholder data structure
            "history_summary": {
                "total_predictions_made": 0,
                "average_accuracy": 0.0,
                "best_performing_type": "income",
                "improvement_trend": "stable"
            },
            
            "prediction_history": [],
            
            # Guidance for future implementation
            "implementation_notes": {
                "status": "Coming Soon",
                "description": "Fitur ini akan menyimpan history prediksi dan membandingkan dengan data actual",
                "benefits": [
                    "Track akurasi prediksi dari waktu ke waktu",
                    "Learning insights untuk improvement",
                    "Personalized model optimization",
                    "Historical trend analysis"
                ]
            },
            
            "next_steps": [
                "Buat lebih banyak prediksi untuk data",
                "Input transaksi actual secara konsisten",
                "Review prediksi vs actual secara berkala"
            ]
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": "Prediction history (placeholder) berhasil diambil",
            "data": response_data
        })
        
    except Exception as e:
        print(f"Error in get_prediction_history: {e}")
        traceback.print_exc()
        
        return safe_json_response(500, {
            "success": False,
            "message": "Gagal mengambil history prediksi",
            "error": str(e)
        })

# ==========================================
# UTILITY ENDPOINTS
# ==========================================

@router.get("/info")
async def get_prediction_info():
    """
    Informasi tentang sistem prediksi keuangan dan capabilities
    """
    try:
        info_data = {
            "prediction_system": {
                "name": "Financial Predictions AI",
                "powered_by": "Facebook Prophet + Custom Financial Models",
                "target_audience": "Mahasiswa Indonesia",
                "budget_method": "50/30/20 Elizabeth Warren",
                "version": "1.0.0"
            },
            
            "capabilities": {
                "income_prediction": {
                    "description": "Prediksi pemasukan berdasarkan pola historis",
                    "min_data_required": "10 transaksi income",
                    "forecast_range": "7-90 hari",
                    "accuracy_typical": "70-85%"
                },
                "expense_prediction": {
                    "description": "Prediksi pengeluaran per budget type (needs/wants/savings)",
                    "categories": ["needs", "wants", "savings"],
                    "budget_integration": "Terintegrasi dengan metode 50/30/20",
                    "accuracy_typical": "65-80%"
                },
                "budget_performance": {
                    "description": "Prediksi comprehensive adherence terhadap 50/30/20",
                    "analysis_depth": "Multi-category dengan health scoring",
                    "recommendations": "AI-powered optimization tips"
                },
                "savings_goals": {
                    "description": "Prediksi timeline pencapaian target tabungan",
                    "scenarios": "Multiple pace scenarios",
                    "acceleration_tips": "Personalized strategies"
                }
            },
            
            "data_requirements": {
                "minimum_transactions": {
                    "income": 5,
                    "expense_per_category": 5,
                    "time_period": "Minimal 2-3 bulan data"
                },
                "optimal_data": {
                    "transactions": "50+ transaksi",
                    "time_period": "6+ bulan data",
                    "consistency": "Regular transaction input"
                }
            },
            
            "accuracy_factors": {
                "data_quality": "Konsistensi dan kelengkapan input",
                "seasonality": "Pola bulanan dan semester",
                "user_behavior": "Stability pola spending/earning",
                "external_factors": "Economic conditions, life changes"
            },
            
            "usage_tips": {
                "for_students": [
                    "Input semua transaksi secara konsisten",
                    "Kategorisasi dengan benar (needs/wants/savings)",
                    "Review prediksi vs actual setiap bulan",
                    "Gunakan insights untuk budget planning"
                ],
                "prediction_frequency": [
                    "Income: Update setiap 2 minggu",
                    "Budget performance: Monthly review",
                    "Savings goals: Check progress weekly"
                ]
            },
            
            "technical_details": {
                "model": "Facebook Prophet Time Series",
                "seasonality": "Custom semester + monthly patterns",
                "confidence_intervals": "80% default",
                "update_frequency": "Real-time dengan new data"
            }
        }
        
        return safe_json_response(200, {
            "success": True,
            "message": "Informasi sistem prediksi berhasil diambil",
            "data": info_data
        })
        
    except Exception as e:
        print(f"Error in get_prediction_info: {e}")
        return safe_json_response(500, {
            "success": False,
            "message": "Gagal mengambil informasi prediksi",
            "error": str(e)
        })

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def _format_individual_prediction(prediction_result: Optional[Dict]) -> Dict[str, Any]:
    """Format individual prediction result untuk response"""
    if not prediction_result or not prediction_result.get("success"):
        return {
            "available": False,
            "error": prediction_result.get("error") if prediction_result else "No data"
        }
    
    return {
        "available": True,
        "total_predicted": prediction_result.get("total_predicted_income") or prediction_result.get("total_predicted_expense", 0),
        "daily_average": prediction_result.get("average_daily_income") or prediction_result.get("average_daily_expense", 0),
        "confidence": prediction_result.get("prediction_confidence", 0),
        "data_points": prediction_result.get("data_points_used", 0),
        "insights": prediction_result.get("insights", [])[:3],  # Top 3 insights
        "recommendations": prediction_result.get("recommendations", [])[:3]  # Top 3 recommendations
    }

def _get_budget_type_context(budget_type: str) -> Dict[str, Any]:
    """Get context information untuk budget type"""
    contexts = {
        "needs": {
            "percentage": 50,
            "description": "Kebutuhan pokok yang harus dipenuhi",
            "categories": [
                "Makanan Pokok",
                "Kos/Tempat Tinggal", 
                "Transportasi Wajib",
                "Pendidikan",
                "Internet & Komunikasi",
                "Kesehatan & Kebersihan"
            ],
            "optimization_tips": [
                "Cari alternatif lebih hemat untuk kebutuhan",
                "Bulk buying untuk groceries",
                "Gunakan transport umum",
                "Share kos dengan teman"
            ]
        },
        "wants": {
            "percentage": 30,
            "description": "Keinginan dan lifestyle yang menyenangkan",
            "categories": [
                "Hiburan & Sosial",
                "Jajan & Snack",
                "Pakaian & Aksesoris", 
                "Organisasi & Event",
                "Target Tabungan Barang"
            ],
            "optimization_tips": [
                "Prioritaskan wants yang paling penting",
                "Gunakan untuk target tabungan barang",
                "Set spending limit harian",
                "Cari alternatif hiburan gratis"
            ]
        },
        "savings": {
            "percentage": 20,
            "description": "Tabungan untuk masa depan dan security",
            "categories": [
                "Tabungan Umum",
                "Dana Darurat",
                "Investasi Masa Depan",
                "Tabungan Jangka Panjang"
            ],
            "optimization_tips": [
                "Automation transfer ke tabungan",
                "Pisahkan rekening tabungan",
                "Prioritaskan emergency fund dulu",
                "Pelajari investasi sederhana"
            ]
        }
    }
    
    return contexts.get(budget_type, {})