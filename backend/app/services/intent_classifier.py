# app/services/intent_classifier.py
import asyncio
from typing import Dict, List, Tuple, Optional
import re
from ..database import get_database
from ..models.ai_intent import AIIntent
from .indonesian_nlp import nlp_service
import logging

logger = logging.getLogger(__name__)

class IntentClassifier:
    def __init__(self):
        self.intents_cache = {}
        self.last_cache_update = None
        
        # Predefined intents
        self.default_intents = {
            'add_expense': {
                'patterns': [
                    'beli makan {amount}',
                    'bayar {category} {amount}',
                    'pengeluaran {category} {amount}',
                    'keluar duit {amount} buat {category}',
                    'transfer {amount}',
                    'top up {amount}',
                ],
                'category': 'transaction',
                'required_entities': ['amount'],
                'actions': ['create_transaction'],
                'confidence_threshold': 0.7
            },
            'add_income': {
                'patterns': [
                    'dapat uang {amount}',
                    'terima {amount}',
                    'pendapatan {amount}',
                    'gaji {amount}',
                    'bonus {amount}',
                    'uang jajan {amount}',
                ],
                'category': 'transaction',
                'required_entities': ['amount'],
                'actions': ['create_transaction'],
                'confidence_threshold': 0.7
            },
            'check_balance': {
                'patterns': [
                    'saldo berapa',
                    'cek saldo',
                    'balance berapa',
                    'uang saya berapa',
                    'duit sisa berapa',
                ],
                'category': 'query',
                'required_entities': [],
                'actions': ['get_balance'],
                'confidence_threshold': 0.8
            },
            'spending_analysis': {
                'patterns': [
                    'analisis pengeluaran',
                    'pengeluaran bulan ini',
                    'spend analysis',
                    'gimana pengeluaran saya',
                    'review spending',
                ],
                'category': 'analysis',
                'required_entities': [],
                'actions': ['analyze_spending'],
                'confidence_threshold': 0.7
            },
            'budget_status': {
                'patterns': [
                    'budget masih aman',
                    'status budget',
                    'cek budget',
                    'budget saya gimana',
                    'masih ada budget',
                ],
                'category': 'analysis',
                'required_entities': [],
                'actions': ['check_budget_status'],
                'confidence_threshold': 0.7
            },
            'create_goal': {
                'patterns': [
                    'pengen nabung buat {item}',
                    'mau saving untuk {item}',
                    'target nabung {item}',
                    'rencana beli {item}',
                ],
                'category': 'goal',
                'required_entities': [],
                'actions': ['create_savings_goal'],
                'confidence_threshold': 0.6
            },
            'greeting': {
                'patterns': [
                    'halo',
                    'hai',
                    'hello',
                    'hi luna',
                    'pagi luna',
                    'siang luna',
                    'malam luna',
                ],
                'category': 'general',
                'required_entities': [],
                'actions': ['greet_user'],
                'confidence_threshold': 0.9
            },
            'help': {
                'patterns': [
                    'bantuin dong',
                    'help',
                    'gimana caranya',
                    'apa aja yang bisa',
                    'fitur apa aja',
                ],
                'category': 'general',
                'required_entities': [],
                'actions': ['show_help'],
                'confidence_threshold': 0.8
            },
            'goodbye': {
                'patterns': [
                    'bye',
                    'dadah',
                    'makasih',
                    'terima kasih',
                    'sampai jumpa',
                ],
                'category': 'general',
                'required_entities': [],
                'actions': ['say_goodbye'],
                'confidence_threshold': 0.8
            }
        }
    
    async def load_intents(self):
        """Load intents from database"""
        try:
            db = await get_database()
            intents = await db.ai_intents.find({"is_active": True}).to_list(None)
            
            self.intents_cache = {}
            for intent in intents:
                self.intents_cache[intent['intent_name']] = intent
            
            logger.info(f"Loaded {len(self.intents_cache)} intents from database")
            
        except Exception as e:
            logger.error(f"Failed to load intents: {e}")
            # Use default intents as fallback
            self.intents_cache = self.default_intents
    
    def calculate_pattern_similarity(self, text: str, pattern: str) -> float:
        """Calculate similarity between text and pattern"""
        text = text.lower().strip()
        pattern = pattern.lower().strip()
        
        # Remove entity placeholders for pattern matching
        pattern_clean = re.sub(r'\{[^}]+\}', '', pattern).strip()
        
        # Simple word overlap scoring
        text_words = set(text.split())
        pattern_words = set(pattern_clean.split())
        
        if not pattern_words:
            return 0.0
        
        overlap = len(text_words.intersection(pattern_words))
        return overlap / len(pattern_words)
    
    async def classify_intent(self, text: str) -> Tuple[Optional[str], float]:
        """Classify intent from user message"""
        if not self.intents_cache:
            await self.load_intents()
        
        best_intent = None
        best_score = 0.0
        
        for intent_name, intent_data in self.intents_cache.items():
            if isinstance(intent_data, dict):
                patterns = intent_data.get('patterns', [])
                threshold = intent_data.get('confidence_threshold', 0.7)
            else:
                # Database format
                patterns = [p.text if hasattr(p, 'text') else p for p in intent_data.get('patterns', [])]
                threshold = intent_data.get('confidence_threshold', 0.7)
            
            max_pattern_score = 0.0
            for pattern in patterns:
                if isinstance(pattern, dict):
                    pattern = pattern.get('text', '')
                score = self.calculate_pattern_similarity(text, pattern)
                max_pattern_score = max(max_pattern_score, score)
            
            if max_pattern_score > best_score and max_pattern_score >= threshold:
                best_score = max_pattern_score
                best_intent = intent_name
        
        return best_intent, best_score
    
    async def get_intent_actions(self, intent_name: str) -> List[str]:
        """Get actions for an intent"""
        if intent_name in self.intents_cache:
            intent_data = self.intents_cache[intent_name]
            if isinstance(intent_data, dict):
                return intent_data.get('actions', [])
            else:
                return intent_data.get('actions', [])
        return []
    
    async def get_intent_responses(self, intent_name: str) -> List[str]:
        """Get response templates for an intent"""
        if intent_name in self.intents_cache:
            intent_data = self.intents_cache[intent_name]
            if isinstance(intent_data, dict):
                return intent_data.get('responses', [])
            else:
                responses = intent_data.get('responses', [])
                return [r.template if hasattr(r, 'template') else r for r in responses]
        return []

# Global instance
intent_classifier = IntentClassifier()