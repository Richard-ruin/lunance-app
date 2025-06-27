# app/services/analytics/prediction_service.py
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

class PredictionService:
    """Centralized prediction service for dashboard"""
    
    async def get_or_generate_prediction(
        self,
        db: AsyncIOMotorDatabase,
        student_id: ObjectId,
        prediction_type: str,
        days_ahead: int = 30
    ) -> Optional[Dict[str, Any]]:
        """Get cached prediction or generate new one"""
        
        try:
            # Check for cached prediction
            cached = await self._get_cached_prediction(
                db, student_id, prediction_type, days_ahead
            )
            
            if cached:
                return cached
            
            # Generate new prediction (simplified without Prophet for now)
            return await self._generate_simple_prediction(
                db, student_id, prediction_type, days_ahead
            )
        
        except Exception as e:
            return None
    
    async def _get_cached_prediction(
        self,
        db: AsyncIOMotorDatabase,
        student_id: ObjectId,
        prediction_type: str,
        days_ahead: int
    ) -> Optional[Dict[str, Any]]:
        """Get cached prediction if available and valid"""
        
        prediction = await db.predictions.find_one({
            "student_id": student_id,
            "prediction_type": prediction_type,
            "cache_until": {"$gt": datetime.utcnow()},
            "is_active": True
        })
        
        if prediction:
            return {
                "prediction_type": prediction_type,
                "cached": True,
                "generated_at": prediction["generated_at"],
                "forecast_summary": self._extract_simple_summary(prediction),
                "insights": prediction.get("insights", [])
            }
        
        return None
    
    async def _generate_simple_prediction(
        self,
        db: AsyncIOMotorDatabase,
        student_id: ObjectId,
        prediction_type: str,
        days_ahead: int
    ) -> Dict[str, Any]:
        """Generate simple prediction based on historical averages"""
        
        # Get historical data (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        pipeline = [
            {
                "$match": {
                    "student_id": student_id,
                    "transaction_date": {"$gte": start_date, "$lte": end_date}
                }
            }
        ]
        
        if prediction_type in ["income", "expense"]:
            pipeline[0]["$match"]["type"] = prediction_type
        
        pipeline.extend([
            {
                "$group": {
                    "_id": None,
                    "daily_avg": {"$avg": "$amount"},
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            }
        ])
        
        result = await db.transactions.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return {
                "prediction_type": prediction_type,
                "cached": False,
                "generated_at": datetime.utcnow(),
                "forecast_summary": {
                    "next_week": {"predicted_total": 0, "confidence": "low"},
                    "next_month": {"predicted_total": 0, "confidence": "low"}
                },
                "insights": [{
                    "type": "info",
                    "message": "Belum cukup data untuk membuat prediksi akurat",
                    "importance": "medium"
                }]
            }
        
        daily_avg = result[0]["daily_avg"]
        
        # Simple predictions
        week_prediction = daily_avg * 7
        month_prediction = daily_avg * days_ahead
        
        # Generate insights
        insights = []
        if prediction_type == "expense":
            if daily_avg > 50000:  # High daily spending
                insights.append({
                    "type": "warning",
                    "message": f"Pengeluaran harian rata-rata tinggi: Rp {daily_avg:,.0f}",
                    "importance": "high"
                })
            else:
                insights.append({
                    "type": "positive",
                    "message": f"Pengeluaran harian terkontrol: Rp {daily_avg:,.0f}",
                    "importance": "medium"
                })
        
        return {
            "prediction_type": prediction_type,
            "cached": False,
            "generated_at": datetime.utcnow(),
            "forecast_summary": {
                "next_week": {
                    "predicted_total": week_prediction,
                    "confidence": "medium"
                },
                "next_month": {
                    "predicted_total": month_prediction,
                    "confidence": "medium"
                }
            },
            "insights": insights,
            "model_info": {
                "method": "historical_average",
                "data_points": result[0]["count"],
                "daily_average": daily_avg
            }
        }
    
    def _extract_simple_summary(self, prediction: Dict) -> Dict[str, Any]:
        """Extract summary from cached prediction"""
        
        forecast_data = prediction.get("forecast_data", [])
        if not forecast_data:
            return {}
        
        # Calculate simple totals
        week_total = sum(f.get("predicted_value", 0) for f in forecast_data[:7])
        month_total = sum(f.get("predicted_value", 0) for f in forecast_data[:30])
        
        return {
            "next_week": {"predicted_total": week_total, "confidence": "medium"},
            "next_month": {"predicted_total": month_total, "confidence": "medium"}
        }