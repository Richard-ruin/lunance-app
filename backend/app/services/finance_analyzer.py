# app/services/finance_analyzer.py - FIXED untuk menghitung real savings dari transaksi actual
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from bson import ObjectId
import traceback

from ..config.database import get_database
from ..models.finance import Transaction, SavingsGoal, TransactionType, TransactionStatus
from ..models.user import User, FinancialSettings
from ..utils.timezone_utils import IndonesiaDatetime, now_for_db
from .financial_categories import IndonesianStudentCategories


class FinanceAnalyzer:
    """
    FIXED: Analyzer yang menghitung tabungan real dari TRANSAKSI AKTUAL (bukan monthly income di setup)
    Menganalisis data keuangan user dan memberikan insight untuk chatbot responses
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
    # ENHANCED: REAL FINANCIAL CALCULATION
    # ==========================================
    
    async def analyze_user_financial_status(self, user_id: str) -> Dict[str, Any]:
        """
        FIXED: Analisis lengkap berdasarkan TRANSAKSI AKTUAL, bukan monthly income setup
        """
        try:
            # Get user financial settings (hanya untuk initial_savings dan budget allocation)
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            financial_settings = user_doc.get("financial_settings", {}) if user_doc else {}
            
            # Calculate current totals dari TRANSAKSI AKTUAL (FIXED)
            current_totals = await self._calculate_current_totals(user_id)
            
            # FIXED: Gunakan REAL monthly income dari transaksi, bukan setup
            real_monthly_income = await self._calculate_real_monthly_income(user_id)
            
            if real_monthly_income <= 0:
                return {
                    "status": "no_transactions",
                    "message": "Belum ada transaksi yang dapat dianalisis",
                    "recommendations": ["Mulai catat pemasukan dan pengeluaran harian Anda"],
                    "current_totals": current_totals,
                    "real_monthly_income": 0
                }
            
            # Budget performance berdasarkan REAL income
            budget_performance = await self._analyze_budget_performance(user_id, real_monthly_income)
            savings_analysis = await self._analyze_savings_goals(user_id)
            spending_patterns = await self._analyze_spending_patterns(user_id)
            
            # Overall financial health
            health_score = self._calculate_health_score(
                current_totals, budget_performance, savings_analysis, real_monthly_income
            )
            
            return {
                "status": "analyzed",
                "user_id": user_id,
                "real_monthly_income": real_monthly_income,  # FIXED: Real dari transaksi
                "setup_monthly_income": financial_settings.get("monthly_income", 0),  # Setup value
                "current_totals": current_totals,
                "budget_performance": budget_performance,
                "savings_analysis": savings_analysis,
                "spending_patterns": spending_patterns,
                "health_score": health_score,
                "recommendations": self._generate_recommendations(
                    budget_performance, savings_analysis, spending_patterns, health_score
                ),
                "analysis_timestamp": now_for_db()
            }
            
        except Exception as e:
            print(f"Error analyzing user financial status: {e}")
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Gagal menganalisis data keuangan: {str(e)}"
            }
    
    async def _calculate_current_totals(self, user_id: str) -> Dict[str, Any]:
        """FIXED: Calculate current financial totals dari TRANSAKSI AKTUAL"""
        try:
            # Get user initial savings dari setup
            user_doc = self.db.users.find_one({"_id": ObjectId(user_id)})
            initial_savings = 0.0
            if user_doc and user_doc.get("financial_settings"):
                initial_savings = user_doc["financial_settings"].get("current_savings", 0.0)
            
            # FIXED: Get all confirmed transactions (REAL data)
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
            
            # FIXED: Real total savings = initial + REAL income - REAL expense
            real_total_savings = initial_savings + total_income - total_expense
            net_this_period = total_income - total_expense
            
            print(f"💰 REAL Financial Calculation:")
            print(f"  Initial Savings: {self.format_currency(initial_savings)}")
            print(f"  Total Income (Real): {self.format_currency(total_income)}")
            print(f"  Total Expense (Real): {self.format_currency(total_expense)}")
            print(f"  Real Total Savings: {self.format_currency(real_total_savings)}")
            
            return {
                "initial_savings": initial_savings,
                "total_income": total_income,
                "total_expense": total_expense,
                "net_this_period": net_this_period,
                "real_total_savings": max(real_total_savings, 0.0),
                "savings_growth": net_this_period,
                "transaction_count": {
                    "income": await self._count_transactions(user_id, "income"),
                    "expense": await self._count_transactions(user_id, "expense")
                }
            }
            
        except Exception as e:
            print(f"Error calculating current totals: {e}")
            return {
                "initial_savings": 0.0, "total_income": 0.0, "total_expense": 0.0,
                "net_this_period": 0.0, "real_total_savings": 0.0, "savings_growth": 0.0,
                "transaction_count": {"income": 0, "expense": 0}
            }
    
    async def _calculate_real_monthly_income(self, user_id: str) -> float:
        """FIXED: Calculate REAL monthly income dari transaksi income 30 hari terakhir"""
        try:
            # Get last 30 days
            thirty_days_ago = now_for_db() - timedelta(days=30)
            
            # Get all income transactions in last 30 days
            pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "type": TransactionType.INCOME.value,
                    "status": TransactionStatus.CONFIRMED.value,
                    "date": {"$gte": thirty_days_ago}
                }},
                {"$group": {
                    "_id": None,
                    "total_income": {"$sum": "$amount"}
                }}
            ]
            
            result = list(self.db.transactions.aggregate(pipeline))
            total_income_30_days = result[0]["total_income"] if result else 0.0
            
            # Calculate monthly average (30 days = 1 month approximation)
            real_monthly_income = total_income_30_days
            
            print(f"📊 Real Monthly Income Calculation:")
            print(f"  Last 30 days income: {self.format_currency(total_income_30_days)}")
            print(f"  Estimated monthly: {self.format_currency(real_monthly_income)}")
            
            return real_monthly_income
            
        except Exception as e:
            print(f"Error calculating real monthly income: {e}")
            return 0.0
    
    async def _analyze_budget_performance(self, user_id: str, monthly_income: float) -> Dict[str, Any]:
        """FIXED: Analyze budget performance 50/30/20 dengan REAL monthly income"""
        try:
            # Get start of current month
            now = IndonesiaDatetime.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_of_month_utc = IndonesiaDatetime.to_utc(start_of_month).replace(tzinfo=None)
            
            # Get current month spending by budget type dari TRANSAKSI AKTUAL
            spending_by_type = await self._get_spending_by_budget_type(user_id, start_of_month_utc)
            
            # FIXED: Calculate budget allocations dari REAL monthly income
            needs_budget = monthly_income * 0.50
            wants_budget = monthly_income * 0.30
            savings_budget = monthly_income * 0.20
            
            print(f"📊 Budget Analysis (Real Income: {self.format_currency(monthly_income)}):")
            print(f"  NEEDS Budget: {self.format_currency(needs_budget)} | Spent: {self.format_currency(spending_by_type.get('needs', 0))}")
            print(f"  WANTS Budget: {self.format_currency(wants_budget)} | Spent: {self.format_currency(spending_by_type.get('wants', 0))}")
            print(f"  SAVINGS Budget: {self.format_currency(savings_budget)} | Spent: {self.format_currency(spending_by_type.get('savings', 0))}")
            
            # Calculate performance
            performance = {
                "needs": {
                    "budget": needs_budget,
                    "spent": spending_by_type.get("needs", 0),
                    "remaining": max(needs_budget - spending_by_type.get("needs", 0), 0),
                    "percentage_used": (spending_by_type.get("needs", 0) / needs_budget * 100) if needs_budget > 0 else 0,
                    "status": "over" if spending_by_type.get("needs", 0) > needs_budget else "under"
                },
                "wants": {
                    "budget": wants_budget,
                    "spent": spending_by_type.get("wants", 0),
                    "remaining": max(wants_budget - spending_by_type.get("wants", 0), 0),
                    "percentage_used": (spending_by_type.get("wants", 0) / wants_budget * 100) if wants_budget > 0 else 0,
                    "status": "over" if spending_by_type.get("wants", 0) > wants_budget else "under"
                },
                "savings": {
                    "budget": savings_budget,
                    "spent": spending_by_type.get("savings", 0),
                    "remaining": max(savings_budget - spending_by_type.get("savings", 0), 0),
                    "percentage_used": (spending_by_type.get("savings", 0) / savings_budget * 100) if savings_budget > 0 else 0,
                    "status": "over" if spending_by_type.get("savings", 0) > savings_budget else "under"
                }
            }
            
            # Overall assessment
            total_spent = sum(spending_by_type.values())
            overall_percentage = (total_spent / monthly_income * 100) if monthly_income > 0 else 0
            
            if overall_percentage <= 70:
                budget_health = "excellent"
            elif overall_percentage <= 90:
                budget_health = "good"
            elif overall_percentage <= 100:
                budget_health = "warning"
            else:
                budget_health = "critical"
            
            return {
                "monthly_income": monthly_income,
                "is_real_income": True,  # FIXED: Indicate this is from real transactions
                "performance": performance,
                "total_spent": total_spent,
                "overall_percentage": overall_percentage,
                "budget_health": budget_health,
                "period": now.strftime("%B %Y")
            }
            
        except Exception as e:
            print(f"Error analyzing budget performance: {e}")
            return {
                "monthly_income": monthly_income,
                "is_real_income": True,
                "performance": {"needs": {}, "wants": {}, "savings": {}},
                "total_spent": 0,
                "overall_percentage": 0,
                "budget_health": "unknown",
                "period": "Unknown"
            }
    
    async def _analyze_savings_goals(self, user_id: str) -> Dict[str, Any]:
        """Analyze savings goals progress"""
        try:
            # Get all savings goals
            goals_cursor = self.db.savings_goals.find({
                "user_id": user_id,
                "status": {"$in": ["active", "paused", "completed"]}
            })
            
            goals = list(goals_cursor)
            if not goals:
                return {
                    "has_goals": False,
                    "total_goals": 0,
                    "active_goals": 0,
                    "completed_goals": 0,
                    "total_target": 0,
                    "total_current": 0,
                    "average_progress": 0,
                    "urgent_goals": []
                }
            
            # Analyze goals
            active_goals = [g for g in goals if g["status"] == "active"]
            completed_goals = [g for g in goals if g["status"] == "completed"]
            
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
                            urgent_goals.append({
                                "id": str(goal["_id"]),
                                "item_name": goal["item_name"],
                                "target_amount": goal["target_amount"],
                                "current_amount": goal["current_amount"],
                                "days_remaining": days_remaining,
                                "progress": (goal["current_amount"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
                            })
                    except:
                        continue
            
            return {
                "has_goals": True,
                "total_goals": len(goals),
                "active_goals": len(active_goals),
                "completed_goals": len(completed_goals),
                "total_target": total_target,
                "total_current": total_current,
                "average_progress": average_progress,
                "urgent_goals": urgent_goals,
                "goals_summary": [
                    {
                        "item_name": g["item_name"],
                        "target_amount": g["target_amount"],
                        "current_amount": g["current_amount"],
                        "progress": (g["current_amount"] / g["target_amount"] * 100) if g["target_amount"] > 0 else 0,
                        "status": g["status"]
                    } for g in goals[:5]  # Top 5 goals
                ]
            }
            
        except Exception as e:
            print(f"Error analyzing savings goals: {e}")
            return {
                "has_goals": False,
                "total_goals": 0,
                "active_goals": 0,
                "completed_goals": 0,
                "total_target": 0,
                "total_current": 0,
                "average_progress": 0,
                "urgent_goals": []
            }
    
    async def _analyze_spending_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze spending patterns from actual transactions"""
        try:
            # Get last 30 days transactions
            thirty_days_ago = now_for_db() - timedelta(days=30)
            
            # Get spending by category
            category_pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "type": TransactionType.EXPENSE.value,
                    "status": TransactionStatus.CONFIRMED.value,
                    "date": {"$gte": thirty_days_ago}
                }},
                {"$group": {
                    "_id": "$category",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"total": -1}}
            ]
            
            category_spending = list(self.db.transactions.aggregate(category_pipeline))
            
            # Get daily spending trend
            daily_pipeline = [
                {"$match": {
                    "user_id": user_id,
                    "type": TransactionType.EXPENSE.value,
                    "status": TransactionStatus.CONFIRMED.value,
                    "date": {"$gte": thirty_days_ago}
                }},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                    "total": {"$sum": "$amount"}
                }},
                {"$sort": {"_id": 1}}
            ]
            
            daily_spending = list(self.db.transactions.aggregate(daily_pipeline))
            
            # Calculate averages
            total_spent = sum(item["total"] for item in category_spending)
            average_daily = total_spent / 30 if total_spent > 0 else 0
            
            return {
                "period_days": 30,
                "total_spent": total_spent,
                "average_daily": average_daily,
                "transaction_count": sum(item["count"] for item in category_spending),
                "top_categories": category_spending[:5],
                "daily_trend": daily_spending,
                "highest_spending_day": max(daily_spending, key=lambda x: x["total"]) if daily_spending else None,
                "lowest_spending_day": min(daily_spending, key=lambda x: x["total"]) if daily_spending else None
            }
            
        except Exception as e:
            print(f"Error analyzing spending patterns: {e}")
            return {
                "period_days": 30,
                "total_spent": 0,
                "average_daily": 0,
                "transaction_count": 0,
                "top_categories": [],
                "daily_trend": [],
                "highest_spending_day": None,
                "lowest_spending_day": None
            }
    
    # ==========================================
    # PURCHASE ANALYSIS METHODS - ENHANCED
    # ==========================================
    
    async def analyze_purchase_impact(self, user_id: str, item_name: str, price: float) -> Dict[str, Any]:
        """
        FIXED: Analisis dampak pembelian berdasarkan REAL financial status
        """
        try:
            # Get current financial analysis (dengan REAL data)
            financial_status = await self.analyze_user_financial_status(user_id)
            
            if financial_status["status"] != "analyzed":
                return {
                    "can_analyze": False,
                    "message": "Tidak dapat menganalisis dampak pembelian - belum ada data transaksi yang cukup",
                    "reason": financial_status.get("message", "Financial data not available")
                }
            
            budget_performance = financial_status["budget_performance"]
            real_monthly_income = financial_status["real_monthly_income"]  # FIXED: Use real income
            
            # Determine item category and budget type
            category, budget_type = IndonesianStudentCategories.get_expense_category_with_budget_type(item_name)
            
            # Calculate impact on budget (dengan REAL income)
            budget_impact = self._calculate_budget_impact(price, budget_type, budget_performance, real_monthly_income)
            
            # Calculate impact on savings goals
            savings_impact = await self._calculate_savings_impact(user_id, price)
            
            # Generate recommendations
            recommendations = self._generate_purchase_recommendations(
                item_name, price, budget_type, budget_impact, savings_impact
            )
            
            # Overall assessment
            overall_assessment = self._assess_purchase_feasibility(budget_impact, savings_impact)
            
            return {
                "can_analyze": True,
                "item_name": item_name,
                "price": price,
                "category": category,
                "budget_type": budget_type,
                "budget_impact": budget_impact,
                "savings_impact": savings_impact,
                "recommendations": recommendations,
                "overall_assessment": overall_assessment,
                "real_monthly_income": real_monthly_income,  # FIXED: Include real income
                "analysis_timestamp": now_for_db()
            }
            
        except Exception as e:
            print(f"Error analyzing purchase impact: {e}")
            return {
                "can_analyze": False,
                "message": f"Gagal menganalisis dampak pembelian: {str(e)}"
            }
    
    def _calculate_budget_impact(self, price: float, budget_type: str, budget_performance: Dict, monthly_income: float) -> Dict[str, Any]:
        """Calculate impact on budget allocation dengan REAL income"""
        try:
            performance = budget_performance["performance"]
            
            if budget_type not in performance:
                return {
                    "impact_level": "unknown",
                    "message": "Budget type tidak dikenali"
                }
            
            budget_info = performance[budget_type]
            current_spent = budget_info["spent"]
            budget_allocation = budget_info["budget"]
            current_remaining = budget_info["remaining"]
            
            # Calculate impact
            after_purchase_spent = current_spent + price
            after_purchase_remaining = max(budget_allocation - after_purchase_spent, 0)
            after_purchase_percentage = (after_purchase_spent / budget_allocation * 100) if budget_allocation > 0 else 0
            
            # Determine impact level
            if after_purchase_percentage <= 70:
                impact_level = "safe"
            elif after_purchase_percentage <= 90:
                impact_level = "moderate"
            elif after_purchase_percentage <= 100:
                impact_level = "high"
            else:
                impact_level = "critical"
            
            print(f"💳 Purchase Impact Analysis:")
            print(f"  Budget Type: {budget_type}")
            print(f"  Current Spent: {self.format_currency(current_spent)}")
            print(f"  Budget Allocation: {self.format_currency(budget_allocation)}")
            print(f"  After Purchase: {self.format_currency(after_purchase_spent)} ({after_purchase_percentage:.1f}%)")
            print(f"  Impact Level: {impact_level}")
            
            return {
                "budget_type": budget_type,
                "budget_allocation": budget_allocation,
                "current_spent": current_spent,
                "current_remaining": current_remaining,
                "current_percentage": budget_info["percentage_used"],
                "after_purchase_spent": after_purchase_spent,
                "after_purchase_remaining": after_purchase_remaining,
                "after_purchase_percentage": after_purchase_percentage,
                "impact_level": impact_level,
                "exceeds_budget": after_purchase_spent > budget_allocation,
                "overspend_amount": max(after_purchase_spent - budget_allocation, 0)
            }
            
        except Exception as e:
            print(f"Error calculating budget impact: {e}")
            return {
                "impact_level": "unknown",
                "message": f"Error calculating impact: {str(e)}"
            }
    
    async def _calculate_savings_impact(self, user_id: str, price: float) -> Dict[str, Any]:
        """Calculate impact on savings goals"""
        try:
            # Get current savings analysis
            savings_analysis = await self._analyze_savings_goals(user_id)
            
            if not savings_analysis["has_goals"]:
                return {
                    "has_impact": False,
                    "message": "Tidak ada target tabungan aktif"
                }
            
            # Calculate impact on total savings progress
            total_current = savings_analysis["total_current"]
            total_target = savings_analysis["total_target"]
            
            # Assume spending reduces potential savings
            adjusted_current = max(total_current - price, 0)
            adjusted_progress = (adjusted_current / total_target * 100) if total_target > 0 else 0
            
            progress_reduction = savings_analysis["average_progress"] - adjusted_progress
            
            # Check impact on urgent goals
            urgent_goals_impact = []
            for goal in savings_analysis["urgent_goals"]:
                days_remaining = goal["days_remaining"]
                daily_needed = (goal["target_amount"] - goal["current_amount"]) / days_remaining if days_remaining > 0 else 0
                daily_needed_after = (goal["target_amount"] - max(goal["current_amount"] - price, 0)) / days_remaining if days_remaining > 0 else 0
                
                urgent_goals_impact.append({
                    "goal": goal["item_name"],
                    "days_remaining": days_remaining,
                    "daily_needed_before": daily_needed,
                    "daily_needed_after": daily_needed_after,
                    "additional_daily_needed": daily_needed_after - daily_needed
                })
            
            return {
                "has_impact": True,
                "total_current": total_current,
                "total_target": total_target,
                "current_progress": savings_analysis["average_progress"],
                "adjusted_progress": adjusted_progress,
                "progress_reduction": progress_reduction,
                "urgent_goals_impact": urgent_goals_impact,
                "delays_goals": progress_reduction > 5  # 5% threshold
            }
            
        except Exception as e:
            print(f"Error calculating savings impact: {e}")
            return {
                "has_impact": False,
                "message": f"Error calculating savings impact: {str(e)}"
            }
    
    # ==========================================
    # HELPER METHODS
    # ==========================================
    
    async def _get_spending_by_budget_type(self, user_id: str, start_date: datetime) -> Dict[str, float]:
        """Get spending by budget type from start_date"""
        try:
            transactions = self.db.transactions.find({
                "user_id": user_id,
                "status": TransactionStatus.CONFIRMED.value,
                "date": {"$gte": start_date},
                "type": TransactionType.EXPENSE.value
            })
            
            spending_by_type = {"needs": 0.0, "wants": 0.0, "savings": 0.0}
            
            for trans in transactions:
                category = trans.get("category", "")
                amount = trans.get("amount", 0.0)
                
                # Determine budget type
                _, budget_type = IndonesianStudentCategories.get_expense_category_with_budget_type(category)
                
                if budget_type in spending_by_type:
                    spending_by_type[budget_type] += amount
            
            return spending_by_type
            
        except Exception as e:
            print(f"Error getting spending by budget type: {e}")
            return {"needs": 0.0, "wants": 0.0, "savings": 0.0}
    
    async def _count_transactions(self, user_id: str, transaction_type: str) -> int:
        """Count transactions by type"""
        try:
            return self.db.transactions.count_documents({
                "user_id": user_id,
                "type": transaction_type,
                "status": TransactionStatus.CONFIRMED.value
            })
        except:
            return 0
    
    def _calculate_health_score(self, current_totals: Dict, budget_performance: Dict, 
                              savings_analysis: Dict, monthly_income: float) -> Dict[str, Any]:
        """Calculate overall financial health score berdasarkan REAL data"""
        try:
            score = 0
            max_score = 100
            
            # Budget discipline score (40 points) - berdasarkan REAL performance
            budget_health = budget_performance.get("budget_health", "unknown")
            if budget_health == "excellent":
                score += 40
            elif budget_health == "good":
                score += 30
            elif budget_health == "warning":
                score += 20
            elif budget_health == "critical":
                score += 10
            
            # Savings progress score (30 points)
            if savings_analysis.get("has_goals"):
                average_progress = savings_analysis.get("average_progress", 0)
                if average_progress >= 80:
                    score += 30
                elif average_progress >= 60:
                    score += 25
                elif average_progress >= 40:
                    score += 20
                elif average_progress >= 20:
                    score += 15
                else:
                    score += 10
            
            # REAL Savings growth score (20 points)
            savings_growth = current_totals.get("savings_growth", 0)
            if savings_growth > 0:
                score += 20
            elif savings_growth >= -monthly_income * 0.1:  # Small negative is OK
                score += 15
            else:
                score += 5
            
            # Transaction activity score (10 points)
            transaction_count = current_totals.get("transaction_count", {})
            total_transactions = transaction_count.get("income", 0) + transaction_count.get("expense", 0)
            if total_transactions >= 20:
                score += 10
            elif total_transactions >= 10:
                score += 8
            elif total_transactions >= 5:
                score += 5
            
            # Determine level
            percentage = (score / max_score) * 100
            if percentage >= 80:
                level = "excellent"
            elif percentage >= 60:
                level = "good"
            elif percentage >= 40:
                level = "fair"
            else:
                level = "needs_improvement"
            
            return {
                "score": score,
                "max_score": max_score,
                "percentage": percentage,
                "level": level,
                "components": {
                    "budget_discipline": budget_health,
                    "savings_progress": savings_analysis.get("average_progress", 0),
                    "savings_growth": savings_growth,
                    "transaction_activity": total_transactions
                }
            }
            
        except Exception as e:
            print(f"Error calculating health score: {e}")
            return {
                "score": 0,
                "max_score": 100,
                "percentage": 0,
                "level": "unknown",
                "components": {}
            }
    
    def _generate_recommendations(self, budget_performance: Dict, savings_analysis: Dict, 
                                spending_patterns: Dict, health_score: Dict) -> List[str]:
        """Generate personalized recommendations berdasarkan REAL performance"""
        recommendations = []
        
        # Budget-based recommendations
        budget_health = budget_performance.get("budget_health", "unknown")
        if budget_health == "critical":
            recommendations.append("🚨 URGENT: Pengeluaran melebihi pemasukan! Kurangi pengeluaran WANTS dan focus pada NEEDS saja")
        elif budget_health == "warning":
            recommendations.append("⚠️ Pengeluaran mendekati batas! Evaluasi kategori WANTS dan pastikan tidak melebihi 30%")
        elif budget_health == "excellent":
            recommendations.append("🎉 Budget management excellent! Pertimbangkan untuk meningkatkan investasi dari surplus")
        
        # Savings-based recommendations
        if savings_analysis.get("has_goals"):
            urgent_goals = savings_analysis.get("urgent_goals", [])
            if urgent_goals:
                recommendations.append(f"⏰ {len(urgent_goals)} target tabungan akan deadline dalam 30 hari! Prioritaskan saving")
            
            average_progress = savings_analysis.get("average_progress", 0)
            if average_progress < 30:
                recommendations.append("📈 Progress target tabungan masih rendah. Alokasikan lebih banyak dari budget WANTS")
        else:
            recommendations.append("🎯 Belum ada target tabungan. Buat target untuk motivasi saving yang lebih baik")
        
        # Spending pattern recommendations berdasarkan REAL transactions
        top_categories = spending_patterns.get("top_categories", [])
        if top_categories:
            top_category = top_categories[0]
            recommendations.append(f"💡 Pengeluaran terbesar: {top_category['_id']} ({self.format_currency(top_category['total'])}). Cek apakah bisa dihemat")
        
        # Health score recommendations
        health_level = health_score.get("level", "unknown")
        if health_level == "needs_improvement":
            recommendations.append("🔧 Mulai disiplin dengan metode 50/30/20 berdasarkan income REAL Anda")
        elif health_level == "fair":
            recommendations.append("📊 Financial health cukup baik. Tingkatkan konsistensi untuk hasil yang lebih optimal")
        
        return recommendations
    
    def _generate_purchase_recommendations(self, item_name: str, price: float, budget_type: str, 
                                         budget_impact: Dict, savings_impact: Dict) -> List[str]:
        """Generate purchase-specific recommendations"""
        recommendations = []
        
        # Budget impact recommendations
        impact_level = budget_impact.get("impact_level", "unknown")
        if impact_level == "critical":
            recommendations.append(f"🚨 TIDAK DIREKOMENDASIKAN: Pembelian ini akan melebihi budget {budget_type.upper()} sebesar {self.format_currency(budget_impact.get('overspend_amount', 0))}")
        elif impact_level == "high":
            recommendations.append(f"⚠️ HATI-HATI: Pembelian ini akan menghabiskan hampir seluruh budget {budget_type.upper()} bulan ini")
        elif impact_level == "moderate":
            recommendations.append(f"💡 PERTIMBANGKAN: Pembelian ini cukup besar untuk budget {budget_type.upper()}, pastikan benar-benar perlu")
        elif impact_level == "safe":
            recommendations.append(f"✅ AMAN: Pembelian ini masih dalam batas wajar untuk budget {budget_type.upper()}")
        
        # Savings impact recommendations
        if savings_impact.get("has_impact") and savings_impact.get("delays_goals"):
            recommendations.append(f"📉 Pembelian ini akan mengurangi progress target tabungan sebesar {savings_impact.get('progress_reduction', 0):.1f}%")
        
        # Alternative suggestions
        if impact_level in ["critical", "high"]:
            if budget_type == "wants":
                recommendations.append("💭 Alternatif: Pertimbangkan untuk menabung dulu untuk barang ini, atau cari versi yang lebih terjangkau")
            elif budget_type == "needs":
                recommendations.append("🔍 Alternatif: Cari opsi yang lebih murah untuk kebutuhan ini, atau tunda jika tidak urgent")
        
        # Timing recommendations
        if budget_type == "wants" and impact_level in ["moderate", "high"]:
            recommendations.append("⏰ Saran waktu: Lebih baik tunggu bulan depan saat budget WANTS reset, atau nabung dari surplus budget")
        
        return recommendations
    
    def _assess_purchase_feasibility(self, budget_impact: Dict, savings_impact: Dict) -> Dict[str, Any]:
        """Assess overall purchase feasibility"""
        impact_level = budget_impact.get("impact_level", "unknown")
        exceeds_budget = budget_impact.get("exceeds_budget", False)
        delays_goals = savings_impact.get("delays_goals", False)
        
        if impact_level == "critical" or exceeds_budget:
            feasibility = "not_recommended"
            message = "Pembelian ini tidak direkomendasikan karena akan merusak budget"
        elif impact_level == "high" or delays_goals:
            feasibility = "risky"
            message = "Pembelian ini berisiko terhadap rencana keuangan Anda"
        elif impact_level == "moderate":
            feasibility = "consider"
            message = "Pembelian ini perlu dipertimbangkan matang-matang"
        elif impact_level == "safe":
            feasibility = "recommended"
            message = "Pembelian ini masih dalam batas yang aman"
        else:
            feasibility = "unknown"
            message = "Tidak dapat menilai kelayakan pembelian"
        
        return {
            "feasibility": feasibility,
            "message": message,
            "factors": {
                "budget_impact": impact_level,
                "exceeds_budget": exceeds_budget,
                "delays_goals": delays_goals
            }
        }