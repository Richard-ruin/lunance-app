# app/services/indoroberta_financial_parser.py - FIXED MODEL PATH
import re
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndoRoBERTaFinancialParser:
    """
    FIXED: Enhanced Financial Parser dengan proper model path detection
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize parser dengan automatic model detection
        """
        # FIXED: Automatic model path detection
        if model_path is None:
            model_path = self._find_trained_models()
        
        self.model_path = model_path
        self.models_loaded = False
        
        # CRITICAL: Initialize rule-based components ALWAYS
        self._init_rule_based_parser()
        
        # Try to load trained models
        if model_path and os.path.exists(model_path):
            try:
                logger.info(f"🔍 Found trained models at: {model_path}")
                self._load_models()
            except Exception as e:
                logger.error(f"❌ Failed to load trained models: {e}")
                logger.info("📋 Falling back to enhanced rule-based parser")
        else:
            logger.warning(f"⚠️ No trained models found. Using enhanced rule-based parser")
    
    def _find_trained_models(self) -> Optional[str]:
        """FIXED: Find trained models in multiple possible locations"""
        
        # Get current file directory
        current_dir = Path(__file__).parent
        
        # Possible model locations
        possible_paths = [
            # In models folder at project root
            current_dir.parent.parent / "models" / "indoroberta-financial-enhanced",
            current_dir.parent.parent / "models" / "indoroberta-financial",
            # In lunance_backend/models
            current_dir.parent.parent / "backend" / "models" / "indoroberta-financial-enhanced", 
            current_dir.parent.parent / "backend" / "models" / "indoroberta-financial",
            # Relative to backend folder
            current_dir.parent.parent / "backend" / "models" / "indoroberta-financial-enhanced",
            current_dir.parent.parent / "backend" / "models" / "indoroberta-financial",
            # Direct models folder
            Path("models") / "indoroberta-financial-enhanced",
            Path("models") / "indoroberta-financial",
            # Absolute paths (customize for your system)
            Path("D:/kuliah/semester 6/Tugas Akhir/aplikasi/maybe/lunance/backend/models/indoroberta-financial-enhanced"),
            Path("D:/kuliah/semester 6/Tugas Akhir/aplikasi/maybe/lunance/backend/models/indoroberta-financial"),
        ]
        
        for path in possible_paths:
            if path.exists():
                # Check if it has the required subdirectories
                intent_path = path / "intent_classifier"
                category_path = path / "category_classifier"
                
                if intent_path.exists() and category_path.exists():
                    logger.info(f"✅ Found complete trained models at: {path}")
                    return str(path)
                else:
                    logger.info(f"📂 Found models folder but incomplete: {path}")
        
        logger.warning("❌ No trained models found in any expected location")
        return None
    
    def _load_models(self):
        """Load fine-tuned IndoBERT models"""
        try:
            # Check if we have transformers installed
            import torch
            from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
            
            # Model paths
            intent_model_path = os.path.join(self.model_path, "intent_classifier")
            category_model_path = os.path.join(self.model_path, "category_classifier")
            
            logger.info(f"📦 Loading intent model from: {intent_model_path}")
            logger.info(f"📦 Loading category model from: {category_model_path}")
            
            # Load intent classifier
            self.intent_tokenizer = AutoTokenizer.from_pretrained(intent_model_path)
            self.intent_model = AutoModelForSequenceClassification.from_pretrained(intent_model_path)
            
            # Load category classifier
            self.category_tokenizer = AutoTokenizer.from_pretrained(category_model_path)
            self.category_model = AutoModelForSequenceClassification.from_pretrained(category_model_path)
            
            # Create pipelines
            self.intent_pipeline = pipeline(
                "text-classification",
                model=self.intent_model,
                tokenizer=self.intent_tokenizer,
                top_k=None
            )
            
            self.category_pipeline = pipeline(
                "text-classification",
                model=self.category_model,
                tokenizer=self.category_tokenizer,
                top_k=None
            )
            
            self.models_loaded = True
            logger.info("✅ IndoBERT models loaded successfully!")
            logger.info(f"🎯 Intent model ready with {len(self.intent_model.config.id2label)} labels")
            logger.info(f"🏷️ Category model ready with {len(self.category_model.config.id2label)} labels")
            
        except ImportError as e:
            logger.error(f"❌ Transformers library not available: {e}")
            logger.info("💡 Install with: pip install transformers torch")
            raise
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            raise
    
    def _init_rule_based_parser(self):
        """Initialize ENHANCED rule-based parser dengan keywords yang lebih lengkap"""
        
        # FIXED: Enhanced keywords untuk mahasiswa Indonesia
        self.income_keywords = [
            'dapat', 'terima', 'kiriman', 'uang saku', 'gaji', 'bayaran', 'dibayar',
            'transfer masuk', 'beasiswa', 'hadiah', 'bonus', 'menang', 'juara',
            'freelance', 'project', 'ngajar', 'les', 'jual', 'jualan', 'untung',
            'dapet', 'cair', 'masuk', 'income', 'penghasilan', 'honor'
        ]
        
        # FIXED: Enhanced expense keywords termasuk "uang kos"
        self.expense_keywords = [
            'bayar', 'beli', 'belanja', 'buat', 'keluar', 'habis', 'spend',
            'ongkos', 'biaya', 'sewa', 'cicilan', 'transfer ke', 'kirim',
            'makan', 'minum', 'jajan', 'transport', 'ojol', 'grab', 'gojek',
            # CRITICAL: Add "uang kos" patterns
            'uang kos', 'uang kostan', 'kos', 'kostan', 'kost', 'sewa kos',
            'bayar kos', 'biaya kos', 'uang tempat tinggal', 'sewa kamar',
            'abis', 'keluar duit', 'pengeluaran', 'expense', 'boros'
        ]
        
        self.savings_keywords = [
            'nabung', 'tabung', 'target', 'ingin beli', 'mau beli', 'pengen beli',
            'kepengen', 'impian', 'rencana beli', 'saving', 'goal', 'tujuan'
        ]
        
        # CRITICAL: Enhanced money patterns
        self.money_patterns = [
            # Pattern untuk X juta (prioritas tertinggi)
            r'(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:juta|jt|m)(?!\w)',
            # Pattern untuk X ribu
            r'(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:ribu|rb|k)(?!\w)',
            # Pattern untuk X miliar
            r'(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:miliar|milyar|b)(?!\w)',
            # Pattern untuk angka dengan format Indonesia (1.000.000)
            r'(?:rp\.?\s*)?(\d{1,3}(?:\.\d{3})+)(?!\d)',
            # Pattern untuk angka biasa (minimal 3 digit untuk avoid false positive)
            r'(?:rp\.?\s*)?(\d{3,})(?!\d)',
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
        
        # Enhanced categories
        self._init_categories()
        
        logger.info("✅ Enhanced rule-based parser initialized with 'uang kos' support")
    
    def _init_categories(self):
        """Initialize financial categories mapping"""
        # 50/30/20 Budget Type Mapping
        self.budget_types = {
            "needs": {
                "percentage": 50,
                "categories": [
                    "Makanan Pokok", "Kos/Tempat Tinggal", "Transportasi Wajib",
                    "Pendidikan", "Internet & Komunikasi", "Kesehatan & Kebersihan"
                ]
            },
            "wants": {
                "percentage": 30,
                "categories": [
                    "Hiburan & Sosial", "Jajan & Snack", "Pakaian & Aksesoris",
                    "Organisasi & Event", "Target Tabungan Barang", "Lainnya (Wants)"
                ]
            },
            "savings": {
                "percentage": 20,
                "categories": [
                    "Tabungan Umum", "Dana Darurat", "Investasi Masa Depan",
                    "Tabungan Jangka Panjang"
                ]
            },
            "income": {
                "categories": [
                    "Uang Saku/Kiriman Ortu", "Part-time Job", "Freelance/Project",
                    "Beasiswa", "Hadiah/Bonus", "Lainnya"
                ]
            }
        }
        
        # FIXED: Enhanced category keywords dengan "uang kos"
        self.category_keywords = {
            # NEEDS
            "Makanan Pokok": ["makan", "nasi", "lauk", "sayur", "buah", "groceries", "beras"],
            "Kos/Tempat Tinggal": [
                "kos", "kost", "kostan", "sewa", "kontrakan", "listrik", "air",
                "uang kos", "uang kostan", "bayar kos", "biaya kos", "sewa kos",
                "tempat tinggal", "sewa kamar", "boarding house", "mess"
            ],
            "Transportasi Wajib": ["transport", "angkot", "bus", "kereta", "ojol", "bensin"],
            "Pendidikan": ["buku", "alat tulis", "fotocopy", "print", "ukt", "spp"],
            
            # WANTS
            "Hiburan & Sosial": ["nonton", "bioskop", "game", "netflix", "hangout"],
            "Jajan & Snack": ["jajan", "snack", "es", "kopi", "bubble tea", "martabak"],
            "Pakaian & Aksesoris": ["baju", "celana", "sepatu", "sandal", "tas"],
            
            # SAVINGS
            "Tabungan Umum": ["tabungan", "saving", "simpan", "deposito"],
            "Dana Darurat": ["dana darurat", "emergency", "darurat", "cadangan"],
            
            # INCOME
            "Uang Saku/Kiriman Ortu": ["uang saku", "kiriman", "ortu", "mama", "papa"],
            "Part-time Job": ["part time", "kerja", "jual", "jualan", "ojol"],
            "Freelance/Project": ["freelance", "project", "tugas", "design", "coding"],
            "Beasiswa": ["beasiswa", "scholarship", "bidikmisi", "pip"],
        }
    
    # ==========================================
    # MAIN PARSING METHODS
    # ==========================================
    
    def parse_amount(self, text: str) -> Optional[float]:
        """FIXED: Parse jumlah uang dengan akurasi tinggi"""
        if not text:
            return None
            
        text_lower = text.lower().strip()
        
        # Coba setiap pattern dengan urutan prioritas
        for pattern in self.money_patterns:
            matches = re.finditer(pattern, text_lower)
            
            for match in matches:
                amount_str = match.group(1)
                original_match = match.group(0)
                
                try:
                    # Clean amount string
                    cleaned_amount = amount_str.replace(',', '.')
                    amount = float(cleaned_amount)
                    
                    # Apply multiplier based on unit in original match
                    final_amount = amount
                    
                    if any(unit in original_match for unit in ['juta', 'jt']):
                        final_amount = amount * 1000000
                    elif any(unit in original_match for unit in ['ribu', 'rb', 'k']):
                        final_amount = amount * 1000
                    elif any(unit in original_match for unit in ['miliar', 'milyar', 'b']):
                        final_amount = amount * 1000000000
                    else:
                        # Check if it's already a large number (format Indonesia)
                        if '.' in amount_str and len(amount_str.replace('.', '')) > 4:
                            # Likely Indonesian format (1.500.000)
                            cleaned_amount = amount_str.replace('.', '')
                            final_amount = float(cleaned_amount)
                    
                    return final_amount
                    
                except ValueError:
                    continue
        
        return None
    
    def detect_transaction_type(self, text: str) -> Optional[str]:
        """FIXED: Deteksi tipe transaksi dengan enhanced logic"""
        if self.models_loaded:
            logger.info(f"🤖 Using ML model for transaction detection: '{text}'")
            return self._detect_transaction_type_ml(text)
        else:
            logger.info(f"📋 Using rule-based transaction detection: '{text}'")
            return self._detect_transaction_type_rule(text)
    
    def _detect_transaction_type_ml(self, text: str) -> Optional[str]:
        """Deteksi menggunakan ML model"""
        try:
            result = self.intent_pipeline(text)
            
            # Get highest score prediction
            best_prediction = max(result, key=lambda x: x['score'])
            
            logger.info(f"🎯 ML prediction: {best_prediction['label']} (confidence: {best_prediction['score']:.3f})")
            
            if best_prediction['score'] > 0.7:  # Confidence threshold
                label = best_prediction['label'].lower()
                
                if label in ['income', 'expense', 'savings_goal']:
                    return label
            
            # Fallback to rule-based
            logger.info("🔄 ML confidence too low, falling back to rule-based")
            return self._detect_transaction_type_rule(text)
            
        except Exception as e:
            logger.error(f"❌ ML detection failed: {e}")
            return self._detect_transaction_type_rule(text)
    
    def _detect_transaction_type_rule(self, text: str) -> Optional[str]:
        """FIXED: Enhanced rule-based detection"""
        text_lower = text.lower()
        
        # Check for savings goal keywords first (highest priority)
        if any(keyword in text_lower for keyword in self.savings_keywords):
            return "savings_goal"
        
        # Enhanced checking for income
        income_score = 0
        for keyword in self.income_keywords:
            if keyword in text_lower:
                income_score += 1
        
        # Enhanced checking for expense (including "uang kos")
        expense_score = 0
        for keyword in self.expense_keywords:
            if keyword in text_lower:
                expense_score += 1
                # Give extra weight to "uang kos" patterns
                if 'uang kos' in keyword and keyword in text_lower:
                    expense_score += 2  # Extra weight
        
        logger.info(f"📊 Score - Income: {income_score}, Expense: {expense_score}")
        
        if income_score > expense_score:
            return "income"
        elif expense_score > income_score:
            return "expense"
        
        return None
    
    def parse_financial_data(self, text: str, monthly_income: float = None) -> Dict[str, Any]:
        """MAIN parsing method dengan enhanced support"""
        try:
            if self.models_loaded:
                logger.info(f"🤖 Parsing with ML models: '{text}'")
            else:
                logger.info(f"📋 Parsing with rules: '{text}'")
            
            # Step 1: Detect transaction type
            transaction_type = self.detect_transaction_type(text)
            
            if not transaction_type:
                return {
                    "is_financial_data": False,
                    "confidence": 0.0,
                    "message": "Bukan data keuangan"
                }
            
            # Step 2: Extract amount
            amount = self.parse_amount(text)
            
            if not amount:
                return {
                    "is_financial_data": False,
                    "confidence": 0.0,
                    "message": "Tidak dapat mendeteksi jumlah uang"
                }
            
            # Step 3: Process based on transaction type
            if transaction_type in ["income", "expense"]:
                category, budget_type = self._extract_category_with_budget_type(text, transaction_type)
                description = self._extract_description(text, amount)
                
                parsed_data = {
                    "type": transaction_type,
                    "amount": amount,
                    "category": category,
                    "budget_type": budget_type if transaction_type == "expense" else None,
                    "description": description,
                    "date": datetime.now()
                }
                
                return {
                    "is_financial_data": True,
                    "confidence": 0.9,
                    "data_type": transaction_type,
                    "parsed_data": parsed_data,
                    "parsing_method": "IndoRoBERTa_ML" if self.models_loaded else "IndoRoBERTa_Rules"
                }
            
            elif transaction_type == "savings_goal":
                target_date = self.parse_target_date(text)
                item_name = self._extract_item_name(text, amount)
                
                parsed_data = {
                    "item_name": item_name,
                    "target_amount": amount,
                    "target_date": target_date,
                    "description": f"Target tabungan: {text[:100]}"
                }
                
                return {
                    "is_financial_data": True,
                    "confidence": 0.9,
                    "data_type": transaction_type,
                    "parsed_data": parsed_data,
                    "parsing_method": "IndoRoBERTa_ML" if self.models_loaded else "IndoRoBERTa_Rules"
                }
            
        except Exception as e:
            logger.error(f"❌ Error parsing financial data: {e}")
            return {
                "is_financial_data": False,
                "confidence": 0.0,
                "error": str(e)
            }
    
    # ==========================================
    # HELPER METHODS (rest of the methods remain same)
    # ==========================================
    
    def parse_target_date(self, text: str) -> Optional[datetime]:
        """Parse tanggal target dari teks"""
        text_lower = text.lower()
        
        for pattern in self.date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    groups = match.groups()
                    
                    if len(groups) == 3:
                        if groups[1].isdigit():
                            # Numeric format
                            day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                        else:
                            # Text format
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
                            return datetime(year, month, 1)
                    
                    elif len(groups) == 1:
                        # Format: dalam 6 bulan / dalam 2 tahun
                        now = datetime.now()
                        if 'bulan' in text_lower:
                            months = int(groups[0])
                            return now + timedelta(days=months * 30)
                        elif 'tahun' in text_lower:
                            years = int(groups[0])
                            return now.replace(year=now.year + years)
                
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _extract_category_with_budget_type(self, text: str, transaction_type: str) -> Tuple[str, str]:
        """Extract kategori dan budget type"""
        if transaction_type == "income":
            category = self._extract_income_category(text)
            return category, "income"
        else:
            category = self._extract_expense_category(text)
            budget_type = self._get_budget_type_from_category(category)
            return category, budget_type
    
    def _extract_income_category(self, text: str) -> str:
        """Extract income category"""
        text_lower = text.lower()
        
        for category, keywords in self.category_keywords.items():
            if any(budget_type in self.budget_types["income"]["categories"] for budget_type in [category]):
                if any(keyword in text_lower for keyword in keywords):
                    return category
        
        return "Lainnya"
    
    def _extract_expense_category(self, text: str) -> str:
        """FIXED: Extract expense category dengan enhanced detection"""
        text_lower = text.lower()
        
        # Check all expense categories with priority
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Special handling for "uang kos" 
                    if 'uang kos' in keyword and 'uang kos' in text_lower:
                        return "Kos/Tempat Tinggal"
                    elif keyword in text_lower:
                        return category
        
        return "Lainnya (Wants)"
    
    def _get_budget_type_from_category(self, category: str) -> str:
        """Get budget type from category"""
        for budget_type, info in self.budget_types.items():
            if budget_type in ["needs", "wants", "savings"]:
                if category in info["categories"]:
                    return budget_type
        
        return "wants"  # Default
    
    def _extract_description(self, text: str, amount: float) -> str:
        """Extract description from text"""
        # Remove amount patterns
        clean_text = text
        for pattern in self.money_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # Clean up
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text[:100] if clean_text else "Transaksi melalui chat"
    
    def _extract_item_name(self, text: str, amount: float) -> str:
        """Extract item name for savings goal"""
        # Remove amount and savings keywords
        clean_text = text.lower()
        
        # Remove money patterns
        for pattern in self.money_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # Remove savings keywords
        for keyword in self.savings_keywords:
            clean_text = clean_text.replace(keyword, '')
        
        # Clean up
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        if len(clean_text) > 2:
            return clean_text.title()[:50]
        else:
            return "Target Tabungan"
    
    def format_currency(self, amount: float) -> str:
        """Format currency to Rupiah"""
        return f"Rp {amount:,.0f}".replace(',', '.')

    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status for debugging"""
        return {
            "models_loaded": self.models_loaded,
            "model_path": self.model_path,
            "model_path_exists": os.path.exists(self.model_path) if self.model_path else False,
            "intent_model_path": os.path.join(self.model_path, "intent_classifier") if self.model_path else None,
            "category_model_path": os.path.join(self.model_path, "category_classifier") if self.model_path else None,
            "intent_model_exists": os.path.exists(os.path.join(self.model_path, "intent_classifier")) if self.model_path else False,
            "category_model_exists": os.path.exists(os.path.join(self.model_path, "category_classifier")) if self.model_path else False,
            "parsing_method": "IndoRoBERTa_ML" if self.models_loaded else "IndoRoBERTa_Rules"
        }