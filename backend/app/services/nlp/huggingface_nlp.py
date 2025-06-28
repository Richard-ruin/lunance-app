# app/services/nlp/huggingface_nlp.py
import logging
from typing import Dict, List, Any, Optional, Tuple
import asyncio
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    pipeline, Pipeline
)
import torch
import numpy as np
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class HuggingFaceNLPService:
    """
    Advanced NLP service using Hugging Face Transformers
    Specifically configured for Indonesian language financial queries
    """
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Model configurations
        self.models = {
            'indonesian_bert': 'indobenchmark/indobert-base-p1',
            'indonesian_roberta': 'flax-community/indonesian-roberta-base',
            'multilingual_bert': 'bert-base-multilingual-cased'
        }
        
        # Initialize components
        self.tokenizer = None
        self.model = None
        self.classifier = None
        self.embedding_model = None
        
        # Intent classification labels (Indonesian financial contexts)
        self.intent_labels = [
            'check_balance',      # Cek saldo
            'view_expenses',      # Lihat pengeluaran
            'budget_help',        # Bantuan budget
            'add_transaction',    # Tambah transaksi
            'savings_goal',       # Target tabungan
            'expense_analysis',   # Analisa pengeluaran
            'debt_inquiry',       # Tanya hutang
            'income_tracking',    # Track pemasukan
            'academic_expenses',  # Pengeluaran kuliah
            'greeting',           # Salam
            'help_general'        # Bantuan umum
        ]
        
        # Cache for embeddings
        self.embedding_cache = {}
        
        # Training data for intent classification
        self.training_examples = {
            'check_balance': [
                "berapa saldo saya sekarang",
                "cek balance terkini",
                "uang saya tinggal berapa",
                "saldo terakhir berapa",
                "check my balance",
                "lihat saldo hari ini"
            ],
            'view_expenses': [
                "pengeluaran hari ini berapa",
                "habis berapa kemarin",
                "spending minggu ini",
                "keluar uang berapa",
                "lihat pengeluaran bulan ini",
                "cek expense terakhir"
            ],
            'budget_help': [
                "bantuan mengatur budget",
                "gimana cara menabung",
                "tips keuangan mahasiswa",
                "help me budget",
                "saran hemat uang",
                "planning keuangan"
            ],
            'add_transaction': [
                "catat makan 25 ribu",
                "beli buku 50000",
                "bayar transport 15rb",
                "add transaction food",
                "habis uang untuk belanja",
                "tadi keluar uang buat"
            ],
            'savings_goal': [
                "target tabungan laptop",
                "mau nabung berapa",
                "goal menabung",
                "planning dana darurat",
                "save money for",
                "rencana tabungan semester"
            ],
            'expense_analysis': [
                "analisa pengeluaran bulan ini",
                "kategori mana yang boros",
                "breakdown spending pattern",
                "dimana uang habis",
                "review keuangan",
                "spending analysis"
            ],
            'academic_expenses': [
                "biaya kuliah semester ini",
                "pengeluaran kampus",
                "budget akademik",
                "uang buku dan lab",
                "tuition and fees",
                "academic costs"
            ],
            'greeting': [
                "halo lunance",
                "selamat pagi",
                "hi there",
                "good morning",
                "hai bot",
                "hello assistant"
            ],
            'help_general': [
                "help me",
                "bantuan umum",
                "apa yang bisa kamu lakukan",
                "fitur apa saja",
                "how to use",
                "panduan aplikasi"
            ]
        }
        
        # Initialize models asynchronously
        asyncio.create_task(self.initialize_models())
    
    async def initialize_models(self):
        """Initialize Hugging Face models"""
        try:
            logger.info("Initializing Hugging Face models...")
            
            # Try Indonesian models first, fallback to multilingual
            model_name = self.models['indonesian_bert']
            
            try:
                # Load tokenizer and model
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModel.from_pretrained(model_name).to(self.device)
                
                logger.info(f"Successfully loaded Indonesian BERT: {model_name}")
                
            except Exception as e:
                logger.warning(f"Failed to load Indonesian model, falling back to multilingual: {e}")
                
                # Fallback to multilingual BERT
                model_name = self.models['multilingual_bert']
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModel.from_pretrained(model_name).to(self.device)
                
                logger.info(f"Loaded multilingual model: {model_name}")
            
            # Initialize text classifier pipeline
            try:
                self.classifier = pipeline(
                    "text-classification",
                    model=model_name,
                    tokenizer=model_name,
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("Text classification pipeline initialized")
                
            except Exception as e:
                logger.warning(f"Failed to initialize classifier pipeline: {e}")
                self.classifier = None
            
            # Set model to evaluation mode
            if self.model:
                self.model.eval()
            
            logger.info("Hugging Face models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            # Initialize fallback simple tokenization
            self.tokenizer = None
            self.model = None
            self.classifier = None
    
    def get_text_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get text embedding using Hugging Face model"""
        try:
            if not self.tokenizer or not self.model:
                return None
            
            # Check cache first
            if text in self.embedding_cache:
                return self.embedding_cache[text]
            
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            ).to(self.device)
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use CLS token embedding or mean pooling
                embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            
            # Cache the result
            self.embedding_cache[text] = embeddings[0]
            
            return embeddings[0]
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        try:
            emb1 = self.get_text_embedding(text1)
            emb2 = self.get_text_embedding(text2)
            
            if emb1 is None or emb2 is None:
                return 0.0
            
            # Cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    async def classify_intent_advanced(self, text: str) -> Dict[str, Any]:
        """Advanced intent classification using semantic similarity"""
        try:
            if not self.model:
                # Fallback to simple classification
                return {'intent': 'help_general', 'confidence': 0.3, 'method': 'fallback'}
            
            best_intent = 'help_general'
            best_score = 0.0
            all_scores = {}
            
            # Calculate similarity with training examples
            for intent, examples in self.training_examples.items():
                intent_scores = []
                
                for example in examples:
                    similarity = self.calculate_similarity(text.lower(), example.lower())
                    intent_scores.append(similarity)
                
                # Use average of top 3 similarities
                intent_scores.sort(reverse=True)
                avg_score = np.mean(intent_scores[:3]) if intent_scores else 0.0
                all_scores[intent] = avg_score
                
                if avg_score > best_score:
                    best_score = avg_score
                    best_intent = intent
            
            # Apply threshold
            confidence = best_score
            if confidence < 0.3:
                best_intent = 'help_general'
                confidence = 0.3
            
            return {
                'intent': best_intent,
                'confidence': confidence,
                'all_scores': all_scores,
                'method': 'semantic_similarity'
            }
            
        except Exception as e:
            logger.error(f"Error in advanced intent classification: {e}")
            return {
                'intent': 'help_general',
                'confidence': 0.1,
                'all_scores': {},
                'method': 'error_fallback'
            }
    
    async def extract_named_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using NER model"""
        try:
            if not self.classifier:
                return []
            
            # Use a simple approach for now
            entities = []
            
            # Amount patterns (Indonesian rupiah)
            import re
            amount_patterns = [
                r'(\d+(?:\.\d{3})*)\s*(?:ribu|rb|k)',
                r'(\d+(?:\.\d{3})*)\s*(?:juta|jt|m)',
                r'(?:rp|rupiah)?\s*(\d+(?:\.\d{3})*)',
            ]
            
            for pattern in amount_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'type': 'MONEY',
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.9
                    })
            
            # Date patterns
            date_patterns = [
                r'(hari ini|today)',
                r'(kemarin|yesterday)', 
                r'(minggu ini|this week)',
                r'(bulan ini|this month)',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
            ]
            
            for pattern in date_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'type': 'DATE',
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.8
                    })
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the text"""
        try:
            if self.classifier:
                # Try using pipeline for sentiment
                try:
                    sentiment_pipeline = pipeline(
                        "sentiment-analysis",
                        model="nlptown/bert-base-multilingual-uncased-sentiment"
                    )
                    result = sentiment_pipeline(text)[0]
                    
                    return {
                        'label': result['label'],
                        'score': result['score'],
                        'method': 'transformer'
                    }
                except:
                    pass
            
            # Fallback: Simple keyword-based sentiment
            positive_words = [
                'baik', 'bagus', 'senang', 'suka', 'terima kasih', 'thanks',
                'hebat', 'keren', 'mantap', 'oke', 'good', 'great', 'awesome'
            ]
            
            negative_words = [
                'buruk', 'jelek', 'sedih', 'benci', 'marah', 'bad', 'terrible',
                'susah', 'sulit', 'ribet', 'bingung', 'confused', 'difficult'
            ]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return {'label': 'POSITIVE', 'score': 0.7, 'method': 'keyword'}
            elif negative_count > positive_count:
                return {'label': 'NEGATIVE', 'score': 0.7, 'method': 'keyword'}
            else:
                return {'label': 'NEUTRAL', 'score': 0.5, 'method': 'keyword'}
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'label': 'NEUTRAL', 'score': 0.5, 'method': 'fallback'}
    
    async def process_text_advanced(self, text: str) -> Dict[str, Any]:
        """Advanced text processing combining multiple NLP tasks"""
        try:
            # Run all tasks concurrently
            tasks = [
                self.classify_intent_advanced(text),
                self.extract_named_entities(text),
                self.analyze_sentiment(text)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            intent_result = results[0] if not isinstance(results[0], Exception) else {'intent': 'help_general', 'confidence': 0.1}
            entities = results[1] if not isinstance(results[1], Exception) else []
            sentiment = results[2] if not isinstance(results[2], Exception) else {'label': 'NEUTRAL', 'score': 0.5}
            
            return {
                'intent': intent_result,
                'entities': entities,
                'sentiment': sentiment,
                'processed_at': datetime.utcnow().isoformat(),
                'model_info': {
                    'tokenizer_available': self.tokenizer is not None,
                    'model_available': self.model is not None,
                    'device': str(self.device)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in advanced text processing: {e}")
            return {
                'intent': {'intent': 'help_general', 'confidence': 0.1},
                'entities': [],
                'sentiment': {'label': 'NEUTRAL', 'score': 0.5},
                'error': str(e)
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            'models_available': self.models,
            'tokenizer_loaded': self.tokenizer is not None,
            'model_loaded': self.model is not None,
            'classifier_loaded': self.classifier is not None,
            'device': str(self.device),
            'cuda_available': torch.cuda.is_available(),
            'cache_size': len(self.embedding_cache),
            'supported_intents': self.intent_labels
        }
    
    def clear_cache(self):
        """Clear embedding cache to free memory"""
        self.embedding_cache.clear()
        logger.info("Embedding cache cleared")

# Global instance
huggingface_nlp = HuggingFaceNLPService()