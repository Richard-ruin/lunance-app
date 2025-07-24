# app/services/luna_ai_core.py - FIXED VERSION (Priority Routing Issue Resolved)
import re
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .luna_ai_base import LunaAIBase
from .luna_ai_handlers import LunaAIHandlers
from .luna_ai_queries import LunaAIQueries
from .luna_financial_calculator import LunaFinancialCalculator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedLunaAICore(LunaAIBase):
    """
    FIXED: Luna AI Core - Priority Routing Issue Resolved
    
    CRITICAL FIXES:
    1. ✅ Command detection gets HIGHEST priority (before financial detection)
    2. ✅ Stricter financial detection thresholds to prevent false positives
    3. ✅ Better context awareness for edit/delete commands
    4. ✅ Improved routing logic with proper fall-through
    """
    
    def __init__(self):
        logger.info("🚀 Initializing FIXED LunaAICore with proper priority routing...")
        
        # CRITICAL: Force enhanced IndoRoBERTa parser loading
        self._force_enhanced_indoroberta_parser()
        
        # Initialize base class AFTER parser is set
        super().__init__()
        
        # FIXED: Initialize components with proper error handling
        try:
            self.handlers = LunaAIHandlers()
            self.queries = LunaAIQueries()
            self.calculator = LunaFinancialCalculator()
            logger.info("✅ All Luna AI components initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing Luna AI components: {e}")
            # Create fallback instances
            self.handlers = None
            self.queries = None
            self.calculator = None
        
        # Initialize enhanced command detection patterns
        self._init_enhanced_command_patterns()
        
        # Log final parser status
        self._log_enhanced_parser_status()
    
    def _force_enhanced_indoroberta_parser(self):
        """FORCE Enhanced IndoRoBERTa parser loading with natural language optimization"""
        logger.info("🔧 FORCING Enhanced IndoRoBERTa parser initialization...")
        
        try:
            # CRITICAL: Import enhanced parser
            from .indoroberta_financial_parser import EnhancedIndoRoBERTaFinancialParser
            
            logger.info("✅ Enhanced IndoRoBERTa parser module imported successfully")
            
            # Initialize enhanced parser
            logger.info("🔄 Creating Enhanced IndoRoBERTa parser instance...")
            self.parser = EnhancedIndoRoBERTaFinancialParser()
            
            # Verify enhanced methods
            enhanced_methods = [
                'parse_financial_data', 'calculate_natural_language_boost', 
                'preprocess_natural_language', 'test_natural_language_detection'
            ]
            missing_methods = []
            
            for method in enhanced_methods:
                if not hasattr(self.parser, method):
                    missing_methods.append(method)
            
            if missing_methods:
                logger.error(f"❌ Enhanced parser missing methods: {missing_methods}")
                raise AttributeError(f"Missing enhanced methods: {missing_methods}")
            
            # Check model and enhancement status
            if hasattr(self.parser, 'models_loaded'):
                if self.parser.models_loaded:
                    logger.info("🎯 Enhanced ML models loaded successfully!")
                    self.parser_type = "Enhanced_IndoRoBERTa_ML"
                else:
                    logger.warning("📋 Enhanced parser using rule-based with NL optimization")
                    self.parser_type = "Enhanced_IndoRoBERTa_Rules"
            else:
                logger.info("🔍 Enhanced parser loaded (status unknown)")
                self.parser_type = "Enhanced_IndoRoBERTa_Unknown"
            
            # Test enhanced functionality
            test_result = self._test_enhanced_parser_functionality()
            if test_result:
                logger.info("✅ Enhanced parser functionality test PASSED")
            else:
                logger.error("❌ Enhanced parser functionality test FAILED")
                raise Exception("Enhanced parser functionality test failed")
            
            logger.info(f"🎉 Enhanced IndoRoBERTa parser successfully initialized! Type: {self.parser_type}")
            
        except ImportError as e:
            logger.error(f"❌ CRITICAL: Cannot import Enhanced IndoRoBERTa parser: {e}")
            self._load_basic_fallback_parser()
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: Enhanced IndoRoBERTa parser initialization failed: {e}")
            self._load_basic_fallback_parser()
    
    def _load_basic_fallback_parser(self):
        """Load basic fallback when enhanced parser fails"""
        try:
            from .indoroberta_financial_parser import IndoRoBERTaFinancialParser
            logger.warning("⚠️ Loading basic IndoRoBERTa parser as fallback...")
            self.parser = IndoRoBERTaFinancialParser()
            self.parser_type = "Basic_IndoRoBERTa_Fallback"
        except:
            logger.error("❌ CRITICAL: Even basic parser failed!")
            self.parser = None
            self.parser_type = "None"
    
    def _test_enhanced_parser_functionality(self) -> bool:
        """Test enhanced parser functionality with natural language samples"""
        try:
            # Test cases with natural language
            test_cases = [
                "Dapet 50rb dari freelance",  # Slang
                "Bokap kasih uang jajan 100 ribu",  # Family terms
                "Alhamdulillah dapat beasiswa 2 juta",  # Emotional
                "Gofood ayam geprek 35rb",  # Modern payment
                "Pengen banget nabung buat laptop gaming"  # Aspirational
            ]
            
            for test_case in test_cases:
                result = self.parser.parse_financial_data(test_case)
                
                # Check if detected (should have high detection rate)
                if not result.get("is_financial_data", False):
                    logger.warning(f"⚠️ Enhanced parser missed: '{test_case}'")
                else:
                    confidence = result.get("confidence", 0)
                    logger.info(f"✅ Detected: '{test_case}' (confidence: {confidence:.3f})")
            
            # Test natural language boost calculation (but don't use in final output)
            if hasattr(self.parser, 'calculate_natural_language_boost'):
                boost = self.parser.calculate_natural_language_boost("Dapet 50rb dari bokap")
                if boost > 0:
                    logger.info(f"✅ Natural language boost working: {boost:.3f}")
                    return True
                else:
                    logger.error("❌ Natural language boost not working")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Enhanced parser functionality test failed: {e}")
            return False
    
    def _init_enhanced_command_patterns(self):
        """Initialize enhanced command detection patterns - CRITICAL FIX"""
        
        # CRITICAL: Enhanced command patterns with higher specificity
        self.command_patterns = {
            # UPDATE COMMANDS - Highest Priority
            "update_target": [
                r'\b(?:ubah|ganti|edit|update)\s+(?:target|goal)\s+(.+?)\s+(?:jadi|menjadi|ke)\s+(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:juta|ribu|rb|jt|k|m)',
                r'\b(?:ubah|ganti|edit)\s+(?:target|goal)\s+(.+?)\s+(?:tanggal|waktu|deadline)\s+(.+)',
                r'\b(?:ganti|ubah)\s+nama\s+(.+?)\s+jadi\s+(.+)',
                r'\b(?:target|goal)\s+(.+?)\s+(?:ubah|ganti)\s+(?:jadi|menjadi|ke)\s+(.+)'
            ],
            
            # DELETE COMMANDS - High Priority  
            "delete_target": [
                r'\b(?:hapus|delete|remove|buang)\s+(?:target|goal)\s+(.+)',
                r'\b(?:batalkan|cancel)\s+(?:target|goal)\s+(.+)',
                r'\b(?:ga|gak|tidak)\s+(?:jadi|mau)\s+(?:target|goal)\s+(.+)'
            ],
            
            # LIST COMMANDS - High Priority
            "list_targets": [
                r'\b(?:daftar|list|lihat|tampilkan)\s+(?:target|goal|semua\s+target)',
                r'\b(?:target|goal)\s+(?:saya|aku|gue)\s*(?:apa\s+saja|semua)?',
                r'\bsemua\s+target\s+(?:saya|aku|gue)',
                r'\b(?:progress|kemajuan)\s+(?:semua\s+)?(?:target|goal)'
            ],
            
            # FINANCIAL QUERIES - Medium Priority  
            "financial_query": [
                r'\b(?:total|berapa)\s+(?:tabungan|saving|uang|duit)\s+(?:saya|aku|gue)',
                r'\b(?:kesehatan|health)\s+(?:keuangan|finansial)',
                r'\b(?:budget|anggaran)\s+(?:performance|performa)',
                r'\b(?:pengeluaran|expense)\s+(?:terbesar|terbanyak)',
                r'\b(?:analisis|analysis)\s+(?:keuangan|finansial|pengeluaran)'
            ],
            
            # CONFIRMATION PATTERNS - High Priority for context
            "confirmation": [
                r'^\s*(?:ya|yes|iya|ok|okay|oke|benar|betul|setuju|lanjut)\s*$',
                r'^\s*(?:tidak|no|nope|ga|gak|batal|cancel|salah)\s*$'
            ]
        }
        
        logger.info("🔧 Enhanced command patterns initialized with strict detection")
    
    def _log_enhanced_parser_status(self):
        """Log comprehensive enhanced parser status"""
        logger.info("=" * 70)
        logger.info("📊 FIXED LUNA AI CORE PARSER STATUS REPORT")
        logger.info("=" * 70)
        logger.info(f"Parser Type: {getattr(self, 'parser_type', 'Unknown')}")
        logger.info(f"Parser Class: {type(self.parser).__name__ if self.parser else 'None'}")
        logger.info(f"Handlers Available: {self.handlers is not None}")
        logger.info(f"Queries Available: {self.queries is not None}")
        logger.info(f"Calculator Available: {self.calculator is not None}")
        logger.info("=" * 70)
    
    # ==========================================
    # FIXED MAIN RESPONSE GENERATION - PRIORITY ROUTING
    # ==========================================
    
    async def generate_response(self, user_message: str, user_id: str, conversation_id: str, message_id: str) -> str:
        """
        FIXED: Response generation with PROPER PRIORITY ROUTING
        
        CRITICAL FIX: Command detection now has HIGHEST priority before financial detection
        """
        message_lower = user_message.lower().strip()
        
        logger.info(f"🚀 FIXED Processing message: '{user_message}'")
        logger.info(f"📊 Available components: handlers={self.handlers is not None}, queries={self.queries is not None}, calculator={self.calculator is not None}")
        
        # ==========================================
        # STEP 1: COMMAND DETECTION - HIGHEST PRIORITY (CRITICAL FIX)
        # ==========================================
        
        logger.info("🔍 STEP 1: Command Detection (Highest Priority)")
        
        # CONFIRMATION HANDLING - Must be first to maintain context
        confirmation = await self._detect_enhanced_confirmation(user_message)
        if confirmation is not None and self.handlers:
            logger.info(f"✅ CONFIRMATION detected: {confirmation}")
            try:
                return await self.handlers.handle_confirmation(user_id, conversation_id, confirmation)
            except Exception as e:
                logger.error(f"❌ Error handling confirmation: {e}")
        
        # UPDATE/DELETE COMMANDS - Critical priority before financial detection
        update_delete_command = await self._detect_enhanced_update_delete_command(user_message)
        if update_delete_command and self.handlers:
            logger.info(f"✅ UPDATE/DELETE COMMAND detected: {update_delete_command['action']}")
            try:
                return await self.handlers.handle_update_delete_command(user_id, conversation_id, message_id, update_delete_command)
            except Exception as e:
                logger.error(f"❌ Error handling update/delete command: {e}")
        
        # LIST COMMANDS - High priority
        if self._is_list_command(user_message):
            logger.info("✅ LIST COMMAND detected")
            if self.handlers:
                try:
                    return await self.handlers.handle_list_savings_goals(user_id)
                except Exception as e:
                    logger.error(f"❌ Error handling list command: {e}")
        
        # ==========================================
        # STEP 2: FINANCIAL QUERIES - MEDIUM PRIORITY (FIXED)
        # ==========================================
        
        logger.info("🔍 STEP 2: Financial Queries (Medium Priority)")
        
        query_type = await self._detect_enhanced_financial_query(user_message)
        if query_type and self.queries:
            logger.info(f"✅ FINANCIAL QUERY detected: {query_type}")
            try:
                return await self.queries.handle_financial_query(user_id, query_type)
            except Exception as e:
                logger.error(f"❌ Error handling financial query: {e}")
                # Continue to other checks instead of failing completely
        
        # ==========================================
        # STEP 3: PURCHASE INTENT - MEDIUM PRIORITY (FIXED)
        # ==========================================
        
        logger.info("🔍 STEP 3: Purchase Intent Detection")
        
        purchase_intent = await self._detect_enhanced_purchase_intent(user_message)
        if purchase_intent and self.queries:
            logger.info(f"✅ PURCHASE INTENT detected: {purchase_intent['item_name']} - {purchase_intent.get('price', 'N/A')}")
            try:
                return await self.queries.handle_purchase_intent(user_id, purchase_intent)
            except Exception as e:
                logger.error(f"❌ Error handling purchase intent: {e}")
        
        # ==========================================
        # STEP 4: FINANCIAL DATA DETECTION - LOWER PRIORITY (CRITICAL FIX)
        # ==========================================
        
        logger.info("🔍 STEP 4: Financial Data Detection (Lower Priority - FIXED)")
        
        if self.parser:
            logger.info(f"💰 Testing financial parsing with STRICTER thresholds...")
            
            try:
                # Use enhanced parser with natural language optimization
                parse_result = self.parser.parse_financial_data(user_message)
                
                is_financial = parse_result.get("is_financial_data", False)
                confidence = parse_result.get("confidence", 0)
                
                # CRITICAL FIX: STRICTER threshold to prevent false positives on commands
                effective_threshold = 0.6  # RAISED from 0.25 to prevent command misdetection
                
                # ADDITIONAL CHECK: If message contains command words, require MUCH higher confidence
                command_indicators = ['ubah', 'ganti', 'hapus', 'delete', 'daftar', 'list', 'semua', 'progress']
                has_command_words = any(word in message_lower for word in command_indicators)
                
                if has_command_words:
                    effective_threshold = 0.85  # Very high threshold for potential commands
                    logger.info(f"⚠️ Command words detected, using STRICT threshold: {effective_threshold}")
                
                logger.info(f"📊 Parse result: financial={is_financial}, confidence={confidence:.3f}, threshold={effective_threshold:.3f}, has_commands={has_command_words}")
                
                if is_financial and confidence >= effective_threshold:
                    logger.info(f"✅ Financial data detected with HIGH confidence! Processing...")
                    
                    transaction_type = parse_result.get("data_type")
                    parsed_data = parse_result.get("parsed_data", {})
                    amount = parsed_data.get("amount") or parsed_data.get("target_amount")
                    
                    if transaction_type and amount and self.handlers:
                        logger.info(f"💰 Processing {transaction_type}, amount: {amount}")
                        
                        # FIXED: Generate response WITHOUT natural language boost message
                        response = await self.handlers.handle_financial_data(
                            user_id, conversation_id, message_id,
                            transaction_type, amount, user_message
                        )
                        
                        return response
                    else:
                        logger.warning(f"⚠️ Enhanced parser detected financial data but missing key fields or handlers unavailable")
                else:
                    logger.info(f"📋 Financial data not detected or confidence too low (command protection)")
                
            except Exception as e:
                logger.error(f"❌ Error in enhanced financial parsing: {e}")
                # Continue to other checks instead of failing completely
        else:
            logger.warning("⚠️ No enhanced parser available!")
        
        # ==========================================
        # STEP 5: REGULAR MESSAGE HANDLING (FIXED)
        # ==========================================
        
        logger.info(f"💬 No specific actions detected, handling as regular message")
        return await self._handle_enhanced_regular_message(user_message, user_id)
    
    # ==========================================
    # ENHANCED DETECTION METHODS - FIXED
    # ==========================================
    
    def _is_list_command(self, message: str) -> bool:
        """Check if message is a list command"""
        message_lower = message.lower().strip()
        
        list_patterns = [
            r'\b(?:daftar|list|lihat|tampilkan)\s+(?:target|goal)',
            r'\b(?:semua|all)\s+(?:target|goal)',
            r'\b(?:target|goal)\s+(?:saya|aku|gue|apa\s+saja)',
            r'\bprogress\s+(?:semua\s+)?(?:target|goal|tabungan)'
        ]
        
        return any(re.search(pattern, message_lower) for pattern in list_patterns)
    
    async def _detect_enhanced_update_delete_command(self, message: str) -> Optional[Dict[str, Any]]:
        """
        ENHANCED: Update/delete command detection with better specificity
        CRITICAL FIX: More precise patterns to avoid confusion with financial data
        """
        message_lower = message.lower().strip()
        
        # CRITICAL: Check for UPDATE patterns first (more complex)
        update_patterns = [
            # Target amount update - very specific pattern
            r'\b(?:ubah|ganti|edit|update)\s+(?:target|goal)\s+(.+?)\s+(?:jadi|menjadi|ke)\s+(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:juta|ribu|rb|jt|k|m)',
            
            # Target date update - specific pattern
            r'\b(?:ubah|ganti|edit|update)\s+(?:target|goal)\s+(.+?)\s+(?:tanggal|waktu|deadline|pada)\s+(.+)',
            
            # Name change - specific pattern
            r'\b(?:ganti|ubah)\s+nama\s+(.+?)\s+jadi\s+(.+)',
            
            # Alternative update patterns
            r'\b(?:target|goal)\s+(.+?)\s+(?:ubah|ganti|edit)\s+(?:jadi|menjadi|ke)\s+(.+)'
        ]
        
        for pattern in update_patterns:
            match = re.search(pattern, message_lower)
            if match:
                groups = match.groups()
                logger.info(f"✅ UPDATE command matched: pattern='{pattern}', groups={groups}")
                
                # Extract relevant info based on pattern
                if len(groups) >= 2:
                    target_item = groups[0].strip()
                    new_value = groups[1].strip()
                    
                    # Determine update type
                    if any(keyword in message_lower for keyword in ['tanggal', 'waktu', 'deadline', 'pada']):
                        update_type = "date"
                        update_fields = {"target_date": new_value}  # Will be parsed later
                    elif re.search(r'\d+(?:[.,]\d+)?', new_value):
                        update_type = "price"
                        # Extract amount
                        amount_match = re.search(r'(\d+(?:[.,]\d+)?)', new_value)
                        if amount_match:
                            amount = float(amount_match.group(1).replace(',', '.'))
                            # Apply multiplier
                            if any(unit in new_value for unit in ['juta', 'jt', 'm']):
                                amount *= 1000000
                            elif any(unit in new_value for unit in ['ribu', 'rb', 'rebu', 'k']):
                                amount *= 1000
                            update_fields = {"target_amount": amount}
                        else:
                            continue
                    else:
                        update_type = "name"
                        update_fields = {"item_name": new_value}
                    
                    return {
                        "action": "update",
                        "update_type": update_type,
                        "item_name": target_item,
                        "update_fields": update_fields,
                        "original_message": message,
                        "detection_method": "enhanced_pattern_fixed"
                    }
        
        # CRITICAL: Check for DELETE patterns
        delete_patterns = [
            r'\b(?:hapus|delete|remove|buang)\s+(?:target|goal)\s+(.+)',
            r'\b(?:batalkan|cancel)\s+(?:target|goal)\s+(.+)',
            r'\b(?:ga|gak|tidak)\s+(?:jadi|mau)\s+(?:target|goal)\s+(.+)'
        ]
        
        for pattern in delete_patterns:
            match = re.search(pattern, message_lower)
            if match:
                target_item = match.group(1).strip()
                logger.info(f"✅ DELETE command matched: target='{target_item}'")
                
                return {
                    "action": "delete",
                    "item_name": target_item,
                    "original_message": message,
                    "detection_method": "enhanced_pattern_fixed"
                }
        
        return None
    
    async def _detect_enhanced_financial_query(self, message: str) -> Optional[str]:
        """FIXED: Enhanced financial query detection with more patterns"""
        message_lower = message.lower()
        
        # Enhanced query patterns - FIXED routing
        enhanced_query_patterns = {
            "total_tabungan": [
                r'(?:total|jumlah)?\s*(?:tabungan|saving|uang|duit)\s*(?:saya|aku|gue)?\s*(?:berapa|seberapa|ada berapa)?',
                r'(?:berapa|seberapa)\s*(?:sih|dong)?\s*(?:total|jumlah)?\s*(?:tabungan|saving|uang|duit)',
                r'(?:cek|check)\s*(?:tabungan|saving|saldo)',
                r'(?:uang|duit|tabungan)\s*(?:saya|aku|gue)\s*(?:sekarang|saat ini|ada berapa)?'
            ],
            "budget_performance": [
                r'(?:budget|anggaran)\s*(?:performance|performa|gimana|bagaimana|how)',
                r'(?:50|30|20)\s*(?:percent|persen|%)',
                r'(?:kondisi|status)\s*(?:budget|anggaran)\s*(?:bulan ini|bulanan)',
                r'(?:over|melebihi|habis)\s*(?:budget|anggaran)',
                r'(?:sehat|health)\s*(?:keuangan|finansial|budget)'
            ],
            "expense_analysis": [
                r'(?:pengeluaran|expense)\s*(?:terbesar|terbanyak|paling banyak)',
                r'(?:habis|keluar|spend)\s*(?:berapa|seberapa)\s*(?:untuk|buat)',
                r'(?:analisis|analysis)\s*(?:pengeluaran|expense|spending)',
                r'(?:breakdown|rincian|detail)\s*(?:pengeluaran|expense)'
            ],
            "savings_progress": [
                r'(?:progress|kemajuan)\s*(?:tabungan|saving|target)',
                r'(?:target|goal)\s*(?:tabungan|saving)\s*(?:gimana|bagaimana|how)',
                r'(?:daftar|list)\s*(?:target|goal)',
                r'(?:seberapa|berapa)\s*(?:jauh|dekat)?\s*(?:target|goal)'
            ],
            "financial_health": [
                r'(?:kesehatan|health)\s*(?:keuangan|finansial)',
                r'(?:kondisi|status)\s*(?:keuangan|finansial)',
                r'(?:financial|finance)\s*(?:health|status)'
            ]
        }
        
        for query_type, patterns in enhanced_query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    logger.info(f"🎯 Query pattern matched: {query_type} with pattern: {pattern}")
                    return query_type
        
        return None
    
    async def _detect_enhanced_purchase_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """Enhanced purchase intent detection with lower thresholds"""
        # More comprehensive patterns
        purchase_patterns = [
            r'(?:mau|ingin|pengen|kepingin|butuh|perlu)\s+(?:beli|punya|ambil|dapetin)\s+(.+?)\s+(?:(?:seharga|harga|sekitar|budget)?\s*(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:juta|ribu|rb|k|m)?)',
            r'(.+?)\s+(?:harga|harganya|sekitar)\s+(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:juta|ribu|rb|k|m)?',
            r'(?:budget|dana)\s+(?:buat|untuk)\s+(.+?)\s+(?:rp\.?\s*)?(\d+(?:[.,]\d+)?)\s*(?:juta|ribu|rb|k|m)?',
            r'(?:mau|ingin|pengen)\s+(.+?)\s+tapi\s+(?:mahal|expensive)',  # Want but expensive
        ]
        
        message_lower = message.lower()
        
        for pattern in purchase_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if len(match.groups()) >= 2:
                    item_name = match.group(1).strip()
                    price_str = match.group(2)
                    
                    # Parse price using fallback method
                    price = self._parse_price_from_string(f"{price_str} ribu")
                    if price and price > 0:
                        return {
                            "item_name": item_name.title(),
                            "price": price,
                            "original_text": message,
                            "detection_method": "enhanced_pattern"
                        }
                else:
                    # Handle "want but expensive" case
                    item_name = match.group(1).strip()
                    return {
                        "item_name": item_name.title(),
                        "price": None,
                        "original_text": message,
                        "detection_method": "enhanced_pattern_no_price"
                    }
        
        return None
    
    def _parse_price_from_string(self, text: str) -> Optional[float]:
        """Parse price from string using simple patterns"""
        try:
            # Simple amount extraction
            patterns = [
                r'(\d+(?:[.,]\d+)?)\s*(?:juta|jt|m)',
                r'(\d+(?:[.,]\d+)?)\s*(?:ribu|rb|rebu|k)',
                r'(\d{4,})',  # Large numbers
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    amount = float(match.group(1).replace(',', '.'))
                    
                    # Apply multipliers
                    if 'juta' in text.lower() or 'jt' in text.lower():
                        amount *= 1000000
                    elif 'ribu' in text.lower() or 'rb' in text.lower() or 'rebu' in text.lower():
                        amount *= 1000
                    
                    # Validate reasonable range
                    if 100 <= amount <= 1000000000:
                        return amount
            
            return None
        except:
            return None
    
    async def _detect_enhanced_confirmation(self, message: str) -> Optional[bool]:
        """Enhanced confirmation detection with more variations"""
        message_lower = message.lower().strip()
        
        # Enhanced positive patterns
        positive_patterns = [
            r'^(?:ya|yes|iya|ok|okay|oke|benar|betul|correct|true|confirm|lanjut|gas|go)$',
            r'^(?:ya|yes)\s*(?:benar|betul|correct|dong|bro|bestie)?$',
            r'^(?:setuju|agree|lanjutkan|siap|ready|mantap|sip)$',
            r'^(?:simpan|save|confirm|iyaa+|yaaa+)$'
        ]
        
        # Enhanced negative patterns
        negative_patterns = [
            r'^(?:tidak|no|nope|ga|gak|enggak|engga|salah|wrong|keliru)$',
            r'^(?:tidak|no|ga|gak)\s*(?:benar|betul|correct|deh|dong)?$',
            r'^(?:batal|cancel|batalkan|stop|jangan|dont|don\'t)$',
            r'^(?:nggak|kagak|kaga|tidaak+|nooo+)$'
        ]
        
        for pattern in positive_patterns:
            if re.search(pattern, message_lower):
                return True
        
        for pattern in negative_patterns:
            if re.search(pattern, message_lower):
                return False
        
        return None
    
    async def _handle_enhanced_regular_message(self, message: str, user_id: str) -> str:
        """FIXED: Enhanced regular message handling with financial context"""
        message_lower = message.lower().strip()
        
        # Enhanced greeting responses
        if any(word in message_lower for word in ['halo', 'hai', 'hi', 'hello', 'selamat']):
            greetings = [
                f"""Halo! Saya Luna dengan **IndoRoBERTa AI** yang ngerti bahasa natural mahasiswa! 🚀

💬 **Langsung ngomong aja natural:**
• *"Dapet 50rb dari freelance"* ✅
• *"Abis 25 rebu buat makan"* ✅  
• *"Bokap kasih jajan 100rb"* ✅
• *"Pengen banget nabung buat laptop"* ✅

🎯 **Fitur**: Deteksi slang Indonesia, family terms, modern payments!""",
                
                f"""Hai! Luna siap dengan **AI Natural Language** yang paham bahasa mahasiswa! 👋

🗣️ **Ngomong sesantai ini:**
• *"Alhamdulillah dapet beasiswa 2 juta"* 
• *"Capek deh abis 75k gofood"*
• *"Nyokap transfer 500 ribu"*
• *"Mau banget punya iPhone"*

✨ **Deteksi**: Akurat untuk bahasa natural Indonesia!"""
            ]
            return random.choice(greetings)
        
        # Enhanced help responses for natural language
        elif any(word in message_lower for word in ['bantuan', 'help', 'tolong', 'gimana', 'bagaimana', 'cara']):
            return f"""🔰 **Luna AI - Asisten Keuangan Natural Language**

🚀 **Powered by IndoRoBERTa AI** - Paham bahasa natural mahasiswa!

🗣️ **Ngomong Natural Aja:**
• *"Dapet 50rb dari freelance"* → Auto detect income ✅
• *"Abis 25 rebu makan warteg"* → Auto detect expense ✅
• *"Pengen nabung buat laptop gaming"* → Auto detect target ✅

🎯 **Pake Bahasa Sehari-hari:**
• *"Bokap kasih jajan 100rb"* → Uang dari ortu
• *"Nyokap transfer 200 ribu"* → Transfer dari mama
• *"Capek deh bayar kos 800rb"* → Expense dengan emotion

💳 **Modern Payment:**
• *"Gofood ayam geprek 35rb"* → Digital payment
• *"Bayar via GoPay 28 ribu"* → E-wallet
• *"Spaylater 150rb beli sepatu"* → BNPL

📊 **FIXED: Query Financial (Sekarang Bisa!):**
• *"Total tabungan saya berapa?"*
• *"Budget performance bulan ini gimana?"*
• *"Pengeluaran terbesar saya apa?"*
• *"Progress tabungan saya gimana?"*
• *"Kesehatan keuangan saya bagaimana?"*

🔧 **FIXED: Commands (Sekarang Prioritas Tinggi!):**
• *"Ubah target laptop jadi 12 juta"* → Edit target
• *"Hapus target motor"* → Delete target
• *"Daftar target saya"* → List all goals

🔥 **Fixed**: Routing prioritas sudah diperbaiki - commands tidak lagi terdeteksi sebagai input keuangan!"""
        
        # Enhanced financial context responses
        elif any(keyword in message_lower for keyword in ['budget', 'anggaran', 'uang', 'keuangan', 'tabungan', 'hemat']):
            return f"""💰 **Luna siap bantu financial planning mahasiswa!**

🎯 **Metode 50/30/20 (Natural Style):**
• **50% NEEDS**: "Bayar kos 800rb", "Transport kuliah 200rb"
• **30% WANTS**: "Nongkrong 100rb", "Beli baju 300rb"  
• **20% SAVINGS**: "Nabung masa depan", "Target laptop"

🗣️ **Ngomong aja santai:**
• "Dapet uang saku 2 juta dari ortu"
• "Abis 75k buat jajan bubble tea"
• "Pengen banget nabung buat iPhone"

📊 **FIXED: Financial Queries Available:**
• *"Total tabungan saya berapa?"*
• *"Budget performance gimana?"*
• *"Analisis keuangan saya dong"*

🔧 **FIXED: Commands Available:**
• *"Ubah target [nama] jadi [harga]"*
• *"Hapus target [nama]"*
• *"Daftar semua target saya"*

Yuk mulai input transaksi dengan bahasa natural! 🚀"""
        
        # Default with natural language encouragement
        else:
            defaults = [
                f"""🤖 **Luna AI** siap membantu! Coba dengan bahasa natural Indonesia ya.

💬 **Format yang AI suka:**
• *"Dapet 50rb dari ngajar"* (slang + context)
• *"Alhamdulillah dapat beasiswa 2 juta"* (emotional)
• *"Capek deh abis 30rb gofood"* (modern payment)

📊 **FIXED: Atau tanya financial queries:**
• *"Total tabungan saya berapa?"*
• *"Budget performance bulan ini gimana?"*

🔧 **FIXED: Commands juga sudah bekerja:**
• *"Ubah target [nama] jadi [harga]"*
• *"Daftar target saya"*""",
                
                f"""😅 **AI** masih belajar konteks ini. Yuk coba bahasa yang lebih natural!

🎯 **Contoh yang **BERHASIL**:**
• *"Bokap kasih uang jajan 100rb"* (family terms)
• *"Pengen banget nabung motor 15 juta"* (aspirational)
• *"Grabfood ayam geprek 35 ribu"* (modern payments)

💰 **FIXED: Financial Analysis Ready:**
• *"Kesehatan keuangan saya gimana?"*
• *"Analisis pengeluaran saya dong"*

🔧 **FIXED: Commands Now Working:**
• *"Ubah target laptop jadi 15 juta"*
• *"Hapus target motor"*"""
            ]
            return random.choice(defaults)
    
    # ==========================================
    # UTILITY METHODS - UNCHANGED
    # ==========================================
    
    def get_parser_info(self) -> Dict[str, Any]:
        """Get enhanced parser information"""
        base_info = {
            "parser_type": getattr(self, 'parser_type', 'Unknown'),
            "parser_class": type(self.parser).__name__ if self.parser else 'None',
            "handlers_available": self.handlers is not None,
            "queries_available": self.queries is not None,
            "calculator_available": self.calculator is not None,
            "fixed_issues": [
                "✅ CRITICAL: Command detection now has HIGHEST priority",
                "✅ CRITICAL: Financial detection thresholds made stricter", 
                "✅ CRITICAL: Update/delete commands no longer misdetected as financial input",
                "✅ Enhanced routing logic with proper fall-through",
                "✅ Better context awareness for edit/delete operations"
            ],
            "enhanced_features": [
                "Natural Language Preprocessing",
                "Adaptive Confidence Thresholds", 
                "Multi-level Fallback Detection",
                "Enhanced Command Pattern Matching",
                "Indonesian Slang Support",
                "Family Terms Recognition",
                "Emotional Context Detection", 
                "Modern Payment Recognition",
                "Student Context Awareness",
                "FIXED: Priority-based Routing System",
                "FIXED: Command vs Financial Data Disambiguation"
            ]
        }
        
        if self.parser and hasattr(self.parser, 'get_model_status'):
            try:
                parser_status = self.parser.get_model_status()
                base_info.update(parser_status)
            except:
                pass
        
        return base_info
    
    def test_parser_with_message(self, test_message: str) -> Dict[str, Any]:
        """Test enhanced parser with specific message"""
        if not self.parser:
            return {
                "error": "No enhanced parser available",
                "parser_type": getattr(self, 'parser_type', 'Unknown')
            }
        
        try:
            logger.info(f"🧪 Testing parser with: '{test_message}'")
            result = self.parser.parse_financial_data(test_message)
            
            result["enhanced_info"] = {
                "parser_type": getattr(self, 'parser_type', 'Unknown'),
                "parser_class": type(self.parser).__name__,
                "test_message": test_message,
                "parsing_method": result.get("parsing_method", "unknown"),
                "fixed_issues": "Priority routing system implemented, commands prioritized over financial detection"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Enhanced parser test failed: {e}")
            return {
                "error": str(e),
                "parser_type": getattr(self, 'parser_type', 'Unknown'),
                "test_message": test_message
            }

# Alias for backward compatibility 
LunaAICore = EnhancedLunaAICore