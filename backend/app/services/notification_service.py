# app/services/notification_service.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from bson import ObjectId

from ..database import get_database
from ..models.notification import Notification
from ..models.user import User
from ..models.budget import Budget
from ..models.savings_goal import SavingsGoal
from ..utils.email_service import send_email

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.db = None
        self.notification_rules = {
            "budget_alert": {
                "triggers": [
                    {"condition": "spent >= 80% of budget", "priority": "medium"},
                    {"condition": "spent >= 100% of budget", "priority": "high"}
                ],
                "frequency": "immediate"
            },
            "goal_reminder": {
                "triggers": [
                    {"condition": "goal_progress < expected_progress", "priority": "medium"},
                    {"condition": "goal_deadline < 30 days", "priority": "high"}
                ],
                "frequency": "weekly"
            },
            "spending_insight": {
                "triggers": [
                    {"condition": "unusual_spending_pattern", "priority": "low"},
                    {"condition": "seasonal_reminder", "priority": "medium"}
                ],
                "frequency": "monthly"
            },
            "weekly_summary": {
                "triggers": [
                    {"condition": "weekly_report", "priority": "low"}
                ],
                "frequency": "weekly"
            }
        }
    
    async def get_database(self):
        if not self.db:
            self.db = await get_database()
        return self.db
    
    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        priority: str = "medium",
        channels: List[str] = ["in_app"],
        data: Optional[Dict[str, Any]] = None,
        scheduled_at: Optional[datetime] = None
    ) -> str:
        """Create a new notification"""
        try:
            db = await self.get_database()
            
            notification = Notification(
                user_id=ObjectId(user_id),
                title=title,
                message=message,
                type=notification_type,
                priority=priority,
                channels=channels,
                scheduled_at=scheduled_at,
                data=data or {}
            )
            
            result = await db.notifications.insert_one(notification.dict(by_alias=True))
            
            # If immediate notification, send now
            if not scheduled_at:
                await self.send_notification(str(result.inserted_id))
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            raise
    
    async def send_notification(self, notification_id: str) -> bool:
        """Send a notification through specified channels"""
        try:
            db = await self.get_database()
            
            notification = await db.notifications.find_one({"_id": ObjectId(notification_id)})
            if not notification:
                return False
            
            user = await db.users.find_one({"_id": notification["user_id"]})
            if not user:
                return False
            
            sent_successfully = False
            
            # Send through each channel
            for channel in notification["channels"]:
                if channel == "email":
                    email_sent = await self.send_email_notification(user, notification)
                    sent_successfully = sent_successfully or email_sent
                elif channel == "push":
                    push_sent = await self.send_push_notification(user, notification)
                    sent_successfully = sent_successfully or push_sent
                elif channel == "in_app":
                    # In-app notifications are stored in database, so always successful
                    sent_successfully = True
            
            # Update notification as sent
            if sent_successfully:
                await db.notifications.update_one(
                    {"_id": ObjectId(notification_id)},
                    {"$set": {"sent_at": datetime.utcnow()}}
                )
            
            return sent_successfully
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False
    
    async def send_email_notification(self, user: Dict[str, Any], notification: Dict[str, Any]) -> bool:
        """Send email notification"""
        try:
            subject = f"Lunance - {notification['title']}"
            body = f"""
            Halo {user['nama_lengkap']},
            
            {notification['message']}
            
            Login ke aplikasi Lunance untuk melihat detail lebih lanjut.
            
            Salam,
            Tim Lunance
            """
            
            await send_email(
                to_email=user['email'],
                subject=subject,
                body=body
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False
    
    async def send_push_notification(self, user: Dict[str, Any], notification: Dict[str, Any]) -> bool:
        """Send push notification (placeholder for FCM integration)"""
        try:
            # TODO: Implement Firebase Cloud Messaging
            # This would integrate with FCM to send push notifications
            logger.info(f"Push notification sent to user {user['_id']}: {notification['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False
    
    async def check_budget_alerts(self, user_id: str) -> List[str]:
        """Check for budget alerts and create notifications"""
        try:
            db = await self.get_database()
            notifications_created = []
            
            # Get active budgets
            budgets = await db.budgets.find({
                "user_id": ObjectId(user_id),
                "is_active": True
            }).to_list(None)
            
            current_month = datetime.utcnow().month
            current_year = datetime.utcnow().year
            
            for budget in budgets:
                # Calculate current spending for this category
                spent_result = await db.transactions.aggregate([
                    {
                        "$match": {
                            "user_id": ObjectId(user_id),
                            "category_id": budget["category_id"],
                            "type": "expense",
                            "$expr": {
                                "$and": [
                                    {"$eq": [{"$month": "$date"}, current_month]},
                                    {"$eq": [{"$year": "$date"}, current_year]}
                                ]
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": None,
                            "total": {"$sum": "$amount"}
                        }
                    }
                ]).to_list(1)
                
                spent_amount = spent_result[0]["total"] if spent_result else 0
                budget_amount = budget["amount"]
                spent_percentage = (spent_amount / budget_amount) * 100
                
                # Get category name
                category = await db.categories.find_one({"_id": budget["category_id"]})
                category_name = category["nama_kategori"] if category else "Unknown Category"
                
                # Check if we should send notification
                should_notify = False
                priority = "medium"
                message = ""
                
                if spent_percentage >= 100:
                    should_notify = True
                    priority = "high"
                    message = f"Budget {category_name} sudah habis! Pengeluaran: Rp{spent_amount:,.0f} dari budget Rp{budget_amount:,.0f}"
                elif spent_percentage >= 80:
                    should_notify = True
                    priority = "medium"
                    message = f"Peringatan: Budget {category_name} sudah {spent_percentage:.0f}% terpakai. Sisa budget: Rp{budget_amount - spent_amount:,.0f}"
                
                if should_notify:
                    # Check if we already sent this alert recently
                    recent_alert = await db.notifications.find_one({
                        "user_id": ObjectId(user_id),
                        "type": "budget_alert",
                        "data.category_id": str(budget["category_id"]),
                        "created_at": {"$gte": datetime.utcnow() - timedelta(hours=24)}
                    })
                    
                    if not recent_alert:
                        notification_id = await self.create_notification(
                            user_id=user_id,
                            title="Budget Alert",
                            message=message,
                            notification_type="budget_alert",
                            priority=priority,
                            channels=["in_app", "email"] if priority == "high" else ["in_app"],
                            data={
                                "category_id": str(budget["category_id"]),
                                "category_name": category_name,
                                "spent_amount": spent_amount,
                                "budget_amount": budget_amount,
                                "spent_percentage": spent_percentage
                            }
                        )
                        notifications_created.append(notification_id)
            
            return notifications_created
            
        except Exception as e:
            logger.error(f"Error checking budget alerts: {str(e)}")
            return []
    
    async def check_goal_reminders(self, user_id: str) -> List[str]:
        """Check for savings goal reminders"""
        try:
            db = await self.get_database()
            notifications_created = []
            
            # Get active savings goals
            goals = await db.savings_goals.find({
                "user_id": ObjectId(user_id),
                "is_active": True
            }).to_list(None)
            
            for goal in goals:
                current_amount = goal.get("current_amount", 0)
                target_amount = goal["target_amount"]
                target_date = goal.get("target_date")
                
                should_notify = False
                message = ""
                priority = "medium"
                
                # Check deadline approaching
                if target_date:
                    days_left = (target_date - datetime.utcnow()).days
                    if days_left <= 30 and days_left > 0:
                        progress_percentage = (current_amount / target_amount) * 100
                        if progress_percentage < 80:  # Behind target
                            should_notify = True
                            priority = "high" if days_left <= 7 else "medium"
                            remaining_amount = target_amount - current_amount
                            message = f"Deadline {goal['nama_goal']} tinggal {days_left} hari! Masih perlu Rp{remaining_amount:,.0f} untuk mencapai target."
                
                # Check monthly progress
                expected_progress = self.calculate_expected_progress(goal)
                actual_progress = (current_amount / target_amount) * 100
                
                if actual_progress < expected_progress - 10:  # 10% behind expected
                    should_notify = True
                    monthly_target = self.calculate_monthly_target(goal)
                    message = f"Progress {goal['nama_goal']} tertinggal dari target. Nabung Rp{monthly_target:,.0f} per bulan untuk catch up!"
                
                if should_notify:
                    # Check if we already sent reminder recently
                    recent_reminder = await db.notifications.find_one({
                        "user_id": ObjectId(user_id),
                        "type": "goal_reminder",
                        "data.goal_id": str(goal["_id"]),
                        "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
                    })
                    
                    if not recent_reminder:
                        notification_id = await self.create_notification(
                            user_id=user_id,
                            title="Savings Goal Reminder",
                            message=message,
                            notification_type="goal_reminder",
                            priority=priority,
                            channels=["in_app"],
                            data={
                                "goal_id": str(goal["_id"]),
                                "goal_name": goal["nama_goal"],
                                "current_amount": current_amount,
                                "target_amount": target_amount,
                                "progress_percentage": actual_progress
                            }
                        )
                        notifications_created.append(notification_id)
            
            return notifications_created
            
        except Exception as e:
            logger.error(f"Error checking goal reminders: {str(e)}")
            return []
    
    def calculate_expected_progress(self, goal: Dict[str, Any]) -> float:
        """Calculate expected progress based on timeline"""
        if not goal.get("target_date"):
            return 0.0
        
        created_at = goal.get("created_at", datetime.utcnow())
        target_date = goal["target_date"]
        now = datetime.utcnow()
        
        total_days = (target_date - created_at).days
        elapsed_days = (now - created_at).days
        
        if total_days <= 0:
            return 100.0
        
        return min(100.0, (elapsed_days / total_days) * 100)
    
    def calculate_monthly_target(self, goal: Dict[str, Any]) -> float:
        """Calculate monthly savings target for goal"""
        if not goal.get("target_date"):
            return 0.0
        
        remaining_amount = goal["target_amount"] - goal.get("current_amount", 0)
        now = datetime.utcnow()
        target_date = goal["target_date"]
        
        months_left = max(1, (target_date.year - now.year) * 12 + (target_date.month - now.month))
        
        return remaining_amount / months_left
    
    async def generate_weekly_summary(self, user_id: str) -> Optional[str]:
        """Generate weekly financial summary notification"""
        try:
            db = await self.get_database()
            
            # Calculate weekly data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(user_id),
                        "date": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$type",
                        "total": {"$sum": "$amount"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            results = await db.transactions.aggregate(pipeline).to_list(None)
            
            income_data = next((r for r in results if r["_id"] == "income"), {"total": 0, "count": 0})
            expense_data = next((r for r in results if r["_id"] == "expense"), {"total": 0, "count": 0})
            
            total_income = income_data["total"]
            total_expense = expense_data["total"]
            net_savings = total_income - total_expense
            transaction_count = income_data["count"] + expense_data["count"]
            
            # Create summary message
            message = f"""Ringkasan Mingguan Anda:
            
💰 Pemasukan: Rp{total_income:,.0f}
💸 Pengeluaran: Rp{total_expense:,.0f}
📊 Net Savings: Rp{net_savings:,.0f}
🔢 Total Transaksi: {transaction_count}
            
{"🎉 Hebat! Anda berhasil menabung minggu ini!" if net_savings > 0 else "💡 Coba kurangi pengeluaran minggu depan ya!"}"""
            
            notification_id = await self.create_notification(
                user_id=user_id,
                title="Ringkasan Mingguan",
                message=message,
                notification_type="weekly_summary",
                priority="low",
                channels=["in_app"],
                data={
                    "total_income": total_income,
                    "total_expense": total_expense,
                    "net_savings": net_savings,
                    "transaction_count": transaction_count,
                    "week_start": start_date.isoformat(),
                    "week_end": end_date.isoformat()
                }
            )
            
            return notification_id
            
        except Exception as e:
            logger.error(f"Error generating weekly summary: {str(e)}")
            return None
    
    async def get_user_notifications(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """Get user notifications with pagination"""
        try:
            db = await self.get_database()
            
            # Build query
            query = {"user_id": ObjectId(user_id)}
            if unread_only:
                query["is_read"] = False
            
            # Get notifications
            notifications = await db.notifications.find(query)\
                .sort("created_at", -1)\
                .skip(offset)\
                .limit(limit)\
                .to_list(length=limit)
            
            # Get total count
            total_count = await db.notifications.count_documents(query)
            unread_count = await db.notifications.count_documents({
                "user_id": ObjectId(user_id),
                "is_read": False
            })
            
            # Format notifications
            formatted_notifications = []
            for notification in notifications:
                formatted_notifications.append({
                    "id": str(notification["_id"]),
                    "title": notification["title"],
                    "message": notification["message"],
                    "type": notification["type"],
                    "priority": notification["priority"],
                    "is_read": notification["is_read"],
                    "created_at": notification["created_at"],
                    "data": notification.get("data", {})
                })
            
            return {
                "notifications": formatted_notifications,
                "pagination": {
                    "total": total_count,
                    "unread": unread_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            raise
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        try:
            db = await self.get_database()
            
            result = await db.notifications.update_one(
                {
                    "_id": ObjectId(notification_id),
                    "user_id": ObjectId(user_id)
                },
                {"$set": {"is_read": True}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    async def mark_all_notifications_read(self, user_id: str) -> int:
        """Mark all notifications as read for user"""
        try:
            db = await self.get_database()
            
            result = await db.notifications.update_many(
                {
                    "user_id": ObjectId(user_id),
                    "is_read": False
                },
                {"$set": {"is_read": True}}
            )
            
            return result.modified_count
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            return 0
    
    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete notification"""
        try:
            db = await self.get_database()
            
            result = await db.notifications.delete_one({
                "_id": ObjectId(notification_id),
                "user_id": ObjectId(user_id)
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting notification: {str(e)}")
            return False