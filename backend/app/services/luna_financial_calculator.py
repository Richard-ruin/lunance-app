# app/services/luna_financial_calculator.py - NEW file untuk mengatasi masalah calculation Luna AI
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId
import traceback

from ..config.database import get_database
from ..models.finance import TransactionType, TransactionStatus, SavingsGoalStatus
from ..models.user import User
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db


class LunaFinancialCalculator:
    """
    NEW Calculator khusus untuk Luna AI yang menghitung data keuangan real-time
    TANPA mengubah finance_service yang sudah ada
    
    Focus pada:
    1. Real-time total savings calculation
    2. Real monthly income dari transaksi aktual
    3. Current month budget performance 
    4. Savings goals progress
    5. Financial health assessment
    """
    
    def __init__(self):
        self.db = get_database()
    
    def format_currency(self, amount: float) -> str:
        """Format currency to Rupiah"""
        try:
            return f"Rp {amount:,.0f}".replace(',', '.')
        except:
            return f"Rp {amount}"
    
    # ==========================================
    # CORE CALCULATION METHODS - FIXED
    # ==========================================
    
    async def calculate_real_total_savings(self, user_id: str) -> Dict[str, Any]:
        """
        FIXED: Calculate REAL total savings = initial_savings + total_income - total_expense
        Menggunakan transaksi CONFIRMED saja
        """
        try:
            # Get user initial savings (setup value)
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            initial_savings = 0.0
            if user_doc and user_doc.get("financial_settings"):
                initial_savings = user_doc["financial_settings"].get("current_savings", 0.0)
            
            print(f"💰 Initial savings from setup: {self.format_currency(initial_savings)}")
            
            # Get all CONFIRMED transactions summary
            pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "status": TransactionStatus.CONFIRMED.value
                }},
                {"$group": {
                    "_id": "$type",
                    "total": {"$sum": "$amount"}
                }}
            ]
            
            transaction_summary = list(self.db.transactions.aggregate(pipeline))
            total_income = 0.0
            total_expense = 0.0
            
            for item in transaction_summary:
                if item["_id"] == TransactionType.INCOME.value:
                    total_income = item["total"]
                elif item["_id"] == TransactionType.EXPENSE.value:
                    total_expense = item["total"]
            
            # REAL total savings calculation
            real_total_savings = initial_savings + total_income - total_expense
            net_growth = total_income - total_expense
            
            print(f"📊 Real Savings Calculation:")
            print(f"  Initial: {self.format_currency(initial_savings)}")
            print(f"  Income: {self.format_currency(total_income)}")
            print(f"  Expense: {self.format_currency(total_expense)}")
            print(f"  Net Growth: {self.format_currency(net_growth)}")
            print(f"  REAL Total: {self.format_currency(real_total_savings)}")
            
            return {
                "initial_savings": initial_savings,
                "total_income": total_income,
                "total_expense": total_expense,
                "net_growth": net_growth,
                "real_total_savings": max(real_total_savings, 0.0),  # Cannot be negative
                "formatted_initial": self.format_currency(initial_savings),
                "formatted_income": self.format_currency(total_income),
                "formatted_expense": self.format_currency(total_expense),
                "formatted_net_growth": self.format_currency(net_growth),
                "formatted_real_total": self.format_currency(max(real_total_savings, 0.0))
            }
            
        except Exception as e:
            print(f"❌ Error calculating real total savings: {e}")
            traceback.print_exc()
            return {
                "initial_savings": 0.0, "total_income": 0.0, "total_expense": 0.0,
                "net_growth": 0.0, "real_total_savings": 0.0,
                "formatted_initial": self.format_currency(0),
                "formatted_income": self.format_currency(0),
                "formatted_expense": self.format_currency(0),
                "formatted_net_growth": self.format_currency(0),
                "formatted_real_total": self.format_currency(0)
            }
    
    async def calculate_real_monthly_income(self, user_id: str) -> Dict[str, Any]:
        """
        FIXED: Calculate REAL monthly income dari transaksi 30 hari terakhir
        BUKAN dari setup monthly_income
        """
        try:
            # Get last 30 days
            thirty_days_ago = now_for_db() - timedelta(days=30)
            
            # Get confirmed income transactions in last 30 days
            pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "type": TransactionType.INCOME.value,
                    "status": TransactionStatus.CONFIRMED.value,
                    "date": {"$gte": thirty_days_ago}
                }},
                {"$group": {
                    "_id": None,
                    "total_income": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }}
            ]
            
            result = list(self.db.transactions.aggregate(pipeline))
            total_income_30_days = result[0]["total_income"] if result else 0.0
            transaction_count = result[0]["count"] if result else 0
            
            # Monthly income = total in last 30 days (approximate 1 month)
            real_monthly_income = total_income_30_days
            
            # Get setup monthly income for comparison
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            setup_monthly_income = 0.0
            if user_doc and user_doc.get("financial_settings"):
                setup_monthly_income = user_doc["financial_settings"].get("monthly_income", 0.0)
            
            print(f"📈 Monthly Income Calculation:")
            print(f"  Real (30 days): {self.format_currency(real_monthly_income)}")
            print(f"  Setup (config): {self.format_currency(setup_monthly_income)}")
            print(f"  Transaction count: {transaction_count}")
            
            return {
                "real_monthly_income": real_monthly_income,
                "setup_monthly_income": setup_monthly_income,
                "period_days": 30,
                "transaction_count": transaction_count,
                "formatted_real": self.format_currency(real_monthly_income),
                "formatted_setup": self.format_currency(setup_monthly_income),
                "income_source": "real_transactions" if real_monthly_income > 0 else "setup_config",
                "active_income_tracking": real_monthly_income > 0
            }
            
        except Exception as e:
            print(f"❌ Error calculating real monthly income: {e}")
            return {
                "real_monthly_income": 0.0, "setup_monthly_income": 0.0,
                "period_days": 30, "transaction_count": 0,
                "formatted_real": self.format_currency(0),
                "formatted_setup": self.format_currency(0),
                "income_source": "none", "active_income_tracking": False
            }
    
    async def calculate_current_month_budget_performance(self, user_id: str) -> Dict[str, Any]:
        """
        FIXED: Calculate budget performance bulan ini dengan 50/30/20 method
        """
        try:
            # Get start of current month in Indonesian timezone
            now = IndonesiaDatetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_of_month_utc = IndonesiaDatetime.to_utc(start_of_month).replace(tzinfo=None)
            
            # Get real monthly income
            income_data = await self.calculate_real_monthly_income(user_id)
            real_monthly_income = income_data["real_monthly_income"]
            setup_monthly_income = income_data["setup_monthly_income"]
            
            # Use real income if available, fallback to setup
            base_income = real_monthly_income if real_monthly_income > 0 else setup_monthly_income
            
            if base_income <= 0:
                return {
                    "has_budget": False,
                    "message": "Belum ada data income untuk menghitung budget 50/30/20",
                    "base_income": 0,
                    "income_source": "none"
                }
            
            # Calculate 50/30/20 allocations
            needs_budget = base_income * 0.50
            wants_budget = base_income * 0.30
            savings_budget = base_income * 0.20
            
            # Get current month spending by budget type
            spending_by_type = await self._get_current_month_spending_by_budget_type(user_id, start_of_month_utc)
            
            # Calculate performance for each category
            performance = {
                "needs": self._calculate_category_performance("needs", needs_budget, spending_by_type.get("needs", 0)),
                "wants": self._calculate_category_performance("wants", wants_budget, spending_by_type.get("wants", 0)),
                "savings": self._calculate_category_performance("savings", savings_budget, spending_by_type.get("savings", 0))
            }
            
            # Overall assessment
            total_spent = sum(spending_by_type.values())
            overall_percentage = (total_spent / base_income * 100) if base_income > 0 else 0
            
            budget_health = self._assess_budget_health(overall_percentage, performance)
            
            print(f"💳 Budget Performance (Base Income: {self.format_currency(base_income)}):")
            print(f"  NEEDS: {performance['needs']['percentage_used']:.1f}%")
            print(f"  WANTS: {performance['wants']['percentage_used']:.1f}%") 
            print(f"  SAVINGS: {performance['savings']['percentage_used']:.1f}%")
            print(f"  Overall Health: {budget_health}")
            
            return {
                "has_budget": True,
                "method": "50/30/20 Elizabeth Warren",
                "period": now.strftime("%B %Y"),
                "base_income": base_income,
                "income_source": income_data["income_source"],
                "budget_allocation": {
                    "needs_budget": needs_budget,
                    "wants_budget": wants_budget,
                    "savings_budget": savings_budget
                },
                "current_spending": spending_by_type,
                "performance": performance,
                "overall": {
                    "total_spent": total_spent,
                    "total_remaining": max(base_income - total_spent, 0),
                    "percentage_used": overall_percentage,
                    "budget_health": budget_health
                },
                "formatted": {
                    "base_income": self.format_currency(base_income),
                    "needs_budget": self.format_currency(needs_budget),
                    "wants_budget": self.format_currency(wants_budget),
                    "savings_budget": self.format_currency(savings_budget),
                    "total_spent": self.format_currency(total_spent),
                    "total_remaining": self.format_currency(max(base_income - total_spent, 0))
                }
            }
            
        except Exception as e:
            print(f"❌ Error calculating budget performance: {e}")
            traceback.print_exc()
            return {
                "has_budget": False,
                "error": str(e),
                "base_income": 0,
                "income_source": "error"
            }
    
    async def calculate_savings_goals_progress(self, user_id: str) -> Dict[str, Any]:
        """
        FIXED: Calculate savings goals progress dengan detail yang akurat
        """
        try:
            # Get all savings goals
            goals_cursor = self.db.savings_goals.find({
                "user_id": user_id,
                "status": {"$in": ["active", "paused", "completed"]}
            }).sort("created_at", -1)
            
            goals = list(goals_cursor)
            
            if not goals:
                return {
                    "has_goals": False,
                    "total_goals": 0,
                    "active_goals": 0,
                    "completed_goals": 0,
                    "message": "Belum ada target tabungan"
                }
            
            # Analyze goals
            active_goals = [g for g in goals if g["status"] == "active"]
            completed_goals = [g for g in goals if g["status"] == "completed"]
            paused_goals = [g for g in goals if g["status"] == "paused"]
            
            # Calculate totals
            total_target = sum(g["target_amount"] for g in goals)
            total_current = sum(g["current_amount"] for g in goals)
            average_progress = (total_current / total_target * 100) if total_target > 0 else 0
            
            # Find urgent goals (deadline < 30 days)
            urgent_goals = []
            for goal in active_goals:
                if goal.get("target_date"):
                    try:
                        target_date = goal["target_date"]
                        if isinstance(target_date, str):
                            target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                        
                        days_remaining = (target_date - datetime.now()).days
                        if 0 < days_remaining <= 30:
                            progress = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
                            urgent_goals.append({
                                "id": str(goal["_id"]),
                                "item_name": goal["item_name"],
                                "target_amount": goal["target_amount"],
                                "current_amount": goal["current_amount"],
                                "progress": progress,
                                "days_remaining": days_remaining,
                                "formatted_target": self.format_currency(goal["target_amount"]),
                                "formatted_current": self.format_currency(goal["current_amount"])
                            })
                    except Exception as e:
                        print(f"Error processing goal date: {e}")
                        continue
            
            # Format goals summary
            goals_summary = []
            for goal in goals[:5]:  # Top 5 recent goals
                progress = (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
                goals_summary.append({
                    "id": str(goal["_id"]),
                    "item_name": goal["item_name"],
                    "target_amount": goal["target_amount"],
                    "current_amount": goal["current_amount"],
                    "progress": progress,
                    "status": goal["status"],
                    "formatted_target": self.format_currency(goal["target_amount"]),
                    "formatted_current": self.format_currency(goal["current_amount"])
                })
            
            print(f"🎯 Savings Goals Analysis:")
            print(f"  Total Goals: {len(goals)} (Active: {len(active_goals)}, Completed: {len(completed_goals)})")
            print(f"  Average Progress: {average_progress:.1f}%")
            print(f"  Urgent Goals: {len(urgent_goals)}")
            
            return {
                "has_goals": True,
                "total_goals": len(goals),
                "active_goals": len(active_goals),
                "completed_goals": len(completed_goals),
                "paused_goals": len(paused_goals),
                "total_target": total_target,
                "total_current": total_current,
                "average_progress": average_progress,
                "urgent_goals": urgent_goals,
                "goals_summary": goals_summary,
                "formatted": {
                    "total_target": self.format_currency(total_target),
                    "total_current": self.format_currency(total_current),
                    "remaining_total": self.format_currency(max(total_target - total_current, 0))
                }
            }
            
        except Exception as e:
            print(f"❌ Error calculating savings goals progress: {e}")
            return {
                "has_goals": False,
                "total_goals": 0,
                "active_goals": 0,
                "completed_goals": 0,
                "error": str(e)
            }
    
    async def calculate_financial_health_score(self, user_id: str) -> Dict[str, Any]:
        """
        FIXED: Calculate comprehensive financial health score
        """
        try:
            # Get all financial data
            savings_data = await self.calculate_real_total_savings(user_id)
            income_data = await self.calculate_real_monthly_income(user_id)
            budget_data = await self.calculate_current_month_budget_performance(user_id)
            goals_data = await self.calculate_savings_goals_progress(user_id)
            
            score = 0
            max_score = 100
            
            # 1. Savings Growth Score (25 points)
            net_growth = savings_data["net_growth"]
            base_income = income_data["real_monthly_income"] or income_data["setup_monthly_income"]
            
            if base_income > 0:
                savings_rate = (net_growth / base_income * 100) if base_income > 0 else 0
                if savings_rate >= 20:
                    score += 25
                elif savings_rate >= 15:
                    score += 20
                elif savings_rate >= 10:
                    score += 15
                elif savings_rate >= 5:
                    score += 10
                elif savings_rate >= 0:
                    score += 5
            
            # 2. Budget Discipline Score (30 points)
            if budget_data.get("has_budget"):
                budget_health = budget_data["overall"]["budget_health"]
                if budget_health == "excellent":
                    score += 30
                elif budget_health == "good":
                    score += 25
                elif budget_health == "warning":
                    score += 15
                elif budget_health == "critical":
                    score += 5
            
            # 3. Savings Goals Progress (25 points)
            if goals_data.get("has_goals"):
                avg_progress = goals_data["average_progress"]
                if avg_progress >= 80:
                    score += 25
                elif avg_progress >= 60:
                    score += 20
                elif avg_progress >= 40:
                    score += 15
                elif avg_progress >= 20:
                    score += 10
                else:
                    score += 5
            else:
                # Bonus for starting savings goals
                score += 5
            
            # 4. Financial Activity Score (20 points)
            total_transactions = savings_data["total_income"] + savings_data["total_expense"]
            if total_transactions > 0:
                if income_data["transaction_count"] >= 10:
                    score += 20
                elif income_data["transaction_count"] >= 5:
                    score += 15
                elif income_data["transaction_count"] >= 3:
                    score += 10
                else:
                    score += 5
            
            # Determine health level
            percentage = (score / max_score) * 100
            if percentage >= 80:
                level = "excellent"
                level_emoji = "🏆"
                level_message = "Financial management Anda luar biasa!"
            elif percentage >= 60:
                level = "good"
                level_emoji = "👍"
                level_message = "Budget management sudah baik, pertahankan!"
            elif percentage >= 40:
                level = "fair"
                level_emoji = "📊"
                level_message = "Ada progress bagus, masih bisa ditingkatkan"
            else:
                level = "needs_improvement"
                level_emoji = "🆘"
                level_message = "Focus pada budgeting 50/30/20 yang konsisten"
            
            print(f"💪 Financial Health Score: {score}/{max_score} ({percentage:.1f}%) - {level}")
            
            return {
                "score": score,
                "max_score": max_score,
                "percentage": percentage,
                "level": level,
                "level_emoji": level_emoji,
                "level_message": level_message,
                "components": {
                    "savings_growth": net_growth,
                    "savings_rate": (net_growth / base_income * 100) if base_income > 0 else 0,
                    "budget_health": budget_data.get("overall", {}).get("budget_health", "unknown"),
                    "goals_progress": goals_data.get("average_progress", 0),
                    "transaction_activity": income_data["transaction_count"]
                },
                "recommendations": self._generate_health_recommendations(level, savings_data, budget_data, goals_data)
            }
            
        except Exception as e:
            print(f"❌ Error calculating financial health score: {e}")
            return {
                "score": 0, "max_score": 100, "percentage": 0,
                "level": "unknown", "level_emoji": "❓",
                "level_message": "Tidak dapat menghitung health score",
                "components": {}, "recommendations": [],
                "error": str(e)
            }
    
    # ==========================================
    # QUERY RESPONSE METHODS - ENHANCED
    # ==========================================
    
    async def get_total_savings_response(self, user_id: str) -> str:
        """
        FIXED: Generate response untuk query "total tabungan saya"
        """
        try:
            savings_data = await self.calculate_real_total_savings(user_id)
            income_data = await self.calculate_real_monthly_income(user_id)
            
            real_total = savings_data["real_total_savings"]
            net_growth = savings_data["net_growth"]
            
            response = f"""💰 **Total Tabungan Anda: {savings_data['formatted_real_total']}**

📊 **Breakdown Keuangan Real-Time:**
• **Tabungan Awal**: {savings_data['formatted_initial']} (dari setup)
• **Total Pemasukan**: {savings_data['formatted_income']} (dari transaksi)
• **Total Pengeluaran**: {savings_data['formatted_expense']} (dari transaksi)
• **Net Growth**: {savings_data['formatted_net_growth']}

"""
            
            # Add growth analysis
            if net_growth > 0:
                response += f"✅ **Excellent!** Tabungan Anda bertumbuh {savings_data['formatted_net_growth']}! 🎉\n\n"
                
                # Calculate savings rate if have income
                if income_data["real_monthly_income"] > 0:
                    savings_rate = (net_growth / income_data["real_monthly_income"] * 100)
                    response += f"📈 **Savings Rate**: {savings_rate:.1f}% dari monthly income\n"
                    
                    if savings_rate >= 20:
                        response += f"🏆 **Amazing!** Anda mencapai target savings 20%+!\n"
                    elif savings_rate >= 10:
                        response += f"👍 **Good!** Hampir mencapai target 20%, tingkatkan sedikit!\n"
                    else:
                        response += f"📊 **Tips**: Target minimal 20% untuk financial growth yang optimal\n"
                
            elif net_growth < 0:
                response += f"⚠️ **Perhatian!** Tabungan berkurang {self.format_currency(abs(net_growth))}.\n\n"
                response += f"🔧 **Action Plan:**\n"
                response += f"• Review pengeluaran kategori WANTS (30%)\n"
                response += f"• Tingkatkan pemasukan jika memungkinkan\n"
                response += f"• Focus strict budgeting 50/30/20\n"
                
            else:
                response += f"📊 **Stabil** - Pemasukan dan pengeluaran seimbang.\n\n"
                response += f"💡 **Saran**: Coba sisihkan lebih untuk savings growth yang positif.\n"
            
            # Add income context
            if income_data["active_income_tracking"]:
                response += f"\n💰 **Income Tracking Aktif**: {income_data['formatted_real']} dalam 30 hari terakhir"
            else:
                response += f"\n📝 **Tips**: Catat lebih banyak transaksi income untuk tracking yang akurat"
            
            response += f"\n\n📱 **Next**: Tanya \"budget performance bulan ini\" untuk analisis 50/30/20!"
            
            return response
            
        except Exception as e:
            print(f"Error generating total savings response: {e}")
            return f"😅 Maaf, terjadi kesalahan saat menghitung total tabungan. Error: {str(e)}\n\nCoba tanya lagi dalam beberapa saat!"
    
    async def get_financial_health_response(self, user_id: str) -> str:
        """
        FIXED: Generate response untuk query "kesehatan keuangan saya"
        """
        try:
            health_data = await self.calculate_financial_health_score(user_id)
            
            response = f"""{health_data['level_emoji']} **Kesehatan Keuangan Anda**

📊 **Financial Health Score**: {health_data['score']}/{health_data['max_score']} ({health_data['percentage']:.1f}%)
🏷️ **Level**: {health_data['level'].replace('_', ' ').title()}

💬 **Assessment**: {health_data['level_message']}

🎯 **Komponen Penilaian:**
• **Savings Rate**: {health_data['components']['savings_rate']:.1f}%
• **Budget Health**: {health_data['components']['budget_health'].replace('_', ' ').title()}
• **Goals Progress**: {health_data['components']['goals_progress']:.1f}%
• **Transaction Activity**: {health_data['components']['transaction_activity']} transaksi income

"""
            
            # Add level-specific advice
            recommendations = health_data["recommendations"]
            if recommendations:
                response += f"💡 **Rekomendasi Personal:**\n"
                for i, rec in enumerate(recommendations[:3], 1):
                    response += f"{i}. {rec}\n"
                response += "\n"
            
            # Add action items based on components
            components = health_data["components"]
            response += f"🎯 **Focus Areas:**\n"
            
            if components["savings_rate"] < 15:
                response += f"📈 **Priority**: Tingkatkan savings rate ke minimal 15-20%\n"
            
            if components["budget_health"] in ["warning", "critical"]:
                response += f"💳 **Priority**: Disiplin budget 50/30/20 yang lebih ketat\n"
            
            if components["goals_progress"] < 50:
                response += f"🎯 **Priority**: Focus pada target tabungan yang sudah dibuat\n"
            
            if components["transaction_activity"] < 5:
                response += f"📝 **Priority**: Tingkatkan tracking transaksi harian\n"
            
            response += f"\n📱 **Track Progress**: Tanya lagi minggu depan untuk lihat improvement!"
            
            return response
            
        except Exception as e:
            print(f"Error generating financial health response: {e}")
            return f"😅 Terjadi kesalahan saat menganalisis kesehatan keuangan. Coba lagi ya!\n\nError: {str(e)}"
    
    async def get_budget_performance_response(self, user_id: str) -> str:
        """
        FIXED: Generate response untuk query "budget performance bulan ini"
        """
        try:
            budget_data = await self.calculate_current_month_budget_performance(user_id)
            
            if not budget_data.get("has_budget"):
                return f"""📊 **Budget Performance Bulan Ini**

{budget_data.get('message', 'Belum ada data budget')}

🚀 **Untuk analisis budget 50/30/20:**
1. Input beberapa transaksi income terlebih dulu
2. Catat pengeluaran harian Anda
3. Minimal 3-5 transaksi untuk analisis yang akurat

💡 **Contoh transaksi:**
• "Dapat uang saku 2 juta dari ortu"
• "Bayar kos 800 ribu"
• "Freelance dapat 500rb"

Setelah ada data, saya bisa kasih analisis budget yang detail! 😊"""
            
            performance = budget_data["performance"]
            overall = budget_data["overall"]
            
            # Health emoji based on budget health
            health_emoji = {
                "excellent": "🟢",
                "good": "🟡", 
                "warning": "🟠",
                "critical": "🔴"
            }.get(overall["budget_health"], "⚪")
            
            response = f"""{health_emoji} **Budget Performance Bulan Ini**

💰 **Base Income**: {budget_data['formatted']['base_income']} ({budget_data['income_source'].replace('_', ' ')})
📊 **Method**: 50/30/20 Elizabeth Warren
🗓️ **Period**: {budget_data['period']}

📈 **Breakdown Budget:**

"""
            
            # Add each budget category dengan visual progress
            for budget_type in ["needs", "wants", "savings"]:
                if budget_type in performance:
                    info = performance[budget_type]
                    percentage_used = info["percentage_used"]
                    
                    # Create visual progress bar
                    filled_bars = min(10, int(percentage_used // 10))
                    progress_bar = "🟩" * filled_bars + "⬜" * (10 - filled_bars)
                    
                    status_emoji = "🟢" if info["status"] == "under" else "🔴"
                    budget_name = budget_type.upper()
                    target_percentage = {"needs": "50%", "wants": "30%", "savings": "20%"}[budget_type]
                    
                    response += f"{status_emoji} **{budget_name}** ({target_percentage}):\n"
                    response += f"   {progress_bar} {percentage_used:.1f}%\n"
                    response += f"   💸 Spent: {info['formatted_spent']}\n"
                    response += f"   💰 Budget: {info['formatted_budget']}\n"
                    response += f"   ⚖️ Remaining: {info['formatted_remaining']}\n\n"
            
            # Overall assessment
            budget_health = overall["budget_health"]
            response += f"💡 **Overall Assessment: {budget_health.replace('_', ' ').title()}**\n\n"
            
            # Health-specific advice
            if budget_health == "critical":
                response += f"🚨 **URGENT ACTION NEEDED!**\n"
                response += f"• STOP semua pengeluaran WANTS yang tidak esensial\n"
                response += f"• Review dan potong pengeluaran NEEDS jika memungkinkan\n"
                response += f"• Cari cara untuk tingkatkan income\n"
                
            elif budget_health == "warning":
                response += f"⚠️ **Perlu Perhatian Khusus**\n"
                response += f"• Monitor spending lebih ketat untuk sisa bulan\n"
                response += f"• Batasi pengeluaran WANTS ke hal penting saja\n"
                response += f"• Evaluasi NEEDS spending untuk optimasi\n"
                
            elif budget_health == "good":
                response += f"👍 **On Track - Keep Going!**\n"
                response += f"• Pertahankan discipline yang sudah baik\n"
                response += f"• Sisakan ruang untuk emergency\n"
                response += f"• Pertimbangkan surplus untuk investasi\n"
                
            else:  # excellent
                response += f"🎉 **Excellent Budget Management!**\n"
                response += f"• Anda adalah role model budgeting 50/30/20!\n"
                response += f"• Surplus bisa untuk investasi atau target besar\n"
                response += f"• Consider untuk lebih aggressive di savings\n"
            
            response += f"\n📱 **Deep Dive**: Tanya \"analisis pengeluaran saya\" untuk detail breakdown!"
            
            return response
            
        except Exception as e:
            print(f"Error generating budget performance response: {e}")
            return f"😅 Terjadi kesalahan saat menganalisis budget performance.\n\nError: {str(e)}\n\nCoba tanya lagi!"
    
    async def get_savings_goals_progress_response(self, user_id: str) -> str:
        """
        FIXED: Generate response untuk query "progress tabungan" / "target saya"
        """
        try:
            goals_data = await self.calculate_savings_goals_progress(user_id)
            
            if not goals_data.get("has_goals"):
                return """🎯 **Progress Tabungan**

Belum ada target tabungan aktif. Yuk buat target pertama untuk motivasi yang lebih baik! 🚀

💡 **Ide Target Tabungan:**
• **Tech**: "Mau nabung buat beli laptop 10 juta pada tanggal 22 januari 2026"
• **Transport**: "Target beli motor 25 juta dalam 1 tahun"
• **Gadget**: "Pengen beli smartphone 5 juta"

🎯 **Kenapa perlu target tabungan?**
• Memberikan motivasi dan fokus yang jelas
• Membantu disiplin budget WANTS (30%)
• Training untuk financial planning jangka panjang

**Coba buat target sekarang!** Contoh: *"Mau nabung buat beli headset 500 ribu"*"""
            
            response = f"""📈 **Progress Target Tabungan Anda**

🎯 **Summary:**
• **Total Target**: {goals_data['total_goals']} target
• **Status**: {goals_data['active_goals']} Aktif | {goals_data['completed_goals']} Selesai
• **Total Target Amount**: {goals_data['formatted']['total_target']}
• **Total Terkumpul**: {goals_data['formatted']['total_current']}
• **Overall Progress**: {goals_data['average_progress']:.1f}%

"""
            
            # Overall progress bar
            overall_progress = goals_data['average_progress']
            filled_bars = int(overall_progress // 10)
            progress_bar = "🟩" * filled_bars + "⬜" * (10 - filled_bars)
            response += f"📊 **Overall Progress**: {progress_bar} {overall_progress:.1f}%\n\n"
            
            # Active goals detail
            if goals_data["goals_summary"]:
                response += "🏃‍♂️ **Target Aktif:**\n\n"
                
                for goal in goals_data["goals_summary"]:
                    if goal["status"] == "active":
                        progress = goal["progress"]
                        filled_bars = int(progress // 10)
                        goal_progress_bar = "🟩" * filled_bars + "⬜" * (10 - filled_bars)
                        
                        remaining = goal["target_amount"] - goal["current_amount"]
                        
                        response += f"🛍️ **{goal['item_name']}**:\n"
                        response += f"   {goal_progress_bar} {progress:.1f}%\n"
                        response += f"   💰 {goal['formatted_current']} / {goal['formatted_target']}\n"
                        response += f"   🎯 Sisa: {self.format_currency(remaining)}\n"
                        
                        # Motivational message
                        if progress >= 80:
                            response += f"   🔥 **Hampir sampai!** Sedikit lagi achieve!\n"
                        elif progress >= 50:
                            response += f"   💪 **Great progress!** Sudah separuh jalan!\n"
                        elif progress >= 20:
                            response += f"   📈 **On track!** Keep consistent!\n"
                        else:
                            response += f"   🚀 **Let's go!** Mulai sprint mode!\n"
                        
                        response += "\n"
            
            # Urgent goals warning
            urgent_goals = goals_data["urgent_goals"]
            if urgent_goals:
                response += f"⏰ **URGENT: {len(urgent_goals)} target deadline < 30 hari!**\n\n"
                
                for goal in urgent_goals:
                    remaining_amount = goal['target_amount'] - goal['current_amount']
                    daily_needed = remaining_amount / goal['days_remaining'] if goal['days_remaining'] > 0 else 0
                    
                    response += f"🔥 **{goal['item_name']}** ({goal['days_remaining']} hari lagi):\n"
                    response += f"   💰 Sisa: {goal['formatted_target']}\n"
                    response += f"   📅 Perlu: {self.format_currency(daily_needed)}/hari\n\n"
            
            # Strategic advice
            response += f"💡 **Strategy Acceleration:**\n"
            
            if overall_progress < 30:
                response += f"🚀 **Quick Wins:**\n"
                response += f"• Alokasikan 50% budget WANTS untuk tabungan target\n"
                response += f"• Set daily saving challenge\n"
                response += f"• Review subscription yang tidak perlu\n"
            elif overall_progress < 60:
                response += f"📈 **Momentum Building:**\n"
                response += f"• Maintain consistency yang bagus!\n"
                response += f"• Consider increase allocation\n"
                response += f"• Track daily progress\n"
            else:
                response += f"🏆 **Excellence Mode:**\n"
                response += f"• Amazing progress! Role model!\n"
                response += f"• Plan next challenging target\n"
                response += f"• Share strategy ke teman\n"
            
            response += f"\n📱 **Keep tracking!** Tanya progress seminggu sekali untuk motivation! 💪"
            
            return response
            
        except Exception as e:
            print(f"Error generating savings goals response: {e}")
            return f"😅 Terjadi kesalahan saat menganalisis progress tabungan.\n\nError: {str(e)}\n\nCoba tanya lagi!"
    
    # ==========================================
    # HELPER METHODS
    # ==========================================
    
    async def _get_current_month_spending_by_budget_type(self, user_id: str, start_of_month_utc: datetime) -> Dict[str, float]:
        """Get current month spending categorized by budget type"""
        try:
            # Get all confirmed expense transactions this month
            transactions = self.db.transactions.find({
                "user_id": user_id,
                "status": TransactionStatus.CONFIRMED.value,
                "date": {"$gte": start_of_month_utc},
                "type": TransactionType.EXPENSE.value
            })
            
            spending_by_type = {"needs": 0.0, "wants": 0.0, "savings": 0.0}
            
            for trans in transactions:
                try:
                    category = trans.get("category", "")
                    amount = trans.get("amount", 0.0)
                    
                    # Determine budget type
                    budget_type = self._categorize_expense_to_budget_type(category)
                    
                    if budget_type in spending_by_type:
                        spending_by_type[budget_type] += amount
                        
                except Exception as e:
                    print(f"Error processing transaction: {e}")
                    continue
            
            return spending_by_type
            
        except Exception as e:
            print(f"Error getting spending by budget type: {e}")
            return {"needs": 0.0, "wants": 0.0, "savings": 0.0}
    
    def _categorize_expense_to_budget_type(self, category: str) -> str:
        """Categorize expense category to budget type 50/30/20"""
        try:
            category_lower = category.lower()
            
            # NEEDS (50%) - Kebutuhan pokok
            needs_keywords = [
                'makan', 'makanan', 'kos', 'sewa', 'transport', 'transportasi', 
                'pendidikan', 'buku', 'kuliah', 'kampus', 'listrik', 'air', 
                'internet', 'pulsa', 'kesehatan', 'obat', 'sabun', 'pasta'
            ]
            for keyword in needs_keywords:
                if keyword in category_lower:
                    return "needs"
            
            # SAVINGS (20%) - Tabungan dan investasi
            savings_keywords = [
                'tabungan', 'saving', 'investasi', 'deposito', 'darurat', 
                'masa depan', 'reksadana', 'saham'
            ]
            for keyword in savings_keywords:
                if keyword in category_lower:
                    return "savings"
            
            # WANTS (30%) - Default atau keinginan
            return "wants"
            
        except Exception as e:
            print(f"Error categorizing expense: {e}")
            return "wants"
    
    def _calculate_category_performance(self, category: str, budget: float, spent: float) -> Dict[str, Any]:
        """Calculate performance metrics for a budget category"""
        try:
            remaining = budget - spent
            percentage_used = (spent / budget * 100) if budget > 0 else 0
            
            # Determine status
            if percentage_used > 100:
                status = "over"
            elif percentage_used > 80:
                status = "warning"
            else:
                status = "under"
            
            return {
                "budget": budget,
                "spent": spent,
                "remaining": max(remaining, 0),
                "percentage_used": percentage_used,
                "status": status,
                "formatted_budget": self.format_currency(budget),
                "formatted_spent": self.format_currency(spent),
                "formatted_remaining": self.format_currency(max(remaining, 0))
            }
            
        except Exception as e:
            print(f"Error calculating category performance: {e}")
            return {
                "budget": budget, "spent": 0, "remaining": budget,
                "percentage_used": 0, "status": "unknown",
                "formatted_budget": self.format_currency(budget),
                "formatted_spent": self.format_currency(0),
                "formatted_remaining": self.format_currency(budget)
            }
    
    def _assess_budget_health(self, overall_percentage: float, performance: Dict) -> str:
        """Assess overall budget health"""
        try:
            # Check if any category is over budget
            over_budget_categories = [cat for cat, info in performance.items() if info["status"] == "over"]
            
            if over_budget_categories:
                return "critical"
            elif overall_percentage > 90:
                return "warning"
            elif overall_percentage > 70:
                return "good"
            else:
                return "excellent"
                
        except Exception as e:
            print(f"Error assessing budget health: {e}")
            return "unknown"
    
    def _generate_health_recommendations(self, level: str, savings_data: Dict, budget_data: Dict, goals_data: Dict) -> List[str]:
        """Generate personalized health recommendations"""
        recommendations = []
        
        try:
            if level == "excellent":
                recommendations.extend([
                    "🎉 Pertahankan financial discipline yang luar biasa!",
                    "💎 Pertimbangkan investasi jangka panjang (reksadana/saham)",
                    "🏆 Share tips budgeting ke teman-teman mahasiswa"
                ])
            elif level == "good":
                recommendations.extend([
                    "👍 Konsistensi adalah kunci - pertahankan tracking harian",
                    "📈 Evaluasi budget WANTS untuk increase savings", 
                    "🎯 Buat target tabungan yang lebih challenging"
                ])
            elif level == "fair":
                recommendations.extend([
                    "🔧 Focus pada konsistensi budgeting 50/30/20",
                    "📊 Review pengeluaran WANTS - potong yang tidak perlu",
                    "💪 Tingkatkan tracking transaksi harian"
                ])
            else:  # needs_improvement
                recommendations.extend([
                    "🚀 Mulai strict budgeting 50% NEEDS, 30% WANTS, 20% SAVINGS",
                    "📝 Track SEMUA pengeluaran harian",
                    "🎯 Identifikasi dan potong pengeluaran impulsif"
                ])
            
            # Add specific recommendations based on data
            if savings_data["net_growth"] < 0:
                recommendations.append("⚠️ Priority: Stop negative cash flow - review semua spending")
            
            if budget_data.get("has_budget") and budget_data["overall"]["budget_health"] == "critical":
                recommendations.append("🚨 Emergency: Immediate spending freeze pada WANTS")
            
            if not goals_data.get("has_goals"):
                recommendations.append("🎯 Buat minimal 1 target tabungan untuk motivasi")
            
            return recommendations[:4]  # Max 4 recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return ["💪 Tetap semangat mengelola keuangan dengan metode 50/30/20!"]