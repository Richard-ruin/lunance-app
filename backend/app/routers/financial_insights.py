# app/routers/financial_insights.py
from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId

from ..middleware.auth_middleware import get_current_verified_user
from ..services.advanced_analytics import AdvancedAnalytics
from ..services.financial_predictor import FinancialPredictor
from ..database import get_database
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/financial-insights", tags=["Financial Insights"])

@router.get("")
async def get_personalized_financial_insights(
    current_user: Dict[str, Any] = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Get comprehensive personalized financial insights"""
    try:
        user_id = current_user["id"]
        
        # Get multiple analytics
        analytics = AdvancedAnalytics(user_id)
        predictor = FinancialPredictor(user_id)
        
        # Gather all insights
        insights = {
            "financial_health": await analytics.calculate_financial_health_score(),
            "cash_flow": await analytics.calculate_cash_flow(3),
            "seasonal_patterns": await analytics.analyze_seasonal_patterns(),
            "recommendations": await analytics.generate_ai_recommendations()
        }
        
        # Generate predictions if enough data
        try:
            predictions = {
                "next_month_expense": await predictor.predict_expenses(30),
                "next_month_balance": await predictor.predict_balance(30)
            }
            insights["predictions"] = predictions
        except:
            insights["predictions"] = None
        
        # Get recent transactions for pattern analysis
        recent_transactions = await db.transactions.find({
            "user_id": ObjectId(user_id),
            "date": {"$gte": datetime.utcnow() - timedelta(days=30)}
        }).sort("date", -1).limit(10).to_list(10)
        
        # Generate personalized insights
        personalized_insights = await generate_personalized_insights(
            insights, recent_transactions, db, user_id
        )
        
        return {
            "status": "success",
            "insights": personalized_insights,
            "generated_at": datetime.utcnow(),
            "user_id": user_id
        }
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mendapatkan financial insights: {str(e)}",
            error_code="FINANCIAL_INSIGHTS_ERROR"
        )

async def generate_personalized_insights(
    analytics_data: Dict[str, Any],
    recent_transactions: List[Dict[str, Any]],
    db,
    user_id: str
) -> Dict[str, Any]:
    """Generate personalized insights based on user data"""
    
    insights = {
        "summary": {
            "financial_health_score": analytics_data["financial_health"]["overall_score"],
            "risk_level": analytics_data["financial_health"]["rating"],
            "total_recommendations": len(analytics_data["recommendations"])
        },
        "key_insights": [],
        "spending_behavior": {},
        "savings_opportunities": [],
        "alerts": [],
        "achievements": []
    }
    
    # Key insights based on financial health
    health_score = analytics_data["financial_health"]["overall_score"]
    if health_score >= 80:
        insights["key_insights"].append({
            "type": "positive",
            "title": "Kesehatan Finansial Excellent",
            "description": "Anda memiliki kontrol keuangan yang sangat baik. Pertahankan kebiasaan ini!",
            "icon": "🎉"
        })
    elif health_score >= 60:
        insights["key_insights"].append({
            "type": "warning",
            "title": "Kesehatan Finansial Cukup Baik",
            "description": "Ada beberapa area yang bisa diperbaiki untuk hasil yang lebih optimal.",
            "icon": "⚡"
        })
    else:
        insights["key_insights"].append({
            "type": "alert",
            "title": "Perlu Perbaikan Finansial",
            "description": "Saatnya fokus memperbaiki kebiasaan keuangan untuk masa depan yang lebih stabil.",
            "icon": "🚨"
        })
    
    # Cash flow insights
    cash_flow = analytics_data["cash_flow"]["summary"]
    if cash_flow["average_net_flow"] > 0:
        insights["key_insights"].append({
            "type": "positive",
            "title": "Cash Flow Positif",
            "description": f"Rata-rata Anda menabung Rp{cash_flow['average_net_flow']:,.0f} per bulan. Hebat!",
            "icon": "💰"
        })
    else:
        insights["alerts"].append({
            "type": "cash_flow",
            "title": "Cash Flow Negatif",
            "description": f"Pengeluaran melebihi pemasukan Rp{abs(cash_flow['average_net_flow']):,.0f} per bulan",
            "priority": "high"
        })
    
    # Spending behavior analysis
    if recent_transactions:
        # Analyze recent spending patterns
        categories_spending = {}
        for transaction in recent_transactions:
            if transaction["type"] == "expense":
                category_id = str(transaction.get("category_id", "unknown"))
                categories_spending[category_id] = categories_spending.get(category_id, 0) + transaction["amount"]
        
        if categories_spending:
            top_category = max(categories_spending, key=categories_spending.get)
            top_amount = categories_spending[top_category]
            
            # Get category name
            category = await db.categories.find_one({"_id": ObjectId(top_category)})
            category_name = category["nama_kategori"] if category else "Unknown"
            
            insights["spending_behavior"] = {
                "top_category": {
                    "name": category_name,
                    "amount": top_amount,
                    "percentage": (top_amount / sum(categories_spending.values())) * 100
                },
                "recent_transactions_count": len([t for t in recent_transactions if t["type"] == "expense"]),
                "avg_transaction_amount": sum(t["amount"] for t in recent_transactions if t["type"] == "expense") / len([t for t in recent_transactions if t["type"] == "expense"]) if recent_transactions else 0
            }
    
    # Savings opportunities
    savings_rate = analytics_data["financial_health"]["component_scores"]["savings_rate"]
    if savings_rate < 60:
        potential_savings = cash_flow["average_expense"] * 0.1  # 10% reduction
        insights["savings_opportunities"].append({
            "title": "Kurangi Pengeluaran 10%",
            "description": f"Dengan mengurangi pengeluaran 10%, Anda bisa menabung tambahan Rp{potential_savings:,.0f} per bulan",
            "potential_amount": potential_savings,
            "difficulty": "medium"
        })
    
    # Seasonal recommendations
    seasonal_patterns = analytics_data["seasonal_patterns"]
    current_month = datetime.utcnow().month
    month_names = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
                   7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}
    
    if seasonal_patterns.get("peak_periods", {}).get("peak_month"):
        peak_month = seasonal_patterns["peak_periods"]["peak_month"]
        if peak_month in month_names.values():
            insights["key_insights"].append({
                "type": "info",
                "title": "Pattern Musiman Terdeteksi",
                "description": f"Biasanya pengeluaran tertinggi di bulan {peak_month}. Siapkan budget ekstra!",
                "icon": "📊"
            })
    
    # Achievements
    if health_score >= 80:
        insights["achievements"].append({
            "title": "Financial Health Expert",
            "description": "Mencapai skor kesehatan finansial di atas 80",
            "badge": "🏆"
        })
    
    if cash_flow["average_net_flow"] > 500000:  # 500k savings per month
        insights["achievements"].append({
            "title": "Super Saver",
            "description": "Menabung lebih dari Rp500.000 per bulan",
            "badge": "💎"
        })
    
    # Predictions insights
    if analytics_data.get("predictions"):
        predictions = analytics_data["predictions"]
        if predictions["next_month_balance"]:
            final_balance = predictions["next_month_balance"]["prediction_data"].predicted_values[-1]
            if final_balance > 0:
                insights["key_insights"].append({
                    "type": "positive",
                    "title": "Prediksi Balance Positif",
                    "description": f"Prediksi balance bulan depan: Rp{final_balance:,.0f}",
                    "icon": "📈"
                })
            else:
                insights["alerts"].append({
                    "type": "prediction",
                    "title": "Prediksi Balance Negatif",
                    "description": f"Balance diprediksi akan minus Rp{abs(final_balance):,.0f} bulan depan",
                    "priority": "high"
                })
    
    return insights