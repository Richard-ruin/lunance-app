from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from bson import ObjectId


class AchievementCriteria(BaseModel):
    type: str = Field(..., description="Criteria type: transaction_count, savings_goal, budget_adherence, streak")
    target_value: float = Field(..., description="Target value to achieve")
    period: str = Field(..., description="Time period: daily, weekly, monthly")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Additional conditions")


class Achievement(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    achievement_id: str = Field(..., description="Unique achievement identifier")
    name: str = Field(..., description="Achievement name")
    description: str = Field(..., description="Achievement description")
    icon: str = Field(..., description="Icon identifier for UI")
    
    # Achievement criteria
    criteria: AchievementCriteria = Field(..., description="Achievement criteria")
    
    # Rewards
    points: int = Field(..., description="Points awarded")
    badge_color: str = Field(..., description="Badge color")
    rarity: str = Field(..., description="Rarity: common, rare, epic, legendary")
    
    # Statistics
    earned_count: int = Field(0, description="Number of times this achievement has been earned")
    difficulty: str = Field(..., description="Difficulty: easy, medium, hard")
    
    is_active: bool = Field(True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# Predefined achievements for Indonesian students
STUDENT_ACHIEVEMENTS = [
    {
        "achievement_id": "first_transaction",
        "name": "Pencatat Pertama",
        "description": "Catat transaksi pertama kamu!",
        "icon": "📝",
        "criteria": {
            "type": "transaction_count",
            "target_value": 1,
            "period": "lifetime",
            "conditions": {}
        },
        "points": 10,
        "badge_color": "green",
        "rarity": "common",
        "difficulty": "easy"
    },
    {
        "achievement_id": "budget_keeper_week",
        "name": "Penjaga Budget Mingguan",
        "description": "Berhasil tidak overspending selama 1 minggu",
        "icon": "💰",
        "criteria": {
            "type": "budget_adherence",
            "target_value": 1.0,
            "period": "weekly",
            "conditions": {"consecutive": True}
        },
        "points": 25,
        "badge_color": "blue",
        "rarity": "common",
        "difficulty": "medium"
    },
    {
        "achievement_id": "saver_50k",
        "name": "Penabung Pemula",
        "description": "Berhasil menabung 50.000 rupiah",
        "icon": "🐷",
        "criteria": {
            "type": "savings_goal",
            "target_value": 50000,
            "period": "lifetime",
            "conditions": {}
        },
        "points": 50,
        "badge_color": "gold",
        "rarity": "rare",
        "difficulty": "medium"
    },
    {
        "achievement_id": "streak_master_30",
        "name": "Master Konsisten",
        "description": "Catat transaksi selama 30 hari berturut-turut",
        "icon": "🔥",
        "criteria": {
            "type": "streak",
            "target_value": 30,
            "period": "daily",
            "conditions": {"activity": "transaction_logging"}
        },
        "points": 100,
        "badge_color": "red",
        "rarity": "epic",
        "difficulty": "hard"
    },
    {
        "achievement_id": "goal_achiever",
        "name": "Pencapai Target",
        "description": "Berhasil mencapai target savings goal pertama",
        "icon": "🎯",
        "criteria": {
            "type": "savings_goal",
            "target_value": 1,
            "period": "lifetime",
            "conditions": {"completed_goals": 1}
        },
        "points": 75,
        "badge_color": "purple",
        "rarity": "rare",
        "difficulty": "medium"
    },
    {
        "achievement_id": "frugal_student",
        "name": "Mahasiswa Hemat",
        "description": "Pengeluaran di bawah rata-rata mahasiswa seurusan selama 1 bulan",
        "icon": "💎",
        "criteria": {
            "type": "budget_adherence",
            "target_value": 0.8,
            "period": "monthly",
            "conditions": {"comparison": "peer_average"}
        },
        "points": 60,
        "badge_color": "emerald",
        "rarity": "rare",
        "difficulty": "medium"
    },
    {
        "achievement_id": "expense_sharer",
        "name": "Teman Patungan",
        "description": "Berbagi pengeluaran dengan teman sebanyak 10 kali",
        "icon": "🤝",
        "criteria": {
            "type": "transaction_count",
            "target_value": 10,
            "period": "lifetime",
            "conditions": {"transaction_type": "shared_expense"}
        },
        "points": 40,
        "badge_color": "orange",
        "rarity": "common",
        "difficulty": "easy"
    },
    {
        "achievement_id": "semester_saver",
        "name": "Penabung Semester",
        "description": "Menabung konsisten selama 1 semester",
        "icon": "🎓",
        "criteria": {
            "type": "savings_goal",
            "target_value": 4,
            "period": "monthly",
            "conditions": {"consecutive": True, "minimum_amount": 25000}
        },
        "points": 150,
        "badge_color": "platinum",
        "rarity": "epic",
        "difficulty": "hard"
    },
    {
        "achievement_id": "legendary_saver",
        "name": "Penabung Legendaris",
        "description": "Berhasil menabung 1 juta rupiah",
        "icon": "👑",
        "criteria": {
            "type": "savings_goal",
            "target_value": 1000000,
            "period": "lifetime",
            "conditions": {}
        },
        "points": 500,
        "badge_color": "rainbow",
        "rarity": "legendary",
        "difficulty": "hard"
    },
    {
        "achievement_id": "early_bird",
        "name": "Bangun Pagi",
        "description": "Catat transaksi sebelum jam 8 pagi sebanyak 7 kali",
        "icon": "🌅",
        "criteria": {
            "type": "transaction_count",
            "target_value": 7,
            "period": "lifetime",
            "conditions": {"time_before": "08:00"}
        },
        "points": 30,
        "badge_color": "yellow",
        "rarity": "common",
        "difficulty": "easy"
    }
]