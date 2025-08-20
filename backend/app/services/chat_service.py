# app/services/chat_service.py - CLEANED VERSION - No AI responses
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId
import logging

from ..config.database import get_database
from ..models.chat import Conversation, Message, MessageType, ConversationStatus
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db

logger = logging.getLogger(__name__)

class ChatService:
    """Simple Chat Service without AI responses"""
    
    def __init__(self):
        self.db = get_database()
        logger.info("✅ ChatService initialized (No AI responses)")
    
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
        
        logger.info(f"✅ Conversation created: {conversation_id}")
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
            logger.error(f"❌ Error getting conversations: {e}")
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
            logger.error(f"❌ Error getting messages: {e}")
            return []
    
    async def send_message(self, user_id: str, conversation_id: str, content: str) -> Dict[str, Any]:
        """Send message without AI response"""
        
        try:
            now = now_for_db()
            logger.info(f"📨 Processing message from user {user_id}: '{content}'")
            
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
            
            # NO AI RESPONSE - Just echo message or return simple confirmation
            echo_timestamp = now_for_db()
            
            echo_message_data = {
                "conversation_id": conversation_id,
                "sender_id": None,
                "sender_type": "system",
                "content": "Pesan Anda telah diterima",
                "message_type": MessageType.TEXT.value,
                "status": "sent",
                "timestamp": echo_timestamp,
                "metadata": {
                    "response_type": "simple_echo",
                    "no_ai": True
                }
            }
            
            echo_result = self.db.messages.insert_one(echo_message_data)
            echo_message_id = str(echo_result.inserted_id)
            
            echo_message = Message(
                id=echo_message_id,
                conversation_id=conversation_id,
                sender_id=None,
                sender_type="system",
                content="Pesan Anda telah diterima",
                message_type=MessageType.TEXT,
                status="sent",
                timestamp=echo_timestamp,
                metadata={
                    "response_type": "simple_echo",
                    "no_ai": True
                }
            )
            
            # Update conversation
            await self._update_conversation_safe(conversation_id, content, "Pesan Anda telah diterima", user_id)
            
            logger.info(f"✅ Message processed successfully (No AI)")
            
            return {
                "user_message": user_message,
                "system_response": echo_message,
                "conversation_updated": True,
                "response_type": "simple_echo"
            }
            
        except Exception as e:
            logger.error(f"❌ Error in send_message: {e}")
            raise e
    
    async def _update_conversation_safe(self, conversation_id: str, user_message: str, system_response: str, user_id: str):
        """Update conversation dengan title generation"""
        try:
            current_conv = self.db.conversations.find_one({"_id": ObjectId(conversation_id)})
            if not current_conv:
                return
            
            current_count = current_conv.get("message_count", 0)
            new_count = current_count + 2
            
            current_title = current_conv.get("title")
            new_title = current_title
            
            # Simple title generation from first words
            if not current_title and current_count == 0:
                words = user_message.split()[:3]
                new_title = " ".join(words) + "..." if len(words) == 3 else " ".join(words)
            
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
            logger.error(f"❌ Error updating conversation: {e}")
    
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
            logger.error(f"Error getting conversation: {e}")
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
            logger.error(f"❌ Error deleting conversation: {e}")
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
            logger.error(f"❌ Error in auto_delete_empty_conversations: {e}")
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
            logger.error(f"Error searching conversations: {e}")
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
            logger.error(f"❌ Error in cleanup_user_conversations: {e}")
            return {"empty_conversations_deleted": 0, "conversations_updated": 0, "total_cleaned": 0}
    
    async def get_chat_statistics(self, user_id: str) -> Dict[str, Any]:
        """Statistik chat"""
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
            
            recent_activity = self.db.conversations.find_one(
                {"user_id": user_id, "status": {"$ne": ConversationStatus.DELETED.value}},
                sort=[("updated_at", -1)]
            )
            
            last_activity = recent_activity.get("updated_at") if recent_activity else None
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "today_messages": 0,
                "weekly_messages": 0,
                "last_activity": last_activity,
                "timezone": "Asia/Jakarta (WIB/GMT+7)",
                "current_time_wib": IndonesiaDatetime.format(IndonesiaDatetime.now()),
                "chat_version": "Simple Chat (No AI)",
                "features_enabled": [
                    "Simple Chat Interface",
                    "Message Storage",
                    "Conversation Management",
                    "No AI Responses"
                ]
            }
        except Exception as e:
            logger.error(f"Error getting chat statistics: {e}")
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