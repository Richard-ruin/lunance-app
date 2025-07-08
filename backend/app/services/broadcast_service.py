# app/services/broadcast_service.py
"""Layanan broadcast untuk mengirim pesan ke multiple users secara real-time."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum

from ..websocket.websocket_manager import connection_manager
from ..services.notification_service import notification_service
from ..services.email_service import EmailService
from ..config.database import get_database
from ..models.user import UserRole

logger = logging.getLogger(__name__)


class BroadcastType(str, Enum):
    """Tipe broadcast message."""
    ANNOUNCEMENT = "announcement"        # Pengumuman umum
    MAINTENANCE = "maintenance"          # Notifikasi maintenance
    FEATURE_UPDATE = "feature_update"    # Update fitur baru
    EMERGENCY = "emergency"              # Notifikasi darurat
    PROMOTION = "promotion"              # Promosi/penawaran
    REMINDER = "reminder"                # Pengingat
    SURVEY = "survey"                    # Survei/feedback


class BroadcastPriority(str, Enum):
    """Prioritas broadcast."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class BroadcastService:
    """Layanan untuk broadcasting pesan ke multiple users."""
    
    def __init__(self):
        self.email_service = EmailService()
        self.active_broadcasts: Dict[str, Dict[str, Any]] = {}
        
        # Template pesan dalam bahasa Indonesia
        self.message_templates = {
            BroadcastType.ANNOUNCEMENT: {
                "title": "📢 Pengumuman Penting",
                "icon": "📢",
                "default_action": "Lihat Detail"
            },
            BroadcastType.MAINTENANCE: {
                "title": "🔧 Pemeliharaan Sistem",
                "icon": "🔧",
                "default_action": "Lihat Jadwal"
            },
            BroadcastType.FEATURE_UPDATE: {
                "title": "🆕 Fitur Baru Tersedia",
                "icon": "🆕",
                "default_action": "Coba Sekarang"
            },
            BroadcastType.EMERGENCY: {
                "title": "🚨 Pemberitahuan Darurat",
                "icon": "🚨",
                "default_action": "Baca Selengkapnya"
            },
            BroadcastType.PROMOTION: {
                "title": "🎉 Penawaran Khusus",
                "icon": "🎉",
                "default_action": "Lihat Penawaran"
            },
            BroadcastType.REMINDER: {
                "title": "⏰ Pengingat",
                "icon": "⏰",
                "default_action": "Lihat Detail"
            },
            BroadcastType.SURVEY: {
                "title": "📝 Survei Feedback",
                "icon": "📝",
                "default_action": "Isi Survei"
            }
        }
    
    async def send_broadcast(
        self,
        message: str,
        broadcast_type: BroadcastType = BroadcastType.ANNOUNCEMENT,
        priority: BroadcastPriority = BroadcastPriority.NORMAL,
        target_users: Optional[List[str]] = None,
        target_roles: Optional[List[UserRole]] = None,
        send_email: bool = False,
        send_push: bool = True,
        send_websocket: bool = True,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
        expires_in_hours: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Kirim broadcast message ke users.
        
        Args:
            message: Isi pesan broadcast
            broadcast_type: Tipe broadcast
            priority: Prioritas pesan
            target_users: List user ID tertentu (jika None, kirim ke semua)
            target_roles: List role tertentu
            send_email: Kirim via email
            send_push: Kirim push notification
            send_websocket: Kirim via WebSocket
            action_url: URL untuk action button
            action_text: Text untuk action button
            expires_in_hours: Jam sampai pesan expire
            data: Data tambahan
            
        Returns:
            Hasil broadcast
        """
        try:
            # Generate broadcast ID
            broadcast_id = f"broadcast_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Dapatkan template pesan
            template = self.message_templates.get(broadcast_type, self.message_templates[BroadcastType.ANNOUNCEMENT])
            
            # Siapkan title dan action text
            title = template["title"]
            if not action_text:
                action_text = template["default_action"]
            
            # Tentukan target users
            if target_users is None:
                target_users = await self._get_all_active_users(target_roles)
            elif target_roles:
                # Filter users berdasarkan role
                filtered_users = await self._filter_users_by_role(target_users, target_roles)
                target_users = filtered_users
            
            # Hitung expiry time
            expires_at = None
            if expires_in_hours:
                expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
            
            # Simpan broadcast info
            broadcast_info = {
                "broadcast_id": broadcast_id,
                "title": title,
                "message": message,
                "type": broadcast_type.value,
                "priority": priority.value,
                "target_users": target_users,
                "target_roles": [role.value for role in target_roles] if target_roles else None,
                "action_url": action_url,
                "action_text": action_text,
                "expires_at": expires_at,
                "data": data or {},
                "created_at": datetime.utcnow(),
                "status": "sending"
            }
            
            self.active_broadcasts[broadcast_id] = broadcast_info
            
            # Hasil broadcast
            results = {
                "broadcast_id": broadcast_id,
                "target_count": len(target_users),
                "websocket_sent": 0,
                "email_sent": 0,
                "push_sent": 0,
                "notifications_created": 0,
                "errors": []
            }
            
            # Kirim via berbagai channel
            tasks = []
            
            if send_websocket:
                tasks.append(self._send_websocket_broadcast(broadcast_info, results))
            
            if send_email:
                tasks.append(self._send_email_broadcast(broadcast_info, results))
            
            if send_push:
                tasks.append(self._send_push_broadcast(broadcast_info, results))
            
            # Selalu buat notification di database
            tasks.append(self._create_notification_broadcast(broadcast_info, results))
            
            # Jalankan semua tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update status
            broadcast_info["status"] = "completed"
            broadcast_info["completed_at"] = datetime.utcnow()
            broadcast_info["results"] = results
            
            logger.info(f"Broadcast {broadcast_id} selesai - Target: {len(target_users)}, "
                       f"WebSocket: {results['websocket_sent']}, Email: {results['email_sent']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error mengirim broadcast: {e}")
            return {
                "error": f"Gagal mengirim broadcast: {str(e)}",
                "broadcast_id": None,
                "target_count": 0
            }
    
    async def send_system_announcement(
        self,
        title: str,
        message: str,
        priority: BroadcastPriority = BroadcastPriority.NORMAL,
        action_url: Optional[str] = None,
        send_email: bool = False
    ) -> Dict[str, Any]:
        """
        Kirim pengumuman sistem ke semua user.
        
        Args:
            title: Judul pengumuman
            message: Isi pengumuman
            priority: Prioritas
            action_url: URL action
            send_email: Kirim email juga
            
        Returns:
            Hasil broadcast
        """
        try:
            return await self.send_broadcast(
                message=message,
                broadcast_type=BroadcastType.ANNOUNCEMENT,
                priority=priority,
                send_email=send_email,
                action_url=action_url,
                action_text="Lihat Detail",
                data={"custom_title": title}
            )
            
        except Exception as e:
            logger.error(f"Error mengirim pengumuman sistem: {e}")
            return {"error": str(e)}
    
    async def send_maintenance_notice(
        self,
        start_time: datetime,
        end_time: datetime,
        description: str = "Pemeliharaan rutin sistem"
    ) -> Dict[str, Any]:
        """
        Kirim notifikasi maintenance.
        
        Args:
            start_time: Waktu mulai maintenance
            end_time: Waktu selesai maintenance
            description: Deskripsi maintenance
            
        Returns:
            Hasil broadcast
        """
        try:
            duration = end_time - start_time
            duration_hours = duration.total_seconds() / 3600
            
            message = (
                f"🔧 {description}\n\n"
                f"📅 Mulai: {start_time.strftime('%d/%m/%Y %H:%M')} WIB\n"
                f"📅 Selesai: {end_time.strftime('%d/%m/%Y %H:%M')} WIB\n"
                f"⏱️ Durasi: {duration_hours:.1f} jam\n\n"
                f"Selama maintenance, layanan mungkin tidak tersedia sementara. "
                f"Mohon maaf atas ketidaknyamanan ini."
            )
            
            return await self.send_broadcast(
                message=message,
                broadcast_type=BroadcastType.MAINTENANCE,
                priority=BroadcastPriority.HIGH,
                send_email=True,
                action_text="Lihat Detail",
                data={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_hours": duration_hours
                }
            )
            
        except Exception as e:
            logger.error(f"Error mengirim notifikasi maintenance: {e}")
            return {"error": str(e)}
    
    async def send_feature_announcement(
        self,
        feature_name: str,
        description: str,
        demo_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Kirim pengumuman fitur baru.
        
        Args:
            feature_name: Nama fitur
            description: Deskripsi fitur
            demo_url: URL demo/tutorial
            
        Returns:
            Hasil broadcast
        """
        try:
            message = (
                f"🆕 Fitur baru telah hadir: {feature_name}!\n\n"
                f"{description}\n\n"
                f"Silakan coba fitur baru ini dan berikan feedback Anda."
            )
            
            return await self.send_broadcast(
                message=message,
                broadcast_type=BroadcastType.FEATURE_UPDATE,
                priority=BroadcastPriority.NORMAL,
                send_email=True,
                action_url=demo_url,
                action_text="Coba Sekarang" if demo_url else "Lihat Detail",
                data={
                    "feature_name": feature_name,
                    "demo_url": demo_url
                }
            )
            
        except Exception as e:
            logger.error(f"Error mengirim pengumuman fitur: {e}")
            return {"error": str(e)}
    
    async def send_emergency_alert(
        self,
        alert_message: str,
        action_required: str,
        action_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Kirim alert darurat.
        
        Args:
            alert_message: Pesan alert
            action_required: Tindakan yang diperlukan
            action_url: URL untuk action
            
        Returns:
            Hasil broadcast
        """
        try:
            message = (
                f"🚨 PEMBERITAHUAN DARURAT\n\n"
                f"{alert_message}\n\n"
                f"⚠️ Tindakan diperlukan: {action_required}"
            )
            
            return await self.send_broadcast(
                message=message,
                broadcast_type=BroadcastType.EMERGENCY,
                priority=BroadcastPriority.URGENT,
                send_email=True,
                send_push=True,
                action_url=action_url,
                action_text="Ambil Tindakan",
                data={
                    "alert_level": "emergency",
                    "action_required": action_required
                }
            )
            
        except Exception as e:
            logger.error(f"Error mengirim alert darurat: {e}")
            return {"error": str(e)}
    
    async def send_targeted_message(
        self,
        user_ids: List[str],
        title: str,
        message: str,
        priority: BroadcastPriority = BroadcastPriority.NORMAL,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Kirim pesan ke user tertentu.
        
        Args:
            user_ids: List user ID target
            title: Judul pesan
            message: Isi pesan
            priority: Prioritas
            action_url: URL action
            action_text: Text action
            
        Returns:
            Hasil broadcast
        """
        try:
            return await self.send_broadcast(
                message=message,
                broadcast_type=BroadcastType.ANNOUNCEMENT,
                priority=priority,
                target_users=user_ids,
                action_url=action_url,
                action_text=action_text or "Lihat Detail",
                data={"custom_title": title}
            )
            
        except Exception as e:
            logger.error(f"Error mengirim pesan targeted: {e}")
            return {"error": str(e)}
    
    async def send_role_based_message(
        self,
        roles: List[UserRole],
        title: str,
        message: str,
        priority: BroadcastPriority = BroadcastPriority.NORMAL,
        action_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Kirim pesan berdasarkan role user.
        
        Args:
            roles: List role target
            title: Judul pesan
            message: Isi pesan
            priority: Prioritas
            action_url: URL action
            
        Returns:
            Hasil broadcast
        """
        try:
            return await self.send_broadcast(
                message=message,
                broadcast_type=BroadcastType.ANNOUNCEMENT,
                priority=priority,
                target_roles=roles,
                action_url=action_url,
                action_text="Lihat Detail",
                data={"custom_title": title}
            )
            
        except Exception as e:
            logger.error(f"Error mengirim pesan role-based: {e}")
            return {"error": str(e)}
    
    async def get_broadcast_status(self, broadcast_id: str) -> Optional[Dict[str, Any]]:
        """
        Dapatkan status broadcast.
        
        Args:
            broadcast_id: ID broadcast
            
        Returns:
            Info status broadcast
        """
        try:
            return self.active_broadcasts.get(broadcast_id)
            
        except Exception as e:
            logger.error(f"Error mendapatkan status broadcast: {e}")
            return None
    
    async def get_broadcast_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Dapatkan history broadcast.
        
        Args:
            limit: Limit jumlah record
            
        Returns:
            List history broadcast
        """
        try:
            # Ambil dari memory (untuk implementasi sederhana)
            # Dalam production, ini bisa disimpan di database
            history = list(self.active_broadcasts.values())
            
            # Sort berdasarkan created_at terbaru
            history.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
            
            return history[:limit]
            
        except Exception as e:
            logger.error(f"Error mendapatkan history broadcast: {e}")
            return []
    
    async def _get_all_active_users(self, target_roles: Optional[List[UserRole]] = None) -> List[str]:
        """Dapatkan semua user aktif."""
        try:
            db = await get_database()
            users_collection = db.users
            
            # Query untuk user aktif
            query = {"is_active": True}
            
            # Filter berdasarkan role jika ada
            if target_roles:
                query["role"] = {"$in": [role.value for role in target_roles]}
            
            # Ambil user IDs
            users = await users_collection.find(query, {"_id": 1}).to_list(None)
            user_ids = [str(user["_id"]) for user in users]
            
            logger.info(f"Ditemukan {len(user_ids)} user aktif untuk broadcast")
            return user_ids
            
        except Exception as e:
            logger.error(f"Error mendapatkan user aktif: {e}")
            return []
    
    async def _filter_users_by_role(self, user_ids: List[str], target_roles: List[UserRole]) -> List[str]:
        """Filter user berdasarkan role."""
        try:
            db = await get_database()
            users_collection = db.users
            
            # Query untuk filter berdasarkan role
            from bson import ObjectId
            query = {
                "_id": {"$in": [ObjectId(uid) for uid in user_ids]},
                "role": {"$in": [role.value for role in target_roles]},
                "is_active": True
            }
            
            users = await users_collection.find(query, {"_id": 1}).to_list(None)
            filtered_ids = [str(user["_id"]) for user in users]
            
            return filtered_ids
            
        except Exception as e:
            logger.error(f"Error filter user by role: {e}")
            return user_ids  # Return original jika error
    
    async def _send_websocket_broadcast(self, broadcast_info: Dict[str, Any], results: Dict[str, Any]):
        """Kirim broadcast via WebSocket."""
        try:
            message = {
                "type": "broadcast",
                "broadcast_type": broadcast_info["type"],
                "priority": broadcast_info["priority"],
                "title": broadcast_info["title"],
                "message": broadcast_info["message"],
                "action_url": broadcast_info["action_url"],
                "action_text": broadcast_info["action_text"],
                "data": broadcast_info["data"],
                "expires_at": broadcast_info["expires_at"].isoformat() if broadcast_info["expires_at"] else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Kirim ke semua connection types
            connection_types = ["chat", "dashboard", "notifications"]
            sent_count = 0
            
            for connection_type in connection_types:
                try:
                    await connection_manager.broadcast_to_type(
                        message, 
                        connection_type,
                        exclude_user_ids=[]
                    )
                    
                    # Hitung user yang terkoneksi di connection type ini
                    active_users = connection_manager.get_active_users(connection_type)
                    sent_count += len(active_users)
                    
                except Exception as e:
                    logger.error(f"Error broadcast WebSocket ke {connection_type}: {e}")
                    results["errors"].append(f"WebSocket {connection_type}: {str(e)}")
            
            results["websocket_sent"] = sent_count
            logger.info(f"WebSocket broadcast terkirim ke {sent_count} koneksi")
            
        except Exception as e:
            logger.error(f"Error WebSocket broadcast: {e}")
            results["errors"].append(f"WebSocket: {str(e)}")
    
    async def _send_email_broadcast(self, broadcast_info: Dict[str, Any], results: Dict[str, Any]):
        """Kirim broadcast via email."""
        try:
            # Dapatkan email users
            target_users = broadcast_info["target_users"]
            
            db = await get_database()
            users_collection = db.users
            
            from bson import ObjectId
            users = await users_collection.find(
                {"_id": {"$in": [ObjectId(uid) for uid in target_users]}},
                {"email": 1, "full_name": 1}
            ).to_list(None)
            
            # Kirim email ke setiap user
            sent_count = 0
            for user in users:
                try:
                    # Template email
                    subject = f"Lunance - {broadcast_info['title']}"
                    
                    html_content = f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                            <h2 style="color: #333; margin-bottom: 20px;">
                                {broadcast_info['title']}
                            </h2>
                            <div style="background: white; padding: 20px; border-radius: 6px; margin-bottom: 20px;">
                                <p style="color: #555; line-height: 1.6; margin: 0;">
                                    {broadcast_info['message'].replace('\n', '<br>')}
                                </p>
                            </div>
                            {f'''
                            <div style="text-align: center;">
                                <a href="{broadcast_info['action_url']}" 
                                   style="background: #3B82F6; color: white; padding: 12px 24px; 
                                          text-decoration: none; border-radius: 6px; display: inline-block;">
                                    {broadcast_info['action_text']}
                                </a>
                            </div>
                            ''' if broadcast_info['action_url'] else ''}
                            <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
                                <p style="color: #888; font-size: 12px; margin: 0;">
                                    Dikirim dari aplikasi Lunance - Manajemen Keuangan Mahasiswa
                                </p>
                            </div>
                        </div>
                    </div>
                    """
                    
                    text_content = f"""
                    {broadcast_info['title']}
                    
                    {broadcast_info['message']}
                    
                    {f"Link: {broadcast_info['action_url']}" if broadcast_info['action_url'] else ""}
                    
                    ---
                    Dikirim dari aplikasi Lunance
                    """
                    
                    # Kirim email
                    success = await self.email_service.send_email(
                        to_email=user["email"],
                        subject=subject,
                        html_content=html_content,
                        text_content=text_content
                    )
                    
                    if success:
                        sent_count += 1
                    
                except Exception as e:
                    logger.error(f"Error kirim email ke {user.get('email', 'unknown')}: {e}")
                    results["errors"].append(f"Email {user.get('email', 'unknown')}: {str(e)}")
            
            results["email_sent"] = sent_count
            logger.info(f"Email broadcast terkirim ke {sent_count} dari {len(users)} user")
            
        except Exception as e:
            logger.error(f"Error email broadcast: {e}")
            results["errors"].append(f"Email: {str(e)}")
    
    async def _send_push_broadcast(self, broadcast_info: Dict[str, Any], results: Dict[str, Any]):
        """Kirim broadcast via push notification (placeholder)."""
        try:
            # Placeholder untuk push notification
            # Implementasi actual akan menggunakan FCM, APNs, dll
            
            target_count = len(broadcast_info["target_users"])
            logger.info(f"Push notification akan dikirim ke {target_count} user")
            
            # Simulasi pengiriman
            results["push_sent"] = target_count
            
        except Exception as e:
            logger.error(f"Error push broadcast: {e}")
            results["errors"].append(f"Push: {str(e)}")
    
    async def _create_notification_broadcast(self, broadcast_info: Dict[str, Any], results: Dict[str, Any]):
        """Buat notification di database untuk broadcast."""
        try:
            from ..models.notification import NotificationCreate, NotificationType, NotificationPriority
            
            # Convert broadcast type ke notification type
            notification_type = NotificationType.SYSTEM
            if broadcast_info["type"] == BroadcastType.ANNOUNCEMENT.value:
                notification_type = NotificationType.SYSTEM
            elif broadcast_info["type"] == BroadcastType.EMERGENCY.value:
                notification_type = NotificationType.ADMIN
            
            # Convert priority
            priority_map = {
                BroadcastPriority.LOW.value: NotificationPriority.LOW,
                BroadcastPriority.NORMAL.value: NotificationPriority.NORMAL,
                BroadcastPriority.HIGH.value: NotificationPriority.HIGH,
                BroadcastPriority.URGENT.value: NotificationPriority.URGENT
            }
            notification_priority = priority_map.get(
                broadcast_info["priority"], 
                NotificationPriority.NORMAL
            )
            
            # Buat notification untuk setiap user
            created_count = 0
            for user_id in broadcast_info["target_users"]:
                try:
                    notification_data = NotificationCreate(
                        title=broadcast_info["title"],
                        message=broadcast_info["message"],
                        type=notification_type,
                        priority=notification_priority,
                        action_url=broadcast_info["action_url"],
                        action_text=broadcast_info["action_text"],
                        data=broadcast_info["data"]
                    )
                    
                    # Buat notification tanpa kirim email/push lagi
                    await notification_service.create_notification(
                        user_id=user_id,
                        notification_data=notification_data,
                        send_email=False,
                        send_push=False
                    )
                    
                    created_count += 1
                    
                except Exception as e:
                    logger.error(f"Error buat notification untuk user {user_id}: {e}")
                    results["errors"].append(f"Notification {user_id}: {str(e)}")
            
            results["notifications_created"] = created_count
            logger.info(f"Notification database dibuat untuk {created_count} user")
            
        except Exception as e:
            logger.error(f"Error buat notification broadcast: {e}")
            results["errors"].append(f"Notification DB: {str(e)}")


# Global broadcast service instance
broadcast_service = BroadcastService()