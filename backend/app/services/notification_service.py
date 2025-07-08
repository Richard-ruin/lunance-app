# app/services/notification_service.py
"""Layanan notifikasi lengkap dengan dukungan bahasa Indonesia untuk Lunance."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bson import ObjectId

from ..config.database import get_database
from ..models.notification import (
    NotificationInDB, NotificationCreate, NotificationResponse, 
    NotificationSettings, NotificationSettingsUpdate, NotificationTemplate,
    NotificationDigest, NotificationStats, NotificationType, NotificationPriority
)
from ..models.common import PaginatedResponse, PaginationParams
from ..services.email_service import EmailService

logger = logging.getLogger(__name__)


class NotificationServiceError(Exception):
    """Exception untuk error layanan notifikasi."""
    pass


class NotificationService:
    """Layanan notifikasi komprehensif dengan dukungan bahasa Indonesia."""
    
    def __init__(self):
        self.collection_name = "notifications"
        self.settings_collection_name = "notification_settings"
        self.templates_collection_name = "notification_templates"
        self.digests_collection_name = "notification_digests"
        self.email_service = EmailService()
        
        # Template notifikasi dalam bahasa Indonesia
        self.default_templates = {
            NotificationType.TRANSACTION: {
                "title": "Transaksi Baru Ditambahkan",
                "message_templates": {
                    "income": "Anda telah mencatat pendapatan sebesar {amount_formatted} untuk kategori {category}",
                    "expense": "Anda telah mencatat pengeluaran sebesar {amount_formatted} untuk kategori {category}"
                },
                "action_text": "Lihat Transaksi",
                "priority": NotificationPriority.NORMAL
            },
            NotificationType.SAVINGS_GOAL: {
                "title": "Update Target Tabungan",
                "message_templates": {
                    "progress": "Target tabungan '{goal_name}' Anda sekarang {progress}% tercapai",
                    "achieved": "🎉 Selamat! Target tabungan '{goal_name}' telah tercapai!",
                    "reminder": "Jangan lupa untuk menabung ke target '{goal_name}' Anda",
                    "deadline_warning": "Target tabungan '{goal_name}' akan berakhir dalam {days_left} hari"
                },
                "action_text": "Lihat Target",
                "priority": NotificationPriority.NORMAL
            },
            NotificationType.BUDGET_ALERT: {
                "title": "Peringatan Anggaran",
                "message_templates": {
                    "warning": "Anggaran kategori {category} sudah terpakai {percentage}% ({amount_used} dari {budget_limit})",
                    "exceeded": "⚠️ Anggaran kategori {category} telah terlampaui sebesar {excess_amount}",
                    "reset": "Anggaran kategori {category} telah direset untuk periode baru"
                },
                "action_text": "Kelola Anggaran",
                "priority": NotificationPriority.HIGH
            },
            NotificationType.AI_INSIGHT: {
                "title": "Wawasan Keuangan",
                "message_templates": {
                    "spending_pattern": "💡 {insight}",
                    "saving_tip": "💰 Tips: {tip}",
                    "budget_recommendation": "📊 Rekomendasi: {recommendation}"
                },
                "action_text": "Pelajari Lebih Lanjut",
                "priority": NotificationPriority.NORMAL
            },
            NotificationType.REMINDER: {
                "title": "Pengingat",
                "message_templates": {
                    "daily": "⏰ {reminder_text}",
                    "weekly": "📅 {reminder_text}",
                    "monthly": "📆 {reminder_text}"
                },
                "action_text": "Lihat Detail",
                "priority": NotificationPriority.NORMAL
            },
            NotificationType.SYSTEM: {
                "title": "Pemberitahuan Sistem",
                "message_templates": {
                    "maintenance": "🔧 Sistem akan menjalani pemeliharaan pada {maintenance_time}",
                    "update": "🆕 Fitur baru telah tersedia: {feature_name}",
                    "announcement": "📢 {announcement_text}"
                },
                "action_text": "Lihat Detail",
                "priority": NotificationPriority.NORMAL
            },
            NotificationType.ADMIN: {
                "title": "Pemberitahuan Admin",
                "message_templates": {
                    "general": "👨‍💼 {admin_message}",
                    "urgent": "🚨 PENTING: {urgent_message}"
                },
                "action_text": "Lihat Detail",
                "priority": NotificationPriority.HIGH
            }
        }
    
    async def create_notification(
        self,
        user_id: str,
        notification_data: NotificationCreate,
        send_email: bool = True,
        send_push: bool = True
    ) -> NotificationResponse:
        """
        Buat dan kirim notifikasi baru.
        
        Args:
            user_id: ID user tujuan
            notification_data: Data notifikasi
            send_email: Kirim via email
            send_push: Kirim push notification
            
        Returns:
            Response notifikasi yang dibuat
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Dapatkan pengaturan notifikasi user
            settings = await self.get_user_settings(user_id)
            
            # Buat dokumen notifikasi
            notification_doc = NotificationInDB(
                user_id=user_id,
                title=notification_data.title,
                message=notification_data.message,
                type=notification_data.type,
                priority=notification_data.priority,
                action_url=notification_data.action_url,
                action_text=notification_data.action_text,
                data=notification_data.data or {},
                is_read=False,
                created_at=datetime.utcnow()
            )
            
            # Insert notifikasi ke database
            result = await collection.insert_one(
                notification_doc.model_dump(by_alias=True, exclude={"id"})
            )
            
            notification_id = str(result.inserted_id)
            
            # Kirim notifikasi email jika diaktifkan
            if send_email and settings and self._should_send_email(settings, notification_data.type):
                asyncio.create_task(self._send_email_notification(
                    user_id, notification_doc
                ))
            
            # Kirim notifikasi real-time via WebSocket
            if settings and settings.websocket_enabled:
                asyncio.create_task(self._send_realtime_notification(
                    user_id, notification_doc
                ))
            
            # Kirim push notification jika diaktifkan
            if send_push and settings and self._should_send_push(settings, notification_data.type):
                asyncio.create_task(self._send_push_notification(
                    user_id, notification_doc
                ))
            
            logger.info(f"Notifikasi berhasil dibuat: {notification_id} untuk user {user_id}")
            
            # Return response notifikasi
            return await self.get_notification_by_id(notification_id, user_id)
            
        except Exception as e:
            logger.error(f"Error membuat notifikasi: {e}")
            raise NotificationServiceError("Gagal membuat notifikasi")
    
    async def get_notification_by_id(
        self,
        notification_id: str,
        user_id: str
    ) -> Optional[NotificationResponse]:
        """
        Dapatkan notifikasi berdasarkan ID.
        
        Args:
            notification_id: ID notifikasi
            user_id: ID user untuk kontrol akses
            
        Returns:
            Response notifikasi atau None
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            notification_doc = await collection.find_one({
                "_id": ObjectId(notification_id),
                "user_id": user_id
            })
            
            if not notification_doc:
                return None
            
            notification = NotificationInDB(**notification_doc)
            
            return NotificationResponse(
                id=str(notification.id),
                user_id=notification.user_id,
                title=notification.title,
                message=notification.message,
                type=notification.type,
                priority=notification.priority,
                action_url=notification.action_url,
                action_text=notification.action_text,
                data=notification.data,
                is_read=notification.is_read,
                read_at=notification.read_at,
                created_at=notification.created_at,
                expires_at=notification.expires_at,
                time_ago=self._format_time_ago(notification.created_at)
            )
            
        except Exception as e:
            logger.error(f"Error mendapatkan notifikasi {notification_id}: {e}")
            return None
    
    async def get_user_notifications(
        self,
        user_id: str,
        page: int = 1,
        per_page: int = 20,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None
    ) -> PaginatedResponse[NotificationResponse]:
        """
        Dapatkan notifikasi user dengan paginasi.
        
        Args:
            user_id: ID user
            page: Nomor halaman
            per_page: Item per halaman
            unread_only: Hanya notifikasi yang belum dibaca
            notification_type: Filter berdasarkan tipe notifikasi
            
        Returns:
            Response notifikasi dengan paginasi
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Buat query
            query = {"user_id": user_id}
            
            if unread_only:
                query["is_read"] = False
            
            if notification_type:
                query["type"] = notification_type.value
            
            # Hapus notifikasi yang sudah expired
            now = datetime.utcnow()
            query["$or"] = [
                {"expires_at": {"$exists": False}},
                {"expires_at": None},
                {"expires_at": {"$gt": now}}
            ]
            
            # Hitung total
            total = await collection.count_documents(query)
            
            # Dapatkan hasil dengan paginasi
            skip = (page - 1) * per_page
            cursor = collection.find(query).sort("created_at", -1)
            cursor = cursor.skip(skip).limit(per_page)
            
            notifications_docs = await cursor.to_list(length=per_page)
            
            # Konversi ke format response
            notifications = []
            for notification_doc in notifications_docs:
                notification = NotificationInDB(**notification_doc)
                notifications.append(NotificationResponse(
                    id=str(notification.id),
                    user_id=notification.user_id,
                    title=notification.title,
                    message=notification.message,
                    type=notification.type,
                    priority=notification.priority,
                    action_url=notification.action_url,
                    action_text=notification.action_text,
                    data=notification.data,
                    is_read=notification.is_read,
                    read_at=notification.read_at,
                    created_at=notification.created_at,
                    expires_at=notification.expires_at,
                    time_ago=self._format_time_ago(notification.created_at)
                ))
            
            return PaginatedResponse.create(
                items=notifications,
                total=total,
                page=page,
                per_page=per_page
            )
            
        except Exception as e:
            logger.error(f"Error mendapatkan notifikasi user: {e}")
            raise NotificationServiceError("Gagal mendapatkan notifikasi")
    
    async def mark_as_read(
        self,
        user_id: str,
        notification_id: str
    ) -> bool:
        """
        Tandai notifikasi sebagai sudah dibaca.
        
        Args:
            user_id: ID user
            notification_id: ID notifikasi
            
        Returns:
            True jika berhasil
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            result = await collection.update_one(
                {
                    "_id": ObjectId(notification_id),
                    "user_id": user_id,
                    "is_read": False
                },
                {
                    "$set": {
                        "is_read": True,
                        "read_at": datetime.utcnow()
                    }
                }
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Notifikasi {notification_id} ditandai sudah dibaca oleh user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error menandai notifikasi sebagai dibaca: {e}")
            return False
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """
        Tandai semua notifikasi user sebagai sudah dibaca.
        
        Args:
            user_id: ID user
            
        Returns:
            Jumlah notifikasi yang ditandai
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            result = await collection.update_many(
                {
                    "user_id": user_id,
                    "is_read": False
                },
                {
                    "$set": {
                        "is_read": True,
                        "read_at": datetime.utcnow()
                    }
                }
            )
            
            count = result.modified_count
            if count > 0:
                logger.info(f"Menandai {count} notifikasi sebagai dibaca untuk user {user_id}")
            
            return count
            
        except Exception as e:
            logger.error(f"Error menandai semua notifikasi sebagai dibaca: {e}")
            return 0
    
    async def delete_notification(
        self,
        user_id: str,
        notification_id: str
    ) -> bool:
        """
        Hapus notifikasi.
        
        Args:
            user_id: ID user
            notification_id: ID notifikasi
            
        Returns:
            True jika berhasil
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            result = await collection.delete_one({
                "_id": ObjectId(notification_id),
                "user_id": user_id
            })
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Notifikasi {notification_id} dihapus oleh user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error menghapus notifikasi: {e}")
            return False
    
    async def get_unread_count(self, user_id: str) -> int:
        """
        Dapatkan jumlah notifikasi yang belum dibaca.
        
        Args:
            user_id: ID user
            
        Returns:
            Jumlah notifikasi belum dibaca
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Hapus notifikasi expired terlebih dahulu
            now = datetime.utcnow()
            query = {
                "user_id": user_id,
                "is_read": False,
                "$or": [
                    {"expires_at": {"$exists": False}},
                    {"expires_at": None},
                    {"expires_at": {"$gt": now}}
                ]
            }
            
            count = await collection.count_documents(query)
            return count
            
        except Exception as e:
            logger.error(f"Error mendapatkan jumlah notifikasi belum dibaca: {e}")
            return 0
    
    async def get_user_settings(self, user_id: str) -> Optional[NotificationSettings]:
        """
        Dapatkan pengaturan notifikasi user.
        
        Args:
            user_id: ID user
            
        Returns:
            Pengaturan notifikasi user
        """
        try:
            db = await get_database()
            collection = db[self.settings_collection_name]
            
            settings_doc = await collection.find_one({"user_id": user_id})
            
            if settings_doc:
                return NotificationSettings(**settings_doc)
            
            # Buat pengaturan default jika belum ada
            default_settings = NotificationSettings(user_id=user_id)
            await collection.insert_one(
                default_settings.model_dump(by_alias=True, exclude={"id"})
            )
            
            return default_settings
            
        except Exception as e:
            logger.error(f"Error mendapatkan pengaturan user: {e}")
            return None
    
    async def update_user_settings(
        self,
        user_id: str,
        settings_update: NotificationSettingsUpdate
    ) -> Optional[NotificationSettings]:
        """
        Update pengaturan notifikasi user.
        
        Args:
            user_id: ID user
            settings_update: Data update pengaturan
            
        Returns:
            Pengaturan yang sudah diupdate
        """
        try:
            db = await get_database()
            collection = db[self.settings_collection_name]
            
            # Siapkan data update
            update_fields = {}
            for field, value in settings_update.model_dump(exclude_none=True).items():
                if value is not None:
                    update_fields[field] = value
            
            if not update_fields:
                return await self.get_user_settings(user_id)
            
            update_fields["updated_at"] = datetime.utcnow()
            
            # Update atau buat pengaturan
            result = await collection.update_one(
                {"user_id": user_id},
                {"$set": update_fields},
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                logger.info(f"Pengaturan notifikasi diupdate untuk user {user_id}")
                return await self.get_user_settings(user_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error mengupdate pengaturan user: {e}")
            return None
    
    # Metode khusus untuk berbagai jenis notifikasi
    
    async def send_transaction_notification(
        self,
        user_id: str,
        transaction_data: Dict[str, Any]
    ):
        """Kirim notifikasi transaksi baru."""
        try:
            template = self.default_templates[NotificationType.TRANSACTION]
            transaction_type = transaction_data["type"]
            
            if transaction_type == "income":
                message = template["message_templates"]["income"].format(
                    amount_formatted=f"Rp {transaction_data['amount']:,.0f}",
                    category=transaction_data['category_name']
                )
            else:
                message = template["message_templates"]["expense"].format(
                    amount_formatted=f"Rp {transaction_data['amount']:,.0f}",
                    category=transaction_data['category_name']
                )
            
            notification = NotificationCreate(
                title=template["title"],
                message=message,
                type=NotificationType.TRANSACTION,
                priority=template["priority"],
                action_url=f"/transactions/{transaction_data['id']}",
                action_text=template["action_text"],
                data={
                    "transaction_id": transaction_data["id"],
                    "amount": transaction_data["amount"],
                    "category": transaction_data["category_name"],
                    "type": transaction_data["type"]
                }
            )
            
            await self.create_notification(user_id, notification)
            
        except Exception as e:
            logger.error(f"Error mengirim notifikasi transaksi: {e}")
    
    async def send_savings_goal_notification(
        self,
        user_id: str,
        goal_data: Dict[str, Any],
        notification_type: str = "progress"
    ):
        """Kirim notifikasi target tabungan."""
        try:
            template = self.default_templates[NotificationType.SAVINGS_GOAL]
            
            if notification_type == "achieved":
                title = "🎉 Target Tabungan Tercapai!"
                message = template["message_templates"]["achieved"].format(
                    goal_name=goal_data['target_name']
                )
                priority = NotificationPriority.HIGH
            elif notification_type == "progress":
                progress = goal_data.get("progress_percentage", 0)
                message = template["message_templates"]["progress"].format(
                    goal_name=goal_data['target_name'],
                    progress=f"{progress:.1f}"
                )
                title = template["title"]
                priority = template["priority"]
            elif notification_type == "reminder":
                message = template["message_templates"]["reminder"].format(
                    goal_name=goal_data['target_name']
                )
                title = "Pengingat Target Tabungan"
                priority = template["priority"]
            else:  # deadline_warning
                days_left = goal_data.get("days_remaining", 0)
                message = template["message_templates"]["deadline_warning"].format(
                    goal_name=goal_data['target_name'],
                    days_left=days_left
                )
                title = "⏰ Deadline Target Tabungan"
                priority = NotificationPriority.HIGH
            
            notification = NotificationCreate(
                title=title,
                message=message,
                type=NotificationType.SAVINGS_GOAL,
                priority=priority,
                action_url=f"/savings-targets/{goal_data['id']}",
                action_text=template["action_text"],
                data={
                    "goal_id": goal_data["id"],
                    "goal_name": goal_data["target_name"],
                    "notification_type": notification_type
                }
            )
            
            await self.create_notification(user_id, notification)
            
        except Exception as e:
            logger.error(f"Error mengirim notifikasi target tabungan: {e}")
    
    async def send_budget_alert(
        self,
        user_id: str,
        budget_data: Dict[str, Any],
        alert_type: str = "warning"
    ):
        """Kirim alert anggaran."""
        try:
            template = self.default_templates[NotificationType.BUDGET_ALERT]
            
            if alert_type == "exceeded":
                title = "⚠️ Anggaran Terlampaui"
                message = template["message_templates"]["exceeded"].format(
                    category=budget_data['category'],
                    excess_amount=f"Rp {budget_data.get('excess_amount', 0):,.0f}"
                )
                priority = NotificationPriority.HIGH
            elif alert_type == "warning":
                percentage = budget_data.get("percentage_used", 0)
                message = template["message_templates"]["warning"].format(
                    category=budget_data['category'],
                    percentage=f"{percentage:.0f}",
                    amount_used=f"Rp {budget_data.get('amount_used', 0):,.0f}",
                    budget_limit=f"Rp {budget_data.get('budget_limit', 0):,.0f}"
                )
                title = template["title"]
                priority = template["priority"]
            else:  # reset
                message = template["message_templates"]["reset"].format(
                    category=budget_data['category']
                )
                title = "Anggaran Direset"
                priority = NotificationPriority.NORMAL
            
            notification = NotificationCreate(
                title=title,
                message=message,
                type=NotificationType.BUDGET_ALERT,
                priority=priority,
                action_url=f"/budgets/{budget_data.get('id', '')}",
                action_text=template["action_text"],
                data={
                    "budget_id": budget_data.get("id"),
                    "category": budget_data["category"],
                    "alert_type": alert_type
                }
            )
            
            await self.create_notification(user_id, notification)
            
        except Exception as e:
            logger.error(f"Error mengirim alert anggaran: {e}")
    
    async def send_ai_insight(
        self,
        user_id: str,
        insight: str,
        insight_type: str = "spending_pattern",
        insight_data: Optional[Dict[str, Any]] = None
    ):
        """Kirim insight AI."""
        try:
            template = self.default_templates[NotificationType.AI_INSIGHT]
            
            message = template["message_templates"].get(insight_type, "💡 {insight}").format(
                insight=insight,
                tip=insight,
                recommendation=insight
            )
            
            notification = NotificationCreate(
                title=template["title"],
                message=message,
                type=NotificationType.AI_INSIGHT,
                priority=template["priority"],
                action_url="/insights",
                action_text=template["action_text"],
                data=insight_data or {}
            )
            
            await self.create_notification(user_id, notification)
            
        except Exception as e:
            logger.error(f"Error mengirim insight AI: {e}")
    
    async def send_reminder(
        self,
        user_id: str,
        reminder_text: str,
        reminder_type: str = "daily",
        action_url: Optional[str] = None
    ):
        """Kirim pengingat."""
        try:
            template = self.default_templates[NotificationType.REMINDER]
            
            message = template["message_templates"].get(reminder_type, "⏰ {reminder_text}").format(
                reminder_text=reminder_text
            )
            
            notification = NotificationCreate(
                title=template["title"],
                message=message,
                type=NotificationType.REMINDER,
                priority=template["priority"],
                action_url=action_url,
                action_text=template["action_text"],
                data={"reminder_type": reminder_type}
            )
            
            await self.create_notification(user_id, notification)
            
        except Exception as e:
            logger.error(f"Error mengirim pengingat: {e}")
    
    async def send_system_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        system_type: str = "announcement",
        priority: NotificationPriority = NotificationPriority.NORMAL,
        action_url: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """Kirim notifikasi sistem."""
        try:
            template = self.default_templates[NotificationType.SYSTEM]
            
            if system_type in template["message_templates"]:
                formatted_message = template["message_templates"][system_type].format(
                    maintenance_time=data.get("maintenance_time", ""),
                    feature_name=data.get("feature_name", ""),
                    announcement_text=message
                )
            else:
                formatted_message = message
            
            notification = NotificationCreate(
                title=title,
                message=formatted_message,
                type=NotificationType.SYSTEM,
                priority=priority,
                action_url=action_url,
                action_text=template["action_text"],
                data=data or {}
            )
            
            await self.create_notification(user_id, notification)
            
        except Exception as e:
            logger.error(f"Error mengirim notifikasi sistem: {e}")
    
    async def send_admin_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        admin_type: str = "general",
        priority: NotificationPriority = NotificationPriority.HIGH,
        action_url: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """Kirim notifikasi admin."""
        try:
            template = self.default_templates[NotificationType.ADMIN]
            
            if admin_type in template["message_templates"]:
                formatted_message = template["message_templates"][admin_type].format(
                    admin_message=message,
                    urgent_message=message
                )
            else:
                formatted_message = message
            
            notification = NotificationCreate(
                title=f"[ADMIN] {title}",
                message=formatted_message,
                type=NotificationType.ADMIN,
                priority=priority,
                action_url=action_url,
                action_text=template["action_text"],
                data=data or {}
            )
            
            await self.create_notification(user_id, notification)
            
        except Exception as e:
            logger.error(f"Error mengirim notifikasi admin: {e}")
    
    async def broadcast_notification(
        self,
        title: str,
        message: str,
        user_ids: Optional[List[str]] = None,
        notification_type: NotificationType = NotificationType.SYSTEM,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        action_url: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """Broadcast notifikasi ke multiple users."""
        try:
            if user_ids is None:
                # Dapatkan semua user aktif
                db = await get_database()
                users_collection = db.users
                user_docs = await users_collection.find(
                    {"is_active": True}, {"_id": 1}
                ).to_list(None)
                user_ids = [str(doc["_id"]) for doc in user_docs]
            
            # Buat notifikasi untuk semua users
            notification_data = NotificationCreate(
                title=title,
                message=message,
                type=notification_type,
                priority=priority,
                action_url=action_url,
                action_text="Lihat Detail" if action_url else None,
                data=data or {}
            )
            
            # Buat notifikasi secara batch
            tasks = []
            for user_id in user_ids:
                task = self.create_notification(
                    user_id, notification_data, send_email=False
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info(f"Notifikasi broadcast terkirim ke {len(user_ids)} user")
            
        except Exception as e:
            logger.error(f"Error broadcast notifikasi: {e}")
    
    async def get_notification_stats(self, user_id: str) -> NotificationStats:
        """Dapatkan statistik notifikasi user."""
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Pipeline aggregasi untuk statistik
            pipeline = [
                {"$match": {"user_id": user_id}},
                {
                    "$group": {
                        "_id": None,
                        "total_sent": {"$sum": 1},
                        "total_read": {
                            "$sum": {"$cond": [{"$eq": ["$is_read", True]}, 1, 0]}
                        },
                        "total_unread": {
                            "$sum": {"$cond": [{"$eq": ["$is_read", False]}, 1, 0]}
                        },
                        "by_type": {
                            "$push": "$type"
                        },
                        "by_priority": {
                            "$push": "$priority"
                        }
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            
            if not result:
                return NotificationStats(
                    total_sent=0,
                    total_read=0,
                    total_unread=0,
                    read_rate=0.0,
                    by_type={},
                    by_priority={},
                    recent_activity=[]
                )
            
            data = result[0]
            total_sent = data["total_sent"]
            total_read = data["total_read"]
            
            # Hitung read rate
            read_rate = (total_read / total_sent * 100) if total_sent > 0 else 0
            
            # Hitung berdasarkan tipe dan prioritas
            by_type = {}
            for notification_type in data["by_type"]:
                by_type[notification_type] = by_type.get(notification_type, 0) + 1
            
            by_priority = {}
            for priority in data["by_priority"]:
                by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # Dapatkan aktivitas terbaru
            recent_docs = await collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(10).to_list(10)
            
            recent_activity = []
            for doc in recent_docs:
                recent_activity.append({
                    "id": str(doc["_id"]),
                    "title": doc["title"],
                    "type": doc["type"],
                    "is_read": doc["is_read"],
                    "created_at": doc["created_at"].isoformat()
                })
            
            return NotificationStats(
                total_sent=total_sent,
                total_read=total_read,
                total_unread=data["total_unread"],
                read_rate=round(read_rate, 2),
                by_type=by_type,
                by_priority=by_priority,
                recent_activity=recent_activity
            )
            
        except Exception as e:
            logger.error(f"Error mendapatkan statistik notifikasi: {e}")
            return NotificationStats(
                total_sent=0,
                total_read=0,
                total_unread=0,
                read_rate=0.0,
                by_type={},
                by_priority={},
                recent_activity=[]
            )
    
    async def cleanup_expired_notifications(self):
        """Bersihkan notifikasi yang sudah expired."""
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            now = datetime.utcnow()
            result = await collection.delete_many({
                "expires_at": {"$lt": now}
            })
            
            if result.deleted_count > 0:
                logger.info(f"Membersihkan {result.deleted_count} notifikasi expired")
            
        except Exception as e:
            logger.error(f"Error membersihkan notifikasi expired: {e}")
    
    def _should_send_email(self, settings: NotificationSettings, notification_type: NotificationType) -> bool:
        """Periksa apakah email harus dikirim untuk tipe notifikasi."""
        if not settings.email_enabled:
            return False
        
        type_mapping = {
            NotificationType.TRANSACTION: settings.email_transactions,
            NotificationType.SAVINGS_GOAL: settings.email_savings_goals,
            NotificationType.BUDGET_ALERT: settings.email_budget_alerts,
            NotificationType.AI_INSIGHT: settings.email_ai_insights,
            NotificationType.REMINDER: settings.email_reminders,
            NotificationType.SYSTEM: True,
            NotificationType.ADMIN: True
        }
        
        return type_mapping.get(notification_type, True)
    
    def _should_send_push(self, settings: NotificationSettings, notification_type: NotificationType) -> bool:
        """Periksa apakah push notification harus dikirim."""
        if not settings.push_enabled:
            return False
        
        type_mapping = {
            NotificationType.TRANSACTION: settings.push_transactions,
            NotificationType.SAVINGS_GOAL: settings.push_savings_goals,
            NotificationType.BUDGET_ALERT: settings.push_budget_alerts,
            NotificationType.AI_INSIGHT: settings.push_ai_insights,
            NotificationType.REMINDER: settings.push_reminders,
            NotificationType.SYSTEM: True,
            NotificationType.ADMIN: True
        }
        
        return type_mapping.get(notification_type, True)
    
    async def _send_email_notification(self, user_id: str, notification: NotificationInDB):
        """Kirim notifikasi email."""
        try:
            # Dapatkan email user
            db = await get_database()
            users_collection = db.users
            user_doc = await users_collection.find_one(
                {"_id": ObjectId(user_id)}, {"email": 1, "full_name": 1}
            )
            
            if not user_doc:
                return
            
            # Buat template email sendiri tanpa menggunakan utils.email_templates
            subject = f"Lunance - {notification.title}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{notification.title}</title>
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .logo {{
                        font-size: 28px;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }}
                    .content {{
                        padding: 30px;
                    }}
                    .notification-box {{
                        background: #f8f9fa;
                        border-left: 4px solid #667eea;
                        padding: 20px;
                        margin: 20px 0;
                        border-radius: 0 8px 8px 0;
                    }}
                    .notification-title {{
                        font-size: 18px;
                        font-weight: bold;
                        color: #333;
                        margin-bottom: 10px;
                    }}
                    .notification-message {{
                        color: #555;
                        line-height: 1.6;
                    }}
                    .action-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 12px 25px;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        padding: 20px;
                        text-align: center;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                    .priority-high {{
                        border-left-color: #f39c12 !important;
                    }}
                    .priority-urgent {{
                        border-left-color: #e74c3c !important;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🌙 Lunance</div>
                        <p>Smart Personal Finance Management</p>
                    </div>
                    <div class="content">
                        <h2>Hai, {user_doc["full_name"]}!</h2>
                        <p>Anda memiliki notifikasi baru dari Lunance:</p>
                        
                        <div class="notification-box {'priority-high' if notification.priority == 'high' else 'priority-urgent' if notification.priority == 'urgent' else ''}">
                            <div class="notification-title">{notification.title}</div>
                            <div class="notification-message">{notification.message.replace('\\n', '<br>')}</div>
                        </div>
                        
                        {f'''
                        <div style="text-align: center;">
                            <a href="{notification.action_url}" class="action-button">
                                {notification.action_text}
                            </a>
                        </div>
                        ''' if notification.action_url else ''}
                        
                        <p>Terima kasih telah menggunakan Lunance untuk mengelola keuangan Anda!</p>
                    </div>
                    <div class="footer">
                        <p><strong>© 2024 Lunance App</strong> - Smart Personal Finance Management</p>
                        <p>Email ini dikirim secara otomatis, mohon jangan balas.</p>
                        <p>Butuh bantuan? Hubungi support@lunance.app</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Lunance - {notification.title}
            
            Hai, {user_doc["full_name"]}!
            
            Anda memiliki notifikasi baru dari Lunance:
            
            {notification.title}
            {notification.message}
            
            {f"Link: {notification.action_url}" if notification.action_url else ""}
            
            Terima kasih telah menggunakan Lunance!
            
            ---
            © 2024 Lunance App
            Smart Personal Finance Management
            """
            
            # Kirim email menggunakan email service yang sudah ada
            await self.email_service.send_email(
                to_email=user_doc["email"],
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Error mengirim email notifikasi: {e}")
    
    async def _send_realtime_notification(self, user_id: str, notification: NotificationInDB):
        """Kirim notifikasi real-time via WebSocket."""
        try:
            from ..websocket.websocket_manager import connection_manager
            
            notification_data = {
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "type": notification.type.value,
                "priority": notification.priority.value,
                "action_url": notification.action_url,
                "action_text": notification.action_text,
                "data": notification.data,
                "created_at": notification.created_at.isoformat()
            }
            
            await connection_manager.send_notification(user_id, notification_data)
            
        except Exception as e:
            logger.error(f"Error mengirim notifikasi real-time: {e}")
    
    async def _send_push_notification(self, user_id: str, notification: NotificationInDB):
        """Kirim push notification (placeholder untuk implementasi masa depan)."""
        try:
            # Placeholder untuk integrasi push notification service
            # Ini akan mengintegrasikan dengan Firebase Cloud Messaging (FCM)
            # atau Apple Push Notification Service (APNs)
            logger.info(f"Push notification akan dikirim ke user {user_id}: {notification.title}")
            
        except Exception as e:
            logger.error(f"Error mengirim push notification: {e}")
    
    def _format_time_ago(self, created_at: datetime) -> str:
        """Format waktu dalam bahasa Indonesia."""
        try:
            now = datetime.utcnow()
            diff = now - created_at
            
            if diff.days > 0:
                if diff.days == 1:
                    return "1 hari yang lalu"
                else:
                    return f"{diff.days} hari yang lalu"
            elif diff.seconds >= 3600:
                hours = diff.seconds // 3600
                if hours == 1:
                    return "1 jam yang lalu"
                else:
                    return f"{hours} jam yang lalu"
            elif diff.seconds >= 60:
                minutes = diff.seconds // 60
                if minutes == 1:
                    return "1 menit yang lalu"
                else:
                    return f"{minutes} menit yang lalu"
            else:
                return "Baru saja"
                
        except Exception:
            return "Waktu tidak diketahui"


# Global notification service instance
notification_service = NotificationService()