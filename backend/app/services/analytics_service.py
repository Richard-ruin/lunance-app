# app/services/analytics_service.py
"""Analytics service for data preparation and financial analysis."""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple
from bson import ObjectId

from ..config.database import get_database
from ..services.transaction_service import transaction_service
from ..services.savings_target_service import savings_target_service

logger = logging.getLogger(__name__)


class AnalyticsServiceError(Exception):
    """Analytics service related error."""
    pass


class AnalyticsService:
    """Service for financial data analytics and preparation."""
    
    def __init__(self):
        self.analytics_cache_collection = "analytics_cache"
    
    async def prepare_prediction_data(
        self,
        user_id: str,
        data_type: str,
        category_id: Optional[str] = None,
        lookback_months: int = 24
    ) -> pd.DataFrame:
        """Prepare data for machine learning predictions."""
        try:
            if data_type == "income":
                data = await self._prepare_income_data(user_id, lookback_months)
            elif data_type == "expense":
                data = await self._prepare_expense_data(user_id, category_id, lookback_months)
            elif data_type == "savings":
                data = await self._prepare_savings_data(user_id, lookback_months)
            elif data_type == "category":
                if not category_id:
                    raise AnalyticsServiceError("Category ID required for category analysis")
                data = await self._prepare_category_data(user_id, category_id, lookback_months)
            else:
                raise AnalyticsServiceError(f"Unsupported data type: {data_type}")
            
            # Clean and validate data
            data = self._clean_financial_data(data)
            
            # Add time-based features
            data = self._add_time_features(data)
            
            # Add trend features
            data = self._add_trend_features(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error preparing prediction data: {e}")
            raise AnalyticsServiceError(f"Failed to prepare {data_type} data")
    
    async def analyze_spending_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze comprehensive spending patterns."""
        try:
            # Get transaction data for analysis
            end_date = date.today()
            start_date = end_date - timedelta(days=365)  # Last year
            
            # Get all transactions
            transactions = await self._get_transaction_data(
                user_id, start_date, end_date
            )
            
            if transactions.empty:
                return {"status": "no_data", "message": "Insufficient transaction data"}
            
            # Analyze patterns
            patterns = {}
            
            # Monthly patterns
            patterns["monthly"] = self._analyze_monthly_patterns(transactions)
            
            # Weekly patterns
            patterns["weekly"] = self._analyze_weekly_patterns(transactions)
            
            # Category patterns
            patterns["categories"] = self._analyze_category_patterns(transactions)
            
            # Seasonal patterns
            patterns["seasonal"] = self._analyze_seasonal_patterns(transactions)
            
            # Anomaly detection
            patterns["anomalies"] = self._detect_spending_anomalies(transactions)
            
            # Trend analysis
            patterns["trends"] = self._analyze_spending_trends(transactions)
            
            return {
                "status": "success",
                "analysis_date": datetime.utcnow().isoformat(),
                "data_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "transaction_count": len(transactions)
                },
                "patterns": patterns
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spending patterns: {e}")
            return {"status": "error", "message": str(e)}
    
    async def calculate_financial_health_score(self, user_id: str) -> Dict[str, Any]:
        """Calculate comprehensive financial health score."""
        try:
            # Get user's financial data
            from ..services.user_service import user_service
            user_stats = await user_service.get_user_stats(user_id)
            
            if not user_stats:
                return {"score": 0, "status": "no_data"}
            
            # Initialize score components
            scores = {}
            
            # 1. Savings Rate Score (25%)
            savings_rate = self._calculate_savings_rate(user_stats)
            scores["savings_rate"] = self._score_savings_rate(savings_rate)
            
            # 2. Emergency Fund Score (20%)
            emergency_fund_ratio = user_stats.current_balance / (user_stats.total_expense / 12) if user_stats.total_expense > 0 else 0
            scores["emergency_fund"] = self._score_emergency_fund(emergency_fund_ratio)
            
            # 3. Spending Consistency Score (20%)
            spending_consistency = await self._calculate_spending_consistency(user_id)
            scores["spending_consistency"] = spending_consistency
            
            # 4. Goal Progress Score (20%)
            goal_progress = await self._calculate_goal_progress_score(user_id)
            scores["goal_progress"] = goal_progress
            
            # 5. Financial Behavior Score (15%)
            behavior_score = await self._calculate_behavior_score(user_id)
            scores["financial_behavior"] = behavior_score
            
            # Calculate weighted overall score
            weights = {
                "savings_rate": 0.25,
                "emergency_fund": 0.20,
                "spending_consistency": 0.20,
                "goal_progress": 0.20,
                "financial_behavior": 0.15
            }
            
            overall_score = sum(scores[component] * weights[component] for component in scores)
            overall_score = round(min(100, max(0, overall_score)), 1)
            
            # Determine health level
            if overall_score >= 80:
                health_level = "excellent"
            elif overall_score >= 60:
                health_level = "good"
            elif overall_score >= 40:
                health_level = "fair"
            else:
                health_level = "needs_improvement"
            
            # Generate recommendations
            recommendations = self._generate_health_recommendations(scores, overall_score)
            
            return {
                "overall_score": overall_score,
                "health_level": health_level,
                "component_scores": scores,
                "recommendations": recommendations,
                "calculation_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating financial health score: {e}")
            return {"score": 0, "status": "error", "message": str(e)}
    
    async def generate_spending_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate actionable spending insights."""
        try:
            insights = []
            
            # Get recent spending data
            end_date = date.today()
            start_date = end_date - timedelta(days=90)  # Last 3 months
            
            transactions = await self._get_transaction_data(user_id, start_date, end_date, "expense")
            
            if transactions.empty:
                return insights
            
            # Insight 1: Top spending categories
            category_analysis = self._analyze_category_spending(transactions)
            if category_analysis:
                insights.append({
                    "type": "category_analysis",
                    "title": "Kategori Pengeluaran Terbesar",
                    "description": f"Anda menghabiskan {category_analysis['top_percentage']:.1f}% dari total pengeluaran untuk {category_analysis['top_category']}",
                    "data": category_analysis,
                    "priority": "high" if category_analysis['top_percentage'] > 40 else "medium"
                })
            
            # Insight 2: Spending trend
            trend_analysis = self._analyze_recent_trend(transactions)
            if trend_analysis:
                insights.append({
                    "type": "trend_analysis",
                    "title": "Tren Pengeluaran",
                    "description": f"Pengeluaran Anda {trend_analysis['trend_description']} sebesar {abs(trend_analysis['change_percentage']):.1f}%",
                    "data": trend_analysis,
                    "priority": "high" if abs(trend_analysis['change_percentage']) > 20 else "medium"
                })
            
            # Insight 3: Unusual spending patterns
            unusual_patterns = self._detect_unusual_patterns(transactions)
            for pattern in unusual_patterns:
                insights.append({
                    "type": "unusual_pattern",
                    "title": "Pola Pengeluaran Tidak Biasa",
                    "description": pattern["description"],
                    "data": pattern,
                    "priority": "medium"
                })
            
            # Insight 4: Savings opportunity
            savings_opportunity = self._identify_savings_opportunities(transactions)
            if savings_opportunity:
                insights.append({
                    "type": "savings_opportunity",
                    "title": "Peluang Menghemat",
                    "description": savings_opportunity["description"],
                    "data": savings_opportunity,
                    "priority": "medium"
                })
            
            # Sort by priority
            priority_order = {"high": 3, "medium": 2, "low": 1}
            insights.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
            
            return insights[:5]  # Return top 5 insights
            
        except Exception as e:
            logger.error(f"Error generating spending insights: {e}")
            return []
    
    async def create_budget_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Create personalized budget recommendations."""
        try:
            # Get user's income and expense data
            from ..services.user_service import user_service
            user_stats = await user_service.get_user_stats(user_id)
            
            if not user_stats:
                return {"status": "no_data"}
            
            # Calculate monthly averages
            monthly_income = user_stats.total_income / 12 if user_stats.total_income > 0 else 0
            monthly_expense = user_stats.total_expense / 12 if user_stats.total_expense > 0 else 0
            
            # Get category breakdown
            category_summary = await transaction_service.get_category_summary(user_id)
            
            # Create budget recommendations based on 50/30/20 rule
            recommendations = {
                "total_income": monthly_income,
                "current_expense": monthly_expense,
                "recommended_budget": {},
                "adjustments": []
            }
            
            # 50/30/20 allocation
            needs_budget = monthly_income * 0.5
            wants_budget = monthly_income * 0.3
            savings_budget = monthly_income * 0.2
            
            recommendations["recommended_budget"] = {
                "needs": needs_budget,
                "wants": wants_budget,
                "savings": savings_budget
            }
            
            # Categorize current spending
            needs_categories = ["Food & Dining", "Transportation", "Bills & Utilities", "Healthcare"]
            wants_categories = ["Entertainment", "Shopping", "Travel"]
            
            current_needs = sum(
                cat.total_amount for cat in category_summary 
                if cat.category_name in needs_categories
            )
            current_wants = sum(
                cat.total_amount for cat in category_summary 
                if cat.category_name in wants_categories
            )
            
            # Generate adjustments
            if current_needs > needs_budget:
                recommendations["adjustments"].append({
                    "type": "reduce_needs",
                    "description": f"Kurangi pengeluaran kebutuhan sebesar Rp {current_needs - needs_budget:,.0f}",
                    "amount": current_needs - needs_budget
                })
            
            if current_wants > wants_budget:
                recommendations["adjustments"].append({
                    "type": "reduce_wants",
                    "description": f"Kurangi pengeluaran keinginan sebesar Rp {current_wants - wants_budget:,.0f}",
                    "amount": current_wants - wants_budget
                })
            
            # Category-specific recommendations
            category_recommendations = []
            for cat in category_summary[:3]:  # Top 3 categories
                if cat.percentage > 30:
                    category_recommendations.append({
                        "category": cat.category_name,
                        "current_amount": cat.total_amount,
                        "recommended_amount": cat.total_amount * 0.8,  # Reduce by 20%
                        "savings_potential": cat.total_amount * 0.2
                    })
            
            recommendations["category_recommendations"] = category_recommendations
            
            return {
                "status": "success",
                "recommendations": recommendations,
                "created_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating budget recommendations: {e}")
            return {"status": "error", "message": str(e)}
    
    # Private helper methods
    async def _prepare_income_data(self, user_id: str, lookback_months: int) -> pd.DataFrame:
        """Prepare income data for analysis."""
        try:
            db = await get_database()
            collection = db.transactions
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=lookback_months * 30)
            
            # Aggregate monthly income
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "transaction_type": "income",
                        "transaction_date": {"$gte": start_date, "$lte": end_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$transaction_date"},
                            "month": {"$month": "$transaction_date"}
                        },
                        "amount": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1}
                    }
                },
                {
                    "$addFields": {
                        "date": {
                            "$dateFromParts": {
                                "year": "$_id.year",
                                "month": "$_id.month",
                                "day": 1
                            }
                        }
                    }
                },
                {"$sort": {"date": 1}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(None)
            
            # Convert to DataFrame
            data = [{
                "date": doc["date"],
                "amount": doc["amount"],
                "transaction_count": doc["transaction_count"]
            } for doc in result]
            
            df = pd.DataFrame(data)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error preparing income data: {e}")
            return pd.DataFrame()
    
    async def _prepare_expense_data(self, user_id: str, category_id: Optional[str], lookback_months: int) -> pd.DataFrame:
        """Prepare expense data for analysis."""
        try:
            db = await get_database()
            collection = db.transactions
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=lookback_months * 30)
            
            # Build match criteria
            match_criteria = {
                "user_id": user_id,
                "transaction_type": "expense",
                "transaction_date": {"$gte": start_date, "$lte": end_date}
            }
            
            if category_id:
                match_criteria["category_id"] = category_id
            
            # Aggregate monthly expenses
            pipeline = [
                {"$match": match_criteria},
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$transaction_date"},
                            "month": {"$month": "$transaction_date"}
                        },
                        "amount": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1}
                    }
                },
                {
                    "$addFields": {
                        "date": {
                            "$dateFromParts": {
                                "year": "$_id.year",
                                "month": "$_id.month",
                                "day": 1
                            }
                        }
                    }
                },
                {"$sort": {"date": 1}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(None)
            
            # Convert to DataFrame
            data = [{
                "date": doc["date"],
                "amount": doc["amount"],
                "transaction_count": doc["transaction_count"]
            } for doc in result]
            
            df = pd.DataFrame(data)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error preparing expense data: {e}")
            return pd.DataFrame()
    
    async def _prepare_savings_data(self, user_id: str, lookback_months: int) -> pd.DataFrame:
        """Prepare savings data for analysis."""
        try:
            # Get income and expense data
            income_df = await self._prepare_income_data(user_id, lookback_months)
            expense_df = await self._prepare_expense_data(user_id, None, lookback_months)
            
            if income_df.empty or expense_df.empty:
                return pd.DataFrame()
            
            # Merge income and expense data
            merged_df = pd.merge(
                income_df[['date', 'amount']].rename(columns={'amount': 'income'}),
                expense_df[['date', 'amount']].rename(columns={'amount': 'expense'}),
                on='date',
                how='outer'
            ).fillna(0)
            
            # Calculate savings
            merged_df['amount'] = merged_df['income'] - merged_df['expense']
            merged_df['savings_rate'] = merged_df['amount'] / merged_df['income'].replace(0, np.nan)
            
            return merged_df[['date', 'amount', 'savings_rate']].dropna()
            
        except Exception as e:
            logger.error(f"Error preparing savings data: {e}")
            return pd.DataFrame()
    
    async def _prepare_category_data(self, user_id: str, category_id: str, lookback_months: int) -> pd.DataFrame:
        """Prepare category-specific data for analysis."""
        return await self._prepare_expense_data(user_id, category_id, lookback_months)
    
    def _clean_financial_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate financial data."""
        if df.empty:
            return df
        
        # Remove negative amounts for income/expense (should not happen)
        df = df[df['amount'] >= 0].copy()
        
        # Remove outliers (amounts more than 3 standard deviations from mean)
        if len(df) > 10:
            mean_amount = df['amount'].mean()
            std_amount = df['amount'].std()
            lower_bound = mean_amount - 3 * std_amount
            upper_bound = mean_amount + 3 * std_amount
            df = df[(df['amount'] >= lower_bound) & (df['amount'] <= upper_bound)]
        
        # Fill missing dates with zero amounts
        if 'date' in df.columns and len(df) > 1:
            df = df.set_index('date').resample('M').sum().fillna(0).reset_index()
        
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features to the dataset."""
        if df.empty or 'date' not in df.columns:
            return df
        
        df = df.copy()
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['year'] = df['date'].dt.year
        df['days_since_start'] = (df['date'] - df['date'].min()).dt.days
        
        return df
    
    def _add_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add trend-based features to the dataset."""
        if df.empty or len(df) < 2:
            return df
        
        df = df.copy()
        
        # Moving averages
        df['ma_3'] = df['amount'].rolling(window=3, min_periods=1).mean()
        df['ma_6'] = df['amount'].rolling(window=6, min_periods=1).mean()
        
        # Lag features
        df['amount_lag_1'] = df['amount'].shift(1)
        df['amount_lag_3'] = df['amount'].shift(3)
        
        # Percentage change
        df['pct_change'] = df['amount'].pct_change()
        
        return df.fillna(0)
    
    async def _get_transaction_data(
        self,
        user_id: str,
        start_date: date,
        end_date: date,
        transaction_type: Optional[str] = None
    ) -> pd.DataFrame:
        """Get transaction data as DataFrame."""
        try:
            db = await get_database()
            collection = db.transactions
            
            # Build query
            query = {
                "user_id": user_id,
                "transaction_date": {"$gte": start_date, "$lte": end_date}
            }
            
            if transaction_type:
                query["transaction_type"] = transaction_type
            
            # Get transactions with category info
            pipeline = [
                {"$match": query},
                {
                    "$lookup": {
                        "from": "categories",
                        "localField": "category_id",
                        "foreignField": "_id",
                        "as": "category"
                    }
                },
                {"$unwind": "$category"},
                {
                    "$project": {
                        "date": "$transaction_date",
                        "amount": 1,
                        "type": "$transaction_type",
                        "category_name": "$category.name",
                        "description": 1,
                        "created_at": 1
                    }
                },
                {"$sort": {"date": 1}}
            ]
            
            result = await collection.aggregate(pipeline).to_list(None)
            
            # Convert to DataFrame
            df = pd.DataFrame(result)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df['day_of_week'] = df['date'].dt.dayofweek
                df['month'] = df['date'].dt.month
                df['week_of_year'] = df['date'].dt.isocalendar().week
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting transaction data: {e}")
            return pd.DataFrame()
    
    def _calculate_savings_rate(self, user_stats) -> float:
        """Calculate savings rate from user stats."""
        if user_stats.total_income == 0:
            return 0
        
        savings = user_stats.total_income - user_stats.total_expense
        return savings / user_stats.total_income
    
    def _score_savings_rate(self, savings_rate: float) -> float:
        """Score savings rate (0-100)."""
        if savings_rate >= 0.3:  # 30% or more
            return 100
        elif savings_rate >= 0.2:  # 20-30%
            return 80
        elif savings_rate >= 0.1:  # 10-20%
            return 60
        elif savings_rate >= 0.05:  # 5-10%
            return 40
        elif savings_rate >= 0:  # 0-5%
            return 20
        else:  # Negative savings rate
            return 0
    
    def _score_emergency_fund(self, fund_ratio: float) -> float:
        """Score emergency fund adequacy (0-100)."""
        if fund_ratio >= 6:  # 6+ months of expenses
            return 100
        elif fund_ratio >= 3:  # 3-6 months
            return 80
        elif fund_ratio >= 1:  # 1-3 months
            return 60
        elif fund_ratio >= 0.5:  # 2 weeks - 1 month
            return 40
        elif fund_ratio > 0:  # Some emergency fund
            return 20
        else:  # No emergency fund
            return 0
    
    async def _calculate_spending_consistency(self, user_id: str) -> float:
        """Calculate spending consistency score (0-100)."""
        try:
            # Get last 6 months of data
            monthly_summary = await transaction_service.get_monthly_summary(
                user_id=user_id,
                limit=6
            )
            
            if len(monthly_summary) < 3:
                return 50  # Default score for insufficient data
            
            expenses = [month.total_expense for month in monthly_summary]
            
            # Calculate coefficient of variation
            mean_expense = np.mean(expenses)
            std_expense = np.std(expenses)
            
            if mean_expense == 0:
                return 0
            
            cv = std_expense / mean_expense
            
            # Convert to consistency score (lower variation = higher score)
            consistency_score = max(0, 100 - (cv * 100))
            return min(100, consistency_score)
            
        except Exception as e:
            logger.error(f"Error calculating spending consistency: {e}")
            return 50
    
    async def _calculate_goal_progress_score(self, user_id: str) -> float:
        """Calculate goal progress score (0-100)."""
        try:
            # Get savings targets
            from ..models.common import PaginationParams
            targets_result = await savings_target_service.list_savings_targets(
                user_id=user_id,
                pagination=PaginationParams(page=1, per_page=20),
                is_achieved=None
            )
            
            if not targets_result.items:
                return 0  # No goals set
            
            total_targets = len(targets_result.items)
            achieved_targets = sum(1 for target in targets_result.items if target.is_achieved)
            
            # Calculate average progress of active targets
            active_targets = [target for target in targets_result.items if not target.is_achieved]
            
            if active_targets:
                avg_progress = sum(target.progress_percentage for target in active_targets) / len(active_targets)
            else:
                avg_progress = 100  # All targets achieved
            
            # Combine achievement rate and progress
            achievement_rate = (achieved_targets / total_targets) * 100
            progress_score = (achievement_rate * 0.6) + (avg_progress * 0.4)
            
            return min(100, progress_score)
            
        except Exception as e:
            logger.error(f"Error calculating goal progress score: {e}")
            return 0
    
    async def _calculate_behavior_score(self, user_id: str) -> float:
        """Calculate financial behavior score (0-100)."""
        try:
            # Get recent transaction data
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
            
            transactions = await self._get_transaction_data(user_id, start_date, end_date)
            
            if transactions.empty:
                return 50
            
            behavior_score = 50  # Base score
            
            # Regular transaction pattern (bonus for consistency)
            if len(transactions) > 10:
                # Check for regular transactions
                daily_counts = transactions.groupby(transactions['date'].dt.date).size()
                consistency_bonus = min(20, len(daily_counts) * 2)  # Up to 20 points
                behavior_score += consistency_bonus
            
            # Category diversification (bonus for balanced spending)
            category_counts = transactions['category_name'].nunique()
            if category_counts >= 5:
                behavior_score += 15
            elif category_counts >= 3:
                behavior_score += 10
            
            # Transaction descriptions (bonus for detailed tracking)
            detailed_transactions = sum(1 for desc in transactions['description'] if len(desc.strip()) > 10)
            detail_ratio = detailed_transactions / len(transactions)
            behavior_score += detail_ratio * 15
            
            return min(100, behavior_score)
            
        except Exception as e:
            logger.error(f"Error calculating behavior score: {e}")
            return 50
    
    def _generate_health_recommendations(self, scores: Dict[str, float], overall_score: float) -> List[str]:
        """Generate recommendations based on financial health scores."""
        recommendations = []
        
        # Savings rate recommendations
        if scores["savings_rate"] < 60:
            recommendations.append("Tingkatkan tingkat tabungan Anda dengan menerapkan aturan 50/30/20 untuk alokasi keuangan.")
        
        # Emergency fund recommendations
        if scores["emergency_fund"] < 60:
            recommendations.append("Bangun dana darurat yang setara dengan 3-6 bulan pengeluaran untuk stabilitas keuangan.")
        
        # Spending consistency recommendations
        if scores["spending_consistency"] < 70:
            recommendations.append("Buat anggaran bulanan untuk meningkatkan konsistensi pengeluaran.")
        
        # Goal progress recommendations
        if scores["goal_progress"] < 50:
            recommendations.append("Tetapkan target tabungan yang realistis dan pantau progress secara rutin.")
        
        # Behavior recommendations
        if scores["financial_behavior"] < 60:
            recommendations.append("Tingkatkan kebiasaan pencatatan keuangan dengan mencatat setiap transaksi secara detail.")
        
        # Overall recommendations
        if overall_score < 40:
            recommendations.insert(0, "Fokus pada dasar-dasar manajemen keuangan: buat anggaran, kurangi pengeluaran, dan mulai menabung.")
        elif overall_score < 70:
            recommendations.insert(0, "Keuangan Anda sudah cukup baik, saatnya untuk optimisasi dan perencanaan jangka panjang.")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _analyze_monthly_patterns(self, transactions: pd.DataFrame) -> Dict[str, Any]:
        """Analyze monthly spending patterns."""
        try:
            monthly_data = transactions.groupby('month').agg({
                'amount': ['sum', 'mean', 'count']
            }).round(2)
            
            monthly_data.columns = ['total', 'average', 'count']
            
            # Find peak and low months
            peak_month = monthly_data['total'].idxmax()
            low_month = monthly_data['total'].idxmin()
            
            return {
                "monthly_totals": monthly_data['total'].to_dict(),
                "peak_month": int(peak_month),
                "low_month": int(low_month),
                "variation_coefficient": float(monthly_data['total'].std() / monthly_data['total'].mean())
            }
            
        except Exception as e:
            logger.error(f"Error analyzing monthly patterns: {e}")
            return {}
    
    def _analyze_weekly_patterns(self, transactions: pd.DataFrame) -> Dict[str, Any]:
        """Analyze weekly spending patterns."""
        try:
            # Map day of week to names
            day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 
                        4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
            
            weekly_data = transactions.groupby('day_of_week').agg({
                'amount': ['sum', 'mean', 'count']
            }).round(2)
            
            weekly_data.columns = ['total', 'average', 'count']
            weekly_data.index = weekly_data.index.map(day_names)
            
            # Find peak spending day
            peak_day = weekly_data['total'].idxmax()
            
            return {
                "daily_totals": weekly_data['total'].to_dict(),
                "peak_day": peak_day,
                "weekend_vs_weekday": {
                    "weekend": float(weekly_data.loc[['Saturday', 'Sunday'], 'total'].sum()),
                    "weekday": float(weekly_data.loc[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], 'total'].sum())
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing weekly patterns: {e}")
            return {}
    
    def _analyze_category_patterns(self, transactions: pd.DataFrame) -> Dict[str, Any]:
        """Analyze category spending patterns."""
        try:
            category_data = transactions.groupby('category_name').agg({
                'amount': ['sum', 'mean', 'count']
            }).round(2)
            
            category_data.columns = ['total', 'average', 'count']
            category_data = category_data.sort_values('total', ascending=False)
            
            # Calculate percentages
            total_spending = category_data['total'].sum()
            category_data['percentage'] = (category_data['total'] / total_spending * 100).round(2)
            
            return {
                "category_breakdown": category_data.to_dict(),
                "top_category": category_data.index[0],
                "concentration_ratio": float(category_data['percentage'].iloc[:3].sum())  # Top 3 categories
            }
            
        except Exception as e:
            logger.error(f"Error analyzing category patterns: {e}")
            return {}
    
    def _analyze_seasonal_patterns(self, transactions: pd.DataFrame) -> Dict[str, Any]:
        """Analyze seasonal spending patterns."""
        try:
            # Group by quarter
            quarterly_data = transactions.groupby('month').agg({
                'amount': 'sum'
            }).round(2)
            
            # Map months to quarters
            quarter_mapping = {1: 'Q1', 2: 'Q1', 3: 'Q1', 4: 'Q2', 5: 'Q2', 6: 'Q2',
                             7: 'Q3', 8: 'Q3', 9: 'Q3', 10: 'Q4', 11: 'Q4', 12: 'Q4'}
            
            quarterly_totals = {}
            for month, amount in quarterly_data['amount'].items():
                quarter = quarter_mapping[month]
                quarterly_totals[quarter] = quarterly_totals.get(quarter, 0) + amount
            
            # Find seasonal peaks
            peak_quarter = max(quarterly_totals, key=quarterly_totals.get)
            
            return {
                "quarterly_totals": quarterly_totals,
                "peak_quarter": peak_quarter,
                "seasonality_index": max(quarterly_totals.values()) / min(quarterly_totals.values()) if quarterly_totals and min(quarterly_totals.values()) > 0 else 1
            }
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal patterns: {e}")
            return {}
    
    def _detect_spending_anomalies(self, transactions: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect spending anomalies."""
        try:
            anomalies = []
            
            if len(transactions) < 10:
                return anomalies
            
            # Calculate Z-scores for transaction amounts
            mean_amount = transactions['amount'].mean()
            std_amount = transactions['amount'].std()
            
            if std_amount > 0:
                transactions['z_score'] = (transactions['amount'] - mean_amount) / std_amount
                
                # Flag transactions with |z_score| > 2.5 as anomalies
                anomalous_transactions = transactions[abs(transactions['z_score']) > 2.5]
                
                for _, transaction in anomalous_transactions.iterrows():
                    anomalies.append({
                        "date": transaction['date'].strftime('%Y-%m-%d'),
                        "amount": float(transaction['amount']),
                        "category": transaction['category_name'],
                        "description": transaction['description'],
                        "z_score": float(transaction['z_score']),
                        "type": "high_amount" if transaction['z_score'] > 0 else "low_amount"
                    })
            
            return anomalies[:5]  # Return top 5 anomalies
            
        except Exception as e:
            logger.error(f"Error detecting spending anomalies: {e}")
            return []
    
    def _analyze_spending_trends(self, transactions: pd.DataFrame) -> Dict[str, Any]:
        """Analyze spending trends over time."""
        try:
            # Group by month-year
            monthly_spending = transactions.groupby(
                transactions['date'].dt.to_period('M')
            )['amount'].sum().reset_index()
            
            if len(monthly_spending) < 2:
                return {"trend": "insufficient_data"}
            
            monthly_spending['date'] = monthly_spending['date'].dt.to_timestamp()
            monthly_spending = monthly_spending.sort_values('date')
            
            # Calculate linear trend
            from scipy import stats
            x = np.arange(len(monthly_spending))
            y = monthly_spending['amount'].values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Determine trend direction
            if slope > 0 and p_value < 0.05:
                trend_direction = "increasing"
            elif slope < 0 and p_value < 0.05:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
            
            # Calculate monthly growth rate
            monthly_growth_rates = monthly_spending['amount'].pct_change().dropna()
            avg_growth_rate = monthly_growth_rates.mean() * 100
            
            return {
                "trend": trend_direction,
                "slope": float(slope),
                "r_squared": float(r_value ** 2),
                "avg_monthly_growth_rate": float(avg_growth_rate),
                "trend_strength": "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.4 else "weak"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spending trends: {e}")
            return {"trend": "unknown"}
    
    def _analyze_category_spending(self, transactions: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Analyze category spending for insights."""
        try:
            if transactions.empty:
                return None
            
            category_totals = transactions.groupby('category_name')['amount'].sum().sort_values(ascending=False)
            total_spending = category_totals.sum()
            
            top_category = category_totals.index[0]
            top_percentage = (category_totals.iloc[0] / total_spending) * 100
            
            return {
                "top_category": top_category,
                "top_amount": float(category_totals.iloc[0]),
                "top_percentage": float(top_percentage),
                "category_distribution": category_totals.head(5).to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing category spending: {e}")
            return None
    
    def _analyze_recent_trend(self, transactions: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Analyze recent spending trend."""
        try:
            if len(transactions) < 30:  # Need at least 30 days of data
                return None
            
            # Split into recent and previous periods
            mid_point = len(transactions) // 2
            recent_transactions = transactions.iloc[mid_point:]
            previous_transactions = transactions.iloc[:mid_point]
            
            recent_total = recent_transactions['amount'].sum()
            previous_total = previous_transactions['amount'].sum()
            
            if previous_total == 0:
                return None
            
            change_percentage = ((recent_total - previous_total) / previous_total) * 100
            
            if change_percentage > 10:
                trend_description = "meningkat"
            elif change_percentage < -10:
                trend_description = "menurun"
            else:
                trend_description = "stabil"
            
            return {
                "change_percentage": float(change_percentage),
                "trend_description": trend_description,
                "recent_total": float(recent_total),
                "previous_total": float(previous_total)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing recent trend: {e}")
            return None
    
    def _detect_unusual_patterns(self, transactions: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect unusual spending patterns."""
        patterns = []
        
        try:
            # Pattern 1: Sudden spike in a specific category
            category_daily = transactions.groupby(['date', 'category_name'])['amount'].sum().reset_index()
            
            for category in transactions['category_name'].unique():
                category_data = category_daily[category_daily['category_name'] == category]['amount']
                
                if len(category_data) > 5:
                    mean_amount = category_data.mean()
                    std_amount = category_data.std()
                    
                    if std_amount > 0:
                        max_amount = category_data.max()
                        z_score = (max_amount - mean_amount) / std_amount
                        
                        if z_score > 3:  # Very unusual spike
                            patterns.append({
                                "type": "category_spike",
                                "description": f"Pengeluaran tidak biasa tinggi untuk kategori {category}",
                                "category": category,
                                "amount": float(max_amount),
                                "normal_average": float(mean_amount)
                            })
            
            # Pattern 2: Weekend vs weekday unusual spending
            weekend_avg = transactions[transactions['day_of_week'].isin([5, 6])]['amount'].mean()
            weekday_avg = transactions[~transactions['day_of_week'].isin([5, 6])]['amount'].mean()
            
            if weekend_avg > weekday_avg * 2:
                patterns.append({
                    "type": "weekend_spending",
                    "description": "Pengeluaran weekend jauh lebih tinggi dari hari kerja",
                    "weekend_average": float(weekend_avg),
                    "weekday_average": float(weekday_avg)
                })
            
            return patterns[:3]  # Return top 3 patterns
            
        except Exception as e:
            logger.error(f"Error detecting unusual patterns: {e}")
            return []
    
    def _identify_savings_opportunities(self, transactions: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Identify potential savings opportunities."""
        try:
            if transactions.empty:
                return None
            
            # Look for high-frequency, low-value transactions that could be optimized
            daily_spending = transactions.groupby('date')['amount'].sum()
            avg_daily_spending = daily_spending.mean()
            
            # Check for categories with high frequency but individual amounts could be reduced
            category_analysis = transactions.groupby('category_name').agg({
                'amount': ['sum', 'mean', 'count']
            })
            category_analysis.columns = ['total', 'average', 'count']
            category_analysis['potential_savings'] = category_analysis['total'] * 0.1  # Assume 10% reduction possible
            
            top_opportunity = category_analysis.sort_values('potential_savings', ascending=False).iloc[0]
            
            return {
                "description": f"Potensi hemat Rp {top_opportunity['potential_savings']:,.0f} per bulan dari kategori {category_analysis.index[0]}",
                "category": category_analysis.index[0],
                "current_spending": float(top_opportunity['total']),
                "potential_savings": float(top_opportunity['potential_savings']),
                "reduction_percentage": 10
            }
            
        except Exception as e:
            logger.error(f"Error identifying savings opportunities: {e}")
            return None


# Global analytics service instance
analytics_service = AnalyticsService()