# app/services/luna_ai_queries.py - FIXED version yang mengganti yang lama
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .luna_ai_base import LunaAIBase
from .luna_financial_calculator import LunaFinancialCalculator
from .finance_advisor import FinanceAdvisor


class LunaAIQueries(LunaAIBase):
    """
    FIXED: Luna AI Queries dengan real financial data calculation
    Versi yang sudah diperbaiki untuk integrasi IndoRoBERTa
    """
    
    def __init__(self):
        super().__init__()
        self.calculator = LunaFinancialCalculator()
        self.advisor = FinanceAdvisor()
    
    # ==========================================
    # PURCHASE INTENT HANDLER - ENHANCED
    # ==========================================
    
    async def handle_purchase_intent(self, user_id: str, purchase_intent: Dict[str, Any]) -> str:
        """FIXED: Handle purchase intent dengan analisis yang akurat"""
        try:
            item_name = purchase_intent["item_name"]
            price = purchase_intent["price"]
            
            print(f"🛒 Processing purchase intent: {item_name} - {self.format_currency(price)}")
            
            # Get real financial data for analysis
            budget_data = await self.calculator.calculate_current_month_budget_performance(user_id)
            savings_data = await self.calculator.calculate_real_total_savings(user_id)
            
            if not budget_data.get("has_budget"):
                return f"""💭 **Analisis Pembelian: {item_name}**
💰 **Harga**: {self.format_currency(price)}

Untuk analisis pembelian yang akurat, saya perlu data transaksi Anda dulu.

🚀 **Mulai dengan:**
1. Input beberapa transaksi income: *"Dapat uang saku 2 juta"*
2. Catat pengeluaran harian: *"Bayar kos 800rb"*, *"Jajan 50rb"*
3. Minimal 3-5 transaksi untuk analisis budget 50/30/20

Setelah ada data, saya bisa kasih analisis: "Apakah aman beli {item_name}?" 😊"""
            
            # Determine budget type for the item
            budget_type = self._determine_item_budget_type(item_name)
            
            # Calculate affordability
            base_income = budget_data["base_income"]
            performance = budget_data["performance"]
            
            if budget_type in performance:
                category_info = performance[budget_type]
                current_remaining = category_info["remaining"]
                
                # Affordability assessment
                if price <= current_remaining:
                    feasibility = "recommended"
                    feasibility_emoji = "✅"
                    feasibility_message = "DIREKOMENDASIKAN"
                elif price <= current_remaining * 1.2:
                    feasibility = "consider"
                    feasibility_emoji = "🤔"
                    feasibility_message = "PERTIMBANGKAN"
                elif price <= current_remaining * 1.5:
                    feasibility = "risky"
                    feasibility_emoji = "⚠️"
                    feasibility_message = "BERISIKO"
                else:
                    feasibility = "not_recommended"
                    feasibility_emoji = "🚨"
                    feasibility_message = "TIDAK DIREKOMENDASIKAN"
                
                # Generate response
                response = f"""💰 **Analisis Pembelian: {item_name}**

**💳 Detail:**
• **Harga**: {self.format_currency(price)}
• **Kategori Budget**: {budget_type.upper()} Budget
• **Sisa Budget {budget_type.upper()}**: {category_info['formatted_remaining']}

{feasibility_emoji} **{feasibility_message}**

"""
                
                # Specific analysis
                if feasibility == "recommended":
                    response += f"💚 **Analisis**: Pembelian ini aman untuk budget {budget_type.upper()} Anda\n"
                    response += f"📊 **Impact**: Hanya {(price/category_info['budget']*100):.1f}% dari budget {budget_type.upper()}\n"
                    
                elif feasibility == "consider":
                    response += f"💡 **Analisis**: Masih bisa dibeli tapi akan menggunakan {(price/category_info['budget']*100):.1f}% budget {budget_type.upper()}\n"
                    response += f"🔍 **Saran**: Pastikan tidak ada pengeluaran {budget_type} lain yang urgent\n"
                    
                elif feasibility == "risky":
                    over_amount = price - current_remaining
                    response += f"⚠️ **Analisis**: Akan melebihi budget {budget_type.upper()} sebesar {self.format_currency(over_amount)}\n"
                    response += f"🤔 **Saran**: Pertimbangkan menunda atau cari versi yang lebih murah\n"
                    
                else:  # not_recommended
                    over_amount = price - current_remaining
                    response += f"❌ **Analisis**: Akan merusak budget {budget_type.upper()} - melebihi {self.format_currency(over_amount)}\n"
                    response += f"🚨 **Saran**: Tunda pembelian atau alokasikan dari budget bulan depan\n"
                
                # Add timing advice
                response += f"\n🗓️ **Timing Advice:**\n"
                if feasibility in ["recommended", "consider"]:
                    response += f"• Bisa dibeli bulan ini dengan monitoring ketat\n"
                else:
                    response += f"• Lebih baik tunggu bulan depan saat budget reset\n"
                    response += f"• Atau buat target tabungan dari budget WANTS\n"
                
                # Add budget context
                budget_health = budget_data["overall"]["budget_health"]
                if budget_health in ["warning", "critical"]:
                    response += f"\n⚠️ **Note**: Budget health saat ini {budget_health} - lebih hati-hati dengan spending"
                
                return response
            
            else:
                return f"💭 **Analisis Pembelian: {item_name}**\n\nMaaf, terjadi kesalahan dalam menganalisis budget. Coba tanya lagi ya!"
            
        except Exception as e:
            print(f"Error handling purchase intent: {e}")
            return f"""💭 **Pertanyaan tentang pembelian {purchase_intent.get('item_name', 'barang')}**

Maaf, terjadi kesalahan saat menganalisis pembelian. 😅

🔧 **Coba lagi dengan format:**
• "Saya ingin membeli [nama barang] seharga [harga]"

**Contoh**: *"Saya ingin membeli laptop seharga 10 juta"*"""
    
    # ==========================================
    # FINANCIAL QUERY HANDLERS - FIXED
    # ==========================================
    
    async def handle_financial_query(self, user_id: str, query_type: str) -> str:
        """FIXED: Handle financial queries dengan response yang akurat dan helpful"""
        try:
            print(f"📊 Processing financial query: {query_type}")
            
            # Route to specific query handlers
            if query_type == "total_tabungan":
                return await self.calculator.get_total_savings_response(user_id)
                
            elif query_type == "financial_health":
                return await self.calculator.get_financial_health_response(user_id)
                
            elif query_type == "budget_performance":
                return await self.calculator.get_budget_performance_response(user_id)
                
            elif query_type == "progress_tabungan":
                return await self.calculator.get_savings_goals_progress_response(user_id)
                
            elif query_type == "list_targets" or query_type == "daftar_target":
                return await self.handle_list_savings_goals(user_id)
                
            elif query_type == "target_bulanan":
                return await self._handle_monthly_target_query(user_id)
                
            elif query_type == "pengeluaran_terbesar":
                return await self._handle_biggest_expense_query(user_id)
                
            elif query_type == "spending_analysis":
                return await self._handle_spending_analysis_query(user_id)
                
            elif query_type == "ringkasan":
                return await self._handle_financial_summary_query(user_id)
                
            else:
                # Fallback untuk query yang tidak dikenali
                return f"""📊 **Financial Query: {query_type.replace('_', ' ').title()}**

Fitur ini sedang dikembangkan. Untuk saat ini Anda bisa tanya:

💰 **Data Keuangan:**
• "Total tabungan saya berapa?"
• "Kesehatan keuangan saya gimana?"
• "Budget performance bulan ini"

🎯 **Target & Progress:**
• "Progress tabungan saya"
• "Daftar target saya"
• "Target bulanan saya"

📊 **Analisis:**
• "Pengeluaran terbesar saya"
• "Analisis pengeluaran saya"
• "Ringkasan keuangan saya"

Coba salah satu ya! 😊"""
            
        except Exception as e:
            print(f"❌ Error handling financial query: {e}")
            return f"""📊 **Financial Query Error**

Maaf, terjadi kesalahan saat memproses query keuangan Anda. 😅

🔧 **Coba tanya dengan format yang lebih spesifik:**
• "Total tabungan saya berapa?"
• "Kesehatan keuangan saya gimana?"
• "Budget performance bulan ini"

Atau tunggu sebentar dan coba lagi!"""
    
    # ==========================================
    # SPECIFIC QUERY HANDLERS - IMPLEMENTATION
    # ==========================================
    
    async def _handle_monthly_target_query(self, user_id: str) -> str:
        """Handle query tentang target bulanan"""
        try:
            budget_data = await self.calculator.calculate_current_month_budget_performance(user_id)
            
            if not budget_data.get("has_budget"):
                return """🎯 **Target Bulanan**

Untuk melihat target bulanan, saya perlu data income Anda dulu.

📝 **Setup yang dibutuhkan:**
1. Input beberapa transaksi income
2. Sistem akan menghitung target savings 20% otomatis
3. Target akan update berdasarkan income real Anda

**Contoh**: *"Dapat uang saku 2 juta dari ortu"*

Setelah ada data income, target bulanan akan muncul otomatis! 🚀"""
            
            base_income = budget_data["base_income"]
            savings_budget = budget_data["budget_allocation"]["savings_budget"]
            savings_performance = budget_data["performance"]["savings"]
            
            # Calculate monthly savings target (20% of income)
            monthly_target = savings_budget
            actual_savings = savings_performance["spent"]
            progress_percentage = (actual_savings / monthly_target * 100) if monthly_target > 0 else 0
            
            response = f"""🎯 **Target Bulanan Anda**

💰 **Base Income**: {budget_data['formatted']['base_income']}
📊 **Target Savings (20%)**: {self.format_currency(monthly_target)}
💳 **Actual Savings**: {savings_performance['formatted_spent']}

📈 **Progress Target:**"""
            
            # Progress bar
            filled_bars = min(10, int(progress_percentage // 10))
            progress_bar = "🟩" * filled_bars + "⬜" * (10 - filled_bars)
            response += f"\n{progress_bar} {progress_percentage:.1f}%\n"
            
            # Status assessment
            if progress_percentage >= 100:
                response += f"\n🎉 **AMAZING!** Target bulanan sudah tercapai!\n"
                response += f"🏆 **Surplus**: {self.format_currency(actual_savings - monthly_target)}\n"
                response += f"💡 **Saran**: Alokasikan surplus untuk investasi atau target jangka panjang\n"
                
            elif progress_percentage >= 75:
                response += f"\n👍 **EXCELLENT!** Hampir mencapai target 20%!\n"
                shortage = monthly_target - actual_savings
                response += f"🎯 **Sisa Target**: {self.format_currency(shortage)}\n"
                response += f"💪 **Saran**: Sedikit push lagi untuk achieve target!\n"
                
            elif progress_percentage >= 50:
                response += f"\n📊 **GOOD!** Sudah separuh jalan ke target\n"
                shortage = monthly_target - actual_savings
                response += f"🎯 **Sisa Target**: {self.format_currency(shortage)}\n"
                response += f"📈 **Saran**: Focus optimasi budget WANTS untuk boost savings\n"
                
            else:
                response += f"\n🚀 **KEEP GOING!** Masih ada waktu untuk catch up\n"
                shortage = monthly_target - actual_savings
                response += f"🎯 **Target Remaining**: {self.format_currency(shortage)}\n"
                response += f"💡 **Action**: Review semua pengeluaran WANTS yang bisa ditunda\n"
            
            return response
            
        except Exception as e:
            print(f"Error handling monthly target query: {e}")
            return "😅 Terjadi kesalahan saat mengambil target bulanan. Coba tanya lagi ya!"
    
    async def _handle_biggest_expense_query(self, user_id: str) -> str:
        """Handle query tentang pengeluaran terbesar"""
        try:
            # Get current month transactions
            now = IndonesiaDatetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_of_month_utc = IndonesiaDatetime.to_utc(start_of_month).replace(tzinfo=None)
            
            # Aggregate spending by category
            pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "type": "expense",
                    "status": "confirmed",
                    "date": {"$gte": start_of_month_utc}
                }},
                {"$group": {
                    "_id": "$category",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"total": -1}}
            ]
            
            category_spending = list(self.db.transactions.aggregate(pipeline))
            
            if not category_spending:
                return """💸 **Pengeluaran Terbesar Bulan Ini**

Belum ada data pengeluaran bulan ini yang dapat dianalisis.

🚀 **Mulai tracking pengeluaran:**
• "Bayar kos 800 ribu"
• "Belanja groceries 150rb"
• "Jajan bubble tea 25rb"

Setelah ada transaksi, saya bisa analisis pengeluaran terbesar Anda! 📊"""
            
            top_category = category_spending[0]
            total_spending = sum(cat["total"] for cat in category_spending)
            
            response = f"""💸 **Pengeluaran Terbesar Bulan Ini**

🏆 **#1 {top_category['_id']}**
• **Total**: {self.format_currency(top_category['total'])} ({(top_category['total']/total_spending*100):.1f}% dari total)
• **Frekuensi**: {top_category['count']}x transaksi
• **Rata-rata**: {self.format_currency(top_category['total']/top_category['count'])}/transaksi

"""
            
            # Show top 3 categories
            if len(category_spending) > 1:
                response += f"📊 **Top 3 Kategori:**\n"
                for i, cat in enumerate(category_spending[:3], 1):
                    percentage = (cat['total'] / total_spending * 100)
                    response += f"{i}. **{cat['_id']}**: {self.format_currency(cat['total'])} ({percentage:.1f}%)\n"
                response += "\n"
            
            response += f"📱 **Deep dive**: Tanya \"budget performance bulan ini\" untuk analisis 50/30/20!"
            
            return response
            
        except Exception as e:
            print(f"Error handling biggest expense query: {e}")
            return "😅 Terjadi kesalahan saat menganalisis pengeluaran terbesar. Coba lagi ya!"
    
    async def _handle_spending_analysis_query(self, user_id: str) -> str:
        """Handle query analisis pengeluaran mendalam"""
        try:
            # Get budget performance first
            budget_data = await self.calculator.calculate_current_month_budget_performance(user_id)
            
            if not budget_data.get("has_budget"):
                return """📈 **Analisis Pengeluaran**

Untuk analisis pengeluaran yang mendalam, saya perlu data transaksi Anda.

📝 **Yang dibutuhkan:**
1. Data income untuk menghitung budget 50/30/20
2. Minimal 5-10 transaksi pengeluaran  
3. Mix kategori: NEEDS, WANTS, SAVINGS

**Start tracking**: *"Bayar kos 800rb"*, *"Jajan 25rb"*, *"Freelance dapat 500rb"*

Setelah ada data, saya bisa kasih analisis pattern spending yang detail! 🔍"""
            
            # Get spending breakdown
            performance = budget_data["performance"]
            base_income = budget_data["base_income"]
            
            response = f"""📈 **Analisis Pengeluaran Mendalam**

💰 **Base Income**: {budget_data['formatted']['base_income']}
📊 **Method**: 50/30/20 Elizabeth Warren
🗓️ **Period**: {budget_data['period']}

📋 **Spending Breakdown:**

"""
            
            # Analyze each budget type
            total_spent = sum(perf["spent"] for perf in performance.values())
            
            for budget_type in ["needs", "wants", "savings"]:
                if budget_type in performance:
                    info = performance[budget_type]
                    percentage_of_income = (info["spent"] / base_income * 100) if base_income > 0 else 0
                    
                    # Visual indicator
                    if info["status"] == "over":
                        status_emoji = "🔴"
                        status_text = "OVER BUDGET"
                    elif info["percentage_used"] > 80:
                        status_emoji = "🟡"
                        status_text = "NEAR LIMIT"
                    else:
                        status_emoji = "🟢"
                        status_text = "ON TRACK"
                    
                    response += f"{status_emoji} **{budget_type.upper()}** ({status_text}):\n"
                    response += f"   💸 Spent: {info['formatted_spent']} ({percentage_of_income:.1f}% of income)\n"
                    response += f"   🎯 Target: {info['formatted_budget']} (Budget: {info['percentage_used']:.1f}%)\n"
                    response += f"   ⚖️ Remaining: {info['formatted_remaining']}\n\n"
            
            response += f"📱 **Next Step**: Tanya \"pengeluaran terbesar saya\" untuk category deep-dive!"
            
            return response
            
        except Exception as e:
            print(f"Error handling spending analysis query: {e}")
            return "😅 Terjadi kesalahan saat menganalisis spending pattern. Coba tanya lagi!"
    
    async def _handle_financial_summary_query(self, user_id: str) -> str:
        """Handle query ringkasan keuangan komprehensif"""
        try:
            # Get all financial data
            savings_data = await self.calculator.calculate_real_total_savings(user_id)
            budget_data = await self.calculator.calculate_current_month_budget_performance(user_id)
            goals_data = await self.calculator.calculate_savings_goals_progress(user_id)
            health_data = await self.calculator.calculate_financial_health_score(user_id)
            
            response = f"""{health_data['level_emoji']} **Ringkasan Keuangan Anda**

💰 **Financial Overview:**
• **Total Tabungan**: {savings_data['formatted_real_total']}
• **Net Growth**: {savings_data['formatted_net_growth']}
• **Health Score**: {health_data['score']}/{health_data['max_score']} ({health_data['level'].replace('_', ' ').title()})

"""
            
            # Budget summary
            if budget_data.get("has_budget"):
                response += f"📊 **Budget Performance (50/30/20):**\n"
                response += f"• **Base Income**: {budget_data['formatted']['base_income']}\n"
                response += f"• **Total Spent**: {budget_data['formatted']['total_spent']}\n"
                response += f"• **Budget Health**: {budget_data['overall']['budget_health'].replace('_', ' ').title()}\n\n"
            
            response += f"\n📱 **Stay connected**: Tanya ringkasan lagi minggu depan untuk track improvement!"
            
            return response
            
        except Exception as e:
            print(f"Error handling financial summary query: {e}")
            return "😅 Terjadi kesalahan saat menyiapkan ringkasan keuangan. Coba lagi ya!"
    
    # ==========================================
    # HELPER METHODS
    # ==========================================
    
    async def handle_list_savings_goals(self, user_id: str) -> str:
        """Handle request untuk list semua savings goals"""
        try:
            goals_data = await self.calculator.calculate_savings_goals_progress(user_id)
            
            if not goals_data.get("has_goals"):
                return """🎯 **Daftar Target Tabungan**

Belum ada target tabungan. Yuk buat target pertama!

💡 **Contoh target tabungan:**
• "Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026"
• "Target beli motor 25 juta dalam 1 tahun"
• "Pengen beli smartphone 5 juta"

**Mulai sekarang!** Contoh: *"Mau nabung buat beli headset 500 ribu"*"""
            
            # Implementation continues...
            return "📊 Target tabungan implementation..."
            
        except Exception as e:
            print(f"Error listing savings goals: {e}")
            return "😅 Maaf, terjadi kesalahan saat mengambil daftar target. Coba lagi ya!"
    
    def _determine_item_budget_type(self, item_name: str) -> str:
        """Determine budget type for an item in purchase analysis"""
        item_lower = item_name.lower()
        
        # NEEDS items
        needs_keywords = ['buku', 'kuliah', 'laptop kuliah', 'hp untuk kuliah', 'transportasi', 'makanan', 'obat', 'vitamin']
        for keyword in needs_keywords:
            if keyword in item_lower:
                return "needs"
        
        # SAVINGS items (investment-like)
        savings_keywords = ['investasi', 'tabungan', 'deposito', 'reksadana', 'saham']
        for keyword in savings_keywords:
            if keyword in item_lower:
                return "savings"
        
        # WANTS items (default for most consumer goods)
        return "wants"