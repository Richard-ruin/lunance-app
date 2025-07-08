# app/websocket/middleware.py
"""Middleware untuk WebSocket dengan autentikasi dan rate limiting."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict
import time

from ..utils.jwt import verify_token, TokenExpiredError, InvalidTokenError
from ..models.user import UserRole

logger = logging.getLogger(__name__)


class WebSocketAuthMiddleware:
    """Middleware autentikasi untuk WebSocket."""
    
    def __init__(self):
        self.authenticated_connections: Dict[str, Dict[str, Any]] = {}
    
    async def authenticate_connection(
        self, 
        websocket: WebSocket, 
        token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Autentikasi koneksi WebSocket.
        
        Args:
            websocket: Instance WebSocket
            token: JWT token untuk autentikasi
            
        Returns:
            Info user jika berhasil, None jika gagal
        """
        try:
            if not token:
                await websocket.close(code=4001, reason="Token autentikasi diperlukan")
                return None
            
            # Verifikasi token
            payload = verify_token(token)
            
            # Info user
            user_info = {
                "user_id": payload.sub,
                "email": payload.email,
                "role": payload.role,
                "authenticated_at": datetime.utcnow(),
                "token": token
            }
            
            # Simpan koneksi yang sudah terautentikasi
            connection_id = f"{websocket.client.host}:{websocket.client.port}"
            self.authenticated_connections[connection_id] = user_info
            
            logger.info(f"WebSocket terautentikasi untuk user: {payload.sub}")
            return user_info
            
        except TokenExpiredError:
            await websocket.close(code=4001, reason="Token sudah kadaluarsa")
            return None
        except InvalidTokenError:
            await websocket.close(code=4001, reason="Token tidak valid")
            return None
        except Exception as e:
            logger.error(f"Error autentikasi WebSocket: {e}")
            await websocket.close(code=4002, reason="Autentikasi gagal")
            return None
    
    async def check_permissions(
        self, 
        user_info: Dict[str, Any], 
        required_role: UserRole = UserRole.STUDENT
    ) -> bool:
        """
        Periksa izin user untuk akses WebSocket.
        
        Args:
            user_info: Informasi user
            required_role: Role yang diperlukan
            
        Returns:
            True jika memiliki izin
        """
        try:
            user_role = user_info.get("role")
            
            if required_role == UserRole.ADMIN:
                return user_role == UserRole.ADMIN
            else:
                return user_role in [UserRole.STUDENT, UserRole.ADMIN]
                
        except Exception as e:
            logger.error(f"Error memeriksa izin: {e}")
            return False
    
    def remove_connection(self, websocket: WebSocket):
        """Hapus koneksi dari daftar terautentikasi."""
        try:
            connection_id = f"{websocket.client.host}:{websocket.client.port}"
            if connection_id in self.authenticated_connections:
                del self.authenticated_connections[connection_id]
        except Exception as e:
            logger.error(f"Error menghapus koneksi: {e}")


class WebSocketRateLimiter:
    """Rate limiter untuk WebSocket messages."""
    
    def __init__(self):
        self.user_message_counts: Dict[str, list] = defaultdict(list)
        self.max_messages_per_minute = 60
        self.max_messages_per_hour = 1000
        self.cleanup_interval = 300  # 5 menit
        self.last_cleanup = time.time()
    
    def is_rate_limited(self, user_id: str) -> Dict[str, Any]:
        """
        Periksa apakah user terkena rate limit.
        
        Args:
            user_id: ID user
            
        Returns:
            Dict dengan status rate limit
        """
        try:
            now = time.time()
            
            # Cleanup old records jika perlu
            if now - self.last_cleanup > self.cleanup_interval:
                self._cleanup_old_records()
                self.last_cleanup = now
            
            # Ambil timestamps pesan user
            user_messages = self.user_message_counts[user_id]
            
            # Hapus pesan yang sudah lebih dari 1 jam
            hour_ago = now - 3600
            user_messages = [ts for ts in user_messages if ts > hour_ago]
            self.user_message_counts[user_id] = user_messages
            
            # Periksa limit per jam
            if len(user_messages) >= self.max_messages_per_hour:
                return {
                    "limited": True,
                    "reason": "Batas pesan per jam terlampaui",
                    "limit_type": "hourly",
                    "reset_in": 3600 - (now - min(user_messages))
                }
            
            # Periksa limit per menit
            minute_ago = now - 60
            recent_messages = [ts for ts in user_messages if ts > minute_ago]
            
            if len(recent_messages) >= self.max_messages_per_minute:
                return {
                    "limited": True,
                    "reason": "Batas pesan per menit terlampaui",
                    "limit_type": "minute",
                    "reset_in": 60 - (now - min(recent_messages))
                }
            
            # Tambahkan timestamp pesan saat ini
            self.user_message_counts[user_id].append(now)
            
            return {
                "limited": False,
                "messages_this_minute": len(recent_messages) + 1,
                "messages_this_hour": len(user_messages) + 1
            }
            
        except Exception as e:
            logger.error(f"Error memeriksa rate limit: {e}")
            return {"limited": False}
    
    def _cleanup_old_records(self):
        """Bersihkan record lama."""
        try:
            now = time.time()
            hour_ago = now - 3600
            
            # Hapus record yang sudah lebih dari 1 jam
            for user_id in list(self.user_message_counts.keys()):
                messages = self.user_message_counts[user_id]
                recent_messages = [ts for ts in messages if ts > hour_ago]
                
                if not recent_messages:
                    del self.user_message_counts[user_id]
                else:
                    self.user_message_counts[user_id] = recent_messages
            
            logger.debug("Rate limiter cleanup selesai")
            
        except Exception as e:
            logger.error(f"Error cleanup rate limiter: {e}")


class WebSocketMessageValidator:
    """Validator untuk pesan WebSocket."""
    
    def __init__(self):
        self.max_message_size = 64 * 1024  # 64KB
        self.required_fields = ["type"]
        
        # Daftar tipe pesan yang valid
        self.valid_message_types = {
            "chat_message": ["message", "session_id"],
            "typing": ["typing"],
            "get_chat_history": ["session_id", "limit"],
            "heartbeat": [],
            "refresh_dashboard": [],
            "get_transactions": ["filters"],
            "get_analytics": ["period"],
            "get_notifications": ["page", "per_page"],
            "mark_read": ["notification_id"],
            "mark_all_read": [],
            "delete_notification": ["notification_id"],
            "get_stats": [],
            "broadcast_announcement": ["announcement", "target_type"]
        }
    
    def validate_message(self, message_text: str) -> Dict[str, Any]:
        """
        Validasi pesan WebSocket.
        
        Args:
            message_text: Teks pesan JSON
            
        Returns:
            Dict dengan hasil validasi
        """
        try:
            # Periksa ukuran pesan
            if len(message_text) > self.max_message_size:
                return {
                    "valid": False,
                    "error": f"Pesan terlalu besar (maksimal {self.max_message_size} bytes)",
                    "error_code": "MESSAGE_TOO_LARGE"
                }
            
            # Parse JSON
            try:
                message_data = json.loads(message_text)
            except json.JSONDecodeError as e:
                return {
                    "valid": False,
                    "error": f"Format JSON tidak valid: {str(e)}",
                    "error_code": "INVALID_JSON"
                }
            
            # Periksa field yang diperlukan
            for field in self.required_fields:
                if field not in message_data:
                    return {
                        "valid": False,
                        "error": f"Field '{field}' diperlukan",
                        "error_code": "MISSING_REQUIRED_FIELD"
                    }
            
            # Periksa tipe pesan
            message_type = message_data.get("type")
            if message_type not in self.valid_message_types:
                return {
                    "valid": False,
                    "error": f"Tipe pesan tidak valid: {message_type}",
                    "error_code": "INVALID_MESSAGE_TYPE"
                }
            
            # Periksa field optional berdasarkan tipe
            optional_fields = self.valid_message_types[message_type]
            for field in optional_fields:
                if field in message_data:
                    # Validasi field spesifik
                    validation_result = self._validate_field(field, message_data[field])
                    if not validation_result["valid"]:
                        return validation_result
            
            return {
                "valid": True,
                "message_data": message_data,
                "message_type": message_type
            }
            
        except Exception as e:
            logger.error(f"Error validasi pesan: {e}")
            return {
                "valid": False,
                "error": "Error internal validasi pesan",
                "error_code": "INTERNAL_VALIDATION_ERROR"
            }
    
    def _validate_field(self, field_name: str, field_value: Any) -> Dict[str, Any]:
        """Validasi field spesifik."""
        try:
            if field_name == "message":
                if not isinstance(field_value, str):
                    return {
                        "valid": False,
                        "error": "Field 'message' harus berupa string",
                        "error_code": "INVALID_FIELD_TYPE"
                    }
                if len(field_value.strip()) == 0:
                    return {
                        "valid": False,
                        "error": "Pesan tidak boleh kosong",
                        "error_code": "EMPTY_MESSAGE"
                    }
                if len(field_value) > 4000:
                    return {
                        "valid": False,
                        "error": "Pesan terlalu panjang (maksimal 4000 karakter)",
                        "error_code": "MESSAGE_TOO_LONG"
                    }
            
            elif field_name == "session_id":
                if field_value and not isinstance(field_value, str):
                    return {
                        "valid": False,
                        "error": "Field 'session_id' harus berupa string",
                        "error_code": "INVALID_FIELD_TYPE"
                    }
            
            elif field_name == "limit":
                if not isinstance(field_value, int) or field_value < 1 or field_value > 100:
                    return {
                        "valid": False,
                        "error": "Field 'limit' harus berupa integer antara 1-100",
                        "error_code": "INVALID_FIELD_VALUE"
                    }
            
            elif field_name == "page":
                if not isinstance(field_value, int) or field_value < 1:
                    return {
                        "valid": False,
                        "error": "Field 'page' harus berupa integer >= 1",
                        "error_code": "INVALID_FIELD_VALUE"
                    }
            
            elif field_name == "per_page":
                if not isinstance(field_value, int) or field_value < 1 or field_value > 100:
                    return {
                        "valid": False,
                        "error": "Field 'per_page' harus berupa integer antara 1-100",
                        "error_code": "INVALID_FIELD_VALUE"
                    }
            
            elif field_name == "period":
                valid_periods = ["day", "week", "month", "year"]
                if field_value not in valid_periods:
                    return {
                        "valid": False,
                        "error": f"Field 'period' harus salah satu dari: {', '.join(valid_periods)}",
                        "error_code": "INVALID_FIELD_VALUE"
                    }
            
            elif field_name == "notification_id":
                if not isinstance(field_value, str) or len(field_value) != 24:
                    return {
                        "valid": False,
                        "error": "Field 'notification_id' harus berupa string ObjectId yang valid",
                        "error_code": "INVALID_FIELD_VALUE"
                    }
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Error validasi field {field_name}: {e}")
            return {
                "valid": False,
                "error": f"Error validasi field {field_name}",
                "error_code": "FIELD_VALIDATION_ERROR"
            }


class WebSocketLogger:
    """Logger khusus untuk WebSocket activities."""
    
    def __init__(self):
        self.logger = logging.getLogger("websocket")
        
        # Setup handler untuk WebSocket logs
        handler = logging.FileHandler("logs/websocket.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_connection(self, user_id: str, connection_type: str, status: str):
        """Log koneksi WebSocket."""
        self.logger.info(f"Koneksi {connection_type}: User {user_id} - {status}")
    
    def log_message(self, user_id: str, message_type: str, direction: str):
        """Log pesan WebSocket."""
        self.logger.debug(f"Pesan {direction}: User {user_id} - Type: {message_type}")
    
    def log_error(self, user_id: str, error: str, context: str):
        """Log error WebSocket."""
        self.logger.error(f"Error {context}: User {user_id} - {error}")
    
    def log_rate_limit(self, user_id: str, limit_type: str):
        """Log rate limiting."""
        self.logger.warning(f"Rate limit {limit_type}: User {user_id}")


# Global instances
websocket_auth = WebSocketAuthMiddleware()
websocket_rate_limiter = WebSocketRateLimiter()
websocket_validator = WebSocketMessageValidator()
websocket_logger = WebSocketLogger()


# Utility functions
async def handle_websocket_error(
    websocket: WebSocket, 
    error_message: str, 
    error_code: str = "UNKNOWN_ERROR",
    close_connection: bool = False
):
    """
    Handle WebSocket error dengan mengirim pesan error ke client.
    
    Args:
        websocket: Instance WebSocket
        error_message: Pesan error
        error_code: Kode error
        close_connection: Apakah tutup koneksi
    """
    try:
        error_response = {
            "type": "error",
            "error": error_message,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not close_connection:
            await websocket.send_text(json.dumps(error_response, default=str))
        else:
            await websocket.close(code=4000, reason=error_message)
            
    except Exception as e:
        logger.error(f"Error handling WebSocket error: {e}")


async def send_websocket_response(
    websocket: WebSocket,
    response_type: str,
    data: Any = None,
    message: str = None
):
    """
    Kirim response terstruktur ke WebSocket client.
    
    Args:
        websocket: Instance WebSocket
        response_type: Tipe response
        data: Data response
        message: Pesan response
    """
    try:
        response = {
            "type": response_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        if message:
            response["message"] = message
        
        await websocket.send_text(json.dumps(response, default=str))
        
    except Exception as e:
        logger.error(f"Error sending WebSocket response: {e}")


def websocket_error_handler(func):
    """
    Decorator untuk handle error di WebSocket endpoints.
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"Unhandled WebSocket error: {e}")
            # Jika masih ada WebSocket connection, kirim error
            if args and hasattr(args[0], 'send_text'):
                try:
                    await handle_websocket_error(
                        args[0], 
                        "Terjadi kesalahan internal", 
                        "INTERNAL_ERROR"
                    )
                except:
                    pass
    
    return wrapper