import re
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..models.chat import Conversation, Message, MessageType, ConversationStatus
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db

class SimpleLunaAI:
    """Enhanced Luna AI with complete financial transaction creation"""
    
    def __init__(self):
        # Financial keywords untuk deteksi
        self.income_keywords = [
            'gaji', 'pendapatan', 'pemasukan', 'terima', 'bonus', 'komisi',
            'freelance', 'usaha', 'bisnis', 'investasi', 'bunga', 'dividen',
            'hadiah', 'dapat', 'penghasilan', 'income'
        ]
        
        self.expense_keywords = [
            'bayar', 'beli', 'belanja', 'buat', 'pengeluaran', 'keluar',
            'spend', 'biaya', 'ongkos', 'cicilan', 'tagihan', 'hutang',
            'kredit', 'pinjam', 'transfer', 'kirim', 'expense'
        ]
        
        self.savings_keywords = [
            'nabung', 'tabung', 'target', 'ingin beli', 'mau beli', 'pengen beli',
            'saving', 'goal', 'impian', 'rencana beli', 'kepengen'
        ]
        
        # Confirmation keywords
        self.confirmation_yes = [
            'ya', 'iya', 'yes', 'benar', 'betul', 'ok', 'oke', 'lanjut',
            'setuju', 'konfirmasi', 'simpan', 'save', 'correct'
        ]
        
        self.confirmation_no = [
            'tidak', 'no', 'nope', 'batal', 'cancel', 'salah', 'gak',
            'enggak', 'batalkan', 'jangan'
        ]
        
        # Regular responses
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
        
        # Database connection
        self.db = get_database()

    def format_currency(self, amount: float) -> str:
        """Format jumlah uang ke format Rupiah"""
        return f"Rp {amount:,.0f}".replace(',', '.')

    def parse_amount(self, text: str) -> Optional[float]:
        """Parse jumlah uang dari teks dengan pattern yang sederhana"""
        text_lower = text.lower()
        print(f"🔍 Parsing amount from: '{text}'")
        
        # Pattern untuk mendeteksi angka dengan unit
        patterns = [
            (r'(\d+(?:\.\d+)?)\s*juta', 1000000),
            (r'(\d+(?:\.\d+)?)\s*ribu', 1000),
            (r'(\d+(?:\.\d+)?)\s*rb', 1000),
            (r'(\d+(?:\.\d+)?)\s*jt', 1000000),
            (r'(\d+(?:\.\d+)?)', 1)  # plain number
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    amount = float(match.group(1)) * multiplier
                    print(f"✅ Amount detected: {amount}")
                    return amount
                except ValueError:
                    continue
        
        print("❌ No amount detected")
        return None

    def detect_transaction_type(self, text: str) -> Optional[str]:
        """Deteksi tipe transaksi dari teks"""
        text_lower = text.lower()
        print(f"🔍 Detecting transaction type from: '{text}'")
        
        # Check for savings goal keywords first
        savings_found = any(keyword in text_lower for keyword in self.savings_keywords)
        if savings_found:
            print("✅ Type detected: savings_goal")
            return "savings_goal"
        
        # Check for income keywords
        income_found = any(keyword in text_lower for keyword in self.income_keywords)
        
        # Check for expense keywords
        expense_found = any(keyword in text_lower for keyword in self.expense_keywords)
        
        print(f"Income keywords found: {income_found}")
        print(f"Expense keywords found: {expense_found}")
        
        if income_found and not expense_found:
            print("✅ Type detected: income")
            return "income"
        elif expense_found and not income_found:
            print("✅ Type detected: expense")
            return "expense"
        elif income_found and expense_found:
            # If both found, prioritize expense (more common in daily usage)
            print("✅ Type detected: expense (both found, prioritizing expense)")
            return "expense"
        
        print("❌ No transaction type detected")
        return None

    def extract_category(self, text: str, transaction_type: str) -> str:
        """Ekstrak kategori dari teks"""
        text_lower = text.lower()
        
        if transaction_type == "income":
            if 'gaji' in text_lower:
                return 'gaji'
            elif any(word in text_lower for word in ['freelance', 'kontrak']):
                return 'freelance'
            elif any(word in text_lower for word in ['bisnis', 'usaha', 'dagang']):
                return 'bisnis'
            elif any(word in text_lower for word in ['bonus', 'komisi']):
                return 'bonus'
            else:
                return 'lainnya'
        else:  # expense
            if any(word in text_lower for word in ['makan', 'restoran', 'food']):
                return 'makanan'
            elif any(word in text_lower for word in ['transport', 'bensin', 'ojek']):
                return 'transportasi'
            elif any(word in text_lower for word in ['listrik', 'air', 'internet', 'telepon', 'tagihan']):
                return 'tagihan'
            elif any(word in text_lower for word in ['belanja', 'shopping', 'beli']):
                return 'belanja'
            elif any(word in text_lower for word in ['hiburan', 'cinema', 'game']):
                return 'hiburan'
            else:
                return 'lainnya'

    def is_confirmation_message(self, message: str) -> Optional[bool]:
        """Cek apakah pesan adalah konfirmasi (True) atau penolakan (False)"""
        message_lower = message.lower().strip()
        
        if any(word in message_lower for word in self.confirmation_yes):
            return True
        elif any(word in message_lower for word in self.confirmation_no):
            return False
        
        return None

    def datetime_to_iso(self, dt: datetime) -> str:
        """Convert datetime to ISO string for JSON serialization"""
        if dt is None:
            return None
        return dt.isoformat()

    def iso_to_datetime(self, iso_string: str) -> datetime:
        """Convert ISO string back to datetime"""
        try:
            return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        except:
            return now_for_db()

    def create_actual_transaction(self, user_id: str, parsed_data: Dict[str, Any], 
                                chat_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create actual transaction in transactions collection"""
        try:
            now = now_for_db()
            
            # Parse date from string if it's a string
            transaction_date = parsed_data.get('date')
            if isinstance(transaction_date, str):
                transaction_date = self.iso_to_datetime(transaction_date)
            elif transaction_date is None:
                transaction_date = now
            
            # Create transaction document
            transaction_data = {
                "user_id": user_id,
                "type": parsed_data["type"],
                "amount": parsed_data["amount"],
                "category": parsed_data["category"],
                "description": parsed_data["description"],
                "date": transaction_date,
                "status": "confirmed",  # Auto-confirm dari chat
                "source": "chat",
                "tags": [],
                "notes": f"Dibuat melalui chat Luna AI",
                "chat_message_id": chat_context.get("message_id"),
                "conversation_id": chat_context.get("conversation_id"),
                "created_at": now,
                "updated_at": now,
                "confirmed_at": now
            }
            
            # Insert to transactions collection
            result = self.db.transactions.insert_one(transaction_data)
            transaction_id = str(result.inserted_id)
            
            print(f"✅ Transaction created with ID: {transaction_id}")
            
            # Return transaction info
            return {
                "success": True,
                "transaction_id": transaction_id,
                "data": transaction_data
            }
            
        except Exception as e:
            print(f"❌ Error creating transaction: {e}")
            return {"success": False, "error": str(e)}

    def create_actual_savings_goal(self, user_id: str, parsed_data: Dict[str, Any],
                                 chat_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create actual savings goal in savings_goals collection"""
        try:
            now = now_for_db()
            
            # Create savings goal document
            goal_data = {
                "user_id": user_id,
                "item_name": parsed_data["item_name"],
                "target_amount": parsed_data["target_amount"],
                "current_amount": 0.0,
                "description": parsed_data.get("description", ""),
                "target_date": None,  # Can be set later
                "status": "active",
                "monthly_target": None,  # Can be calculated later
                "source": "chat",
                "tags": [],
                "notes": f"Dibuat melalui chat Luna AI",
                "chat_message_id": chat_context.get("message_id"),
                "conversation_id": chat_context.get("conversation_id"),
                "created_at": now,
                "updated_at": now
            }
            
            # Insert to savings_goals collection
            result = self.db.savings_goals.insert_one(goal_data)
            goal_id = str(result.inserted_id)
            
            print(f"✅ Savings goal created with ID: {goal_id}")
            
            # Return goal info
            return {
                "success": True,
                "goal_id": goal_id,
                "data": goal_data
            }
            
        except Exception as e:
            print(f"❌ Error creating savings goal: {e}")
            return {"success": False, "error": str(e)}

    def store_pending_data(self, user_id: str, conversation_id: str, message_id: str,
                          data_type: str, parsed_data: Dict[str, Any], 
                          original_message: str, confirmation_message: str) -> str:
        """Store pending financial data to database with proper serialization"""
        try:
            now = now_for_db()
            expires_at = now + timedelta(hours=24)  # Expired dalam 24 jam
            
            # Serialize datetime objects in parsed_data
            serialized_parsed_data = {}
            for key, value in parsed_data.items():
                if isinstance(value, datetime):
                    serialized_parsed_data[key] = self.datetime_to_iso(value)
                else:
                    serialized_parsed_data[key] = value
            
            pending_data = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "chat_message_id": message_id,
                "data_type": data_type,
                "parsed_data": serialized_parsed_data,  # Use serialized data
                "original_message": original_message,
                "luna_response": confirmation_message,
                "is_confirmed": False,
                "expires_at": expires_at,
                "created_at": now
            }
            
            result = self.db.pending_financial_data.insert_one(pending_data)
            pending_id = str(result.inserted_id)
            print(f"✅ Pending data stored with ID: {pending_id}")
            return pending_id
            
        except Exception as e:
            print(f"❌ Error storing pending data: {e}")
            return None

    def get_latest_pending_data(self, user_id: str, conversation_id: str):
        """Get latest pending data for user in conversation"""
        try:
            result = self.db.pending_financial_data.find_one(
                {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "is_confirmed": False
                },
                sort=[("created_at", -1)]
            )
            return result
        except Exception as e:
            print(f"❌ Error getting pending data: {e}")
            return None

    def confirm_pending_data(self, pending_id: str, user_id: str, confirmed: bool) -> Dict[str, Any]:
        """Confirm or cancel pending financial data and create actual records"""
        try:
            # Get the pending data first
            pending_doc = self.db.pending_financial_data.find_one(
                {"_id": ObjectId(pending_id), "user_id": user_id, "is_confirmed": False}
            )
            
            if not pending_doc:
                return {"success": False, "message": "Pending data not found"}
            
            if confirmed:
                # Mark as confirmed first
                now = now_for_db()
                self.db.pending_financial_data.update_one(
                    {"_id": ObjectId(pending_id)},
                    {"$set": {
                        "is_confirmed": True,
                        "confirmed_at": now
                    }}
                )
                
                # Create actual transaction/savings goal
                chat_context = {
                    "message_id": pending_doc["chat_message_id"],
                    "conversation_id": pending_doc["conversation_id"]
                }
                
                if pending_doc["data_type"] == "transaction" or pending_doc["data_type"] in ["income", "expense"]:
                    # Create actual transaction
                    result = self.create_actual_transaction(
                        user_id, 
                        pending_doc["parsed_data"], 
                        chat_context
                    )
                    
                    if result["success"]:
                        return {
                            "success": True,
                            "message": "Transaction created successfully",
                            "transaction_id": result["transaction_id"],
                            "data": result["data"],
                            "type": "transaction"
                        }
                    else:
                        return {"success": False, "message": f"Failed to create transaction: {result.get('error')}"}
                        
                elif pending_doc["data_type"] == "savings_goal":
                    # Create actual savings goal
                    result = self.create_actual_savings_goal(
                        user_id,
                        pending_doc["parsed_data"],
                        chat_context
                    )
                    
                    if result["success"]:
                        return {
                            "success": True,
                            "message": "Savings goal created successfully", 
                            "goal_id": result["goal_id"],
                            "data": result["data"],
                            "type": "savings_goal"
                        }
                    else:
                        return {"success": False, "message": f"Failed to create savings goal: {result.get('error')}"}
                
                return {"success": True, "message": "Data confirmed but no action taken"}
                
            else:
                # Delete the pending data
                result = self.db.pending_financial_data.delete_one(
                    {"_id": ObjectId(pending_id), "user_id": user_id}
                )
                
                if result.deleted_count > 0:
                    return {"success": True, "message": "Data cancelled"}
                else:
                    return {"success": False, "message": "Data not found"}
                    
        except Exception as e:
            print(f"❌ Error confirming pending data: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

    async def generate_response(self, user_message: str, user_id: str, conversation_id: str, message_id: str) -> str:
        """Generate response dari Luna AI dengan financial parsing capability"""
        message_lower = user_message.lower()
        print(f"🤖 Luna processing: '{user_message}'")
        
        # Check for confirmation first (untuk pending financial data)
        confirmation = self.is_confirmation_message(user_message)
        if confirmation is not None:
            print(f"📝 Confirmation detected: {confirmation}")
            return await self.handle_confirmation(user_id, conversation_id, confirmation)
        
        # Parse untuk data keuangan
        amount = self.parse_amount(user_message)
        if amount:
            transaction_type = self.detect_transaction_type(user_message)
            if transaction_type:
                print(f"💰 Financial data detected: {transaction_type}, amount: {amount}")
                return await self.handle_financial_data(
                    user_id, conversation_id, message_id,
                    transaction_type, amount, user_message
                )
        
        # Regular Luna responses
        print("💬 Regular message handling")
        return await self.handle_regular_message(user_message)

    async def handle_financial_data(self, user_id: str, conversation_id: str, message_id: str,
                                  transaction_type: str, amount: float, original_message: str) -> str:
        """Handle financial data yang di-parse dari pesan"""
        
        if transaction_type in ["income", "expense"]:
            category = self.extract_category(original_message, transaction_type)
            trans_type_id = "pemasukan" if transaction_type == "income" else "pengeluaran"
            
            confirmation_message = f"""💰 Saya mendeteksi data {trans_type_id}:

📋 **Detail Transaksi:**
• Jenis: {trans_type_id.title()}
• Jumlah: {self.format_currency(amount)}
• Kategori: {category.title()}
• Keterangan: {original_message}
• Tanggal: {IndonesiaDatetime.format_date_only(now_for_db())}

Apakah informasi ini sudah benar? Ketik **"ya"** untuk menyimpan atau **"tidak"** untuk membatalkan."""

            # Create parsed_data with properly serializable data
            parsed_data = {
                "type": transaction_type,
                "amount": amount,
                "category": category,
                "description": original_message,
                "date": self.datetime_to_iso(now_for_db())  # Convert to ISO string
            }

        elif transaction_type == "savings_goal":
            # Extract item name from original message
            item_name = original_message.replace(str(int(amount)), "").replace("juta", "").replace("ribu", "").strip()
            if not item_name or len(item_name) < 3:
                item_name = "Target tabungan"
            
            confirmation_message = f"""🎯 Saya mendeteksi target tabungan baru:

📋 **Detail Target Tabungan:**
• Barang yang ingin dibeli: {item_name}
• Target jumlah: {self.format_currency(amount)}
• Keterangan: {original_message}

Apakah informasi ini sudah benar? Ketik **"ya"** untuk menyimpan atau **"tidak"** untuk membatalkan."""

            # Create parsed_data with properly serializable data
            parsed_data = {
                "item_name": item_name,
                "target_amount": amount,
                "description": original_message
            }

        # Store pending data
        pending_id = self.store_pending_data(
            user_id, conversation_id, message_id, transaction_type,
            parsed_data, original_message, confirmation_message
        )
        
        return confirmation_message

    async def handle_confirmation(self, user_id: str, conversation_id: str, confirmed: bool) -> str:
        """Handle konfirmasi dari user untuk data keuangan"""
        print(f"🔄 Processing confirmation: {confirmed}")
        
        # Get latest pending data for this conversation
        pending_data = self.get_latest_pending_data(user_id, conversation_id)
        
        if not pending_data:
            print("❌ No pending data found")
            return await self.handle_regular_message("ya" if confirmed else "tidak")
        
        pending_id = str(pending_data["_id"])
        result = self.confirm_pending_data(pending_id, user_id, confirmed)
        
        if confirmed and result["success"]:
            data_type = result.get("type", pending_data["data_type"])
            
            if data_type == "transaction" or data_type in ["income", "expense"]:
                # Get the created transaction data
                created_data = result.get("data", {})
                trans_type = "pemasukan" if created_data.get("type") == "income" else "pengeluaran"
                
                response = f"""✅ **{trans_type.title()} berhasil disimpan!**

💰 {self.format_currency(created_data.get('amount', 0))} - {created_data.get('category', '').title()}
📝 {created_data.get('description', '')}
📅 {IndonesiaDatetime.format_date_only(created_data.get('date', now_for_db()))}

💾 **ID Transaksi:** {result.get('transaction_id', 'N/A')}

Data keuangan Anda telah tersimpan di database. Anda bisa melihat riwayat transaksi di menu Explore Finance. Ada transaksi lain yang ingin dicatat?"""
                
            elif data_type == "savings_goal":
                # Get the created goal data  
                created_data = result.get("data", {})
                
                response = f"""🎯 **Target tabungan berhasil dibuat!**

🛍️ **{created_data.get('item_name', 'Target baru')}**
💰 Target: {self.format_currency(created_data.get('target_amount', 0))}
📊 Progress: Rp 0 (0%)

💾 **ID Target:** {result.get('goal_id', 'N/A')}

Target tabungan Anda telah tersimpan di database. Mulai menabung sekarang untuk mencapai target Anda! 💪"""
            
            # Add random tip
            tip = random.choice(self.expense_tips)
            response += f"\n\n{tip}"
            
        elif not confirmed and result["success"]:
            response = "❌ **Data dibatalkan.**\n\nTidak masalah! Jika ada transaksi atau target tabungan lain yang ingin dicatat, silakan beritahu saya kapan saja."
            
        else:
            response = f"⚠️ **Terjadi kesalahan:** {result.get('message', 'Tidak dapat memproses konfirmasi')}"
        
        return response

    async def handle_regular_message(self, user_message: str) -> str:
        """Handle pesan regular (non-financial)"""
        message_lower = user_message.lower()
        
        # Greeting responses
        if any(word in message_lower for word in ['halo', 'hai', 'hi', 'hello', 'selamat']):
            return random.choice(self.greetings)
            
        # Thank you responses
        elif any(word in message_lower for word in ['terima kasih', 'thanks', 'makasih']):
            return "Sama-sama! Senang bisa membantu Anda. Ada lagi yang ingin dibahas tentang keuangan?"
            
        # Help requests
        elif any(word in message_lower for word in ['bantuan', 'help', 'tolong', 'gimana', 'bagaimana']):
            return """Tentu! Saya bisa membantu Anda dengan:

📊 **Mencatat Keuangan:**
• Catat pemasukan: "Dapat gaji 5 juta"
• Catat pengeluaran: "Bayar listrik 200 ribu"
• Target tabungan: "Mau nabung buat beli laptop 10 juta"

💡 **Analisis & Tips:**
• Tips menghemat uang
• Membuat budget
• Perencanaan keuangan
• Saran investasi dasar

✨ **Fitur Baru:**
• Data otomatis tersimpan ke database
• Lihat riwayat di menu Explore Finance
• Tracking progress target tabungan

Ada yang ingin dicoba sekarang?"""
            
        # Question about Luna
        elif any(word in message_lower for word in ['luna', 'kamu', 'anda', 'siapa']):
            return "Saya Luna, asisten AI yang dirancang khusus untuk membantu mengelola keuangan pribadi. Saya bisa membantu Anda dengan budgeting, tips menghemat, analisis keuangan, dan mencatat transaksi yang otomatis tersimpan ke database!"
            
        # Financial keyword responses
        elif any(keyword in message_lower for keyword in ['budget', 'anggaran', 'uang', 'keuangan', 'tabungan', 'investasi', 'pengeluaran', 'pemasukan']):
            response = random.choice(self.financial_responses)
            
            # Add specific tips
            if 'budget' in message_lower or 'anggaran' in message_lower:
                response += "\n\n📋 Untuk membuat budget yang efektif:\n1. Catat semua pemasukan\n2. List semua pengeluaran wajib\n3. Alokasikan untuk tabungan\n4. Sisanya untuk pengeluaran fleksibel"
            elif 'tabungan' in message_lower:
                response += "\n\n🏦 Tips menabung:\n• Otomatis transfer ke rekening tabungan\n• Mulai dari jumlah kecil tapi konsisten\n• Pisahkan rekening tabungan dengan pengeluaran"
            
            # Add random tip
            if random.choice([True, False]):
                response += f"\n\n{random.choice(self.expense_tips)}"
                
            return response
        
        # Default responses
        else:
            return random.choice(self.general_responses)

    def generate_conversation_title(self, user_message: str, luna_response: str) -> str:
        """Generate judul percakapan"""
        
        # Prioritas keywords untuk judul
        priority_keywords = {
            'budget': 'Budget Planning',
            'anggaran': 'Perencanaan Anggaran',
            'tabungan': 'Tips Menabung',
            'investasi': 'Panduan Investasi',
            'pengeluaran': 'Pencatatan Pengeluaran',
            'pemasukan': 'Pencatatan Pemasukan',
            'keuangan': 'Konsultasi Keuangan',
            'gaji': 'Pencatatan Gaji',
            'bayar': 'Pencatatan Pembayaran',
            'dapat': 'Pencatatan Pemasukan',
            'beli': 'Pencatatan Belanja',
            'nabung': 'Target Tabungan'
        }
        
        user_lower = user_message.lower()
        for keyword, title in priority_keywords.items():
            if keyword in user_lower:
                return title
        
        # Default title generation
        words = re.findall(r'\b\w+\b', user_message)
        stop_words = {
            'saya', 'aku', 'anda', 'kamu', 'ini', 'itu', 'di', 'ke', 'dari', 'untuk',
            'dengan', 'pada', 'yang', 'adalah', 'akan', 'sudah', 'belum', 'tidak'
        }
        
        important_words = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        title_words = important_words[:6] if important_words else words[:6]
        title = ' '.join(title_words)
        
        if title:
            title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
        else:
            title = "Chat Keuangan"
        
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title

class ChatService:
    """Enhanced Chat Service dengan complete financial integration"""
    
    def __init__(self):
        self.db = get_database()
        self.luna_ai = SimpleLunaAI()
    
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
        """Send message dengan enhanced Luna AI and complete financial integration"""
        
        try:
            now = now_for_db()
            print(f"📨 Processing message: '{content}'")
            
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
            
            # Generate Luna response
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
            
            return {
                "user_message": user_message,
                "luna_response": luna_message,
                "conversation_updated": True
            }
            
        except Exception as e:
            print(f"❌ Error in send_message: {e}")
            raise e
    
    async def _update_conversation_safe(self, conversation_id: str, user_message: str, luna_response: str, user_id: str):
        """Update conversation"""
        try:
            current_conv = self.db.conversations.find_one({"_id": ObjectId(conversation_id)})
            if not current_conv:
                return
            
            current_count = current_conv.get("message_count", 0)
            new_count = current_count + 2
            
            current_title = current_conv.get("title")
            new_title = current_title
            
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
    
    # Include other required methods (same as before)
    async def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
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
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "today_messages": 0,
                "weekly_messages": 0,
                "last_activity": None,
                "timezone": "Asia/Jakarta (WIB/GMT+7)",
                "current_time_wib": IndonesiaDatetime.format(IndonesiaDatetime.now())
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