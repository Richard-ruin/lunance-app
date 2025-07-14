# app/services/luna_ai_core.py - Core Luna AI functionality
import re
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .enhanced_financial_parser import EnhancedFinancialParser
from .financial_categories import IndonesianStudentCategories

class LunaAICore:
    """Core Luna AI dengan kemampuan financial intelligence untuk mahasiswa Indonesia"""
    
    def __init__(self):
        self.db = get_database()
        self.parser = EnhancedFinancialParser()
        
        # Confirmation keywords
        self.confirmation_yes = [
            'ya', 'iya', 'yes', 'benar', 'betul', 'ok', 'oke', 'lanjut',
            'setuju', 'konfirmasi', 'simpan', 'save', 'correct', 'bener'
        ]
        
        self.confirmation_no = [
            'tidak', 'no', 'nope', 'batal', 'cancel', 'salah', 'gak',
            'enggak', 'batalkan', 'jangan', 'engga'
        ]
        
        # Responses untuk mahasiswa Indonesia
        self.greetings = [
            "Halo! Saya Luna, asisten keuangan khusus untuk anda. Ada yang bisa saya bantu hari ini?",
            "Hi! Luna di sini. Siap membantu Anda mengelola keuangan dengan lebih baik!",
            "Selamat datang! Saya Luna, mari kita atur keuangan Anda bersama-sama.",
            "Halo! Saya Luna, AI finansial yang paham betul kebutuhan mahasiswa Indonesia. Ada yang ingin dibahas?",
        ]
        
        self.financial_responses = [
            "Pertanyaan bagus tentang keuangan mahasiswa! Mari kita analisis bersama-sama.",
            "Untuk mengelola keuangan mahasiswa yang lebih baik, saya sarankan Anda mulai dengan budgeting uang saku bulanan.",
            "Berdasarkan data keuangan Anda, tips terbaik adalah sisihkan 20% uang saku untuk tabungan darurat.",
            "Saya bisa membantu Anda melacak pengeluaran harian dan memberikan insight keuangan yang berguna untuk mahasiswa.",
            "Mari kita buat rencana keuangan yang realistis sesuai kondisi mahasiswa Indonesia!",
        ]
        
        self.general_responses = [
            "Terima kasih atas pertanyaan Anda. Sebagai asisten keuangan mahasiswa, saya lebih fokus membantu masalah finansial.",
            "Saya di sini untuk membantu Anda dengan topik keuangan mahasiswa. Ada yang ingin dibahas tentang finansial?",
            "Mungkin saya bisa membantu lebih baik jika pertanyaannya terkait keuangan mahasiswa Indonesia?",
        ]
        
        # Tips khusus mahasiswa Indonesia
        self.student_tips = [
            "💡 Tips hemat mahasiswa: Masak sendiri bisa menghemat 40-60% pengeluaran makan bulanan.",
            "💰 Saran: Manfaatkan transportasi umum atau ojol sharing untuk menghemat ongkos harian.",
            "📊 Insight: Tracking pengeluaran jajan bisa menghemat Rp 200-500rb per bulan.",
            "🎯 Goal: Tetapkan target tabungan 15-20% dari uang saku bulanan untuk dana darurat.",
            "🏦 Tips: Pisahkan rekening untuk uang kuliah, uang jajan, dan tabungan.",
            "📱 Smart: Gunakan aplikasi mobile banking untuk monitoring pengeluaran real-time.",
            "🍜 Hemat: Cari tempat makan dengan harga mahasiswa atau beli bahan masak bareng teman kos.",
            "📚 Edu: Investasi untuk buku dan kursus online bisa jadi investasi terbaik mahasiswa.",
        ]
        
        # Response templates for financial queries
        self.financial_query_responses = {
            "total_tabungan": "📊 **Total Tabungan Anda**: {amount}\n\nIni termasuk tabungan awal + akumulasi pemasukan - pengeluaran. Tetap semangat menabung! 💪",
            "target_bulanan": "🎯 **Target Tabungan Bulan Ini**: {target}\n**Sudah Tercapai**: {achieved} ({percentage}%)\n\n{status_message}",
            "pengeluaran_terbesar": "💸 **Kategori Pengeluaran Terbesar**: {category}\n**Jumlah**: {amount}\n\n💡 Tips: {tip}",
            "progress_tabungan": "📈 **Progress Tabungan**: {items_progress}\n\nTerus semangat! Setiap rupiah yang ditabung adalah langkah menuju impian Anda! ✨",
        }
    
    def format_currency(self, amount: float) -> str:
        """Format jumlah uang ke format Rupiah"""
        return f"Rp {amount:,.0f}".replace(',', '.')
    
    def is_confirmation_message(self, message: str) -> Optional[bool]:
        """Cek apakah pesan adalah konfirmasi"""
        message_lower = message.lower().strip()
        
        if any(word in message_lower for word in self.confirmation_yes):
            return True
        elif any(word in message_lower for word in self.confirmation_no):
            return False
        
        return None
    
    def is_financial_query(self, message: str) -> Optional[str]:
        """Deteksi apakah pesan adalah pertanyaan tentang data keuangan"""
        message_lower = message.lower()
        
        query_patterns = {
            "total_tabungan": ["total tabungan", "berapa tabungan", "jumlah tabungan", "tabungan saya"],
            "target_bulanan": ["target bulan", "target bulanan", "progress bulan", "pencapaian bulan"],
            "pengeluaran_terbesar": ["pengeluaran terbesar", "habis buat apa", "keluar paling banyak", "spend terbanyak"],
            "progress_tabungan": ["progress tabungan", "kemajuan nabung", "target tabungan", "capaian target"],
            "ringkasan": ["ringkasan", "summary", "laporan", "rekapan", "overview"],
            "kategori": ["kategori", "jenis pengeluaran", "pembagian"],
        }
        
        for query_type, keywords in query_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return query_type
        
        return None
    
    def datetime_to_iso(self, dt: datetime) -> str:
        """Convert datetime to ISO string"""
        if dt is None:
            return None
        return dt.isoformat()
    
    def iso_to_datetime(self, iso_string: str) -> datetime:
        """Convert ISO string back to datetime"""
        try:
            return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        except:
            return now_for_db()
    
    def store_pending_data(self, user_id: str, conversation_id: str, message_id: str,
                          data_type: str, parsed_data: Dict[str, Any], 
                          original_message: str, confirmation_message: str) -> str:
        """Store pending financial data dengan serialization yang benar"""
        try:
            now = now_for_db()
            expires_at = now + timedelta(hours=24)
            
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
                "parsed_data": serialized_parsed_data,
                "original_message": original_message,
                "luna_response": confirmation_message,
                "is_confirmed": False,
                "expires_at": expires_at,
                "created_at": now
            }
            
            result = self.db.pending_financial_data.insert_one(pending_data)
            return str(result.inserted_id)
            
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
    
    async def generate_response(self, user_message: str, user_id: str, conversation_id: str, message_id: str) -> str:
        """Generate response dari Luna AI dengan financial intelligence"""
        message_lower = user_message.lower()
        print(f"🤖 Luna processing: '{user_message}'")
        
        # Check for confirmation first (untuk pending financial data)
        confirmation = self.is_confirmation_message(user_message)
        if confirmation is not None:
            print(f"📝 Confirmation detected: {confirmation}")
            return await self.handle_confirmation(user_id, conversation_id, confirmation)
        
        # Check if it's a financial query
        query_type = self.is_financial_query(user_message)
        if query_type:
            print(f"📊 Financial query detected: {query_type}")
            return await self.handle_financial_query(user_id, query_type)
        
        # Parse untuk data keuangan
        amount = self.parser.parse_amount(user_message)
        if amount:
            transaction_type = self.parser.detect_transaction_type(user_message)
            if transaction_type:
                print(f"💰 Financial data detected: {transaction_type}, amount: {amount}")
                return await self.handle_financial_data(
                    user_id, conversation_id, message_id,
                    transaction_type, amount, user_message
                )
        
        # Regular Luna responses
        print("💬 Regular message handling")
        return await self.handle_regular_message(user_message)
    
    async def handle_financial_query(self, user_id: str, query_type: str) -> str:
        """Handle pertanyaan tentang data keuangan user"""
        try:
            # Import finance service untuk mendapatkan data
            from .finance_service import FinanceService
            finance_service = FinanceService()
            
            if query_type == "total_tabungan":
                # Calculate total tabungan real-time
                dashboard = await finance_service.get_financial_dashboard(user_id)
                total_tabungan = dashboard["calculated_totals"]["actual_current_savings"]
                
                return self.financial_query_responses["total_tabungan"].format(
                    amount=self.format_currency(total_tabungan)
                )
            
            elif query_type == "target_bulanan":
                monthly_progress = await finance_service._calculate_monthly_savings_progress(user_id)
                percentage = monthly_progress["progress_percentage"]
                
                if percentage >= 100:
                    status_message = "🎉 Selamat! Target bulan ini sudah tercapai!"
                elif percentage >= 75:
                    status_message = "👍 Hampir sampai target! Sedikit lagi!"
                elif percentage >= 50:
                    status_message = "💪 Separuh jalan sudah ditempuh, tetap semangat!"
                else:
                    status_message = "🚀 Masih ada waktu, yuk lebih giat menabung!"
                
                return self.financial_query_responses["target_bulanan"].format(
                    target=self.format_currency(monthly_progress["monthly_target"]),
                    achieved=self.format_currency(monthly_progress["net_savings_this_month"]),
                    percentage=f"{percentage:.1f}",
                    status_message=status_message
                )
            
            elif query_type == "pengeluaran_terbesar":
                summary = await finance_service.get_financial_summary(user_id, "monthly")
                if summary.expense_categories:
                    top_category = max(summary.expense_categories.items(), key=lambda x: x[1])
                    category_name, amount = top_category
                    
                    # Get tip based on category
                    tips = {
                        "Makanan & Minuman": "Coba masak sendiri atau cari tempat makan dengan harga mahasiswa",
                        "Transportasi": "Gunakan transportasi umum atau sharing ojol dengan teman",
                        "Hiburan & Sosial": "Atur budget hiburan maksimal 10-15% dari uang saku",
                        "Internet & Komunikasi": "Manfaatkan WiFi kampus atau cari paket data yang lebih hemat"
                    }
                    tip = tips.get(category_name, "Coba evaluasi apakah pengeluaran ini benar-benar perlu")
                    
                    return self.financial_query_responses["pengeluaran_terbesar"].format(
                        category=category_name,
                        amount=self.format_currency(amount),
                        tip=tip
                    )
                else:
                    return "🤔 Belum ada data pengeluaran bulan ini. Yuk mulai catat pengeluaran harian Anda!"
            
            elif query_type == "progress_tabungan":
                goals = await finance_service.get_user_savings_goals(user_id, "active")
                if goals:
                    items_progress = []
                    for goal in goals[:3]:  # Show top 3
                        progress_bar = "🟩" * int(goal.progress_percentage // 10) + "⬜" * (10 - int(goal.progress_percentage // 10))
                        items_progress.append(
                            f"🛍️ **{goal.item_name}**: {progress_bar} {goal.progress_percentage:.1f}%\n"
                            f"   💰 {self.format_currency(goal.current_amount)} / {self.format_currency(goal.target_amount)}"
                        )
                    
                    return self.financial_query_responses["progress_tabungan"].format(
                        items_progress="\n\n".join(items_progress)
                    )
                else:
                    return "🎯 Belum ada target tabungan aktif. Yuk buat target pertama! Contoh: 'Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026'"
            
            else:
                return "📊 Fitur ini sedang dikembangkan. Sementara Anda bisa tanya tentang total tabungan, target bulanan, atau progress tabungan Anda."
        
        except Exception as e:
            print(f"❌ Error handling financial query: {e}")
            return "😅 Maaf, terjadi kesalahan saat mengambil data. Coba tanya lagi dalam beberapa saat ya!"
    
    async def handle_financial_data(self, user_id: str, conversation_id: str, message_id: str,
                                  transaction_type: str, amount: float, original_message: str) -> str:
        """Handle financial data yang di-parse dari pesan"""
        
        parse_result = self.parser.parse_financial_data(original_message)
        
        if not parse_result["is_financial_data"]:
            return await self.handle_regular_message(original_message)
        
        parsed_data = parse_result["parsed_data"]
        suggestions = parse_result.get("suggestions", [])
        
        if transaction_type in ["income", "expense"]:
            trans_type_id = "pemasukan" if transaction_type == "income" else "pengeluaran"
            
            confirmation_message = f"""💰 Saya mendeteksi data {trans_type_id}:

📋 **Detail Transaksi:**
• Jenis: {trans_type_id.title()}
• Jumlah: {self.format_currency(amount)}
• Kategori: {parsed_data['category']}
• Keterangan: {parsed_data['description']}
• Tanggal: {IndonesiaDatetime.format_date_only(parsed_data['date'])}

Apakah informasi ini sudah benar? Ketik **"ya"** untuk menyimpan atau **"tidak"** untuk membatalkan."""

            if suggestions:
                confirmation_message += f"\n\n💡 {suggestions[0]}"
            
            # Convert datetime to ISO string for storage
            storage_data = parsed_data.copy()
            storage_data["date"] = self.datetime_to_iso(parsed_data["date"])

        elif transaction_type == "savings_goal":
            target_date_str = ""
            if parsed_data.get("target_date"):
                target_date_str = f"• Target Waktu: {IndonesiaDatetime.format_date_only(parsed_data['target_date'])}\n"
            
            confirmation_message = f"""🎯 Saya mendeteksi target tabungan baru:

📋 **Detail Target Tabungan:**
• Barang yang ingin dibeli: {parsed_data['item_name']}
• Target jumlah: {self.format_currency(parsed_data['target_amount'])}
{target_date_str}• Keterangan: {parsed_data['description']}

Apakah informasi ini sudah benar? Ketik **"ya"** untuk menyimpan atau **"tidak"** untuk membatalkan."""

            if suggestions:
                confirmation_message += f"\n\n💡 {suggestions[0]}"
            
            # Convert datetime to ISO string for storage
            storage_data = parsed_data.copy()
            if parsed_data.get("target_date"):
                storage_data["target_date"] = self.datetime_to_iso(parsed_data["target_date"])

        # Store pending data
        pending_id = self.store_pending_data(
            user_id, conversation_id, message_id, transaction_type,
            storage_data, original_message, confirmation_message
        )
        
        return confirmation_message
    
    async def handle_confirmation(self, user_id: str, conversation_id: str, confirmed: bool) -> str:
        """Handle konfirmasi dari user untuk data keuangan"""
        print(f"🔄 Processing confirmation: {confirmed}")
        
        # Get latest pending data
        pending_data = self.get_latest_pending_data(user_id, conversation_id)
        
        if not pending_data:
            print("❌ No pending data found")
            return await self.handle_regular_message("ya" if confirmed else "tidak")
        
        if confirmed:
            return await self.confirm_financial_data(user_id, pending_data)
        else:
            return await self.cancel_financial_data(user_id, pending_data)
    
    async def confirm_financial_data(self, user_id: str, pending_data: dict) -> str:
        """Konfirmasi dan simpan data keuangan"""
        try:
            # Import finance service
            from .finance_service import FinanceService
            finance_service = FinanceService()
            
            pending_id = str(pending_data["_id"])
            result = finance_service.confirm_pending_data(pending_id, user_id, True)
            
            if result["success"]:
                data_type = result.get("type", pending_data["data_type"])
                
                if data_type == "transaction" or data_type in ["income", "expense"]:
                    created_data = result.get("data", {})
                    trans_type = "pemasukan" if created_data.get("type") == "income" else "pengeluaran"
                    
                    response = f"""✅ **{trans_type.title()} berhasil disimpan!**

💰 {self.format_currency(created_data.get('amount', 0))} - {created_data.get('category', '')}
📝 {created_data.get('description', '')}
📅 {IndonesiaDatetime.format_date_only(created_data.get('date', now_for_db()))}

Data keuangan Anda telah tersimpan. Anda bisa lihat ringkasan dengan bertanya "total tabungan saya" atau "ringkasan bulan ini"."""
                    
                elif data_type == "savings_goal":
                    created_data = result.get("data", {})
                    
                    response = f"""🎯 **Target tabungan berhasil dibuat!**

🛍️ **{created_data.get('item_name', 'Target baru')}**
💰 Target: {self.format_currency(created_data.get('target_amount', 0))}
📊 Progress: Rp 0 (0%)

Mulai menabung sekarang untuk mencapai target Anda! 💪"""
                
                # Add random student tip
                tip = random.choice(self.student_tips)
                response += f"\n\n{tip}"
                
                return response
            else:
                return f"⚠️ **Terjadi kesalahan:** {result.get('message', 'Tidak dapat menyimpan data')}"
        
        except Exception as e:
            print(f"❌ Error confirming financial data: {e}")
            return "😅 Maaf, terjadi kesalahan saat menyimpan data. Coba lagi ya!"
    
    async def cancel_financial_data(self, user_id: str, pending_data: dict) -> str:
        """Batalkan data keuangan"""
        try:
            # Import finance service
            from .finance_service import FinanceService
            finance_service = FinanceService()
            
            pending_id = str(pending_data["_id"])
            result = finance_service.confirm_pending_data(pending_id, user_id, False)
            
            if result["success"]:
                return "❌ **Data dibatalkan.**\n\nTidak masalah! Jika ada transaksi atau target tabungan lain yang ingin dicatat, silakan beritahu saya kapan saja."
            else:
                return f"⚠️ **Terjadi kesalahan:** {result.get('message', 'Tidak dapat membatalkan data')}"
        
        except Exception as e:
            print(f"❌ Error cancelling financial data: {e}")
            return "😅 Maaf, terjadi kesalahan. Coba lagi ya!"
    
    async def handle_regular_message(self, user_message: str) -> str:
        """Handle pesan regular (non-financial)"""
        message_lower = user_message.lower()
        
        # Greeting responses
        if any(word in message_lower for word in ['halo', 'hai', 'hi', 'hello', 'selamat']):
            return random.choice(self.greetings)
            
        # Thank you responses
        elif any(word in message_lower for word in ['terima kasih', 'thanks', 'makasih', 'thx']):
            return "Sama-sama! Senang bisa membantu Anda mengelola keuangan mahasiswa. Ada lagi yang ingin dibahas?"
            
        # Help requests
        elif any(word in message_lower for word in ['bantuan', 'help', 'tolong', 'gimana', 'bagaimana']):
            return """Tentu! Saya bisa membantu Anda dengan:

📊 **Mencatat Keuangan Mahasiswa:**
• Catat pemasukan: "Dapat uang saku 1 juta"
• Catat pengeluaran: "Bayar kos 500 ribu"
• Target tabungan: "Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026"

📈 **Tanya Data Keuangan:**
• "Total tabungan saya"
• "Target bulanan bulan ini"
• "Pengeluaran terbesar"
• "Progress tabungan"

💡 **Tips Keuangan Mahasiswa:**
• Tips menghemat uang saku
• Budgeting untuk mahasiswa
• Perencanaan keuangan
• Strategi menabung

Ada yang ingin dicoba sekarang?"""
            
        # Question about Luna
        elif any(word in message_lower for word in ['luna', 'kamu', 'anda', 'siapa']):
            return "Saya Luna, asisten AI yang dirancang khusus untuk membantu mahasiswa Indonesia mengelola keuangan. Saya paham betul tantangan keuangan mahasiswa dan bisa membantu Anda dengan budgeting, tips menghemat, tracking pengeluaran, dan mencatat transaksi yang otomatis tersimpan!"
            
        # Financial keyword responses
        elif any(keyword in message_lower for keyword in ['budget', 'anggaran', 'uang', 'keuangan', 'tabungan', 'hemat', 'mahasiswa']):
            response = random.choice(self.financial_responses)
            
            # Add specific tips based on keywords
            if any(word in message_lower for word in ['budget', 'anggaran']):
                response += "\n\n📋 **Tips Budget Mahasiswa:**\n• 50% untuk kebutuhan (makan, transport, kos)\n• 30% untuk keinginan (hiburan, jajan)\n• 20% untuk tabungan dan dana darurat"
            elif 'tabungan' in message_lower:
                response += "\n\n🏦 **Tips Menabung Mahasiswa:**\n• Sisihkan 15-20% uang saku untuk tabungan\n• Buat target tabungan yang spesifik\n• Gunakan rekening terpisah untuk tabungan"
            elif 'hemat' in message_lower:
                response += "\n\n💡 **Tips Hemat Mahasiswa:**\n• Masak sendiri atau makan bersama teman kos\n• Manfaatkan diskon dan promo mahasiswa\n• Gunakan transportasi umum\n• Beli buku bekas atau pinjam dari perpustakaan"
            
            # Add random student tip
            response += f"\n\n{random.choice(self.student_tips)}"
            return response
        
        # Default responses
        else:
            response = random.choice(self.general_responses)
            
            # Sometimes add a helpful tip
            if random.choice([True, False]):
                response += f"\n\n{random.choice(self.student_tips)}"
            
            return response
    
    def generate_conversation_title(self, user_message: str, luna_response: str) -> str:
        """Generate judul percakapan yang relevan"""
        
        # Priority keywords untuk judul
        priority_keywords = {
            'budget': 'Budget Mahasiswa',
            'anggaran': 'Perencanaan Anggaran',
            'tabungan': 'Tips Menabung',
            'hemat': 'Tips Hemat Mahasiswa',
            'uang saku': 'Manajemen Uang Saku',
            'pengeluaran': 'Tracking Pengeluaran',
            'pemasukan': 'Catat Pemasukan',
            'keuangan': 'Konsultasi Keuangan',
            'kos': 'Biaya Kos',
            'makan': 'Pengeluaran Makan',
            'transport': 'Biaya Transport',
            'nabung': 'Target Tabungan',
            'laptop': 'Tabungan Laptop',
            'hp': 'Tabungan HP',
            'motor': 'Tabungan Motor'
        }
        
        user_lower = user_message.lower()
        for keyword, title in priority_keywords.items():
            if keyword in user_lower:
                return title
        
        # Default title generation
        words = re.findall(r'\b\w+\b', user_message)
        stop_words = {
            'saya', 'aku', 'anda', 'kamu', 'ini', 'itu', 'di', 'ke', 'dari', 'untuk',
            'dengan', 'pada', 'yang', 'adalah', 'akan', 'sudah', 'belum', 'tidak', 'mau', 'ingin'
        }
        
        important_words = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        title_words = important_words[:4] if important_words else words[:4]
        title = ' '.join(title_words)
        
        if title:
            title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
        else:
            title = "Chat Keuangan"
        
        if len(title) > 40:
            title = title[:37] + "..."
        
        return title