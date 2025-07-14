# app/services/chat_service.py - Updated untuk menggunakan Luna AI Core
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..models.chat import Conversation, Message, MessageType, ConversationStatus
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .luna_ai_core import LunaAICore

class ChatService:
    """Enhanced Chat Service dengan Luna AI Core integration"""
    
    def __init__(self):
        self.db = get_database()
        self.luna_ai = LunaAICore()
    
    async def create_conversation(self, user_id: str) -> Conversation:
        """Membuat percakapan baru"""
        now = now_for_db()
        
        conversation_data = {
            "user_id": user_id,
            "title": None,
            "status": ConversationStatus.ACTIVE.value,
            "last_message": None,
            "last_message_at": None,
            "message_count": 0,
            "created_at": now,
            "updated_at": now
        }
        
        result = self.db.conversations.insert_one(conversation_data)
        conversation_id = str(result.inserted_id)
        
        conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            title=None,
            status=ConversationStatus.ACTIVE,
            last_message=None,
            last_message_at=None,
            message_count=0,
            created_at=now,
            updated_at=now
        )
        
        print(f"✅ Conversation created: {conversation_id}")
        return conversation
    
    async def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Conversation]:
        """Mengambil daftar percakapan user"""
        try:
            query = {
                "user_id": user_id,
                "$or": [
                    {"status": ConversationStatus.ACTIVE.value},
                    {"status": {"$exists": False}}
                ]
            }
            
            cursor = self.db.conversations.find(query).sort("updated_at", -1).limit(limit)
            
            conversations = []
            for doc in cursor:
                if "created_at" not in doc:
                    doc["created_at"] = doc.get("updated_at", now_for_db())
                if "status" not in doc:
                    doc["status"] = ConversationStatus.ACTIVE.value
                
                conversation = Conversation.from_mongo(doc)
                conversations.append(conversation)
            
            return conversations
            
        except Exception as e:
            print(f"❌ Error getting conversations: {e}")
            return []
    
    async def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Message]:
        """Mengambil pesan dalam percakapan"""
        try:
            cursor = self.db.messages.find(
                {"conversation_id": conversation_id}
            ).sort("timestamp", 1).limit(limit)
            
            messages = []
            for doc in cursor:
                if "timestamp" not in doc:
                    doc["timestamp"] = now_for_db()
                
                message = Message.from_mongo(doc)
                messages.append(message)
            
            return messages
            
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    async def send_message(self, user_id: str, conversation_id: str, content: str) -> Dict[str, Any]:
        """Send message dengan Luna AI Core integration"""
        
        try:
            now = now_for_db()
            print(f"📨 Processing message from user {user_id}: '{content}'")
            
            # Save user message
            user_message_data = {
                "conversation_id": conversation_id,
                "sender_id": user_id,
                "sender_type": "user",
                "content": content,
                "message_type": MessageType.TEXT.value,
                "status": "sent",
                "timestamp": now
            }
            
            user_result = self.db.messages.insert_one(user_message_data)
            user_message_id = str(user_result.inserted_id)
            
            user_message = Message(
                id=user_message_id,
                conversation_id=conversation_id,
                sender_id=user_id,
                sender_type="user",
                content=content,
                message_type=MessageType.TEXT,
                status="sent",
                timestamp=now
            )
            
            # Generate Luna response using Luna AI Core
            luna_response_text = await self.luna_ai.generate_response(
                content, user_id, conversation_id, user_message_id
            )
            
            luna_timestamp = now_for_db()
            
            # Save Luna response
            luna_message_data = {
                "conversation_id": conversation_id,
                "sender_id": None,
                "sender_type": "luna",
                "content": luna_response_text,
                "message_type": MessageType.TEXT.value,
                "status": "sent",
                "timestamp": luna_timestamp
            }
            
            luna_result = self.db.messages.insert_one(luna_message_data)
            luna_message_id = str(luna_result.inserted_id)
            
            luna_message = Message(
                id=luna_message_id,
                conversation_id=conversation_id,
                sender_id=None,
                sender_type="luna",
                content=luna_response_text,
                message_type=MessageType.TEXT,
                status="sent",
                timestamp=luna_timestamp
            )
            
            # Update conversation
            await self._update_conversation_safe(conversation_id, content, luna_response_text, user_id)
            
            print(f"✅ Message processed successfully")
            
            # Check for financial data metadata
            financial_metadata = {}
            response_type = "regular"
            
            # If Luna response contains financial confirmation, add metadata
            if any(phrase in luna_response_text for phrase in ["detail transaksi", "target tabungan", "ketik **\"ya\"**"]):
                financial_metadata = {
                    "contains_financial_data": True,
                    "requires_confirmation": True,
                    "data_type": "confirmation_request"
                }
                response_type = "financial_confirmation"
            elif any(phrase in luna_response_text for phrase in ["berhasil disimpan", "berhasil dibuat", "data dibatalkan"]):
                financial_metadata = {
                    "contains_financial_data": True,
                    "requires_confirmation": False,
                    "data_type": "financial_result"
                }
                response_type = "financial_result"
            elif any(phrase in luna_response_text for phrase in ["total tabungan", "target bulan", "progress tabungan", "pengeluaran terbesar"]):
                financial_metadata = {
                    "contains_financial_data": True,
                    "requires_confirmation": False,
                    "data_type": "financial_query_result"
                }
                response_type = "financial_info"
            
            return {
                "user_message": user_message,
                "luna_response": luna_message,
                "conversation_updated": True,
                "financial_data": financial_metadata if financial_metadata else None,
                "response_type": response_type
            }
            
        except Exception as e:
            print(f"❌ Error in send_message: {e}")
            raise e
    
    async def _update_conversation_safe(self, conversation_id: str, user_message: str, luna_response: str, user_id: str):
        """Update conversation dengan title generation"""
        try:
            current_conv = self.db.conversations.find_one({"_id": ObjectId(conversation_id)})
            if not current_conv:
                return
            
            current_count = current_conv.get("message_count", 0)
            new_count = current_count + 2
            
            current_title = current_conv.get("title")
            new_title = current_title
            
            # Generate title from first user message using Luna AI Core
            if not current_title and current_count == 0:
                new_title = self.luna_ai.generate_conversation_title(user_message, luna_response)
            
            update_time = now_for_db()
            
            update_data = {
                "last_message": user_message,
                "last_message_at": update_time,
                "updated_at": update_time,
                "message_count": new_count,
                "status": ConversationStatus.ACTIVE.value
            }
            
            if new_title:
                update_data["title"] = new_title
            
            self.db.conversations.update_one(
                {"_id": ObjectId(conversation_id)},
                {"$set": update_data}
            )
            
        except Exception as e:
            print(f"❌ Error updating conversation: {e}")
    
    async def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Mengambil percakapan berdasarkan ID"""
        try:
            doc = self.db.conversations.find_one({"_id": ObjectId(conversation_id)})
            if doc:
                if "created_at" not in doc:
                    doc["created_at"] = doc.get("updated_at", now_for_db())
                if "status" not in doc:
                    doc["status"] = ConversationStatus.ACTIVE.value
                return Conversation.from_mongo(doc)
            return None
        except Exception as e:
            print(f"Error getting conversation: {e}")
            return None
    
    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Hapus percakapan"""
        try:
            result = self.db.conversations.update_one(
                {"_id": ObjectId(conversation_id), "user_id": user_id},
                {"$set": {
                    "status": ConversationStatus.DELETED.value,
                    "updated_at": now_for_db()
                }}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error deleting conversation: {e}")
            return False
    
    async def auto_delete_empty_conversations(self, user_id: str) -> int:
        """Auto-delete conversations kosong"""
        try:
            empty_conversations = self.db.conversations.find({
                "user_id": user_id,
                "$or": [
                    {"message_count": 0},
                    {"message_count": {"$exists": False}},
                    {"last_message": {"$exists": False}},
                    {"last_message": None}
                ],
                "status": {"$ne": ConversationStatus.DELETED.value}
            })
            
            deleted_count = 0
            for conv in empty_conversations:
                conversation_id = str(conv["_id"])
                message_count = self.db.messages.count_documents({
                    "conversation_id": conversation_id
                })
                
                if message_count == 0:
                    result = self.db.conversations.update_one(
                        {"_id": conv["_id"]},
                        {"$set": {
                            "status": ConversationStatus.DELETED.value,
                            "updated_at": now_for_db()
                        }}
                    )
                    if result.modified_count > 0:
                        deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"❌ Error in auto_delete_empty_conversations: {e}")
            return 0
    
    async def search_conversations(self, user_id: str, query: str) -> List[Conversation]:
        """Search percakapan"""
        try:
            search_query = {
                "user_id": user_id,
                "$or": [
                    {"status": ConversationStatus.ACTIVE.value},
                    {"status": {"$exists": False}}
                ],
                "$and": [
                    {"$or": [
                        {"title": {"$regex": query, "$options": "i"}},
                        {"last_message": {"$regex": query, "$options": "i"}}
                    ]}
                ]
            }
            
            conversations = self.db.conversations.find(search_query).sort("updated_at", -1)
            
            result = []
            for doc in conversations:
                if "created_at" not in doc:
                    doc["created_at"] = doc.get("updated_at", now_for_db())
                if "status" not in doc:
                    doc["status"] = ConversationStatus.ACTIVE.value
                result.append(Conversation.from_mongo(doc))
            
            return result
        except Exception as e:
            print(f"Error searching conversations: {e}")
            return []
    
    async def cleanup_user_conversations(self, user_id: str) -> Dict[str, int]:
        """Cleanup conversations user"""
        try:
            empty_deleted = await self.auto_delete_empty_conversations(user_id)
            return {
                "empty_conversations_deleted": empty_deleted,
                "conversations_updated": 0,
                "total_cleaned": empty_deleted
            }
        except Exception as e:
            print(f"❌ Error in cleanup_user_conversations: {e}")
            return {"empty_conversations_deleted": 0, "conversations_updated": 0, "total_cleaned": 0}
    
    async def get_chat_statistics(self, user_id: str) -> Dict[str, Any]:
        """Statistik chat dengan timezone Indonesia"""
        try:
            total_conversations = self.db.conversations.count_documents({
                "user_id": user_id,
                "status": {"$ne": ConversationStatus.DELETED.value}
            })
            
            user_conversations = self.db.conversations.find(
                {"user_id": user_id, "status": {"$ne": ConversationStatus.DELETED.value}},
                {"_id": 1}
            )
            conversation_ids = [str(conv["_id"]) for conv in user_conversations]
            
            total_messages = self.db.messages.count_documents({
                "conversation_id": {"$in": conversation_ids}
            })
            
            # Get recent activity
            recent_activity = self.db.conversations.find_one(
                {"user_id": user_id, "status": {"$ne": ConversationStatus.DELETED.value}},
                sort=[("updated_at", -1)]
            )
            
            last_activity = recent_activity.get("updated_at") if recent_activity else None
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "today_messages": 0,  # Would need more complex query for accurate count
                "weekly_messages": 0, # Would need more complex query for accurate count
                "last_activity": last_activity,
                "timezone": "Asia/Jakarta (WIB/GMT+7)",
                "current_time_wib": IndonesiaDatetime.format(IndonesiaDatetime.now()),
                "luna_ai_version": "Enhanced for Indonesian Students",
                "features_enabled": [
                    "Financial Intelligence",
                    "Auto Transaction Parsing",
                    "Student Categories",
                    "Target Date Recognition",
                    "Real-time Financial Queries",
                    "Bahasa Indonesia Support"
                ]
            }
        except Exception as e:
            print(f"Error getting chat statistics: {e}")
            return {
                "total_conversations": 0,
                "total_messages": 0,
                "today_messages": 0,
                "weekly_messages": 0,
                "last_activity": None,
                "timezone": "Asia/Jakarta (WIB/GMT+7)",
                "current_time_wib": IndonesiaDatetime.format(IndonesiaDatetime.now()),
                "error": str(e)
            }
    
    # === FINANCIAL CHAT INTEGRATION METHODS ===
    
    async def get_pending_financial_confirmations(self, user_id: str, conversation_id: str) -> List[Dict[str, Any]]:
        """Dapatkan financial data yang belum dikonfirmasi untuk conversation ini"""
        try:
            pending_data = self.luna_ai.db.pending_financial_data.find({
                "user_id": user_id,
                "conversation_id": conversation_id,
                "is_confirmed": False,
                "expires_at": {"$gt": now_for_db()}
            }).sort("created_at", -1)
            
            result = []
            for data in pending_data:
                result.append({
                    "pending_id": str(data["_id"]),
                    "data_type": data["data_type"],
                    "parsed_data": data["parsed_data"],
                    "original_message": data["original_message"],
                    "created_at": data["created_at"],
                    "expires_at": data["expires_at"]
                })
            
            return result
        except Exception as e:
            print(f"Error getting pending confirmations: {e}")
            return []
    
    async def confirm_financial_data_via_chat(self, user_id: str, conversation_id: str, 
                                           confirmed: bool, pending_id: str = None) -> Dict[str, Any]:
        """Konfirmasi financial data melalui chat interface"""
        try:
            if not pending_id:
                # Get latest pending data
                pending_data = self.luna_ai.get_latest_pending_data(user_id, conversation_id)
                if pending_data:
                    pending_id = str(pending_data["_id"])
            
            if not pending_id:
                return {"success": False, "message": "Tidak ada data yang menunggu konfirmasi"}
            
            # Use Luna AI Core confirmation logic
            from .finance_service import FinanceService
            finance_service = FinanceService()
            
            result = finance_service.confirm_pending_data(pending_id, user_id, confirmed)
            
            return result
        except Exception as e:
            print(f"Error confirming financial data via chat: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    async def get_financial_chat_context(self, user_id: str) -> Dict[str, Any]:
        """Dapatkan context keuangan untuk chat (untuk Luna AI responses)"""
        try:
            # Get user's current financial status for context
            from .finance_service import FinanceService
            finance_service = FinanceService()
            
            # Get basic financial dashboard
            dashboard = await finance_service.get_financial_dashboard(user_id)
            
            context = {
                "total_savings": dashboard["calculated_totals"]["actual_current_savings"],
                "monthly_target": dashboard["user_financial_settings"]["monthly_savings_target"],
                "active_goals_count": dashboard["active_goals"]["count"],
                "recent_transactions_count": len(dashboard["recent_activity"]["transactions"]),
                "needs_sync": dashboard["sync_status"]["needs_sync"]
            }
            
            return context
        except Exception as e:
            print(f"Error getting financial chat context: {e}")
            return {
                "total_savings": 0,
                "monthly_target": 0,
                "active_goals_count": 0,
                "recent_transactions_count": 0,
                "needs_sync": False,
                "error": str(e)
            }