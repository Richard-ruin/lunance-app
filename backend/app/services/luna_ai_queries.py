# app/services/luna_ai_queries.py - Financial Query Handlers untuk Luna AI
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId

from ..config.database import get_database
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .luna_ai_base import LunaAIBase
from .finance_analyzer import FinanceAnalyzer
from .finance_advisor import FinanceAdvisor


class LunaAIQueries(LunaAIBase):
    """Luna AI Queries untuk financial queries & purchase analysis"""
    
    def __init__(self):
        super().__init__()
        self.analyzer = FinanceAnalyzer()
        self.advisor = FinanceAdvisor()
    
    # ==========================================
    # PURCHASE INTENT HANDLER
    # ==========================================
    
    async def handle_purchase_intent(self, user_id: str, purchase_intent: Dict[str, Any]) -> str:
        """Handle purchase intent dengan analisis lengkap"""
        try:
            item_name = purchase_intent["item_name"]
            price = purchase_intent["price"]
            
            # Analyze purchase impact menggunakan FinanceAnalyzer
            purchase_advice = await self.advisor.generate_purchase_advice(user_id, item_name, price)
            
            if not purchase_advice["can_advise"]:
                return f"""🤔 **Pertanyaan tentang pembelian {item_name} seharga {self.format_currency(price)}**

{purchase_advice["message"]}

Untuk mendapatkan analisis yang akurat, silakan:
1. Setup budget bulanan dengan metode 50/30/20
2. Catat beberapa transaksi untuk building profile
3. Tanyakan lagi setelah setup selesai

Butuh bantuan setup? Ketik: **"bantuan setup budget"**"""
            
            # Generate comprehensive response
            response = f"""💰 **Analisis Pembelian: {item_name}**

**Harga**: {purchase_advice["formatted_price"]}
**Kategori**: {purchase_advice["category"]} ({purchase_advice["budget_type"].upper()})

"""
            
            # Main assessment
            feasibility = purchase_advice["feasibility"]
            if feasibility == "not_recommended":
                response += "🚨 **TIDAK DIREKOMENDASIKAN**\n\n"
            elif feasibility == "risky":
                response += "⚠️ **BERISIKO - Pertimbangkan Matang-Matang**\n\n"
            elif feasibility == "consider":
                response += "🤔 **PERTIMBANGKAN DENGAN HATI-HATI**\n\n"
            elif feasibility == "recommended":
                response += "✅ **DIREKOMENDASIKAN**\n\n"
            
            # Add main advice
            for advice in purchase_advice["advice"][:3]:  # Limit to 3 main points
                response += f"• {advice}\n"
            
            response += "\n"
            
            # Add alternatives if needed
            if purchase_advice["alternatives"]:
                response += "**🔄 Alternatif:**\n"
                for alt in purchase_advice["alternatives"][:3]:  # Limit to 3 alternatives
                    response += f"• {alt}\n"
                response += "\n"
            
            # Add timing advice
            timeline = purchase_advice["timeline_advice"]
            if timeline["recommended_timing"] != "anytime":
                response += f"**⏰ Waktu yang Tepat:** {timeline['action']}\n\n"
            
            # Add motivational closing
            if feasibility == "recommended":
                response += "💪 Dengan financial health yang baik, Anda bisa menikmati pembelian ini tanpa khawatir!"
            elif feasibility == "not_recommended":
                response += "🎯 Focus pada stabilitas budget dulu, nanti pasti ada kesempatan yang tepat!"
            else:
                response += "📊 Keputusan ada di tangan Anda! Pertimbangkan dengan bijak sesuai prioritas."
            
            return response
            
        except Exception as e:
            print(f"Error handling purchase intent: {e}")
            return f"""🤔 **Pertanyaan tentang pembelian {purchase_intent.get('item_name', 'barang')}**

Maaf, terjadi kesalahan saat menganalisis pembelian. Coba tanyakan lagi dengan format:

*"Saya ingin membeli [nama barang] seharga [harga]"*

Contoh: *"Saya ingin membeli laptop seharga 10 juta"*"""
    
    # ==========================================
    # FINANCIAL QUERY HANDLERS
    # ==========================================
    
    async def handle_financial_query(self, user_id: str, query_type: str) -> str:
        """Handle pertanyaan tentang data keuangan user dengan analisis mendalam"""
        try:
            if query_type == "list_targets":
                return await self.handle_list_savings_goals(user_id)
            
            # Use FinanceAnalyzer for comprehensive analysis
            financial_analysis = await self.analyzer.analyze_user_financial_status(user_id)
            
            if financial_analysis["status"] != "analyzed":
                return f"""📊 **Data Keuangan Belum Tersedia**

{financial_analysis.get("message", "Belum ada data keuangan yang dapat dianalisis")}

Untuk mendapatkan insight keuangan yang akurat:
1. Setup budget bulanan dengan metode 50/30/20
2. Catat beberapa transaksi (pemasukan & pengeluaran)
3. Buat target tabungan untuk motivasi

Butuh bantuan setup? Ketik: **"bantuan setup budget"**"""
            
            # Handle different query types
            if query_type == "total_tabungan":
                return await self._handle_total_tabungan_query(financial_analysis)
            elif query_type == "financial_health":
                return await self._handle_financial_health_query(financial_analysis)
            elif query_type == "budget_performance":
                return await self._handle_budget_performance_query(financial_analysis)
            elif query_type == "spending_analysis":
                return await self._handle_spending_analysis_query(financial_analysis)
            elif query_type == "progress_tabungan":
                return await self._handle_progress_tabungan_query(financial_analysis)
            elif query_type == "target_bulanan":
                return await self._handle_target_bulanan_query(financial_analysis)
            elif query_type == "pengeluaran_terbesar":
                return await self._handle_pengeluaran_terbesar_query(financial_analysis)
            elif query_type == "ringkasan":
                return await self._handle_ringkasan_query(financial_analysis)
            else:
                return "📊 Fitur analisis ini sedang dikembangkan. Untuk saat ini Anda bisa tanya tentang total tabungan, kesehatan keuangan, atau performa budget."
            
        except Exception as e:
            print(f"❌ Error handling financial query: {e}")
            return f"😅 Maaf, terjadi kesalahan saat menganalisis data keuangan. Coba tanya lagi ya! Error: {str(e)}"
    
    async def _handle_total_tabungan_query(self, financial_analysis: Dict[str, Any]) -> str:
        """Handle query total tabungan"""
        current_totals = financial_analysis["current_totals"]
        total_savings = current_totals["real_total_savings"]
        
        response = f"""📊 **Total Tabungan Anda**: {self.format_currency(total_savings)}

**Breakdown:**
• Tabungan Awal: {self.format_currency(current_totals["initial_savings"])}
• Total Pemasukan: {self.format_currency(current_totals["total_income"])}
• Total Pengeluaran: {self.format_currency(current_totals["total_expense"])}
• **Net Growth**: {self.format_currency(current_totals["savings_growth"])}

"""
        
        # Add contextual advice
        if current_totals["savings_growth"] > 0:
            response += "📈 **Selamat!** Tabungan Anda bertumbuh positif!\n\n"
        elif current_totals["savings_growth"] < 0:
            response += "📉 **Perhatian!** Tabungan Anda berkurang. Waktunya evaluasi pengeluaran.\n\n"
        else:
            response += "📊 **Stabil** - Pemasukan dan pengeluaran seimbang.\n\n"
        
        # Add tips based on health level
        health_level = financial_analysis["health_score"]["level"]
        if health_level == "needs_improvement":
            response += "💡 **Saran:** Focus pada budgeting 50/30/20 untuk meningkatkan tabungan"
        elif health_level == "fair":
            response += "💪 **Saran:** Pertahankan konsistensi dan tingkatkan sedikit alokasi savings"
        elif health_level == "good":
            response += "🎯 **Saran:** Excellent! Pertimbangkan untuk mulai investasi sederhana"
        else:
            response += "🏆 **Saran:** Amazing! Anda bisa mulai explore investasi jangka panjang"
        
        response += "\n\nTetap semangat menabung! 💪"
        
        return response
    
    async def _handle_financial_health_query(self, financial_analysis: Dict[str, Any]) -> str:
        """Handle query kesehatan keuangan"""
        health_score = financial_analysis["health_score"]
        
        # Emoji based on health level
        level_emoji = {
            "excellent": "🏆",
            "good": "👍",
            "fair": "📊",
            "needs_improvement": "🆘"
        }
        
        emoji = level_emoji.get(health_score["level"], "📊")
        
        response = f"""{emoji} **Kesehatan Keuangan Anda**

**Score**: {health_score['score']}/{health_score['max_score']} ({health_score['percentage']:.1f}%)
**Level**: {health_score['level'].replace('_', ' ').title()}

**Komponen Penilaian:**
• Budget Discipline: {health_score['components'].get('budget_discipline', 'Unknown')}
• Savings Progress: {health_score['components'].get('savings_progress', 0):.1f}%
• Savings Growth: {self.format_currency(health_score['components'].get('savings_growth', 0))}
• Transaction Activity: {health_score['components'].get('transaction_activity', 0)} transaksi

"""
        
        # Add level-specific message
        if health_score["level"] == "excellent":
            response += "🎉 **Luar Biasa!** Financial management Anda sudah sangat baik!"
        elif health_score["level"] == "good":
            response += "👏 **Bagus!** Anda sudah on track dengan financial planning"
        elif health_score["level"] == "fair":
            response += "📈 **Cukup Baik!** Ada ruang untuk improvement"
        else:
            response += "💪 **Semangat!** Mari kita tingkatkan financial health Anda"
        
        response += "\n\n💡 **Rekomendasi:**\n"
        
        # Add top 3 recommendations
        for i, rec in enumerate(financial_analysis['recommendations'][:3], 1):
            response += f"{i}. {rec}\n"
        
        return response
    
    async def _handle_budget_performance_query(self, financial_analysis: Dict[str, Any]) -> str:
        """Handle query performa budget"""
        budget_perf = financial_analysis["budget_performance"]
        performance = budget_perf["performance"]
        
        # Health emoji
        health_emoji = {
            "excellent": "🟢",
            "good": "🟡",
            "warning": "🟠",
            "critical": "🔴"
        }
        
        emoji = health_emoji.get(budget_perf["budget_health"], "⚪")
        
        response = f"""{emoji} **Performa Budget Bulan Ini**

**Income**: {self.format_currency(budget_perf['monthly_income'])}
**Budget Health**: {budget_perf['budget_health'].replace('_', ' ').title()}
**Total Spent**: {self.format_currency(budget_perf['total_spent'])} ({budget_perf['overall_percentage']:.1f}%)

**Detail per Kategori:**

"""
        
        # Add each budget category
        for budget_type, info in performance.items():
            status_emoji = "🟢" if info["status"] == "under" else "🔴"
            response += f"{status_emoji} **{budget_type.upper()}** ({budget_type == 'needs' and '50%' or budget_type == 'wants' and '30%' or '20%'}):\n"
            response += f"   Used: {self.format_currency(info['spent'])} ({info['percentage_used']:.1f}%)\n"
            response += f"   Budget: {self.format_currency(info['budget'])}\n"
            response += f"   Remaining: {self.format_currency(info['remaining'])}\n\n"
        
        # Add contextual advice
        if budget_perf["budget_health"] == "critical":
            response += "🚨 **Urgent Action Needed!** Kurangi pengeluaran segera"
        elif budget_perf["budget_health"] == "warning":
            response += "⚠️ **Perlu Perhatian** - Monitor spending lebih ketat"
        elif budget_perf["budget_health"] == "good":
            response += "👍 **On Track** - Pertahankan discipline ini"
        else:
            response += "🎉 **Excellent** - Budget management sangat baik!"
        
        return response
    
    async def _handle_spending_analysis_query(self, financial_analysis: Dict[str, Any]) -> str:
        """Handle query analisis pengeluaran"""
        spending_patterns = financial_analysis["spending_patterns"]
        top_categories = spending_patterns["top_categories"]
        
        response = f"""📈 **Analisis Pengeluaran (30 Hari Terakhir)**

**Summary:**
• Total Pengeluaran: {self.format_currency(spending_patterns['total_spent'])}
• Rata-rata Harian: {self.format_currency(spending_patterns['average_daily'])}
• Jumlah Transaksi: {spending_patterns['transaction_count']}

**Top 5 Kategori Pengeluaran:**

"""
        
        # Add top categories
        for i, cat in enumerate(top_categories[:5], 1):
            percentage = (cat['total'] / spending_patterns['total_spent'] * 100) if spending_patterns['total_spent'] > 0 else 0
            response += f"{i}. **{cat['_id']}**: {self.format_currency(cat['total'])} ({percentage:.1f}%)\n"
            response += f"   {cat['count']} transaksi\n\n"
        
        # Add insights
        if top_categories:
            top_category = top_categories[0]
            response += f"💡 **Insight:** Pengeluaran terbesar Anda adalah {top_category['_id']}\n"
            
            # Category-specific tips
            category_tips = {
                "Makanan Pokok": "Tip: Masak sendiri bisa menghemat 40-60%",
                "Jajan & Snack": "Tip: Batasi jajan ke 10% dari budget WANTS",
                "Transportasi Wajib": "Tip: Gunakan transportasi umum untuk hemat",
                "Hiburan & Sosial": "Tip: Cari hiburan gratis atau promo mahasiswa"
            }
            
            tip = category_tips.get(top_category['_id'], "Evaluasi apakah pengeluaran ini bisa dikurangi")
            response += f"💰 {tip}"
        
        return response
    
    async def _handle_progress_tabungan_query(self, financial_analysis: Dict[str, Any]) -> str:
        """Handle query progress tabungan"""
        savings_analysis = financial_analysis["savings_analysis"]
        
        if not savings_analysis["has_goals"]:
            return """🎯 **Progress Tabungan**

Belum ada target tabungan aktif. Yuk buat target pertama!

**Contoh membuat target:**
• "Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026"
• "Target beli motor 25 juta dalam 1 tahun"
• "Pengen beli hp 5 juta"

💡 Target tabungan akan membantu Anda lebih fokus dan disiplin dalam menabung!"""
        
        response = f"""📈 **Progress Tabungan Anda**

**Summary:**
• Total Target: {savings_analysis['total_goals']} target
• Aktif: {savings_analysis['active_goals']} | Selesai: {savings_analysis['completed_goals']}
• Total Target Amount: {self.format_currency(savings_analysis['total_target'])}
• Total Terkumpul: {self.format_currency(savings_analysis['total_current'])}
• **Average Progress**: {savings_analysis['average_progress']:.1f}%

**Target Aktif:**

"""
        
        # Add active goals
        for goal in savings_analysis["goals_summary"]:
            if goal["status"] == "active":
                progress_bar = "🟩" * int(goal["progress"] // 10) + "⬜" * (10 - int(goal["progress"] // 10))
                response += f"🛍️ **{goal['item_name']}**:\n"
                response += f"   {progress_bar} {goal['progress']:.1f}%\n"
                response += f"   💰 {self.format_currency(goal['current_amount'])} / {self.format_currency(goal['target_amount'])}\n\n"
        
        # Add urgent goals warning
        urgent_goals = savings_analysis["urgent_goals"]
        if urgent_goals:
            response += f"⏰ **Urgent:** {len(urgent_goals)} target akan deadline dalam 30 hari!\n"
            for goal in urgent_goals:
                response += f"• {goal['item_name']} ({goal['days_remaining']} hari lagi)\n"
            response += "\n"
        
        response += "Terus semangat! Setiap rupiah yang ditabung adalah langkah menuju impian Anda! ✨"
        
        return response
    
    async def _handle_target_bulanan_query(self, financial_analysis: Dict[str, Any]) -> str:
        """Handle query target bulanan"""
        # Get monthly savings progress
        from .finance_service import FinanceService
        finance_service = FinanceService()
        
        monthly_progress = await finance_service._calculate_monthly_savings_progress(financial_analysis["user_id"])
        percentage = monthly_progress["progress_percentage"]
        
        response = f"""🎯 **Target Tabungan Bulan Ini**

**Target**: {self.format_currency(monthly_progress['monthly_target'])}
**Sudah Tercapai**: {self.format_currency(monthly_progress['net_savings_this_month'])} ({percentage:.1f}%)

**Breakdown:**
• Pemasukan Bulan Ini: {self.format_currency(monthly_progress['monthly_income'])}
• Pengeluaran Bulan Ini: {self.format_currency(monthly_progress['monthly_expense'])}
• **Net Savings**: {self.format_currency(monthly_progress['net_savings_this_month'])}

"""
        
        # Status message based on progress
        if percentage >= 100:
            response += "🎉 **Selamat!** Target bulan ini sudah tercapai! Luar biasa!\n\n"
            response += "💡 **Saran:** Pertimbangkan untuk menaikkan target bulan depan atau invest surplus ini"
        elif percentage >= 75:
            response += "👍 **Hampir sampai target!** Sedikit lagi, tetap semangat!\n\n"
            response += "💪 **Saran:** Kurangi sedikit pengeluaran WANTS untuk mencapai target"
        elif percentage >= 50:
            response += "📊 **Separuh jalan sudah ditempuh!** Keep going!\n\n"
            response += "🎯 **Saran:** Evaluasi pengeluaran dan fokus pada target tabungan"
        else:
            response += "🚀 **Masih ada waktu!** Yuk lebih giat menabung!\n\n"
            response += "💡 **Saran:** Review kembali pengeluaran dan prioritaskan saving"
        
        return response
    
    async def _handle_pengeluaran_terbesar_query(self, financial_analysis: Dict[str, Any]) -> str:
        """Handle query pengeluaran terbesar"""
        spending_patterns = financial_analysis["spending_patterns"]
        top_categories = spending_patterns["top_categories"]
        
        if not top_categories:
            return "🤔 **Belum ada data pengeluaran** bulan ini. Yuk mulai catat pengeluaran harian Anda!"
        
        top_category = top_categories[0]
        category_name = top_category["_id"]
        amount = top_category["total"]
        count = top_category["count"]
        
        response = f"""💸 **Kategori Pengeluaran Terbesar**

**{category_name}**: {self.format_currency(amount)}
**Jumlah Transaksi**: {count}x transaksi
**Rata-rata per Transaksi**: {self.format_currency(amount / count)}

"""
        
        # Add percentage of total spending
        total_spent = spending_patterns["total_spent"]
        if total_spent > 0:
            percentage = (amount / total_spent) * 100
            response += f"**Persentase**: {percentage:.1f}% dari total pengeluaran\n\n"
        
        # Category-specific tips
        category_tips = {
            "Makanan Pokok": "🍚 Tip: Masak sendiri bisa menghemat 40-60% budget makan bulanan",
            "Jajan & Snack": "🍕 Tip: Batasi jajan ke maksimal 10% dari budget WANTS",
            "Transportasi Wajib": "🚌 Tip: Gunakan transportasi umum untuk menghemat budget NEEDS",
            "Hiburan & Sosial": "🎬 Tip: Cari hiburan gratis atau promo mahasiswa untuk menghemat",
            "Kos/Tempat Tinggal": "🏠 Tip: Pertimbangkan sharing cost atau cari tempat yang lebih ekonomis",
            "Pakaian & Aksesoris": "👕 Tip: Beli pakaian saat sale atau di thrift shop untuk hemat"
        }
        
        tip = category_tips.get(category_name, "💡 Evaluasi apakah pengeluaran ini bisa dikurangi atau dioptimalkan")
        response += tip
        
        return response
    
    async def _handle_ringkasan_query(self, financial_analysis: Dict[str, Any]) -> str:
        """Handle query ringkasan keuangan"""
        current_totals = financial_analysis["current_totals"]
        budget_perf = financial_analysis["budget_performance"]
        savings_analysis = financial_analysis["savings_analysis"]
        health_score = financial_analysis["health_score"]
        
        response = f"""📊 **Ringkasan Keuangan Anda**

**💰 Total Tabungan**: {self.format_currency(current_totals['real_total_savings'])}
**📈 Net Growth**: {self.format_currency(current_totals['savings_growth'])}
**💊 Health Score**: {health_score['score']}/{health_score['max_score']} ({health_score['level'].replace('_', ' ').title()})

**📊 Budget Performance:**
• Monthly Income: {self.format_currency(budget_perf['monthly_income'])}
• Total Spent: {self.format_currency(budget_perf['total_spent'])} ({budget_perf['overall_percentage']:.1f}%)
• Budget Health: {budget_perf['budget_health'].replace('_', ' ').title()}

**🎯 Savings Goals:**
• Total Targets: {savings_analysis['total_goals']}
• Active: {savings_analysis['active_goals']} | Completed: {savings_analysis['completed_goals']}
• Average Progress: {savings_analysis['average_progress']:.1f}%

**📈 Activity:**
• Income Transactions: {current_totals['transaction_count']['income']}
• Expense Transactions: {current_totals['transaction_count']['expense']}

"""
        
        # Add quick insights
        insights = []
        
        if current_totals['savings_growth'] > 0:
            insights.append("✅ Tabungan bertumbuh positif")
        elif current_totals['savings_growth'] < 0:
            insights.append("⚠️ Tabungan menurun, perlu evaluasi")
        
        if budget_perf['budget_health'] == 'excellent':
            insights.append("✅ Budget management sangat baik")
        elif budget_perf['budget_health'] == 'critical':
            insights.append("🚨 Budget over limit, perlu action")
        
        if savings_analysis['urgent_goals']:
            insights.append(f"⏰ {len(savings_analysis['urgent_goals'])} target urgent")
        
        if health_score['level'] == 'excellent':
            insights.append("🏆 Financial health excellent")
        elif health_score['level'] == 'needs_improvement':
            insights.append("💪 Perlu improve financial discipline")
        
        if insights:
            response += "**💡 Quick Insights:**\n"
            for insight in insights:
                response += f"• {insight}\n"
        
        return response
    
    # ==========================================
    # UTILITY METHOD FROM HANDLERS
    # ==========================================
    
    async def handle_list_savings_goals(self, user_id: str) -> str:
        """Handle request untuk list semua savings goals - import from handlers"""
        from .luna_ai_handlers import LunaAIHandlers
        handlers = LunaAIHandlers()
        return await handlers.handle_list_savings_goals(user_id)