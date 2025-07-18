# app/services/enhanced_financial_parser.py - FIXED VERSION dengan amount parsing yang akurat
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from ..services.financial_categories import IndonesianStudentCategories

class EnhancedFinancialParser:
    """Enhanced parser untuk mengekstrak data keuangan dari pesan chat mahasiswa Indonesia dengan metode 50/30/20"""
    
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
        
        # FIXED: Pattern untuk mendeteksi jumlah uang dengan akurasi tinggi
        self.money_patterns = [
            # Pattern untuk X juta (prioritas tertinggi)
            r'(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:juta|jt|m)(?!\w)',
            # Pattern untuk X ribu
            r'(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:ribu|rb|k)(?!\w)',
            # Pattern untuk X miliar
            r'(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:miliar|milyar|b)(?!\w)',
            # Pattern untuk angka dengan format Indonesia (1.000.000)
            r'(?:rp\.?\s*)?(\d{1,3}(?:\.\d{3})+)(?!\d)',
            # Pattern untuk angka biasa
            r'(?:rp\.?\s*)?(\d+)(?!\d)',
        ]
        
        # Pattern untuk mendeteksi tanggal target
        self.date_patterns = [
            r'(?:pada\s+)?(?:tanggal\s+)?(\d{1,2})\s+(\w+)\s+(\d{4})',  # 22 januari 2026
            r'(?:pada\s+)?(?:tanggal\s+)?(\d{1,2})[-/](\d{1,2})[-/](\d{4})',  # 22/01/2026
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
        
        # Time-related words yang harus difilter dari nama barang
        self.time_filter_words = {
            'januari', 'februari', 'maret', 'april', 'mei', 'juni',
            'juli', 'agustus', 'september', 'oktober', 'november', 'desember',
            'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'agu', 'sep', 'okt', 'nov', 'des',
            'bulan', 'tahun', 'hari', 'minggu', 'lagi', 'mendatang', 'depan',
            'kemudian', 'nanti', 'besok', 'esok', 'masa', 'waktu',
            'dalam', 'pada', 'tanggal', 'sebelum', 'sesudah', 'sampai', 'hingga',
            'satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan', 'sepuluh'
        }
        
        # Budget type guidance untuk 50/30/20
        self.budget_guidance = {
            "needs": {
                "percentage": 50,
                "description": "Kebutuhan pokok yang HARUS dibayar",
                "examples": ["kos", "makan pokok", "transport kuliah", "buku"],
                "advice": "Prioritaskan kategori ini, target maksimal 50% dari pemasukan"
            },
            "wants": {
                "percentage": 30,
                "description": "Keinginan dan lifestyle yang menyenangkan",
                "examples": ["jajan", "hiburan", "baju baru", "target tabungan barang"],
                "advice": "Fleksibel tapi jangan lebih dari 30%, bisa untuk target nabung"
            },
            "savings": {
                "percentage": 20,
                "description": "Tabungan dan investasi untuk masa depan",
                "examples": ["tabungan umum", "dana darurat", "investasi"],
                "advice": "Minimal 20% untuk membangun wealth jangka panjang"
            }
        }
    
    def parse_amount(self, text: str) -> Optional[float]:
        """FIXED: Parse jumlah uang dengan akurasi tinggi"""
        if not text:
            return None
            
        text_lower = text.lower().strip()
        print(f"🔍 Parsing amount from: '{text_lower}'")
        
        # Coba setiap pattern dengan urutan prioritas
        for i, pattern in enumerate(self.money_patterns):
            matches = re.finditer(pattern, text_lower)
            
            for match in matches:
                amount_str = match.group(1)
                original_match = match.group(0)
                
                print(f"  Pattern {i+1}: Found '{original_match}' -> amount_str: '{amount_str}'")
                
                try:
                    # Clean amount string
                    cleaned_amount = amount_str.replace(',', '.')
                    amount = float(cleaned_amount)
                    
                    # Apply multiplier based on unit in original match
                    final_amount = amount
                    
                    if any(unit in original_match for unit in ['juta', 'jt']):
                        final_amount = amount * 1000000
                        print(f"    Applied multiplier 1,000,000: {amount} -> {final_amount}")
                    elif any(unit in original_match for unit in ['ribu', 'rb', 'k']):
                        final_amount = amount * 1000
                        print(f"    Applied multiplier 1,000: {amount} -> {final_amount}")
                    elif any(unit in original_match for unit in ['miliar', 'milyar', 'b']):
                        final_amount = amount * 1000000000
                        print(f"    Applied multiplier 1,000,000,000: {amount} -> {final_amount}")
                    else:
                        # Check if it's already a large number (format Indonesia)
                        if '.' in amount_str and len(amount_str.replace('.', '')) > 4:
                            # Likely Indonesian format (1.500.000)
                            cleaned_amount = amount_str.replace('.', '')
                            final_amount = float(cleaned_amount)
                            print(f"    Indonesian format detected: {amount_str} -> {final_amount}")
                    
                    print(f"✅ Final parsed amount: {final_amount}")
                    return final_amount
                    
                except ValueError as e:
                    print(f"    Failed to parse '{amount_str}': {e}")
                    continue
        
        print(f"❌ No amount found in: '{text_lower}'")
        return None
    
    def parse_target_date(self, text: str) -> Optional[datetime]:
        """Parse tanggal target dari teks"""
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
    
    def extract_category_with_budget_type(self, text: str, transaction_type: str) -> Tuple[str, str]:
        """
        Ekstrak kategori dan budget type menggunakan Indonesian Student Categories
        Returns: (category_name, budget_type)
        """
        if transaction_type == "income":
            category = IndonesianStudentCategories.get_income_category(text)
            return category, "income"
        else:
            # Get category with budget type for expenses (50/30/20)
            category, budget_type = IndonesianStudentCategories.get_expense_category_with_budget_type(text)
            return category, budget_type
    
    def extract_description(self, text: str, amount: float) -> str:
        """Ekstrak deskripsi dari teks"""
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
        """
        FIXED: Ekstrak nama barang untuk target tabungan dengan filter yang lebih baik
        """
        # Start with original text
        clean_text = text.lower()
        
        # 1. Remove money patterns first
        for pattern in self.money_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # 2. Remove date patterns
        if target_date:
            for pattern in self.date_patterns:
                clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # 3. Remove savings keywords and action words
        savings_action_words = [
            'nabung', 'tabung', 'target', 'ingin', 'mau', 'pengen', 'beli', 'buat',
            'kepengen', 'impian', 'rencana', 'saving', 'goal', 'tujuan', 'untuk'
        ]
        
        for word in savings_action_words:
            clean_text = re.sub(rf'\b{word}\b', '', clean_text, flags=re.IGNORECASE)
        
        # 4. Remove time-related words more aggressively
        for time_word in self.time_filter_words:
            clean_text = re.sub(rf'\b{time_word}\b', '', clean_text, flags=re.IGNORECASE)
        
        # 5. Remove numeric expressions that might indicate time
        clean_text = re.sub(r'\b\d{1,2}\b', '', clean_text)  # Remove 1-2 digit numbers
        clean_text = re.sub(r'\b\d{4}\b', '', clean_text)    # Remove years
        
        # 6. Remove common connecting words and prepositions
        connecting_words = [
            'dengan', 'dan', 'atau', 'yang', 'ini', 'itu', 'tersebut',
            'di', 'ke', 'dari', 'untuk', 'pada', 'dalam', 'oleh', 'kepada',
            'sebagai', 'seperti', 'antara', 'hingga', 'sampai', 'sejak'
        ]
        
        for word in connecting_words:
            clean_text = re.sub(rf'\b{word}\b', '', clean_text, flags=re.IGNORECASE)
        
        # 7. Clean up multiple spaces and trim
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # 8. Additional cleanup - remove remaining single characters and short words
        words = clean_text.split()
        meaningful_words = []
        
        for word in words:
            # Skip if word is too short (except common items like 'hp', 'tv', etc.)
            if len(word) < 2:
                continue
            
            # Skip if word is still a time indicator
            if word.lower() in self.time_filter_words:
                continue
            
            # Skip if word looks like a date fragment
            if re.match(r'^\d+$', word):
                continue
            
            meaningful_words.append(word)
        
        # 9. Reconstruct the item name
        final_name = ' '.join(meaningful_words)
        
        # 10. Handle edge cases
        if not final_name or len(final_name.strip()) < 2:
            # Try to extract from common item patterns
            original_lower = text.lower()
            
            # Look for common electronics/items
            item_patterns = [
                r'\b(laptop|notebook|macbook)\b',
                r'\b(hp|handphone|smartphone|iphone|samsung)\b',
                r'\b(motor|sepeda|mobil|kendaraan)\b',
                r'\b(tv|televisi|monitor)\b',
                r'\b(kulkas|mesin cuci|ac|kipas)\b',
                r'\b(sepatu|sandal|tas|baju|kemeja)\b',
                r'\b(buku|novel|komik)\b',
                r'\b(kamera|drone|headset)\b'
            ]
            
            for pattern in item_patterns:
                match = re.search(pattern, original_lower)
                if match:
                    return match.group(1).title()
            
            # Last resort - return generic name
            return "Target Tabungan"
        
        # 11. Capitalize properly and limit length
        final_name = final_name.title()
        if len(final_name) > 50:
            final_name = final_name[:47] + "..."
        
        return final_name
    
    def generate_budget_guidance(self, category: str, budget_type: str, amount: float, monthly_income: float = None) -> Dict[str, Any]:
        """Generate guidance berdasarkan budget type 50/30/20"""
        guidance = self.budget_guidance.get(budget_type, {})
        
        result = {
            "budget_type": budget_type,
            "category": category,
            "guidance": guidance,
            "amount": amount,
            "recommendations": []
        }
        
        if monthly_income and monthly_income > 0:
            budget_allocation = monthly_income * (guidance.get("percentage", 0) / 100)
            percentage_of_budget = (amount / budget_allocation * 100) if budget_allocation > 0 else 0
            
            result.update({
                "monthly_income": monthly_income,
                "budget_allocation": budget_allocation,
                "percentage_of_budget": percentage_of_budget,
                "remaining_budget": max(budget_allocation - amount, 0)
            })
            
            # Generate specific recommendations
            if budget_type == "needs":
                if percentage_of_budget > 50:
                    result["recommendations"].append("⚠️ Pengeluaran NEEDS ini cukup besar, pastikan masih dalam budget 50%")
                else:
                    result["recommendations"].append("✅ Pengeluaran NEEDS ini wajar untuk kebutuhan pokok")
            
            elif budget_type == "wants":
                if percentage_of_budget > 30:
                    result["recommendations"].append("🔍 Pertimbangkan apakah ini benar-benar perlu dari budget WANTS 30%")
                else:
                    result["recommendations"].append("💡 Pengeluaran WANTS ini OK, masih dalam batas budget 30%")
            
            elif budget_type == "savings":
                result["recommendations"].append("📈 Bagus! Ini investasi untuk masa depan dari budget SAVINGS 20%")
        
        return result
    
    def parse_financial_data(self, text: str, monthly_income: float = None) -> Dict[str, Any]:
        """Parse data keuangan dari teks chat dengan enhanced 50/30/20 guidance"""
        result = {
            "is_financial_data": False,
            "confidence": 0.0,
            "data_type": None,
            "parsed_data": None,
            "suggestions": [],
            "validation_errors": [],
            "budget_guidance": None
        }
        
        print(f"📝 Parsing financial data: '{text}'")
        
        # Detect amount first
        amount = self.parse_amount(text)
        if not amount:
            print("❌ No amount detected")
            return result
        
        print(f"💰 Amount detected: {amount}")
        
        # Detect transaction type
        data_type = self.detect_transaction_type(text)
        if not data_type:
            print("❌ No transaction type detected")
            return result
        
        print(f"📊 Transaction type: {data_type}")
        
        result["is_financial_data"] = True
        result["data_type"] = data_type
        
        if data_type in ["income", "expense"]:
            category, budget_type = self.extract_category_with_budget_type(text, data_type)
            description = self.extract_description(text, amount)
            
            result["parsed_data"] = {
                "type": data_type,
                "amount": amount,
                "category": category,
                "budget_type": budget_type,
                "description": description,
                "date": datetime.now()
            }
            
            # Generate budget guidance untuk 50/30/20
            if data_type == "expense" and monthly_income:
                result["budget_guidance"] = self.generate_budget_guidance(
                    category, budget_type, amount, monthly_income
                )
            
            # Calculate confidence based on category match
            if category != "Lainnya" and category != "Lainnya (Wants)":
                result["confidence"] = 0.9
                result["suggestions"].append(f"✅ Dikategorikan sebagai {budget_type.upper()} ({self.budget_guidance.get(budget_type, {}).get('percentage', 0)}%) - {category}")
            else:
                result["confidence"] = 0.7
                similar = IndonesianStudentCategories.suggest_similar_categories(text, budget_type)
                if similar:
                    result["suggestions"] = [f"🔍 Mungkin maksud Anda kategori: {', '.join(similar)}"]
            
            # Add budget type explanation
            if budget_type in self.budget_guidance:
                guidance = self.budget_guidance[budget_type]
                result["suggestions"].append(f"💡 {guidance['description']} - {guidance['advice']}")
            
        elif data_type == "savings_goal":
            target_date = self.parse_target_date(text)
            item_name = self.extract_item_name_for_savings(text, amount, target_date)
            description = f"Target tabungan: {text[:100]}"
            
            result["parsed_data"] = {
                "item_name": item_name,
                "target_amount": amount,
                "target_date": target_date,
                "description": description,
                "budget_source": "wants"  # Target tabungan dari wants budget (30%)
            }
            
            # Higher confidence if target date is specified
            result["confidence"] = 0.9 if target_date else 0.7
            
            # Add guidance untuk savings goals
            result["budget_guidance"] = {
                "budget_type": "wants",
                "source": "30% wants budget",
                "guidance": self.budget_guidance["wants"],
                "target_amount": amount,
                "recommendations": [
                    "🎯 Target tabungan ini akan dialokasikan dari budget WANTS (30%)",
                    "💡 Pastikan sisakan budget wants untuk hiburan dan kebutuhan lifestyle lainnya"
                ]
            }
            
            if target_date:
                result["suggestions"].append(f"📅 Target waktu: {target_date.strftime('%d %B %Y')}")
                
                # Calculate monthly saving needed if monthly income available
                if monthly_income:
                    months_remaining = max((target_date - datetime.now()).days / 30, 1)
                    monthly_needed = amount / months_remaining
                    wants_budget = monthly_income * 0.3
                    percentage_of_wants = (monthly_needed / wants_budget * 100) if wants_budget > 0 else 0
                    
                    result["budget_guidance"]["monthly_needed"] = monthly_needed
                    result["budget_guidance"]["months_remaining"] = months_remaining
                    result["budget_guidance"]["percentage_of_wants_budget"] = percentage_of_wants
                    
                    if percentage_of_wants > 50:
                        result["suggestions"].append("⚠️ Target ini butuh lebih dari 50% budget WANTS bulanan")
                    else:
                        result["suggestions"].append(f"✅ Perlu {percentage_of_wants:.1f}% dari budget WANTS bulanan")
            else:
                result["suggestions"].append("💡 Tip: Tambahkan target waktu untuk perencanaan yang lebih baik, contoh: 'pada tanggal 22 januari 2026'")
        
        print(f"✅ Parsing result: {result['data_type']} - {result['confidence']} confidence")
        return result
    
    def validate_budget_allocation(self, amount: float, budget_type: str, monthly_income: float) -> Dict[str, Any]:
        """Validasi apakah pengeluaran sesuai dengan alokasi budget 50/30/20"""
        if monthly_income <= 0:
            return {"valid": False, "message": "Monthly income tidak tersedia"}
        
        budget_percentages = {"needs": 0.5, "wants": 0.3, "savings": 0.2}
        budget_allocation = monthly_income * budget_percentages.get(budget_type, 0)
        
        percentage_used = (amount / budget_allocation * 100) if budget_allocation > 0 else 0
        
        validation = {
            "valid": True,
            "budget_type": budget_type,
            "amount": amount,
            "budget_allocation": budget_allocation,
            "percentage_used": percentage_used,
            "remaining_budget": max(budget_allocation - amount, 0),
            "status": "within_budget",
            "recommendations": []
        }
        
        if percentage_used > 100:
            validation["status"] = "over_budget"
            validation["recommendations"].append(f"🚨 Melebihi budget {budget_type.upper()} ({budget_percentages.get(budget_type, 0)*100}%)")
        elif percentage_used > 80:
            validation["status"] = "near_limit"
            validation["recommendations"].append(f"⚠️ Mendekati batas budget {budget_type.upper()}")
        else:
            validation["status"] = "within_budget"
            validation["recommendations"].append(f"✅ Masih dalam batas budget {budget_type.upper()}")
        
        return validation