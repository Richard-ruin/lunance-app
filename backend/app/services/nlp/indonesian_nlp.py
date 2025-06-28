# app/services/nlp/indonesian_nlp.py
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from transformers import AutoTokenizer, AutoModel, pipeline
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class IndonesianNLPService:
    def __init__(self):
        self.model_name = "indobenchmark/indobert-base-p1"
        self.tokenizer = None
        self.model = None
        self.sentiment_analyzer = None
        self.is_initialized = False
        
        # Indonesian financial keywords and patterns
        self.finance_keywords = {
            "expense": ["pengeluaran", "keluar", "bayar", "beli", "belanja", "spend", "buat", "untuk"],
            "income": ["pendapatan", "masuk", "dapat", "terima", "gaji", "uang", "income", "pemasukan"],
            "budget": ["budget", "anggaran", "batasan", "limit", "rencana"],
            "savings": ["tabungan", "nabung", "simpan", "save", "hemat"],
            "balance": ["saldo", "balance", "total", "jumlah"],
            "category": ["kategori", "jenis", "tipe", "macam"],
            "help": ["bantuan", "help", "tolong", "gimana", "bagaimana", "cara"]
        }
        
        # Intent patterns
        self.intent_patterns = {
            "ask_balance": [
                r"saldo\s*(saya|ku)?",
                r"berapa\s*(saldo|uang|balance)",
                r"total\s*(uang|balance|saldo)",
                r"cek\s*(saldo|balance)"
            ],
            "expense_query": [
                r"pengeluaran\s*(saya|ku)?\s*(hari\s*ini|kemarin|minggu\s*ini|bulan\s*ini)?",
                r"berapa\s*(pengeluaran|keluar|spend)",
                r"habis\s*(berapa|uang)",
                r"beli\s*(apa|berapa)"
            ],
            "budget_help": [
                r"budget\s*(saya|ku)?",
                r"anggaran\s*(saya|ku)?",
                r"atur\s*(budget|anggaran)",
                r"batasan\s*(pengeluaran|budget)"
            ],
            "savings_advice": [
                r"cara\s*(nabung|hemat|save)",
                r"tips\s*(hemat|nabung)",
                r"gimana\s*(nabung|hemat)",
                r"saran\s*(tabungan|hemat)"
            ],
            "add_transaction": [
                r"catat\s*(pengeluaran|pemasukan|transaksi)",
                r"input\s*(transaksi|pengeluaran)",
                r"tambah\s*(transaksi|pengeluaran)",
                r"baru\s*(beli|bayar|dapat|terima)"
            ]
        }
        
        # Category keywords
        self.category_keywords = {
            "food": ["makan", "makanan", "minum", "minuman", "jajan", "snack", "warung", "restaurant", "kantin"],
            "transportation": ["transport", "transportasi", "ojol", "gojek", "grab", "bus", "kereta", "bensin"],
            "academic": ["kuliah", "kampus", "buku", "fotokopi", "tugas", "praktikum", "ukt", "spp"],
            "entertainment": ["nonton", "game", "musik", "hiburan", "main", "jalan"],
            "health": ["obat", "dokter", "rumah sakit", "kesehatan", "vitamin"],
            "shopping": ["belanja", "baju", "sepatu", "kosmetik", "skincare"]
        }
        
        # Amount patterns
        self.amount_patterns = [
            r"(\d+\.?\d*)\s*(ribu|rb|k)",
            r"(\d+\.?\d*)\s*(juta|jt|m)",
            r"Rp\.?\s*(\d+\.?\d*)",
            r"(\d{1,3}(?:\.\d{3})*)"
        ]
        
    async def initialize(self):
        """Initialize the NLP models"""
        try:
            logger.info("Initializing Indonesian NLP models...")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            
            # Load sentiment analyzer
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="ayameRushia/bert-base-indonesian-1.5G-sentiment-analysis-smsa"
            )
            
            self.is_initialized = True
            logger.info("Indonesian NLP models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP models: {str(e)}")
            self.is_initialized = False
    
    async def analyze_message(self, message: str) -> Dict[str, Any]:
        """Analyze user message for intent, entities, and context"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            message_lower = message.lower()
            
            # Detect intent
            intent = self._detect_intent(message_lower)
            
            # Extract entities
            entities = self._extract_entities(message_lower)
            
            # Get sentiment
            sentiment = await self._get_sentiment(message)
            
            # Calculate confidence
            confidence = self._calculate_confidence(intent, entities, message_lower)
            
            return {
                "intent": intent,
                "entities": entities,
                "sentiment": sentiment,
                "confidence": confidence,
                "keywords": self._extract_keywords(message_lower)
            }
            
        except Exception as e:
            logger.error(f"Message analysis failed: {str(e)}")
            return {
                "intent": "unknown",
                "entities": {},
                "sentiment": "neutral",
                "confidence": 0.0,
                "keywords": []
            }
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message):
                    return intent
        
        # Fallback: check for keyword-based intent
        if any(keyword in message for keyword in self.finance_keywords["help"]):
            return "general_help"
        elif any(keyword in message for keyword in self.finance_keywords["expense"]):
            return "expense_query"
        elif any(keyword in message for keyword in self.finance_keywords["income"]):
            return "income_query"
        elif any(keyword in message for keyword in self.finance_keywords["budget"]):
            return "budget_help"
        elif any(keyword in message for keyword in self.finance_keywords["savings"]):
            return "savings_advice"
        
        return "unknown"
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities like amounts, categories, dates from message"""
        entities = {}
        
        # Extract amount
        amount = self._extract_amount(message)
        if amount:
            entities["amount"] = amount
        
        # Extract category
        category = self._extract_category(message)
        if category:
            entities["category"] = category
        
        # Extract time period
        time_period = self._extract_time_period(message)
        if time_period:
            entities["time_period"] = time_period
        
        return entities
    
    def _extract_amount(self, message: str) -> Optional[float]:
        """Extract monetary amount from message"""
        for pattern in self.amount_patterns:
            match = re.search(pattern, message)
            if match:
                try:
                    if "ribu" in message or "rb" in message or "k" in message:
                        return float(match.group(1)) * 1000
                    elif "juta" in message or "jt" in message or "m" in message:
                        return float(match.group(1)) * 1000000
                    else:
                        # Remove dots as thousand separators
                        amount_str = match.group(1).replace(".", "")
                        return float(amount_str)
                except (ValueError, IndexError):
                    continue
        return None
    
    def _extract_category(self, message: str) -> Optional[str]:
        """Extract expense/income category from message"""
        for category, keywords in self.category_keywords.items():
            if any(keyword in message for keyword in keywords):
                return category
        return None
    
    def _extract_time_period(self, message: str) -> Optional[str]:
        """Extract time period from message"""
        time_patterns = {
            "today": ["hari ini", "today"],
            "yesterday": ["kemarin", "yesterday"],
            "this_week": ["minggu ini", "seminggu", "this week"],
            "this_month": ["bulan ini", "sebulan", "this month"],
            "last_week": ["minggu lalu", "last week"],
            "last_month": ["bulan lalu", "last month"]
        }
        
        for period, keywords in time_patterns.items():
            if any(keyword in message for keyword in keywords):
                return period
        
        return None
    
    async def _get_sentiment(self, message: str) -> str:
        """Get sentiment of the message"""
        try:
            if self.sentiment_analyzer:
                result = self.sentiment_analyzer(message)
                if result and len(result) > 0:
                    sentiment = result[0]["label"].lower()
                    return sentiment if sentiment in ["positive", "negative", "neutral"] else "neutral"
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {str(e)}")
        
        return "neutral"
    
    def _extract_keywords(self, message: str) -> List[str]:
        """Extract relevant keywords from message"""
        keywords = []
        words = message.split()
        
        for word in words:
            # Skip common words
            if len(word) > 2 and word not in ["dan", "atau", "yang", "untuk", "dari", "dengan", "pada", "dalam"]:
                # Check if word is a financial keyword
                for category, category_keywords in self.finance_keywords.items():
                    if word in category_keywords:
                        keywords.append(word)
                        break
                
                # Check category keywords
                for category, category_keywords in self.category_keywords.items():
                    if word in category_keywords:
                        keywords.append(word)
                        break
        
        return list(set(keywords))  # Remove duplicates
    
    def _calculate_confidence(self, intent: str, entities: Dict, message: str) -> float:
        """Calculate confidence score for the analysis"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if intent is detected with patterns
        if intent != "unknown":
            confidence += 0.3
        
        # Increase confidence if entities are found
        if entities:
            confidence += 0.2 * len(entities)
        
        # Increase confidence if message contains clear financial keywords
        finance_word_count = sum(
            1 for word in message.split()
            if any(word in keywords for keywords in self.finance_keywords.values())
        )
        confidence += min(0.1 * finance_word_count, 0.2)
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    async def generate_response_suggestions(self, intent: str, entities: Dict[str, Any]) -> List[str]:
        """Generate contextual response suggestions"""
        suggestions = []
        
        if intent == "ask_balance":
            suggestions = [
                "Tampilkan pengeluaran bulan ini",
                "Lihat budget saya",
                "Tips menghemat uang"
            ]
        elif intent == "expense_query":
            suggestions = [
                "Tambah pengeluaran baru",
                "Lihat pengeluaran per kategori",
                "Bandingkan dengan bulan lalu"
            ]
        elif intent == "budget_help":
            suggestions = [
                "Buat budget baru",
                "Lihat progress budget",
                "Tips mengatur budget mahasiswa"
            ]
        elif intent == "savings_advice":
            suggestions = [
                "Buat target tabungan",
                "Tips hemat untuk mahasiswa",
                "Lihat progress menabung"
            ]
        else:
            suggestions = [
                "Cek saldo saya",
                "Tambah transaksi baru",
                "Lihat statistik keuangan",
                "Tips mengatur keuangan"
            ]
        
        return suggestions[:3]  # Return max 3 suggestions


# Singleton instance
nlp_service = IndonesianNLPService()