# app/services/luna_ai.py
import asyncio
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from ..database import get_database
from ..models.chat_message import ChatResponse, MessageEntity
from .indonesian_nlp import nlp_service
from .intent_classifier import intent_classifier
from .financial_actions import financial_actions_service

logger = logging.getLogger(__name__)

class LunaAIService:
    def __init__(self):
        self.conversation_context = {}
        
        # Response templates
        self.response_templates = {
            'greeting': [
                "Halo! Saya Luna, asisten keuangan Anda. Ada yang bisa saya bantu hari ini? 😊",
                "Hi! Saya di sini untuk membantu mengatur keuangan Anda. Mau ngapain nih? 💰",
                "Halo! Luna siap membantu urusan keuangan Anda. Ada transaksi baru? 📊"
            ],
            'transaction_added': [
                "Tercatat! {transaction_type} {category} {amount} untuk {date}. {additional_info}",
                "Oke, sudah saya catat {transaction_type} {amount} untuk {category}. {budget_info}",
                "Siap! {transaction_type} {amount} di kategori {category} sudah masuk. {suggestion}"
            ],
            'balance_info': [
                "Saldo Anda saat ini: {balance}. {additional_info}",
                "Balance terkini: {balance}. {spending_insight}",
                "Uang Anda sekarang: {balance}. {suggestion}"
            ],
            'spending_analysis': [
                "Berdasarkan analisis pengeluaran Anda: {analysis_result}",
                "Saya lihat pola pengeluaran Anda: {patterns}. {recommendations}",
                "Analisis spending bulan ini: {summary}. {actionable_advice}"
            ],
            'budget_status': [
                "Status budget Anda: {status}. {details}",
                "Budget check: {budget_summary}. {alert_if_needed}",
                "Update budget: {current_usage}. {recommendation}"
            ],
            'goal_created': [
                "Goal '{goal_name}' berhasil dibuat! Target: {amount} dalam {timeframe}. {motivation}",
                "Savings goal baru: {goal_name} - {amount}. {strategy_suggestion}",
                "Perfect! Goal {goal_name} sudah diset. {progress_info}"
            ],
            'help': [
                "Saya bisa bantu:\n• Catat transaksi: 'Beli makan 25ribu'\n• Cek saldo: 'Saldo berapa?'\n• Analisis: 'Pengeluaran bulan ini gimana?'\n• Set goal: 'Pengen nabung buat laptop'",
                "Luna bisa:\n📝 Input transaksi otomatis\n📊 Analisis keuangan\n🎯 Bantu set savings goal\n💡 Kasih saran finansial\n\nMau coba yang mana?",
                "Fitur Luna:\n• Smart transaction input\n• Financial analysis\n• Budget monitoring\n• Savings goal tracker\n• Personal finance advice\n\nAda yang mau dicoba?"
            ],
            'goodbye': [
                "Sampai jumpa! Jangan lupa kelola keuangan dengan bijak ya! 💙",
                "Bye! Semoga keuangan Anda selalu sehat dan terus berkembang! 🌟",
                "Dadah! Luna akan selalu di sini kalau butuh bantuan keuangan. Take care! 💰"
            ],
            'fallback': [
                "Maaf, saya kurang paham. Bisa dijelaskan lagi atau ketik 'help' untuk melihat apa yang bisa saya lakukan?",
                "Hmm, saya belum mengerti maksudnya. Coba ketik 'help' untuk lihat fitur saya ya! 🤔",
                "Sorry, bisa diulang dengan kata-kata yang berbeda? Atau ketik 'help' untuk panduan."
            ]
        }
    
    async def process_message(
        self, 
        user_id: str, 
        session_id: str, 
        message: str,
        context: Dict[str, Any] = None
    ) -> ChatResponse:
        """Process user message and generate AI response"""
        start_time = datetime.now()
        
        try:
            # Extract entities
            entities = await nlp_service.extract_entities(message)
            
            # Analyze sentiment
            sentiment, sentiment_score = await nlp_service.analyze_sentiment(message)
            
            # Classify intent
            intent, confidence = await intent_classifier.classify_intent(message)
            
            # Get or create conversation context
            conversation_context = context or {}
            
            # Process based on intent
            if intent:
                response = await self._handle_intent(
                    intent, entities, user_id, conversation_context
                )
            else:
                response = self._generate_fallback_response()
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create response object
            chat_response = ChatResponse(
                message=response['message'],
                intent=intent,
                entities=[MessageEntity(**entity) for entity in entities],
                actions_performed=response.get('actions', []),
                suggestions=response.get('suggestions', []),
                context=response.get('context', {}),
                confidence=confidence,
                processing_time=processing_time
            )
            
            return chat_response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return ChatResponse(
                message="Maaf, terjadi error. Silakan coba lagi.",
                intent=None,
                entities=[],
                actions_performed=[],
                suggestions=[],
                context={},
                confidence=0.0,
                processing_time=0.0
            )
    
    async def _handle_intent(
        self, 
        intent: str, 
        entities: List[Dict], 
        user_id: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle specific intent"""
        
        if intent == 'greeting':
            return await self._handle_greeting(user_id, context)
        
        elif intent == 'add_expense' or intent == 'add_income':
            return await self._handle_transaction(intent, entities, user_id, context)
        
        elif intent == 'check_balance':
            return await self._handle_balance_check(user_id, context)
        
        elif intent == 'spending_analysis':
            return await self._handle_spending_analysis(user_id, context)
        
        elif intent == 'budget_status':
            return await self._handle_budget_status(user_id, context)
        
        elif intent == 'create_goal':
            return await self._handle_goal_creation(entities, user_id, context)
        
        elif intent == 'help':
            return await self._handle_help()
        
        elif intent == 'goodbye':
            return await self._handle_goodbye()
        
        else:
            return self._generate_fallback_response()
    
    async def _handle_greeting(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greeting intent"""
        # Get user info for personalization
        user_info = await financial_actions_service.get_user_summary(user_id)
        
        greeting_template = random.choice(self.response_templates['greeting'])
        
        # Add personalized touch based on time or recent activity
        current_hour = datetime.now().hour
        if current_hour < 12:
            time_greeting = "Selamat pagi! "
        elif current_hour < 17:
            time_greeting = "Selamat siang! "
        else:
            time_greeting = "Selamat malam! "
        
        message = time_greeting + greeting_template
        
        return {
            'message': message,
            'actions': ['greet_user'],
            'suggestions': [
                "Cek saldo saya",
                "Analisis pengeluaran bulan ini",
                "Catat pengeluaran baru"
            ],
            'context': {'greeted': True}
        }
    
    async def _handle_transaction(
        self, intent: str, entities: List[Dict], user_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle transaction creation"""
        
        # Extract transaction data from entities
        amount = None
        category = None
        date = None
        transaction_type = 'expense' if intent == 'add_expense' else 'income'
        
        for entity in entities:
            if entity['entity_type'] == 'amount':
                amount = entity['value']
            elif entity['entity_type'] == 'category':
                category = entity['value']
            elif entity['entity_type'] == 'date':
                date = entity['value']
            elif entity['entity_type'] == 'transaction_type':
                transaction_type = entity['value']
        
        if not amount:
            return {
                'message': "Berapa jumlahnya? Contoh: 'Beli makan 25ribu'",
                'actions': [],
                'suggestions': ["25ribu", "50ribu", "100ribu"],
                'context': {'awaiting_amount': True, 'transaction_type': transaction_type}
            }
        
        # Create transaction
        transaction_result = await financial_actions_service.create_transaction(
            user_id=user_id,
            amount=amount,
            category=category or 'other',
            transaction_type=transaction_type,
            date=date
        )
        
        if transaction_result['success']:
            # Generate response with additional insights
            template = random.choice(self.response_templates['transaction_added'])
            
            additional_info = ""
            if transaction_result.get('budget_alert'):
                additional_info = f" ⚠️ {transaction_result['budget_alert']}"
            elif transaction_result.get('spending_insight'):
                additional_info = f" 📊 {transaction_result['spending_insight']}"
            
            message = template.format(
                transaction_type="Pengeluaran" if transaction_type == "expense" else "Pemasukan",
                category=category or "lainnya",
                amount=f"Rp{amount:,.0f}",
                date="hari ini",
                additional_info=additional_info,
                budget_info="",
                suggestion=""
            )
            
            return {
                'message': message,
                'actions': ['create_transaction'],
                'suggestions': transaction_result.get('suggestions', []),
                'context': {'last_transaction': transaction_result['transaction_id']}
            }
        else:
            return {
                'message': f"Gagal mencatat transaksi: {transaction_result.get('error', 'Unknown error')}",
                'actions': [],
                'suggestions': ["Coba lagi", "Cek format input"],
                'context': {}
            }
    
    async def _handle_balance_check(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle balance inquiry"""
        
        balance_info = await financial_actions_service.get_current_balance(user_id)
        
        template = random.choice(self.response_templates['balance_info'])
        
        additional_info = ""
        if balance_info.get('recent_spending'):
            additional_info = f" Pengeluaran 7 hari terakhir: Rp{balance_info['recent_spending']:,.0f}"
        
        message = template.format(
            balance=f"Rp{balance_info['balance']:,.0f}",
            additional_info=additional_info,
            spending_insight="",
            suggestion=""
        )
        
        suggestions = ["Analisis pengeluaran", "Lihat transaksi terbaru"]
        if balance_info['balance'] > 100000:
            suggestions.append("Set savings goal")
        
        return {
            'message': message,
            'actions': ['get_balance'],
            'suggestions': suggestions,
            'context': {'current_balance': balance_info['balance']}
        }
    
    async def _handle_spending_analysis(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle spending analysis request"""
        
        analysis = await financial_actions_service.analyze_spending(user_id)
        
        template = random.choice(self.response_templates['spending_analysis'])
        
        # Build analysis result text
        analysis_text = f"Total pengeluaran bulan ini: Rp{analysis['total_spending']:,.0f}"
        
        if analysis.get('top_categories'):
            top_cat = analysis['top_categories'][0]
            analysis_text += f"\n🔸 Terbesar: {top_cat['name']} (Rp{top_cat['amount']:,.0f})"
        
        if analysis.get('comparison'):
            comparison = analysis['comparison']
            if comparison['change'] > 0:
                analysis_text += f"\n📈 Naik {comparison['change']:.1f}% dari bulan lalu"
            else:
                analysis_text += f"\n📉 Turun {abs(comparison['change']):.1f}% dari bulan lalu"
        
        recommendations = ""
        if analysis.get('recommendations'):
            recommendations = "\n\n💡 Saran: " + "; ".join(analysis['recommendations'][:2])
        
        message = template.format(
            analysis_result=analysis_text,
            patterns="",
            recommendations=recommendations,
            summary="",
            actionable_advice=""
        )
        
        return {
            'message': message,
            'actions': ['analyze_spending'],
            'suggestions': ["Lihat detail per kategori", "Set budget baru", "Export laporan"],
            'context': {'analysis_data': analysis}
        }
    
    async def _handle_budget_status(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle budget status check"""
        
        budget_status = await financial_actions_service.get_budget_status(user_id)
        
        template = random.choice(self.response_templates['budget_status'])
        
        status_text = ""
        alert_text = ""
        
        for budget in budget_status.get('budgets', []):
            usage_pct = (budget['used'] / budget['amount']) * 100
            status = "AMAN" if usage_pct < 70 else "PERHATIAN" if usage_pct < 90 else "OVER"
            
            status_text += f"\n• {budget['category']}: {usage_pct:.1f}% ({status})"
            
            if usage_pct > 80:
                alert_text += f" ⚠️ {budget['category']} sudah {usage_pct:.1f}%"
        
        message = template.format(
            status=status_text,
            details="",
            budget_summary=status_text,
            alert_if_needed=alert_text,
            current_usage=status_text,
            recommendation=""
        )
        
        return {
            'message': message,
            'actions': ['check_budget_status'],
            'suggestions': ["Adjust budget", "Lihat tips hemat", "Set alert"],
            'context': {'budget_data': budget_status}
        }
    
    async def _handle_goal_creation(
        self, entities: List[Dict], user_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle savings goal creation"""
        
        # This would need more sophisticated entity extraction for goal items
        # For now, return a guided response
        
        return {
            'message': "Keren! Mau nabung untuk apa? Dan kira-kira butuh berapa untuk mencapainya? 🎯\n\nContoh: 'Pengen nabung buat laptop 15 juta'",
            'actions': [],
            'suggestions': ["Laptop 15 juta", "Motor 18 juta", "Liburan 5 juta"],
            'context': {'creating_goal': True}
        }
    
    async def _handle_help(self) -> Dict[str, Any]:
        """Handle help request"""
        
        help_message = random.choice(self.response_templates['help'])
        
        return {
            'message': help_message,
            'actions': ['show_help'],
            'suggestions': [
                "Beli makan 25ribu",
                "Saldo berapa?",
                "Analisis bulan ini",
                "Set goal baru"
            ],
            'context': {'help_shown': True}
        }
    
    async def _handle_goodbye(self) -> Dict[str, Any]:
        """Handle goodbye"""
        
        goodbye_message = random.choice(self.response_templates['goodbye'])
        
        return {
            'message': goodbye_message,
            'actions': ['say_goodbye'],
            'suggestions': [],
            'context': {'conversation_ended': True}
        }
    
    def _generate_fallback_response(self) -> Dict[str, Any]:
        """Generate fallback response for unrecognized input"""
        
        fallback_message = random.choice(self.response_templates['fallback'])
        
        return {
            'message': fallback_message,
            'actions': [],
            'suggestions': [
                "help",
                "Beli makan 25ribu",
                "Saldo berapa?",
                "Analisis pengeluaran"
            ],
            'context': {}
        }

# Global instance
luna_ai = LunaAIService()