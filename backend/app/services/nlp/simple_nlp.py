# app/services/nlp/simple_nlp.py
import re
import string
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

logger = logging.getLogger(__name__)

class SimpleNLPService:
    """Simple NLP service for Indonesian text processing"""
    
    def __init__(self):
        # Initialize Sastrawi for Indonesian language processing
        try:
            self.stemmer_factory = StemmerFactory()
            self.stemmer = self.stemmer_factory.create_stemmer()
            
            self.stopword_factory = StopWordRemoverFactory()
            self.stopword_remover = self.stopword_factory.create_stop_word_remover()
        except Exception as e:
            logger.warning(f"Failed to initialize Sastrawi: {e}")
            self.stemmer = None
            self.stopword_remover = None
        
        # Indonesian financial keywords
        self.financial_keywords = {
            'balance': ['saldo', 'balance', 'uang', 'duit', 'dana', 'money'],
            'expense': ['pengeluaran', 'expense', 'belanja', 'beli', 'bayar', 'spend', 'cost', 'biaya'],
            'income': ['pemasukan', 'income', 'gaji', 'salary', 'pendapatan', 'terima', 'dapat'],
            'budget': ['budget', 'anggaran', 'rencana', 'target', 'limit'],
            'savings': ['tabungan', 'savings', 'nabung', 'simpan', 'save'],
            'debt': ['hutang', 'debt', 'pinjam', 'loan', 'cicil'],
            'food': ['makan', 'food', 'makanan', 'jajan', 'snack', 'meal'],
            'transport': ['transport', 'transportasi', 'ojol', 'grab', 'gojek', 'bus', 'kereta'],
            'entertainment': ['hiburan', 'entertainment', 'nonton', 'game', 'musik'],
            'academic': ['kuliah', 'kampus', 'buku', 'tugas', 'ujian', 'semester'],
            'help': ['help', 'bantuan', 'tolong', 'gimana', 'bagaimana', 'cara']
        }
        
        # Time expressions in Indonesian
        self.time_patterns = {
            'today': ['hari ini', 'today'],
            'yesterday': ['kemarin', 'yesterday'],
            'week': ['minggu ini', 'this week', 'seminggu'],
            'month': ['bulan ini', 'this month', 'sebulan'],
            'year': ['tahun ini', 'this year', 'setahun']
        }
        
        # Amount patterns (Indonesian rupiah)
        self.amount_patterns = [
            r'(\d+(?:\.\d{3})*)\s*(?:ribu|rb|k)',  # 50 ribu, 50rb, 50k
            r'(\d+(?:\.\d{3})*)\s*(?:juta|jt|m)',  # 2 juta, 2jt, 2m
            r'(?:rp|rupiah)?\s*(\d+(?:\.\d{3})*)',  # Rp 50.000, 50.000
            r'(\d+)\s*(?:rb|ribu)',  # 50rb, 50 ribu
            r'(\d+(?:\.\d+)?)\s*(?:jt|juta)',  # 1.5jt, 1.5 juta
        ]
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation except for numbers
        text = re.sub(r'[^\w\s\d.,]', ' ', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        cleaned_text = self.clean_text(text)
        
        # Remove stopwords if Sastrawi is available
        if self.stopword_remover:
            try:
                cleaned_text = self.stopword_remover.remove(cleaned_text)
            except Exception:
                pass
        
        # Extract words
        words = cleaned_text.split()
        
        # Stem words if stemmer is available
        if self.stemmer:
            try:
                words = [self.stemmer.stem(word) for word in words]
            except Exception:
                pass
        
        return words
    
    def extract_amount(self, text: str) -> Optional[float]:
        """Extract monetary amount from text"""
        text = self.clean_text(text)
        
        for pattern in self.amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                amount_str = matches[0]
                
                # Handle different formats
                try:
                    # Remove dots used as thousand separators
                    amount_str = amount_str.replace('.', '')
                    amount = float(amount_str)
                    
                    # Apply multipliers based on pattern
                    if 'ribu' in pattern or 'rb' in pattern or 'k' in pattern:
                        amount *= 1000
                    elif 'juta' in pattern or 'jt' in pattern or 'm' in pattern:
                        amount *= 1000000
                    
                    return amount
                except ValueError:
                    continue
        
        return None
    
    def extract_time_period(self, text: str) -> Optional[str]:
        """Extract time period from text"""
        text = self.clean_text(text)
        
        for period, patterns in self.time_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return period
        
        return None
    
    def extract_category(self, text: str) -> Optional[str]:
        """Extract expense/income category from text"""
        text = self.clean_text(text)
        keywords = self.extract_keywords(text)
        
        # Score each category
        category_scores = {}
        for category, category_keywords in self.financial_keywords.items():
            score = 0
            for keyword in category_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in text:
                    score += 2  # Exact match
                for extracted_keyword in keywords:
                    if keyword_lower in extracted_keyword or extracted_keyword in keyword_lower:
                        score += 1  # Partial match
            
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return None
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        entities = {}
        
        # Extract amount
        amount = self.extract_amount(text)
        if amount:
            entities['amount'] = amount
        
        # Extract time period
        time_period = self.extract_time_period(text)
        if time_period:
            entities['time_period'] = time_period
        
        # Extract category
        category = self.extract_category(text)
        if category:
            entities['category'] = category
        
        # Extract keywords
        keywords = self.extract_keywords(text)
        entities['keywords'] = keywords
        
        return entities
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple similarity between two texts"""
        keywords1 = set(self.extract_keywords(text1))
        keywords2 = set(self.extract_keywords(text2))
        
        if not keywords1 and not keywords2:
            return 0.0
        
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def detect_language(self, text: str) -> str:
        """Simple language detection (Indonesian vs English)"""
        # Indonesian common words
        indonesian_words = [
            'saya', 'aku', 'kamu', 'anda', 'ini', 'itu', 'dan', 'atau', 'yang', 'di', 'ke',
            'dari', 'untuk', 'dengan', 'pada', 'dalam', 'adalah', 'akan', 'sudah', 'belum',
            'mau', 'ingin', 'bisa', 'tidak', 'ya', 'oke', 'gimana', 'bagaimana'
        ]
        
        # English common words
        english_words = [
            'i', 'you', 'me', 'my', 'your', 'this', 'that', 'and', 'or', 'the', 'to',
            'from', 'for', 'with', 'in', 'on', 'at', 'is', 'are', 'was', 'were',
            'will', 'would', 'can', 'could', 'not', 'yes', 'ok', 'how', 'what'
        ]
        
        text_lower = text.lower()
        words = text_lower.split()
        
        indonesian_count = sum(1 for word in words if word in indonesian_words)
        english_count = sum(1 for word in words if word in english_words)
        
        return 'id' if indonesian_count >= english_count else 'en'
    
    def extract_date_mentions(self, text: str) -> List[datetime]:
        """Extract date mentions from text"""
        dates = []
        text = self.clean_text(text)
        
        # Simple date patterns
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{1,2})\s+(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)\s+(\d{4})',
            r'(kemarin|yesterday)',
            r'(hari ini|today)',
            r'(besok|tomorrow)'
        ]
        
        today = datetime.now()
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if isinstance(match, tuple) and len(match) == 3:
                        if match[1].isdigit():  # DD/MM/YYYY format
                            day, month, year = int(match[0]), int(match[1]), int(match[2])
                            dates.append(datetime(year, month, day))
                        else:  # Month name format
                            month_names = {
                                'januari': 1, 'februari': 2, 'maret': 3, 'april': 4,
                                'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
                                'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
                            }
                            day, month_name, year = int(match[0]), match[1].lower(), int(match[2])
                            month = month_names.get(month_name)
                            if month:
                                dates.append(datetime(year, month, day))
                    elif isinstance(match, str):
                        if match in ['kemarin', 'yesterday']:
                            dates.append(today - timedelta(days=1))
                        elif match in ['hari ini', 'today']:
                            dates.append(today)
                        elif match in ['besok', 'tomorrow']:
                            dates.append(today + timedelta(days=1))
                except ValueError:
                    continue
        
        return dates
    
    def is_question(self, text: str) -> bool:
        """Check if text is a question"""
        question_words = [
            'apa', 'siapa', 'kapan', 'dimana', 'mengapa', 'bagaimana', 'berapa',
            'what', 'who', 'when', 'where', 'why', 'how', 'how much'
        ]
        
        text_lower = text.lower()
        
        # Check for question words
        for word in question_words:
            if word in text_lower:
                return True
        
        # Check for question mark
        if '?' in text:
            return True
        
        return False
    
    def extract_transaction_info(self, text: str) -> Dict[str, Any]:
        """Extract transaction information from text"""
        info = {}
        
        # Extract amount
        amount = self.extract_amount(text)
        if amount:
            info['amount'] = amount
        
        # Extract category
        category = self.extract_category(text)
        if category:
            info['category'] = category
        
        # Extract dates
        dates = self.extract_date_mentions(text)
        if dates:
            info['date'] = dates[0]  # Use first date found
        
        # Determine transaction type
        expense_indicators = ['beli', 'bayar', 'belanja', 'spent', 'keluar', 'habis']
        income_indicators = ['terima', 'dapat', 'gaji', 'income', 'masuk']
        
        text_lower = text.lower()
        
        expense_score = sum(1 for indicator in expense_indicators if indicator in text_lower)
        income_score = sum(1 for indicator in income_indicators if indicator in text_lower)
        
        if expense_score > income_score:
            info['type'] = 'expense'
        elif income_score > expense_score:
            info['type'] = 'income'
        
        return info
    
    async def preprocess_message(self, message: str) -> Dict[str, Any]:
        """Preprocess message for intent classification"""
        return {
            'original_text': message,
            'cleaned_text': self.clean_text(message),
            'keywords': self.extract_keywords(message),
            'entities': self.extract_entities(message),
            'language': self.detect_language(message),
            'is_question': self.is_question(message),
            'transaction_info': self.extract_transaction_info(message)
        }