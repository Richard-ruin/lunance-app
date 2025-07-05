# app/routers/advanced_analytics.py
from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId

from ..middleware.auth_middleware import get_current_verified_user
from ..services.advanced_analytics import AdvancedAnalytics
from ..database import get_database
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/analytics", tags=["Advanced Analytics"])

@router.get("/cash-flow")
async def get_cash_flow_analysis(
    months: int = Query(6, ge=1, le=24, description="Number of months to analyze"),
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get detailed cash flow analysis"""
    try:
        analytics = AdvancedAnalytics(current_user["id"])
        cash_flow_data = await analytics.calculate_cash_flow(months)
        
        return {
            "status": "success",
            "analysis_period": f"{months} months",
            "cash_flow": cash_flow_data,
            "chart_data": {
                "type": "line",
                "data": {
                    "labels": [item["month"] for item in cash_flow_data["monthly_cash_flow"]],
                    "datasets": [
                        {
                            "label": "Income",
                            "data": [item["income"] for item in cash_flow_data["monthly_cash_flow"]],
                            "borderColor": "#10B981",
                            "backgroundColor": "rgba(16, 185, 129, 0.1)"
                        },
                        {
                            "label": "Expense", 
                            "data": [item["expense"] for item in cash_flow_data["monthly_cash_flow"]],
                            "borderColor": "#EF4444",
                            "backgroundColor": "rgba(239, 68, 68, 0.1)"
                        },
                        {
                            "label": "Net Flow",
                            "data": [item["net_flow"] for item in cash_flow_data["monthly_cash_flow"]],
                            "borderColor": "#8B5CF6",
                            "backgroundColor": "rgba(139, 92, 246, 0.1)"
                        }
                    ]
                }
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan cash flow analysis: {str(e)}",
            error_code="CASH_FLOW_ANALYSIS_ERROR"
        )

@router.get("/seasonal-patterns")
async def get_seasonal_patterns(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get seasonal spending patterns analysis"""
    try:
        analytics = AdvancedAnalytics(current_user["id"])
        seasonal_data = await analytics.analyze_seasonal_patterns()
        
        return {
            "status": "success",
            "seasonal_patterns": seasonal_data,
            "charts": {
                "monthly_spending": {
                    "type": "bar",
                    "data": {
                        "labels": list(seasonal_data["monthly_patterns"].keys()),
                        "datasets": [{
                            "label": "Monthly Spending",
                            "data": list(seasonal_data["monthly_patterns"].values()),
                            "backgroundColor": "rgba(59, 130, 246, 0.6)",
                            "borderColor": "#3B82F6"
                        }]
                    }
                },
                "weekly_spending": {
                    "type": "radar",
                    "data": {
                        "labels": list(seasonal_data["weekly_patterns"].keys()),
                        "datasets": [{
                            "label": "Weekly Spending Pattern",
                            "data": list(seasonal_data["weekly_patterns"].values()),
                            "backgroundColor": "rgba(16, 185, 129, 0.2)",
                            "borderColor": "#10B981"
                        }]
                    }
                }
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan seasonal patterns: {str(e)}",
            error_code="SEASONAL_PATTERNS_ERROR"
        )

@router.get("/financial-health")
async def get_financial_health_score(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get comprehensive financial health score and analysis"""
    try:
        analytics = AdvancedAnalytics(current_user["id"])
        health_data = await analytics.calculate_financial_health_score()
        
        return {
            "status": "success",
            "financial_health": health_data,
            "chart_data": {
                "type": "doughnut",
                "data": {
                    "labels": [
                        "Savings Rate",
                        "Budget Adherence", 
                        "Income Stability",
                        "Expense Control",
                        "Goal Progress"
                    ],
                    "datasets": [{
                        "data": [
                            health_data["component_scores"]["savings_rate"],
                            health_data["component_scores"]["budget_adherence"],
                            health_data["component_scores"]["income_stability"],
                            health_data["component_scores"]["expense_control"],
                            health_data["component_scores"]["goal_progress"]
                        ],
                        "backgroundColor": [
                            "#10B981",  # Green
                            "#3B82F6",  # Blue
                            "#8B5CF6",  # Purple
                            "#F59E0B",  # Yellow
                            "#EF4444"   # Red
                        ]
                    }]
                }
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan financial health score: {str(e)}",
            error_code="FINANCIAL_HEALTH_ERROR"
        )

@router.get("/recommendations")
async def get_ai_recommendations(
    current_user: Dict[str, Any] = Depends(get_current_verified_user)
):
    """Get AI-powered financial recommendations"""
    try:
        analytics = AdvancedAnalytics(current_user["id"])
        recommendations = await analytics.generate_ai_recommendations()
        
        # Categorize recommendations by priority
        high_priority = [r for r in recommendations if r["priority"] == "high"]
        medium_priority = [r for r in recommendations if r["priority"] == "medium"]
        low_priority = [r for r in recommendations if r["priority"] == "low"]
        
        return {
            "status": "success",
            "recommendations": {
                "all": recommendations,
                "high_priority": high_priority,
                "medium_priority": medium_priority,
                "low_priority": low_priority
            },
            "summary": {
                "total_recommendations": len(recommendations),
                "high_priority_count": len(high_priority),
                "medium_priority_count": len(medium_priority),
                "low_priority_count": len(low_priority)
            },
            "action_plan": {
                "immediate_actions": [r["action_items"][0] for r in high_priority if r["action_items"]],
                "weekly_goals": [r["action_items"][1] for r in medium_priority if len(r["action_items"]) > 1],
                "monthly_objectives": [r["action_items"][-1] for r in recommendations if r["action_items"]]
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan AI recommendations: {str(e)}",
            error_code="AI_RECOMMENDATIONS_ERROR"
        )

@router.get("/peer-comparison")
async def get_peer_comparison(
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Get anonymous peer comparison analysis"""
    try:
        user_id = ObjectId(current_user["id"])
        
        # Get user's financial metrics for last 3 months
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        
        # User's metrics
        user_pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$type",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1},
                    "avg": {"$avg": "$amount"}
                }
            }
        ]
        
        user_results = await db.transactions.aggregate(user_pipeline).to_list(None)
        
        user_income = next((r["total"] for r in user_results if r["_id"] == "income"), 0)
        user_expense = next((r["total"] for r in user_results if r["_id"] == "expense"), 0)
        user_savings_rate = ((user_income - user_expense) / user_income * 100) if user_income > 0 else 0
        
        # Peer metrics (anonymous aggregation)
        peer_pipeline = [
            {
                "$match": {
                    "date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "user_id": "$user_id",
                        "type": "$type"
                    },
                    "total": {"$sum": "$amount"}
                }
            },
            {
                "$group": {
                    "_id": {
                        "user_id": "$_id.user_id"
                    },
                    "income": {
                        "$sum": {
                            "$cond": [{"$eq": ["$_id.type", "income"]}, "$total", 0]
                        }
                    },
                    "expense": {
                        "$sum": {
                            "$cond": [{"$eq": ["$_id.type", "expense"]}, "$total", 0]
                        }
                    }
                }
            },
            {
                "$project": {
                    "income": 1,
                    "expense": 1,
                    "savings_rate": {
                        "$cond": [
                            {"$gt": ["$income", 0]},
                            {"$multiply": [{"$divide": [{"$subtract": ["$income", "$expense"]}, "$income"]}, 100]},
                            0
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_income": {"$avg": "$income"},
                    "avg_expense": {"$avg": "$expense"},
                    "avg_savings_rate": {"$avg": "$savings_rate"},
                    "median_income": {"$median": "$income"},
                    "median_expense": {"$median": "$expense"},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        peer_results = await db.transactions.aggregate(peer_pipeline).to_list(1)
        
        if not peer_results:
            return {
                "status": "no_data",
                "message": "Insufficient peer data for comparison"
            }
        
        peer_data = peer_results[0]
        
        # Calculate percentiles
        def calculate_percentile(user_value, peer_avg):
            if peer_avg == 0:
                return 50
            ratio = user_value / peer_avg
            if ratio >= 1.5:
                return 90
            elif ratio >= 1.2:
                return 75
            elif ratio >= 0.8:
                return 50
            elif ratio >= 0.6:
                return 25
            else:
                return 10
        
        comparison = {
            "income": {
                "user_value": user_income,
                "peer_average": peer_data["avg_income"],
                "peer_median": peer_data.get("median_income", peer_data["avg_income"]),
                "percentile": calculate_percentile(user_income, peer_data["avg_income"]),
                "comparison": "above" if user_income > peer_data["avg_income"] else "below"
            },
            "expense": {
                "user_value": user_expense,
                "peer_average": peer_data["avg_expense"],
                "peer_median": peer_data.get("median_expense", peer_data["avg_expense"]),
                "percentile": calculate_percentile(user_expense, peer_data["avg_expense"]),
                "comparison": "above" if user_expense > peer_data["avg_expense"] else "below"
            },
            "savings_rate": {
                "user_value": user_savings_rate,
                "peer_average": peer_data["avg_savings_rate"],
                "percentile": calculate_percentile(user_savings_rate, peer_data["avg_savings_rate"]),
                "comparison": "above" if user_savings_rate > peer_data["avg_savings_rate"] else "below"
            }
        }
        
        return {
            "status": "success",
            "peer_comparison": comparison,
            "sample_size": peer_data["count"],
            "analysis_period": "3 months",
            "insights": [
                f"Income Anda {'di atas' if comparison['income']['comparison'] == 'above' else 'di bawah'} rata-rata peer",
                f"Pengeluaran Anda {'lebih tinggi' if comparison['expense']['comparison'] == 'above' else 'lebih rendah'} dari peer",
                f"Savings rate Anda {'lebih baik' if comparison['savings_rate']['comparison'] == 'above' else 'perlu ditingkatkan'} dibanding peer"
            ]
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan peer comparison: {str(e)}",
            error_code="PEER_COMPARISON_ERROR"
        )

@router.get("/risk-assessment")
async def get_financial_risk_assessment(
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Get financial risk assessment"""
    try:
        user_id = ObjectId(current_user["id"])
        
        # Calculate risk factors
        risk_factors = {}
        
        # 1. Income volatility
        income_pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "type": "income",
                    "date": {"$gte": datetime.utcnow() - timedelta(days=180)}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date"},
                        "month": {"$month": "$date"}
                    },
                    "monthly_income": {"$sum": "$amount"}
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        
        income_results = await db.transactions.aggregate(income_pipeline).to_list(None)
        
        if len(income_results) >= 3:
            monthly_incomes = [r["monthly_income"] for r in income_results]
            income_mean = sum(monthly_incomes) / len(monthly_incomes)
            income_volatility = (max(monthly_incomes) - min(monthly_incomes)) / income_mean if income_mean > 0 else 0
            
            risk_factors["income_volatility"] = {
                "score": min(100, income_volatility * 100),
                "level": "high" if income_volatility > 0.5 else "medium" if income_volatility > 0.2 else "low"
            }
        else:
            risk_factors["income_volatility"] = {"score": 50, "level": "unknown"}
        
        # 2. Expense sustainability
        expense_pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "type": "expense",
                    "date": {"$gte": datetime.utcnow() - timedelta(days=90)}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_expense": {"$sum": "$amount"}
                }
            }
        ]
        
        expense_result = await db.transactions.aggregate(expense_pipeline).to_list(1)
        monthly_expense = (expense_result[0]["total_expense"] / 3) if expense_result else 0
        
        # Compare with income
        if len(income_results) > 0:
            avg_monthly_income = sum(r["monthly_income"] for r in income_results[-3:]) / min(3, len(income_results))
            expense_ratio = monthly_expense / avg_monthly_income if avg_monthly_income > 0 else 0
            
            risk_factors["expense_sustainability"] = {
                "score": min(100, expense_ratio * 100),
                "level": "high" if expense_ratio > 0.9 else "medium" if expense_ratio > 0.7 else "low"
            }
        else:
            risk_factors["expense_sustainability"] = {"score": 50, "level": "unknown"}
        
        # 3. Emergency fund adequacy
        current_balance_pipeline = [
            {
                "$match": {"user_id": user_id}
            },
            {
                "$group": {
                    "_id": None,
                    "total_income": {
                        "$sum": {"$cond": [{"$eq": ["$type", "income"]}, "$amount", 0]}
                    },
                    "total_expense": {
                        "$sum": {"$cond": [{"$eq": ["$type", "expense"]}, "$amount", 0]}
                    }
                }
            }
        ]
        
        balance_result = await db.transactions.aggregate(current_balance_pipeline).to_list(1)
        current_balance = 0
        if balance_result:
            current_balance = balance_result[0]["total_income"] - balance_result[0]["total_expense"]
        
        emergency_fund_months = (current_balance / monthly_expense) if monthly_expense > 0 else 0
        
        risk_factors["emergency_fund"] = {
            "score": max(0, 100 - (emergency_fund_months / 6 * 100)) if emergency_fund_months < 6 else 0,
            "level": "high" if emergency_fund_months < 1 else "medium" if emergency_fund_months < 3 else "low",
            "months_covered": emergency_fund_months
        }
        
        # 4. Budget adherence risk
        budget_risk_pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "is_active": True
                }
            }
        ]
        
        budgets = await db.budgets.find({"user_id": user_id, "is_active": True}).to_list(None)
        
        if budgets:
            total_budget = sum(b["amount"] for b in budgets)
            budget_adherence_score = (monthly_expense / total_budget * 100) if total_budget > 0 else 0
            
            risk_factors["budget_adherence"] = {
                "score": max(0, budget_adherence_score - 100) if budget_adherence_score > 100 else 0,
                "level": "high" if budget_adherence_score > 120 else "medium" if budget_adherence_score > 100 else "low"
            }
        else:
            risk_factors["budget_adherence"] = {"score": 30, "level": "medium"}
        
        # Calculate overall risk score
        risk_scores = [rf["score"] for rf in risk_factors.values()]
        overall_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        # Generate risk level and recommendations
        if overall_risk_score < 25:
            risk_level = "low"
            risk_recommendations = ["Pertahankan kebiasaan finansial yang baik", "Pertimbangkan investasi untuk pertumbuhan"]
        elif overall_risk_score < 50:
            risk_level = "medium"
            risk_recommendations = ["Tingkatkan emergency fund", "Review dan optimasi budget"]
        elif overall_risk_score < 75:
            risk_level = "high"
            risk_recommendations = ["Kurangi pengeluaran tidak penting", "Cari sumber income tambahan", "Buat emergency fund"]
        else:
            risk_level = "critical"
            risk_recommendations = ["Segera kurangi pengeluaran drastis", "Cari bantuan financial advisor", "Prioritaskan pembayaran utang"]
        
        return {
            "status": "success",
            "risk_assessment": {
                "overall_risk_score": round(overall_risk_score, 1),
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "recommendations": risk_recommendations
            },
            "details": {
                "current_balance": current_balance,
                "monthly_expense": monthly_expense,
                "emergency_fund_months": round(emergency_fund_months, 1)
            }
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan risk assessment: {str(e)}",
            error_code="RISK_ASSESSMENT_ERROR"
        )