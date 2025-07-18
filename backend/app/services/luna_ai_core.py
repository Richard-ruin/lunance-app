# app/services/luna_ai_core.py - Final integrated version with all components
import re
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .luna_ai_base import LunaAIBase
from .luna_ai_handlers import LunaAIHandlers
from .luna_ai_queries import LunaAIQueries


class LunaAICore(LunaAIBase):
    """
    Core Luna AI yang mengintegrasikan semua komponen:
    - Base functionality (detection, extraction, utilities)
    - Handlers (transaction input, CRUD operations)
    - Queries (financial queries, purchase analysis)
    """
    
    def __init__(self):
        super().__init__()
        self.handlers = LunaAIHandlers()
        self.queries = LunaAIQueries()
    
    # ==========================================
    # MAIN RESPONSE GENERATION
    # ==========================================
    
    async def generate_response(self, user_message: str, user_id: str, conversation_id: str, message_id: str) -> str:
        """Generate response dari Luna AI dengan enhanced financial intelligence"""
        message_lower = user_message.lower()
        print(f"🤖 Luna processing: '{user_message}'")
        
        # 1. Check for purchase intent FIRST (high priority)
        purchase_intent = self.is_purchase_intent(user_message)
        if purchase_intent:
            print(f"🛒 Purchase intent detected: {purchase_intent['item_name']} - {purchase_intent['price']}")
            return await self.queries.handle_purchase_intent(user_id, purchase_intent)
        
        # 2. Check for update/delete commands
        update_delete_command = self.is_update_delete_command(user_message)
        if update_delete_command:
            print(f"🔧 Update/Delete command detected: {update_delete_command['action']}")
            return await self.handlers.handle_update_delete_command(user_id, conversation_id, message_id, update_delete_command)
        
        # 3. Check for confirmation (untuk pending financial data)
        confirmation = self.is_confirmation_message(user_message)
        if confirmation is not None:
            print(f"📝 Confirmation detected: {confirmation}")
            return await self.handlers.handle_confirmation(user_id, conversation_id, confirmation)
        
        # 4. Check if it's a financial query
        query_type = self.is_financial_query(user_message)
        if query_type:
            print(f"📊 Financial query detected: {query_type}")
            return await self.queries.handle_financial_query(user_id, query_type)
        
        # 5. Parse untuk data keuangan (transactions & savings goals)
        amount = self.parser.parse_amount(user_message)
        if amount:
            transaction_type = self.parser.detect_transaction_type(user_message)
            if transaction_type:
                print(f"💰 Financial data detected: {transaction_type}, amount: {amount}")
                return await self.handlers.handle_financial_data(
                    user_id, conversation_id, message_id,
                    transaction_type, amount, user_message
                )
        
        # 6. Regular Luna responses
        print("💬 Regular message handling")
        return await self.handlers.handle_regular_message(user_message)
    
    # ==========================================
    # PASS-THROUGH METHODS (for backward compatibility)
    # ==========================================
    
    async def handle_purchase_intent(self, user_id: str, purchase_intent: Dict[str, Any]) -> str:
        """Pass-through to queries handler"""
        return await self.queries.handle_purchase_intent(user_id, purchase_intent)
    
    async def handle_financial_query(self, user_id: str, query_type: str) -> str:
        """Pass-through to queries handler"""
        return await self.queries.handle_financial_query(user_id, query_type)
    
    async def handle_financial_data(self, user_id: str, conversation_id: str, message_id: str,
                                  transaction_type: str, amount: float, original_message: str) -> str:
        """Pass-through to handlers"""
        return await self.handlers.handle_financial_data(
            user_id, conversation_id, message_id, transaction_type, amount, original_message
        )
    
    async def handle_update_delete_command(self, user_id: str, conversation_id: str, message_id: str, command: Dict[str, Any]) -> str:
        """Pass-through to handlers"""
        return await self.handlers.handle_update_delete_command(user_id, conversation_id, message_id, command)
    
    async def handle_confirmation(self, user_id: str, conversation_id: str, confirmed: bool) -> str:
        """Pass-through to handlers"""
        return await self.handlers.handle_confirmation(user_id, conversation_id, confirmed)
    
    async def handle_regular_message(self, user_message: str) -> str:
        """Pass-through to handlers"""
        return await self.handlers.handle_regular_message(user_message)
    
    async def handle_list_savings_goals(self, user_id: str) -> str:
        """Pass-through to handlers"""
        return await self.handlers.handle_list_savings_goals(user_id)
    
    # ==========================================
    # ADDITIONAL UTILITY METHODS
    # ==========================================
    
    async def get_user_financial_context(self, user_id: str) -> Dict[str, Any]:
        """Get financial context untuk chat personalization"""
        try:
            # Use analyzer to get comprehensive financial status
            financial_analysis = await self.queries.analyzer.analyze_user_financial_status(user_id)
            
            if financial_analysis["status"] == "analyzed":
                return {
                    "has_financial_data": True,
                    "total_savings": financial_analysis["current_totals"]["real_total_savings"],
                    "monthly_income": financial_analysis["monthly_income"],
                    "budget_health": financial_analysis["budget_performance"]["budget_health"],
                    "financial_health_level": financial_analysis["health_score"]["level"],
                    "active_goals": financial_analysis["savings_analysis"]["active_goals"],
                    "urgent_goals": len(financial_analysis["savings_analysis"]["urgent_goals"]),
                    "transaction_count": financial_analysis["current_totals"]["transaction_count"],
                    "needs_attention": financial_analysis["budget_performance"]["budget_health"] in ["warning", "critical"]
                }
            else:
                return {
                    "has_financial_data": False,
                    "message": financial_analysis.get("message", "No financial data available")
                }
                
        except Exception as e:
            print(f"❌ Error getting financial context: {e}")
            return {
                "has_financial_data": False,
                "error": str(e)
            }
    
    async def generate_proactive_advice(self, user_id: str) -> Optional[str]:
        """Generate proactive advice berdasarkan kondisi finansial"""
        try:
            # Get financial context
            context = await self.get_user_financial_context(user_id)
            
            if not context["has_financial_data"]:
                return None
            
            # Generate advice based on conditions
            advice_messages = []
            
            # Budget health warnings
            if context["budget_health"] == "critical":
                advice_messages.append("🚨 **Perhatian!** Budget Anda over limit. Segera kurangi pengeluaran!")
            elif context["budget_health"] == "warning":
                advice_messages.append("⚠️ **Hati-hati!** Budget mendekati batas. Monitor spending lebih ketat.")
            
            # Urgent goals reminder
            if context["urgent_goals"] > 0:
                advice_messages.append(f"⏰ **Reminder:** {context['urgent_goals']} target tabungan akan deadline dalam 30 hari!")
            
            # Positive reinforcement
            if context["budget_health"] == "excellent" and context["financial_health_level"] == "excellent":
                advice_messages.append("🎉 **Excellent!** Financial management Anda sangat baik. Pertahankan!")
            
            # Return random advice if any
            if advice_messages:
                return random.choice(advice_messages)
            
            return None
            
        except Exception as e:
            print(f"❌ Error generating proactive advice: {e}")
            return None
    
    def get_response_metadata(self, user_message: str, luna_response: str) -> Dict[str, Any]:
        """Generate metadata untuk response analytics"""
        metadata = {
            "message_type": "regular",
            "contains_financial_data": False,
            "detected_intent": None,
            "confidence": 0.0,
            "processing_time": datetime.now().isoformat()
        }
        
        # Detect message type
        if self.is_purchase_intent(user_message):
            metadata["message_type"] = "purchase_intent"
            metadata["detected_intent"] = "purchase_analysis"
            metadata["confidence"] = 0.8
        elif self.is_update_delete_command(user_message):
            metadata["message_type"] = "crud_command"
            metadata["detected_intent"] = "savings_goal_management"
            metadata["confidence"] = 0.9
        elif self.is_financial_query(user_message):
            metadata["message_type"] = "financial_query"
            metadata["detected_intent"] = "data_inquiry"
            metadata["confidence"] = 0.8
        elif self.parser.parse_amount(user_message):
            metadata["message_type"] = "financial_input"
            metadata["detected_intent"] = "transaction_input"
            metadata["confidence"] = 0.7
        
        # Check if response contains financial data
        if any(phrase in luna_response for phrase in ["detail transaksi", "target tabungan", "ketik **\"ya\"**"]):
            metadata["contains_financial_data"] = True
        
        return metadata
    
    def get_suggested_actions(self, user_message: str, financial_context: Dict[str, Any]) -> List[str]:
        """Generate suggested actions untuk user"""
        suggestions = []
        
        # Based on financial context
        if financial_context.get("has_financial_data"):
            if financial_context.get("needs_attention"):
                suggestions.extend([
                    "Cek performa budget bulan ini",
                    "Lihat pengeluaran terbesar",
                    "Minta tips menghemat"
                ])
            else:
                suggestions.extend([
                    "Lihat progress tabungan",
                    "Analisis pembelian barang",
                    "Cek kesehatan keuangan"
                ])
        else:
            suggestions.extend([
                "Setup budget 50/30/20",
                "Catat transaksi pertama",
                "Buat target tabungan"
            ])
        
        # Based on current message
        if "beli" in user_message.lower():
            suggestions.append("Analisis dampak pembelian")
        elif "tabungan" in user_message.lower():
            suggestions.append("Lihat target tabungan")
        elif "budget" in user_message.lower():
            suggestions.append("Cek performa budget")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    # ==========================================
    # CONVERSATION MANAGEMENT
    # ==========================================
    
    def should_create_new_conversation(self, user_message: str, current_conversation_age: int) -> bool:
        """Determine if new conversation should be created"""
        # Create new conversation if:
        # 1. Current conversation is old (>24 hours)
        # 2. Message is a clear new topic
        # 3. User explicitly asks for new session
        
        if current_conversation_age > 24 * 60 * 60:  # 24 hours in seconds
            return True
        
        new_topic_indicators = [
            "mulai dari awal", "conversation baru", "reset chat",
            "topik baru", "ganti bahasan", "clear history"
        ]
        
        if any(indicator in user_message.lower() for indicator in new_topic_indicators):
            return True
        
        return False
    
    def get_conversation_summary(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary dari conversation untuk analytics"""
        summary = {
            "total_messages": len(messages),
            "user_messages": 0,
            "luna_responses": 0,
            "financial_transactions": 0,
            "savings_goals_created": 0,
            "purchase_analyses": 0,
            "topics_covered": set(),
            "dominant_intent": None
        }
        
        intents = []
        
        for msg in messages:
            if msg.get("sender_type") == "user":
                summary["user_messages"] += 1
                content = msg.get("content", "")
                
                # Detect intents
                if self.is_purchase_intent(content):
                    intents.append("purchase_analysis")
                    summary["purchase_analyses"] += 1
                elif self.parser.parse_amount(content):
                    intents.append("financial_input")
                    summary["financial_transactions"] += 1
                elif self.is_financial_query(content):
                    intents.append("financial_query")
                
                # Track topics
                if "budget" in content.lower():
                    summary["topics_covered"].add("budgeting")
                if "tabungan" in content.lower():
                    summary["topics_covered"].add("savings")
                if "beli" in content.lower():
                    summary["topics_covered"].add("purchasing")
                
            elif msg.get("sender_type") == "luna":
                summary["luna_responses"] += 1
                
                # Count goal creations
                if "target tabungan berhasil dibuat" in msg.get("content", ""):
                    summary["savings_goals_created"] += 1
        
        # Determine dominant intent
        if intents:
            intent_counts = {intent: intents.count(intent) for intent in set(intents)}
            summary["dominant_intent"] = max(intent_counts, key=intent_counts.get)
        
        summary["topics_covered"] = list(summary["topics_covered"])
        
        return summary