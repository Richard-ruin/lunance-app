from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
import calendar
from bson import ObjectId

def generate_object_id() -> str:
    """Generate ObjectId baru sebagai string"""
    return str(ObjectId())

def validate_object_id(obj_id: str) -> bool:
    """Validasi apakah string adalah ObjectId yang valid"""
    try:
        ObjectId(obj_id)
        return True
    except:
        return False

def format_currency(amount: float, currency: str = "IDR") -> str:
    """Format angka menjadi format mata uang"""
    if currency == "IDR":
        # Format Rupiah: Rp 1.000.000
        return f"Rp {amount:,.0f}".replace(",", ".")
    elif currency == "USD":
        # Format Dollar: $1,000.00
        return f"${amount:,.2f}"
    else:
        # Format default
        return f"{currency} {amount:,.2f}"

def parse_amount(amount_str: str) -> Optional[float]:
    """Parse string jumlah uang menjadi float"""
    if not amount_str:
        return None
    
    # Hapus semua karakter selain digit, titik, dan koma
    cleaned = re.sub(r'[^\d.,]', '', amount_str.strip())
    
    # Handle format Indonesia (1.000.000,50)
    if ',' in cleaned and '.' in cleaned:
        # Jika ada titik dan koma, asumsi titik sebagai thousand separator
        cleaned = cleaned.replace('.', '').replace(',', '.')
    elif ',' in cleaned:
        # Jika hanya ada koma, bisa jadi decimal separator atau thousand separator
        parts = cleaned.split(',')
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Likely decimal separator
            cleaned = cleaned.replace(',', '.')
        else:
            # Likely thousand separator
            cleaned = cleaned.replace(',', '')
    
    try:
        return float(cleaned)
    except ValueError:
        return None

def extract_date(date_str: str) -> Optional[datetime]:
    """Extract tanggal dari string natural language"""
    if not date_str:
        return None
    
    date_str = date_str.lower().strip()
    now = datetime.now()
    
    # Hari ini
    if any(word in date_str for word in ['hari ini', 'today', 'sekarang']):
        return now
    
    # Kemarin
    if any(word in date_str for word in ['kemarin', 'yesterday']):
        return now - timedelta(days=1)
    
    # Besok
    if any(word in date_str for word in ['besok', 'tomorrow']):
        return now + timedelta(days=1)
    
    # Minggu lalu
    if any(word in date_str for word in ['minggu lalu', 'last week']):
        return now - timedelta(weeks=1)
    
    # Bulan lalu
    if any(word in date_str for word in ['bulan lalu', 'last month']):
        if now.month == 1:
            return now.replace(year=now.year-1, month=12)
        else:
            return now.replace(month=now.month-1)
    
    # Try parsing common date formats
    date_patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
        r'(\d{1,2})\s+(jan|feb|mar|apr|mei|jun|jul|agt|sep|okt|nov|des)',  # DD MMM
        r'(\d{1,2})\s+(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)',  # DD Month
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                if pattern.startswith(r'(\d{1,2})[/-](\d{1,2})'):  # DD/MM/YYYY
                    day, month, year = match.groups()
                    return datetime(int(year), int(month), int(day))
                elif pattern.startswith(r'(\d{4})'):  # YYYY/MM/DD
                    year, month, day = match.groups()
                    return datetime(int(year), int(month), int(day))
                # Add more date parsing logic as needed
            except ValueError:
                continue
    
    return None

def get_month_range(date: datetime) -> tuple:
    """Mendapatkan range tanggal untuk bulan tertentu"""
    start_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Last day of month
    last_day = calendar.monthrange(date.year, date.month)[1]
    end_date = date.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    
    return start_date, end_date

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Menghitung persentase perubahan"""
    if old_value == 0:
        return 100.0 if new_value > 0 else 0.0
    
    return ((new_value - old_value) / old_value) * 100

def categorize_expense_keywords() -> Dict[str, List[str]]:
    """Daftar keyword untuk kategorisasi otomatis expense"""
    return {
        "Makanan & Minuman": [
            "makan", "minum", "restoran", "cafe", "warung", "kantin", "delivery",
            "gofood", "grabfood", "foodpanda", "mcdonald", "kfc", "pizza", "bakso",
            "nasi", "ayam", "bebek", "soto", "gado", "rendang", "sate", "coffee",
            "starbucks", "dunkin", "bread", "roti", "kue", "snack", "es", "jus"
        ],
        "Transportasi": [
            "ojek", "taksi", "bus", "kereta", "pesawat", "bensin", "solar", "parkir",
            "gojek", "grab", "uber", "tol", "tiket", "garuda", "lion", "citilink",
            "transjakarta", "mrt", "lrt", "service", "servis", "motor", "mobil"
        ],
        "Belanja": [
            "beli", "baju", "celana", "sepatu", "tas", "dompet", "jam", "elektronik",
            "handphone", "laptop", "tv", "kulkas", "mesin", "furniture", "kasur",
            "meja", "kursi", "lemari", "shopee", "tokopedia", "lazada", "bukalapak",
            "amazon", "zalora", "blibli", "supermarket", "hypermart", "carrefour",
            "giant", "alfamart", "indomaret"
        ],
        "Hiburan": [
            "nonton", "bioskop", "cinema", "film", "konser", "musik", "game", "netflix",
            "spotify", "youtube", "disney", "hbo", "amazon prime", "apple music",
            "steam", "playstation", "xbox", "switch", "karaoke", "billiard",
            "bowling", "gym", "fitness", "olahraga", "renang", "badminton"
        ],
        "Kesehatan": [
            "dokter", "rumah sakit", "klinik", "obat", "vitamin", "apotek", "medical",
            "checkup", "laboratorium", "rontgen", "usg", "ct scan", "mri", "dental",
            "gigi", "mata", "kacamata", "softlens", "terapi", "fisioterapi",
            "pijat", "spa", "facial", "skincare", "kosmetik"
        ],
        "Pendidikan": [
            "sekolah", "kuliah", "universitas", "kursus", "les", "bimbel", "buku",
            "alat tulis", "pensil", "pulpen", "kertas", "print", "fotocopy",
            "semester", "spp", "uang kuliah", "wisuda", "thesis", "skripsi",
            "seminar", "workshop", "training", "certification", "udemy", "coursera"
        ],
        "Tagihan": [
            "listrik", "air", "gas", "telepon", "internet", "wifi", "pulsa", "token",
            "pln", "pdam", "telkom", "indihome", "first media", "biznet", "xl",
            "telkomsel", "indosat", "three", "smartfren", "pajak", "insurance",
            "asuransi", "cicilan", "kredit", "loan", "mortgage", "kartu kredit"
        ]
    }

def categorize_income_keywords() -> Dict[str, List[str]]:
    """Daftar keyword untuk kategorisasi otomatis income"""
    return {
        "Gaji": [
            "gaji", "salary", "payroll", "thr", "bonus", "tunjangan", "allowance",
            "overtime", "lembur", "komisi", "commission", "insentif", "incentive"
        ],
        "Freelance": [
            "freelance", "project", "proyek", "kontrak", "contract", "jasa",
            "konsultasi", "consultation", "design", "desain", "website", "aplikasi",
            "photography", "foto", "video", "editing", "writing", "translation"
        ],
        "Bisnis": [
            "penjualan", "sales", "jualan", "dagang", "toko", "warung", "bisnis",
            "business", "profit", "keuntungan", "modal", "investasi", "saham",
            "dividen", "bunga", "deposito", "reksadana", "trading", "crypto"
        ],
        "Investasi": [
            "dividen", "dividend", "bunga", "interest", "deposito", "reksadana",
            "mutual fund", "saham", "stock", "obligasi", "bond", "crypto", "bitcoin",
            "ethereum", "trading", "capital gain", "p2p", "peer to peer"
        ],
        "Lainnya": [
            "hadiah", "gift", "prize", "menang", "lottery", "undian", "cashback",
            "refund", "reimburse", "claim", "asuransi", "insurance", "jual",
            "sell", "lelang", "auction"
        ]
    }

def extract_category_from_text(text: str, transaction_type: str) -> str:
    """Extract kategori dari text menggunakan keyword matching"""
    if not text:
        return "Lainnya"
    
    text_lower = text.lower()
    
    if transaction_type == "expense":
        categories = categorize_expense_keywords()
    else:
        categories = categorize_income_keywords()
    
    # Hitung score untuk setiap kategori
    category_scores = {}
    for category, keywords in categories.items():
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += 1
        category_scores[category] = score
    
    # Pilih kategori dengan score tertinggi
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        if category_scores[best_category] > 0:
            return best_category
    
    return "Lainnya"

def generate_conversation_title(first_message: str) -> str:
    """Generate judul percakapan dari pesan pertama"""
    if not first_message:
        return f"Percakapan {datetime.now().strftime('%d %b %Y')}"
    
    # Truncate dan clean up
    title = first_message.strip()[:50]
    
    # Hapus newlines
    title = title.replace('\n', ' ').replace('\r', ' ')
    
    # Clean multiple spaces
    title = re.sub(r'\s+', ' ', title)
    
    # Add ellipsis jika terpotong
    if len(first_message.strip()) > 50:
        title += "..."
    
    return title

def calculate_savings_suggestion(monthly_income: float, monthly_expenses: float, 
                               savings_percentage: float = 20.0) -> Dict[str, float]:
    """Menghitung saran tabungan berdasarkan income dan expenses"""
    
    # Surplus bulanan
    monthly_surplus = monthly_income - monthly_expenses
    
    # Target tabungan berdasarkan persentase income
    target_by_percentage = monthly_income * (savings_percentage / 100)
    
    # Maksimal tabungan yang bisa dicapai
    max_possible_savings = max(0, monthly_surplus)
    
    # Saran tabungan (yang lebih realistis)
    suggested_savings = min(target_by_percentage, max_possible_savings)
    
    # Emergency fund suggestion (3-6 bulan expenses)
    emergency_fund_min = monthly_expenses * 3
    emergency_fund_max = monthly_expenses * 6
    
    return {
        "monthly_surplus": monthly_surplus,
        "target_by_percentage": target_by_percentage,
        "max_possible_savings": max_possible_savings,
        "suggested_savings": suggested_savings,
        "emergency_fund_min": emergency_fund_min,
        "emergency_fund_max": emergency_fund_max,
        "savings_rate": (suggested_savings / monthly_income * 100) if monthly_income > 0 else 0
    }

def format_duration(seconds: float) -> str:
    """Format durasi dalam detik menjadi string yang readable"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:.0f}m {remaining_seconds:.0f}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {remaining_minutes:.0f}m"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename untuk file upload"""
    # Hapus karakter yang tidak aman
    filename = re.sub(r'[^\w\s-.]', '', filename)
    
    # Replace spaces dengan underscore
    filename = re.sub(r'\s+', '_', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    return filename.strip('_')

def validate_phone_number(phone: str) -> bool:
    """Validasi nomor telepon Indonesia"""
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Indonesian phone number patterns
    patterns = [
        r'^08\d{8,11}$',  # 08xxxxxxxxxx
        r'^628\d{8,11}$',  # 628xxxxxxxxxx
        r'^\+628\d{8,11}$'  # +628xxxxxxxxxx
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone):
            return True
    
    return False

def get_financial_insights(transactions: List[Dict], period_days: int = 30) -> Dict[str, Any]:
    """Generate insights keuangan dari daftar transaksi"""
    if not transactions:
        return {}
    
    now = datetime.now()
    period_start = now - timedelta(days=period_days)
    
    # Filter transaksi dalam period
    recent_transactions = [
        t for t in transactions 
        if t.get('date') and t['date'] >= period_start
    ]
    
    # Kalkulasi dasar
    total_income = sum(t['amount'] for t in recent_transactions if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in recent_transactions if t['type'] == 'expense')
    net_income = total_income - total_expense
    
    # Expense by category
    expense_by_category = {}
    for t in recent_transactions:
        if t['type'] == 'expense':
            category = t.get('category', 'Lainnya')
            expense_by_category[category] = expense_by_category.get(category, 0) + t['amount']
    
    # Top spending category
    top_spending_category = max(expense_by_category.items(), key=lambda x: x[1]) if expense_by_category else None
    
    # Average daily spending
    avg_daily_expense = total_expense / period_days if period_days > 0 else 0
    
    # Spending trend (compare with previous period)
    prev_period_start = period_start - timedelta(days=period_days)
    prev_transactions = [
        t for t in transactions 
        if t.get('date') and prev_period_start <= t['date'] < period_start
    ]
    prev_total_expense = sum(t['amount'] for t in prev_transactions if t['type'] == 'expense')
    
    expense_trend = calculate_percentage_change(prev_total_expense, total_expense)
    
    return {
        "period_days": period_days,
        "transaction_count": len(recent_transactions),
        "total_income": total_income,
        "total_expense": total_expense,
        "net_income": net_income,
        "expense_by_category": expense_by_category,
        "top_spending_category": top_spending_category,
        "avg_daily_expense": avg_daily_expense,
        "expense_trend_percentage": expense_trend,
        "savings_rate": (net_income / total_income * 100) if total_income > 0 else 0
    }