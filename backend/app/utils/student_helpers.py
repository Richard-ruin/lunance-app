# app/utils/student_helpers.py
import os
import uuid
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from PIL import Image
import aiofiles
from fastapi import UploadFile
from pathlib import Path

from app.utils.constants import (
    INDONESIAN_E_WALLETS, INDONESIAN_BANKS, EXPENSE_CATEGORIES, 
    INCOME_CATEGORIES, EXPERIENCE_POINTS, LEVEL_THRESHOLDS,
    DEFAULT_BUDGET_ALLOCATION, ACHIEVEMENTS, PREDICTION_RULES,
    FILE_UPLOAD, NOTIFICATION_TEMPLATES
)
import logging

logger = logging.getLogger(__name__)

# University validation data
INDONESIAN_UNIVERSITIES = {
    "Universitas Indonesia": {
        "faculties": [
            "Fakultas Kedokteran", "Fakultas Kedokteran Gigi", "Fakultas Matematika dan Ilmu Pengetahuan Alam",
            "Fakultas Teknik", "Fakultas Hukum", "Fakultas Ekonomi dan Bisnis", "Fakultas Ilmu Pengetahuan Budaya",
            "Fakultas Psikologi", "Fakultas Ilmu Sosial dan Ilmu Politik", "Fakultas Kesehatan Masyarakat",
            "Fakultas Ilmu Keperawatan", "Fakultas Farmasi", "Fakultas Ilmu Komputer", "Fakultas Ilmu Administrasi"
        ]
    },
    "Institut Teknologi Bandung": {
        "faculties": [
            "Fakultas Matematika dan Ilmu Pengetahuan Alam", "Fakultas Ilmu dan Teknologi Kebumian",
            "Fakultas Teknik Mesin dan Dirgantara", "Fakultas Teknik Elektro dan Informatika",
            "Fakultas Teknik Sipil dan Lingkungan", "Fakultas Teknik Pertambangan dan Perminyakan",
            "Fakultas Teknologi Industri", "Fakultas Seni Rupa dan Desain", "Sekolah Bisnis dan Manajemen",
            "Sekolah Farmasi", "Sekolah Ilmu dan Teknologi Hayati", "Sekolah Arsitektur, Perencanaan dan Pengembangan Kebijakan"
        ]
    },
    "Universitas Gadjah Mada": {
        "faculties": [
            "Fakultas Biologi", "Fakultas Ekonomika dan Bisnis", "Fakultas Farmasi", "Fakultas Filsafat",
            "Fakultas Geografi", "Fakultas Hukum", "Fakultas Ilmu Budaya", "Fakultas Ilmu Sosial dan Ilmu Politik",
            "Fakultas Kedokteran", "Fakultas Kedokteran Gigi", "Fakultas Kedokteran Hewan", "Fakultas Kehutanan",
            "Fakultas Matematika dan Ilmu Pengetahuan Alam", "Fakultas Pertanian", "Fakultas Peternakan",
            "Fakultas Psikologi", "Fakultas Teknik", "Fakultas Teknologi Pertanian", "Sekolah Vokasi"
        ]
    }
}

# Student expense categories (from your original constants)
STUDENT_EXPENSE_CATEGORIES = {
    "academic": {
        "name": "Akademik",
        "subcategories": ["buku", "alat_tulis", "fotokopi", "uang_kuliah", "lab", "praktikum", "seminar"]
    },
    "food": {
        "name": "Makanan & Minuman", 
        "subcategories": ["makan_siang", "snack", "kopi", "jajan", "groceries", "makan_malam"]
    },
    "transportation": {
        "name": "Transportasi",
        "subcategories": ["ojol", "bus", "kereta", "bensin", "parkir", "grab", "gojek"]
    },
    "entertainment": {
        "name": "Hiburan",
        "subcategories": ["nonton", "game", "music", "hobi", "olahraga", "traveling"]
    },
    "health": {
        "name": "Kesehatan",
        "subcategories": ["obat", "dokter", "vitamin", "olahraga", "gym"]
    },
    "technology": {
        "name": "Teknologi",
        "subcategories": ["internet", "pulsa", "aplikasi", "gadget", "software"]
    },
    "clothing": {
        "name": "Pakaian",
        "subcategories": ["baju", "sepatu", "aksesoris", "laundry"]
    },
    "social": {
        "name": "Sosial",
        "subcategories": ["hang_out", "kado", "donasi", "organisasi"]
    },
    "emergency": {
        "name": "Darurat",
        "subcategories": ["medis", "keluarga", "teknis"]
    }
}

# Achievement definitions (from your original file)
STUDENT_ACHIEVEMENTS = {
    "first_login": {
        "name": "Welcome to Lunance!",
        "description": "Complete your first login",
        "points": 10,
        "badge": "🎉"
    },
    "profile_completion": {
        "name": "Profile Master",
        "description": "Complete your profile 100%",
        "points": 50,
        "badge": "✅"
    },
    "first_transaction": {
        "name": "First Step",
        "description": "Record your first transaction",
        "points": 15,
        "badge": "💸"
    },
    "savings_goal_created": {
        "name": "Goal Setter", 
        "description": "Create your first savings goal",
        "points": 25,
        "badge": "🎯"
    },
    "weekly_budget_met": {
        "name": "Budget Ninja",
        "description": "Stay within weekly budget",
        "points": 30,
        "badge": "🥷"
    },
    "expense_shared": {
        "name": "Team Player",
        "description": "Share your first expense with friends",
        "points": 20,
        "badge": "🤝"
    },
    "streak_7_days": {
        "name": "Week Warrior",
        "description": "Log transactions for 7 consecutive days",
        "points": 40,
        "badge": "🔥"
    },
    "streak_30_days": {
        "name": "Monthly Master",
        "description": "Log transactions for 30 consecutive days",
        "points": 100,
        "badge": "🏆"
    }
}

def generate_filename(original_filename: str, prefix: str = "") -> str:
    """Generate a unique filename for uploads"""
    file_extension = Path(original_filename).suffix
    unique_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    if prefix:
        return f"{prefix}_{timestamp}_{unique_id}{file_extension}"
    return f"{timestamp}_{unique_id}{file_extension}"

def validate_indonesian_phone(phone: str) -> bool:
    """Validate Indonesian phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it starts with common Indonesian prefixes
    valid_prefixes = ['08', '628', '+628']
    
    for prefix in valid_prefixes:
        if phone.startswith(prefix):
            return len(digits_only) >= 10 and len(digits_only) <= 15
    
    return False

def format_currency(amount: float, currency: str = "IDR") -> str:
    """Format currency for Indonesian Rupiah"""
    if currency == "IDR":
        # Format with thousand separators using dots (Indonesian style)
        formatted = f"{amount:,.0f}".replace(",", ".")
        return f"Rp {formatted}"
    return f"{currency} {amount:,.2f}"

def format_indonesian_currency(amount: float) -> str:
    """Format amount in Indonesian Rupiah"""
    try:
        # Convert to integer if it's a whole number
        if amount == int(amount):
            amount = int(amount)
        
        # Format with thousand separators
        formatted = f"Rp {amount:,.0f}" if isinstance(amount, int) else f"Rp {amount:,.2f}"
        return formatted.replace(",", ".")  # Use dots as thousand separators (Indonesian style)
        
    except Exception:
        return f"Rp {amount}"

def get_academic_semester_info(date: datetime) -> dict:
    """Get academic semester information based on date"""
    year = date.year
    month = date.month
    
    # Indonesian academic calendar (rough estimation)
    if month >= 8:  # August - December (Odd semester)
        semester = "ganjil"
        semester_start = datetime(year, 8, 1)
        academic_year = f"{year}/{year + 1}"
    elif month <= 1:  # January (still odd semester)
        semester = "ganjil"
        semester_start = datetime(year - 1, 8, 1)
        academic_year = f"{year - 1}/{year}"
    elif month >= 2 and month <= 6:  # February - June (Even semester)
        semester = "genap"
        semester_start = datetime(year, 2, 1)
        academic_year = f"{year - 1}/{year}"
    else:  # July (break period)
        semester = "libur"
        semester_start = datetime(year, 7, 1)
        academic_year = f"{year}/{year + 1}"
    
    # Calculate week in semester
    week_in_semester = max(1, min(16, ((date - semester_start).days // 7) + 1))
    
    return {
        "semester": semester,
        "academic_year": academic_year,
        "week_in_semester": week_in_semester,
        "is_exam_period": week_in_semester >= 14 and semester != "libur"
    }

def categorize_student_expense(title: str, amount: float, location_type: Optional[str] = None) -> dict:
    """Auto-categorize student expenses based on title and context"""
    title_lower = title.lower()
    
    # Food keywords from EXPENSE_CATEGORIES
    food_keywords = EXPENSE_CATEGORIES["food"]["subcategories"]
    transport_keywords = EXPENSE_CATEGORIES["transportation"]["subcategories"] 
    education_keywords = EXPENSE_CATEGORIES["academic"]["subcategories"]
    entertainment_keywords = EXPENSE_CATEGORIES["entertainment"]["subcategories"]
    
    confidence = 0.7  # Default confidence
    is_unusual = False
    academic_related = False
    
    # Check for food
    if any(keyword in title_lower for keyword in food_keywords) or location_type == "restaurant":
        category_suggestion = "food"
        if amount > 50000:  # More than 50k for food might be unusual for students
            is_unusual = True
            confidence = 0.8
    
    # Check for transport
    elif any(keyword in title_lower for keyword in transport_keywords) or location_type == "transport":
        category_suggestion = "transportation"
        if amount > 100000:  # More than 100k for transport
            is_unusual = True
    
    # Check for education
    elif any(keyword in title_lower for keyword in education_keywords):
        category_suggestion = "academic"
        academic_related = True
        confidence = 0.9
    
    # Check for entertainment
    elif any(keyword in title_lower for keyword in entertainment_keywords):
        category_suggestion = "entertainment"
        if amount > 200000:  # More than 200k for entertainment
            is_unusual = True
    
    else:
        category_suggestion = "other"
        confidence = 0.3
        if amount > 500000:  # Large amount without clear category
            is_unusual = True
    
    return {
        "suggested_category": category_suggestion,
        "confidence": confidence,
        "is_unusual": is_unusual,
        "academic_related": academic_related
    }

def get_budget_recommendations(monthly_income: float, current_expenses: float) -> dict:
    """Generate budget recommendations for students"""
    
    # Use the budget allocation from constants
    budget_amounts = {}
    for category, percentage in DEFAULT_BUDGET_ALLOCATION.items():
        budget_amounts[category] = monthly_income * (percentage / 100)
    
    # Calculate remaining budget
    total_recommended_expense = monthly_income * 0.80  # 80% for expenses, 20% for savings
    remaining_budget = total_recommended_expense - current_expenses
    
    # Generate advice
    advice = []
    if remaining_budget < 0:
        advice.append("Anda sudah melebihi budget yang direkomendasikan bulan ini!")
        advice.append("Coba kurangi pengeluaran untuk hiburan dan makanan di luar.")
    elif remaining_budget < monthly_income * 0.10:
        advice.append("Budget Anda hampir habis. Hati-hati dengan pengeluaran selanjutnya.")
    else:
        advice.append("Budget Anda masih aman. Pertahankan pola pengeluaran ini.")
    
    return {
        "recommended_allocations": budget_amounts,
        "remaining_budget": remaining_budget,
        "budget_status": "over" if remaining_budget < 0 else "warning" if remaining_budget < monthly_income * 0.10 else "safe",
        "advice": advice
    }

def generate_savings_challenge(current_balance: float, monthly_income: float) -> dict:
    """Generate personalized savings challenges for students"""
    
    # Calculate appropriate challenge amount (5-10% of monthly income)
    min_challenge = monthly_income * 0.05
    max_challenge = monthly_income * 0.10
    
    challenges = [
        {
            "title": "Hemat Jajan Sehari",
            "description": "Coba tidak jajan selama 1 hari dan masukkan uang jajan ke tabungan",
            "target_amount": 25000,
            "duration_days": 1,
            "difficulty": "mudah"
        },
        {
            "title": "Minggu Hemat Transport",
            "description": "Gunakan transportasi umum atau jalan kaki selama seminggu",
            "target_amount": 50000,
            "duration_days": 7,
            "difficulty": "sedang"
        },
        {
            "title": "Challenge 50rb Sebulan",
            "description": "Tabung 50 ribu dalam sebulan dengan mengurangi pengeluaran tidak penting",
            "target_amount": 50000,
            "duration_days": 30,
            "difficulty": "sedang"
        },
        {
            "title": "Tabungan Semester",
            "description": "Kumpulkan tabungan untuk keperluan semester depan",
            "target_amount": min(max_challenge * 4, 200000),
            "duration_days": 120,
            "difficulty": "sulit"
        }
    ]
    
    # Filter challenges based on income level
    affordable_challenges = [
        challenge for challenge in challenges 
        if challenge["target_amount"] <= max_challenge * (challenge["duration_days"] / 30)
    ]
    
    return {
        "available_challenges": affordable_challenges,
        "recommended_monthly_savings": min_challenge,
        "current_savings_rate": (current_balance / monthly_income) if monthly_income > 0 else 0
    }

async def validate_university_info(university: str, faculty: str = None, major: str = None) -> bool:
    """Validate university, faculty, and major combination"""
    try:
        # Check if university is in our database
        if university in INDONESIAN_UNIVERSITIES:
            if faculty:
                # Check if faculty exists for this university
                if faculty not in INDONESIAN_UNIVERSITIES[university]["faculties"]:
                    return False
        
        # For now, we'll be lenient with majors since there are too many to list
        # In production, you might want a more comprehensive database
        return True
        
    except Exception as e:
        logger.error(f"University validation error: {str(e)}")
        return False

async def process_profile_picture(file: UploadFile, user_id: str) -> str:
    """Process and save profile picture"""
    try:
        # Create upload directory if it doesn't exist
        upload_dir = Path("static/uploads/profile_pictures")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ['.jpg', '.jpeg', '.png']:
            raise ValueError("Unsupported file format. Use JPG, JPEG, or PNG.")
        
        filename = f"{user_id}_{uuid.uuid4().hex}{file_extension}"
        file_path = upload_dir / filename
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > FILE_UPLOAD["PROFILE_PICTURE_MAX_SIZE"]:
            raise ValueError("File size too large. Maximum 2MB allowed.")
        
        # Save original file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Process image (resize, optimize)
        await optimize_profile_picture(str(file_path))
        
        # Return URL path
        return f"/static/profile_pictures/{filename}"
        
    except Exception as e:
        logger.error(f"Profile picture processing error: {str(e)}")
        raise ValueError(f"Failed to process profile picture: {str(e)}")

async def optimize_profile_picture(file_path: str) -> None:
    """Optimize profile picture (resize and compress)"""
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize to maximum 400x400 while maintaining aspect ratio
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(file_path, 'JPEG', quality=85, optimize=True)
            
    except Exception as e:
        logger.error(f"Image optimization error: {str(e)}")
        # If optimization fails, keep the original file

def calculate_user_level(experience_points: int) -> int:
    """Calculate user level based on experience points"""
    for level, threshold in enumerate(LEVEL_THRESHOLDS, 1):
        if experience_points < threshold:
            return level - 1 if level > 1 else 1
    
    # For levels beyond the threshold list
    if experience_points >= LEVEL_THRESHOLDS[-1]:
        additional_levels = (experience_points - LEVEL_THRESHOLDS[-1]) // 500
        return len(LEVEL_THRESHOLDS) + additional_levels
    
    return len(LEVEL_THRESHOLDS)

async def update_user_achievements(student: "Student", achievement_trigger: str) -> List[str]:
    """Update user achievements and return newly earned achievements"""
    try:
        newly_earned = []
        
        if achievement_trigger in STUDENT_ACHIEVEMENTS:
            achievement_id = achievement_trigger
            achievement = STUDENT_ACHIEVEMENTS[achievement_id]
            
            # Check if user already has this achievement
            existing_achievements = [ach.achievement_id for ach in student.gamification.achievements]
            
            if achievement_id not in existing_achievements:
                # Award achievement
                from app.models.student import Achievement
                new_achievement = Achievement(
                    achievement_id=achievement_id,
                    earned_date=datetime.utcnow(),
                    progress=100.0
                )
                
                student.gamification.achievements.append(new_achievement)
                student.gamification.experience_points += achievement["points"]
                student.gamification.level = calculate_user_level(student.gamification.experience_points)
                
                # Add badge if not already present
                if achievement["badge"] not in student.gamification.badges:
                    student.gamification.badges.append(achievement["badge"])
                
                newly_earned.append(achievement_id)
                
                # Update student in database
                from app.api.v1.students.crud import student_crud
                from app.models.student import StudentUpdate
                student_update = StudentUpdate()
                student_update.gamification = student.gamification
                await student_crud.update_student(str(student.id), student_update)
                
                logger.info(f"Achievement earned: {achievement_id} by user {student.email}")
        
        return newly_earned
        
    except Exception as e:
        logger.error(f"Achievement update error: {str(e)}")
        return []

def get_student_expense_categories() -> Dict[str, Any]:
    """Get expense categories suitable for students"""
    return STUDENT_EXPENSE_CATEGORIES

def get_achievement_definitions() -> Dict[str, Any]:
    """Get all achievement definitions"""
    return STUDENT_ACHIEVEMENTS

def validate_academic_calendar_event(event_type: str, start_date: datetime, end_date: datetime) -> bool:
    """Validate academic calendar event"""
    valid_event_types = [
        "semester_start", "semester_end", "midterm_exam", "final_exam", 
        "holiday", "registration", "thesis_defense", "graduation"
    ]
    
    if event_type not in valid_event_types:
        return False
    
    if start_date >= end_date:
        return False
    
    # Additional validation logic can be added here
    return True

def calculate_semester_progress(semester_start: datetime, semester_end: datetime) -> float:
    """Calculate semester progress percentage"""
    try:
        now = datetime.utcnow()
        total_duration = (semester_end - semester_start).total_seconds()
        elapsed_duration = (now - semester_start).total_seconds()
        
        if elapsed_duration < 0:
            return 0.0
        elif elapsed_duration > total_duration:
            return 100.0
        else:
            return (elapsed_duration / total_duration) * 100
            
    except Exception:
        return 0.0

def get_student_financial_tips(profile_data: Dict[str, Any]) -> List[str]:
    """Get personalized financial tips based on student profile"""
    tips = []
    
    # Basic tips for all students
    tips.extend([
        "Track your daily expenses to understand spending patterns",
        "Set aside at least 10% of your allowance for emergency fund",
        "Use student discounts whenever possible"
    ])
    
    # Semester-specific tips
    semester = profile_data.get("semester", 0)
    if semester <= 2:
        tips.append("As a new student, focus on learning to budget your monthly allowance")
    elif semester >= 7:
        tips.append("Start planning for post-graduation expenses and job search costs")
    
    # Accommodation-specific tips
    accommodation = profile_data.get("accommodation", "")
    if accommodation == "kos":
        tips.append("Consider cooking your own meals to save on food expenses")
    elif accommodation == "asrama":
        tips.append("Take advantage of dorm facilities to minimize additional costs")
    
    # Transportation-specific tips
    transportation = profile_data.get("transportation", "")
    if transportation == "motor":
        tips.append("Track fuel expenses and consider carpooling to save costs")
    elif transportation == "public_transport":
        tips.append("Look into monthly transport passes for better rates")
    
    return tips

def get_spending_insights(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate spending insights from transaction data"""
    insights = {
        "total_spent": 0,
        "most_expensive_category": None,
        "most_frequent_category": None,
        "daily_average": 0,
        "category_breakdown": {}
    }
    
    if not transactions:
        return insights
    
    # Calculate totals and breakdowns
    category_totals = {}
    category_counts = {}
    
    for transaction in transactions:
        amount = transaction.get("amount", 0)
        category = transaction.get("category", "other")
        
        insights["total_spent"] += amount
        
        if category not in category_totals:
            category_totals[category] = 0
            category_counts[category] = 0
        
        category_totals[category] += amount
        category_counts[category] += 1
    
    # Find most expensive and frequent categories
    if category_totals:
        insights["most_expensive_category"] = max(category_totals, key=category_totals.get)
        insights["most_frequent_category"] = max(category_counts, key=category_counts.get)
        insights["category_breakdown"] = category_totals
    
    # Calculate daily average (assuming transactions are from current month)
    if transactions:
        insights["daily_average"] = insights["total_spent"] / max(len(transactions), 1)
    
    return insights

def generate_budget_recommendations(
    monthly_allowance: float, 
    spending_history: List[Dict[str, Any]]
) -> Dict[str, float]:
    """Generate budget recommendations based on allowance and spending history"""
    recommendations = {}
    
    if monthly_allowance <= 0:
        return recommendations
    
    # Default budget allocation for students (percentages)
    default_allocation = {
        "food": 0.40,          # 40% for food
        "transportation": 0.15, # 15% for transportation
        "academic": 0.10,       # 10% for academic expenses
        "entertainment": 0.10,  # 10% for entertainment
        "emergency": 0.15,      # 15% for emergency fund
        "savings": 0.10         # 10% for savings
    }
    
    # Calculate recommended amounts
    for category, percentage in default_allocation.items():
        recommendations[category] = monthly_allowance * percentage
    
    # Adjust based on spending history if available
    if spending_history:
        insights = get_spending_insights(spending_history)
        category_breakdown = insights.get("category_breakdown", {})
        
        # If user spends more in certain categories, adjust recommendations
        for category, spent_amount in category_breakdown.items():
            if category in recommendations:
                # Increase budget slightly if consistently overspending
                current_budget = recommendations[category]
                if spent_amount > current_budget * 1.2:  # 20% over budget
                    recommendations[category] = min(
                        spent_amount * 1.1,  # 10% buffer
                        monthly_allowance * 0.5  # Max 50% of allowance for any category
                    )
    
    return recommendations

def get_notification_message(template_key: str, **kwargs) -> str:
    """Get formatted notification message from template"""
    template = NOTIFICATION_TEMPLATES.get(template_key, "")
    try:
        return template.format(**kwargs)
    except KeyError:
        return template

def get_expense_category_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Get expense category information by slug"""
    return EXPENSE_CATEGORIES.get(slug)

def get_income_category_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Get income category information by slug"""
    return INCOME_CATEGORIES.get(slug)

def predict_category_budget_impact(category: str, current_week: int, semester: str) -> Dict[str, Any]:
    """Predict budget impact based on academic calendar"""
    impact = {
        "multiplier": 1.0,
        "reason": "Normal period",
        "recommendations": []
    }
    
    # Check prediction rules
    for rule_key, rule in PREDICTION_RULES.items():
        if category in rule.get("categories", []):
            # Simple logic for demonstration
            if rule_key == "academic_start" and current_week <= 2:
                impact["multiplier"] = rule["multiplier"]
                impact["reason"] = rule["description"]
                impact["recommendations"].append("Consider setting aside extra budget for academic expenses")
            elif rule_key == "exam_period" and current_week >= 14:
                impact["multiplier"] = rule["multiplier"]
                impact["reason"] = rule["description"]
                impact["recommendations"].append("Expect higher food and health expenses during exam period")
    
    return [{"title": "impactHemat Jajan Sehari",
            "description": "Coba tidak jajan selama 1 hari dan masukkan uang jajan ke tabungan",
            "target_amount": 25000,
            "duration_days": 1,
            "difficulty": "mudah"
        },
        {
            "title": "Minggu Hemat Transport",
            "description": "Gunakan transportasi umum atau jalan kaki selama seminggu",
            "target_amount": 50000,
            "duration_days": 7,
            "difficulty": "sedang"
        },
        {
            "title": "Challenge 50rb Sebulan",
            "description": "Tabung 50 ribu dalam sebulan dengan mengurangi pengeluaran tidak penting",
            "target_amount": 50000,
            "duration_days": 30,
            "difficulty": "sedang"
        },
        {
            "title": "Tabungan Semester",
            "description": "Kumpulkan tabungan untuk keperluan semester depan",
            "target_amount": min(max_challenge * 4, 200000),
            "duration_days": 120,
            "difficulty": "sulit"
        }
    ]
    
    # Filter challenges based on income level
    affordable_challenges = [
        challenge for challenge in challenges 
        if challenge["target_amount"] <= max_challenge * (challenge["duration_days"] / 30)
    ]
    
    return {
        "available_challenges": affordable_challenges,
        "recommended_monthly_savings": min_challenge,
        "current_savings_rate": (current_balance / monthly_income) if monthly_income > 0 else 0
    }