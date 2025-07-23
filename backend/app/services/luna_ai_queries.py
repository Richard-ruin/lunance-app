# app/services/luna_ai_queries.py - FIXED version with proper integration
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId
import logging

from ..config.database import get_database
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .luna_ai_base import LunaAIBase
from .luna_financial_calculator import LunaFinancialCalculator

# Import services with proper error handling
try:
    from .finance_analyzer import FinanceAnalyzer
    FINANCE_ANALYZER_AVAILABLE = True
except ImportError:
    FINANCE_ANALYZER_AVAILABLE = False
    print("⚠️ FinanceAnalyzer not available")

try:
    from .finance_advisor import FinanceAdvisor  
    FINANCE_ADVISOR_AVAILABLE = True
except ImportError:
    FINANCE_ADVISOR_AVAILABLE = False
    print("⚠️ FinanceAdvisor not available")

logger = logging.getLogger(__name__)

class LunaAIQueries(LunaAIBase):
    """
    FIXED: Luna AI Queries with proper service integration
    Resolves Issue 2: Restored financial query capabilities
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize calculator (primary dependency)
        try:
            self.calculator = LunaFinancialCalculator()
            logger.info("✅ LunaFinancialCalculator initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LunaFinancialCalculator: {e}")
            self.calculator = None
        
        # Initialize optional services with error handling
        self.analyzer = None
        self.advisor = None
        
        if FINANCE_ANALYZER_AVAILABLE:
            try:
                self.analyzer = FinanceAnalyzer()
                logger.info("✅ FinanceAnalyzer initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize FinanceAnalyzer: {e}")
        
        if FINANCE_ADVISOR_AVAILABLE:
            try:
                self.advisor = FinanceAdvisor()
                logger.info("✅ FinanceAdvisor initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize FinanceAdvisor: {e}")
        
        logger.info(f"🔧 LunaAIQueries initialized - Calculator: {self.calculator is not None}, Analyzer: {self.analyzer is not None}, Advisor: {self.advisor is not None}")
    
    # ==========================================
    # PURCHASE INTENT HANDLER - FIXED
    # ==========================================
    
    async def handle_purchase_intent(self, user_id: str, purchase_intent: Dict[str, Any]) -> str:
        """FIXED: Handle purchase intent with proper error handling and fallbacks"""
        try:
            item_name = purchase_intent["item_name"]
            price = purchase_intent.get("price")
            
            logger.info(f"🛒 Processing purchase intent: {item_name} - {self.format_currency(price) if price else 'No price'}")
            
            # If no price provided
            if not price:
                return f"""💭 **Pertanyaan tentang pembelian {item_name}**

Untuk analisis yang akurat, coba sebutkan perkiraan harganya ya!

💡 **Contoh format yang lengkap:**
• *"Saya ingin membeli {item_name} seharga 2 juta"*
• *"Mau beli {item_name} budget 500rb"*
• *"Pengen {item_name} kira-kira 1.5 juta"*

Dengan info harga, saya bisa kasih analisis apakah aman untuk budget 50/30/20 kamu! 🎯"""
            
            # FIXED: Try purchase analysis with multiple fallback levels
            analysis_result = None
            
            # Level 1: Try with analyzer (most detailed)
            if self.analyzer:
                try:
                    analysis_result = await self.analyzer.analyze_purchase_impact(user_id, item_name, price)
                    if analysis_result.get("can_analyze"):
                        return self._generate_detailed_purchase_response(analysis_result)
                except Exception as e:
                    logger.error(f"❌ Analyzer purchase analysis failed: {e}")
            
            # Level 2: Try with advisor (medium detail)  
            if self.advisor:
                try:
                    advice_result = await self.advisor.generate_purchase_advice(user_id, item_name, price)
                    if advice_result.get("can_advise"):
                        return self._generate_advisor_purchase_response(advice_result)
                except Exception as e:
                    logger.error(f"❌ Advisor purchase analysis failed: {e}")
            
            # Level 3: Try with calculator (basic analysis)
            if self.calculator:
                try:
                    budget_data = await self.calculator.calculate_current_month_budget_performance(user_id)
                    if budget_data.get("has_budget"):
                        return self._generate_basic_purchase_response(item_name, price, budget_data)
                except Exception as e:
                    logger.error(f"❌ Calculator purchase analysis failed: {e}")
            
            # Level 4: Fallback - no financial data available
            return f"""💭 **Analisis Pembelian: {item_name}**
💰 **Harga**: {self.format_currency(price)}

Untuk analisis pembelian yang akurat, saya perlu data transaksi Anda dulu.

🚀 **Mulai dengan:**
1. Input beberapa transaksi income: *"Dapat uang saku 2 juta"*
2. Catat pengeluaran harian: *"Bayar kos 800rb"*, *"Jajan 50rb"*
3. Minimal 3-5 transaksi untuk analisis budget 50/30/20

Setelah ada data, saya bisa kasih analisis: "Apakah aman beli {item_name}?" 😊"""
            
        except Exception as e:
            logger.error(f"❌ Error in handle_purchase_intent: {e}")
            return f"""💭 **Pertanyaan tentang pembelian {purchase_intent.get('item_name', 'barang')}**

Maaf, terjadi kesalahan saat menganalisis pembelian. 😅

🔧 **Coba lagi dengan format:**
• "Saya ingin membeli [nama barang] seharga [harga]"

**Contoh**: *"Saya ingin membeli laptop seharga 10 juta"*"""
    
    def _generate_detailed_purchase_response(self, analysis_result: Dict[str, Any]) -> str:
        """Generate detailed purchase response from analyzer"""
        try:
            item_name = analysis_result["item_name"]
            price = analysis_result["price"]
            budget_type = analysis_result["budget_type"]
            feasibility = analysis_result["overall_assessment"]["feasibility"]
            budget_impact = analysis_result["budget_impact"]
            
            # Main recommendation
            if feasibility == "not_recommended":
                status_emoji = "🚨"
                status_text = "TIDAK DIREKOMENDASIKAN"
                reason = f"Akan melebihi budget {budget_type.upper()} sebesar {self.format_currency(budget_impact.get('overspend_amount', 0))}"
            elif feasibility == "risky":
                status_emoji = "⚠️"
                status_text = "BERISIKO"  
                reason = f"Akan menggunakan {budget_impact.get('after_purchase_percentage', 0):.1f}% dari budget {budget_type.upper()}"
            elif feasibility == "consider":
                status_emoji = "🤔"
                status_text = "PERTIMBANGKAN"
                reason = f"Menggunakan {budget_impact.get('after_purchase_percentage', 0):.1f}% budget {budget_type.upper()}"
            else:
                status_emoji = "✅"
                status_text = "DIREKOMENDASIKAN"
                reason = f"Hanya {budget_impact.get('after_purchase_percentage', 0):.1f}% dari budget {budget_type.upper()}"
            
            response = f"""💰 **Analisis Pembelian: {item_name}**

**💳 Detail:**
• **Harga**: {self.format_currency(price)}
• **Kategori Budget**: {budget_type.upper()} Budget
• **Sisa Budget {budget_type.upper()}**: {budget_impact.get('formatted_remaining', 'N/A')}

{status_emoji} **{status_text}**

📊 **Analisis**: {reason}

💡 **Rekomendasi**: {analysis_result['recommendations'][0] if analysis_result.get('recommendations') else 'Sesuaikan dengan kondisi budget Anda'}"""
            
            return response
        except Exception as e:
            logger.error(f"❌ Error generating detailed purchase response: {e}")
            return "😅 Terjadi kesalahan saat menyusun analisis pembelian."
    
    def _generate_advisor_purchase_response(self, advice_result: Dict[str, Any]) -> str:
        """Generate purchase response from advisor"""
        try:
            item_name = advice_result["item_name"]
            price = advice_result["price"]
            feasibility = advice_result["feasibility"]
            
            status_map = {
                "not_recommended": ("🚨", "TIDAK DIREKOMENDASIKAN"),
                "risky": ("⚠️", "BERISIKO"),
                "consider": ("🤔", "PERTIMBANGKAN"),
                "recommended": ("✅", "DIREKOMENDASIKAN")
            }
            
            status_emoji, status_text = status_map.get(feasibility, ("🤔", "PERLU EVALUASI"))
            
            response = f"""💰 **Analisis Pembelian: {item_name}**

**💳 Detail:**
• **Harga**: {advice_result['formatted_price']}
• **Kategori**: {advice_result['budget_type'].upper()}

{status_emoji} **{status_text}**

💡 **Saran**: {advice_result['advice'][0] if advice_result.get('advice') else 'Sesuaikan dengan budget Anda'}

⏰ **Timing**: {advice_result.get('timeline_advice', {}).get('action', 'Evaluasi timing pembelian')}"""
            
            return response
        except Exception as e:
            logger.error(f"❌ Error generating advisor purchase response: {e}")
            return "😅 Terjadi kesalahan saat menyusun saran pembelian."
    
    def _generate_basic_purchase_response(self, item_name: str, price: float, budget_data: Dict[str, Any]) -> str:
        """Generate basic purchase response using calculator only"""
        try:
            # Simple budget type determination
            item_lower = item_name.lower()
            if any(word in item_lower for word in ['laptop', 'hp', 'handphone', 'gadget', 'baju', 'sepatu']):
                budget_type = "wants"
            elif any(word in item_lower for word in ['buku', 'alat tulis', 'obat']):
                budget_type = "needs"
            else:
                budget_type = "wants"
            
            # Get budget performance
            performance = budget_data.get("performance", {})
            category_data = performance.get(budget_type, {})
            
            if not category_data:
                return f"""💰 **Analisis Pembelian: {item_name}**
💳 **Harga**: {self.format_currency(price)}

Untuk analisis yang akurat, pastikan sudah ada transaksi income dan expense di bulan ini."""
            
            remaining = category_data.get("remaining", 0)
            budget = category_data.get("budget", 0)
            
            if price <= remaining:
                status = "✅ **AMAN DIBELI**"
                advice = f"Masih ada sisa budget {budget_type.upper()}: {self.format_currency(remaining)}"
            elif price <= budget:
                over_amount = price - remaining
                status = "⚠️ **HATI-HATI**"
                advice = f"Akan melebihi sisa budget sebesar {self.format_currency(over_amount)}"
            else:
                status = "🚨 **TIDAK DIREKOMENDASIKAN**"
                advice = f"Melebihi total budget {budget_type.upper()} sebesar {self.format_currency(price - budget)}"
            
            response = f"""💰 **Analisis Pembelian: {item_name}**

**💳 Detail:**
• **Harga**: {self.format_currency(price)}
• **Kategori**: {budget_type.upper()} Budget
• **Budget Tersedia**: {self.format_currency(remaining)}

{status}

💡 **Analisis**: {advice}"""
            
            return response
        except Exception as e:
            logger.error(f"❌ Error generating basic purchase response: {e}")
            return "😅 Terjadi kesalahan saat analisis pembelian basic."
    
    # ==========================================
    # FINANCIAL QUERY HANDLERS - FIXED
    # ==========================================
    
    async def handle_financial_query(self, user_id: str, query_type: str) -> str:
        """FIXED: Handle financial queries with proper service integration and fallbacks"""
        try:
            logger.info(f"📊 Processing financial query: {query_type}")
            
            # FIXED: Route to specific query handlers with fallbacks
            if query_type == "total_tabungan":
                return await self._handle_total_savings_query(user_id)
                
            elif query_type == "financial_health":
                return await self._handle_financial_health_query(user_id)
                
            elif query_type == "budget_performance":
                return await self._handle_budget_performance_query(user_id)
                
            elif query_type == "savings_progress":
                return await self._handle_savings_progress_query(user_id)
                
            elif query_type == "list_targets" or query_type == "daftar_target":
                return await self._handle_list_savings_goals(user_id)
                
            elif query_type == "expense_analysis":
                return await self._handle_expense_analysis_query(user_id)
            
            else:
                # Fallback untuk query yang tidak dikenali
                return f"""📊 **Financial Query: {query_type.replace('_', ' ').title()}**

✅ **FIXED: Queries yang tersedia:**

💰 **Data Keuangan:**
• "Total tabungan saya berapa?"
• "Kesehatan keuangan saya gimana?"
• "Budget performance bulan ini"

🎯 **Target & Progress:**
• "Progress tabungan saya"
• "Daftar target saya"

📊 **Analisis:**
• "Pengeluaran terbesar saya"
• "Analisis pengeluaran saya"

Coba salah satu ya! 😊"""
            
        except Exception as e:
            logger.error(f"❌ Error handling financial query: {e}")
            return f"""📊 **Financial Query Error**

Maaf, terjadi kesalahan saat memproses query keuangan Anda. 😅

🔧 **Coba tanya dengan format yang spesifik:**
• "Total tabungan saya berapa?"
• "Kesehatan keuangan saya gimana?"
• "Budget performance bulan ini"

Error: {str(e)}"""
    
    # ==========================================
    # SPECIFIC QUERY HANDLERS - FIXED IMPLEMENTATION
    # ==========================================
    
    async def _handle_total_savings_query(self, user_id: str) -> str:
        """FIXED: Handle total savings query with multiple fallback levels"""
        try:
            # Level 1: Try with calculator (most reliable)
            if self.calculator:
                try:
                    return await self.calculator.get_total_savings_response(user_id)
                except Exception as e:
                    logger.error(f"❌ Calculator total savings failed: {e}")
            
            # Level 2: Try with analyzer
            if self.analyzer:
                try:
                    financial_status = await self.analyzer.analyze_user_financial_status(user_id)
                    if financial_status["status"] == "analyzed":
                        current_totals = financial_status["current_totals"]
                        real_total = current_totals["real_total_savings"]
                        
                        return f"""💰 **Total Tabungan Anda: {self.format_currency(real_total)}**

📊 **Breakdown (dari Analyzer):**
• **Tabungan Awal**: {self.format_currency(current_totals['initial_savings'])}
• **Total Pemasukan**: {self.format_currency(current_totals['total_income'])}
• **Total Pengeluaran**: {self.format_currency(current_totals['total_expense'])}
• **Net Growth**: {self.format_currency(current_totals['savings_growth'])}

💡 **Status**: {financial_status['health_score']['level'].replace('_', ' ').title()}"""
                except Exception as e:
                    logger.error(f"❌ Analyzer total savings failed: {e}")
            
            # Level 3: Basic fallback using database direct
            return await self._basic_total_savings_fallback(user_id)
            
        except Exception as e:
            logger.error(f"❌ Error in _handle_total_savings_query: {e}")
            return f"😅 Terjadi kesalahan saat menghitung total tabungan. Coba lagi ya!"
    
    async def _handle_financial_health_query(self, user_id: str) -> str:
        """FIXED: Handle financial health query"""
        try:
            # Level 1: Try with calculator
            if self.calculator:
                try:
                    return await self.calculator.get_financial_health_response(user_id)
                except Exception as e:
                    logger.error(f"❌ Calculator health analysis failed: {e}")
            
            # Level 2: Basic health assessment
            return await self._basic_health_assessment_fallback(user_id)
            
        except Exception as e:
            logger.error(f"❌ Error in _handle_financial_health_query: {e}")
            return f"😅 Terjadi kesalahan saat menganalisis kesehatan keuangan. Coba lagi ya!"
    
    async def _handle_budget_performance_query(self, user_id: str) -> str:
        """FIXED: Handle budget performance query"""
        try:
            # Level 1: Try with calculator
            if self.calculator:
                try:
                    return await self.calculator.get_budget_performance_response(user_id)
                except Exception as e:
                    logger.error(f"❌ Calculator budget performance failed: {e}")
            
            # Level 2: Basic budget check
            return await self._basic_budget_check_fallback(user_id)
            
        except Exception as e:
            logger.error(f"❌ Error in _handle_budget_performance_query: {e}")
            return f"😅 Terjadi kesalahan saat menganalisis budget performance. Coba lagi ya!"
    
    async def _handle_savings_progress_query(self, user_id: str) -> str:
        """FIXED: Handle savings progress query"""
        try:
            # Level 1: Try with calculator
            if self.calculator:
                try:
                    return await self.calculator.get_savings_goals_progress_response(user_id)
                except Exception as e:
                    logger.error(f"❌ Calculator savings progress failed: {e}")
            
            # Level 2: Basic savings goals check
            return await self._basic_savings_goals_fallback(user_id)
            
        except Exception as e:
            logger.error(f"❌ Error in _handle_savings_progress_query: {e}")
            return f"😅 Terjadi kesalahan saat menganalisis progress tabungan. Coba lagi ya!"
    
    async def _handle_expense_analysis_query(self, user_id: str) -> str:
        """FIXED: Handle expense analysis query"""
        try:
            # Simple expense analysis using database
            now = datetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Get expense transactions this month
            expenses = list(self.db.transactions.find({
                "user_id": user_id,
                "type": "expense",
                "status": "confirmed",
                "date": {"$gte": start_of_month}
            }))
            
            if not expenses:
                return """📊 **Analisis Pengeluaran**

Belum ada data pengeluaran bulan ini yang dapat dianalisis.

🚀 **Mulai tracking pengeluaran:**
• "Bayar kos 800 ribu"
• "Belanja groceries 150rb"
• "Jajan bubble tea 25rb"

Setelah ada transaksi, saya bisa analisis pengeluaran terbesar Anda! 📊"""
            
            # Group by category
            category_totals = {}
            total_expense = 0
            
            for expense in expenses:
                category = expense.get("category", "Lainnya")
                amount = expense.get("amount", 0)
                category_totals[category] = category_totals.get(category, 0) + amount
                total_expense += amount
            
            # Sort by amount
            sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            
            response = f"""📊 **Analisis Pengeluaran Bulan Ini**

💰 **Total Pengeluaran**: {self.format_currency(total_expense)}

🏆 **Top 5 Kategori:**
"""
            
            for i, (category, amount) in enumerate(sorted_categories[:5], 1):
                percentage = (amount / total_expense * 100) if total_expense > 0 else 0
                response += f"{i}. **{category}**: {self.format_currency(amount)} ({percentage:.1f}%)\n"
            
            response += f"\n📱 **Deep dive**: Tanya \"budget performance bulan ini\" untuk analisis 50/30/20!"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in _handle_expense_analysis_query: {e}")
            return f"😅 Terjadi kesalahan saat menganalisis pengeluaran. Coba lagi ya!"
    
    async def _handle_list_savings_goals(self, user_id: str) -> str:
        """FIXED: Handle list savings goals query"""
        try:
            # Get savings goals from database
            goals = list(self.db.savings_goals.find({
                "user_id": user_id,
                "status": {"$in": ["active", "paused", "completed"]}
            }).sort("created_at", -1))
            
            if not goals:
                return """🎯 **Daftar Target Tabungan**

Belum ada target tabungan. Yuk buat target pertama!

💡 **Contoh target tabungan:**
• "Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026"
• "Target beli motor 25 juta dalam 1 tahun"
• "Pengen beli smartphone 5 juta"

**Mulai sekarang!** Contoh: *"Mau nabung buat beli headset 500 ribu"*"""
            
            # Group goals by status
            active_goals = [g for g in goals if g["status"] == "active"]
            completed_goals = [g for g in goals if g["status"] == "completed"]
            paused_goals = [g for g in goals if g["status"] == "paused"]
            
            response = "🎯 **Daftar Target Tabungan Anda**:\n\n"
            
            # Active goals
            if active_goals:
                response += "**🟢 Target Aktif:**\n"
                for goal in active_goals:
                    progress = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
                    progress_bar = "🟩" * int(progress // 10) + "⬜" * (10 - int(progress // 10))
                    
                    target_date_str = ""
                    if goal.get("target_date"):
                        try:
                            target_date = goal["target_date"]
                            if isinstance(target_date, str):
                                target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                            
                            days_remaining = (target_date - datetime.now()).days
                            if days_remaining > 0:
                                target_date_str = f" (⏰ {days_remaining} hari lagi)"
                            elif days_remaining == 0:
                                target_date_str = " (⏰ hari ini!)"
                            else:
                                target_date_str = f" (⚠️ lewat {abs(days_remaining)} hari)"
                        except:
                            pass
                    
                    response += f"• **{goal['item_name']}**{target_date_str}\n"
                    response += f"  {progress_bar} {progress:.1f}%\n"
                    response += f"  💰 {self.format_currency(goal['current_amount'])} / {self.format_currency(goal['target_amount'])}\n\n"
            
            # Completed goals
            if completed_goals:
                response += "**🎉 Target Tercapai:**\n"
                for goal in completed_goals[:3]:  # Show max 3
                    response += f"• **{goal['item_name']}** - {self.format_currency(goal['target_amount'])} ✅\n"
                if len(completed_goals) > 3:
                    response += f"• *...dan {len(completed_goals) - 3} target lainnya*\n"
                response += "\n"
            
            # Paused goals
            if paused_goals:
                response += "**⏸️ Target Dipause:**\n"
                for goal in paused_goals[:2]:  # Show max 2
                    progress = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
                    response += f"• **{goal['item_name']}** ({progress:.1f}%) - {self.format_currency(goal['target_amount'])}\n"
                response += "\n"
            
            response += """**🛠️ Perintah yang bisa digunakan:**
• *"ubah target [nama]"* - Ubah target
• *"hapus target [nama]"* - Hapus target
• *"progress tabungan"* - Lihat progress detail

💡 *Tip: Sebutkan nama barang yang spesifik untuk perintah yang lebih akurat*"""
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in _handle_list_savings_goals: {e}")
            return f"😅 Maaf, terjadi kesalahan saat mengambil daftar target. Coba lagi ya!"
    
    # ==========================================
    # FALLBACK METHODS - BASIC IMPLEMENTATIONS
    # ==========================================
    
    async def _basic_total_savings_fallback(self, user_id: str) -> str:
        """Basic fallback for total savings calculation"""
        try:
            # Get user's initial savings
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            initial_savings = 0.0
            if user_doc and user_doc.get("financial_settings"):
                initial_savings = user_doc["financial_settings"].get("current_savings", 0.0)
            
            # Get transaction summary
            income_total = list(self.db.transactions.aggregate([
                {"$match": {"user_id": user_id, "type": "income", "status": "confirmed"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]))
            
            expense_total = list(self.db.transactions.aggregate([
                {"$match": {"user_id": user_id, "type": "expense", "status": "confirmed"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]))
            
            total_income = income_total[0]["total"] if income_total else 0
            total_expense = expense_total[0]["total"] if expense_total else 0
            
            real_total_savings = initial_savings + total_income - total_expense
            
            return f"""💰 **Total Tabungan Anda: {self.format_currency(max(real_total_savings, 0))}**

📊 **Breakdown (Fallback Calculation):**
• **Tabungan Awal**: {self.format_currency(initial_savings)}
• **Total Pemasukan**: {self.format_currency(total_income)}
• **Total Pengeluaran**: {self.format_currency(total_expense)}
• **Net Growth**: {self.format_currency(total_income - total_expense)}

💡 **Tips**: Input lebih banyak transaksi untuk analisis yang lebih akurat!"""
            
        except Exception as e:
            logger.error(f"❌ Error in basic savings fallback: {e}")
            return "😅 Tidak dapat menghitung total tabungan. Pastikan sudah ada transaksi yang tercatat."
    
    async def _basic_health_assessment_fallback(self, user_id: str) -> str:
        """Basic fallback for financial health assessment"""
        try:
            # Simple health check based on transaction count and balance
            transaction_count = self.db.transactions.count_documents({
                "user_id": user_id,
                "status": "confirmed"
            })
            
            if transaction_count < 5:
                health_level = "needs_data"
                health_emoji = "📊"
                health_message = "Butuh lebih banyak data transaksi untuk analisis"
            else:
                # Simple calculation
                now = datetime.now()
                this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                
                monthly_income = list(self.db.transactions.aggregate([
                    {"$match": {"user_id": user_id, "type": "income", "status": "confirmed", "date": {"$gte": this_month}}},
                    {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
                ]))
                
                monthly_expense = list(self.db.transactions.aggregate([
                    {"$match": {"user_id": user_id, "type": "expense", "status": "confirmed", "date": {"$gte": this_month}}},
                    {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
                ]))
                
                income = monthly_income[0]["total"] if monthly_income else 0
                expense = monthly_expense[0]["total"] if monthly_expense else 0
                
                if income > expense:
                    health_level = "good"
                    health_emoji = "👍"
                    health_message = "Pemasukan lebih besar dari pengeluaran - bagus!"
                elif income == expense:
                    health_level = "fair"
                    health_emoji = "📊"
                    health_message = "Pemasukan dan pengeluaran seimbang"
                else:
                    health_level = "needs_improvement"
                    health_emoji = "🆘"
                    health_message = "Pengeluaran melebihi pemasukan - perlu perhatian"
            
            return f"""{health_emoji} **Kesehatan Keuangan Anda (Basic Assessment)**

📊 **Status**: {health_level.replace('_', ' ').title()}

💬 **Assessment**: {health_message}

🎯 **Total Transaksi**: {transaction_count} transaksi

💡 **Tips**: Untuk analisis yang lebih detail, pastikan input transaksi secara konsisten!"""
            
        except Exception as e:
            logger.error(f"❌ Error in basic health assessment: {e}")
            return "😅 Tidak dapat melakukan analisis kesehatan keuangan basic."
    
    async def _basic_budget_check_fallback(self, user_id: str) -> str:
        """Basic fallback for budget performance check"""
        try:
            # Get user monthly income
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            monthly_income = 0
            if user_doc and user_doc.get("financial_settings"):
                monthly_income = user_doc["financial_settings"].get("monthly_income", 0)
            
            if monthly_income <= 0:
                return """📊 **Budget Performance Bulan Ini**

Belum ada setup monthly income untuk analisis budget 50/30/20.

🚀 **Untuk analisis budget:**
1. Setup monthly income di pengaturan
2. Input beberapa transaksi pengeluaran
3. Saya akan analisis dengan metode 50/30/20

💡 **Contoh**: Monthly income 2 juta = Budget NEEDS 1 juta, WANTS 600rb, SAVINGS 400rb"""
            
            # Get current month expenses
            now = datetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            total_expense = list(self.db.transactions.aggregate([
                {"$match": {"user_id": user_id, "type": "expense", "status": "confirmed", "date": {"$gte": start_of_month}}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]))
            
            spent_this_month = total_expense[0]["total"] if total_expense else 0
            remaining = monthly_income - spent_this_month
            percentage_used = (spent_this_month / monthly_income * 100) if monthly_income > 0 else 0
            
            if percentage_used <= 70:
                status = "🟢 Excellent"
            elif percentage_used <= 90:
                status = "🟡 Good"
            elif percentage_used <= 100:
                status = "🟠 Warning"
            else:
                status = "🔴 Over Budget"
            
            return f"""📊 **Budget Performance Bulan Ini (Basic Check)**

💰 **Monthly Income**: {self.format_currency(monthly_income)}
💸 **Total Spent**: {self.format_currency(spent_this_month)}
💰 **Remaining**: {self.format_currency(remaining)}

📈 **Usage**: {percentage_used:.1f}% dari income

{status}

💡 **Untuk analisis 50/30/20 yang detail, input lebih banyak transaksi dengan kategori yang jelas!**"""
            
        except Exception as e:
            logger.error(f"❌ Error in basic budget check: {e}")
            return "😅 Tidak dapat melakukan pengecekan budget basic."
    
    async def _basic_savings_goals_fallback(self, user_id: str) -> str:
        """Basic fallback for savings goals progress"""
        try:
            # Count savings goals
            total_goals = self.db.savings_goals.count_documents({
                "user_id": user_id,
                "status": {"$in": ["active", "paused", "completed"]}
            })
            
            active_goals = self.db.savings_goals.count_documents({
                "user_id": user_id,
                "status": "active"
            })
            
            completed_goals = self.db.savings_goals.count_documents({
                "user_id": user_id,
                "status": "completed"
            })
            
            if total_goals == 0:
                return """🎯 **Progress Target Tabungan**

Belum ada target tabungan aktif. Yuk buat target pertama untuk motivasi yang lebih baik! 🚀

💡 **Ide Target Tabungan:**
• **Tech**: "Mau nabung buat beli laptop 10 juta"
• **Transport**: "Target beli motor 25 juta"
• **Gadget**: "Pengen beli smartphone 5 juta"

🎯 **Kenapa perlu target tabungan?**
• Memberikan motivasi dan fokus yang jelas
• Membantu disiplin budget WANTS (30%)
• Training untuk financial planning jangka panjang

**Coba buat target sekarang!** Contoh: *"Mau nabung buat beli headset 500 ribu"*"""
            
            # Get sample of active goals
            sample_goals = list(self.db.savings_goals.find({
                "user_id": user_id,
                "status": "active"
            }).limit(3))
            
            response = f"""📈 **Progress Target Tabungan (Basic View)**

🎯 **Summary:**
• **Total Target**: {total_goals} target
• **Status**: {active_goals} Aktif | {completed_goals} Selesai

"""
            
            if sample_goals:
                response += "🏃‍♂️ **Contoh Target Aktif:**\n\n"
                for goal in sample_goals:
                    progress = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
                    response += f"• **{goal['item_name']}**: {progress:.1f}% ({self.format_currency(goal['current_amount'])} / {self.format_currency(goal['target_amount'])})\n"
            
            response += f"\n💡 **Tips**: Tanya \"daftar target saya\" untuk melihat semua target dengan detail lengkap!"
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in basic savings goals fallback: {e}")
            return "😅 Tidak dapat mengambil progress target tabungan basic."