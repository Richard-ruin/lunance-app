# app/services/luna_ai_finance.py - Luna AI Financial Integration for Chatbot

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json

from .financial_categories import IndonesianStudentCategories
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db

logger = logging.getLogger(__name__)

@dataclass
class ParsedFinancialData:
    """Structured financial data from chat"""
    data_type: str  # "transaction", "savings_goal", "budget_inquiry"
    transaction_type: Optional[str] = None  # "income", "expense"
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    item_name: Optional[str] = None  # for savings goals
    target_amount: Optional[float] = None  # for savings goals
    target_date: Optional[datetime] = None
    confidence: float = 0.0
    original_text: str = ""

class LunaAIFinanceParser:
    """Luna AI Finance Parser - Extract financial data from Indonesian chat messages"""
    
    def __init__(self):
        self.categories = IndonesianStudentCategories()
        logger.info("🤖 Luna AI Finance Parser initialized")
    
    def parse_financial_message(self, message: str) -> Dict[str, Any]:
        """Main method to parse financial message"""
        try:
            message = message.strip()
            logger.info(f"🤖 Luna parsing: '{message}'")
            
            # Check if message contains financial data
            if not self._is_financial_message(message):
                return {
                    "is_financial_data": False,
                    "confidence": 0.0,
                    "message": "Pesan tidak mengandung data keuangan",
                    "parsing_method": "Luna_AI"
                }
            
            # Try to parse as transaction
            transaction_result = self._parse_transaction(message)
            if transaction_result:
                logger.info(f"✅ Luna detected transaction: {transaction_result.data_type}")
                return self._format_response(transaction_result)
            
            # Try to parse as savings goal
            goal_result = self._parse_savings_goal(message)
            if goal_result:
                logger.info(f"✅ Luna detected savings goal: {goal_result.item_name}")
                return self._format_response(goal_result)
            
            # Try to parse as budget inquiry
            budget_result = self._parse_budget_inquiry(message)
            if budget_result:
                logger.info(f"✅ Luna detected budget inquiry")
                return self._format_response(budget_result)
            
            return {
                "is_financial_data": False,
                "confidence": 0.1,
                "message": "Tidak dapat mengidentifikasi jenis data keuangan",
                "parsing_method": "Luna_AI"
            }
            
        except Exception as e:
            logger.error(f"❌ Luna parsing error: {e}")
            return {
                "is_financial_data": False,
                "error": str(e),
                "parsing_method": "Luna_AI"
            }
    
    def _is_financial_message(self, message: str) -> bool:
        """Check if message contains financial keywords"""
        financial_keywords = [
            # Transaction keywords
            'beli', 'bayar', 'buat', 'dapat', 'terima', 'keluar', 'masuk',
            'spend', 'spending', 'pengeluaran', 'pemasukan', 'income',
            
            # Amount keywords
            'ribu', 'rb', 'juta', 'jt', 'rp', 'rupiah', 'duit', 'uang',
            
            # Category keywords
            'makan', 'transport', 'kos', 'buku', 'jajan', 'bensin', 'pulsa',
            
            # Savings keywords
            'nabung', 'tabung', 'saving', 'target', 'goal', 'beli',
            
            # Budget keywords
            'budget', 'anggaran', 'limit', 'batas', 'sisa', 'habis'
        ]
        
        message_lower = message.lower()
        for keyword in financial_keywords:
            if keyword in message_lower:
                return True
        
        # Check for currency patterns
        currency_patterns = [
            r'\d+\s*(ribu|rb|juta|jt)',
            r'rp\s*\d+',
            r'\d+\s*k',
            r'\d{1,3}(\.\d{3})*'
        ]
        
        for pattern in currency_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def _parse_transaction(self, message: str) -> Optional[ParsedFinancialData]:
        """Parse transaction from message"""
        try:
            # Extract amount
            amount = self._extract_amount(message)
            if not amount:
                return None
            
            # Determine transaction type
            transaction_type = self._determine_transaction_type(message)
            if not transaction_type:
                return None
            
            # Extract category
            category = self._extract_category(message, transaction_type)
            if not category:
                category = "Lainnya"
            
            # Extract description
            description = self._extract_description(message, amount, category)
            
            # Calculate confidence
            confidence = self._calculate_confidence(message, amount, category, transaction_type)
            
            return ParsedFinancialData(
                data_type="transaction",
                transaction_type=transaction_type,
                amount=amount,
                category=category,
                description=description,
                confidence=confidence,
                original_text=message
            )
            
        except Exception as e:
            logger.error(f"❌ Error parsing transaction: {e}")
            return None
    
    def _parse_savings_goal(self, message: str) -> Optional[ParsedFinancialData]:
        """Parse savings goal from message"""
        try:
            # Look for savings goal keywords
            savings_keywords = ['nabung', 'tabung', 'saving', 'target', 'pengen beli', 'mau beli']
            has_savings_keyword = any(keyword in message.lower() for keyword in savings_keywords)
            
            if not has_savings_keyword:
                return None
            
            # Extract target amount
            amount = self._extract_amount(message)
            if not amount:
                return None
            
            # Extract item name
            item_name = self._extract_item_name(message)
            if not item_name:
                item_name = "Item tidak disebutkan"
            
            # Extract target date
            target_date = self._extract_target_date(message)
            
            # Extract description
            description = f"Target menabung untuk {item_name}"
            
            confidence = 0.8 if item_name != "Item tidak disebutkan" else 0.6
            
            return ParsedFinancialData(
                data_type="savings_goal",
                amount=amount,
                target_amount=amount,
                item_name=item_name,
                target_date=target_date,
                description=description,
                confidence=confidence,
                original_text=message
            )
            
        except Exception as e:
            logger.error(f"❌ Error parsing savings goal: {e}")
            return None
    
    def _parse_budget_inquiry(self, message: str) -> Optional[ParsedFinancialData]:
        """Parse budget inquiry from message"""
        try:
            budget_keywords = ['budget', 'anggaran', 'sisa', 'limit', 'batas', 'habis', 'cukup']
            has_budget_keyword = any(keyword in message.lower() for keyword in budget_keywords)
            
            if not has_budget_keyword:
                return None
            
            return ParsedFinancialData(
                data_type="budget_inquiry",
                description="Pertanyaan tentang budget",
                confidence=0.7,
                original_text=message
            )
            
        except Exception as e:
            logger.error(f"❌ Error parsing budget inquiry: {e}")
            return None
    
    def _extract_amount(self, message: str) -> Optional[float]:
        """Extract amount from message"""
        try:
            message_lower = message.lower()
            
            # Pattern untuk jumlah uang
            patterns = [
                # Format: 50 ribu, 2 juta
                r'(\d+(?:\.\d+)?)\s*(ribu|rb)',
                r'(\d+(?:\.\d+)?)\s*(juta|jt)',
                
                # Format: Rp 50000
                r'rp\s*(\d+(?:\.\d{3})*)',
                
                # Format: 50k
                r'(\d+)\s*k(?!\w)',
                
                # Format: angka biasa dengan titik pemisah ribuan
                r'(\d{1,3}(?:\.\d{3})+)',
                
                # Format: angka biasa
                r'(\d+)'
            ]
            
            for i, pattern in enumerate(patterns):
                matches = re.findall(pattern, message_lower)
                for match in matches:
                    if isinstance(match, tuple):
                        if len(match) == 2:  # Amount with unit
                            amount_str, unit = match
                            amount = float(amount_str)
                            
                            if unit in ['ribu', 'rb']:
                                amount *= 1000
                            elif unit in ['juta', 'jt']:
                                amount *= 1000000
                        else:
                            amount = float(match[0])
                    else:
                        amount = float(match)
                    
                    # Handle special cases
                    if i == 2:  # Rp format
                        amount_str = match.replace('.', '')
                        amount = float(amount_str)
                    elif i == 3:  # k format
                        amount *= 1000
                    elif i == 4:  # dotted format
                        amount_str = match.replace('.', '')
                        amount = float(amount_str)
                    
                    # Validate amount (should be reasonable)
                    if 100 <= amount <= 100000000:  # 100 rupiah to 100 juta
                        return amount
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting amount: {e}")
            return None
    
    def _determine_transaction_type(self, message: str) -> Optional[str]:
        """Determine if transaction is income or expense"""
        message_lower = message.lower()
        
        # Income keywords
        income_keywords = [
            'dapat', 'terima', 'masuk', 'gaji', 'kiriman', 'bonus', 
            'hadiah', 'jual', 'income', 'pemasukan', 'dapet'
        ]
        
        # Expense keywords
        expense_keywords = [
            'beli', 'bayar', 'buat', 'keluar', 'spend', 'pengeluaran',
            'shopping', 'belanja', 'makan', 'transport', 'kos'
        ]
        
        # Check for income keywords
        for keyword in income_keywords:
            if keyword in message_lower:
                return "income"
        
        # Check for expense keywords
        for keyword in expense_keywords:
            if keyword in message_lower:
                return "expense"
        
        # Default to expense if amount is mentioned without clear indication
        return "expense"
    
    def _extract_category(self, message: str, transaction_type: str) -> str:
        """Extract category from message"""
        message_lower = message.lower()
        
        if transaction_type == "income":
            # Income categories
            income_patterns = {
                "Uang Saku/Kiriman Ortu": ['uang saku', 'kiriman', 'ortu', 'orang tua', 'mama', 'papa'],
                "Part-time Job": ['kerja', 'job', 'part time', 'freelance', 'project'],
                "Beasiswa": ['beasiswa', 'scholarship'],
                "Hadiah/Bonus": ['hadiah', 'bonus', 'gift', 'dapat'],
                "Lainnya": []
            }
        else:
            # Expense categories - use Indonesian Student Categories
            expense_patterns = {
                # NEEDS (50%)
                "Makanan Pokok": ['makan', 'makanan', 'nasi', 'lauk', 'sarapan', 'minum', 'groceries'],
                "Kos/Tempat Tinggal": ['kos', 'kost', 'sewa', 'listrik', 'air', 'tempat tinggal'],
                "Transportasi Wajib": ['transport', 'transportasi', 'angkot', 'bus', 'ojek', 'bensin', 'parkir'],
                "Pendidikan": ['buku', 'alat tulis', 'print', 'fotocopy', 'ukt', 'spp', 'kuliah'],
                "Internet & Komunikasi": ['internet', 'wifi', 'pulsa', 'kuota', 'paket data'],
                "Kesehatan & Kebersihan": ['obat', 'dokter', 'shampo', 'sabun', 'pasta gigi'],
                
                # WANTS (30%)
                "Hiburan & Sosial": ['nongkrong', 'cinema', 'game', 'hiburan', 'main'],
                "Jajan & Snack": ['jajan', 'snack', 'es', 'kopi', 'teh', 'cemilan'],
                "Pakaian & Aksesoris": ['baju', 'celana', 'sepatu', 'tas', 'jaket'],
                "Organisasi & Event": ['ukm', 'organisasi', 'event', 'acara'],
                
                # SAVINGS (20%)
                "Tabungan Umum": ['tabung', 'nabung', 'saving', 'simpan'],
                
                # Default
                "Lainnya": []
            }
        
        # Find matching category
        categories = income_patterns if transaction_type == "income" else expense_patterns
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return category
        
        return "Lainnya"
    
    def _extract_description(self, message: str, amount: float, category: str) -> str:
        """Extract or generate description"""
        # Clean message for description
        clean_message = message.strip()
        
        # Remove common prefixes
        prefixes_to_remove = ['luna', 'hai', 'halo', 'aku', 'saya', 'tadi', 'barusan']
        words = clean_message.lower().split()
        filtered_words = [word for word in words if word not in prefixes_to_remove]
        
        if len(filtered_words) > 0:
            description = ' '.join(filtered_words[:10])  # Max 10 words
            return description.capitalize()
        
        # Generate description based on category and amount
        amount_str = f"{amount:,.0f}".replace(',', '.')
        return f"{category} sebesar Rp {amount_str}"
    
    def _extract_item_name(self, message: str) -> str:
        """Extract item name for savings goal"""
        message_lower = message.lower()
        
        # Common items students save for
        items_patterns = {
            "Laptop": ['laptop', 'notebook', 'macbook'],
            "Handphone": ['hp', 'handphone', 'smartphone', 'iphone', 'android'],
            "Motor": ['motor', 'sepeda motor', 'motorcycle'],
            "Kamera": ['kamera', 'camera', 'dslr'],
            "Sepatu": ['sepatu', 'shoes', 'sneakers'],
            "Tas": ['tas', 'bag', 'backpack'],
            "Pakaian": ['baju', 'jaket', 'celana'],
            "Liburan": ['liburan', 'vacation', 'trip', 'jalan-jalan'],
        }
        
        for item, keywords in items_patterns.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return item
        
        # Try to extract after "beli" or "untuk"
        patterns = [
            r'(?:beli|untuk)\s+(\w+(?:\s+\w+)*)',
            r'nabung\s+(?:buat|untuk)\s+(\w+(?:\s+\w+)*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                return match.group(1).title()
        
        return "Item yang diinginkan"
    
    def _extract_target_date(self, message: str) -> Optional[datetime]:
        """Extract target date from message"""
        try:
            message_lower = message.lower()
            
            # Patterns for dates
            patterns = [
                r'(\d{1,2})\s+bulan',  # "3 bulan"
                r'bulan\s+(\w+)',      # "bulan depan"
                r'tahun\s+depan',      # "tahun depan"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    if 'bulan' in pattern:
                        if match.group(1).isdigit():
                            months = int(match.group(1))
                            return datetime.now() + timedelta(days=months * 30)
                        elif 'depan' in match.group(1):
                            return datetime.now() + timedelta(days=30)
                    elif 'tahun depan' in message_lower:
                        return datetime.now() + timedelta(days=365)
            
            # Default target: 6 months from now
            return datetime.now() + timedelta(days=180)
            
        except Exception as e:
            logger.error(f"❌ Error extracting target date: {e}")
            return None
    
    def _calculate_confidence(self, message: str, amount: float, category: str, transaction_type: str) -> float:
        """Calculate confidence score"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for clear amount
        if amount:
            confidence += 0.2
        
        # Boost confidence for specific category
        if category != "Lainnya":
            confidence += 0.2
        
        # Boost confidence for clear transaction type keywords
        message_lower = message.lower()
        clear_keywords = ['beli', 'bayar', 'dapat', 'terima', 'makan', 'transport']
        for keyword in clear_keywords:
            if keyword in message_lower:
                confidence += 0.1
                break
        
        return min(confidence, 1.0)
    
    def _format_response(self, parsed_data: ParsedFinancialData) -> Dict[str, Any]:
        """Format parsed data to response format"""
        response = {
            "is_financial_data": True,
            "confidence": parsed_data.confidence,
            "data_type": parsed_data.data_type,
            "parsing_method": "Luna_AI",
            "original_message": parsed_data.original_text
        }
        
        if parsed_data.data_type == "transaction":
            response["parsed_data"] = {
                "type": parsed_data.transaction_type,
                "amount": parsed_data.amount,
                "category": parsed_data.category,
                "description": parsed_data.description,
                "date": datetime.now().isoformat()
            }
            
            # Add budget type classification
            budget_type = self._get_budget_type(parsed_data.category)
            response["parsed_data"]["budget_type"] = budget_type
            
        elif parsed_data.data_type == "savings_goal":
            response["parsed_data"] = {
                "item_name": parsed_data.item_name,
                "target_amount": parsed_data.target_amount,
                "description": parsed_data.description,
                "target_date": parsed_data.target_date.isoformat() if parsed_data.target_date else None
            }
            
        elif parsed_data.data_type == "budget_inquiry":
            response["parsed_data"] = {
                "inquiry_type": "budget_status",
                "description": parsed_data.description
            }
        
        return response
    
    def _get_budget_type(self, category: str) -> str:
        """Get budget type for category"""
        try:
            return IndonesianStudentCategories.get_budget_type(category)
        except:
            return "wants"  # Default to wants
    
    def get_financial_advice(self, parsed_data: Dict[str, Any]) -> str:
        """Generate financial advice based on parsed data"""
        try:
            if not parsed_data.get("is_financial_data"):
                return "Saya tidak bisa memberikan saran keuangan untuk pesan ini."
            
            data_type = parsed_data.get("data_type")
            parsed_info = parsed_data.get("parsed_data", {})
            
            if data_type == "transaction":
                return self._generate_transaction_advice(parsed_info)
            elif data_type == "savings_goal":
                return self._generate_savings_advice(parsed_info)
            elif data_type == "budget_inquiry":
                return self._generate_budget_advice()
            
            return "Terima kasih sudah berbagi informasi keuangan!"
            
        except Exception as e:
            logger.error(f"❌ Error generating advice: {e}")
            return "Saya akan membantu menganalisis keuangan Anda dengan lebih baik."
    
    def _generate_transaction_advice(self, transaction_data: Dict[str, Any]) -> str:
        """Generate advice for transaction"""
        trans_type = transaction_data.get("type", "")
        amount = transaction_data.get("amount", 0)
        category = transaction_data.get("category", "")
        budget_type = transaction_data.get("budget_type", "wants")
        
        if trans_type == "income":
            return f"💰 Bagus! Pemasukan dari {category} sebesar {self._format_currency(amount)}. Ingat untuk mengalokasikan dengan metode 50/30/20 ya!"
        
        elif trans_type == "expense":
            if budget_type == "needs":
                return f"🏠 Pengeluaran NEEDS untuk {category} sebesar {self._format_currency(amount)}. Ini termasuk kebutuhan pokok, pastikan tidak melebihi 50% budget bulanan."
            elif budget_type == "wants":
                return f"🎯 Pengeluaran WANTS untuk {category} sebesar {self._format_currency(amount)}. Pastikan total WANTS tidak melebihi 30% budget bulanan ya!"
            else:  # savings
                return f"💎 Bagus! Anda menabung untuk {category} sebesar {self._format_currency(amount)}. Terus konsisten dengan target 20% untuk savings!"
        
        return "Transaksi telah dicatat. Jaga keseimbangan budget 50/30/20!"
    
    def _generate_savings_advice(self, goal_data: Dict[str, Any]) -> str:
        """Generate advice for savings goal"""
        item_name = goal_data.get("item_name", "")
        target_amount = goal_data.get("target_amount", 0)
        
        # Calculate monthly savings needed (assuming 6 months)
        monthly_needed = target_amount / 6
        
        return f"🎯 Target menabung untuk {item_name} sebesar {self._format_currency(target_amount)} tercatat! " \
               f"Jika ingin tercapai dalam 6 bulan, Anda perlu menabung sekitar {self._format_currency(monthly_needed)} per bulan dari budget WANTS (30%)."
    
    def _generate_budget_advice(self) -> str:
        """Generate general budget advice"""
        return "📊 Untuk mengecek status budget, gunakan metode 50/30/20:\n" \
               "• 50% untuk NEEDS (kebutuhan pokok)\n" \
               "• 30% untuk WANTS (keinginan & target tabungan)\n" \
               "• 20% untuk SAVINGS (tabungan masa depan)"
    
    def _format_currency(self, amount: float) -> str:
        """Format currency"""
        return f"Rp {amount:,.0f}".replace(',', '.')

# Singleton instance
luna_finance_parser = LunaAIFinanceParser()

def parse_financial_message(message: str) -> Dict[str, Any]:
    """Global function to parse financial message"""
    return luna_finance_parser.parse_financial_message(message)

def get_financial_advice(parsed_data: Dict[str, Any]) -> str:
    """Global function to get financial advice"""
    return luna_finance_parser.get_financial_advice(parsed_data)