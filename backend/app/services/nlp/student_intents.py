# app/services/nlp/student_intents.py
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from app.services.nlp.simple_nlp import SimpleNLPService

logger = logging.getLogger(__name__)

class StudentIntentClassifier:
    """Intent classifier specifically designed for Indonesian student finance queries"""
    
    def __init__(self):
        self.nlp_service = SimpleNLPService()
        
        # Define intents with Indonesian patterns
        self.intent_patterns = {
            'check_balance': {
                'patterns': [
                    r'(?:berapa|cek|lihat)\s*(?:saldo|balance|uang)',
                    r'saldo\s*(?:saya|aku|ku)',
                    r'(?:uang|duit)\s*(?:saya|aku|ku)\s*(?:berapa|tinggal)',
                    r'check\s*balance',
                    r'(?:punya|ada)\s*(?:berapa|uang)'
                ],
                'keywords': ['saldo', 'balance', 'uang', 'cek', 'berapa', 'lihat', 'check'],
                'confidence_boost': 0.8
            },
            
            'view_expenses': {
                'patterns': [
                    r'(?:lihat|cek|tampilkan)\s*(?:pengeluaran|expense)',
                    r'pengeluaran\s*(?:saya|aku|ku)',
                    r'(?:habis|keluar)\s*(?:berapa|uang)',
                    r'(?:spending|spent)\s*(?:today|hari ini|kemarin)',
                    r'(?:beli|belanja|bayar)\s*(?:apa|berapa)'
                ],
                'keywords': ['pengeluaran', 'expense', 'spending', 'keluar', 'habis', 'beli', 'belanja', 'bayar'],
                'confidence_boost': 0.7
            },
            
            'budget_help': {
                'patterns': [
                    r'(?:bantuan|help|tolong)\s*(?:budget|anggaran)',
                    r'(?:gimana|bagaimana)\s*(?:ngatur|atur|manage)\s*(?:uang|keuangan)',
                    r'(?:tips|saran|advice)\s*(?:keuangan|financial)',
                    r'(?:hemat|saving|menabung)',
                    r'budget\s*(?:planning|advice)'
                ],
                'keywords': ['budget', 'anggaran', 'tips', 'saran', 'hemat', 'atur', 'manage', 'planning'],
                'confidence_boost': 0.9
            },
            
            'add_transaction': {
                'patterns': [
                    r'(?:catat|tambah|add|input)\s*(?:transaksi|transaction|pengeluaran)',
                    r'(?:beli|bayar|belanja)\s*.+\s*(?:\d+|ribu|juta)',
                    r'(?:habis|keluar|spent)\s*.+\s*(?:\d+|ribu|juta)',
                    r'tadi\s*(?:beli|bayar|belanja)',
                    r'(?:makan|transport|kuliah)\s*.+\s*(?:\d+|ribu|juta)'
                ],
                'keywords': ['catat', 'tambah', 'add', 'beli', 'bayar', 'belanja', 'habis', 'spent'],
                'confidence_boost': 0.8
            },
            
            'savings_goal': {
                'patterns': [
                    r'(?:target|goal|tujuan)\s*(?:tabungan|saving)',
                    r'(?:mau|ingin|pengen)\s*(?:nabung|menabung|save)',
                    r'(?:rencana|planning)\s*(?:keuangan|financial)',
                    r'savings\s*(?:goal|target|plan)',
                    r'(?:dana|uang)\s*(?:darurat|emergency)'
                ],
                'keywords': ['target', 'goal', 'tabungan', 'saving', 'nabung', 'rencana', 'planning', 'dana'],
                'confidence_boost': 0.8
            },
            
            'expense_analysis': {
                'patterns': [
                    r'(?:analisa|analisis|analysis)\s*(?:pengeluaran|spending)',
                    r'(?:dimana|where)\s*(?:uang|duit)\s*(?:habis|keluar)',
                    r'(?:kategori|category)\s*(?:terbanyak|highest|most)',
                    r'(?:spending|pengeluaran)\s*(?:pattern|pola)',
                    r'(?:breakdown|rincian)\s*(?:pengeluaran|expense)'
                ],
                'keywords': ['analisa', 'analisis', 'analysis', 'kategori', 'breakdown', 'rincian', 'pattern'],
                'confidence_boost': 0.7
            },
            
            'debt_inquiry': {
                'patterns': [
                    r'(?:hutang|debt|loan|pinjam)',
                    r'(?:bayar|cicil|payment)\s*(?:hutang|debt)',
                    r'(?:owe|owes|utang)\s*(?:berapa|how much)',
                    r'(?:kredit|credit|pinjaman)',
                    r'(?:teman|friend)\s*(?:pinjam|lend|borrow)'
                ],
                'keywords': ['hutang', 'debt', 'loan', 'pinjam', 'bayar', 'cicil', 'kredit', 'utang'],
                'confidence_boost': 0.9
            },
            
            'income_tracking': {
                'patterns': [
                    r'(?:pemasukan|income|gaji|salary)',
                    r'(?:terima|dapat|received)\s*(?:uang|money)',
                    r'(?:allowance|uang saku|jajan)',
                    r'(?:part time|freelance|kerja)',
                    r'(?:beasiswa|scholarship)'
                ],
                'keywords': ['pemasukan', 'income', 'gaji', 'salary', 'terima', 'dapat', 'allowance', 'beasiswa'],
                'confidence_boost': 0.8
            },
            
            'academic_expenses': {
                'patterns': [
                    r'(?:kuliah|kampus|university|college)',
                    r'(?:buku|book|textbook)\s*(?:\d+|ribu|juta)',
                    r'(?:uang kuliah|tuition|spp)',
                    r'(?:lab|praktikum|practicum)',
                    r'(?:semester|ujian|exam)\s*(?:fee|biaya)'
                ],
                'keywords': ['kuliah', 'kampus', 'university', 'buku', 'tuition', 'spp', 'lab', 'semester'],
                'confidence_boost': 0.9
            },
            
            'greeting': {
                'patterns': [
                    r'^(?:hai|halo|hello|hi)(?:\s|$)',
                    r'^(?:selamat|good)\s*(?:pagi|siang|sore|malam|morning|afternoon|evening)',
                    r'(?:apa kabar|how are you)',
                    r'^(?:assalamualaikum|peace)'
                ],
                'keywords': ['hai', 'halo', 'hello', 'hi', 'selamat', 'good', 'morning', 'kabar'],
                'confidence_boost': 1.0
            },
            
            'help_general': {
                'patterns': [
                    r'(?:help|bantuan|tolong)',
                    r'(?:gimana|bagaimana|how)\s*(?:cara|way|to)',
                    r'(?:bisa|can)\s*(?:bantu|help)',
                    r'(?:fitur|feature|fungsi)',
                    r'(?:tutorial|guide|panduan)'
                ],
                'keywords': ['help', 'bantuan', 'tolong', 'gimana', 'bagaimana', 'cara', 'bisa', 'bantu'],
                'confidence_boost': 0.6
            }
        }
        
        # Category keywords for entity extraction
        self.category_keywords = {
            'food': ['makan', 'makanan', 'jajan', 'snack', 'food', 'meal', 'breakfast', 'lunch', 'dinner'],
            'transport': ['transport', 'transportasi', 'ojol', 'grab', 'gojek', 'bus', 'kereta', 'bensin'],
            'academic': ['kuliah', 'kampus', 'buku', 'book', 'tugas', 'assignment', 'ujian', 'exam'],
            'entertainment': ['hiburan', 'entertainment', 'nonton', 'movie', 'game', 'musik', 'music'],
            'health': ['kesehatan', 'health', 'obat', 'medicine', 'dokter', 'doctor', 'hospital'],
            'shopping': ['belanja', 'shopping', 'beli', 'buy', 'baju', 'clothes', 'sepatu', 'shoes']
        }
    
    def extract_entities_from_text(self, text: str) -> Dict[str, Any]:
        """Extract entities specific to student finance context"""
        entities = self.nlp_service.extract_entities(text)
        
        # Enhanced category detection for students
        text_lower = text.lower()
        
        # Check for specific student categories
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entities['category'] = category
                    break
            if 'category' in entities:
                break
        
        # Extract academic context
        academic_terms = ['semester', 'kuliah', 'kampus', 'ujian', 'uts', 'uas', 'skripsi', 'thesis']
        if any(term in text_lower for term in academic_terms):
            entities['context'] = 'academic'
        
        # Extract urgency level
        urgent_terms = ['urgent', 'penting', 'segera', 'cepat', 'darurat', 'emergency']
        if any(term in text_lower for term in urgent_terms):
            entities['urgency'] = 'high'
        
        return entities
    
    def calculate_intent_confidence(self, text: str, intent: str) -> float:
        """Calculate confidence score for a specific intent"""
        if intent not in self.intent_patterns:
            return 0.0
        
        intent_data = self.intent_patterns[intent]
        text_lower = text.lower()
        
        confidence = 0.0
        
        # Check pattern matches
        pattern_matches = 0
        for pattern in intent_data['patterns']:
            if re.search(pattern, text_lower):
                pattern_matches += 1
        
        if pattern_matches > 0:
            confidence += intent_data['confidence_boost'] * (pattern_matches / len(intent_data['patterns']))
        
        # Check keyword matches
        keyword_matches = 0
        words = text_lower.split()
        for keyword in intent_data['keywords']:
            if keyword in text_lower:
                keyword_matches += 1
        
        if keyword_matches > 0:
            confidence += 0.3 * (keyword_matches / len(intent_data['keywords']))
        
        # Boost confidence for exact phrase matches
        for pattern in intent_data['patterns']:
            if re.search(pattern, text_lower):
                confidence += 0.2
                break
        
        return min(confidence, 1.0)
    
    async def classify_intent(self, text: str) -> Dict[str, Any]:
        """Classify intent with confidence scores"""
        try:
            # Preprocess text
            preprocessed = await self.nlp_service.preprocess_message(text)
            
            # Calculate confidence for each intent
            intent_scores = {}
            for intent in self.intent_patterns.keys():
                score = self.calculate_intent_confidence(text, intent)
                if score > 0:
                    intent_scores[intent] = score
            
            # Determine best intent
            if not intent_scores:
                best_intent = 'help_general'
                confidence = 0.3
            else:
                best_intent = max(intent_scores, key=intent_scores.get)
                confidence = intent_scores[best_intent]
            
            # Extract entities
            entities = self.extract_entities_from_text(text)
            
            # Special handling for transaction-like messages
            if 'amount' in entities and ('beli' in text.lower() or 'bayar' in text.lower() or 'habis' in text.lower()):
                if best_intent not in ['add_transaction']:
                    best_intent = 'add_transaction'
                    confidence = max(confidence, 0.8)
            
            return {
                'intent': best_intent,
                'confidence': confidence,
                'entities': entities,
                'all_scores': intent_scores,
                'preprocessed': preprocessed
            }
            
        except Exception as e:
            logger.error(f"Error in intent classification: {str(e)}")
            return {
                'intent': 'help_general',
                'confidence': 0.1,
                'entities': {},
                'all_scores': {},
                'preprocessed': {}
            }
    
    def get_suggested_followup_questions(self, intent: str, entities: Dict[str, Any]) -> List[str]:
        """Get suggested follow-up questions based on intent and entities"""
        suggestions = []
        
        if intent == 'check_balance':
            suggestions = [
                "Mau lihat pengeluaran hari ini?",
                "Butuh bantuan mengatur budget?",
                "Mau cek kategori pengeluaran terbanyak?"
            ]
        
        elif intent == 'add_transaction':
            if 'amount' not in entities:
                suggestions.append("Berapa jumlahnya?")
            if 'category' not in entities:
                suggestions.append("Untuk kategori apa nih?")
            suggestions.append("Mau tambah catatan?")
        
        elif intent == 'budget_help':
            suggestions = [
                "Mau buat budget berdasarkan pengeluaran bulan lalu?",
                "Perlu tips menghemat uang jajan?",
                "Mau setting target tabungan?"
            ]
        
        elif intent == 'view_expenses':
            suggestions = [
                "Mau lihat breakdown per kategori?",
                "Perbandingan dengan bulan lalu?",
                "Cek pengeluaran terbesar minggu ini?"
            ]
        
        elif intent == 'savings_goal':
            suggestions = [
                "Mau buat target tabungan baru?",
                "Lihat progress tabungan yang ada?",
                "Butuh tips cara menabung konsisten?"
            ]
        
        elif intent == 'academic_expenses':
            suggestions = [
                "Mau track pengeluaran kuliah terpisah?",
                "Perlu budget khusus untuk semester ini?",
                "Cek total pengeluaran akademik bulan ini?"
            ]
        
        else:
            suggestions = [
                "Ada yang bisa saya bantu lagi?",
                "Mau cek saldo atau pengeluaran?",
                "Butuh tips keuangan lainnya?"
            ]
        
        return suggestions[:3]  # Return max 3 suggestions
    
    def detect_transaction_details(self, text: str) -> Optional[Dict[str, Any]]:
        """Detect if message contains transaction details"""
        transaction_info = self.nlp_service.extract_transaction_info(text)
        
        if not transaction_info:
            return None
        
        # Enhance with student-specific context
        text_lower = text.lower()
        
        # Detect payment method
        payment_methods = {
            'cash': ['cash', 'tunai', 'uang cash'],
            'e_wallet': ['gopay', 'ovo', 'dana', 'linkaja', 'shopeepay'],
            'bank_transfer': ['transfer', 'atm', 'debit'],
            'credit': ['credit', 'kredit', 'cicil']
        }
        
        for method, keywords in payment_methods.items():
            if any(keyword in text_lower for keyword in keywords):
                transaction_info['payment_method'] = method
                break
        
        # Detect location context
        location_indicators = {
            'campus': ['kampus', 'kantin', 'cafeteria', 'lab', 'kelas'],
            'mall': ['mall', 'shopping center', 'plaza'],
            'restaurant': ['resto', 'restaurant', 'warung', 'cafe'],
            'online': ['online', 'shopee', 'tokopedia', 'grab food', 'gofood']
        }
        
        for location, keywords in location_indicators.items():
            if any(keyword in text_lower for keyword in keywords):
                transaction_info['location_type'] = location
                break
        
        return transaction_info if transaction_info else None