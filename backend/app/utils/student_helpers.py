import os
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from PIL import Image
import aiofiles
from fastapi import UploadFile

from app.models.student import Student
from app.config.settings import settings
from app.core.exceptions import FileUploadException
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

# Student expense categories
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

# Achievement definitions
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
        upload_dir = os.path.join(settings.UPLOAD_DIR, "profile_pictures")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ['.jpg', '.jpeg', '.png']:
            raise FileUploadException("Unsupported file format. Use JPG, JPEG, or PNG.")
        
        filename = f"{user_id}_{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save original file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Process image (resize, optimize)
        await optimize_profile_picture(file_path)
        
        # Return URL path
        return f"/static/uploads/profile_pictures/{filename}"
        
    except Exception as e:
        logger.error(f"Profile picture processing error: {str(e)}")
        raise FileUploadException(f"Failed to process profile picture: {str(e)}")


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
    # Level progression: Level 1 = 0-99 points, Level 2 = 100-299, Level 3 = 300-599, etc.
    if experience_points < 100:
        return 1
    elif experience_points < 300:
        return 2
    elif experience_points < 600:
        return 3
    elif experience_points < 1000:
        return 4
    elif experience_points < 1500:
        return 5
    else:
        # Advanced levels: every 500 points = 1 level
        return 6 + ((experience_points - 1500) // 500)


async def update_user_achievements(student: Student, achievement_trigger: str) -> List[str]:
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