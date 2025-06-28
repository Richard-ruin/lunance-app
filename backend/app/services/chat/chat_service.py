# app/services/chat/chat_service.py
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.chat import ChatResponse, DataUsed
from backend.app.models.user import Student
from app.services.nlp.indonesian_nlp import nlp_service
from app.utils.currency_formatter import format_idr

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.response_templates = {
            "greeting": [
                "Halo! Saya Luna, asisten keuangan Anda. Ada yang bisa saya bantu hari ini?",
                "Hi! Apa kabar? Mau tanya tentang keuangan atau butuh tips hemat?",
                "Selamat datang! Saya siap membantu mengatur keuangan Anda. Ada pertanyaan?"
            ],
            "balance": "Saldo Anda saat ini adalah {balance}. {additional_info}",
            "expense_summary": "Pengeluaran Anda {period} adalah {amount}. Kategori terbesar: {top_category} ({category_amount}).",
            "budget_status": "Budget {period} Anda: {used}/{total} ({percentage}%). {status_message}",
            "savings_advice": [
                "Tips hemat untuk mahasiswa: 1) Masak sendiri daripada jajan terus 2) Gunakan transportasi umum 3) Manfaatkan diskon mahasiswa",
                "Coba challenge '50 ribu sebulan': kurangi jajan dan masukkan selisihnya ke tabungan!",
                "Atur budget dengan rumus 50-30-20: 50% kebutuhan, 30% keinginan, 20% tabungan"
            ],
            "error": "Maaf, saya tidak bisa memproses permintaan Anda saat ini. Coba lagi atau tanyakan dengan cara lain.",
            "unknown": "Hmm, saya kurang paham. Coba tanyakan tentang saldo, pengeluaran, budget, atau minta tips hemat?"
        }
    
    async def process_message(self, message: str, student: Student, session_id: str) -> ChatResponse:
        """Process user message and generate response"""
        try:
            # Analyze message with NLP
            analysis = await nlp_service.analyze_message(message)
            
            # Generate response based on intent
            response = await self._generate_response(
                analysis["intent"],
                analysis["entities"],
                student,
                message
            )
            
            # Get suggestions
            suggestions = await nlp_service.generate_response_suggestions(
                analysis["intent"], 
                analysis["entities"]
            )
            
            return ChatResponse(
                message=response["message"],
                response_type=response["response_type"],
                data_used=response.get("data_used"),
                suggestions=suggestions,
                confidence=analysis["confidence"]
            )
            
        except Exception as e:
            logger.error(f"Message processing failed: {str(e)}")
            return ChatResponse(
                message=self.response_templates["error"],
                response_type="error",
                suggestions=["Cek saldo", "Lihat pengeluaran", "Tips hemat"],
                confidence=0.0
            )
    
    async def _generate_response(self, intent: str, entities: Dict, student: Student, original_message: str) -> Dict[str, Any]:
        """Generate response based on detected intent"""
        
        if intent == "ask_balance":
            return await self._handle_balance_query(student, entities)
        
        elif intent == "expense_query":
            return await self._handle_expense_query(student, entities)
        
        elif intent == "budget_help":
            return await self._handle_budget_query(student, entities)
        
        elif intent == "savings_advice":
            return await self._handle_savings_advice(student, entities)
        
        elif intent == "add_transaction":
            return await self._handle_add_transaction_help(student, entities)
        
        elif intent == "income_query":
            return await self._handle_income_query(student, entities)
        
        elif intent == "general_help":
            return await self._handle_general_help(student)
        
        elif self._is_greeting(original_message):
            return {
                "message": self._get_random_template("greeting"),
                "response_type": "greeting"
            }
        
        else:
            return {
                "message": self.response_templates["unknown"],
                "response_type": "unknown"
            }
    
    async def _handle_balance_query(self, student: Student, entities: Dict) -> Dict[str, Any]:
        """Handle balance and financial summary queries"""
        try:
            # Get recent transactions to calculate current balance
            transactions = await self._get_recent_transactions(student.id, days=30)
            
            total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
            total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
            balance = total_income - total_expense
            
            # Add contextual information
            if balance > 0:
                additional_info = "Keuangan Anda terkendali dengan baik! 👍"
            elif balance == 0:
                additional_info = "Pengeluaran sama dengan pemasukan bulan ini."
            else:
                additional_info = "Pengeluaran lebih besar dari pemasukan. Coba kurangi pengeluaran atau cari tambahan income."
            
            message = self.response_templates["balance"].format(
                balance=format_idr(balance),
                additional_info=additional_info
            )
            
            return {
                "message": message,
                "response_type": "info",
                "data_used": DataUsed(
                    transactions_count=len(transactions),
                    period_analyzed="30 hari terakhir"
                )
            }
            
        except Exception as e:
            logger.error(f"Balance query failed: {str(e)}")
            return {
                "message": "Maaf, saya tidak bisa mengambil data saldo Anda saat ini.",
                "response_type": "error"
            }
    
    async def _handle_expense_query(self, student: Student, entities: Dict) -> Dict[str, Any]:
        """Handle expense queries"""
        try:
            # Determine time period
            period = entities.get("time_period", "this_month")
            days = self._get_days_from_period(period)
            period_text = self._get_period_text(period)
            
            # Get transactions
            transactions = await self._get_recent_transactions(student.id, days=days)
            expenses = [t for t in transactions if t["type"] == "expense"]
            
            if not expenses:
                return {
                    "message": f"Tidak ada pengeluaran {period_text}.",
                    "response_type": "info"
                }
            
            total_expense = sum(t["amount"] for t in expenses)
            
            # Get top category
            category_totals = {}
            for expense in expenses:
                category = expense.get("category_name", "Lainnya")
                category_totals[category] = category_totals.get(category, 0) + expense["amount"]
            
            top_category = max(category_totals, key=category_totals.get) if category_totals else "Tidak ada"
            top_category_amount = category_totals.get(top_category, 0)
            
            message = self.response_templates["expense_summary"].format(
                period=period_text,
                amount=format_idr(total_expense),
                top_category=top_category,
                category_amount=format_idr(top_category_amount)
            )
            
            return {
                "message": message,
                "response_type": "info",
                "data_used": DataUsed(
                    transactions_count=len(expenses),
                    period_analyzed=period_text
                )
            }
            
        except Exception as e:
            logger.error(f"Expense query failed: {str(e)}")
            return {
                "message": "Maaf, saya tidak bisa mengambil data pengeluaran Anda saat ini.",
                "response_type": "error"
            }
    
    async def _handle_budget_query(self, student: Student, entities: Dict) -> Dict[str, Any]:
        """Handle budget-related queries"""
        try:
            # Get monthly allowance from student profile
            monthly_allowance = student.profile.monthly_allowance
            
            if monthly_allowance <= 0:
                return {
                    "message": "Anda belum mengatur allowance bulanan. Silakan update profil Anda dulu untuk mendapat saran budget yang lebih akurat.",
                    "response_type": "advice"
                }
            
            # Get this month's expenses
            transactions = await self._get_recent_transactions(student.id, days=30)
            monthly_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
            
            # Calculate budget usage
            budget_used_percentage = (monthly_expense / monthly_allowance) * 100
            
            if budget_used_percentage <= 70:
                status_message = "Budget Anda masih aman! 😊"
            elif budget_used_percentage <= 90:
                status_message = "Hati-hati, budget hampir habis! ⚠️"
            else:
                status_message = "Budget sudah terlampaui! Kurangi pengeluaran ya. 🚨"
            
            message = self.response_templates["budget_status"].format(
                period="bulan ini",
                used=format_idr(monthly_expense),
                total=format_idr(monthly_allowance),
                percentage=f"{budget_used_percentage:.1f}",
                status_message=status_message
            )
            
            return {
                "message": message,
                "response_type": "info",
                "data_used": DataUsed(
                    transactions_count=len(transactions),
                    period_analyzed="bulan ini"
                )
            }
            
        except Exception as e:
            logger.error(f"Budget query failed: {str(e)}")
            return {
                "message": "Maaf, saya tidak bisa mengambil data budget Anda saat ini.",
                "response_type": "error"
            }
    
    async def _handle_savings_advice(self, student: Student, entities: Dict) -> Dict[str, Any]:
        """Handle savings advice requests"""
        advice = self._get_random_template("savings_advice")
        
        # Add personalized advice based on student data
        try:
            transactions = await self._get_recent_transactions(student.id, days=30)
            expenses = [t for t in transactions if t["type"] == "expense"]
            
            if expenses:
                # Find top spending category
                category_totals = {}
                for expense in expenses:
                    category = expense.get("category_name", "Lainnya")
                    category_totals[category] = category_totals.get(category, 0) + expense["amount"]
                
                if category_totals:
                    top_category = max(category_totals, key=category_totals.get)
                    top_amount = category_totals[top_category]
                    
                    # Add specific advice based on top category
                    if top_category.lower() in ["makanan", "food"]:
                        advice += f"\n\nSaya lihat pengeluaran terbesar Anda di kategori {top_category} ({format_idr(top_amount)}). Coba masak sendiri lebih sering untuk menghemat!"
                    elif top_category.lower() in ["transportasi", "transportation"]:
                        advice += f"\n\nPengeluaran transportasi Anda cukup tinggi ({format_idr(top_amount)}). Coba gunakan transportasi umum atau bike sharing untuk hemat."
        
        except Exception as e:
            logger.warning(f"Could not personalize savings advice: {str(e)}")
        
        return {
            "message": advice,
            "response_type": "advice"
        }
    
    async def _handle_add_transaction_help(self, student: Student, entities: Dict) -> Dict[str, Any]:
        """Help user add new transaction"""
        message = "Untuk menambah transaksi baru, Anda bisa:\n\n"
        message += "1. Buka menu 'Tambah Transaksi' di aplikasi\n"
        message += "2. Atau katakan ke saya seperti: 'Catat pengeluaran makan 25 ribu'\n"
        message += "3. Saya akan bantu mengkategorikan transaksi Anda"
        
        if entities.get("amount"):
            amount = entities["amount"]
            category = entities.get("category", "makanan")
            message += f"\n\nSaya deteksi Anda ingin catat transaksi {format_idr(amount)} untuk kategori {category}. Benar?"
        
        return {
            "message": message,
            "response_type": "help"
        }
    
    async def _handle_income_query(self, student: Student, entities: Dict) -> Dict[str, Any]:
        """Handle income-related queries"""
        try:
            period = entities.get("time_period", "this_month")
            days = self._get_days_from_period(period)
            period_text = self._get_period_text(period)
            
            transactions = await self._get_recent_transactions(student.id, days=days)
            income_transactions = [t for t in transactions if t["type"] == "income"]
            
            total_income = sum(t["amount"] for t in income_transactions)
            
            if total_income == 0:
                message = f"Tidak ada pemasukan tercatat {period_text}."
            else:
                message = f"Total pemasukan {period_text}: {format_idr(total_income)}"
                
                # Add breakdown by source if available
                income_sources = {}
                for income in income_transactions:
                    source = income.get("category_name", "Lainnya")
                    income_sources[source] = income_sources.get(source, 0) + income["amount"]
                
                if len(income_sources) > 1:
                    message += "\n\nRincian:"
                    for source, amount in income_sources.items():
                        message += f"\n• {source}: {format_idr(amount)}"
            
            return {
                "message": message,
                "response_type": "info",
                "data_used": DataUsed(
                    transactions_count=len(income_transactions),
                    period_analyzed=period_text
                )
            }
            
        except Exception as e:
            logger.error(f"Income query failed: {str(e)}")
            return {
                "message": "Maaf, saya tidak bisa mengambil data pemasukan Anda saat ini.",
                "response_type": "error"
            }
    
    async def _handle_general_help(self, student: Student) -> Dict[str, Any]:
        """Handle general help requests"""
        help_message = "Berikut yang bisa saya bantu:\n\n"
        help_message += "💰 Cek saldo dan ringkasan keuangan\n"
        help_message += "📊 Lihat pengeluaran dan pemasukan\n"
        help_message += "📝 Bantuan mengatur budget\n"
        help_message += "💡 Tips hemat untuk mahasiswa\n"
        help_message += "📈 Saran menabung dan investasi\n\n"
        help_message += "Contoh pertanyaan:\n"
        help_message += "• 'Berapa saldo saya?'\n"
        help_message += "• 'Pengeluaran minggu ini berapa?'\n"
        help_message += "• 'Tips hemat untuk mahasiswa'\n"
        help_message += "• 'Gimana cara ngatur budget?'"
        
        return {
            "message": help_message,
            "response_type": "help"
        }
    
    async def _get_recent_transactions(self, student_id: str, days: int = 30) -> List[Dict]:
        """Get recent transactions for a student"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Query transactions from database
            transactions_cursor = self.db.transactions.find({
                "student_id": student_id,
                "transaction_date": {"$gte": start_date}
            }).sort("transaction_date", -1)
            
            transactions = []
            async for transaction in transactions_cursor:
                # Convert ObjectId to string
                transaction["_id"] = str(transaction["_id"])
                transaction["student_id"] = str(transaction["student_id"])
                if "category_id" in transaction:
                    transaction["category_id"] = str(transaction["category_id"])
                
                # Get category name if needed
                if "category_id" in transaction and "category_name" not in transaction:
                    category = await self.db.categories.find_one({"_id": transaction["category_id"]})
                    transaction["category_name"] = category["name"] if category else "Lainnya"
                
                transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            logger.error(f"Failed to get recent transactions: {str(e)}")
            return []
    
    def _get_days_from_period(self, period: str) -> int:
        """Convert period string to number of days"""
        period_mapping = {
            "today": 1,
            "yesterday": 1,
            "this_week": 7,
            "this_month": 30,
            "last_week": 7,
            "last_month": 30
        }
        return period_mapping.get(period, 30)
    
    def _get_period_text(self, period: str) -> str:
        """Convert period to Indonesian text"""
        period_text = {
            "today": "hari ini",
            "yesterday": "kemarin",
            "this_week": "minggu ini",
            "this_month": "bulan ini",
            "last_week": "minggu lalu",
            "last_month": "bulan lalu"
        }
        return period_text.get(period, "bulan ini")
    
    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        greetings = ["halo", "hai", "hi", "hello", "selamat", "pagi", "siang", "malam", "sore"]
        message_lower = message.lower()
        return any(greeting in message_lower for greeting in greetings)
    
    def _get_random_template(self, template_key: str) -> str:
        """Get random template from list"""
        templates = self.response_templates.get(template_key, [])
        if isinstance(templates, list):
            import random
            return random.choice(templates)
        return templates