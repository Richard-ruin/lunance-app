# app/services/luna_ai_core.py - ENHANCED dengan Single Field Update
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
        
        # ===========================================
        # ENHANCED: Update & Delete Keywords
        # ===========================================
        self.update_keywords = [
            'ubah', 'ganti', 'edit', 'update', 'revisi', 'perbaiki',
            'modifikasi', 'change', 'modify', 'adjust', 'koreksi'
        ]
        
        self.delete_keywords = [
            'hapus', 'delete', 'remove', 'buang', 'hilangkan', 'batalkan',
            'cancel', 'drop', 'destroy', 'eliminate'
        ]
        
        self.target_keywords = [
            'target', 'tabungan', 'goal', 'nabung', 'saving'
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
            "list_targets": "🎯 **Target Tabungan Anda**:\n{targets_list}\n\nUntuk mengubah target, ketik: *\"ubah target [nama barang]\"*\nUntuk menghapus target, ketik: *\"hapus target [nama barang]\"*",
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
    
    # ===========================================
    # ENHANCED: Update & Delete Detection Methods
    # ===========================================
    
    def determine_update_type(self, message_lower: str) -> str:
        """Determine jenis update berdasarkan keywords"""
        if any(indicator in message_lower for indicator in ['tanggal', 'waktu', 'deadline', 'kapan', 'bulan', 'tahun']):
            return "date"
        elif any(indicator in message_lower for indicator in ['jadi', 'menjadi', 'harga', 'ribu', 'juta', 'rb', 'jt', 'rp']):
            return "price"  
        elif any(indicator in message_lower for indicator in ['ganti nama', 'ubah nama', 'nama jadi', 'namanya']):
            return "name"
        else:
            return "unknown"
    
    def clean_item_name_for_update(self, name: str) -> str:
        """Clean item name untuk update (remove price/date artifacts)"""
        clean_name = name
        
        # Remove price indicators
        clean_name = re.sub(r'\d+\s*(juta|ribu|rb|jt|m|k)', '', clean_name, flags=re.IGNORECASE)
        
        # Remove date indicators  
        clean_name = re.sub(r'\d+\s*(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)', '', clean_name, flags=re.IGNORECASE)
        clean_name = re.sub(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', '', clean_name)
        
        # Remove time-related words
        time_words = ['tanggal', 'pada', 'waktu', 'deadline', 'bulan', 'tahun']
        for word in time_words:
            clean_name = re.sub(rf'\b{word}\b', '', clean_name, flags=re.IGNORECASE)
        
        # Clean up spaces
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()
        
        return clean_name
    
    def parse_price_for_update(self, message_lower: str) -> Optional[float]:
        """
        ENHANCED: Parse harga khusus untuk update dengan filter tanggal yang lebih kuat
        """
        # 1. Hilangkan bagian tanggal dari message dulu
        message_without_dates = message_lower
        
        # Remove common date patterns to avoid confusion
        date_removal_patterns = [
            r'\d{1,2}\s+(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)\s+\d{4}',
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',
            r'tanggal\s+\d{1,2}',
            r'pada\s+\d{1,2}',
            r'bulan\s+\w+',
            r'tahun\s+\d{4}'
        ]
        
        for pattern in date_removal_patterns:
            message_without_dates = re.sub(pattern, '', message_without_dates, flags=re.IGNORECASE)
        
        print(f"🧹 Cleaned message: '{message_without_dates}' (from: '{message_lower}')")
        
        # 2. Parse amount dari message yang sudah dibersihkan dari tanggal
        amount = self.parser.parse_amount(message_without_dates)
        print(f"💰 Parsed amount: {amount}")
        
        return amount
    
    def extract_update_fields(self, message_lower: str) -> Dict[str, Any]:
        """
        FIXED: Extract field yang akan diupdate dengan prioritas yang jelas
        ATURAN: Hanya 1 field per pesan untuk menghindari konflik parsing
        """
        update_fields = {}
        original_message = message_lower
        
        print(f"🔍 Analyzing update command: '{original_message}'")
        
        # 1. PRIORITAS TERTINGGI: Cek apakah ini update TANGGAL
        # Pattern yang menunjukkan update tanggal/waktu
        date_update_indicators = [
            'tanggal', 'waktu', 'deadline', 'target waktu', 'kapan', 'bulan', 'tahun'
        ]
        
        is_date_update = any(indicator in message_lower for indicator in date_update_indicators)
        
        # 2. Jika ini adalah update tanggal, HANYA parse tanggal
        if is_date_update:
            print(f"🗓️ Detected DATE update command: {original_message}")
            
            target_date = self.parser.parse_target_date(message_lower)
            if target_date:
                update_fields["target_date"] = target_date
                print(f"✅ Parsed target_date: {target_date}")
                return update_fields  # RETURN langsung, jangan parse yang lain
            else:
                print("❌ Failed to parse target_date")
                return update_fields
        
        # 3. PRIORITAS KEDUA: Cek apakah ini update HARGA
        # Pattern yang menunjukkan update harga
        price_update_indicators = [
            'jadi', 'menjadi', 'ganti harga', 'ubah harga', 'harga jadi', 
            'ribu', 'juta', 'rb', 'jt', 'rp', 'rupiah'
        ]
        
        is_price_update = any(indicator in message_lower for indicator in price_update_indicators)
        
        # 4. Jika ini adalah update harga, HANYA parse harga
        if is_price_update and not is_date_update:  # Pastikan bukan date update
            print(f"💰 Detected PRICE update command: {original_message}")
            
            # Parse harga dengan context yang lebih spesifik
            amount = self.parse_price_for_update(message_lower)
            if amount:
                update_fields["target_amount"] = amount
                print(f"✅ Parsed target_amount: {amount}")
                return update_fields  # RETURN langsung, jangan parse yang lain
            else:
                print("❌ Failed to parse target_amount")
        
        # 5. PRIORITAS KETIGA: Cek apakah ini update NAMA
        name_update_indicators = [
            'ganti nama', 'ubah nama', 'nama jadi', 'namanya', 'rename'
        ]
        
        is_name_update = any(indicator in message_lower for indicator in name_update_indicators)
        
        # 6. Jika ini adalah update nama, HANYA parse nama
        if is_name_update:
            print(f"📝 Detected NAME update command: {original_message}")
            
            # Extract new name after "jadi" or similar
            name_patterns = [
                r'(?:nama\s+)?(?:jadi|menjadi|ke)\s+(.+?)(?:\s+(?:tanggal|pada|waktu|deadline)|\s*$)',
                r'(?:ganti|ubah)\s+nama\s+(?:jadi|menjadi|ke)?\s*(.+?)(?:\s+(?:tanggal|pada|waktu|deadline)|\s*$)'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    new_name = match.group(1).strip()
                    # Clean up the name - remove price/date info if accidentally included
                    new_name = self.clean_item_name_for_update(new_name)
                    if new_name and len(new_name) > 2:
                        update_fields["item_name"] = new_name
                        print(f"✅ Parsed item_name: {new_name}")
                        return update_fields
                    break
        
        # 7. FALLBACK: Jika tidak ada indicator yang jelas, coba deteksi otomatis
        # Tapi tetap hanya ambil 1 field dengan prioritas: Date > Price > Name
        
        print("🔄 Trying fallback detection...")
        
        # Coba tanggal dulu
        target_date = self.parser.parse_target_date(message_lower)
        if target_date:
            update_fields["target_date"] = target_date
            print(f"🔄 Fallback parsed target_date: {target_date}")
            return update_fields
        
        # Lalu coba harga
        amount = self.parse_price_for_update(message_lower)
        if amount:
            update_fields["target_amount"] = amount
            print(f"🔄 Fallback parsed target_amount: {amount}")
            return update_fields
        
        print(f"❌ No update fields detected in: {original_message}")
        return update_fields
    
    def is_update_delete_command(self, message: str) -> Optional[Dict[str, Any]]:
        """
        ENHANCED: Deteksi perintah update/delete dengan klasifikasi yang lebih baik
        """
        message_lower = message.lower().strip()
        
        # Check for update commands
        has_update = any(word in message_lower for word in self.update_keywords)
        has_delete = any(word in message_lower for word in self.delete_keywords)
        has_target = any(word in message_lower for word in self.target_keywords)
        
        if (has_update or has_delete) and has_target:
            # Extract item name from message
            item_name = self.extract_item_name_from_command(message_lower)
            
            if has_update:
                # Determine update type for better UX
                update_type = self.determine_update_type(message_lower)
                
                # Check what fields to update (HANYA 1 field)
                update_fields = self.extract_update_fields(message_lower)
                
                return {
                    "action": "update",
                    "update_type": update_type,  # "date", "price", "name", or "unknown"
                    "item_name": item_name,
                    "update_fields": update_fields,
                    "original_message": message
                }
            elif has_delete:
                return {
                    "action": "delete",
                    "item_name": item_name,
                    "original_message": message
                }
        
        # Special command to list all targets
        if any(phrase in message_lower for phrase in ["daftar target", "list target", "target saya", "semua target"]):
            return {
                "action": "list",
                "original_message": message
            }
        
        return None
    
    def extract_item_name_from_command(self, message_lower: str) -> str:
        """Extract nama barang dari perintah update/delete"""
        # Remove action words
        clean_message = message_lower
        
        # Remove update/delete keywords
        for word in self.update_keywords + self.delete_keywords + self.target_keywords:
            clean_message = re.sub(rf'\b{word}\b', '', clean_message, flags=re.IGNORECASE)
        
        # Remove common connecting words
        remove_words = ['untuk', 'buat', 'pada', 'tanggal', 'dalam', 'mau', 'ingin', 'pengen', 'jadi', 'menjadi']
        for word in remove_words:
            clean_message = re.sub(rf'\b{word}\b', '', clean_message, flags=re.IGNORECASE)
        
        # Clean up and return
        clean_message = re.sub(r'\s+', ' ', clean_message).strip()
        return clean_message if clean_message else "target"
    
    # ===========================================
    # Enhanced Financial Query Detection
    # ===========================================
    
    def is_financial_query(self, message: str) -> Optional[str]:
        """Deteksi apakah pesan adalah pertanyaan tentang data keuangan"""
        message_lower = message.lower()
        
        query_patterns = {
            "total_tabungan": ["total tabungan", "berapa tabungan", "jumlah tabungan", "tabungan saya"],
            "target_bulanan": ["target bulan", "target bulanan", "progress bulan", "pencapaian bulan"],
            "pengeluaran_terbesar": ["pengeluaran terbesar", "habis buat apa", "keluar paling banyak", "spend terbanyak"],
            "progress_tabungan": ["progress tabungan", "kemajuan nabung", "target tabungan", "capaian target"],
            "list_targets": ["daftar target", "list target", "target saya", "semua target", "target apa saja"],
            "ringkasan": ["ringkasan", "summary", "laporan", "rekapan", "overview"],
            "kategori": ["kategori", "jenis pengeluaran", "pembagian"],
        }
        
        for query_type, keywords in query_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return query_type
        
        return None
    
    # ===========================================
    # Enhanced Response Generation
    # ===========================================
    
    async def generate_response(self, user_message: str, user_id: str, conversation_id: str, message_id: str) -> str:
        """Generate response dari Luna AI dengan financial intelligence"""
        message_lower = user_message.lower()
        print(f"🤖 Luna processing: '{user_message}'")
        
        # Check for update/delete commands first
        update_delete_command = self.is_update_delete_command(user_message)
        if update_delete_command:
            print(f"🔧 Update/Delete command detected: {update_delete_command['action']}")
            return await self.handle_update_delete_command(user_id, conversation_id, message_id, update_delete_command)
        
        # Check for confirmation (untuk pending financial data)
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
    
    # ===========================================
    # ENHANCED: Update & Delete Handler Methods
    # ===========================================
    
    async def handle_update_delete_command(self, user_id: str, conversation_id: str, message_id: str, command: Dict[str, Any]) -> str:
        """Handle perintah update/delete savings goal"""
        action = command["action"]
        
        if action == "list":
            return await self.handle_list_savings_goals(user_id)
        
        item_name = command.get("item_name", "").strip()
        
        # Find matching savings goals
        matching_goals = await self.find_matching_savings_goals(user_id, item_name)
        
        if not matching_goals:
            return f"""🔍 **Target tabungan tidak ditemukan**

Saya tidak menemukan target tabungan dengan nama yang mirip dengan "*{item_name}*".

Untuk melihat semua target Anda, ketik: **"daftar target saya"**

Atau coba perintah dengan nama yang lebih spesifik, contoh:
• "ubah target laptop"
• "hapus target motor"
• "update target hp" """
        
        if len(matching_goals) > 1:
            # Multiple matches - ask user to specify
            goals_list = []
            for i, goal in enumerate(matching_goals[:5], 1):
                status_icon = "🟢" if goal["status"] == "active" else "🟡"
                goals_list.append(f"{i}. {status_icon} **{goal['item_name']}** - {self.format_currency(goal['target_amount'])}")
            
            return f"""🎯 **Beberapa target ditemukan untuk "{item_name}"**:

{chr(10).join(goals_list)}

Silakan sebutkan nama target yang lebih spesifik, atau gunakan perintah:
• "{'ubah' if action == 'update' else 'hapus'} target {matching_goals[0]['item_name']}"

Contoh: *"ubah target {matching_goals[0]['item_name']} jadi 15 juta"*"""
        
        # Single match found
        goal = matching_goals[0]
        
        if action == "update":
            return await self.handle_update_savings_goal(user_id, conversation_id, message_id, goal, command)
        elif action == "delete":
            return await self.handle_delete_savings_goal(user_id, conversation_id, message_id, goal, command)
    
    async def find_matching_savings_goals(self, user_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Cari savings goals yang cocok dengan search term"""
        try:
            # Get all active savings goals
            goals_cursor = self.db.savings_goals.find({
                "user_id": user_id,
                "status": {"$in": ["active", "paused"]}
            }).sort("created_at", -1)
            
            all_goals = list(goals_cursor)
            matching_goals = []
            
            search_lower = search_term.lower()
            
            for goal in all_goals:
                item_name_lower = goal["item_name"].lower()
                
                # Exact match
                if search_lower == item_name_lower:
                    matching_goals.insert(0, goal)
                # Contains match
                elif search_lower in item_name_lower or item_name_lower in search_lower:
                    matching_goals.append(goal)
                # Word match
                elif any(word in item_name_lower for word in search_lower.split() if len(word) > 2):
                    matching_goals.append(goal)
            
            return matching_goals
            
        except Exception as e:
            print(f"❌ Error finding matching savings goals: {e}")
            return []
    
    async def handle_update_savings_goal(self, user_id: str, conversation_id: str, message_id: str, 
                                       goal: Dict[str, Any], command: Dict[str, Any]) -> str:
        """
        ENHANCED: Handle update dengan validasi field tunggal
        """
        update_fields = command.get("update_fields", {})
        update_type = command.get("update_type", "unknown")
        
        print(f"🔧 Processing update for goal: {goal['item_name']}")
        print(f"📋 Update fields: {update_fields}")
        print(f"🏷️ Update type: {update_type}")
        
        if not update_fields:
            # No specific fields detected, berikan contoh spesifik
            current_target_date = ""
            if goal.get("target_date"):
                try:
                    target_date = goal["target_date"]
                    if isinstance(target_date, str):
                        target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                    current_target_date = f"\n• **Target Waktu**: {IndonesiaDatetime.format_date_only(target_date)}"
                except:
                    pass
            
            return f"""🔧 **Apa yang ingin diubah dari target "{goal['item_name']}"?**

**Data saat ini:**
• **Nama**: {goal['item_name']}
• **Target Harga**: {self.format_currency(goal['target_amount'])}{current_target_date}

**⚠️ PENTING: Hanya bisa ubah 1 hal per pesan**

**Contoh perintah:**
• *"ubah target {goal['item_name']} tanggal 31 desember 2025"* - Ubah deadline saja
• *"ubah target {goal['item_name']} jadi 15 juta"* - Ubah harga saja  
• *"ganti nama {goal['item_name']} jadi smartphone"* - Ubah nama saja

**🚫 JANGAN:** "ubah target laptop jadi 15 juta tanggal 31 desember"
**✅ LAKUKAN:** Dua pesan terpisah untuk dua perubahan

Ketik perintah yang ingin Anda lakukan! 😊"""
        
        # Validate hanya 1 field yang diupdate
        if len(update_fields) > 1:
            field_names = list(update_fields.keys())
            return f"""❌ **Terlalu banyak perubahan sekaligus!**

Anda mencoba mengubah: **{', '.join(field_names)}**

**Aturan: Hanya 1 perubahan per pesan**

Silakan lakukan perubahan satu per satu:

1️⃣ **Untuk mengubah harga:**
   *"ubah target {goal['item_name']} jadi [harga baru]"*

2️⃣ **Untuk mengubah tanggal:**  
   *"ubah target {goal['item_name']} tanggal [tanggal baru]"*

3️⃣ **Untuk mengubah nama:**
   *"ganti nama {goal['item_name']} jadi [nama baru]"*

Coba lagi dengan 1 perubahan saja ya! 😊"""
        
        # Prepare confirmation message untuk 1 field
        changes = []
        new_data = {}
        
        if "target_amount" in update_fields:
            old_amount = goal["target_amount"]
            new_amount = update_fields["target_amount"]
            changes.append(f"• **Harga**: {self.format_currency(old_amount)} → {self.format_currency(new_amount)}")
            new_data["target_amount"] = new_amount
            
            # Tambahan info untuk price update
            price_change = new_amount - old_amount
            if price_change > 0:
                changes.append(f"  📈 *Naik {self.format_currency(price_change)}*")
            else:
                changes.append(f"  📉 *Turun {self.format_currency(abs(price_change))}*")
        
        if "target_date" in update_fields:
            old_date = goal.get("target_date")
            new_date = update_fields["target_date"]
            
            old_date_str = "Tidak ada"
            if old_date:
                try:
                    if isinstance(old_date, str):
                        old_date = datetime.fromisoformat(old_date.replace('Z', '+00:00'))
                    old_date_str = IndonesiaDatetime.format_date_only(old_date)
                except:
                    old_date_str = "Tidak valid"
            
            new_date_str = IndonesiaDatetime.format_date_only(new_date)
            changes.append(f"• **Target Waktu**: {old_date_str} → {new_date_str}")
            new_data["target_date"] = self.datetime_to_iso(new_date)
            
            # Tambahan info untuk date update
            if old_date:
                try:
                    days_diff = (new_date - old_date).days
                    if days_diff > 0:
                        changes.append(f"  ⏰ *Diperpanjang {days_diff} hari*")
                    elif days_diff < 0:
                        changes.append(f"  ⚡ *Dipercepat {abs(days_diff)} hari*")
                    else:
                        changes.append(f"  📅 *Tanggal sama*")
                except:
                    pass
        
        if "item_name" in update_fields:
            old_name = goal["item_name"]
            new_name = update_fields["item_name"]
            changes.append(f"• **Nama**: {old_name} → {new_name}")
            new_data["item_name"] = new_name
        
        if not changes:
            return "🤔 Saya tidak bisa mendeteksi perubahan yang ingin dilakukan. Coba sebutkan dengan lebih jelas ya!"
        
        # Store pending update
        confirmation_message = f"""🔧 **Konfirmasi Perubahan Target Tabungan:**

**Target**: {goal['item_name']}

**Perubahan yang akan dilakukan:**
{chr(10).join(changes)}

Apakah perubahan ini sudah benar? Ketik **"ya"** untuk menyimpan atau **"tidak"** untuk membatalkan.

💡 *Setelah ini, Anda bisa melakukan perubahan lain jika diperlukan dengan pesan terpisah.*"""
        
        # Store pending update data
        pending_id = self.store_pending_update_delete(
            user_id, conversation_id, message_id, "update_savings_goal",
            {"goal_id": str(goal["_id"]), "updates": new_data},
            command["original_message"], confirmation_message
        )
        
        return confirmation_message
    
    async def handle_delete_savings_goal(self, user_id: str, conversation_id: str, message_id: str, 
                                       goal: Dict[str, Any], command: Dict[str, Any]) -> str:
        """Handle delete savings goal"""
        
        # Calculate progress info
        progress = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
        
        progress_info = ""
        if goal["current_amount"] > 0:
            progress_info = f"\n**Progress saat ini**: {self.format_currency(goal['current_amount'])} ({progress:.1f}%)"
        
        target_date_info = ""
        if goal.get("target_date"):
            try:
                target_date = goal["target_date"]
                if isinstance(target_date, str):
                    target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                target_date_info = f"\n**Target Waktu**: {IndonesiaDatetime.format_date_only(target_date)}"
            except:
                pass
        
        # Store pending delete
        confirmation_message = f"""🗑️ **Konfirmasi Hapus Target Tabungan:**

**Target yang akan dihapus:**
• **Nama**: {goal['item_name']}
• **Target Harga**: {self.format_currency(goal['target_amount'])}{target_date_info}{progress_info}

⚠️ **Perhatian**: Data target dan progress tabungan akan hilang permanen!

Apakah Anda yakin ingin menghapus target ini? Ketik **"ya"** untuk menghapus atau **"tidak"** untuk membatalkan."""
        
        # Store pending delete data
        pending_id = self.store_pending_update_delete(
            user_id, conversation_id, message_id, "delete_savings_goal",
            {"goal_id": str(goal["_id"])},
            command["original_message"], confirmation_message
        )
        
        return confirmation_message
    
    # ===========================================
    # Utility Methods for Update/Delete
    # ===========================================
    
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
    
    def store_pending_update_delete(self, user_id: str, conversation_id: str, message_id: str,
                                  action_type: str, action_data: Dict[str, Any], 
                                  original_message: str, confirmation_message: str) -> str:
        """Store pending update/delete action"""
        try:
            now = now_for_db()
            expires_at = now + timedelta(hours=24)
            
            pending_data = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "chat_message_id": message_id,
                "data_type": action_type,
                "parsed_data": action_data,
                "original_message": original_message,
                "luna_response": confirmation_message,
                "is_confirmed": False,
                "expires_at": expires_at,
                "created_at": now
            }
            
            result = self.db.pending_financial_data.insert_one(pending_data)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error storing pending update/delete: {e}")
            return None
    
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
    
    # ===========================================
    # Continue with other existing methods...
    # (handle_financial_query, handle_financial_data, handle_confirmation, etc.)
    # Saya akan tambahkan di bagian berikutnya
    # ===========================================
    
    async def handle_list_savings_goals(self, user_id: str) -> str:
        """Handle request untuk list semua savings goals"""
        try:
            # Get all savings goals
            goals_cursor = self.db.savings_goals.find({
                "user_id": user_id,
                "status": {"$in": ["active", "paused", "completed"]}
            }).sort("created_at", -1)
            
            goals = list(goals_cursor)
            
            if not goals:
                return """🎯 **Belum Ada Target Tabungan**

Anda belum memiliki target tabungan. Yuk buat target pertama!

**Contoh membuat target:**
• "Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026"
• "Target beli motor 25 juta dalam 1 tahun"
• "Pengen beli hp 5 juta"

💡 Target tabungan akan membantu Anda lebih fokus dan disiplin dalam menabung!"""
            
            # Group by status
            active_goals = [g for g in goals if g["status"] == "active"]
            completed_goals = [g for g in goals if g["status"] == "completed"]
            paused_goals = [g for g in goals if g["status"] == "paused"]
            
            response = "🎯 **Target Tabungan Anda**:\n\n"
            
            # Active goals
            if active_goals:
                response += "**🟢 Target Aktif:**\n"
                for goal in active_goals:
                    progress = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
                    progress_bar = "🟩" * int(progress // 10) + "⬜" * (10 - int(progress // 10))
                    
                    target_date_str = ""
                    if goal.get("target_date"):
                        target_date = goal["target_date"]
                        if isinstance(target_date, str):
                            try:
                                target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                            except:
                                target_date = None
                        
                        if target_date:
                            days_remaining = (target_date - datetime.now()).days
                            if days_remaining > 0:
                                target_date_str = f" (⏰ {days_remaining} hari lagi)"
                            elif days_remaining == 0:
                                target_date_str = " (⏰ hari ini!)"
                            else:
                                target_date_str = f" (⚠️ lewat {abs(days_remaining)} hari)"
                    
                    response += f"• **{goal['item_name']}**{target_date_str}\n"
                    response += f"  {progress_bar} {progress:.1f}%\n"
                    response += f"  💰 {self.format_currency(goal['current_amount'])} / {self.format_currency(goal['target_amount'])}\n\n"
            
            # Completed goals
            if completed_goals:
                response += "**🎉 Target Tercapai:**\n"
                for goal in completed_goals[:3]:  # Show max 3
                    response += f"• **{goal['item_name']}** - {self.format_currency(goal['target_amount'])} ✅\n"
                if len(completed_goals) > 3:
                    response += f"• *...dan {len(completed_goals) - 3} target lainnya*\n"
                response += "\n"
            
            # Paused goals
            if paused_goals:
                response += "**⏸️ Target Dipause:**\n"
                for goal in paused_goals[:2]:  # Show max 2
                    progress = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
                    response += f"• **{goal['item_name']}** ({progress:.1f}%) - {self.format_currency(goal['target_amount'])}\n"
                response += "\n"
            
            response += """**🛠️ Perintah yang bisa digunakan:**
• *"ubah target [nama] tanggal [tanggal baru]"* - Ubah target waktu saja
• *"ubah target [nama] jadi [harga baru]"* - Ubah harga saja
• *"ganti nama [nama] jadi [nama baru]"* - Ubah nama saja
• *"hapus target [nama]"* - Hapus target
• *"progress tabungan"* - Lihat progress detail

⚠️ **INGAT**: Hanya 1 perubahan per pesan untuk hasil yang akurat!

💡 *Tip: Sebutkan nama barang yang spesifik untuk perintah yang lebih akurat*"""
            
            return response
            
        except Exception as e:
            print(f"❌ Error listing savings goals: {e}")
            return "😅 Maaf, terjadi kesalahan saat mengambil daftar target. Coba lagi ya!"
    
    # Continue other methods from previous implementation...
    # (I'll add the remaining methods in a follow-up if needed)
    
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
• "Daftar target saya"

🔧 **Kelola Target Tabungan (1 perubahan per pesan):**
• "Ubah target laptop tanggal 31 desember 2025" - Ubah deadline
• "Ubah target laptop jadi 15 juta" - Ubah harga
• "Ganti nama laptop jadi smartphone" - Ubah nama
• "Hapus target motor" - Hapus target

💡 **Tips Keuangan Mahasiswa:**
• Tips menghemat uang saku
• Budgeting untuk mahasiswa
• Perencanaan keuangan
• Strategi menabung

Ada yang ingin dicoba sekarang?"""
            
        # Question about Luna
        elif any(word in message_lower for word in ['luna', 'kamu', 'anda', 'siapa']):
            return "Saya Luna, asisten AI yang dirancang khusus untuk membantu mahasiswa Indonesia mengelola keuangan. Saya paham betul tantangan keuangan mahasiswa dan bisa membantu Anda dengan budgeting, tips menghemat, tracking pengeluaran, mencatat transaksi, dan mengelola target tabungan dengan sistem 1 perubahan per pesan untuk akurasi terbaik!"
            
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
    
    async def handle_financial_query(self, user_id: str, query_type: str) -> str:
        """Handle pertanyaan tentang data keuangan user"""
        try:
            # Import finance service untuk mendapatkan data
            from .finance_service import FinanceService
            finance_service = FinanceService()
            
            if query_type == "list_targets":
                return await self.handle_list_savings_goals(user_id)
            
            elif query_type == "total_tabungan":
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
        """Handle konfirmasi dari user untuk data keuangan atau update/delete"""
        print(f"🔄 Processing confirmation: {confirmed}")
        
        # Get latest pending data
        pending_data = self.get_latest_pending_data(user_id, conversation_id)
        
        if not pending_data:
            print("❌ No pending data found")
            return await self.handle_regular_message("ya" if confirmed else "tidak")
        
        data_type = pending_data.get("data_type")
        
        if confirmed:
            if data_type in ["update_savings_goal", "delete_savings_goal"]:
                return await self.confirm_update_delete_action(user_id, pending_data)
            else:
                return await self.confirm_financial_data(user_id, pending_data)
        else:
            if data_type in ["update_savings_goal", "delete_savings_goal"]:
                return await self.cancel_update_delete_action(user_id, pending_data)
            else:
                return await self.cancel_financial_data(user_id, pending_data)
    
    async def confirm_update_delete_action(self, user_id: str, pending_data: dict) -> str:
        """Konfirmasi dan eksekusi update/delete savings goal"""
        try:
            data_type = pending_data["data_type"]
            action_data = pending_data["parsed_data"]
            goal_id = action_data["goal_id"]
            
            if data_type == "update_savings_goal":
                # Update savings goal
                updates = action_data["updates"]
                
                # Prepare update data
                update_data = {
                    "updated_at": now_for_db()
                }
                update_data.update(updates)
                
                # Convert ISO string back to datetime if needed
                if "target_date" in update_data and isinstance(update_data["target_date"], str):
                    try:
                        update_data["target_date"] = self.iso_to_datetime(update_data["target_date"])
                    except:
                        update_data["target_date"] = None
                
                # Update in database
                result = self.db.savings_goals.update_one(
                    {"_id": ObjectId(goal_id), "user_id": user_id},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    # Get updated goal for response
                    updated_goal = self.db.savings_goals.find_one({"_id": ObjectId(goal_id)})
                    
                    # Determine what was updated for response
                    updated_field = ""
                    if "target_amount" in updates:
                        updated_field = "harga"
                    elif "target_date" in updates:
                        updated_field = "tanggal target"
                    elif "item_name" in updates:
                        updated_field = "nama"
                    
                    response = f"""✅ **Target tabungan berhasil diubah!**

**Target yang diperbarui:**
• **Nama**: {updated_goal['item_name']}
• **Target Harga**: {self.format_currency(updated_goal['target_amount'])}"""
                    
                    if updated_goal.get("target_date"):
                        try:
                            target_date = updated_goal["target_date"]
                            if isinstance(target_date, str):
                                target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                            response += f"\n• **Target Waktu**: {IndonesiaDatetime.format_date_only(target_date)}"
                        except:
                            pass
                    
                    progress = (updated_goal["current_amount"] / updated_goal["target_amount"] * 100) if updated_goal["target_amount"] > 0 else 0
                    response += f"\n• **Progress**: {self.format_currency(updated_goal['current_amount'])} ({progress:.1f}%)"
                    
                    response += f"\n\n🎯 **{updated_field.title()} berhasil diperbarui!**"
                    
                    if updated_field != "tanggal target":
                        response += "\n\n💡 *Ingin mengubah tanggal target? Ketik: \"ubah target [nama] tanggal [tanggal baru]\"*"
                    elif updated_field != "harga":
                        response += "\n\n💡 *Ingin mengubah harga target? Ketik: \"ubah target [nama] jadi [harga baru]\"*"
                    
                    response += f"\n\n{random.choice(self.student_tips)}"
                    
                    # Mark as confirmed
                    self.db.pending_financial_data.update_one(
                        {"_id": ObjectId(pending_data["_id"])},
                        {"$set": {"is_confirmed": True, "confirmed_at": now_for_db()}}
                    )
                    
                    return response
                else:
                    return "⚠️ Target tidak ditemukan atau tidak ada perubahan yang dilakukan."
            
            elif data_type == "delete_savings_goal":
                # Delete savings goal
                result = self.db.savings_goals.delete_one(
                    {"_id": ObjectId(goal_id), "user_id": user_id}
                )
                
                if result.deleted_count > 0:
                    # Mark as confirmed
                    self.db.pending_financial_data.update_one(
                        {"_id": ObjectId(pending_data["_id"])},
                        {"$set": {"is_confirmed": True, "confirmed_at": now_for_db()}}
                    )
                    
                    return """✅ **Target tabungan berhasil dihapus!**

Target telah dihapus dari daftar Anda. Jangan khawatir, Anda masih bisa membuat target baru kapan saja!

**Contoh membuat target baru:**
• "Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026"
• "Target beli motor 25 juta dalam 1 tahun"

Tetap semangat menabung! 💪"""
                else:
                    return "⚠️ Target tidak ditemukan atau sudah dihapus sebelumnya."
            
        except Exception as e:
            print(f"❌ Error confirming update/delete action: {e}")
            return "😅 Maaf, terjadi kesalahan saat memproses permintaan. Coba lagi ya!"
    
    async def cancel_update_delete_action(self, user_id: str, pending_data: dict) -> str:
        """Batalkan update/delete action"""
        try:
            data_type = pending_data["data_type"]
            
            # Delete pending data
            self.db.pending_financial_data.delete_one({"_id": ObjectId(pending_data["_id"])})
            
            if data_type == "update_savings_goal":
                return "❌ **Perubahan target dibatalkan.**\n\nTidak ada perubahan yang dilakukan pada target tabungan Anda."
            elif data_type == "delete_savings_goal":
                return "❌ **Penghapusan target dibatalkan.**\n\nTarget tabungan Anda tetap aman dan tidak dihapus."
            
        except Exception as e:
            print(f"❌ Error cancelling update/delete action: {e}")
            return "😅 Maaf, terjadi kesalahan. Coba lagi ya!"
    
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

Mulai menabung sekarang untuk mencapai target Anda! 💪

💡 *Untuk mengubah target ini nanti, gunakan: "ubah target [nama] ..."*"""
                
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
            'motor': 'Tabungan Motor',
            'ubah target': 'Update Target Tabungan',
            'hapus target': 'Kelola Target Tabungan',
            'daftar target': 'Target Tabungan'
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