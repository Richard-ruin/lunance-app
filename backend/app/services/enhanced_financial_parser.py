# app/services/enhanced_financial_parser.py - Enhanced parser for Indonesian students
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from ..services.financial_categories import IndonesianStudentCategories

class EnhancedFinancialParser:
    """Enhanced parser untuk mengekstrak data keuangan dari pesan chat mahasiswa Indonesia"""
    
    def __init__(self):
        # Keywords untuk mengidentifikasi tipe transaksi (disesuaikan untuk mahasiswa)
        self.income_keywords = [
            'dapat', 'terima', 'kiriman', 'uang saku', 'gaji', 'bayaran', 'dibayar',
            'transfer masuk', 'beasiswa', 'hadiah', 'bonus', 'menang', 'juara',
            'freelance', 'project', 'ngajar', 'les', 'jual', 'jualan', 'untung'
        ]
        
        self.expense_keywords = [
            'bayar', 'beli', 'belanja', 'buat', 'keluar', 'habis', 'spend',
            'ongkos', 'biaya', 'sewa', 'cicilan', 'transfer ke', 'kirim',
            'makan', 'minum', 'jajan', 'transport', 'ojol', 'grab', 'gojek'
        ]
        
        self.savings_keywords = [
            'nabung', 'tabung', 'target', 'ingin beli', 'mau beli', 'pengen beli',
            'kepengen', 'impian', 'rencana beli', 'saving', 'goal', 'tujuan'
        ]
        
        # Pattern untuk mendeteksi jumlah uang (improved untuk bahasa Indonesia)
        self.money_patterns = [
            r'(?:rp\.?\s*)?(\d{1,3}(?:\.\d{3})*(?:\,\d{1,2})?)\s*(?:ribu|rb|k)',  # 500 ribu, 500k
            r'(?:rp\.?\s*)?(\d{1,3}(?:\.\d{3})*(?:\,\d{1,2})?)\s*(?:juta|jt|m)',  # 5 juta, 5m
            r'(?:rp\.?\s*)?(\d{1,3}(?:\.\d{3})*(?:\,\d{1,2})?)\s*(?:miliar|b)',   # 1 miliar
            r'(?:rp\.?\s*)?(\d+\.?\d*)',  # angka biasa dengan/tanpa desimal
        ]
        
        # Pattern untuk mendeteksi tanggal target (new feature)
        self.date_patterns = [
            r'(?:pada\s+)?(?:tanggal\s+)?(\d{1,2})\s+(\w+)\s+(\d{4})',  # 22 januari 2026
            r'(?:pada\s+)?(?:tanggal\s+)?(\d{1,2})[-/](\d{1,2})[-/](\d{4})',  # 22/01/2026 atau 22-01-2026
            r'(?:pada\s+)?(?:bulan\s+)?(\w+)\s+(\d{4})',  # januari 2026
            r'(?:dalam\s+)?(\d+)\s+(?:bulan|bln)',  # dalam 6 bulan
            r'(?:dalam\s+)?(\d+)\s+(?:tahun|thn)',  # dalam 2 tahun
        ]
        
        # Mapping bulan Indonesia
        self.month_mapping = {
            'januari': 1, 'februari': 2, 'maret': 3, 'april': 4,
            'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
            'september': 9, 'oktober': 10, 'november': 11, 'desember': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'jun': 6, 'jul': 7, 'agu': 8, 'sep': 9, 'okt': 10, 'nov': 11, 'des': 12
        }
    
    def parse_amount(self, text: str) -> Optional[float]:
        """Parse jumlah uang dari teks (improved)"""
        text_lower = text.lower()
        
        for pattern in self.money_patterns:
            match = re.search(pattern, text_lower)
            if match:
                amount_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    amount = float(amount_str)
                    
                    # Apply multiplier based on unit
                    if any(unit in text_lower for unit in ['ribu', 'rb', 'k']):
                        amount *= 1000
                    elif any(unit in text_lower for unit in ['juta', 'jt', 'm']):
                        amount *= 1000000
                    elif any(unit in text_lower for unit in ['miliar', 'b']):
                        amount *= 1000000000
                    
                    return amount
                except ValueError:
                    continue
        
        return None
    
    def parse_target_date(self, text: str) -> Optional[datetime]:
        """Parse tanggal target dari teks (new feature)"""
        text_lower = text.lower()
        
        for pattern in self.date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    groups = match.groups()
                    
                    if len(groups) == 3:
                        # Format: 22 januari 2026 atau 22/01/2026
                        if groups[1].isdigit():
                            # Numeric format: 22/01/2026
                            day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                        else:
                            # Text format: 22 januari 2026
                            day = int(groups[0])
                            month_name = groups[1].lower()
                            year = int(groups[2])
                            month = self.month_mapping.get(month_name)
                            if not month:
                                continue
                        
                        return datetime(year, month, day)
                    
                    elif len(groups) == 2:
                        # Format: januari 2026
                        month_name = groups[0].lower()
                        year = int(groups[1])
                        month = self.month_mapping.get(month_name)
                        if month:
                            return datetime(year, month, 1)  # Set to first day of month
                    
                    elif len(groups) == 1:
                        # Format: dalam 6 bulan / dalam 2 tahun
                        now = datetime.now()
                        if 'bulan' in text_lower:
                            months = int(groups[0])
                            return now + timedelta(days=months * 30)  # Approximate
                        elif 'tahun' in text_lower:
                            years = int(groups[0])
                            return now.replace(year=now.year + years)
                
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def detect_transaction_type(self, text: str) -> Optional[str]:
        """Deteksi tipe transaksi dari teks"""
        text_lower = text.lower()
        
        # Check for savings goal keywords first
        if any(keyword in text_lower for keyword in self.savings_keywords):
            return "savings_goal"
        
        # Check for income (prioritize specific student income patterns)
        income_score = sum(1 for keyword in self.income_keywords if keyword in text_lower)
        
        # Check for expense (more common for students)
        expense_score = sum(1 for keyword in self.expense_keywords if keyword in text_lower)
        
        if income_score > expense_score:
            return "income"
        elif expense_score > income_score:
            return "expense"
        
        return None
    
    def extract_category(self, text: str, transaction_type: str) -> str:
        """Ekstrak kategori menggunakan Indonesian Student Categories"""
        if transaction_type == "income":
            return IndonesianStudentCategories.get_income_category(text)
        else:
            return IndonesianStudentCategories.get_expense_category(text)
    
    def extract_description(self, text: str, amount: float) -> str:
        """Ekstrak deskripsi dari teks (improved)"""
        # Remove amount patterns and common words
        clean_text = text
        for pattern in self.money_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # Remove date patterns
        for pattern in self.date_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # Remove common connecting words
        remove_words = ['untuk', 'buat', 'pada', 'tanggal', 'dalam', 'mau', 'ingin', 'pengen']
        for word in remove_words:
            clean_text = re.sub(rf'\b{word}\b', '', clean_text, flags=re.IGNORECASE)
        
        # Clean up and return
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text[:100] if clean_text else "Transaksi melalui chat"
    
    def extract_item_name_for_savings(self, text: str, amount: float, target_date: Optional[datetime] = None) -> str:
        """Ekstrak nama barang untuk target tabungan"""
        # Remove amount and date patterns
        clean_text = text
        for pattern in self.money_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        if target_date:
            for pattern in self.date_patterns:
                clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # Remove savings keywords
        savings_words = ['nabung', 'tabung', 'target', 'ingin', 'mau', 'pengen', 'beli', 'buat']
        for word in savings_words:
            clean_text = re.sub(rf'\b{word}\b', '', clean_text, flags=re.IGNORECASE)
        
        # Clean up
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # If still empty or too short, provide default
        if not clean_text or len(clean_text) < 3:
            return "Target tabungan"
        
        return clean_text[:50]  # Limit length
    
    def parse_financial_data(self, text: str) -> Dict[str, Any]:
        """Parse data keuangan dari teks chat (enhanced)"""
        result = {
            "is_financial_data": False,
            "confidence": 0.0,
            "data_type": None,
            "parsed_data": None,
            "suggestions": [],
            "validation_errors": []
        }
        
        # Detect amount first
        amount = self.parse_amount(text)
        if not amount:
            return result
        
        # Detect transaction type
        data_type = self.detect_transaction_type(text)
        if not data_type:
            return result
        
        result["is_financial_data"] = True
        result["data_type"] = data_type
        
        if data_type in ["income", "expense"]:
            category = self.extract_category(text, data_type)
            description = self.extract_description(text, amount)
            
            result["parsed_data"] = {
                "type": data_type,
                "amount": amount,
                "category": category,
                "description": description,
                "date": datetime.now()
            }
            
            # Calculate confidence based on category match
            if category != "Lainnya":
                result["confidence"] = 0.9
            else:
                result["confidence"] = 0.7
                # Suggest similar categories
                similar = IndonesianStudentCategories.suggest_similar_categories(text, data_type)
                if similar:
                    result["suggestions"] = [f"Mungkin maksud Anda kategori: {', '.join(similar)}"]
            
        elif data_type == "savings_goal":
            target_date = self.parse_target_date(text)
            item_name = self.extract_item_name_for_savings(text, amount, target_date)
            description = f"Target tabungan: {text[:100]}"
            
            result["parsed_data"] = {
                "item_name": item_name,
                "target_amount": amount,
                "target_date": target_date,
                "description": description
            }
            
            # Higher confidence if target date is specified
            result["confidence"] = 0.9 if target_date else 0.7
            
            if target_date:
                result["suggestions"].append(f"Target waktu: {target_date.strftime('%d %B %Y')}")
            else:
                result["suggestions"].append("Tip: Tambahkan target waktu untuk perencanaan yang lebih baik, contoh: 'pada tanggal 22 januari 2026'")
        
        return result