# app/services/analytics/student_insights.py
from datetime import datetime, timedelta
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

class StudentInsightsService:
    """Service for generating student-specific financial insights"""
    
    async def generate_student_insights(
        self, 
        db: AsyncIOMotorDatabase, 
        student_id: ObjectId
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered insights for student"""
        
        insights = []
        
        try:
            # Get student data
            student = await db.students.find_one({"_id": student_id})
            if not student:
                return insights
            
            # Get recent transactions (last 30 days)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            transactions = await db.transactions.find({
                "student_id": student_id,
                "transaction_date": {"$gte": start_date, "$lte": end_date}
            }).to_list(length=None)
            
            # Generate insights
            insights.extend(await self._analyze_spending_patterns(transactions))
            insights.extend(await self._analyze_budget_adherence(student, transactions))
            insights.extend(await self._analyze_category_trends(db, transactions))
            insights.extend(await self._generate_academic_insights(student, transactions))
            
        except Exception as e:
            # Return empty insights on error
            pass
        
        return insights
    
    async def _analyze_spending_patterns(self, transactions: List[Dict]) -> List[Dict]:
        """Analyze spending patterns"""
        insights = []
        
        if not transactions:
            return insights
        
        expenses = [t for t in transactions if t.get("type") == "expense"]
        
        if len(expenses) < 5:
            return insights
        
        # Calculate daily averages
        daily_amounts = {}
        for expense in expenses:
            date_key = expense["transaction_date"].strftime("%Y-%m-%d")
            if date_key not in daily_amounts:
                daily_amounts[date_key] = 0
            daily_amounts[date_key] += expense["amount"]
        
        avg_daily = sum(daily_amounts.values()) / len(daily_amounts) if daily_amounts else 0
        
        # Check for high spending days
        high_spending_days = [day for day, amount in daily_amounts.items() if amount > avg_daily * 1.5]
        
        if len(high_spending_days) > 3:
            insights.append({
                "type": "pattern",
                "title": "Pola Pengeluaran Tidak Konsisten",
                "message": f"Kamu memiliki {len(high_spending_days)} hari dengan pengeluaran tinggi bulan ini",
                "priority": "medium",
                "actionable": True,
                "action": "Coba buat budget harian untuk mengontrol pengeluaran"
            })
        
        return insights
    
    async def _analyze_budget_adherence(self, student: Dict, transactions: List[Dict]) -> List[Dict]:
        """Analyze budget adherence"""
        insights = []
        
        monthly_allowance = student.get("profile", {}).get("monthly_allowance", 0)
        if monthly_allowance <= 0:
            return insights
        
        # Calculate monthly expenses
        expenses = [t for t in transactions if t.get("type") == "expense"]
        total_expenses = sum(e["amount"] for e in expenses)
        
        budget_usage = (total_expenses / monthly_allowance) * 100
        
        if budget_usage > 90:
            insights.append({
                "type": "budget",
                "title": "Budget Hampir Habis",
                "message": f"Kamu sudah menggunakan {budget_usage:.1f}% dari budget bulanan",
                "priority": "high",
                "actionable": True,
                "action": "Batasi pengeluaran untuk kategori non-essential"
            })
        elif budget_usage > 75:
            insights.append({
                "type": "budget", 
                "title": "Budget Warning",
                "message": f"Penggunaan budget sudah mencapai {budget_usage:.1f}%",
                "priority": "medium",
                "actionable": True,
                "action": "Monitor pengeluaran lebih ketat"
            })
        
        return insights
    
    async def _analyze_category_trends(self, db: AsyncIOMotorDatabase, transactions: List[Dict]) -> List[Dict]:
        """Analyze category spending trends"""
        insights = []
        
        expenses = [t for t in transactions if t.get("type") == "expense"]
        if len(expenses) < 5:
            return insights
        
        # Group by category
        category_totals = {}
        for expense in expenses:
            cat_id = expense.get("category_id")
            if cat_id:
                if cat_id not in category_totals:
                    category_totals[cat_id] = 0
                category_totals[cat_id] += expense["amount"]
        
        # Get top category
        if category_totals:
            top_category_id = max(category_totals, key=category_totals.get)
            top_amount = category_totals[top_category_id]
            total_expenses = sum(category_totals.values())
            
            if top_amount > total_expenses * 0.4:  # More than 40% in one category
                category = await db.categories.find_one({"_id": top_category_id})
                category_name = category.get("name", "Unknown") if category else "Unknown"
                
                insights.append({
                    "type": "category",
                    "title": "Dominasi Kategori Pengeluaran",
                    "message": f"Kategori '{category_name}' menghabiskan {(top_amount/total_expenses)*100:.1f}% budget",
                    "priority": "medium",
                    "actionable": True,
                    "action": f"Pertimbangkan untuk mengurangi pengeluaran di kategori {category_name}"
                })
        
        return insights
    
    async def _generate_academic_insights(self, student: Dict, transactions: List[Dict]) -> List[Dict]:
        """Generate academic calendar-based insights"""
        insights = []
        
        profile = student.get("profile", {})
        semester = profile.get("semester", 0)
        
        # Check if it's exam period (basic logic)
        now = datetime.utcnow()
        month = now.month
        
        # Assuming exam periods are around month 6 (June) and 12 (December)
        if month in [5, 6, 11, 12]:
            expenses = [t for t in transactions if t.get("type") == "expense"]
            entertainment_keywords = ["hiburan", "entertainment", "game", "movie"]
            
            entertainment_expenses = []
            for expense in expenses:
                title = expense.get("title", "").lower()
                if any(keyword in title for keyword in entertainment_keywords):
                    entertainment_expenses.append(expense)
            
            if entertainment_expenses:
                total_entertainment = sum(e["amount"] for e in entertainment_expenses)
                insights.append({
                    "type": "academic",
                    "title": "Periode Ujian - Fokus Belajar",
                    "message": f"Pengeluaran hiburan Rp {total_entertainment:,.0f} selama periode ujian",
                    "priority": "medium",
                    "actionable": True,
                    "action": "Kurangi pengeluaran hiburan untuk fokus belajar dan menghemat"
                })
        
        return insights