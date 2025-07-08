# app/services/realtime_service.py
"""Real-time service for dashboard updates and live data."""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bson import ObjectId

from ..config.database import get_database
from ..services.transaction_service import transaction_service
from ..services.savings_target_service import savings_target_service
from ..services.user_service import user_service
from ..websocket.websocket_manager import connection_manager

logger = logging.getLogger(__name__)


class RealtimeServiceError(Exception):
    """Real-time service related error."""
    pass


class RealtimeService:
    """Service for real-time dashboard updates and live data."""
    
    def __init__(self):
        pass
    
    async def get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dashboard data dictionary
        """
        try:
            # Get user profile
            user_profile = await user_service.get_user_profile(user_id)
            
            # Get transaction summary (last 30 days)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            transaction_summary = await transaction_service.get_transaction_summary(
                user_id, start_date, end_date
            )
            
            # Get recent transactions
            recent_transactions = await self.get_recent_transactions(user_id, {"limit": 5})
            
            # Get savings targets summary
            savings_summary = await savings_target_service.get_user_savings_summary(user_id)
            
            # Get monthly summary for current year
            current_year = datetime.now().year
            monthly_summary = await transaction_service.get_monthly_summary(
                user_id, current_year, 12
            )
            
            # Get category summary (last 30 days)
            category_summary = await transaction_service.get_category_summary(
                user_id, start_date, end_date
            )
            
            # Calculate financial health score
            financial_health = await self._calculate_financial_health(user_id)
            
            return {
                "user_profile": user_profile.model_dump() if user_profile else None,
                "transaction_summary": transaction_summary.model_dump(),
                "recent_transactions": [t.model_dump() for t in recent_transactions],
                "savings_summary": savings_summary.model_dump(),
                "monthly_summary": [m.model_dump() for m in monthly_summary],
                "category_summary": [c.model_dump() for c in category_summary[:5]],  # Top 5 categories
                "financial_health": financial_health,
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data for user {user_id}: {e}")
            return {
                "error": "Failed to load dashboard data",
                "updated_at": datetime.utcnow().isoformat()
            }
    
    async def get_recent_transactions(
        self, 
        user_id: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Get recent transactions for user.
        
        Args:
            user_id: User ID
            filters: Optional filters
            
        Returns:
            List of recent transactions
        """
        try:
            from ..models.common import PaginationParams
            from ..models.transaction import TransactionFilters
            
            # Set default filters
            limit = filters.get("limit", 10) if filters else 10
            days_back = filters.get("days_back", 7) if filters else 7
            
            # Create pagination params
            pagination = PaginationParams(
                page=1,
                per_page=limit,
                sort_by="created_at",
                sort_order="desc"
            )
            
            # Create transaction filters
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            transaction_filters = TransactionFilters(
                start_date=start_date,
                end_date=end_date
            )
            
            # Get transactions
            result = await transaction_service.list_transactions(
                user_id, pagination, transaction_filters
            )
            
            return result.items
            
        except Exception as e:
            logger.error(f"Error getting recent transactions: {e}")
            return []
    
    async def get_analytics_data(
        self, 
        user_id: str, 
        period: str = "month"
    ) -> Dict[str, Any]:
        """
        Get analytics data for specified period.
        
        Args:
            user_id: User ID
            period: Analysis period (day, week, month, year)
            
        Returns:
            Analytics data
        """
        try:
            end_date = datetime.now().date()
            
            if period == "day":
                start_date = end_date
                daily_summary = await transaction_service.get_daily_summary(
                    user_id, start_date, end_date
                )
                return {
                    "period": "day",
                    "daily_summary": [d.model_dump() for d in daily_summary],
                    "generated_at": datetime.utcnow().isoformat()
                }
            
            elif period == "week":
                start_date = end_date - timedelta(days=7)
                daily_summary = await transaction_service.get_daily_summary(
                    user_id, start_date, end_date
                )
                return {
                    "period": "week",
                    "daily_summary": [d.model_dump() for d in daily_summary],
                    "generated_at": datetime.utcnow().isoformat()
                }
            
            elif period == "month":
                start_date = end_date - timedelta(days=30)
                transaction_summary = await transaction_service.get_transaction_summary(
                    user_id, start_date, end_date
                )
                category_summary = await transaction_service.get_category_summary(
                    user_id, start_date, end_date
                )
                return {
                    "period": "month",
                    "transaction_summary": transaction_summary.model_dump(),
                    "category_summary": [c.model_dump() for c in category_summary],
                    "generated_at": datetime.utcnow().isoformat()
                }
            
            elif period == "year":
                current_year = datetime.now().year
                monthly_summary = await transaction_service.get_monthly_summary(
                    user_id, current_year
                )
                return {
                    "period": "year",
                    "monthly_summary": [m.model_dump() for m in monthly_summary],
                    "generated_at": datetime.utcnow().isoformat()
                }
            
            else:
                raise ValueError(f"Invalid period: {period}")
                
        except Exception as e:
            logger.error(f"Error getting analytics data: {e}")
            return {
                "error": "Failed to load analytics data",
                "period": period,
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def broadcast_transaction_update(
        self, 
        user_id: str, 
        transaction_data: Dict[str, Any],
        action: str = "created"
    ):
        """
        Broadcast transaction update to user's dashboard.
        
        Args:
            user_id: User ID
            transaction_data: Transaction data
            action: Action performed (created, updated, deleted)
        """
        try:
            # Prepare update message
            update_message = {
                "type": "transaction_update",
                "action": action,
                "transaction": transaction_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to dashboard WebSocket
            await connection_manager.send_dashboard_update(user_id, update_message)
            
            # Also refresh transaction summary
            await self._refresh_dashboard_summary(user_id)
            
            logger.info(f"Transaction update broadcasted for user {user_id}: {action}")
            
        except Exception as e:
            logger.error(f"Error broadcasting transaction update: {e}")
    
    async def broadcast_savings_update(
        self, 
        user_id: str, 
        savings_data: Dict[str, Any],
        action: str = "updated"
    ):
        """
        Broadcast savings target update to user's dashboard.
        
        Args:
            user_id: User ID
            savings_data: Savings target data
            action: Action performed (updated, achieved, created)
        """
        try:
            # Prepare update message
            update_message = {
                "type": "savings_update",
                "action": action,
                "savings_target": savings_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to dashboard WebSocket
            await connection_manager.send_dashboard_update(user_id, update_message)
            
            # Refresh savings summary
            savings_summary = await savings_target_service.get_user_savings_summary(user_id)
            summary_update = {
                "type": "savings_summary_update",
                "summary": savings_summary.model_dump(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await connection_manager.send_dashboard_update(user_id, summary_update)
            
            logger.info(f"Savings update broadcasted for user {user_id}: {action}")
            
        except Exception as e:
            logger.error(f"Error broadcasting savings update: {e}")
    
    async def broadcast_budget_alert(
        self, 
        user_id: str, 
        budget_data: Dict[str, Any],
        alert_type: str = "warning"
    ):
        """
        Broadcast budget alert to user.
        
        Args:
            user_id: User ID
            budget_data: Budget data
            alert_type: Type of alert (warning, exceeded, reset)
        """
        try:
            # Prepare alert message
            alert_message = {
                "type": "budget_alert",
                "alert_type": alert_type,
                "budget": budget_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to dashboard WebSocket
            await connection_manager.send_dashboard_update(user_id, alert_message)
            
            # Also send as notification
            await connection_manager.send_notification(user_id, {
                "title": f"Budget {alert_type.title()}",
                "message": f"Your {budget_data.get('category', 'budget')} has {alert_type}",
                "type": "budget_alert",
                "data": budget_data
            })
            
            logger.info(f"Budget alert broadcasted for user {user_id}: {alert_type}")
            
        except Exception as e:
            logger.error(f"Error broadcasting budget alert: {e}")
    
    async def broadcast_ai_insight(
        self, 
        user_id: str, 
        insight: str,
        insight_data: Optional[Dict[str, Any]] = None
    ):
        """
        Broadcast AI insight to user.
        
        Args:
            user_id: User ID
            insight: Insight message
            insight_data: Additional insight data
        """
        try:
            # Prepare insight message
            insight_message = {
                "type": "ai_insight",
                "insight": insight,
                "data": insight_data or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to dashboard WebSocket
            await connection_manager.send_dashboard_update(user_id, insight_message)
            
            # Also send as notification
            await connection_manager.send_notification(user_id, {
                "title": "Financial Insight 💡",
                "message": insight,
                "type": "ai_insight",
                "data": insight_data or {}
            })
            
            logger.info(f"AI insight broadcasted for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting AI insight: {e}")
    
    async def send_live_chart_update(
        self, 
        user_id: str, 
        chart_type: str,
        chart_data: Dict[str, Any]
    ):
        """
        Send live chart update to user.
        
        Args:
            user_id: User ID
            chart_type: Type of chart (spending, income, savings, etc.)
            chart_data: Chart data
        """
        try:
            # Prepare chart update message
            chart_message = {
                "type": "chart_update",
                "chart_type": chart_type,
                "data": chart_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to dashboard WebSocket
            await connection_manager.send_dashboard_update(user_id, chart_message)
            
            logger.debug(f"Chart update sent for user {user_id}: {chart_type}")
            
        except Exception as e:
            logger.error(f"Error sending chart update: {e}")
    
    async def broadcast_system_update(
        self, 
        user_ids: Optional[List[str]] = None,
        message: str = "System update available",
        update_type: str = "info"
    ):
        """
        Broadcast system update to users.
        
        Args:
            user_ids: List of user IDs (if None, broadcast to all)
            message: Update message
            update_type: Type of update (info, warning, maintenance)
        """
        try:
            # Prepare system update message
            system_message = {
                "type": "system_update",
                "update_type": update_type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if user_ids:
                # Send to specific users
                for user_id in user_ids:
                    await connection_manager.send_dashboard_update(user_id, system_message)
            else:
                # Broadcast to all dashboard connections
                await connection_manager.broadcast_to_type(system_message, "dashboard")
            
            logger.info(f"System update broadcasted: {update_type} - {message}")
            
        except Exception as e:
            logger.error(f"Error broadcasting system update: {e}")
    
    async def get_live_stats(self) -> Dict[str, Any]:
        """
        Get live system statistics.
        
        Returns:
            Live system statistics
        """
        try:
            # Get connection stats
            connection_stats = connection_manager.get_connection_stats()
            
            # Get database stats
            db = await get_database()
            
            # Count active users (connected in last 24 hours)
            from datetime import datetime, timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            users_collection = db.users
            active_users = await users_collection.count_documents({
                "updated_at": {"$gte": yesterday}
            })
            
            # Count recent transactions (today)
            today = datetime.utcnow().date()
            transactions_collection = db.transactions
            today_transactions = await transactions_collection.count_documents({
                "created_at": {
                    "$gte": datetime.combine(today, datetime.min.time()),
                    "$lt": datetime.combine(today, datetime.max.time())
                }
            })
            
            # Count notifications sent today
            notifications_collection = db.notifications
            today_notifications = await notifications_collection.count_documents({
                "created_at": {
                    "$gte": datetime.combine(today, datetime.min.time()),
                    "$lt": datetime.combine(today, datetime.max.time())
                }
            })
            
            return {
                "websocket_connections": connection_stats,
                "active_users_24h": active_users,
                "transactions_today": today_transactions,
                "notifications_today": today_notifications,
                "system_health": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting live stats: {e}")
            return {
                "error": "Failed to get live stats",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _refresh_dashboard_summary(self, user_id: str):
        """Refresh dashboard summary data."""
        try:
            # Get updated transaction summary
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            transaction_summary = await transaction_service.get_transaction_summary(
                user_id, start_date, end_date
            )
            
            # Prepare summary update
            summary_update = {
                "type": "summary_update",
                "transaction_summary": transaction_summary.model_dump(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send to dashboard WebSocket
            await connection_manager.send_dashboard_update(user_id, summary_update)
            
        except Exception as e:
            logger.error(f"Error refreshing dashboard summary: {e}")
    
    async def _calculate_financial_health(self, user_id: str) -> Dict[str, Any]:
        """
        Calculate financial health score for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Financial health data
        """
        try:
            # Get last 30 days data
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            # Get transaction summary
            transaction_summary = await transaction_service.get_transaction_summary(
                user_id, start_date, end_date
            )
            
            # Get savings summary
            savings_summary = await savings_target_service.get_user_savings_summary(user_id)
            
            # Calculate health score (0-100)
            score_components = {
                "savings_rate": 0,    # 40 points max
                "expense_control": 0,  # 30 points max
                "goal_progress": 0,    # 20 points max
                "consistency": 0       # 10 points max
            }
            
            # Savings rate score (income - expense) / income
            if transaction_summary.total_income > 0:
                savings_rate = (transaction_summary.net_amount / transaction_summary.total_income) * 100
                if savings_rate > 20:
                    score_components["savings_rate"] = 40
                elif savings_rate > 10:
                    score_components["savings_rate"] = 30
                elif savings_rate > 0:
                    score_components["savings_rate"] = 20
                else:
                    score_components["savings_rate"] = 0
            
            # Expense control (consistent spending)
            if transaction_summary.transaction_count > 0:
                avg_expense = transaction_summary.total_expense / max(1, transaction_summary.transaction_count)
                if avg_expense < 100000:  # Under 100k per transaction
                    score_components["expense_control"] = 30
                elif avg_expense < 200000:  # Under 200k per transaction
                    score_components["expense_control"] = 20
                else:
                    score_components["expense_control"] = 10
            
            # Goal progress
            if savings_summary.active_targets > 0:
                progress_score = min(30, savings_summary.overall_progress / 5)  # 5% progress = 1 point
                score_components["goal_progress"] = progress_score
            
            # Consistency (having transactions regularly)
            if transaction_summary.transaction_count >= 10:  # At least 10 transactions in 30 days
                score_components["consistency"] = 10
            elif transaction_summary.transaction_count >= 5:
                score_components["consistency"] = 5
            
            total_score = sum(score_components.values())
            
            # Determine health level
            if total_score >= 80:
                health_level = "Excellent"
                health_color = "#10B981"  # Green
            elif total_score >= 60:
                health_level = "Good"
                health_color = "#F59E0B"  # Yellow
            elif total_score >= 40:
                health_level = "Fair"
                health_color = "#F97316"  # Orange
            else:
                health_level = "Needs Improvement"
                health_color = "#EF4444"  # Red
            
            return {
                "score": round(total_score),
                "level": health_level,
                "color": health_color,
                "components": score_components,
                "insights": self._generate_health_insights(score_components, transaction_summary, savings_summary),
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating financial health: {e}")
            return {
                "score": 0,
                "level": "Unknown",
                "color": "#6B7280",
                "error": "Unable to calculate",
                "calculated_at": datetime.utcnow().isoformat()
            }
    
    def _generate_health_insights(
        self, 
        score_components: Dict[str, float],
        transaction_summary: Any,
        savings_summary: Any
    ) -> List[str]:
        """Generate health insights based on score components."""
        insights = []
        
        # Savings rate insights
        if score_components["savings_rate"] < 20:
            insights.append("Consider increasing your savings rate to improve financial health")
        elif score_components["savings_rate"] >= 30:
            insights.append("Great job maintaining a healthy savings rate!")
        
        # Expense control insights
        if score_components["expense_control"] < 15:
            insights.append("Try to control your spending by setting monthly budgets")
        
        # Goal progress insights
        if score_components["goal_progress"] < 10 and savings_summary.active_targets > 0:
            insights.append("Focus on contributing regularly to your savings goals")
        elif savings_summary.active_targets == 0:
            insights.append("Set some savings goals to improve your financial planning")
        
        # Consistency insights
        if score_components["consistency"] < 5:
            insights.append("Try to track your transactions more regularly")
        
        return insights


# Global realtime service instance
realtime_service = RealtimeService