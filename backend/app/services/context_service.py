# app/services/context_service.py
"""Context service for maintaining chat context and user interactions."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from bson import ObjectId

from ..config.database import get_database
from ..models.ai_chat import ContextMemory, FinancialContext
from ..services.user_service import user_service
from ..services.transaction_service import transaction_service
from ..services.savings_target_service import savings_target_service

logger = logging.getLogger(__name__)


class ContextServiceError(Exception):
    """Context service related error."""
    pass


class ContextService:
    """Service for managing chat context and user interaction patterns."""
    
    def __init__(self):
        self.context_collection = "context_memory"
        self.interaction_patterns_collection = "interaction_patterns"
        self.user_preferences_collection = "user_chat_preferences"
    
    async def get_user_context(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> Optional[ContextMemory]:
        """Get user's context memory."""
        try:
            db = await get_database()
            collection = db[self.context_collection]
            
            query = {"user_id": user_id}
            if session_id:
                query["session_id"] = session_id
            
            # Get the most recent context
            context_doc = await collection.find_one(
                query,
                sort=[("updated_at", -1)]
            )
            
            if context_doc:
                return ContextMemory(**context_doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return None
    
    async def update_user_context(
        self,
        user_id: str,
        session_id: str,
        conversation_context: List[str],
        financial_insights: Optional[Dict[str, Any]] = None,
        user_goals: Optional[List[str]] = None
    ) -> bool:
        """Update user's context memory."""
        try:
            db = await get_database()
            collection = db[self.context_collection]
            
            # Get existing context or create new one
            existing_context = await collection.find_one({
                "user_id": user_id,
                "session_id": session_id
            })
            
            if existing_context:
                # Update existing context
                update_data = {
                    "conversation_context": conversation_context[-20:],  # Keep last 20 exchanges
                    "updated_at": datetime.utcnow()
                }
                
                if financial_insights:
                    update_data["financial_situation"] = financial_insights
                
                if user_goals:
                    update_data["user_goals"] = user_goals
                
                await collection.update_one(
                    {"_id": existing_context["_id"]},
                    {"$set": update_data}
                )
            else:
                # Create new context
                context_doc = {
                    "user_id": user_id,
                    "session_id": session_id,
                    "user_goals": user_goals or [],
                    "preferences": {},
                    "conversation_context": conversation_context[-20:],
                    "financial_situation": financial_insights,
                    "last_advice_given": None,
                    "interaction_patterns": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await collection.insert_one(context_doc)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user context: {e}")
            return False
    
    async def get_financial_context(self, user_id: str) -> FinancialContext:
        """Get comprehensive financial context for user."""
        try:
            # Get user stats
            user_stats = await user_service.get_user_stats(user_id)
            
            # Get recent transactions (last 30 days)
            from datetime import date, timedelta
            from ..models.common import PaginationParams
            from ..models.transaction import TransactionFilters
            
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            recent_transactions_result = await transaction_service.list_transactions(
                user_id=user_id,
                pagination=PaginationParams(page=1, per_page=20, sort_by="created_at", sort_order="desc"),
                filters=TransactionFilters(start_date=start_date, end_date=end_date)
            )
            
            # Get active savings targets
            savings_targets_result = await savings_target_service.list_savings_targets(
                user_id=user_id,
                pagination=PaginationParams(page=1, per_page=10),
                is_achieved=False
            )
            
            # Get category summary for spending patterns
            category_summary = await transaction_service.get_category_summary(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Calculate spending trends
            spending_trends = await self._calculate_spending_trends(user_id)
            
            # Calculate monthly averages
            monthly_income = user_stats.total_income / 12 if user_stats and user_stats.total_income > 0 else 0
            monthly_expense = user_stats.total_expense / 12 if user_stats and user_stats.total_expense > 0 else 0
            
            return FinancialContext(
                current_balance=user_stats.current_balance if user_stats else 0,
                monthly_income=monthly_income,
                monthly_expense=monthly_expense,
                top_categories=[
                    {
                        "name": cat.category_name,
                        "amount": cat.total_amount,
                        "percentage": cat.percentage,
                        "icon": cat.category_icon,
                        "color": cat.category_color
                    }
                    for cat in category_summary[:5]
                ],
                savings_targets=[
                    {
                        "id": target.id,
                        "name": target.target_name,
                        "progress_percentage": target.progress_percentage,
                        "current_amount": target.current_amount,
                        "target_amount": target.target_amount,
                        "target_date": target.target_date.isoformat(),
                        "days_remaining": target.days_remaining
                    }
                    for target in savings_targets_result.items
                ],
                recent_transactions=[
                    {
                        "id": trans.id,
                        "description": trans.description,
                        "amount": trans.amount,
                        "type": trans.transaction_type.value,
                        "category": trans.category_name,
                        "date": trans.transaction_date.isoformat(),
                        "category_color": trans.category_color
                    }
                    for trans in recent_transactions_result.items
                ],
                spending_trends=spending_trends
            )
            
        except Exception as e:
            logger.error(f"Error getting financial context: {e}")
            return FinancialContext(
                current_balance=0,
                monthly_income=0,
                monthly_expense=0,
                top_categories=[],
                savings_targets=[],
                recent_transactions=[],
                spending_trends={}
            )
    
    async def analyze_interaction_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user interaction patterns."""
        try:
            db = await get_database()
            
            # Get chat messages for analysis
            messages_collection = db.chat_messages
            
            # Analyze message frequency
            message_frequency = await self._analyze_message_frequency(user_id, messages_collection)
            
            # Analyze topic preferences
            topic_preferences = await self._analyze_topic_preferences(user_id, messages_collection)
            
            # Analyze response patterns
            response_patterns = await self._analyze_response_patterns(user_id, messages_collection)
            
            # Analyze session duration patterns
            session_patterns = await self._analyze_session_patterns(user_id)
            
            return {
                "message_frequency": message_frequency,
                "topic_preferences": topic_preferences,
                "response_patterns": response_patterns,
                "session_patterns": session_patterns,
                "engagement_score": self._calculate_engagement_score(
                    message_frequency, topic_preferences, session_patterns
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing interaction patterns: {e}")
            return {}
    
    async def get_personalized_recommendations(self, user_id: str) -> List[str]:
        """Get personalized recommendations based on user context."""
        try:
            # Get financial context
            financial_context = await self.get_financial_context(user_id)
            
            # Get interaction patterns
            interaction_patterns = await self.analyze_interaction_patterns(user_id)
            
            recommendations = []
            
            # Financial health recommendations
            if financial_context.current_balance < financial_context.monthly_expense:
                recommendations.append(
                    "Saldo Anda lebih rendah dari pengeluaran bulanan. Pertimbangkan untuk mengurangi pengeluaran atau mencari sumber pendapatan tambahan."
                )
            
            # Savings recommendations
            savings_rate = (financial_context.monthly_income - financial_context.monthly_expense) / financial_context.monthly_income if financial_context.monthly_income > 0 else 0
            
            if savings_rate < 0.1:
                recommendations.append(
                    "Tingkat tabungan Anda masih rendah. Coba terapkan aturan 50/30/20 untuk alokasi keuangan yang lebih baik."
                )
            elif savings_rate > 0.3:
                recommendations.append(
                    "Tingkat tabungan Anda sangat baik! Pertimbangkan untuk diversifikasi investasi."
                )
            
            # Category-specific recommendations
            if financial_context.top_categories:
                top_category = financial_context.top_categories[0]
                if top_category["percentage"] > 40:
                    recommendations.append(
                        f"Pengeluaran untuk '{top_category['name']}' sangat tinggi ({top_category['percentage']:.1f}%). Coba kurangi pengeluaran di kategori ini."
                    )
            
            # Goal-based recommendations
            for target in financial_context.savings_targets:
                if target["progress_percentage"] < 25 and target["days_remaining"] < 90:
                    recommendations.append(
                        f"Target '{target['name']}' memerlukan perhatian lebih. Tingkatkan kontribusi untuk mencapai target tepat waktu."
                    )
            
            # Interaction-based recommendations
            engagement_score = interaction_patterns.get("engagement_score", 0)
            if engagement_score < 0.3:
                recommendations.append(
                    "Gunakan chatbot lebih aktif untuk mendapatkan insight keuangan yang lebih personal."
                )
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {e}")
            return []
    
    async def update_user_goals(
        self,
        user_id: str,
        goals: List[str],
        session_id: Optional[str] = None
    ) -> bool:
        """Update user's financial goals."""
        try:
            db = await get_database()
            collection = db[self.context_collection]
            
            query = {"user_id": user_id}
            if session_id:
                query["session_id"] = session_id
            
            await collection.update_many(
                query,
                {
                    "$set": {
                        "user_goals": goals,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user goals: {e}")
            return False
    
    async def get_conversation_suggestions(self, user_id: str) -> List[str]:
        """Get conversation suggestions based on context."""
        try:
            financial_context = await self.get_financial_context(user_id)
            
            suggestions = []
            
            # Basic financial queries
            suggestions.extend([
                "Berapa saldo saya saat ini?",
                "Analisis pengeluaran bulan ini",
                "Tips untuk menabung lebih banyak",
                "Buat anggaran bulanan"
            ])
            
            # Context-aware suggestions
            if financial_context.savings_targets:
                suggestions.append("Bagaimana progress target tabungan saya?")
            
            if financial_context.recent_transactions:
                suggestions.append("Analisis transaksi terbaru saya")
            
            if len(financial_context.top_categories) > 0:
                top_category = financial_context.top_categories[0]
                suggestions.append(f"Cara mengurangi pengeluaran untuk {top_category['name']}")
            
            return suggestions[:8]  # Return top 8 suggestions
            
        except Exception as e:
            logger.error(f"Error getting conversation suggestions: {e}")
            return [
                "Berapa saldo saya?",
                "Analisis pengeluaran",
                "Tips menabung",
                "Buat anggaran"
            ]
    
    # Private helper methods
    async def _calculate_spending_trends(self, user_id: str) -> Dict[str, Any]:
        """Calculate spending trends for user."""
        try:
            # Get last 3 months of data
            monthly_summary = await transaction_service.get_monthly_summary(
                user_id=user_id,
                limit=3
            )
            
            if len(monthly_summary) < 2:
                return {"trend": "insufficient_data"}
            
            # Calculate trend
            recent_expense = monthly_summary[-1].total_expense
            previous_expense = monthly_summary[-2].total_expense
            
            if previous_expense == 0:
                trend = "stable"
                change_percentage = 0
            else:
                change_percentage = ((recent_expense - previous_expense) / previous_expense) * 100
                
                if change_percentage > 10:
                    trend = "increasing"
                elif change_percentage < -10:
                    trend = "decreasing"
                else:
                    trend = "stable"
            
            return {
                "trend": trend,
                "change_percentage": round(change_percentage, 2),
                "recent_expense": recent_expense,
                "previous_expense": previous_expense,
                "months_analyzed": len(monthly_summary)
            }
            
        except Exception as e:
            logger.error(f"Error calculating spending trends: {e}")
            return {"trend": "unknown"}
    
    async def _analyze_message_frequency(self, user_id: str, collection) -> Dict[str, Any]:
        """Analyze user's message frequency patterns."""
        try:
            # Get messages from last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "role": "user",
                        "created_at": {"$gte": thirty_days_ago}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$created_at"
                            }
                        },
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            daily_counts = await collection.aggregate(pipeline).to_list(None)
            
            total_messages = sum(item["count"] for item in daily_counts)
            avg_daily_messages = total_messages / 30 if daily_counts else 0
            
            return {
                "total_messages_30_days": total_messages,
                "avg_daily_messages": round(avg_daily_messages, 2),
                "active_days": len(daily_counts),
                "frequency_score": min(1.0, avg_daily_messages / 5)  # Normalized to 0-1
            }
            
        except Exception as e:
            logger.error(f"Error analyzing message frequency: {e}")
            return {"frequency_score": 0}
    
    async def _analyze_topic_preferences(self, user_id: str, collection) -> Dict[str, Any]:
        """Analyze user's topic preferences."""
        try:
            # Get recent messages
            recent_messages = await collection.find({
                "user_id": user_id,
                "role": "user"
            }).limit(100).to_list(100)
            
            # Simple keyword analysis
            financial_keywords = {
                "balance": ["saldo", "balance", "uang"],
                "spending": ["pengeluaran", "belanja", "spending", "expense"],
                "saving": ["tabungan", "saving", "hemat", "nabung"],
                "budget": ["anggaran", "budget", "rencana"],
                "investment": ["investasi", "investment", "saham"],
                "goal": ["target", "goal", "tujuan"]
            }
            
            topic_counts = {topic: 0 for topic in financial_keywords.keys()}
            
            for message in recent_messages:
                content = message["content"].lower()
                for topic, keywords in financial_keywords.items():
                    if any(keyword in content for keyword in keywords):
                        topic_counts[topic] += 1
            
            total_relevant_messages = sum(topic_counts.values())
            
            if total_relevant_messages > 0:
                topic_preferences = {
                    topic: round(count / total_relevant_messages, 2)
                    for topic, count in topic_counts.items()
                }
            else:
                topic_preferences = {}
            
            return {
                "topic_distribution": topic_preferences,
                "most_discussed_topic": max(topic_counts, key=topic_counts.get) if topic_counts else None,
                "financial_focus_score": min(1.0, total_relevant_messages / len(recent_messages)) if recent_messages else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing topic preferences: {e}")
            return {"financial_focus_score": 0}
    
    async def _analyze_response_patterns(self, user_id: str, collection) -> Dict[str, Any]:
        """Analyze user's response patterns."""
        try:
            # Get conversation pairs (user message -> AI response)
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$sort": {"created_at": 1}
                },
                {
                    "$group": {
                        "_id": "$session_id",
                        "messages": {
                            "$push": {
                                "role": "$role",
                                "created_at": "$created_at",
                                "processing_time": "$processing_time"
                            }
                        }
                    }
                }
            ]
            
            sessions = await collection.aggregate(pipeline).to_list(None)
            
            total_response_time = 0
            response_count = 0
            
            for session in sessions:
                messages = session["messages"]
                for i in range(len(messages) - 1):
                    if (messages[i]["role"] == "user" and 
                        messages[i + 1]["role"] == "assistant" and
                        messages[i + 1].get("processing_time")):
                        
                        total_response_time += messages[i + 1]["processing_time"]
                        response_count += 1
            
            avg_response_time = total_response_time / response_count if response_count > 0 else 0
            
            return {
                "avg_ai_response_time": round(avg_response_time, 2),
                "total_conversations": len(sessions),
                "response_satisfaction_score": max(0, min(1, (3 - avg_response_time) / 3))  # Lower response time = higher satisfaction
            }
            
        except Exception as e:
            logger.error(f"Error analyzing response patterns: {e}")
            return {"response_satisfaction_score": 0.5}
    
    async def _analyze_session_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's session patterns."""
        try:
            db = await get_database()
            sessions_collection = db.chat_sessions
            
            # Get recent sessions
            sessions = await sessions_collection.find({
                "user_id": user_id
            }).sort("created_at", -1).limit(20).to_list(20)
            
            if not sessions:
                return {"engagement_score": 0}
            
            total_messages = sum(session["message_count"] for session in sessions)
            avg_messages_per_session = total_messages / len(sessions)
            
            # Calculate session durations
            session_durations = []
            for session in sessions:
                if session.get("last_activity") and session.get("created_at"):
                    duration = (session["last_activity"] - session["created_at"]).total_seconds() / 60
                    session_durations.append(duration)
            
            avg_session_duration = sum(session_durations) / len(session_durations) if session_durations else 0
            
            return {
                "total_sessions": len(sessions),
                "avg_messages_per_session": round(avg_messages_per_session, 2),
                "avg_session_duration_minutes": round(avg_session_duration, 2),
                "session_engagement_score": min(1.0, avg_messages_per_session / 10)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing session patterns: {e}")
            return {"session_engagement_score": 0}
    
    def _calculate_engagement_score(
        self,
        message_frequency: Dict[str, Any],
        topic_preferences: Dict[str, Any],
        session_patterns: Dict[str, Any]
    ) -> float:
        """Calculate overall user engagement score."""
        try:
            # Weight different factors
            frequency_score = message_frequency.get("frequency_score", 0) * 0.3
            focus_score = topic_preferences.get("financial_focus_score", 0) * 0.3
            session_score = session_patterns.get("session_engagement_score", 0) * 0.4
            
            total_score = frequency_score + focus_score + session_score
            return round(min(1.0, total_score), 2)
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0.0


# Global context service instance
context_service = ContextService()