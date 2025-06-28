# app/services/nlp/response_templates.py
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from backend.app.models.user import Student
from app.models.chat import ChatResponse, DataUsed
from app.models.transaction import TransactionFilter
from app.utils.currency_formatter import format_idr, format_percentage_id
from app.config.database import get_database
from app.api.v1.transactions.crud import TransactionCRUD

logger = logging.getLogger(__name__)

class ResponseTemplateService:
    """Service for generating contextual responses to student queries"""
    
    def __init__(self):
        self.response_templates = {
            'greeting': [
                "Halo {name}! 👋 Saya Lunance AI, siap membantu mengelola keuangan kamu. Ada yang bisa saya bantu hari ini?",
                "Hi {name}! Selamat datang kembali di Lunance! 😊 Mau cek keuangan atau ada pertanyaan lain?",
                "Hai {name}! Gimana kabarnya? Ada yang mau ditanyakan soal keuangan hari ini? 💰",
                "Selamat datang {name}! Saya di sini untuk membantu mengatur keuangan kamu. Mau mulai dari mana?",
                "Halo {name}! Ready untuk manage keuangan yang lebih baik? Ada yang perlu dibantu? 🚀"
            ],
            
            'balance_info': [
                "Saldo kamu saat ini: {balance}. {status_message}",
                "Total uang kamu sekarang {balance}. {advice}",
                "Balance kamu: {balance}. {insight}",
                "Berdasarkan transaksi terbaru, saldo kamu {balance}. {status_message}",
                "Update saldo: {balance}. {financial_health_status}"
            ],
            
            'expense_summary': [
                "Pengeluaran {period}: {amount}. Kategori terbanyak: {top_category} ({percentage})",
                "Kamu sudah habiskan {amount} {period}. Paling banyak untuk {top_category}",
                "Total spending {period}: {amount}. {top_category} jadi pengeluaran terbesarmu",
                "Summary {period}: keluar {amount}, didominasi {top_category} ({percentage})",
                "Pengeluaran {period} mencapai {amount}. {insight}"
            ],
            
            'budget_advice': [
                "Berdasarkan pola pengeluaran kamu, saya sarankan budget harian sekitar {daily_budget}",
                "Budget yang cocok untuk kamu: {monthly_budget}/bulan atau {daily_budget}/hari",
                "Idealnya kamu punya budget {allocation} untuk setiap kategori",
                "Saran budget: {daily_budget}/hari untuk pengeluaran rutin. {specific_advice}",
                "Budget recommendation: {monthly_budget}/bulan dengan pembagian {allocation}"
            ],
            
            'savings_motivation': [
                "Keren! Target tabungan kamu {progress}% tercapai. Tinggal {remaining} lagi! 🎯",
                "Progress tabungan: {current_amount} dari {target_amount}. Keep going! 💪",
                "Wah, kamu sudah menabung {saved_amount}! Sisanya {remaining} lagi untuk capai target",
                "Amazing! {progress}% dari target tabungan sudah terkumpul. {remaining} lagi sampai finish! 🏆",
                "Great job! Tabungan {current_amount} dari target {target_amount}. {motivation_message}"
            ],
            
            'transaction_help': [
                "Untuk mencatat transaksi baru, gunakan menu 'Tambah Transaksi' di aplikasi ya!",
                "Saya bisa bantu analisa setelah transaksi tercatat. Coba gunakan fitur input transaksi dulu.",
                "Transaksi bisa dicatat langsung di menu utama. Nanti saya bantu analisa pola pengeluarannya!",
                "Pakai fitur 'Add Transaction' untuk catat pengeluaran. Setelah itu saya bisa kasih insight!",
                "Record transaksi dulu di app, baru saya bisa bantu dengan analisa dan tips keuangan."
            ],
            
            'expense_analysis': [
                "Analisis pengeluaran {period}: Total {total}, rata-rata {average}/hari. {insight}",
                "Spending pattern kamu {period}: {breakdown}. {recommendation}",
                "Pengeluaran kamu {period} didominasi {top_category} ({percentage}). {advice}",
                "Breakdown {period}: {total} total, {top_category} paling banyak. {insight}",
                "Pattern analysis: {average}/hari rata-rata, {top_category} kategori tertinggi. {advice}"
            ],
            
            'help_response': [
                "Saya bisa bantu kamu untuk:\n• Cek saldo dan pengeluaran\n• Analisis keuangan\n• Tips budgeting\n• Catat transaksi\n• Planning tabungan",
                "Ada beberapa hal yang bisa saya bantu:\n• Monitor keuangan harian\n• Buat budget yang realistis\n• Track progress tabungan\n• Analisa spending pattern",
                "Lunance AI bisa:\n• Cek balance real-time\n• Breakdown pengeluaran per kategori\n• Kasih saran keuangan personal\n• Bantu planning keuangan jangka panjang",
                "Fitur yang tersedia:\n• Financial monitoring\n• Budget recommendations\n• Savings goal tracking\n• Expense pattern analysis\n• Academic expense planning",
                "Saya siap membantu:\n• Real-time balance check\n• Smart budgeting tips\n• Savings strategies\n• Expense optimization\n• Financial health assessment"
            ],
            
            'academic_expense_advice': [
                "Untuk pengeluaran kuliah, alokasikan sekitar {percentage}% dari budget bulanan kamu",
                "Tips hemat kuliah: Beli buku bekas, fotokopi seperlunya, manfaatin fasilitas kampus gratis",
                "Budget akademik yang ideal: {amount}/semester untuk buku, {lab_fee} untuk lab, sisanya untuk keperluan harian",
                "Academic budgeting: {percentage}% untuk kuliah, sisanya untuk living expenses. {tips}",
                "Semester budgeting: {amount} untuk akademik, termasuk {lab_fee} untuk praktikum dan lab fees"
            ],
            
            'debt_management': [
                "Tips manage hutang: Prioritaskan yang bunga tinggi, buat jadwal pembayaran konsisten",
                "Strategi bayar hutang: List semua hutang, bayar minimum untuk semua, extra payment untuk yang tertinggi bunganya",
                "Debt management: Buat emergency fund dulu, baru fokus bayar hutang dengan metode debt avalanche",
                "Kelola cicilan: Automate pembayaran, track due dates, hindari late fees",
                "Hutang strategy: Consolidate kalau bisa, negotiate payment terms, prioritas berdasarkan interest rate"
            ],
            
            'income_optimization': [
                "Tips tambah income: Part-time job, freelance online, jual skill digital, tutor teman",
                "Income boost for students: Online tutoring, content creation, micro jobs, skill monetization",
                "Cara cari tambahan: Freelance writing, graphic design, programming, data entry",
                "Student income ideas: Campus jobs, delivery driver, online teaching, social media management",
                "Extra money tips: Sell unused items, photography services, translation work, virtual assistant"
            ],
            
            'financial_motivation': [
                "Great job managing your finances! Consistency is key to financial success! 💪",
                "You're on the right track! Small steps lead to big financial wins! 🎯",
                "Keep it up! Every rupiah saved today is an investment in your future! 🚀",
                "Impressive financial discipline! You're building great money habits! 👏",
                "Excellent progress! Your future self will thank you for these smart decisions! 🌟"
            ]
        }
        
        self.error_responses = [
            "Maaf, saya belum bisa memproses permintaan itu. Bisa dijelaskan lebih detail?",
            "Hmm, saya kurang paham. Coba tanya dengan cara lain ya!",
            "Sorry, belum ngerti maksudnya. Mau coba tanya yang lain?",
            "Saya masih belajar untuk pertanyaan ini. Bisa coba dengan cara yang berbeda?",
            "Belum bisa handle pertanyaan itu nih. Ada hal lain yang bisa saya bantu?"
        ]
        
        # Indonesian financial expressions
        self.indonesian_expressions = {
            'positive_balance': [
                "Alhamdulillah masih ada uang nih! 😊",
                "Saldo masih sehat ya!",
                "Good job, masih ada tabungan!",
                "Keuangan terkontrol dengan baik!",
                "Mantap, balance masih positif!"
            ],
            'low_balance': [
                "Wah, tipis nih. Hati-hati pengeluarannya ya!",
                "Saldo hampir habis, time to save more!",
                "Alert! Perlu top up atau kurangi spending",
                "Danger zone! Better watch your expenses",
                "Red alert! Saatnya hemat atau cari tambahan income"
            ],
            'overspending': [
                "Boros nih bulan ini! Time to cut back",
                "Spending over budget, need to adjust habits",
                "Pengeluaran kebanyakan, perlu evaluasi",
                "Budget overrun! Perlu strategi hemat",
                "Keluar budget nih, saatnya kontrol diri"
            ]
        }
    
    async def get_student_financial_data(self, student: Student) -> Dict[str, Any]:
        """Get comprehensive student financial data"""
        try:
            # Get database connection
            db = await get_database()
            transaction_crud = TransactionCRUD(db)
            
            # Date ranges
            today = datetime.utcnow()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Get transactions for the last month
            transactions_response = await transaction_crud.get_transactions(
                student_id=str(student.id),
                filters=TransactionFilter(
                    start_date=month_ago,
                    end_date=today
                ),
                limit=200
            )
            
            recent_transactions = transactions_response["transactions"]
            
            # Calculate financial metrics
            total_income = sum(t.amount for t in recent_transactions if t.type == 'income')
            total_expense = sum(t.amount for t in recent_transactions if t.type == 'expense')
            current_balance = total_income - total_expense
            
            # Period-specific calculations
            week_expenses = sum(
                t.amount for t in recent_transactions 
                if t.type == 'expense' and t.transaction_date >= week_ago
            )
            
            today_expenses = sum(
                t.amount for t in recent_transactions 
                if t.type == 'expense' and t.transaction_date.date() == today.date()
            )
            
            # Get category breakdown
            try:
                category_breakdown = await transaction_crud.get_category_breakdown(
                    student_id=str(student.id),
                    start_date=month_ago,
                    end_date=today,
                    transaction_type="expense"
                )
            except Exception:
                category_breakdown = []
            
            # Process category data
            top_category = None
            category_totals = {}
            
            if category_breakdown:
                top_category = category_breakdown[0]
                category_totals = {cb.category_name: cb.amount for cb in category_breakdown}
            
            # Calculate averages and patterns
            days_in_period = 30
            daily_average = total_expense / days_in_period if total_expense > 0 else 0
            weekly_average = week_expenses / 7 if week_expenses > 0 else 0
            
            # Financial health indicators
            monthly_allowance = student.profile.monthly_allowance or 0
            savings_rate = 0
            if monthly_allowance > 0:
                savings_rate = ((monthly_allowance - total_expense) / monthly_allowance) * 100
            
            # Spending vs budget analysis
            budget_status = "unknown"
            if monthly_allowance > 0:
                if total_expense <= monthly_allowance * 0.7:
                    budget_status = "excellent"
                elif total_expense <= monthly_allowance * 0.85:
                    budget_status = "good"
                elif total_expense <= monthly_allowance:
                    budget_status = "warning"
                else:
                    budget_status = "over_budget"
            
            return {
                'current_balance': current_balance,
                'total_income': total_income,
                'total_expense': total_expense,
                'week_expenses': week_expenses,
                'today_expenses': today_expenses,
                'month_expenses': total_expense,
                'category_totals': category_totals,
                'top_category': top_category.category_name if top_category else 'makanan',
                'top_category_amount': top_category.amount if top_category else 0,
                'top_category_percentage': top_category.percentage if top_category else 0,
                'transaction_count': len(recent_transactions),
                'daily_average': daily_average,
                'weekly_average': weekly_average,
                'savings_rate': savings_rate,
                'budget_status': budget_status,
                'monthly_allowance': monthly_allowance,
                'category_breakdown': category_breakdown
            }
            
        except Exception as e:
            logger.error(f"Error getting financial data: {str(e)}")
            return self._get_default_financial_data()
    
    def _get_default_financial_data(self) -> Dict[str, Any]:
        """Return default financial data structure"""
        return {
            'current_balance': 0,
            'total_income': 0,
            'total_expense': 0,
            'week_expenses': 0,
            'today_expenses': 0,
            'month_expenses': 0,
            'category_totals': {},
            'top_category': 'makanan',
            'top_category_amount': 0,
            'top_category_percentage': 0,
            'transaction_count': 0,
            'daily_average': 0,
            'weekly_average': 0,
            'savings_rate': 0,
            'budget_status': 'unknown',
            'monthly_allowance': 0,
            'category_breakdown': []
        }
    
    def get_financial_health_status(self, financial_data: Dict[str, Any]) -> str:
        """Get financial health status message"""
        balance = financial_data.get('current_balance', 0)
        budget_status = financial_data.get('budget_status', 'unknown')
        savings_rate = financial_data.get('savings_rate', 0)
        
        if balance < 0:
            return random.choice([
                "🚨 Minus! Perlu kontrol pengeluaran segera",
                "⚠️ Saldo negatif, time for emergency budgeting",
                "❌ Over budget, perlu strategi financial recovery"
            ])
        elif budget_status == "over_budget":
            return random.choice([
                "⚠️ Pengeluaran melebihi budget, hati-hati ya",
                "🟡 Spending over limit, need to adjust",
                "📊 Budget overrun, time to cut back"
            ])
        elif budget_status == "excellent" and savings_rate > 20:
            return random.choice([
                "🤩 Excellent! Keuangan sangat sehat dan rajin menabung",
                "🌟 Outstanding financial management!",
                "👑 Financial superstar! Keep it up!"
            ])
        elif budget_status == "good":
            return random.choice([
                "😊 Keuangan terkontrol baik, good job!",
                "👍 Balance sehat, maintain this habit",
                "✅ Good financial discipline!"
            ])
        else:
            return random.choice([
                "📈 Keuangan cukup stabil",
                "💰 Balance masih oke",
                "📊 Financial status normal"
            ])
    
    def get_personalized_suggestions(self, intent: str, student: Student, financial_data: Dict[str, Any]) -> List[str]:
        """Get personalized suggestions based on context"""
        suggestions = []
        
        # Base suggestions by intent
        base_suggestions = {
            'check_balance': ["Lihat pengeluaran hari ini", "Tips menghemat", "Analisa kategori"],
            'view_expenses': ["Breakdown per kategori", "Bandingkan periode", "Tips hemat"],
            'budget_help': ["Buat budget realistis", "Tips mahasiswa", "Setting reminder"],
            'savings_goal': ["Tips menabung", "Challenge 30 hari", "Target semester"],
            'expense_analysis': ["Optimasi pengeluaran", "Pattern analysis", "Budget adjustment"]
        }
        
        suggestions.extend(base_suggestions.get(intent, ["Bantuan umum", "Tips keuangan", "Cek saldo"]))
        
        # Add contextual suggestions
        balance = financial_data.get('current_balance', 0)
        budget_status = financial_data.get('budget_status', 'unknown')
        top_category = financial_data.get('top_category', '')
        
        if balance < 50000:  # Low balance
            suggestions.append("Tips cari income tambahan")
        
        if budget_status == "over_budget":
            suggestions.append("Emergency budget plan")
        
        if top_category and financial_data.get('top_category_percentage', 0) > 40:
            suggestions.append(f"Tips hemat {top_category}")
        
        # Student-specific suggestions
        if student.profile.semester <= 2:
            suggestions.append("Tips finansial mahasiswa baru")
        
        if student.profile.accommodation == "kos":
            suggestions.append("Hemat biaya kos")
        
        if len(student.profile.savings_goals) == 0:
            suggestions.append("Mulai target tabungan")
        
        # Limit and randomize
        return random.sample(suggestions, min(3, len(suggestions)))
    
    async def generate_response(
        self, 
        intent: str, 
        entities: Dict[str, Any], 
        student: Student,
        user_message: str
    ) -> ChatResponse:
        """Generate comprehensive contextual response"""
        
        try:
            # Get student financial data
            financial_data = await self.get_student_financial_data(student)
            
            # Prepare base response data
            response_data = {
                'name': student.profile.nickname or student.profile.full_name.split()[0],
                'balance': format_idr(financial_data.get('current_balance', 0)),
                'total_expense': format_idr(financial_data.get('total_expense', 0)),
                'week_expenses': format_idr(financial_data.get('week_expenses', 0)),
                'today_expenses': format_idr(financial_data.get('today_expenses', 0)),
                'daily_average': format_idr(financial_data.get('daily_average', 0)),
                'monthly_allowance': format_idr(student.profile.monthly_allowance or 0),
                'top_category': financial_data.get('top_category', 'makanan'),
                'financial_health_status': self.get_financial_health_status(financial_data)
            }
            
            # Create data usage info
            data_used = DataUsed(
                transactions_count=financial_data.get('transaction_count', 0),
                period_analyzed="30 hari terakhir"
            )
            
            # Generate response based on intent
            if intent == 'greeting':
                message = random.choice(self.response_templates['greeting']).format(**response_data)
                suggestions = self.get_personalized_suggestions('greeting', student, financial_data)
                response_type = "greeting"
            
            elif intent == 'check_balance':
                balance = financial_data.get('current_balance', 0)
                
                if balance > 100000:
                    status_message = random.choice(self.indonesian_expressions['positive_balance'])
                elif balance > 0:
                    status_message = "Saldo masih ada, tapi jangan boros ya! 😊"
                elif balance == 0:
                    status_message = "Wah habis ya! Time to top up atau cari income tambahan"
                else:
                    status_message = random.choice(self.indonesian_expressions['low_balance'])
                
                response_data.update({
                    'status_message': status_message,
                    'advice': self.get_financial_health_status(financial_data),
                    'insight': f"Pengeluaran bulan ini {response_data['total_expense']}"
                })
                
                message = random.choice(self.response_templates['balance_info']).format(**response_data)
                suggestions = self.get_personalized_suggestions('check_balance', student, financial_data)
                response_type = "balance_info"
            
            elif intent == 'view_expenses':
                period = entities.get('time_period', 'bulan ini')
                
                if period == 'hari ini':
                    amount = response_data['today_expenses']
                elif period == 'minggu ini':
                    amount = response_data['week_expenses']
                else:
                    amount = response_data['total_expense']
                
                top_category = financial_data.get('top_category', 'makanan')
                percentage = format_percentage_id(financial_data.get('top_category_percentage', 0))
                
                # Generate insights
                if financial_data.get('budget_status') == 'over_budget':
                    insight = random.choice(self.indonesian_expressions['overspending'])
                elif financial_data.get('daily_average', 0) > 50000:
                    insight = "Pengeluaran harian cukup tinggi nih, bisa dioptimalkan"
                else:
                    insight = "Pola pengeluaran masih terkontrol"
                
                response_data.update({
                    'period': period,
                    'amount': amount,
                    'top_category': top_category,
                    'percentage': percentage,
                    'insight': insight
                })
                
                message = random.choice(self.response_templates['expense_summary']).format(**response_data)
                suggestions = self.get_personalized_suggestions('view_expenses', student, financial_data)
                response_type = "expense_summary"
            
            elif intent == 'budget_help':
                monthly_allowance = student.profile.monthly_allowance or 1500000  # Default 1.5M
                daily_budget = monthly_allowance / 30
                
                # Generate specific advice based on spending pattern
                current_daily_avg = financial_data.get('daily_average', 0)
                if current_daily_avg > daily_budget:
                    specific_advice = f"Target daily kamu {format_idr(daily_budget)}, tapi actual {format_idr(current_daily_avg)}. Perlu kurangi {format_idr(current_daily_avg - daily_budget)}/hari"
                else:
                    specific_advice = f"Good job! Pengeluaran harian masih di bawah target"
                
                response_data.update({
                    'daily_budget': format_idr(daily_budget),
                    'monthly_budget': format_idr(monthly_allowance),
                    'allocation': "40% makanan, 15% transport, 10% akademik, 15% hiburan, 20% tabungan",
                    'specific_advice': specific_advice
                })
                
                message = random.choice(self.response_templates['budget_advice']).format(**response_data)
                suggestions = self.get_personalized_suggestions('budget_help', student, financial_data)
                response_type = "budget_advice"
            
            elif intent == 'add_transaction':
                amount = entities.get('amount')
                category = entities.get('category', 'lainnya')
                
                if amount:
                    # Provide guidance for recording transaction
                    message = f"Untuk mencatat transaksi {format_idr(amount)} kategori {category}, gunakan menu 'Tambah Transaksi' di aplikasi. Setelah itu saya bisa bantu analisa impact ke budget kamu!"
                    
                    suggestions = [
                        "Analisa impact ke budget",
                        "Tips hemat kategori ini",
                        "Cek sisa budget hari ini"
                    ]
                else:
                    message = random.choice(self.response_templates['transaction_help'])
                    suggestions = [
                        "Panduan input transaksi",
                        "Tips kategorisasi",
                        "Automated expense tracking"
                    ]
                
                response_type = "transaction_help"
            
            elif intent == 'savings_goal':
                savings_goals = student.profile.savings_goals
                
                if savings_goals:
                    active_goal = next((goal for goal in savings_goals if goal.is_active), None)
                    if active_goal:
                        progress = (active_goal.current_amount / active_goal.target_amount * 100) if active_goal.target_amount > 0 else 0
                        remaining = active_goal.target_amount - active_goal.current_amount
                        
                        # Calculate estimated completion time
                        savings_rate_monthly = financial_data.get('monthly_allowance', 0) * 0.2  # Assume 20% savings rate
                        months_to_complete = remaining / savings_rate_monthly if savings_rate_monthly > 0 else 0
                        
                        motivation_message = ""
                        if progress >= 80:
                            motivation_message = "Tinggal sedikit lagi! You're almost there! 🎯"
                        elif progress >= 50:
                            motivation_message = "Halfway there! Keep the momentum! 💪"
                        elif progress >= 25:
                            motivation_message = "Good start! Consistency is key! 📈"
                        else:
                            motivation_message = "Great goal! Let's build this habit! 🚀"
                        
                        response_data.update({
                            'progress': f"{progress:.1f}",
                            'remaining': format_idr(remaining),
                            'current_amount': format_idr(active_goal.current_amount),
                            'target_amount': format_idr(active_goal.target_amount),
                            'saved_amount': format_idr(active_goal.current_amount),
                            'motivation_message': motivation_message,
                            'months_to_complete': f"{months_to_complete:.1f}" if months_to_complete > 0 else "tidak terhitung"
                        })
                        message = random.choice(self.response_templates['savings_motivation']).format(**response_data)
                    else:
                        message = "Kamu punya savings goals tapi belum ada yang aktif. Yuk aktifkan salah satu atau buat target baru!"
                else:
                    message = "Belum ada target tabungan nih. Yuk mulai dengan target kecil dulu! Misalnya dana darurat {format_idr(student.profile.monthly_allowance * 3)} atau gadget impian."
                
                suggestions = self.get_personalized_suggestions('savings_goal', student, financial_data)
                response_type = "savings_goal"
            
            elif intent == 'expense_analysis':
                period = entities.get('time_period', 'bulan ini')
                total = financial_data.get('total_expense', 0)
                average = financial_data.get('daily_average', 0)
                
                top_category = financial_data.get('top_category', 'makanan')
                top_percentage = financial_data.get('top_category_percentage', 0)
                percentage = format_percentage_id(top_percentage)
                
                # Generate insights based on data
                monthly_allowance = student.profile.monthly_allowance or 0
                if monthly_allowance > 0:
                    expense_ratio = (total / monthly_allowance) * 100
                    if expense_ratio > 90:
                        insight = "Pengeluaran sangat tinggi! Perlu emergency budget review"
                        recommendation = "Prioritas: potong pengeluaran non-essential segera"
                    elif expense_ratio > 80:
                        insight = "Pengeluaran cukup tinggi, perlu hati-hati"
                        recommendation = "Saran: review dan kurangi pengeluaran optional"
                    elif expense_ratio > 60:
                        insight = "Pengeluaran normal, masih ada ruang untuk saving"
                        recommendation = "Good: bisa dialokasikan lebih untuk tabungan"
                    else:
                        insight = "Excellent control! Pengeluaran sangat terkendali"
                        recommendation = "Perfect: pertahankan habit ini dan tingkatkan savings"
                else:
                    insight = "Perlu input monthly allowance untuk analisa yang akurat"
                    recommendation = "Set budget bulanan dulu untuk insights yang lebih baik"
                
                # Category-specific advice
                if top_percentage > 50:
                    advice = f"⚠️ {top_category} terlalu dominan ({percentage}). Target ideal max 40%"
                elif top_percentage > 40:
                    advice = f"📊 {top_category} agak tinggi ({percentage}). Bisa dioptimalkan sedikit"
                else:
                    advice = f"✅ Distribusi pengeluaran cukup seimbang"
                
                response_data.update({
                    'period': period,
                    'total': format_idr(total),
                    'average': format_idr(average),
                    'insight': insight,
                    'top_category': top_category,
                    'percentage': percentage,
                    'breakdown': f"{top_category} {percentage}",
                    'recommendation': recommendation,
                    'advice': advice
                })
                
                message = random.choice(self.response_templates['expense_analysis']).format(**response_data)
                suggestions = self.get_personalized_suggestions('expense_analysis', student, financial_data)
                response_type = "expense_analysis"
            
            elif intent == 'academic_expenses':
                academic_percentage = 10  # 10% of monthly allowance for academic
                monthly_allowance = student.profile.monthly_allowance or 1500000
                academic_budget = monthly_allowance * (academic_percentage / 100)
                lab_fee = academic_budget * 0.3  # 30% of academic budget for lab
                
                # Semester-specific advice
                semester = student.profile.semester
                if semester <= 2:
                    tips = "Focus on basic textbooks and digital resources"
                elif semester <= 4:
                    tips = "Balance between books and practical equipment"
                elif semester <= 6:
                    tips = "Invest in specialized software and advanced materials"
                else:
                    tips = "Prioritize thesis research and final project needs"
                
                response_data.update({
                    'percentage': academic_percentage,
                    'amount': format_idr(academic_budget),
                    'lab_fee': format_idr(lab_fee),
                    'tips': tips
                })
                
                message = random.choice(self.response_templates['academic_expense_advice']).format(**response_data)
                suggestions = self.get_personalized_suggestions('academic_expenses', student, financial_data)
                response_type = "academic_advice"
            
            elif intent == 'debt_inquiry':
                message = random.choice(self.response_templates['debt_management'])
                suggestions = [
                    "Debt consolidation tips",
                    "Payment priority strategy", 
                    "Emergency fund vs debt"
                ]
                response_type = "debt_inquiry"
            
            elif intent == 'income_tracking':
                income = financial_data.get('total_income', 0)
                income_sources = len(student.profile.income_sources)
                
                if income > 0:
                    message = f"Pemasukan bulan ini: {format_idr(income)} dari {income_sources + 1} sumber (termasuk uang saku). {random.choice(self.response_templates['income_optimization'])}"
                else:
                    message = f"Belum ada pencatatan pemasukan selain uang saku. {random.choice(self.response_templates['income_optimization'])}"
                
                suggestions = [
                    "Freelance opportunities",
                    "Part-time job ideas",
                    "Passive income untuk student"
                ]
                response_type = "income_tracking"
            
            elif intent == 'help_general':
                message = random.choice(self.response_templates['help_response'])
                suggestions = self.get_personalized_suggestions('help_general', student, financial_data)
                response_type = "help"
            
            else:
                # Fallback with personalized touch
                balance_status = "positif" if financial_data.get('current_balance', 0) > 0 else "perlu perhatian"
                message = f"Hmm, saya belum paham betul maksud kamu. Tapi saya lihat saldo kamu {balance_status}. Mau tanya hal spesifik tentang keuangan?"
                suggestions = [
                    "Cek saldo detail",
                    "Analisa pengeluaran",
                    "Tips budgeting"
                ]
                response_type = "unclear"
            
            # Add motivational message if user is doing well
            if financial_data.get('budget_status') == 'excellent':
                message += f"\n\n{random.choice(self.response_templates['financial_motivation'])}"
            
            return ChatResponse(
                message=message,
                response_type=response_type,
                data_used=data_used,
                suggestions=suggestions,
                confidence=0.85
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return ChatResponse(
                message=random.choice(self.error_responses),
                response_type="error",
                confidence=0.1,
                suggestions=["Coba lagi", "Bantuan umum", "Hubungi support"]
            )
    
    def get_contextual_tips(self, category: str, amount: float, student: Student) -> List[str]:
        """Get contextual money-saving tips"""
        tips = {
            'makanan': [
                "Masak sendiri lebih hemat daripada beli terus",
                "Cari promo lunch di sekitar kampus",
                "Meal prep weekend untuk seminggu",
                "Hindari jajan impulsif, bawa bekal air minum"
            ],
            'transport': [
                "Pakai transportasi umum atau bike sharing",
                "Carpool dengan teman sekampus",
                "Jalan kaki kalau jarak dekat, sekalian olahraga",
                "Manfaatkan shuttle kampus kalau ada"
            ],
            'hiburan': [
                "Cari free events di kampus atau sekitar",
                "Subscription sharing dengan teman untuk streaming",
                "Manfaatkan fasilitas kampus: gym, library, wifi",
                "Window shopping aja dulu, jangan beli impulsif"
            ],
            'akademik': [
                "Beli buku bekas atau pinjam dari senior",
                "Fotokopi chapter penting aja, jangan satu buku",
                "Join study group untuk share resources",
                "Manfaatkan e-book dan digital library"
            ]
        }
        
        category_tips = tips.get(category, [
            "Track semua pengeluaran biar aware",
            "Set budget harian dan stick to it",
            "Bedakan wants vs needs sebelum beli",
            "Cari alternatif yang lebih murah"
        ])
        
        # Add amount-specific advice
        if amount > 100000:
            category_tips.append("Untuk pembelian besar, tunggu 24 jam sebelum decide")
        
        return random.sample(category_tips, min(2, len(category_tips)))
    
    def generate_weekly_summary(self, student: Student, financial_data: Dict[str, Any]) -> str:
        """Generate weekly financial summary"""
        week_expenses = financial_data.get('week_expenses', 0)
        daily_avg = week_expenses / 7
        top_category = financial_data.get('top_category', 'makanan')
        
        weekly_budget = (student.profile.monthly_allowance or 1500000) / 4
        
        if week_expenses <= weekly_budget * 0.7:
            status = "🌟 Excellent! Pengeluaran minggu ini sangat terkontrol"
        elif week_expenses <= weekly_budget:
            status = "✅ Good job! Masih dalam budget mingguan"
        elif week_expenses <= weekly_budget * 1.2:
            status = "⚠️ Sedikit over budget, hati-hati untuk sisa minggu"
        else:
            status = "🚨 Significantly over budget, perlu evaluasi spending"
        
        summary = f"""📊 **Weekly Summary**
{status}

💰 Total pengeluaran: {format_idr(week_expenses)}
📈 Rata-rata harian: {format_idr(daily_avg)}
🏆 Kategori tertinggi: {top_category}
🎯 Target mingguan: {format_idr(weekly_budget)}
"""
        
        return summary
    
    def get_savings_challenge_suggestions(self, student: Student, financial_data: Dict[str, Any]) -> List[str]:
        """Generate savings challenge suggestions"""
        monthly_allowance = student.profile.monthly_allowance or 1500000
        current_expenses = financial_data.get('total_expense', 0)
        
        challenges = []
        
        # Challenge based on expense level
        if current_expenses > monthly_allowance * 0.8:
            challenges.extend([
                "Challenge: Kurangi jajan 50% minggu ini",
                "Challenge: No unnecessary spending selama 7 hari",
                "Challenge: Cook at home challenge 5 hari"
            ])
        else:
            challenges.extend([
                "Challenge: Tabung Rp 10.000 setiap hari",
                "Challenge: 50-30-20 rule (50% needs, 30% wants, 20% savings)",
                "Challenge: Zero-waste money week"
            ])
        
        # Semester-specific challenges
        if student.profile.semester <= 2:
            challenges.append("Freshman savings challenge: Rp 25.000/minggu")
        else:
            challenges.append("Senior savings challenge: Prepare graduation fund")
        
        return random.sample(challenges, min(3, len(challenges)))