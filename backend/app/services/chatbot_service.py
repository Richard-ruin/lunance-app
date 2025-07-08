# app/services/chatbot_service.py
"""AI Chatbot service with Indonesian language support."""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import re
from bson import ObjectId

from ..config.database import get_database
from ..config.settings import settings
from ..models.ai_chat import (
    ChatMessageCreate, ChatMessageResponse, ChatSessionCreate, ChatSessionResponse,
    ChatHistoryResponse, FinancialContext, AIInsight, MessageRole, MessageType,
    ContextMemory, ChatPreferences, AIModelConfig, CHAT_TEMPLATES
)
from ..models.common import PaginatedResponse, PaginationParams
from ..services.user_service import user_service
from ..services.transaction_service import transaction_service
from ..services.savings_target_service import savings_target_service

logger = logging.getLogger(__name__)


class ChatbotServiceError(Exception):
    """Chatbot service related error."""
    pass


class ChatbotService:
    """AI Chatbot service with financial intelligence."""
    
    def __init__(self):
        self.chat_sessions_collection = "chat_sessions"
        self.chat_messages_collection = "chat_messages"
        self.context_memory_collection = "context_memory"
        
        # Indonesian financial terms dictionary
        self.indonesian_financial_terms = {
            "uang": ["money", "cash", "funds"],
            "tabungan": ["savings", "saved money"],
            "pengeluaran": ["expense", "spending", "expenditure"],
            "pemasukan": ["income", "earning", "revenue"],
            "anggaran": ["budget", "budgeting"],
            "investasi": ["investment", "investing"],
            "hutang": ["debt", "loan"],
            "cicilan": ["installment", "payment"],
            "gaji": ["salary", "wage"],
            "belanja": ["shopping", "purchase"],
            "transfer": ["transfer", "send money"],
            "saldo": ["balance", "account balance"],
            "target": ["goal", "target", "objective"],
            "hemat": ["save", "economical", "frugal"],
            "boros": ["wasteful", "spendthrift"],
            "untung": ["profit", "gain"],
            "rugi": ["loss", "deficit"]
        }
        
        # Common Indonesian expressions for financial queries
        self.financial_query_patterns = {
            "balance_inquiry": [
                r"berapa.*saldo",
                r"cek.*saldo",
                r"saldo.*saya",
                r"uang.*tersisa"
            ],
            "expense_analysis": [
                r"pengeluaran.*bulan.*ini",
                r"habis.*uang.*untuk.*apa",
                r"spending.*analysis",
                r"analisis.*pengeluaran"
            ],
            "savings_advice": [
                r"cara.*menabung",
                r"tips.*hemat",
                r"bagaimana.*saving",
                r"mau.*nabung"
            ],
            "budget_help": [
                r"buat.*anggaran",
                r"budget.*planning",
                r"mengatur.*uang",
                r"financial.*plan"
            ]
        }
    
    async def create_chat_session(
        self,
        user_id: str,
        session_data: ChatSessionCreate
    ) -> ChatSessionResponse:
        """Create new chat session."""
        try:
            db = await get_database()
            collection = db[self.chat_sessions_collection]
            
            session_doc = {
                "user_id": user_id,
                "session_name": session_data.session_name or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                "is_active": session_data.is_active,
                "message_count": 0,
                "last_activity": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await collection.insert_one(session_doc)
            session_id = str(result.inserted_id)
            
            # Initialize context memory for this session
            await self._initialize_context_memory(user_id, session_id)
            
            logger.info(f"Chat session created: {session_id} for user {user_id}")
            
            return ChatSessionResponse(
                id=session_id,
                user_id=user_id,
                session_name=session_doc["session_name"],
                is_active=session_doc["is_active"],
                message_count=0,
                last_activity=session_doc["last_activity"],
                created_at=session_doc["created_at"],
                updated_at=session_doc["updated_at"]
            )
            
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            raise ChatbotServiceError("Failed to create chat session")
    
    async def process_message(
        self,
        user_id: str,
        session_id: str,
        message_data: ChatMessageCreate
    ) -> ChatMessageResponse:
        """Process user message and generate AI response."""
        try:
            # Save user message
            user_message = await self._save_message(
                user_id=user_id,
                session_id=session_id,
                content=message_data.content,
                role=MessageRole.USER,
                message_type=message_data.message_type,
                metadata=message_data.metadata
            )
            
            # Get user's financial context
            financial_context = await self._get_financial_context(user_id)
            
            # Get conversation context
            conversation_context = await self._get_conversation_context(session_id, limit=10)
            
            # Get user preferences
            user_preferences = await self._get_user_preferences(user_id)
            
            # Process message and generate response
            start_time = datetime.utcnow()
            ai_response = await self._generate_ai_response(
                user_message=message_data.content,
                financial_context=financial_context,
                conversation_context=conversation_context,
                user_preferences=user_preferences,
                context_data=message_data.context_data
            )
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Save AI response
            ai_message = await self._save_message(
                user_id=user_id,
                session_id=session_id,
                content=ai_response["content"],
                role=MessageRole.ASSISTANT,
                message_type=ai_response["message_type"],
                metadata=ai_response.get("metadata"),
                tokens_used=ai_response.get("tokens_used"),
                processing_time=processing_time,
                confidence_score=ai_response.get("confidence_score")
            )
            
            # Update context memory
            await self._update_context_memory(user_id, session_id, message_data.content, ai_response["content"])
            
            # Update session activity
            await self._update_session_activity(session_id)
            
            return ai_message
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Return fallback response
            fallback_response = await self._generate_fallback_response(user_id, message_data.content)
            return await self._save_message(
                user_id=user_id,
                session_id=session_id,
                content=fallback_response,
                role=MessageRole.ASSISTANT,
                message_type=MessageType.TEXT,
                metadata={"error": True, "fallback": True}
            )
    
    async def get_chat_history(
        self,
        user_id: str,
        session_id: str,
        pagination: PaginationParams
    ) -> ChatHistoryResponse:
        """Get chat history for a session."""
        try:
            db = await get_database()
            
            # Get session info
            sessions_collection = db[self.chat_sessions_collection]
            session_doc = await sessions_collection.find_one({
                "_id": ObjectId(session_id),
                "user_id": user_id
            })
            
            if not session_doc:
                raise ChatbotServiceError("Chat session not found")
            
            session = ChatSessionResponse(**session_doc, id=str(session_doc["_id"]))
            
            # Get messages
            messages_collection = db[self.chat_messages_collection]
            
            # Build query
            query = {
                "user_id": user_id,
                "session_id": session_id
            }
            
            # Get total count
            total = await messages_collection.count_documents(query)
            
            # Get paginated messages
            skip = (pagination.page - 1) * pagination.per_page
            cursor = messages_collection.find(query).sort("created_at", 1)
            cursor = cursor.skip(skip).limit(pagination.per_page)
            
            messages_docs = await cursor.to_list(length=pagination.per_page)
            
            # Convert to response format
            messages = []
            for msg_doc in messages_docs:
                messages.append(ChatMessageResponse(
                    id=str(msg_doc["_id"]),
                    user_id=msg_doc["user_id"],
                    session_id=msg_doc["session_id"],
                    content=msg_doc["content"],
                    role=MessageRole(msg_doc["role"]),
                    message_type=MessageType(msg_doc["message_type"]),
                    metadata=msg_doc.get("metadata"),
                    tokens_used=msg_doc.get("tokens_used"),
                    processing_time=msg_doc.get("processing_time"),
                    confidence_score=msg_doc.get("confidence_score"),
                    created_at=msg_doc["created_at"]
                ))
            
            return ChatHistoryResponse(
                session=session,
                messages=messages,
                total_messages=total
            )
            
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            raise ChatbotServiceError("Failed to get chat history")
    
    async def list_chat_sessions(
        self,
        user_id: str,
        pagination: PaginationParams,
        is_active: Optional[bool] = None
    ) -> PaginatedResponse[ChatSessionResponse]:
        """List user's chat sessions."""
        try:
            db = await get_database()
            collection = db[self.chat_sessions_collection]
            
            # Build query
            query = {"user_id": user_id}
            if is_active is not None:
                query["is_active"] = is_active
            
            # Get total count
            total = await collection.count_documents(query)
            
            # Get paginated results
            skip = (pagination.page - 1) * pagination.per_page
            cursor = collection.find(query).sort("last_activity", -1)
            cursor = cursor.skip(skip).limit(pagination.per_page)
            
            sessions_docs = await cursor.to_list(length=pagination.per_page)
            
            # Convert to response format
            sessions = []
            for session_doc in sessions_docs:
                sessions.append(ChatSessionResponse(
                    id=str(session_doc["_id"]),
                    user_id=session_doc["user_id"],
                    session_name=session_doc["session_name"],
                    is_active=session_doc["is_active"],
                    message_count=session_doc["message_count"],
                    last_activity=session_doc["last_activity"],
                    created_at=session_doc["created_at"],
                    updated_at=session_doc["updated_at"]
                ))
            
            return PaginatedResponse.create(
                items=sessions,
                total=total,
                page=pagination.page,
                per_page=pagination.per_page
            )
            
        except Exception as e:
            logger.error(f"Error listing chat sessions: {e}")
            raise ChatbotServiceError("Failed to list chat sessions")
    
    async def delete_chat_session(self, user_id: str, session_id: str) -> bool:
        """Delete chat session and all messages."""
        try:
            db = await get_database()
            
            # Delete session
            sessions_collection = db[self.chat_sessions_collection]
            session_result = await sessions_collection.delete_one({
                "_id": ObjectId(session_id),
                "user_id": user_id
            })
            
            if session_result.deleted_count == 0:
                return False
            
            # Delete all messages in session
            messages_collection = db[self.chat_messages_collection]
            await messages_collection.delete_many({
                "user_id": user_id,
                "session_id": session_id
            })
            
            # Delete context memory
            context_collection = db[self.context_memory_collection]
            await context_collection.delete_one({
                "user_id": user_id,
                "session_id": session_id
            })
            
            logger.info(f"Chat session deleted: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting chat session: {e}")
            return False
    
    async def clear_user_chat_history(self, user_id: str) -> bool:
        """Clear all chat history for user."""
        try:
            db = await get_database()
            
            # Delete all sessions
            sessions_collection = db[self.chat_sessions_collection]
            await sessions_collection.delete_many({"user_id": user_id})
            
            # Delete all messages
            messages_collection = db[self.chat_messages_collection]
            await messages_collection.delete_many({"user_id": user_id})
            
            # Delete all context memory
            context_collection = db[self.context_memory_collection]
            await context_collection.delete_many({"user_id": user_id})
            
            logger.info(f"All chat history cleared for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing chat history: {e}")
            return False
    
    async def generate_proactive_insights(self, user_id: str) -> List[AIInsight]:
        """Generate proactive financial insights for user."""
        try:
            financial_context = await self._get_financial_context(user_id)
            insights = []
            
            # Spending pattern insights
            if financial_context.monthly_expense > financial_context.monthly_income * 0.9:
                insights.append(AIInsight(
                    insight_type="spending_warning",
                    title="Peringatan Pengeluaran Tinggi",
                    description="Pengeluaran bulanan Anda mendekati total pemasukan. Pertimbangkan untuk mengurangi pengeluaran di beberapa kategori.",
                    confidence=0.9,
                    priority="high",
                    action_items=[
                        "Review pengeluaran kategori tertinggi",
                        "Buat anggaran bulanan yang lebih ketat",
                        "Cari cara untuk mengurangi biaya rutin"
                    ]
                ))
            
            # Savings opportunity
            if financial_context.current_balance > financial_context.monthly_expense * 2:
                insights.append(AIInsight(
                    insight_type="savings_opportunity",
                    title="Peluang Menabung",
                    description="Anda memiliki saldo yang cukup baik. Pertimbangkan untuk meningkatkan target tabungan atau investasi.",
                    confidence=0.8,
                    priority="medium",
                    action_items=[
                        "Buat target tabungan baru",
                        "Pertimbangkan investasi jangka pendek",
                        "Tingkatkan dana darurat"
                    ]
                ))
            
            # Goal achievement prediction
            if financial_context.savings_targets:
                for target in financial_context.savings_targets:
                    if target.get("progress_percentage", 0) > 80:
                        insights.append(AIInsight(
                            insight_type="goal_achievement",
                            title=f"Target '{target.get('name')}' Hampir Tercapai",
                            description=f"Anda sudah mencapai {target.get('progress_percentage')}% dari target. Pertahankan momentum!",
                            confidence=0.95,
                            priority="high",
                            action_items=[
                                "Pertahankan kontribusi rutin",
                                "Siapkan target baru setelah ini tercapai"
                            ]
                        ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating proactive insights: {e}")
            return []
    
    # Private helper methods
    async def _save_message(
        self,
        user_id: str,
        session_id: str,
        content: str,
        role: MessageRole,
        message_type: MessageType = MessageType.TEXT,
        metadata: Optional[Dict[str, Any]] = None,
        tokens_used: Optional[int] = None,
        processing_time: Optional[float] = None,
        confidence_score: Optional[float] = None
    ) -> ChatMessageResponse:
        """Save message to database."""
        try:
            db = await get_database()
            collection = db[self.chat_messages_collection]
            
            message_doc = {
                "user_id": user_id,
                "session_id": session_id,
                "content": content,
                "role": role.value,
                "message_type": message_type.value,
                "metadata": metadata or {},
                "tokens_used": tokens_used,
                "processing_time": processing_time,
                "confidence_score": confidence_score,
                "created_at": datetime.utcnow()
            }
            
            result = await collection.insert_one(message_doc)
            message_id = str(result.inserted_id)
            
            # Update session message count
            sessions_collection = db[self.chat_sessions_collection]
            await sessions_collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$inc": {"message_count": 1}}
            )
            
            return ChatMessageResponse(
                id=message_id,
                user_id=user_id,
                session_id=session_id,
                content=content,
                role=role,
                message_type=message_type,
                metadata=metadata or {},
                tokens_used=tokens_used,
                processing_time=processing_time,
                confidence_score=confidence_score,
                created_at=message_doc["created_at"]
            )
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise ChatbotServiceError("Failed to save message")
    
    async def _get_financial_context(self, user_id: str) -> FinancialContext:
        """Get user's financial context for AI processing."""
        try:
            # Get user stats
            user_stats = await user_service.get_user_stats(user_id)
            
            # Get recent transactions
            from ..models.common import PaginationParams
            recent_transactions_result = await transaction_service.list_transactions(
                user_id=user_id,
                pagination=PaginationParams(page=1, per_page=10, sort_by="created_at", sort_order="desc"),
                filters=None
            )
            
            # Get savings targets
            savings_targets_result = await savings_target_service.list_savings_targets(
                user_id=user_id,
                pagination=PaginationParams(page=1, per_page=5),
                is_achieved=False
            )
            
            # Get category summary
            category_summary = await transaction_service.get_category_summary(
                user_id=user_id,
                transaction_type=None
            )
            
            # Calculate monthly averages (rough estimates)
            monthly_income = user_stats.total_income / 12 if user_stats else 0
            monthly_expense = user_stats.total_expense / 12 if user_stats else 0
            
            return FinancialContext(
                current_balance=user_stats.current_balance if user_stats else 0,
                monthly_income=monthly_income,
                monthly_expense=monthly_expense,
                top_categories=[
                    {
                        "name": cat.category_name,
                        "amount": cat.total_amount,
                        "percentage": cat.percentage
                    }
                    for cat in category_summary[:5]
                ],
                savings_targets=[
                    {
                        "name": target.target_name,
                        "progress_percentage": target.progress_percentage,
                        "current_amount": target.current_amount,
                        "target_amount": target.target_amount
                    }
                    for target in savings_targets_result.items
                ],
                recent_transactions=[
                    {
                        "description": trans.description,
                        "amount": trans.amount,
                        "type": trans.transaction_type.value,
                        "category": trans.category_name,
                        "date": trans.transaction_date.isoformat()
                    }
                    for trans in recent_transactions_result.items
                ]
            )
            
        except Exception as e:
            logger.error(f"Error getting financial context: {e}")
            return FinancialContext(
                current_balance=0,
                monthly_income=0,
                monthly_expense=0,
                top_categories=[],
                savings_targets=[],
                recent_transactions=[]
            )
    
    async def _generate_ai_response(
        self,
        user_message: str,
        financial_context: FinancialContext,
        conversation_context: List[str],
        user_preferences: ChatPreferences,
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate AI response using financial intelligence."""
        try:
            # Detect message intent and type
            message_type, intent = self._detect_message_intent(user_message)
            
            # Generate appropriate response based on intent
            if intent == "balance_inquiry":
                response_content = await self._generate_balance_response(financial_context, user_preferences.language)
            elif intent == "expense_analysis":
                response_content = await self._generate_expense_analysis(financial_context, user_preferences.language)
            elif intent == "savings_advice":
                response_content = await self._generate_savings_advice(financial_context, user_preferences.language)
            elif intent == "budget_help":
                response_content = await self._generate_budget_help(financial_context, user_preferences.language)
            else:
                response_content = await self._generate_general_response(
                    user_message, financial_context, conversation_context, user_preferences.language
                )
            
            return {
                "content": response_content,
                "message_type": message_type,
                "confidence_score": 0.85,
                "tokens_used": len(response_content.split()) * 1.3,  # Rough estimate
                "metadata": {
                    "intent": intent,
                    "language": user_preferences.language,
                    "context_used": bool(financial_context.recent_transactions)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                "content": CHAT_TEMPLATES["error_fallback"][user_preferences.language],
                "message_type": MessageType.TEXT,
                "confidence_score": 0.5,
                "metadata": {"error": True}
            }
    
    def _detect_message_intent(self, message: str) -> Tuple[MessageType, str]:
        """Detect user message intent."""
        message_lower = message.lower()
        
        # Check for financial query patterns
        for intent, patterns in self.financial_query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    message_type_map = {
                        "balance_inquiry": MessageType.TEXT,
                        "expense_analysis": MessageType.SPENDING_ANALYSIS,
                        "savings_advice": MessageType.FINANCIAL_ADVICE,
                        "budget_help": MessageType.BUDGET_RECOMMENDATION
                    }
                    return message_type_map.get(intent, MessageType.TEXT), intent
        
        return MessageType.TEXT, "general"
    
    async def _generate_balance_response(self, context: FinancialContext, language: str) -> str:
        """Generate balance inquiry response."""
        if language == "id":
            return f"""Saldo Anda saat ini adalah Rp {context.current_balance:,.0f}.

📊 Ringkasan Keuangan:
• Rata-rata pemasukan bulanan: Rp {context.monthly_income:,.0f}
• Rata-rata pengeluaran bulanan: Rp {context.monthly_expense:,.0f}
• Selisih bulanan: Rp {context.monthly_income - context.monthly_expense:,.0f}

{'✅ Keuangan Anda dalam kondisi baik!' if context.current_balance > context.monthly_expense * 3 else '⚠️ Pertimbangkan untuk meningkatkan tabungan Anda.'}"""
        else:
            return f"""Your current balance is Rp {context.current_balance:,.0f}.

📊 Financial Summary:
• Average monthly income: Rp {context.monthly_income:,.0f}
• Average monthly expense: Rp {context.monthly_expense:,.0f}
• Monthly difference: Rp {context.monthly_income - context.monthly_expense:,.0f}

{'✅ Your finances are in good shape!' if context.current_balance > context.monthly_expense * 3 else '⚠️ Consider increasing your savings.'}"""
    
    async def _generate_expense_analysis(self, context: FinancialContext, language: str) -> str:
        """Generate expense analysis response."""
        if not context.top_categories:
            if language == "id":
                return "Belum ada data pengeluaran yang cukup untuk dianalisis. Mulai catat transaksi Anda untuk mendapatkan insight yang lebih baik!"
            else:
                return "Not enough expense data to analyze yet. Start recording your transactions to get better insights!"
        
        if language == "id":
            response = f"📈 Analisis Pengeluaran Anda:\n\nTotal pengeluaran bulanan: Rp {context.monthly_expense:,.0f}\n\n🏆 Kategori pengeluaran terbesar:\n"
            for i, cat in enumerate(context.top_categories[:3], 1):
                response += f"{i}. {cat['name']}: Rp {cat['amount']:,.0f} ({cat['percentage']:.1f}%)\n"
            
            response += "\n💡 Saran:\n"
            if context.top_categories[0]['percentage'] > 40:
                response += f"• Kategori '{context.top_categories[0]['name']}' menghabiskan {context.top_categories[0]['percentage']:.1f}% dari total pengeluaran. Coba kurangi pengeluaran di kategori ini.\n"
            response += "• Review pengeluaran rutin bulanan\n• Bandingkan dengan bulan sebelumnya\n• Buat target pengurangan untuk kategori tertinggi"
        else:
            response = f"📈 Your Expense Analysis:\n\nTotal monthly expenses: Rp {context.monthly_expense:,.0f}\n\n🏆 Top spending categories:\n"
            for i, cat in enumerate(context.top_categories[:3], 1):
                response += f"{i}. {cat['name']}: Rp {cat['amount']:,.0f} ({cat['percentage']:.1f}%)\n"
            
            response += "\n💡 Suggestions:\n"
            if context.top_categories[0]['percentage'] > 40:
                response += f"• '{context.top_categories[0]['name']}' accounts for {context.top_categories[0]['percentage']:.1f}% of total expenses. Try reducing spending in this category.\n"
            response += "• Review monthly recurring expenses\n• Compare with previous months\n• Set reduction targets for top categories"
        
        return response
    
    async def _generate_savings_advice(self, context: FinancialContext, language: str) -> str:
        """Generate savings advice response."""
        savings_rate = (context.monthly_income - context.monthly_expense) / context.monthly_income * 100 if context.monthly_income > 0 else 0
        
        if language == "id":
            response = f"💰 Tips Menabung untuk Anda:\n\n📊 Tingkat tabungan saat ini: {savings_rate:.1f}%\n"
            
            if savings_rate < 10:
                response += "\n🚨 Tingkat tabungan Anda masih rendah. Berikut tips untuk meningkatkannya:\n"
                response += "• Terapkan aturan 50/30/20 (50% kebutuhan, 30% keinginan, 20% tabungan)\n"
                response += "• Mulai dengan menabung Rp 10,000 per hari\n"
                response += "• Kurangi pengeluaran di kategori 'keinginan'\n"
                response += "• Cari sumber penghasilan tambahan"
            elif savings_rate < 20:
                response += "\n✅ Tingkat tabungan Anda sudah baik! Tips untuk meningkatkan:\n"
                response += "• Target naik menjadi 20-25%\n"
                response += "• Otomatisasi transfer ke tabungan\n"
                response += "• Buat target tabungan spesifik"
            else:
                response += "\n🌟 Excellent! Tingkat tabungan Anda sangat baik. Pertimbangkan:\n"
                response += "• Diversifikasi investasi\n"
                response += "• Buat dana darurat 6-12 bulan\n"
                response += "• Investasi jangka panjang"
            
            if context.savings_targets:
                response += f"\n🎯 Target tabungan aktif: {len(context.savings_targets)} target\n"
                for target in context.savings_targets[:2]:
                    response += f"• {target['name']}: {target['progress_percentage']:.1f}% tercapai\n"
        else:
            response = f"💰 Savings Tips for You:\n\n📊 Current savings rate: {savings_rate:.1f}%\n"
            
            if savings_rate < 10:
                response += "\n🚨 Your savings rate is low. Here are tips to improve:\n"
                response += "• Apply the 50/30/20 rule (50% needs, 30% wants, 20% savings)\n"
                response += "• Start by saving Rp 10,000 per day\n"
                response += "• Reduce spending on 'wants' categories\n"
                response += "• Find additional income sources"
            elif savings_rate < 20:
                response += "\n✅ Your savings rate is good! Tips to improve:\n"
                response += "• Target to reach 20-25%\n"
                response += "• Automate transfers to savings\n"
                response += "• Set specific savings goals"
            else:
                response += "\n🌟 Excellent! Your savings rate is very good. Consider:\n"
                response += "• Diversify investments\n"
                response += "• Build 6-12 months emergency fund\n"
                response += "• Long-term investments"
            
            if context.savings_targets:
                response += f"\n🎯 Active savings targets: {len(context.savings_targets)} targets\n"
                for target in context.savings_targets[:2]:
                    response += f"• {target['name']}: {target['progress_percentage']:.1f}% achieved\n"
        
        return response
    
    async def _generate_budget_help(self, context: FinancialContext, language: str) -> str:
        """Generate budget planning help."""
        if language == "id":
            response = "📋 Panduan Membuat Anggaran:\n\n"
            response += f"💰 Pemasukan bulanan: Rp {context.monthly_income:,.0f}\n"
            response += f"💸 Pengeluaran bulanan: Rp {context.monthly_expense:,.0f}\n\n"
            
            response += "📊 Rekomendasi Alokasi Anggaran:\n"
            response += f"• Kebutuhan pokok (50%): Rp {context.monthly_income * 0.5:,.0f}\n"
            response += f"• Keinginan (30%): Rp {context.monthly_income * 0.3:,.0f}\n"
            response += f"• Tabungan & Investasi (20%): Rp {context.monthly_income * 0.2:,.0f}\n\n"
            
            response += "🎯 Langkah-langkah:\n"
            response += "1. Catat semua pemasukan dan pengeluaran\n"
            response += "2. Kategorikan pengeluaran (kebutuhan vs keinginan)\n"
            response += "3. Tetapkan batas untuk setiap kategori\n"
            response += "4. Monitor dan evaluasi setiap minggu\n"
            response += "5. Sesuaikan jika diperlukan"
        else:
            response = "📋 Budget Planning Guide:\n\n"
            response += f"💰 Monthly income: Rp {context.monthly_income:,.0f}\n"
            response += f"💸 Monthly expenses: Rp {context.monthly_expense:,.0f}\n\n"
            
            response += "📊 Recommended Budget Allocation:\n"
            response += f"• Needs (50%): Rp {context.monthly_income * 0.5:,.0f}\n"
            response += f"• Wants (30%): Rp {context.monthly_income * 0.3:,.0f}\n"
            response += f"• Savings & Investment (20%): Rp {context.monthly_income * 0.2:,.0f}\n\n"
            
            response += "🎯 Steps:\n"
            response += "1. Record all income and expenses\n"
            response += "2. Categorize expenses (needs vs wants)\n"
            response += "3. Set limits for each category\n"
            response += "4. Monitor and evaluate weekly\n"
            response += "5. Adjust as needed"
        
        return response
    
    async def _generate_general_response(
        self,
        message: str,
        context: FinancialContext,
        conversation_context: List[str],
        language: str
    ) -> str:
        """Generate general response for non-specific queries."""
        # This is a simplified implementation
        # In a real scenario, you would use a more sophisticated NLP model
        
        if language == "id":
            return f"Terima kasih atas pertanyaan Anda! Sebagai asisten keuangan, saya di sini untuk membantu Anda mengelola keuangan dengan lebih baik. Anda bisa bertanya tentang:\n\n• Analisis pengeluaran\n• Tips menabung\n• Perencanaan anggaran\n• Progress target tabungan\n• Cek saldo dan transaksi\n\nApa yang ingin Anda ketahui tentang keuangan Anda hari ini?"
        else:
            return f"Thank you for your question! As your financial assistant, I'm here to help you manage your finances better. You can ask about:\n\n• Expense analysis\n• Savings tips\n• Budget planning\n• Savings target progress\n• Balance and transaction checks\n\nWhat would you like to know about your finances today?"
    
    async def _generate_fallback_response(self, user_id: str, message: str) -> str:
        """Generate fallback response when AI processing fails."""
        user = await user_service.get_user_by_id(user_id)
        language = "id"  # Default to Indonesian
        
        return CHAT_TEMPLATES["error_fallback"][language]
    
    async def _get_conversation_context(self, session_id: str, limit: int = 10) -> List[str]:
        """Get recent conversation context."""
        try:
            db = await get_database()
            collection = db[self.chat_messages_collection]
            
            cursor = collection.find({"session_id": session_id}).sort("created_at", -1).limit(limit)
            messages = await cursor.to_list(length=limit)
            
            return [msg["content"] for msg in reversed(messages)]
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return []
    
    async def _get_user_preferences(self, user_id: str) -> ChatPreferences:
        """Get user chat preferences."""
        # This would typically come from a user preferences collection
        # For now, return defaults
        return ChatPreferences()
    
    async def _initialize_context_memory(self, user_id: str, session_id: str):
        """Initialize context memory for new session."""
        try:
            db = await get_database()
            collection = db[self.context_memory_collection]
            
            memory_doc = {
                "user_id": user_id,
                "session_id": session_id,
                "user_goals": [],
                "preferences": {},
                "conversation_context": [],
                "financial_situation": None,
                "last_advice_given": None,
                "interaction_patterns": {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await collection.insert_one(memory_doc)
            
        except Exception as e:
            logger.error(f"Error initializing context memory: {e}")
    
    async def _update_context_memory(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        ai_response: str
    ):
        """Update context memory with new conversation."""
        try:
            db = await get_database()
            collection = db[self.context_memory_collection]
            
            # Update conversation context (keep last 20 exchanges)
            await collection.update_one(
                {"user_id": user_id, "session_id": session_id},
                {
                    "$push": {
                        "conversation_context": {
                            "$each": [user_message, ai_response],
                            "$slice": -20
                        }
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating context memory: {e}")
    
    async def _update_session_activity(self, session_id: str):
        """Update session last activity."""
        try:
            db = await get_database()
            collection = db[self.chat_sessions_collection]
            
            await collection.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "last_activity": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error updating session activity: {e}")


# Global chatbot service instance
chatbot_service = ChatbotService()