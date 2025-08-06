# app/services/indoroberta_financial_parser.py - FIXED VERSION
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

class EnhancedIndoRoBERTaFinancialParser:
    """
    FIXED VERSION: Natural Language Optimized IndoRoBERTa Parser
    
    CRITICAL FIXES:
    1. ✅ Balanced natural language boost (tidak over-boost)
    2. ✅ Proper threshold adjustment untuk balance detection
    3. ✅ Improved command vs financial data disambiguation
    4. ✅ Better confidence calculation
    """
    
    def __init__(self, model_path: str = None):
        """Initialize parser with FIXED natural language support"""
        
        # CRITICAL: Automatic model path detection
        if model_path is None:
            model_path = self._find_trained_models()
        
        self.model_path = model_path
        self.models_loaded = False
        
        # Initialize natural language indicators dengan FIXED weights
        self._init_fixed_natural_language_indicators()
        
        # CRITICAL: Load ML models if available
        if model_path and os.path.exists(model_path):
            try:
                logger.info(f"🔍 Loading enhanced ML models from: {model_path}")
                self._load_models()
            except Exception as e:
                logger.error(f"❌ Failed to load ML models: {e}")
                logger.warning("📋 Falling back to enhanced rule-based parsing")
                self.models_loaded = False
        else:
            logger.warning(f"⚠️ No trained models found at {model_path}")
            logger.info("📋 Using enhanced rule-based parsing only")
            self.models_loaded = False
        
        # Initialize enhanced patterns
        self._init_enhanced_patterns()
        
        # FIXED: Set balanced thresholds
        self._set_balanced_thresholds()
    
    def _init_fixed_natural_language_indicators(self):
        """FIXED: Initialize natural language indicators with BALANCED weights"""
        
        # FIXED: Reduced boost values untuk avoid over-detection
        self.slang_indicators = {
            'dapet': ['dapet', 'dpt'],
            'habis': ['abis', 'abs', 'habis'],
            'pengen': ['pengen', 'pen', 'ingin', 'mau'],
            'bayar': ['bayar', 'byr'],
            'dapat': ['dapat', 'dpt', 'dapet'],
            'transfer': ['tf', 'transfer', 'kirim'],
            'belanja': ['belanja', 'shopping', 'beli'],
            'nabung': ['nabung', 'menabung', 'saving'],
            'ribu': ['rb', 'ribu', 'rebu', 'k'],
            'juta': ['jt', 'juta', 'm'],
        }
        
        # FIXED: Reduced boost values
        self.family_terms = [
            'bokap', 'nyokap', 'ortu', 'orang tua',
            'papa', 'mama', 'ayah', 'ibu', 'bapak',
            'papah', 'mamah', 'umi', 'abi',
            'kakak', 'adek', 'om', 'tante', 'bude', 'pakde'
        ]
        
        self.emotional_indicators = [
            'alhamdulillah', 'syukur', 'senang', 'seneng',
            'sedih', 'capek', 'gregetan', 'boros',
            'huhu', 'hehe', 'wkwk', 'anjay',
            'asli', 'parah', 'mantap', 'keren'
        ]
        
        self.modern_payment_terms = [
            'gofood', 'grabfood', 'shopeefood',
            'gopay', 'ovo', 'dana', 'linkaja',
            'spaylater', 'kredivo', 'akulaku',
            'qris', 'cod', 'transfer bank'
        ]
        
        self.student_context = [
            'ukt', 'spp', 'kos', 'kost', 'kampus',
            'kuliah', 'semester', 'wisuda', 'skripsi',
            'praktek', 'lab', 'organisasi', 'ukm'
        ]
        
        # CRITICAL: Add COMMAND EXCLUSION indicators
        self.command_indicators = [
            'total', 'berapa', 'lihat', 'daftar', 'semua', 'progress',
            'ubah', 'ganti', 'hapus', 'delete', 'list', 'tampilkan',
            'kesehatan', 'analisis', 'performance', 'gimana', 'bagaimana'
        ]
        
        self.natural_amount_patterns = [
            r'\d+\s*(?:rb|ribu|rebu)',
            r'\d+(?:[.,]\d+)?\s*(?:jt|juta)',
            r'\d+\s*(?:k|m)',
            r'rp\.?\s*\d+',
            r'\d{1,3}(?:\.\d{3})+'  # Indonesian format
        ]
    
    def _set_balanced_thresholds(self):
        """FIXED: Set BALANCED confidence thresholds"""
        if self.models_loaded:
            # FIXED: Raised thresholds for better precision
            self.base_confidence_threshold = 0.55  # RAISED from 0.3
            self.enhanced_confidence_threshold = 0.45  # RAISED from 0.2
            self.fallback_confidence_threshold = 0.35  # RAISED from 0.1
        else:
            # Rule-based thresholds - slightly higher
            self.base_confidence_threshold = 0.7  # RAISED from 0.6
            self.enhanced_confidence_threshold = 0.55  # RAISED from 0.4
            self.fallback_confidence_threshold = 0.4  # RAISED from 0.3
        
        logger.info(f"🎯 FIXED Balanced thresholds: base={self.base_confidence_threshold}, enhanced={self.enhanced_confidence_threshold}, fallback={self.fallback_confidence_threshold}")
    
    def calculate_natural_language_boost(self, text: str) -> float:
        """FIXED: Calculate BALANCED confidence boost"""
        text_lower = text.lower()
        boost = 0.0
        indicators_found = []
        
        # CRITICAL: Check for COMMAND indicators first (NEGATIVE boost)
        command_count = sum(1 for indicator in self.command_indicators if indicator in text_lower)
        if command_count > 0:
            command_penalty = min(command_count * 0.1, 0.3)  # Max 30% penalty
            boost -= command_penalty
            indicators_found.append(f"command_penalty:-{command_penalty:.2f}")
            logger.info(f"⚠️ Command indicators detected: {command_count}, penalty: -{command_penalty:.2f}")
        
        # Check slang indicators - REDUCED boost
        slang_boost = 0
        for word, variants in self.slang_indicators.items():
            if any(variant in text_lower for variant in variants):
                slang_boost += 0.08  # REDUCED from 0.15
                indicators_found.append(f"slang:{word}")
        boost += min(slang_boost, 0.15)  # Cap slang boost
        
        # Check family terms - REDUCED boost
        for term in self.family_terms:
            if term in text_lower:
                boost += 0.06  # REDUCED from 0.1
                indicators_found.append(f"family:{term}")
                break  # Only count once
        
        # Check emotional context - REDUCED boost
        for term in self.emotional_indicators:
            if term in text_lower:
                boost += 0.05  # REDUCED from 0.08
                indicators_found.append(f"emotion:{term}")
                break  # Only count once
        
        # Check modern payment terms - REDUCED boost
        for term in self.modern_payment_terms:
            if term in text_lower:
                boost += 0.08  # REDUCED from 0.12
                indicators_found.append(f"payment:{term}")
                break  # Only count once
        
        # Check student context - REDUCED boost
        for term in self.student_context:
            if term in text_lower:
                boost += 0.05  # REDUCED from 0.08
                indicators_found.append(f"student:{term}")
                break  # Only count once
        
        # Check natural amount formats
        for pattern in self.natural_amount_patterns:
            if re.search(pattern, text_lower):
                boost += 0.04  # REDUCED from 0.05
                indicators_found.append("natural_amount")
                break  # Only count once
        
        # FIXED: Cap maximum boost to prevent over-detection
        boost = max(min(boost, 0.25), -0.3)  # Range: -30% to +25%
        
        if boost != 0:
            logger.info(f"🎯 FIXED Natural language boost: {boost:+.2f} from {indicators_found}")
        
        return boost
    
    def preprocess_natural_language(self, text: str) -> str:
        """ENHANCED: Preprocess with command detection"""
        processed_text = text.lower().strip()
        
        # CRITICAL: Flag if this looks like a command/query
        self.looks_like_command = any(indicator in processed_text for indicator in self.command_indicators)
        
        # Normalize slang to standard form (but preserve original context)
        slang_normalization = {
            'dapet': 'dapat', 'dpt': 'dapat',
            'abis': 'habis', 'abs': 'habis',
            'pengen': 'ingin', 'pen': 'ingin',
            'byr': 'bayar',
            'tf': 'transfer',
            'rb': 'ribu', 'rebu': 'ribu',
            'jt': 'juta',
            'bokap': 'ayah', 'nyokap': 'ibu',
            'ortu': 'orang tua'
        }
        
        # Apply normalization
        for slang, standard in slang_normalization.items():
            processed_text = re.sub(rf'\b{slang}\b', standard, processed_text)
        
        # Normalize amount formats
        processed_text = re.sub(r'(\d+)\s*k\b', r'\1 ribu', processed_text)
        processed_text = re.sub(r'(\d+)\s*m\b', r'\1 juta', processed_text)
        
        # Clean extra whitespace
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        return processed_text
    
    def _find_trained_models(self) -> Optional[str]:
        """Find trained models in multiple possible locations"""
        current_dir = Path(__file__).parent
        
        # Possible model locations (prioritize enhanced version)
        possible_paths = [
            current_dir.parent.parent / "models" / "indoroberta-balanced",
            current_dir.parent.parent / "backend" / "models" / "indoroberta-balanced", 
            Path("models") / "indoroberta-balanced",
            Path("D:/kuliah/semester 6/Tugas Akhir/aplikasi/maybe/lunance/backend/models/indoroberta-balanced"),
            
            # Standard version as backup
            current_dir.parent.parent / "models" / "indoroberta-financial",
            current_dir.parent.parent / "backend" / "models" / "indoroberta-financial",
            Path("models") / "indoroberta-financial",
        ]
        
        for path in possible_paths:
            if path.exists():
                intent_path = path / "intent_classifier"
                category_path = path / "category_classifier"
                
                if intent_path.exists() and category_path.exists():
                    logger.info(f"✅ Found complete trained models at: {path}")
                    return str(path)
        
        logger.error("❌ No trained models found")
        return None
    
    def _load_models(self):
        """Load fine-tuned IndoBERT models"""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
            
            # Model paths
            intent_model_path = os.path.join(self.model_path, "intent_classifier")
            category_model_path = os.path.join(self.model_path, "category_classifier")
            
            logger.info(f"📦 Loading enhanced ML models...")
            
            # Load models
            self.intent_tokenizer = AutoTokenizer.from_pretrained(intent_model_path)
            self.intent_model = AutoModelForSequenceClassification.from_pretrained(intent_model_path)
            
            self.category_tokenizer = AutoTokenizer.from_pretrained(category_model_path)
            self.category_model = AutoModelForSequenceClassification.from_pretrained(category_model_path)
            
            # Create pipelines
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            self.intent_pipeline = pipeline(
                "text-classification",
                model=self.intent_model,
                tokenizer=self.intent_tokenizer,
                device=0 if device == "cuda" else -1,
                return_all_scores=True
            )
            
            self.category_pipeline = pipeline(
                "text-classification",
                model=self.category_model,
                tokenizer=self.category_tokenizer,
                device=0 if device == "cuda" else -1,
                return_all_scores=True
            )
            
            self.models_loaded = True
            logger.info("✅ Enhanced ML models loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Error loading ML models: {e}")
            raise
    
    def _init_enhanced_patterns(self):
        """Initialize enhanced patterns for fallback parsing"""
        
        # ENHANCED MONEY PATTERNS - More comprehensive
        self.money_patterns = [
            # Indonesian natural formats (highest priority)
            r'(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:juta|jt|m)(?!\w)',
            r'(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:ribu|rb|rebu|k)(?!\w)',
            r'(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:miliar|milyar|b)(?!\w)',
            
            # Standard formats
            r'(?:rp\.?\s*)?(\d{1,3}(?:\.\d{3})+)(?!\d)',
            r'(?:rp\.?\s*)?(\d{3,})(?!\d)',
            
            # Natural language patterns
            r'(?:sejumlah|sebesar|senilai)\s+(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:juta|ribu|rb|jt|k|m)?',
            r'(?:harga|biaya|ongkos)\s+(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:juta|ribu|rb|jt|k|m)?',
        ]
        
        # ENHANCED TRANSACTION TYPE PATTERNS
        self.income_patterns = [
            # Getting money
            r'\b(?:dapat|dapet|dpt|terima|nerima|masuk|cair|transfer|kiriman)\b.*?(?:dari|dr)',
            r'\b(?:gaji|honor|fee|bayaran|pendapatan|penghasilan|beasiswa)\b',
            r'\b(?:freelance|part\s*time|kerja|ngajar)\b.*?(?:dapat|dapet|terima)',
            r'\b(?:bonus|hadiah|cashback|refund)\b',
            r'\b(?:bokap|nyokap|ortu|orang\s*tua|papa|mama|ayah|ibu)\s*(?:kasih|kirim|transfer)',
        ]
        
        self.expense_patterns = [
            # Spending money
            r'\b(?:bayar|byr|beli|belanja|habis|abis|keluar|spend|shopping)\b',
            r'\b(?:buat|untuk|utk)\s+(?:beli|bayar)',
            r'\b(?:gofood|grabfood|delivery|pesan|order)\b',
            r'\b(?:kos|kuliah|makan|transport|bensin|parkir)\b',
            r'\b(?:jajan|nongkrong|hangout|cafe|bioskop)\b',
        ]
        
        self.savings_goal_patterns = [
            # Savings targets
            r'\b(?:nabung|menabung|saving|target|goal)\b.*?(?:buat|untuk|demi)',
            r'\b(?:mau|ingin|pengen|kepingin)\s+(?:beli|punya|ambil)',
            r'\b(?:impian|mimpi|cita-cita)\b.*?(?:punya|beli)',
            r'\b(?:rencana|planning)\s+(?:beli|ambil)',
        ]
        
        # CRITICAL: Command exclusion patterns
        self.command_exclusion_patterns = [
            r'\b(?:total|berapa|semua|daftar|list|lihat|tampilkan)\s+(?:tabungan|target|goal)',
            r'\b(?:kesehatan|analisis|performance)\s+(?:keuangan|budget)',
            r'\b(?:progress|kemajuan)\s+(?:tabungan|target)',
            r'\b(?:ubah|ganti|hapus|delete)\s+(?:target|goal)',
        ]
        
        # DATE PATTERNS for target dates
        self.date_patterns = [
            r'(?:pada\s+)?(?:tanggal\s+)?(\d{1,2})\s+(\w+)\s+(\d{4})',
            r'(?:pada\s+)?(?:tanggal\s+)?(\d{1,2})[-/](\d{1,2})[-/](\d{4})',
            r'(?:pada\s+)?(?:bulan\s+)?(\w+)\s+(\d{4})',
            r'(?:dalam\s+)?(\d+)\s+(?:bulan|bln)',
            r'(?:dalam\s+)?(\d+)\s+(?:tahun|thn)',
            r'(?:sebelum|menjelang)\s+(\w+)',
        ]
        
        # Month mapping
        self.month_mapping = {
            'januari': 1, 'februari': 2, 'maret': 3, 'april': 4,
            'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
            'september': 9, 'oktober': 10, 'november': 11, 'desember': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'jun': 6, 'jul': 7, 'agu': 8, 'sep': 9, 'okt': 10, 'nov': 11, 'des': 12
        }
    
    # ==========================================
    # FIXED MAIN PARSING METHODS
    # ==========================================
    
    def parse_financial_data(self, text: str, monthly_income: float = None) -> Dict[str, Any]:
        """
        FIXED: Main parsing method with BALANCED natural language optimization
        """
        try:
            original_text = text
            logger.info(f"🔍 FIXED Enhanced parsing: '{text}'")
            
            # Step 1: Calculate BALANCED natural language boost
            nl_boost = self.calculate_natural_language_boost(text)
            
            # Step 2: Preprocess natural language with command detection
            processed_text = self.preprocess_natural_language(text)
            if processed_text != text.lower():
                logger.info(f"📝 Preprocessed: '{processed_text}'")
            
            # CRITICAL: Early command exclusion check
            if self._is_likely_command(original_text, nl_boost):
                logger.info(f"🚫 EARLY EXCLUSION: Detected as command/query, skipping financial parsing")
                return {
                    "is_financial_data": False,
                    "confidence": 0.0,
                    "message": "Terdeteksi sebagai command/query, bukan data keuangan",
                    "parsing_method": "Command_Exclusion",
                    "natural_language_boost": nl_boost,
                    "exclusion_reason": "Command indicators detected"
                }
            
            # Step 3: Try ML parsing if available
            if self.models_loaded:
                ml_result = self._parse_with_ml_enhanced(processed_text, nl_boost)
                if ml_result["is_financial_data"]:
                    logger.info(f"✅ ML parsing successful with confidence: {ml_result['confidence']:.3f}")
                    return ml_result
                else:
                    logger.info(f"📋 ML parsing failed, trying FIXED fallback...")
            
            # Step 4: FIXED Enhanced fallback parsing
            fallback_result = self._parse_with_fixed_fallback(original_text, processed_text, nl_boost)
            if fallback_result["is_financial_data"]:
                logger.info(f"✅ FIXED Enhanced fallback successful")
                return fallback_result
            
            # Step 5: Last resort - conservative pattern matching
            conservative_result = self._parse_with_conservative_patterns(original_text, nl_boost)
            if conservative_result["is_financial_data"]:
                logger.info(f"✅ Conservative pattern matching successful")
                return conservative_result
            
            # No financial data detected
            return {
                "is_financial_data": False,
                "confidence": 0.0,
                "message": "Tidak terdeteksi sebagai data keuangan",
                "parsing_method": "FIXED_Enhanced_IndoRoBERTa",
                "natural_language_boost": nl_boost
            }
            
        except Exception as e:
            logger.error(f"❌ Error in FIXED enhanced parsing: {e}")
            return {
                "is_financial_data": False,
                "confidence": 0.0,
                "error": str(e),
                "parsing_method": "FIXED_Enhanced_IndoRoBERTa_Error"
            }
    
    def _is_likely_command(self, text: str, nl_boost: float) -> bool:
        """CRITICAL: Early detection of commands/queries to prevent misclassification"""
        text_lower = text.lower()
        
        # Check for command exclusion patterns
        for pattern in self.command_exclusion_patterns:
            if re.search(pattern, text_lower):
                logger.info(f"🚫 Command exclusion pattern matched: {pattern}")
                return True
        
        # Check if negative boost (due to command indicators) is significant
        if nl_boost < -0.15:
            logger.info(f"🚫 High command penalty detected: {nl_boost:.2f}")
            return True
        
        # Check for query structure patterns
        query_structures = [
            r'\b(?:berapa|seberapa)\s+(?:total|jumlah|saldo)',
            r'\b(?:gimana|bagaimana)\s+(?:budget|keuangan|kondisi)',
            r'\b(?:apa\s+saja|daftar|semua)\s',
            r'\b(?:analisis|analysis)\s',
            r'\b(?:progress|kemajuan)\s',
        ]
        
        for pattern in query_structures:
            if re.search(pattern, text_lower):
                logger.info(f"🚫 Query structure detected: {pattern}")
                return True
        
        return False
    
    def _parse_with_ml_enhanced(self, text: str, nl_boost: float) -> Dict[str, Any]:
        """FIXED: Enhanced ML parsing with BALANCED natural language boost"""
        try:
            # Get ML predictions
            intent_result = self.intent_pipeline(text)
            
            if isinstance(intent_result, list) and len(intent_result) > 0:
                predictions = intent_result[0] if isinstance(intent_result[0], list) else intent_result
                
                best_prediction = None
                best_score = 0
                
                for pred in predictions:
                    if isinstance(pred, dict) and 'score' in pred and 'label' in pred:
                        if pred['score'] > best_score:
                            best_score = pred['score']
                            best_prediction = pred
                
                if best_prediction:
                    # Apply BALANCED natural language boost
                    boosted_confidence = min(1.0, max(0.0, best_score + nl_boost))
                    
                    # Use BALANCED adaptive threshold
                    threshold = self.enhanced_confidence_threshold if nl_boost > 0.05 else self.base_confidence_threshold
                    
                    # CRITICAL: Extra check for commands
                    if hasattr(self, 'looks_like_command') and self.looks_like_command:
                        threshold = max(threshold, 0.75)  # Much higher threshold for potential commands
                        logger.info(f"⚠️ Command detected in preprocessing, using strict threshold: {threshold:.3f}")
                    
                    logger.info(f"🎯 FIXED ML prediction: {best_prediction['label']} (original: {best_score:.3f}, boosted: {boosted_confidence:.3f}, threshold: {threshold:.3f})")
                    
                    if boosted_confidence >= threshold:
                        transaction_type = best_prediction['label'].lower()
                        
                        if transaction_type in ['income', 'expense', 'savings_goal']:
                            return self._build_ml_result(text, transaction_type, boosted_confidence, nl_boost)
            
            return {"is_financial_data": False, "confidence": 0.0}
            
        except Exception as e:
            logger.error(f"❌ FIXED ML parsing error: {e}")
            return {"is_financial_data": False, "confidence": 0.0}
    
    def _parse_with_fixed_fallback(self, original_text: str, processed_text: str, nl_boost: float) -> Dict[str, Any]:
        """FIXED: Enhanced rule-based fallback parsing with command exclusion"""
        try:
            # CRITICAL: Skip parsing if looks like command
            if nl_boost < -0.1:  # Significant command penalty
                logger.info(f"🚫 Skipping fallback due to command penalty: {nl_boost:.2f}")
                return {"is_financial_data": False, "confidence": 0.0}
            
            # Detect transaction type using enhanced patterns
            transaction_type = self._detect_type_with_patterns(processed_text)
            
            if not transaction_type:
                return {"is_financial_data": False, "confidence": 0.0}
            
            # Extract amount
            amount = self.parse_amount(original_text)
            if not amount:
                return {"is_financial_data": False, "confidence": 0.0}
            
            # FIXED: Calculate BALANCED confidence
            base_confidence = 0.65  # Slightly reduced for balance
            final_confidence = min(1.0, max(0.0, base_confidence + nl_boost))
            
            # CRITICAL: Apply minimum threshold
            if final_confidence < self.fallback_confidence_threshold:
                logger.info(f"📋 Fallback confidence too low: {final_confidence:.3f} < {self.fallback_confidence_threshold:.3f}")
                return {"is_financial_data": False, "confidence": 0.0}
            
            logger.info(f"📋 FIXED Fallback detection: {transaction_type} with confidence {final_confidence:.3f}")
            
            return self._build_fallback_result(original_text, transaction_type, amount, final_confidence, nl_boost)
            
        except Exception as e:
            logger.error(f"❌ FIXED enhanced fallback error: {e}")
            return {"is_financial_data": False, "confidence": 0.0}
    
    def _parse_with_conservative_patterns(self, text: str, nl_boost: float) -> Dict[str, Any]:
        """FIXED: Conservative pattern matching with strict criteria"""
        try:
            text_lower = text.lower()
            
            # CRITICAL: Skip if command penalty is high
            if nl_boost < -0.05:
                logger.info(f"🚫 Skipping conservative parsing due to command indicators")
                return {"is_financial_data": False, "confidence": 0.0}
            
            # More strict financial indicators
            strict_financial_indicators = [
                r'\b(?:dapat|dapet|terima)\s+\d+',  # Got [amount]
                r'\b(?:bayar|beli|habis|abis)\s+\d+',  # Paid/spent [amount]
                r'\b(?:nabung|saving)\s+(?:buat|untuk)\s+\w+',  # Saving for [item]
                r'\d+\s*(?:rb|ribu|jt|juta)\s+(?:dari|untuk|buat)',  # [amount] from/for
            ]
            
            # Check if any strict indicator matches
            has_strict_indicator = any(re.search(pattern, text_lower) for pattern in strict_financial_indicators)
            
            if has_strict_indicator and nl_boost > 0.05:  # Require positive natural language boost
                # Try to extract amount
                amount = self.parse_amount(text)
                
                if amount:
                    # Conservative type detection
                    if any(word in text_lower for word in ['dapat', 'dapet', 'terima', 'masuk', 'gaji', 'honor']):
                        transaction_type = 'income'
                    elif any(word in text_lower for word in ['nabung', 'target', 'ingin beli', 'mau beli']):
                        transaction_type = 'savings_goal'
                    else:
                        transaction_type = 'expense'
                    
                    # Conservative confidence calculation
                    confidence = min(0.5, 0.3 + nl_boost)  # Lower maximum confidence
                    
                    logger.info(f"⚡ FIXED Conservative pattern match: {transaction_type} with confidence {confidence:.3f}")
                    
                    return self._build_conservative_result(text, transaction_type, amount, confidence, nl_boost)
            
            return {"is_financial_data": False, "confidence": 0.0}
            
        except Exception as e:
            logger.error(f"❌ FIXED conservative pattern error: {e}")
            return {"is_financial_data": False, "confidence": 0.0}
    
    def _detect_type_with_patterns(self, text: str) -> Optional[str]:
        """Detect transaction type using enhanced patterns with command exclusion"""
        
        # CRITICAL: Check command exclusion first
        for pattern in self.command_exclusion_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.info(f"🚫 Command exclusion in type detection: {pattern}")
                return None
        
        # Check income patterns
        for pattern in self.income_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return 'income'
        
        # Check savings goal patterns
        for pattern in self.savings_goal_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return 'savings_goal'
        
        # Check expense patterns
        for pattern in self.expense_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return 'expense'
        
        return None
        
    # ==========================================
    # KEEP OTHER METHODS FROM ORIGINAL CODE
    # ==========================================
    
    def _build_ml_result(self, text: str, transaction_type: str, confidence: float, nl_boost: float) -> Dict[str, Any]:
        """Build result from ML prediction"""
        
        amount = self.parse_amount(text)
        if not amount:
            return {"is_financial_data": False, "confidence": 0.0}
        
        if transaction_type in ['income', 'expense']:
            category, budget_type = self._detect_category_smart(text, transaction_type)
            description = self._extract_description(text, amount)
            
            parsed_data = {
                "type": transaction_type,
                "amount": amount,
                "category": category,
                "budget_type": budget_type if transaction_type == "expense" else None,
                "description": description,
                "date": datetime.now()
            }
            
        else:  # savings_goal
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
            "confidence": confidence,
            "data_type": transaction_type,
            "parsed_data": parsed_data,
            "parsing_method": "FIXED_Enhanced_ML",
            "natural_language_boost": nl_boost
        }
    
    def _build_fallback_result(self, text: str, transaction_type: str, amount: float, confidence: float, nl_boost: float) -> Dict[str, Any]:
        """Build result from fallback parsing"""
        
        if transaction_type in ['income', 'expense']:
            category, budget_type = self._detect_category_smart(text, transaction_type)
            description = self._extract_description(text, amount)
            
            parsed_data = {
                "type": transaction_type,
                "amount": amount,
                "category": category,
                "budget_type": budget_type if transaction_type == "expense" else None,
                "description": description,
                "date": datetime.now()
            }
            
        else:  # savings_goal
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
            "confidence": confidence,
            "data_type": transaction_type,
            "parsed_data": parsed_data,
            "parsing_method": "FIXED_Enhanced_Fallback",
            "natural_language_boost": nl_boost
        }
    
    def _build_conservative_result(self, text: str, transaction_type: str, amount: float, confidence: float, nl_boost: float) -> Dict[str, Any]:
        """Build result from conservative pattern matching"""
        
        if transaction_type in ['income', 'expense']:
            # Simple category detection for conservative mode
            if transaction_type == 'income':
                category = "Lainnya"
                budget_type = "income"
            else:
                category = "Lainnya (Wants)"
                budget_type = "wants"
            
            description = self._extract_description(text, amount)
            
            parsed_data = {
                "type": transaction_type,
                "amount": amount,
                "category": category,
                "budget_type": budget_type if transaction_type == "expense" else None,
                "description": description,
                "date": datetime.now()
            }
            
        else:  # savings_goal
            item_name = self._extract_item_name(text, amount)
            
            parsed_data = {
                "item_name": item_name,
                "target_amount": amount,
                "target_date": None,
                "description": f"Target tabungan: {text[:100]}"
            }
        
        return {
            "is_financial_data": True,
            "confidence": confidence,
            "data_type": transaction_type,
            "parsed_data": parsed_data,
            "parsing_method": "FIXED_Enhanced_Conservative",
            "natural_language_boost": nl_boost
        }
    
    # ==========================================
    # KEEP ALL OTHER HELPER METHODS FROM ORIGINAL
    # ==========================================
    
    def parse_amount(self, text: str) -> Optional[float]:
        """Enhanced amount parsing with better Indonesian support"""
        if not text:
            return None
            
        text_lower = text.lower().strip()
        
        for pattern in self.money_patterns:
            matches = re.finditer(pattern, text_lower)
            
            for match in matches:
                amount_str = match.group(1)
                original_match = match.group(0)
                
                try:
                    cleaned_amount = amount_str.replace(',', '.')
                    amount = float(cleaned_amount)
                    
                    # Apply multiplier
                    final_amount = amount
                    
                    if any(unit in original_match for unit in ['juta', 'jt', 'm']):
                        final_amount = amount * 1000000
                    elif any(unit in original_match for unit in ['ribu', 'rb', 'rebu', 'k']):
                        final_amount = amount * 1000
                    elif any(unit in original_match for unit in ['miliar', 'milyar', 'b']):
                        final_amount = amount * 1000000000
                    else:
                        # Check Indonesian format
                        if '.' in amount_str and len(amount_str.replace('.', '')) > 4:
                            cleaned_amount = amount_str.replace('.', '')
                            final_amount = float(cleaned_amount)
                    
                    # Validate reasonable amount (for students)
                    if 100 <= final_amount <= 1000000000:  # 100 Rp to 1 billion
                        return final_amount
                        
                except ValueError:
                    continue
        
        return None
    
    def _detect_category_smart(self, text: str, transaction_type: str) -> Tuple[str, str]:
        """Smart category detection with ML + rules"""
        
        if self.models_loaded:
            try:
                # Try ML category detection
                result = self.category_pipeline(text)
                
                if isinstance(result, list) and len(result) > 0:
                    predictions = result[0] if isinstance(result[0], list) else result
                    
                    best_prediction = None
                    best_score = 0
                    
                    for pred in predictions:
                        if isinstance(pred, dict) and 'score' in pred and 'label' in pred:
                            if pred['score'] > best_score:
                                best_score = pred['score']
                                best_prediction = pred
                    
                    if best_prediction and best_prediction['score'] > 0.3:  # Lower threshold
                        category = best_prediction['label']
                        budget_type = self._map_category_to_budget_type(category, transaction_type)
                        return category, budget_type
            except:
                pass
        
        # Fallback to rule-based category detection
        return self._detect_category_rules(text, transaction_type)
    
    def _detect_category_rules(self, text: str, transaction_type: str) -> Tuple[str, str]:
        """Rule-based category detection as fallback"""
        text_lower = text.lower()
        
        if transaction_type == "income":
            # Income category patterns
            if any(term in text_lower for term in ['ortu', 'bokap', 'nyokap', 'papa', 'mama', 'ayah', 'ibu']):
                return "Uang Saku/Kiriman Ortu", "income"
            elif any(term in text_lower for term in ['freelance', 'project', 'ngajar', 'les']):
                return "Freelance/Project", "income"
            elif any(term in text_lower for term in ['beasiswa', 'scholarship', 'bidikmisi']):
                return "Beasiswa", "income"
            elif any(term in text_lower for term in ['part time', 'kerja', 'gaji']):
                return "Part-time Job", "income"
            else:
                return "Lainnya", "income"
        
        elif transaction_type == "expense":
            # Expense category patterns with budget type
            if any(term in text_lower for term in ['kos', 'kost', 'sewa', 'listrik', 'air']):
                return "Kos/Tempat Tinggal", "needs"
            elif any(term in text_lower for term in ['makan', 'nasi', 'lauk', 'groceries', 'masak']):
                return "Makanan Pokok", "needs"
            elif any(term in text_lower for term in ['transport', 'angkot', 'bus', 'bensin', 'parkir']):
                return "Transportasi Wajib", "needs"
            elif any(term in text_lower for term in ['buku', 'ukt', 'spp', 'kuliah', 'praktikum']):
                return "Pendidikan", "needs"
            elif any(term in text_lower for term in ['internet', 'wifi', 'pulsa', 'kuota']):
                return "Internet & Komunikasi", "needs"
            elif any(term in text_lower for term in ['obat', 'dokter', 'shampo', 'sabun']):
                return "Kesehatan & Kebersihan", "needs"
            elif any(term in text_lower for term in ['jajan', 'snack', 'kopi', 'gofood', 'grabfood']):
                return "Jajan & Snack", "wants"
            elif any(term in text_lower for term in ['nonton', 'bioskop', 'game', 'netflix', 'hangout']):
                return "Hiburan & Sosial", "wants"
            elif any(term in text_lower for term in ['baju', 'sepatu', 'tas', 'fashion']):
                return "Pakaian & Aksesoris", "wants"
            elif any(term in text_lower for term in ['nabung', 'tabungan', 'saving']):
                return "Tabungan Umum", "savings"
            else:
                return "Lainnya (Wants)", "wants"
        
        else:  # savings_goal
            return "Target Tabungan", "savings"
    
    def _map_category_to_budget_type(self, category: str, transaction_type: str) -> str:
        """Map category to budget type for 50/30/20"""
        if transaction_type == "income":
            return "income"
        elif transaction_type == "savings_goal":
            return "savings"
        else:  # expense
            category_lower = category.lower()
            
            # NEEDS categories
            if any(keyword in category_lower for keyword in [
                'kos', 'tempat tinggal', 'makanan pokok', 'transportasi wajib', 
                'pendidikan', 'kesehatan', 'komunikasi', 'internet'
            ]):
                return "needs"
            
            # SAVINGS categories
            elif any(keyword in category_lower for keyword in [
                'tabungan', 'saving', 'investasi', 'dana darurat'
            ]):
                return "savings"
            
            # WANTS categories (default)
            else:
                return "wants"
    
    def parse_target_date(self, text: str) -> Optional[datetime]:
        """Enhanced target date parsing"""
        text_lower = text.lower()
        
        for pattern in self.date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    groups = match.groups()
                    
                    if len(groups) == 3:
                        if groups[1].isdigit():
                            day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                        else:
                            day = int(groups[0])
                            month_name = groups[1].lower()
                            year = int(groups[2])
                            month = self.month_mapping.get(month_name)
                            if not month:
                                continue
                        
                        return datetime(year, month, day)
                    
                    elif len(groups) == 2:
                        month_name = groups[0].lower()
                        year = int(groups[1])
                        month = self.month_mapping.get(month_name)
                        if month:
                            return datetime(year, month, 1)
                    
                    elif len(groups) == 1:
                        now = datetime.now()
                        if 'bulan' in text_lower:
                            months = int(groups[0])
                            return now + timedelta(days=months * 30)
                        elif 'tahun' in text_lower:
                            years = int(groups[0])
                            return now.replace(year=now.year + years)
                        elif groups[0] in self.month_mapping:
                            # Month name only, assume current year
                            month = self.month_mapping[groups[0]]
                            return datetime(now.year, month, 1)
                
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _extract_description(self, text: str, amount: float) -> str:
        """Extract meaningful description from text"""
        clean_text = text
        
        # Remove amount patterns
        for pattern in self.money_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # Remove common financial keywords but keep context
        financial_words = ['bayar', 'beli', 'dapat', 'dapet', 'transfer', 'habis', 'abis']
        for word in financial_words:
            clean_text = re.sub(rf'\b{word}\b', '', clean_text, flags=re.IGNORECASE)
        
        # Clean up whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text[:100] if clean_text else "Transaksi melalui chat"
    
    def _extract_item_name(self, text: str, amount: float) -> str:
        """Extract item name for savings goal"""
        clean_text = text.lower()
        
        # Remove amount patterns
        for pattern in self.money_patterns:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # Remove savings keywords
        savings_keywords = ['nabung', 'target', 'ingin beli', 'mau beli', 'pengen beli', 'buat', 'untuk']
        for keyword in savings_keywords:
            clean_text = clean_text.replace(keyword, '')
        
        # Clean up
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        if len(clean_text) > 2:
            return clean_text.title()[:50]
        else:
            return "Target Tabungan"
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def format_currency(self, amount: float) -> str:
        """Format currency to Rupiah"""
        return f"Rp {amount:,.0f}".replace(',', '.')
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get enhanced model status"""
        return {
            "models_loaded": self.models_loaded,
            "model_path": self.model_path,
            "parsing_method": "FIXED_Enhanced_IndoRoBERTa_NL_Optimized",
            "natural_language_features": {
                "slang_indicators": len(self.slang_indicators),
                "family_terms": len(self.family_terms),
                "emotional_indicators": len(self.emotional_indicators),
                "modern_payment_terms": len(self.modern_payment_terms),
                "student_context": len(self.student_context),
                "command_indicators": len(self.command_indicators)
            },
            "balanced_thresholds": {
                "base": self.base_confidence_threshold,
                "enhanced": self.enhanced_confidence_threshold,
                "fallback": self.fallback_confidence_threshold
            },
            "fixed_features": [
                "✅ Balanced Natural Language Boost (tidak over-boost)",
                "✅ Command/Query Early Exclusion System", 
                "✅ Proper Confidence Threshold Balance",
                "✅ Improved Command vs Financial Disambiguation",
                "✅ Conservative Pattern Matching Fallback",
                "✅ Indonesian Slang Support dengan balance",
                "✅ Family Terms Recognition dengan limit",
                "✅ Modern Payment Context dengan cap",
                "✅ Student Context Awareness dengan balance"
            ]
        }
    
    def test_natural_language_detection(self, test_messages: List[str]) -> Dict[str, Any]:
        """Test FIXED natural language detection capabilities"""
        results = []
        
        for message in test_messages:
            try:
                result = self.parse_financial_data(message)
                results.append({
                    "message": message,
                    "detected": result["is_financial_data"],
                    "confidence": result.get("confidence", 0),
                    "method": result.get("parsing_method", "unknown"),
                    "nl_boost": result.get("natural_language_boost", 0),
                    "exclusion_reason": result.get("exclusion_reason", None)
                })
            except Exception as e:
                results.append({
                    "message": message,
                    "detected": False,
                    "error": str(e)
                })
        
        # Calculate summary stats
        total_tests = len(results)
        detected_count = sum(1 for r in results if r.get("detected", False))
        excluded_count = sum(1 for r in results if r.get("exclusion_reason"))
        avg_confidence = sum(r.get("confidence", 0) for r in results) / total_tests if total_tests > 0 else 0
        
        return {
            "test_results": results,
            "summary": {
                "total_tests": total_tests,
                "detected_count": detected_count,
                "excluded_count": excluded_count,
                "detection_rate": detected_count / total_tests if total_tests > 0 else 0,
                "exclusion_rate": excluded_count / total_tests if total_tests > 0 else 0,
                "average_confidence": avg_confidence
            },
            "fixed_version": "v2.0 - Balanced NL Boost & Command Exclusion"
        }

# Alias for backward compatibility
IndoRoBERTaFinancialParser = EnhancedIndoRoBERTaFinancialParser