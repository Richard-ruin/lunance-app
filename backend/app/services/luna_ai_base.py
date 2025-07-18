# app/services/luna_ai_base.py - Core Luna AI functionality
import re
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .enhanced_financial_parser import EnhancedFinancialParser
from .financial_categories import IndonesianStudentCategories


class LunaAIBase:
    """Base Luna AI dengan core functionality"""
    
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
        
        # Update & Delete Keywords
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
        
        # Purchase Intent Keywords
        self.purchase_intent_keywords = [
            'ingin beli', 'mau beli', 'pengen beli', 'mau buat beli',
            'planning beli', 'rencana beli', 'kepingin beli', 'butuh beli',
            'mau ambil', 'ingin ambil', 'pengen ambil', 'planning ambil'
        ]
        
        # Responses untuk mahasiswa Indonesia
        self.greetings = [
            "Halo! Saya Luna, asisten keuangan khusus untuk anda. Ada yang bisa saya bantu hari ini?",
            "Hi! Luna di sini. Siap membantu Anda mengelola keuangan dengan lebih baik!",
            "Selamat datang! Saya Luna, mari kita atur keuangan Anda bersama-sama.",
            "Halo! Saya Luna, AI finansial yang paham betul kebutuhan mahasiswa Indonesia. Ada yang ingin dibahas?",
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
    
    def format_currency(self, amount: float) -> str:
        """Format jumlah uang ke format Rupiah"""
        return f"Rp {amount:,.0f}".replace(',', '.')
    
    # ==========================================
    # DETECTION METHODS
    # ==========================================
    
    def is_confirmation_message(self, message: str) -> Optional[bool]:
        """Cek apakah pesan adalah konfirmasi"""
        message_lower = message.lower().strip()
        
        if any(word in message_lower for word in self.confirmation_yes):
            return True
        elif any(word in message_lower for word in self.confirmation_no):
            return False
        
        return None
    
    def is_purchase_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect purchase intent dari pesan user"""
        message_lower = message.lower()
        
        # Check for purchase intent keywords
        has_purchase_intent = any(keyword in message_lower for keyword in self.purchase_intent_keywords)
        
        if not has_purchase_intent:
            return None
        
        # Parse amount dari message
        amount = self.parser.parse_amount(message)
        
        if not amount:
            return None
        
        # Extract item name
        item_name = self._extract_item_name_from_purchase_intent(message, amount)
        
        # Determine confidence
        confidence = 0.8 if item_name and len(item_name) > 2 else 0.6
        
        return {
            "item_name": item_name,
            "price": amount,
            "intent_type": "purchase_inquiry",
            "confidence": confidence,
            "original_message": message
        }
    
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
            "financial_health": ["kesehatan keuangan", "kondisi keuangan", "financial health", "sehat keuangan"],
            "budget_performance": ["performa budget", "budget performance", "pencapaian budget", "budget bulan ini"],
            "spending_analysis": ["analisis pengeluaran", "pola pengeluaran", "spending pattern", "kebiasaan belanja"]
        }
        
        for query_type, keywords in query_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return query_type
        
        return None
    
    def is_update_delete_command(self, message: str) -> Optional[Dict[str, Any]]:
        """Deteksi perintah update/delete dengan klasifikasi yang lebih baik"""
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
                    "update_type": update_type,  
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
    
    # ==========================================
    # EXTRACTION METHODS
    # ==========================================
    
    def _extract_item_name_from_purchase_intent(self, message: str, amount: float) -> str:
        """Extract item name dari purchase intent message"""
        # Remove purchase intent keywords
        clean_message = message.lower()
        
        for keyword in self.purchase_intent_keywords:
            clean_message = re.sub(rf'\b{keyword}\b', '', clean_message, flags=re.IGNORECASE)
        
        # Remove amount patterns
        for pattern in self.parser.money_patterns:
            clean_message = re.sub(pattern, '', clean_message, flags=re.IGNORECASE)
        
        # Remove common connecting words
        remove_words = ['seharga', 'dengan harga', 'harga', 'sekitar', 'kira-kira', 'kurang lebih']
        for word in remove_words:
            clean_message = re.sub(rf'\b{word}\b', '', clean_message, flags=re.IGNORECASE)
        
        # Clean up and return
        clean_message = re.sub(r'\s+', ' ', clean_message).strip()
        
        # If too short, try to extract from common patterns
        if len(clean_message) < 2:
            # Look for common item patterns
            item_patterns = [
                r'\b(laptop|notebook|macbook)\b',
                r'\b(hp|handphone|smartphone|iphone|samsung)\b',
                r'\b(motor|sepeda|mobil)\b',
                r'\b(baju|kemeja|celana|sepatu)\b',
                r'\b(tas|dompet|jaket)\b'
            ]
            
            for pattern in item_patterns:
                match = re.search(pattern, message.lower())
                if match:
                    return match.group(1).title()
            
            return "barang"
        
        return clean_message.title()
    
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
    
    def extract_update_fields(self, message_lower: str) -> Dict[str, Any]:
        """Extract field yang akan diupdate dengan prioritas yang jelas"""
        update_fields = {}
        
        # Check for date update first
        date_update_indicators = [
            'tanggal', 'waktu', 'deadline', 'target waktu', 'kapan', 'bulan', 'tahun'
        ]
        
        is_date_update = any(indicator in message_lower for indicator in date_update_indicators)
        
        if is_date_update:
            target_date = self.parser.parse_target_date(message_lower)
            if target_date:
                update_fields["target_date"] = target_date
                return update_fields
        
        # Check for price update
        price_update_indicators = [
            'jadi', 'menjadi', 'ganti harga', 'ubah harga', 'harga jadi', 
            'ribu', 'juta', 'rb', 'jt', 'rp', 'rupiah'
        ]
        
        is_price_update = any(indicator in message_lower for indicator in price_update_indicators)
        
        if is_price_update and not is_date_update:
            amount = self.parse_price_for_update(message_lower)
            if amount:
                update_fields["target_amount"] = amount
                return update_fields
        
        # Check for name update
        name_update_indicators = [
            'ganti nama', 'ubah nama', 'nama jadi', 'namanya', 'rename'
        ]
        
        is_name_update = any(indicator in message_lower for indicator in name_update_indicators)
        
        if is_name_update:
            name_patterns = [
                r'(?:nama\s+)?(?:jadi|menjadi|ke)\s+(.+?)(?:\s+(?:tanggal|pada|waktu|deadline)|\s*$)',
                r'(?:ganti|ubah)\s+nama\s+(?:jadi|menjadi|ke)?\s*(.+?)(?:\s+(?:tanggal|pada|waktu|deadline)|\s*$)'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    new_name = match.group(1).strip()
                    new_name = self.clean_item_name_for_update(new_name)
                    if new_name and len(new_name) > 2:
                        update_fields["item_name"] = new_name
                        return update_fields
                    break
        
        return update_fields
    
    def parse_price_for_update(self, message_lower: str) -> Optional[float]:
        """Parse harga khusus untuk update dengan filter tanggal yang lebih kuat"""
        # Remove common date patterns to avoid confusion
        message_without_dates = message_lower
        
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
        
        # Parse amount dari message yang sudah dibersihkan
        amount = self.parser.parse_amount(message_without_dates)
        
        return amount
    
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
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
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
            'ingin beli': 'Analisis Pembelian',
            'mau beli': 'Konsultasi Pembelian',
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