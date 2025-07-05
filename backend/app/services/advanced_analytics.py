# app/services/advanced_analytics.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Dict, List, Any, Optional
import asyncio
import logging

from ..database import get_database

logger = logging.getLogger(__name__)

class AdvancedAnalytics:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = None
    
    async def get_database(self):
        if not self.db:
            self.db = await get_database()
        return self.db
    
    async def calculate_cash_flow(self, months: int = 6) -> Dict[str, Any]:
        """Calculate detailed cash flow analysis"""
        try:
            db = await self.get_database()
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=months * 30)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(self.user_id),
                        "date": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"},
                            "type": "$type"
                        },
                        "total": {"$sum": "$amount"},
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1}
                }
            ]
            
            results = await db.transactions.aggregate(pipeline).to_list(None)
            
            # Process results
            monthly_data = {}
            for result in results:
                month_key = f"{result['_id']['year']}-{result['_id']['month']:02d}"
                if month_key not in monthly_data:
                    monthly_data[month_key] = {"income": 0, "expense": 0}
                
                monthly_data[month_key][result["_id"]["type"]] = result["total"]
            
            # Calculate cash flow metrics
            cash_flow_data = []
            for month, data in monthly_data.items():
                net_flow = data["income"] - data["expense"]
                cash_flow_data.append({
                    "month": month,
                    "income": data["income"],
                    "expense": data["expense"],
                    "net_flow": net_flow,
                    "cash_flow_ratio": data["income"] / data["expense"] if data["expense"] > 0 else 0
                })
            
            # Calculate averages and trends
            if cash_flow_data:
                avg_income = np.mean([d["income"] for d in cash_flow_data])
                avg_expense = np.mean([d["expense"] for d in cash_flow_data])
                avg_net_flow = avg_income - avg_expense
                
                # Calculate trend (simple linear regression)
                months_count = len(cash_flow_data)
                if months_count > 1:
                    x = np.arange(months_count)
                    net_flows = [d["net_flow"] for d in cash_flow_data]
                    trend = np.polyfit(x, net_flows, 1)[0]  # Slope
                else:
                    trend = 0
            else:
                avg_income = avg_expense = avg_net_flow = trend = 0
            
            return {
                "monthly_cash_flow": cash_flow_data,
                "summary": {
                    "average_income": round(avg_income, 2),
                    "average_expense": round(avg_expense, 2),
                    "average_net_flow": round(avg_net_flow, 2),
                    "trend": round(trend, 2),
                    "months_analyzed": len(cash_flow_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in cash flow analysis: {str(e)}")
            raise
    
    async def analyze_seasonal_patterns(self) -> Dict[str, Any]:
        """Analyze seasonal spending patterns"""
        try:
            db = await self.get_database()
            
            # Get last 2 years of data for seasonal analysis
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=730)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(self.user_id),
                        "type": "expense",
                        "date": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "month": {"$month": "$date"},
                            "day_of_week": {"$dayOfWeek": "$date"},
                            "category": "$category_id"
                        },
                        "total": {"$sum": "$amount"},
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            results = await db.transactions.aggregate(pipeline).to_list(None)
            
            # Process monthly patterns
            monthly_spending = {}
            weekly_spending = {}
            category_patterns = {}
            
            for result in results:
                month = result["_id"]["month"]
                day_of_week = result["_id"]["day_of_week"]
                category = str(result["_id"]["category"])
                total = result["total"]
                
                # Monthly patterns
                if month not in monthly_spending:
                    monthly_spending[month] = 0
                monthly_spending[month] += total
                
                # Weekly patterns (1=Sunday, 7=Saturday)
                if day_of_week not in weekly_spending:
                    weekly_spending[day_of_week] = 0
                weekly_spending[day_of_week] += total
                
                # Category patterns by month
                if category not in category_patterns:
                    category_patterns[category] = {}
                if month not in category_patterns[category]:
                    category_patterns[category][month] = 0
                category_patterns[category][month] += total
            
            # Find peak and low spending periods
            if monthly_spending:
                peak_month = max(monthly_spending, key=monthly_spending.get)
                low_month = min(monthly_spending, key=monthly_spending.get)
            else:
                peak_month = low_month = None
            
            if weekly_spending:
                peak_day = max(weekly_spending, key=weekly_spending.get)
                low_day = min(weekly_spending, key=weekly_spending.get)
            else:
                peak_day = low_day = None
            
            # Convert day numbers to names
            day_names = {1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday", 
                        5: "Thursday", 6: "Friday", 7: "Saturday"}
            month_names = {1: "January", 2: "February", 3: "March", 4: "April",
                          5: "May", 6: "June", 7: "July", 8: "August",
                          9: "September", 10: "October", 11: "November", 12: "December"}
            
            return {
                "monthly_patterns": {
                    str(month_names.get(month, f"Month {month}")): round(total, 2)
                    for month, total in monthly_spending.items()
                },
                "weekly_patterns": {
                    day_names.get(day, f"Day {day}"): round(total, 2)
                    for day, total in weekly_spending.items()
                },
                "peak_periods": {
                    "peak_month": month_names.get(peak_month, "N/A") if peak_month else "N/A",
                    "low_month": month_names.get(low_month, "N/A") if low_month else "N/A",
                    "peak_day": day_names.get(peak_day, "N/A") if peak_day else "N/A",
                    "low_day": day_names.get(low_day, "N/A") if low_day else "N/A"
                },
                "insights": self._generate_seasonal_insights(monthly_spending, weekly_spending)
            }
            
        except Exception as e:
            logger.error(f"Error in seasonal analysis: {str(e)}")
            raise
    
    def _generate_seasonal_insights(self, monthly_spending: Dict, weekly_spending: Dict) -> List[str]:
        """Generate insights from seasonal patterns"""
        insights = []
        
        if monthly_spending:
            # Check for holiday spending
            high_months = [1, 11, 12]  # Jan, Nov, Dec (holidays)
            holiday_spending = sum(monthly_spending.get(month, 0) for month in high_months)
            total_spending = sum(monthly_spending.values())
            
            if holiday_spending > total_spending * 0.35:
                insights.append("Pengeluaran tinggi di musim liburan (Nov-Jan)")
        
        if weekly_spending:
            # Check for weekend spending
            weekend_spending = weekly_spending.get(1, 0) + weekly_spending.get(7, 0)  # Sun + Sat
            weekday_spending = sum(spending for day, spending in weekly_spending.items() if day not in [1, 7])
            
            if weekend_spending > weekday_spending * 0.4:
                insights.append("Pengeluaran lebih tinggi di akhir pekan")
        
        if not insights:
            insights.append("Pola pengeluaran cukup konsisten sepanjang tahun")
        
        return insights
    
    async def calculate_financial_health_score(self) -> Dict[str, Any]:
        """Calculate comprehensive financial health score"""
        try:
            db = await self.get_database()
            
            # Get data for last 3 months
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=90)
            
            # Calculate monthly metrics
            pipeline = [
                {
                    "$match": {
                        "user_id": ObjectId(self.user_id),
                        "date": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "type": "$type",
                            "month": {"$month": "$date"}
                        },
                        "total": {"$sum": "$amount"}
                    }
                }
            ]
            
            results = await db.transactions.aggregate(pipeline).to_list(None)
            
            # Process monthly data
            monthly_data = {}
            for result in results:
                month = result["_id"]["month"]
                trans_type = result["_id"]["type"]
                
                if month not in monthly_data:
                    monthly_data[month] = {"income": 0, "expense": 0}
                
                monthly_data[month][trans_type] = result["total"]
            
            # Calculate metrics
            if not monthly_data:
                return self._default_health_score()
            
            # Average monthly values
            avg_income = np.mean([data["income"] for data in monthly_data.values()])
            avg_expense = np.mean([data["expense"] for data in monthly_data.values()])
            avg_savings = avg_income - avg_expense
            
            # Get savings goals progress
            savings_goals = await db.savings_goals.find({
                "user_id": ObjectId(self.user_id),
                "is_active": True
            }).to_list(None)
            
            avg_goal_progress = 0
            if savings_goals:
                progress_sum = sum(goal.get("current_amount", 0) / goal.get("target_amount", 1) 
                                 for goal in savings_goals)
                avg_goal_progress = (progress_sum / len(savings_goals)) * 100
            
            # Get budget adherence
            budget_adherence = await self._calculate_budget_adherence()
            
            # Calculate component scores
            scores = {
                'savings_rate': min(100, (avg_savings / avg_income * 100 * 2) if avg_income > 0 else 0),
                'budget_adherence': budget_adherence,
                'income_stability': self._calculate_income_stability(monthly_data),
                'expense_control': self._calculate_expense_control(monthly_data),
                'goal_progress': min(100, avg_goal_progress * 2)
            }
            
            # Calculate weighted total score
            weights = {
                'savings_rate': 0.25,
                'budget_adherence': 0.2,
                'income_stability': 0.2,
                'expense_control': 0.2,
                'goal_progress': 0.15
            }
            
            total_score = sum(scores[key] * weights[key] for key in scores)
            
            return {
                'overall_score': round(total_score, 1),
                'component_scores': {k: round(v, 1) for k, v in scores.items()},
                'rating': self._get_health_rating(total_score),
                'recommendations': self._generate_health_recommendations(scores),
                'monthly_summary': {
                    'avg_income': round(avg_income, 2),
                    'avg_expense': round(avg_expense, 2),
                    'avg_savings': round(avg_savings, 2),
                    'savings_rate': round((avg_savings / avg_income * 100) if avg_income > 0 else 0, 1)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating financial health: {str(e)}")
            return self._default_health_score()
    
    def _default_health_score(self) -> Dict[str, Any]:
        """Return default health score when insufficient data"""
        return {
            'overall_score': 0.0,
            'component_scores': {
                'savings_rate': 0.0,
                'budget_adherence': 0.0,
                'income_stability': 0.0,
                'expense_control': 0.0,
                'goal_progress': 0.0
            },
            'rating': 'Insufficient Data',
            'recommendations': ['Tambahkan lebih banyak transaksi untuk analisis yang lebih akurat'],
            'monthly_summary': {
                'avg_income': 0.0,
                'avg_expense': 0.0,
                'avg_savings': 0.0,
                'savings_rate': 0.0
            }
        }
    
    async def _calculate_budget_adherence(self) -> float:
        """Calculate how well user adheres to budgets"""
        try:
            db = await self.get_database()
            
            # Get active budgets
            budgets = await db.budgets.find({
                "user_id": ObjectId(self.user_id),
                "is_active": True
            }).to_list(None)
            
            if not budgets:
                return 50.0  # Neutral score if no budgets
            
            adherence_scores = []
            current_month = datetime.utcnow().month
            current_year = datetime.utcnow().year
            
            for budget in budgets:
                # Get spending for this category this month
                spent = await db.transactions.aggregate([
                    {
                        "$match": {
                            "user_id": ObjectId(self.user_id),
                            "category_id": budget["category_id"],
                            "type": "expense",
                            "$expr": {
                                "$and": [
                                    {"$eq": [{"$month": "$date"}, current_month]},
                                    {"$eq": [{"$year": "$date"}, current_year]}
                                ]
                            }
                        }
                    },
                    {
                        "$group": {
                            "_id": None,
                            "total": {"$sum": "$amount"}
                        }
                    }
                ]).to_list(1)
                
                spent_amount = spent[0]["total"] if spent else 0
                budget_amount = budget["amount"]
                
                # Calculate adherence (100% if under budget, decreasing as overspend increases)
                if spent_amount <= budget_amount:
                    adherence_scores.append(100.0)
                else:
                    overspend_ratio = spent_amount / budget_amount
                    adherence = max(0, 100 - (overspend_ratio - 1) * 50)
                    adherence_scores.append(adherence)
            
            return np.mean(adherence_scores) if adherence_scores else 50.0
            
        except Exception:
            return 50.0
    
    def _calculate_income_stability(self, monthly_data: Dict) -> float:
        """Calculate income stability score"""
        incomes = [data["income"] for data in monthly_data.values()]
        
        if len(incomes) < 2:
            return 50.0
        
        mean_income = np.mean(incomes)
        if mean_income == 0:
            return 0.0
        
        # Calculate coefficient of variation
        cv = np.std(incomes) / mean_income
        
        # Convert to score (lower CV = higher stability)
        stability_score = max(0, 100 - cv * 100)
        return min(100, stability_score)
    
    def _calculate_expense_control(self, monthly_data: Dict) -> float:
        """Calculate expense control score"""
        expenses = [data["expense"] for data in monthly_data.values()]
        
        if len(expenses) < 2:
            return 50.0
        
        # Check if expenses are trending down or stable
        x = np.arange(len(expenses))
        if len(x) > 1:
            slope = np.polyfit(x, expenses, 1)[0]
            
            # Negative slope (decreasing expenses) = good control
            if slope <= 0:
                return 80.0
            else:
                # Positive slope (increasing expenses) = poor control
                mean_expense = np.mean(expenses)
                increase_rate = slope / mean_expense if mean_expense > 0 else 0
                return max(20, 80 - increase_rate * 1000)
        
        return 50.0
    
    def _get_health_rating(self, score: float) -> str:
        """Get health rating based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        elif score >= 20:
            return "Poor"
        else:
            return "Critical"
    
    def _generate_health_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate personalized recommendations based on scores"""
        recommendations = []
        
        if scores['savings_rate'] < 50:
            recommendations.append("Tingkatkan tingkat menabung dengan mengurangi pengeluaran tidak penting")
        
        if scores['budget_adherence'] < 60:
            recommendations.append("Buat budget yang lebih realistis dan pantau pengeluaran secara berkala")
        
        if scores['income_stability'] < 50:
            recommendations.append("Pertimbangkan sumber pendapatan tambahan untuk stabilitas keuangan")
        
        if scores['expense_control'] < 60:
            recommendations.append("Tinjau dan kategorikan pengeluaran untuk kontrol yang lebih baik")
        
        if scores['goal_progress'] < 40:
            recommendations.append("Set target menabung yang lebih realistis dan buat rencana pencapaian")
        
        if not recommendations:
            recommendations.append("Pertahankan kebiasaan keuangan yang baik!")
        
        return recommendations
    
    async def generate_ai_recommendations(self) -> List[Dict[str, Any]]:
        """Generate AI-powered financial recommendations"""
        try:
            # Get financial health data
            health_data = await self.calculate_financial_health_score()
            cash_flow = await self.calculate_cash_flow(3)
            
            recommendations = []
            
            # Savings recommendations
            if health_data['component_scores']['savings_rate'] < 60:
                avg_income = health_data['monthly_summary']['avg_income']
                target_savings = avg_income * 0.2  # 20% savings goal
                
                recommendations.append({
                    "type": "savings",
                    "priority": "high",
                    "title": "Tingkatkan Tingkat Menabung",
                    "description": f"Target menabung Rp{target_savings:,.0f} per bulan (20% dari pendapatan)",
                    "action_items": [
                        "Buat budget ketat untuk pengeluaran bulanan",
                        "Otomatisasi transfer ke rekening tabungan",
                        "Cari cara mengurangi pengeluaran rutin"
                    ]
                })
            
            # Budget recommendations
            if health_data['component_scores']['budget_adherence'] < 50:
                recommendations.append({
                    "type": "budget",
                    "priority": "medium",
                    "title": "Perbaiki Kepatuhan Budget",
                    "description": "Budget sering terlampaui, perlu penyesuaian strategi",
                    "action_items": [
                        "Review dan sesuaikan budget dengan pola pengeluaran aktual",
                        "Set alert untuk spending di setiap kategori",
                        "Gunakan metode envelope budgeting"
                    ]
                })
            
            # Cash flow recommendations
            if cash_flow['summary']['average_net_flow'] < 0:
                recommendations.append({
                    "type": "cash_flow",
                    "priority": "high",
                    "title": "Atasi Cash Flow Negatif",
                    "description": "Pengeluaran lebih besar dari pendapatan setiap bulan",
                    "action_items": [
                        "Identifikasi pengeluaran yang bisa dikurangi",
                        "Cari sumber pendapatan tambahan",
                        "Prioritaskan pembayaran utang"
                    ]
                })
            
            # Goal-based recommendations
            if health_data['component_scores']['goal_progress'] < 40:
                recommendations.append({
                    "type": "goals",
                    "priority": "medium",
                    "title": "Optimalkan Progress Savings Goals",
                    "description": "Kemajuan menabung untuk tujuan khusus masih lambat",
                    "action_items": [
                        "Review timeline dan target savings goals",
                        "Buat auto-debit untuk savings goals",
                        "Breakdown goals besar menjadi milestone kecil"
                    ]
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []