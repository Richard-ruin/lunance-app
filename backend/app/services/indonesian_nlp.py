# app/services/indonesian_nlp.py
import torch
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    pipeline
)
import re
import asyncio
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class IndonesianNLPService:
    def __init__(self):
        self.intent_model = None
        self.sentiment_model = None
        self.tokenizer = None
        self.embeddings_model = None
        
        # Indonesian currency patterns
        self.currency_patterns = [
            r'(\d+(?:\.\d{3})*)\s*(?:ribu|rb|k)',
            r'(\d+(?:\.\d{3})*)\s*(?:juta|jt)',
            r'(\d+(?:\.\d{3})*)\s*(?:rp|rupiah)',
            r'(\d+(?:\.\d{3})*)',
        ]
        
        # Date patterns in Indonesian
        self.date_patterns = {
            'hari ini': 0,
            'kemarin': -1,
            'lusa': -2,
            'minggu lalu': -7,
            'bulan lalu': -30,
            'tahun lalu': -365,
        }
        
        # Category mapping
        self.category_mapping = {
            'makan': 'food',
            'makanan': 'food',
            'jajan': 'food',
            'resto': 'food',
            'restoran': 'food',
            'transport': 'transportation',
            'ojek': 'transportation',
            'gojek': 'transportation',
            'grab': 'transportation',
            'bus': 'transportation',
            'kereta': 'transportation',
            'belanja': 'shopping',
            'shopping': 'shopping',
            'baju': 'shopping',
            'sepatu': 'shopping',
            'hiburan': 'entertainment',
            'nonton': 'entertainment',
            'cinema': 'entertainment',
            'game': 'entertainment',
            'kos': 'housing',
            'kontrakan': 'housing',
            'listrik': 'utilities',
            'air': 'utilities',
            'wifi': 'utilities',
            'pulsa': 'utilities',
            'sekolah': 'education',
            'kuliah': 'education',
            'buku': 'education',
            'kesehatan': 'health',
            'dokter': 'health',
            'obat': 'health',
        }
    
    async def initialize_models(self):
        """Initialize all Indonesian NLP models"""
        try:
            logger.info("Loading Indonesian NLP models...")
            
            # Load IndoBERT for embeddings and intent classification
            self.tokenizer = AutoTokenizer.from_pretrained("indolem/indobert-base-uncased")
            self.embeddings_model = AutoModel.from_pretrained("indolem/indobert-base-uncased")
            
            # Load sentiment analysis model
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="w11wo/indonesian-roberta-base-sentiment-classifier",
                tokenizer="w11wo/indonesian-roberta-base-sentiment-classifier"
            )
            
            logger.info("✅ Indonesian NLP models loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Indonesian NLP models: {e}")
            # Fallback: use simple pattern matching
            self.sentiment_model = None
    
    def extract_amount(self, text: str) -> Optional[float]:
        """Extract monetary amount from Indonesian text"""
        text = text.lower()
        
        for pattern in self.currency_patterns:
            matches = re.findall(pattern, text)
            if matches:
                amount_str = matches[0].replace('.', '')
                try:
                    amount = float(amount_str)
                    
                    # Convert based on suffix
                    if 'ribu' in text or 'rb' in text or 'k' in text:
                        amount *= 1000
                    elif 'juta' in text or 'jt' in text:
                        amount *= 1000000
                    
                    return amount
                except ValueError:
                    continue
        
        return None
    
    def extract_category(self, text: str) -> Optional[str]:
        """Extract transaction category from Indonesian text"""
        text = text.lower()
        
        for indo_category, eng_category in self.category_mapping.items():
            if indo_category in text:
                return eng_category
        
        return None
    
    def extract_date(self, text: str) -> Optional[datetime]:
        """Extract date from Indonesian text"""
        text = text.lower()
        today = datetime.now()
        
        for pattern, days_offset in self.date_patterns.items():
            if pattern in text:
                return today + timedelta(days=days_offset)
        
        # Check for specific date patterns
        date_match = re.search(r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?', text)
        if date_match:
            day, month, year = date_match.groups()
            year = int(year) if year else today.year
            if year < 100:  # Handle 2-digit years
                year += 2000
            try:
                return datetime(year, int(month), int(day))
            except ValueError:
                pass
        
        return None
    
    def extract_transaction_type(self, text: str) -> str:
        """Determine if it's income or expense"""
        text = text.lower()
        
        income_keywords = [
            'dapat', 'terima', 'gaji', 'pendapatan', 'masuk', 'uang jajan',
            'transfer masuk', 'bonus', 'hadiah', 'cashback'
        ]
        
        expense_keywords = [
            'beli', 'bayar', 'buat', 'untuk', 'pengeluaran', 'keluar',
            'belanja', 'transfer', 'kirim', 'top up'
        ]
        
        for keyword in income_keywords:
            if keyword in text:
                return 'income'
        
        for keyword in expense_keywords:
            if keyword in text:
                return 'expense'
        
        # Default to expense if amount is found
        return 'expense'
    
    async def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze sentiment of Indonesian text"""
        try:
            if self.sentiment_model:
                result = self.sentiment_model(text)[0]
                label = result['label'].lower()
                score = result['score']
                
                # Map to standard labels
                if 'pos' in label:
                    return 'positive', score
                elif 'neg' in label:
                    return 'negative', score
                else:
                    return 'neutral', score
            else:
                # Fallback sentiment analysis
                return self._simple_sentiment_analysis(text)
                
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return self._simple_sentiment_analysis(text)
    
    def _simple_sentiment_analysis(self, text: str) -> Tuple[str, float]:
        """Simple sentiment analysis fallback"""
        text = text.lower()
        
        positive_words = [
            'senang', 'bahagia', 'bagus', 'baik', 'keren', 'oke', 'mantap',
            'suka', 'cinta', 'amazing', 'perfect', 'excellent'
        ]
        
        negative_words = [
            'kesal', 'marah', 'sedih', 'jelek', 'buruk', 'benci', 'kecewa',
            'stress', 'cape', 'lelah', 'bosan', 'terrible', 'bad'
        ]
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        if pos_count > neg_count:
            return 'positive', 0.6 + (pos_count * 0.1)
        elif neg_count > pos_count:
            return 'negative', 0.6 + (neg_count * 0.1)
        else:
            return 'neutral', 0.5
    
    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract all financial entities from text"""
        entities = []
        
        # Extract amount
        amount = self.extract_amount(text)
        if amount:
            entities.append({
                'entity_type': 'amount',
                'value': amount,
                'confidence': 0.9,
                'start_pos': 0,
                'end_pos': len(text)
            })
        
        # Extract category
        category = self.extract_category(text)
        if category:
            entities.append({
                'entity_type': 'category',
                'value': category,
                'confidence': 0.8,
                'start_pos': 0,
                'end_pos': len(text)
            })
        
        # Extract date
        date = self.extract_date(text)
        if date:
            entities.append({
                'entity_type': 'date',
                'value': date.isoformat(),
                'confidence': 0.7,
                'start_pos': 0,
                'end_pos': len(text)
            })
        
        # Extract transaction type
        trans_type = self.extract_transaction_type(text)
        entities.append({
            'entity_type': 'transaction_type',
            'value': trans_type,
            'confidence': 0.7,
            'start_pos': 0,
            'end_pos': len(text)
        })
        
        return entities

# Global instance
nlp_service = IndonesianNLPService()