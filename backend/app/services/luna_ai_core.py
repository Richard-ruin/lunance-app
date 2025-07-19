# app/services/luna_ai_core.py - UPDATED VERSION
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
from .luna_ai_queries import LunaAIQueries  # ✅ Now uses the FIXED version
from .luna_financial_calculator import LunaFinancialCalculator

# Setup logging for tracking parser usage
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LunaAICore(LunaAIBase):
    """
    FIXED Luna AI Core with FORCED IndoRoBERTa integration
    """
    
    def __init__(self):
        logger.info("🤖 Initializing LunaAICore with IndoRoBERTa integration...")
        
        # CRITICAL: Force IndoRoBERTa parser loading
        self._force_indoroberta_parser()
        
        # Initialize base class AFTER parser is set
        super().__init__()
        
        # Initialize other components
        self.handlers = LunaAIHandlers()
        self.queries = LunaAIQueries()  # ✅ Now uses FIXED LunaAIQueries
        self.calculator = LunaFinancialCalculator()
        
        # Log final parser status
        self._log_parser_status()
    
    def _force_indoroberta_parser(self):
        """FORCE IndoRoBERTa parser loading with detailed logging"""
        logger.info("🔧 FORCING IndoRoBERTa parser initialization...")
        
        try:
            # CRITICAL: Direct import with absolute path
            from .indoroberta_financial_parser import IndoRoBERTaFinancialParser
            
            logger.info("✅ IndoRoBERTa parser module imported successfully")
            
            # Initialize parser with explicit logging
            logger.info("🔄 Creating IndoRoBERTa parser instance...")
            self.parser = IndoRoBERTaFinancialParser()
            
            # Check if parser has methods we need
            required_methods = ['parse_financial_data', 'parse_amount', 'detect_transaction_type']
            missing_methods = []
            
            for method in required_methods:
                if not hasattr(self.parser, method):
                    missing_methods.append(method)
            
            if missing_methods:
                logger.error(f"❌ IndoRoBERTa parser missing methods: {missing_methods}")
                raise AttributeError(f"Missing methods: {missing_methods}")
            
            # Check model loading status
            if hasattr(self.parser, 'models_loaded'):
                if self.parser.models_loaded:
                    logger.info("🎯 IndoRoBERTa ML models loaded successfully!")
                    self.parser_type = "IndoRoBERTa_ML"
                else:
                    logger.warning("📋 IndoRoBERTa using rule-based fallback")
                    self.parser_type = "IndoRoBERTa_Rules"
            else:
                logger.info("🔍 IndoRoBERTa parser loaded (status unknown)")
                self.parser_type = "IndoRoBERTa_Unknown"
            
            # Test parser functionality
            test_result = self._test_parser_functionality()
            if test_result:
                logger.info("✅ IndoRoBERTa parser functionality test PASSED")
            else:
                logger.error("❌ IndoRoBERTa parser functionality test FAILED")
                raise Exception("Parser functionality test failed")
            
            logger.info(f"🎉 IndoRoBERTa parser successfully initialized! Type: {self.parser_type}")
            
        except ImportError as e:
            logger.error(f"❌ CRITICAL: Cannot import IndoRoBERTa parser: {e}")
            self._load_fallback_parser()
            
        except Exception as e:
            logger.error(f"❌ CRITICAL: IndoRoBERTa parser initialization failed: {e}")
            self._load_fallback_parser()
    
    def _load_fallback_parser(self):
        """Load fallback parser when IndoRoBERTa fails"""
        logger.error("❌ FALLBACK SHOULD NOT BE USED - IndoRoBERTa required!")
        self.parser = None
        self.parser_type = "None"
    
    def _test_parser_functionality(self) -> bool:
        """Test parser functionality dengan sample data"""
        try:
            # Test parsing
            test_parse = self.parser.parse_financial_data("Bayar kos 800 ribu")
            if not test_parse.get("is_financial_data"):
                logger.error("❌ Parser test failed: not detected as financial data")
                return False
            
            logger.info("✅ All parser functionality tests passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Parser functionality test failed with exception: {e}")
            return False
    
    def _log_parser_status(self):
        """Log comprehensive parser status"""
        logger.info("=" * 60)
        logger.info("📊 LUNA AI CORE PARSER STATUS REPORT")
        logger.info("=" * 60)
        logger.info(f"Parser Type: {getattr(self, 'parser_type', 'Unknown')}")
        logger.info(f"Parser Object: {type(self.parser).__name__ if self.parser else 'None'}")
        
        if self.parser:
            logger.info(f"Parser Module: {self.parser.__class__.__module__}")
            
            # Check for IndoRoBERTa specific attributes
            if hasattr(self.parser, 'models_loaded'):
                logger.info(f"ML Models Loaded: {self.parser.models_loaded}")
            
            if hasattr(self.parser, 'model_path'):
                logger.info(f"Model Path: {getattr(self.parser, 'model_path', 'Not set')}")
            
            # List available methods
            parser_methods = [method for method in dir(self.parser) if not method.startswith('_')]
            logger.info(f"Available Methods: {len(parser_methods)}")
            logger.info(f"Key Methods: {[m for m in parser_methods if 'parse' in m or 'detect' in m]}")
        
        logger.info("=" * 60)
    
    # ==========================================
    # MAIN RESPONSE GENERATION - Rest unchanged
    # ==========================================
    
    async def generate_response(self, user_message: str, user_id: str, conversation_id: str, message_id: str) -> str:
        """Enhanced response generation with IndoRoBERTa"""
        message_lower = user_message.lower().strip()
        
        # Log parser usage
        logger.info(f"🤖 Luna processing with {getattr(self, 'parser_type', 'Unknown')} parser: '{user_message}'")
        
        # 1. Purchase intent
        purchase_intent = self.is_purchase_intent(user_message)
        if purchase_intent:
            logger.info(f"🛒 Purchase intent: {purchase_intent['item_name']} - {purchase_intent['price']}")
            return await self.queries.handle_purchase_intent(user_id, purchase_intent)
        
        # 2. Financial queries
        query_type = self.is_financial_query(user_message)
        if query_type:
            logger.info(f"📊 Financial query: {query_type}")
            return await self.queries.handle_financial_query(user_id, query_type)
        
        # 3. Update/delete commands  
        update_delete_command = self.is_update_delete_command(user_message)
        if update_delete_command:
            logger.info(f"🔧 Update/Delete command: {update_delete_command['action']}")
            return await self.handlers.handle_update_delete_command(user_id, conversation_id, message_id, update_delete_command)
        
        # 4. Confirmation handling
        confirmation = self.is_confirmation_message(user_message)
        if confirmation is not None:
            logger.info(f"📝 Confirmation: {confirmation}")
            return await self.handlers.handle_confirmation(user_id, conversation_id, confirmation)
        
        # 5. Financial data parsing with IndoRoBERTa
        if self.parser:
            logger.info(f"💰 Attempting financial parsing with {getattr(self, 'parser_type', 'Unknown')} parser...")
            
            try:
                parse_result = self.parser.parse_financial_data(user_message)
                
                if parse_result.get("is_financial_data"):
                    logger.info(f"✅ Financial data detected by {getattr(self, 'parser_type', 'Unknown')} parser!")
                    
                    transaction_type = parse_result.get("data_type")
                    amount = parse_result.get("parsed_data", {}).get("amount") or parse_result.get("parsed_data", {}).get("target_amount")
                    
                    if transaction_type and amount:
                        logger.info(f"💰 Processing financial data: {transaction_type}, amount: {amount}")
                        return await self.handlers.handle_financial_data(
                            user_id, conversation_id, message_id,
                            transaction_type, amount, user_message
                        )
                else:
                    logger.info(f"📋 No financial data detected by {getattr(self, 'parser_type', 'Unknown')} parser")
                
            except Exception as e:
                logger.error(f"❌ Error in financial parsing: {e}")
        else:
            logger.warning("⚠️ No parser available!")
        
        # 6. Regular message handling
        return await self.handlers.handle_regular_message(user_message)
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    def get_parser_info(self) -> Dict[str, Any]:
        """Get detailed parser information"""
        return {
            "parser_type": getattr(self, 'parser_type', 'Unknown'),
            "parser_class": type(self.parser).__name__ if self.parser else 'None',
            "parser_module": self.parser.__class__.__module__ if self.parser else 'None',
            "models_loaded": getattr(self.parser, 'models_loaded', False) if self.parser else False,
            "model_path": getattr(self.parser, 'model_path', None) if self.parser else None,
            "available_methods": [method for method in dir(self.parser) if not method.startswith('_')] if self.parser else [],
            "has_parse_financial_data": hasattr(self.parser, 'parse_financial_data') if self.parser else False,
            "has_parse_amount": hasattr(self.parser, 'parse_amount') if self.parser else False,
            "has_detect_transaction_type": hasattr(self.parser, 'detect_transaction_type') if self.parser else False
        }
    
    def test_parser_with_message(self, test_message: str) -> Dict[str, Any]:
        """Test parser with a specific message"""
        if not self.parser:
            return {
                "error": "No parser available",
                "parser_type": getattr(self, 'parser_type', 'Unknown')
            }
        
        try:
            logger.info(f"🧪 Testing parser with: '{test_message}'")
            result = self.parser.parse_financial_data(test_message)
            result["parser_info"] = {
                "parser_type": getattr(self, 'parser_type', 'Unknown'),
                "parser_class": type(self.parser).__name__,
                "test_message": test_message
            }
            return result
            
        except Exception as e:
            logger.error(f"❌ Parser test failed: {e}")
            return {
                "error": str(e),
                "parser_type": getattr(self, 'parser_type', 'Unknown'),
                "test_message": test_message
            }