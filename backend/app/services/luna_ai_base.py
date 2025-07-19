# app/services/luna_ai_base.py - CLEAN VERSION (IndoRoBERTa only)
import re
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db

# FIXED: Only import IndoRoBERTa parser - NO FALLBACK
try:
    from .indoroberta_financial_parser import IndoRoBERTaFinancialParser
    print("✅ IndoRoBERTa Financial Parser imported successfully")
    INDOROBERTA_AVAILABLE = True
except ImportError as e:
    print(f"❌ Failed to import IndoRoBERTa parser: {e}")
    print("🚨 CRITICAL: IndoRoBERTa parser is required!")
    INDOROBERTA_AVAILABLE = False

try:
    from .financial_categories import IndonesianStudentCategories
except ImportError:
    print("⚠️ IndonesianStudentCategories not found")
    IndonesianStudentCategories = None


class LunaAIBase:
    """Base Luna AI dengan IndoRoBERTa integration ONLY - NO FALLBACK"""
    
    def __init__(self):
        self.db = get_database()
        
        # CRITICAL: Initialize IndoRoBERTa parser ONLY
        if INDOROBERTA_AVAILABLE:
            try:
                print("🤖 Initializing IndoRoBERTa Financial Parser...")
                self.parser = IndoRoBERTaFinancialParser()
                
                # Check if models are loaded
                if hasattr(self.parser, 'models_loaded'):
                    if self.parser.models_loaded:
                        print("✅ IndoRoBERTa ML models loaded successfully!")
                    else:
                        print("📋 Using rule-based parser (IndoRoBERTa models not loaded)")
                
                # Log parser status
                if hasattr(self.parser, 'get_model_status'):
                    try:
                        status = self.parser.get_model_status()
                        print(f"📊 Parser Model Status: {status}")
                    except Exception as e:
                        print(f"⚠️ Could not get parser status: {e}")
                
            except Exception as e:
                print(f"❌ Error initializing IndoRoBERTa parser: {e}")
                print("🚨 CRITICAL: IndoRoBERTa parser initialization failed!")
                self.parser = None
        else:
            print("❌ IndoRoBERTa parser not available - SYSTEM WILL NOT WORK PROPERLY")
            self.parser = None
        
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
            "Halo! Saya Luna, asisten keuangan dengan IndoRoBERTa AI. Ada yang bisa saya bantu hari ini?",
            "Hi! Luna di sini dengan teknologi IndoRoBERTa untuk mengelola keuangan Anda!",
            "Selamat datang! Saya Luna dengan AI parsing yang canggih untuk mahasiswa Indonesia.",
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
    # INDOROBERTA PARSING METHODS ONLY
    # ==========================================
    
    def parse_financial_message(self, message: str) -> Dict[str, Any]:
        """Parse financial message menggunakan IndoRoBERTa ONLY"""
        if not self.parser:
            print("❌ CRITICAL: No IndoRoBERTa parser available!")
            return {
                "is_financial_data": False, 
                "error": "IndoRoBERTa parser not available",
                "parsing_method": "none"
            }
        
        try:
            print(f"🔍 Parsing with IndoRoBERTa: '{message}'")
            result = self.parser.parse_financial_data(message)
            
            # Add method info to result
            if hasattr(self.parser, 'models_loaded'):
                result["parsing_method"] = "IndoRoBERTa_ML" if self.parser.models_loaded else "IndoRoBERTa_Rules"
            else:
                result["parsing_method"] = "IndoRoBERTa"
            
            return result
        except Exception as e:
            print(f"❌ Error parsing with IndoRoBERTa: {e}")
            return {
                "is_financial_data": False, 
                "error": str(e),
                "parsing_method": "error"
            }
    
    # ==========================================
    # DETECTION METHODS (use IndoRoBERTa only)
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
        """Detect purchase intent menggunakan IndoRoBERTa"""
        message_lower = message.lower()
        
        # Check for purchase intent keywords
        has_purchase_intent = any(keyword in message_lower for keyword in self.purchase_intent_keywords)
        
        if not has_purchase_intent:
            return None
        
        # Parse amount using IndoRoBERTa
        if not self.parser:
            print("❌ Cannot parse purchase intent - no IndoRoBERTa parser")
            return None
        
        amount = self.parser.parse_amount(message)
        if not amount:
            return None
        
        # Extract item name
        item_name = self._extract_item_name_from_purchase_intent(message, amount)
        
        return {
            "item_name": item_name,
            "price": amount,
            "intent_type": "purchase_inquiry",
            "confidence": 0.8,
            "original_message": message,
            "parsed_by": "IndoRoBERTa"
        }
    
    def is_financial_query(self, message: str) -> Optional[str]:
        """Deteksi financial queries"""
        message_lower = message.lower()
        
        query_patterns = {
            "total_tabungan": ["total tabungan", "berapa tabungan", "jumlah tabungan", "tabungan saya"],
            "target_bulanan": ["target bulan", "target bulanan", "progress bulan", "pencapaian bulan"],
            "pengeluaran_terbesar": ["pengeluaran terbesar", "habis buat apa", "keluar paling banyak", "spend terbanyak"],
            "progress_tabungan": ["progress tabungan", "kemajuan nabung", "target tabungan", "capaian target"],
            "list_targets": ["daftar target", "list target", "target saya", "semua target", "target apa saja"],
            "ringkasan": ["ringkasan", "summary", "laporan", "rekapan", "overview"],
            "financial_health": ["kesehatan keuangan", "kondisi keuangan", "financial health", "sehat keuangan"],
            "budget_performance": ["performa budget", "budget performance", "pencapaian budget", "budget bulan ini"],
            "spending_analysis": ["analisis pengeluaran", "pola pengeluaran", "spending pattern", "kebiasaan belanja"]
        }
        
        for query_type, keywords in query_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return query_type
        
        return None
    
    def is_update_delete_command(self, message: str) -> Optional[Dict[str, Any]]:
        """Deteksi perintah update/delete"""
        message_lower = message.lower().strip()
        
        # Check for update/delete commands
        has_update = any(word in message_lower for word in self.update_keywords)
        has_delete = any(word in message_lower for word in self.delete_keywords)
        has_target = any(word in message_lower for word in self.target_keywords)
        
        if (has_update or has_delete) and has_target:
            # Extract item name from message
            item_name = self.extract_item_name_from_command(message_lower)
            
            if has_update:
                # Determine update type
                update_type = self.determine_update_type(message_lower)
                
                # Extract update fields using IndoRoBERTa
                update_fields = self.extract_update_fields(message_lower)
                
                return {
                    "action": "update",
                    "update_type": update_type,  
                    "item_name": item_name,
                    "update_fields": update_fields,
                    "original_message": message,
                    "parsed_by": "IndoRoBERTa"
                }
            elif has_delete:
                return {
                    "action": "delete",
                    "item_name": item_name,
                    "original_message": message,
                    "parsed_by": "IndoRoBERTa"
                }
        
        # Special command to list all targets
        if any(phrase in message_lower for phrase in ["daftar target", "list target", "target saya", "semua target"]):
            return {
                "action": "list",
                "original_message": message
            }
        
        return None
    
    # ==========================================
    # EXTRACTION METHODS (using IndoRoBERTa)
    # ==========================================
    
    def _extract_item_name_from_purchase_intent(self, message: str, amount: float) -> str:
        """Extract item name dari purchase intent message"""
        # Remove purchase intent keywords
        clean_message = message.lower()
        
        for keyword in self.purchase_intent_keywords:
            clean_message = re.sub(rf'\b{keyword}\b', '', clean_message, flags=re.IGNORECASE)
        
        # Remove amount patterns using IndoRoBERTa if available
        if self.parser and hasattr(self.parser, 'money_patterns'):
            for pattern in self.parser.money_patterns:
                clean_message = re.sub(pattern, '', clean_message, flags=re.IGNORECASE)
        
        # Clean up and return
        clean_message = re.sub(r'\s+', ' ', clean_message).strip()
        
        if len(clean_message) < 2:
            return "barang"
        
        return clean_message.title()
    
    def extract_item_name_from_command(self, message_lower: str) -> str:
        """Extract nama barang dari perintah update/delete"""
        clean_message = message_lower
        
        # Remove action words
        for word in self.update_keywords + self.delete_keywords + self.target_keywords:
            clean_message = re.sub(rf'\b{word}\b', '', clean_message, flags=re.IGNORECASE)
        
        # Remove common connecting words
        remove_words = ['untuk', 'buat', 'pada', 'tanggal', 'dalam', 'mau', 'ingin', 'pengen', 'jadi', 'menjadi']
        for word in remove_words:
            clean_message = re.sub(rf'\b{word}\b', '', clean_message, flags=re.IGNORECASE)
        
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
        """Extract field yang akan diupdate menggunakan IndoRoBERTa"""
        update_fields = {}
        
        # Check for date update using IndoRoBERTa
        date_update_indicators = ['tanggal', 'waktu', 'deadline', 'target waktu', 'kapan', 'bulan', 'tahun']
        is_date_update = any(indicator in message_lower for indicator in date_update_indicators)
        
        if is_date_update and self.parser and hasattr(self.parser, 'parse_target_date'):
            target_date = self.parser.parse_target_date(message_lower)
            if target_date:
                update_fields["target_date"] = target_date
                return update_fields
        
        # Check for price update using IndoRoBERTa
        price_update_indicators = ['jadi', 'menjadi', 'ganti harga', 'ubah harga', 'harga jadi', 'ribu', 'juta', 'rb', 'jt', 'rp', 'rupiah']
        is_price_update = any(indicator in message_lower for indicator in price_update_indicators)
        
        if is_price_update and not is_date_update:
            amount = self.parse_price_for_update(message_lower)
            if amount:
                update_fields["target_amount"] = amount
                return update_fields
        
        # Check for name update
        name_update_indicators = ['ganti nama', 'ubah nama', 'nama jadi', 'namanya', 'rename']
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
        """Parse harga untuk update menggunakan IndoRoBERTa"""
        # Remove date patterns
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
        
        # Parse amount using IndoRoBERTa
        if self.parser and hasattr(self.parser, 'parse_amount'):
            return self.parser.parse_amount(message_without_dates)
        
        return None
    
    def clean_item_name_for_update(self, name: str) -> str:
        """Clean item name untuk update"""
        clean_name = name
        
        # Remove price and date indicators
        clean_name = re.sub(r'\d+\s*(juta|ribu|rb|jt|m|k)', '', clean_name, flags=re.IGNORECASE)
        clean_name = re.sub(r'\d+\s*(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)', '', clean_name, flags=re.IGNORECASE)
        clean_name = re.sub(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', '', clean_name)
        
        # Remove time-related words
        time_words = ['tanggal', 'pada', 'waktu', 'deadline', 'bulan', 'tahun']
        for word in time_words:
            clean_name = re.sub(rf'\b{word}\b', '', clean_name, flags=re.IGNORECASE)
        
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
        """Store pending financial data"""
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
                "created_at": now,
                "parsed_by": "IndoRoBERTa"  # Add parser info
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
                "created_at": now,
                "parsed_by": "IndoRoBERTa"  # Add parser info
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
            'budget': 'Budget IndoRoBERTa',
            'anggaran': 'Perencanaan Anggaran AI',
            'tabungan': 'AI Tips Menabung',
            'hemat': 'Tips Hemat AI',
            'uang saku': 'Manajemen Uang Saku',
            'pengeluaran': 'AI Tracking Pengeluaran',
            'pemasukan': 'Catat Pemasukan AI',
            'keuangan': 'Konsultasi Keuangan AI',
            'ingin beli': 'AI Analisis Pembelian',
            'mau beli': 'Konsultasi Pembelian AI',
            'nabung': 'Target Tabungan AI',
            'laptop': 'Tabungan Laptop',
            'hp': 'Tabungan HP',
            'motor': 'Tabungan Motor',
            'ubah target': 'Update Target AI',
            'hapus target': 'Kelola Target AI',
            'daftar target': 'Target Tabungan AI'
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
        title_words = important_words[:3] if important_words else words[:3]  # Reduced to 3 words
        title = ' '.join(title_words)
        
        if title:
            title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
            title = f"AI {title}"  # Add AI prefix
        else:
            title = "IndoRoBERTa Chat"
        
        if len(title) > 40:
            title = title[:37] + "..."
        
        return title