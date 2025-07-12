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

    def generate_conversation_title(self, user_message: str, luna_response: str) -> str:
        """Generate judul percakapan dari pesan user dan Luna (maksimal 10 kata)"""
        
        # Prioritas keywords untuk judul
        priority_keywords = {
            'budget': 'Budget Planning',
            'anggaran': 'Perencanaan Anggaran',
            'tabungan': 'Tips Menabung',
            'investasi': 'Panduan Investasi',
            'pengeluaran': 'Analisis Pengeluaran',
            'pemasukan': 'Manajemen Pemasukan',
            'keuangan': 'Konsultasi Keuangan',
            'hutang': 'Strategi Hutang',
            'cicilan': 'Manajemen Cicilan',
            'gaji': 'Perencanaan Gaji'
        }
        
        # Cek kata kunci prioritas dalam pesan user
        user_lower = user_message.lower()
        for keyword, title in priority_keywords.items():
            if keyword in user_lower:
                return title
        
        # Jika tidak ada kata kunci finansial, ambil dari awal pesan user
        # Bersihkan dan ambil kata-kata penting
        words = re.findall(r'\b\w+\b', user_message)
        
        # Filter kata-kata yang tidak penting
        stop_words = {
            'saya', 'aku', 'anda', 'kamu', 'ini', 'itu', 'di', 'ke', 'dari', 'untuk',
            'dengan', 'pada', 'yang', 'adalah', 'akan', 'sudah', 'belum', 'tidak',
            'jangan', 'bisa', 'dapat', 'harus', 'ingin', 'mau', 'ada', 'dan', 'atau',
            'tapi', 'tetapi', 'kalau', 'jika', 'bila', 'ketika', 'saat', 'waktu'
        }
        
        important_words = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        
        # Ambil maksimal 10 kata pertama yang penting
        title_words = important_words[:10] if important_words else words[:10]
        
        # Gabungkan dan buat title
        title = ' '.join(title_words)
        
        # Kapitalisasi kata pertama
        if title:
            title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
        else:
            title = "Chat Keuangan"
        
        # Batasi panjang maksimal
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title

class ChatService:
    """Service untuk mengelola chat dan percakapan dengan timezone Indonesia yang benar"""
    
    def __init__(self):
        self.db = get_database()
        self.luna_ai = LunaAI()
    
    async def create_conversation(self, user_id: str) -> Conversation:
        """Membuat percakapan baru dengan timezone Indonesia yang benar"""
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
        """Mengambil daftar percakapan user dengan timezone yang benar"""
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
        """Mengambil pesan dalam percakapan dengan timezone yang benar"""
        try:
            print(f"Getting messages for conversation: {conversation_id}")
            
            cursor = self.db.messages.find(
                {"conversation_id": conversation_id}
            ).sort("timestamp", 1).limit(limit)
            
            messages = []
            for doc in cursor:
                # Ensure timestamp exists dengan timezone Indonesia
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
        """Mengirim pesan user dan generate response dari Luna dengan timezone Indonesia yang benar"""
        
        try:
            # Menggunakan waktu Indonesia yang benar
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
            
            # Update conversation dengan timestamp Indonesia dan generate title
            await self._update_conversation_safe(conversation_id, content, luna_response, user_id)
            
            print(f"✅ Messages sent successfully at {indonesia_time_str}")
            
            return {
                "user_message": user_message,
                "luna_response": luna_message,
                "conversation_updated": True
            }
            
        except Exception as e:
            print(f"❌ Error in send_message: {e}")
            raise e
    
    async def _update_conversation_safe(self, conversation_id: str, user_message: str, luna_response: str, user_id: str):
        """Update conversation dengan timezone Indonesia dan auto-generate title"""
        try:
            current_conv = self.db.conversations.find_one({"_id": ObjectId(conversation_id)})
            if not current_conv:
                print(f"⚠️ Conversation {conversation_id} not found for update")
                return
            
            current_count = current_conv.get("message_count", 0)
            new_count = current_count + 2  # User message + Luna response
            
            current_title = current_conv.get("title")
            new_title = current_title
            
            # Generate title untuk conversation baru (message_count == 0)
            if not current_title and current_count == 0:
                new_title = self.luna_ai.generate_conversation_title(user_message, luna_response)
                print(f"Generated conversation title: {new_title}")
            
            # Menggunakan waktu Indonesia untuk update
            update_time = now_for_db()
            indonesia_time_str = IndonesiaDatetime.format(update_time)
            
            update_data = {
                "last_message": user_message,  # Simpan pesan user sebagai last_message
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
    
    async def auto_delete_empty_conversations(self, user_id: str) -> int:
        """Auto-delete conversations yang tidak memiliki pesan (message_count = 0)"""
        try:
            print(f"🧹 Checking for empty conversations for user: {user_id}")
            
            # Cari conversations dengan message_count = 0 atau tidak ada pesan sama sekali
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
                
                # Double check: pastikan tidak ada pesan di messages collection
                message_count = self.db.messages.count_documents({
                    "conversation_id": conversation_id
                })
                
                if message_count == 0:
                    # Delete conversation yang benar-benar kosong
                    result = self.db.conversations.update_one(
                        {"_id": conv["_id"]},
                        {"$set": {
                            "status": ConversationStatus.DELETED.value,
                            "updated_at": now_for_db()
                        }}
                    )
                    
                    if result.modified_count > 0:
                        deleted_count += 1
                        created_time = IndonesiaDatetime.format(conv.get("created_at", now_for_db()))
                        print(f"🗑️ Deleted empty conversation {conversation_id} created at {created_time}")
            
            if deleted_count > 0:
                print(f"✅ Auto-deleted {deleted_count} empty conversations for user {user_id}")
            else:
                print(f"✅ No empty conversations found for user {user_id}")
            
            return deleted_count
            
        except Exception as e:
            print(f"❌ Error in auto_delete_empty_conversations: {e}")
            return 0
    
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
    
    async def cleanup_user_conversations(self, user_id: str) -> Dict[str, int]:
        """Comprehensive cleanup untuk user conversations"""
        try:
            print(f"🧹 Starting comprehensive cleanup for user: {user_id}")
            
            # 1. Auto-delete empty conversations
            empty_deleted = await self.auto_delete_empty_conversations(user_id)
            
            # 2. Update message counts untuk conversations yang ada
            conversations = self.db.conversations.find({
                "user_id": user_id,
                "status": {"$ne": ConversationStatus.DELETED.value}
            })
            
            updated_count = 0
            for conv in conversations:
                conversation_id = str(conv["_id"])
                
                # Hitung jumlah pesan yang sebenarnya
                actual_message_count = self.db.messages.count_documents({
                    "conversation_id": conversation_id
                })
                
                current_count = conv.get("message_count", 0)
                
                if actual_message_count != current_count:
                    update_data = {
                        "message_count": actual_message_count,
                        "updated_at": now_for_db()
                    }
                    
                    # Jika tidak ada pesan, hapus conversation
                    if actual_message_count == 0:
                        update_data["status"] = ConversationStatus.DELETED.value
                    else:
                        # Update last_message jika diperlukan
                        last_message = self.db.messages.find_one(
                            {"conversation_id": conversation_id},
                            sort=[("timestamp", -1)]
                        )
                        
                        if last_message:
                            update_data["last_message"] = last_message.get("content")
                            update_data["last_message_at"] = last_message.get("timestamp")
                    
                    result = self.db.conversations.update_one(
                        {"_id": conv["_id"]},
                        {"$set": update_data}
                    )
                    
                    if result.modified_count > 0:
                        updated_count += 1
            
            cleanup_stats = {
                "empty_conversations_deleted": empty_deleted,
                "conversations_updated": updated_count,
                "total_cleaned": empty_deleted + updated_count
            }
            
            print(f"✅ Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            print(f"❌ Error in cleanup_user_conversations: {e}")
            return {"empty_conversations_deleted": 0, "conversations_updated": 0, "total_cleaned": 0}
    
    async def get_chat_statistics(self, user_id: str) -> Dict[str, Any]:
        """Mendapatkan statistik chat dengan timezone Indonesia yang benar"""
        try:
            # Total conversations (active only)
            total_conversations = self.db.conversations.count_documents({
                "user_id": user_id,
                "status": {"$ne": ConversationStatus.DELETED.value}
            })
            
            # Get conversation IDs
            user_conversations = self.db.conversations.find(
                {
                    "user_id": user_id,
                    "status": {"$ne": ConversationStatus.DELETED.value}
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
            # Convert to UTC for database query (karena database menyimpan dalam UTC)
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
                "timezone": "Asia/Jakarta (WIB/GMT+7)",
                "current_time_wib": IndonesiaDatetime.format(indonesia_now)
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
                "current_time_wib": IndonesiaDatetime.format(IndonesiaDatetime.now())
            }