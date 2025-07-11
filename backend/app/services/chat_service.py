import re
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..models.chat import Conversation, Message, MessageType, ConversationStatus
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db

class LunaAI:
    """Simple Luna AI chatbot with financial focus"""
    
    def __init__(self):
        self.financial_keywords = [
            'budget', 'anggaran', 'uang', 'keuangan', 'tabungan', 'investasi',
            'pengeluaran', 'pemasukan', 'gaji', 'belanja', 'cicilan', 'hutang',
            'kredit', 'bank', 'atm', 'transfer', 'pembayaran', 'bayar'
        ]
        
        self.greetings = [
            "Halo! Saya Luna, asisten keuangan pribadi Anda. Ada yang bisa saya bantu hari ini?",
            "Hi! Luna di sini. Siap membantu Anda mengelola keuangan dengan lebih baik!",
            "Selamat datang! Saya Luna, mari kita atur keuangan Anda bersama-sama.",
        ]
        
        self.financial_responses = [
            "Itu pertanyaan bagus tentang keuangan! Mari kita analisis bersama-sama.",
            "Untuk mengelola keuangan yang lebih baik, saya sarankan Anda mulai dengan membuat anggaran bulanan.",
            "Berdasarkan pengalaman, tips terbaik adalah mengalokasikan 20% penghasilan untuk tabungan.",
            "Saya bisa membantu Anda melacak pengeluaran dan memberikan insight keuangan yang berguna.",
            "Mari kita buat rencana keuangan yang sesuai dengan tujuan Anda!",
        ]
        
        self.general_responses = [
            "Terima kasih atas pertanyaan Anda. Sebagai asisten keuangan, saya lebih fokus membantu masalah finansial.",
            "Saya di sini untuk membantu Anda dengan topik keuangan. Ada yang ingin dibahas tentang finansial?",
            "Mungkin saya bisa membantu lebih baik jika pertanyaannya terkait keuangan personal Anda?",
        ]
        
        self.expense_tips = [
            "💡 Tip hemat: Coba gunakan metode 50/30/20 - 50% kebutuhan, 30% keinginan, 20% tabungan.",
            "💰 Saran: Selalu bandingkan harga sebelum membeli barang besar.",
            "📊 Insight: Tracking pengeluaran harian bisa menghemat 15-20% budget bulanan.",
            "🎯 Goal: Tetapkan target tabungan bulanan yang realistis dan konsisten.",
        ]

    def generate_response(self, user_message: str, user_id: str = None) -> str:
        """Generate response dari Luna AI"""
        message_lower = user_message.lower()
        
        # Greeting responses
        if any(word in message_lower for word in ['halo', 'hai', 'hi', 'hello', 'selamat']):
            return random.choice(self.greetings)
        
        # Thank you responses
        if any(word in message_lower for word in ['terima kasih', 'thanks', 'makasih']):
            return "Sama-sama! Senang bisa membantu Anda. Ada lagi yang ingin dibahas tentang keuangan?"
        
        # Financial keyword responses
        if any(keyword in message_lower for keyword in self.financial_keywords):
            response = random.choice(self.financial_responses)
            
            # Add specific tips based on keywords
            if 'budget' in message_lower or 'anggaran' in message_lower:
                response += "\n\n" + "📋 Untuk membuat budget yang efektif:\n1. Catat semua pemasukan\n2. List semua pengeluaran wajib\n3. Alokasikan untuk tabungan\n4. Sisanya untuk pengeluaran fleksibel"
            elif 'tabungan' in message_lower:
                response += "\n\n" + "🏦 Tips menabung:\n• Otomatis transfer ke rekening tabungan\n• Mulai dari jumlah kecil tapi konsisten\n• Pisahkan rekening tabungan dengan pengeluaran"
            elif 'investasi' in message_lower:
                response += "\n\n" + "📈 Prinsip investasi pemula:\n• Pelajari dulu sebelum berinvestasi\n• Diversifikasi portfolio\n• Investasi jangka panjang lebih aman\n• Gunakan uang dingin"
            
            # Add random tip
            if random.choice([True, False]):
                response += "\n\n" + random.choice(self.expense_tips)
                
            return response
        
        # Question about Luna
        if any(word in message_lower for word in ['luna', 'kamu', 'anda', 'siapa']):
            return "Saya Luna, asisten AI yang dirancang khusus untuk membantu mengelola keuangan pribadi. Saya bisa membantu Anda dengan budgeting, tips menghemat, dan analisis keuangan sederhana!"
        
        # Help requests
        if any(word in message_lower for word in ['bantuan', 'help', 'tolong', 'gimana', 'bagaimana']):
            return "Tentu! Saya bisa membantu Anda dengan:\n\n📊 Analisis pengeluaran\n💰 Tips menghemat uang\n📋 Membuat budget\n🎯 Perencanaan keuangan\n💡 Saran investasi dasar\n\nAda topik spesifik yang ingin dibahas?"
        
        # Default responses
        return random.choice(self.general_responses)

class ChatService:
    """Service untuk mengelola chat dan percakapan"""
    
    def __init__(self):
        self.db = get_database()
        self.luna_ai = LunaAI()
    
    async def create_conversation(self, user_id: str) -> Conversation:
        """Membuat percakapan baru dengan timezone Indonesia"""
        # Menggunakan waktu Indonesia untuk konsistensi
        now = now_for_db()
        
        conversation_data = {
            "user_id": user_id,
            "title": None,  # Will be auto-generated dari pesan pertama
            "status": ConversationStatus.ACTIVE.value,
            "last_message": None,
            "last_message_at": None,
            "message_count": 0,
            "created_at": now,
            "updated_at": now
        }
        
        print(f"Creating conversation at Indonesia time: {IndonesiaDatetime.format(now)}")
        print(f"Conversation data: {conversation_data}")
        
        # Insert ke database
        result = self.db.conversations.insert_one(conversation_data)
        conversation_id = str(result.inserted_id)
        
        # Create conversation object
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
        
        print(f"✅ Conversation created successfully with ID: {conversation_id}")
        
        return conversation
    
    async def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Conversation]:
        """Mengambil daftar percakapan user"""
        try:
            print(f"Getting conversations for user: {user_id}, limit: {limit}")
            
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
                # Ensure all required fields exist
                if "created_at" not in doc:
                    doc["created_at"] = doc.get("updated_at", now_for_db())
                if "status" not in doc:
                    doc["status"] = ConversationStatus.ACTIVE.value
                
                conversation = Conversation.from_mongo(doc)
                conversations.append(conversation)
                
                # Debug: show timezone info
                if doc.get("created_at"):
                    indonesia_time = IndonesiaDatetime.format(doc["created_at"])
                    print(f"Conversation {doc['_id']}: created at {indonesia_time} WIB")
            
            print(f"✅ Found {len(conversations)} conversations")
            return conversations
            
        except Exception as e:
            print(f"❌ Error getting conversations: {e}")
            return []
    
    async def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Message]:
        """Mengambil pesan dalam percakapan"""
        try:
            print(f"Getting messages for conversation: {conversation_id}")
            
            cursor = self.db.messages.find(
                {"conversation_id": conversation_id}
            ).sort("timestamp", 1).limit(limit)
            
            messages = []
            for doc in cursor:
                # Ensure timestamp exists
                if "timestamp" not in doc:
                    doc["timestamp"] = now_for_db()
                
                message = Message.from_mongo(doc)
                messages.append(message)
                
                # Debug: show timezone info
                indonesia_time = IndonesiaDatetime.format(doc["timestamp"])
                print(f"Message {doc['_id']}: sent at {indonesia_time} WIB")
            
            print(f"✅ Found {len(messages)} messages")
            return messages
            
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    async def send_message(self, user_id: str, conversation_id: str, content: str) -> Dict[str, Any]:
        """Mengirim pesan user dan generate response dari Luna dengan timezone Indonesia"""
        
        try:
            # Menggunakan waktu Indonesia
            now = now_for_db()
            indonesia_time_str = IndonesiaDatetime.format(now)
            
            print(f"Sending message at Indonesia time: {indonesia_time_str}")
            
            # Simpan pesan user dengan timestamp Indonesia
            user_message_data = {
                "conversation_id": conversation_id,
                "sender_id": user_id,
                "sender_type": "user",
                "content": content,
                "message_type": MessageType.TEXT.value,
                "status": "sent",
                "timestamp": now
            }
            
            print(f"User message timestamp: {indonesia_time_str}")
            
            user_result = self.db.messages.insert_one(user_message_data)
            user_message_id = str(user_result.inserted_id)
            
            # Create user message object
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
            
            # Generate response dari Luna
            luna_response = self.luna_ai.generate_response(content, user_id)
            luna_timestamp = now_for_db()  # Waktu Indonesia untuk Luna response
            luna_time_str = IndonesiaDatetime.format(luna_timestamp)
            
            print(f"Luna response timestamp: {luna_time_str}")
            
            # Simpan response Luna dengan timestamp Indonesia
            luna_message_data = {
                "conversation_id": conversation_id,
                "sender_id": None,
                "sender_type": "luna",
                "content": luna_response,
                "message_type": MessageType.TEXT.value,
                "status": "sent",
                "timestamp": luna_timestamp
            }
            
            luna_result = self.db.messages.insert_one(luna_message_data)
            luna_message_id = str(luna_result.inserted_id)
            
            # Create luna message object
            luna_message = Message(
                id=luna_message_id,
                conversation_id=conversation_id,
                sender_id=None,
                sender_type="luna",
                content=luna_response,
                message_type=MessageType.TEXT,
                status="sent",
                timestamp=luna_timestamp
            )
            
            # Update conversation dengan timestamp Indonesia
            await self._update_conversation_safe(conversation_id, content, user_id)
            
            print(f"✅ Messages sent successfully at {indonesia_time_str}")
            
            return {
                "user_message": user_message,
                "luna_response": luna_message,
                "conversation_updated": True
            }
            
        except Exception as e:
            print(f"❌ Error in send_message: {e}")
            raise e
    
    async def _update_conversation_safe(self, conversation_id: str, last_message: str, user_id: str):
        """Update conversation dengan timezone Indonesia"""
        try:
            current_conv = self.db.conversations.find_one({"_id": ObjectId(conversation_id)})
            if not current_conv:
                print(f"⚠️ Conversation {conversation_id} not found for update")
                return
            
            current_count = current_conv.get("message_count", 0)
            new_count = current_count + 2
            
            current_title = current_conv.get("title")
            new_title = current_title
            if not current_title and current_count == 0:
                new_title = last_message[:50] + "..." if len(last_message) > 50 else last_message
            
            # Menggunakan waktu Indonesia untuk update
            update_time = now_for_db()
            indonesia_time_str = IndonesiaDatetime.format(update_time)
            
            update_data = {
                "last_message": last_message,
                "last_message_at": update_time,
                "updated_at": update_time,
                "message_count": new_count,
                "status": ConversationStatus.ACTIVE.value
            }
            
            if new_title:
                update_data["title"] = new_title
            
            print(f"Updating conversation at Indonesia time: {indonesia_time_str}")
            
            result = self.db.conversations.update_one(
                {"_id": ObjectId(conversation_id)},
                {"$set": update_data}
            )
            
            print(f"✅ Conversation updated: matched={result.matched_count}, modified={result.modified_count}")
            
        except Exception as e:
            print(f"❌ Error updating conversation: {e}")
    
    async def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Mengambil percakapan berdasarkan ID"""
        try:
            doc = self.db.conversations.find_one({"_id": ObjectId(conversation_id)})
            if doc:
                # Ensure required fields
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
        """Menghapus percakapan (soft delete) dengan timestamp Indonesia"""
        try:
            update_data = {
                "status": ConversationStatus.DELETED.value,
                "updated_at": now_for_db()
            }
            
            result = self.db.conversations.update_one(
                {"_id": ObjectId(conversation_id), "user_id": user_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"❌ Error deleting conversation: {e}")
            return False
    
    async def search_conversations(self, user_id: str, query: str) -> List[Conversation]:
        """Mencari percakapan berdasarkan query"""
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
    
    async def fix_timezone_for_existing_data(self):
        """Fix timezone untuk data yang sudah ada - convert UTC to Indonesia time"""
        try:
            print("🕐 Fixing timezone for existing data...")
            
            # Fix conversations
            conversations = self.db.conversations.find({})
            conv_fixed = 0
            
            for conv in conversations:
                update_fields = {}
                
                # Convert UTC timestamps to Indonesia time if they exist
                for field in ["created_at", "updated_at", "last_message_at"]:
                    if field in conv and conv[field]:
                        utc_time = conv[field]
                        # Convert to Indonesia time then back to naive UTC for storage consistency
                        indonesia_time = IndonesiaDatetime.from_utc(utc_time)
                        # For display, we'll handle timezone conversion in the API response
                        # For now, keep as is but note the timezone
                        print(f"Conversation {conv['_id']} {field}: {IndonesiaDatetime.format(utc_time)} WIB")
                
                if update_fields:
                    self.db.conversations.update_one(
                        {"_id": conv["_id"]},
                        {"$set": update_fields}
                    )
                    conv_fixed += 1
            
            # Fix messages
            messages = self.db.messages.find({})
            msg_fixed = 0
            
            for msg in messages:
                if "timestamp" in msg and msg["timestamp"]:
                    utc_time = msg["timestamp"]
                    print(f"Message {msg['_id']} timestamp: {IndonesiaDatetime.format(utc_time)} WIB")
            
            print(f"✅ Timezone info logged for existing data")
            
        except Exception as e:
            print(f"❌ Error fixing timezone: {e}")
    
    async def get_chat_statistics(self, user_id: str) -> Dict[str, Any]:
        """Mendapatkan statistik chat dengan timezone Indonesia"""
        try:
            # Total conversations
            total_conversations = self.db.conversations.count_documents({
                "user_id": user_id,
                "$or": [
                    {"status": ConversationStatus.ACTIVE.value},
                    {"status": {"$exists": False}}
                ]
            })
            
            # Get conversation IDs
            user_conversations = self.db.conversations.find(
                {
                    "user_id": user_id,
                    "$or": [
                        {"status": ConversationStatus.ACTIVE.value},
                        {"status": {"$exists": False}}
                    ]
                },
                {"_id": 1}
            )
            conversation_ids = [str(conv["_id"]) for conv in user_conversations]
            
            # Total messages
            total_messages = self.db.messages.count_documents({
                "conversation_id": {"$in": conversation_ids}
            })
            
            # Today messages (Indonesia time)
            indonesia_now = IndonesiaDatetime.now()
            today_start = indonesia_now.replace(hour=0, minute=0, second=0, microsecond=0)
            # Convert to UTC for database query
            today_start_utc = IndonesiaDatetime.to_utc(today_start).replace(tzinfo=None)
            
            today_messages = self.db.messages.count_documents({
                "conversation_id": {"$in": conversation_ids},
                "timestamp": {"$gte": today_start_utc}
            })
            
            # Weekly messages
            from datetime import timedelta
            week_start = today_start - timedelta(days=7)
            week_start_utc = IndonesiaDatetime.to_utc(week_start).replace(tzinfo=None)
            
            weekly_messages = self.db.messages.count_documents({
                "conversation_id": {"$in": conversation_ids},
                "timestamp": {"$gte": week_start_utc}
            })
            
            # Last activity
            last_message = self.db.messages.find_one(
                {"conversation_id": {"$in": conversation_ids}},
                sort=[("timestamp", -1)]
            )
            last_activity = last_message.get("timestamp") if last_message else None
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "today_messages": today_messages,
                "weekly_messages": weekly_messages,
                "last_activity": last_activity,
                "timezone": "Asia/Jakarta (WIB/GMT+7)"
            }
        except Exception as e:
            print(f"Error getting chat statistics: {e}")
            return {
                "total_conversations": 0,
                "total_messages": 0,
                "today_messages": 0,
                "weekly_messages": 0,
                "last_activity": None,
                "timezone": "Asia/Jakarta (WIB/GMT+7)"
            }