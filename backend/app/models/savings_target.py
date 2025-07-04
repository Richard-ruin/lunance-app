"""
SavingsTarget Model
Model untuk tracking target tabungan dan pencapaian finansial
"""

from datetime import datetime, date
from typing import Optional
from enum import Enum
from pydantic import Field, field_validator, model_validator
from beanie import Indexed

from .base import BaseDocument, SoftDeleteMixin, AuditMixin


class TargetStatus(str, Enum):
    """Status target tabungan"""
    ACTIVE = "active"
    ACHIEVED = "achieved"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class TargetPriority(str, Enum):
    """Prioritas target"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class SavingsTarget(BaseDocument, SoftDeleteMixin, AuditMixin):
    """
    Model Target Tabungan
    
    Features:
    - Multiple savings targets per user
    - Progress tracking
    - Target deadline
    - Priority system
    - Achievement rewards/badges
    
    Fields:
    - user_id: Reference ke User
    - target_name: Nama target tabungan
    - target_amount: Nominal target
    - target_date: Target deadline
    - current_amount: Jumlah yang sudah terkumpul
    - is_achieved: Status pencapaian
    - priority: Prioritas target
    - description: Deskripsi target
    - category: Kategori target (opsional)
    """
    
    # References
    user_id: Indexed(str) = Field(..., description="ID User")
    
    # Target Details
    target_name: str = Field(..., min_length=1, max_length=200, description="Nama target")
    target_amount: float = Field(..., gt=0, description="Nominal target")
    target_date: Indexed(date) = Field(..., description="Target deadline")
    
    # Progress Tracking
    current_amount: float = Field(default=0.0, ge=0, description="Jumlah terkumpul")
    is_achieved: bool = Field(default=False, description="Status pencapaian")
    achieved_date: Optional[datetime] = Field(default=None, description="Tanggal tercapai")
    
    # Target Properties
    priority: TargetPriority = Field(default=TargetPriority.MEDIUM, description="Prioritas target")
    status: TargetStatus = Field(default=TargetStatus.ACTIVE, description="Status target")
    description: Optional[str] = Field(default=None, max_length=1000, description="Deskripsi target")
    category: Optional[str] = Field(default=None, max_length=100, description="Kategori target")
    
    # UI/Motivation
    icon: Optional[str] = Field(default=None, max_length=50, description="Icon target")
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Warna target")
    motivation_note: Optional[str] = Field(default=None, max_length=500, description="Catatan motivasi")
    
    # Tracking
    last_contribution: Optional[datetime] = Field(default=None, description="Kontribusi terakhir")
    contribution_count: int = Field(default=0, ge=0, description="Jumlah kontribusi")
    
    # Reminder settings
    reminder_enabled: bool = Field(default=True, description="Enable reminder")
    reminder_frequency: Optional[str] = Field(default="weekly", pattern="^(daily|weekly|monthly)$", description="Frekuensi reminder")
    
    class Settings:
        name = "savings_targets"
        indexes = [
            "user_id",
            "target_date",
            "is_achieved",
            "status",
            "priority",
            [("user_id", 1), ("target_date", 1)],  # User targets by date
            [("user_id", 1), ("is_achieved", 1)],  # User targets by achievement
            [("user_id", 1), ("status", 1)],       # User targets by status
        ]
    
    @field_validator("target_name")
    @classmethod
    def validate_target_name(cls, v):
        """Validasi nama target"""
        if not v or not v.strip():
            raise ValueError("Nama target tidak boleh kosong")
        
        # Clean up name
        v = " ".join(v.strip().split())
        
        return v
    
    @field_validator("target_amount")
    @classmethod
    def validate_target_amount(cls, v):
        """Validasi nominal target"""
        if v <= 0:
            raise ValueError("Nominal target harus lebih dari 0")
        
        # Limit maksimum untuk mencegah input yang tidak realistis
        if v > 10_000_000_000:  # 10 Milyar
            raise ValueError("Nominal target terlalu besar")
        
        # Round ke 2 decimal places
        return round(v, 2)
    
    @field_validator("current_amount")
    @classmethod
    def validate_current_amount(cls, v):
        """Validasi jumlah terkumpul"""
        if v < 0:
            raise ValueError("Jumlah terkumpul tidak boleh negatif")
        
        # Round ke 2 decimal places
        return round(v, 2)
    
    @field_validator("target_date")
    @classmethod
    def validate_target_date(cls, v):
        """Validasi target deadline"""
        if not v:
            raise ValueError("Target deadline tidak boleh kosong")
        
        # Target date tidak boleh di masa lalu
        if v < date.today():
            raise ValueError("Target deadline tidak boleh di masa lalu")
        
        # Target date tidak boleh terlalu jauh (misalnya 20 tahun)
        max_date = date.today().replace(year=date.today().year + 20)
        if v > max_date:
            raise ValueError("Target deadline terlalu jauh di masa depan")
        
        return v
    
    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        """Validasi hex color code"""
        if not v:
            return v
        
        v = v.strip().upper()
        
        # Ensure starts with #
        if not v.startswith("#"):
            v = "#" + v
        
        return v
    
    @field_validator("reminder_frequency")
    @classmethod
    def validate_reminder_frequency(cls, v):
        """Validasi frekuensi reminder"""
        if not v:
            return v
        
        valid_frequencies = ["daily", "weekly", "monthly"]
        if v not in valid_frequencies:
            raise ValueError(f"Frekuensi reminder harus salah satu dari: {valid_frequencies}")
        
        return v
    
    @model_validator(mode="after")
    def validate_target_consistency(self):
        """Validasi konsistensi data target"""
        # Jika current_amount >= target_amount, otomatis achieved
        if self.current_amount >= self.target_amount and not self.is_achieved:
            self.is_achieved = True
            self.status = TargetStatus.ACHIEVED
            if not self.achieved_date:
                self.achieved_date = datetime.utcnow()
        
        # Jika sudah achieved tapi current_amount < target_amount
        elif self.is_achieved and self.current_amount < self.target_amount:
            self.is_achieved = False
            self.achieved_date = None
            if self.status == TargetStatus.ACHIEVED:
                self.status = TargetStatus.ACTIVE
        
        return self
    
    def get_progress_percentage(self) -> float:
        """Get progress dalam bentuk persentase"""
        if self.target_amount <= 0:
            return 0.0
        
        percentage = (self.current_amount / self.target_amount) * 100
        return min(percentage, 100.0)  # Cap at 100%
    
    def get_remaining_amount(self) -> float:
        """Get sisa nominal yang perlu dikumpulkan"""
        remaining = self.target_amount - self.current_amount
        return max(remaining, 0.0)  # Tidak boleh negatif
    
    def get_days_remaining(self) -> int:
        """Get sisa hari sampai deadline"""
        today = date.today()
        if self.target_date <= today:
            return 0
        
        delta = self.target_date - today
        return delta.days
    
    def get_daily_savings_needed(self) -> float:
        """Get nominal yang perlu ditabung per hari"""
        days_remaining = self.get_days_remaining()
        if days_remaining <= 0:
            return 0.0
        
        remaining_amount = self.get_remaining_amount()
        return remaining_amount / days_remaining
    
    def is_overdue(self) -> bool:
        """Check apakah target sudah melewati deadline"""
        return date.today() > self.target_date and not self.is_achieved
    
    def is_near_deadline(self, days_threshold: int = 7) -> bool:
        """Check apakah mendekati deadline"""
        days_remaining = self.get_days_remaining()
        return 0 < days_remaining <= days_threshold and not self.is_achieved
    
    def get_status_color(self) -> str:
        """Get warna berdasarkan status"""
        if self.is_achieved:
            return "#4CAF50"  # Green
        elif self.is_overdue():
            return "#F44336"  # Red
        elif self.is_near_deadline():
            return "#FF9800"  # Orange
        else:
            return "#2196F3"  # Blue
    
    def get_motivation_message(self) -> str:
        """Get pesan motivasi berdasarkan progress"""
        progress = self.get_progress_percentage()
        
        if self.is_achieved:
            return "🎉 Selamat! Target berhasil dicapai!"
        elif progress >= 90:
            return "💪 Hampir sampai! Sedikit lagi!"
        elif progress >= 75:
            return "⭐ Bagus sekali! Terus semangat!"
        elif progress >= 50:
            return "👍 Sudah setengah jalan! Lanjutkan!"
        elif progress >= 25:
            return "🚀 Awal yang baik! Terus menabung!"
        else:
            return "📈 Mulai menabung untuk mencapai target!"
    
    async def add_contribution(self, amount: float, description: Optional[str] = None):
        """Tambah kontribusi ke target"""
        if amount <= 0:
            raise ValueError("Nominal kontribusi harus lebih dari 0")
        
        self.current_amount += amount
        self.contribution_count += 1
        self.last_contribution = datetime.utcnow()
        
        # Check if target achieved
        if self.current_amount >= self.target_amount and not self.is_achieved:
            self.is_achieved = True
            self.status = TargetStatus.ACHIEVED
            self.achieved_date = datetime.utcnow()
        
        await self.save_with_timestamp()
    
    async def subtract_contribution(self, amount: float, description: Optional[str] = None):
        """Kurangi kontribusi dari target (untuk koreksi)"""
        if amount <= 0:
            raise ValueError("Nominal pengurangan harus lebih dari 0")
        
        if amount > self.current_amount:
            raise ValueError("Nominal pengurangan melebihi jumlah terkumpul")
        
        self.current_amount -= amount
        
        # Check if no longer achieved
        if self.current_amount < self.target_amount and self.is_achieved:
            self.is_achieved = False
            self.status = TargetStatus.ACTIVE
            self.achieved_date = None
        
        await self.save_with_timestamp()
    
    async def complete(self):
        """Mark target sebagai achieved"""
        self.is_achieved = True
        self.status = TargetStatus.ACHIEVED
        self.achieved_date = datetime.utcnow()
        await self.save_with_timestamp()
    
    async def cancel(self):
        """Cancel target"""
        self.status = TargetStatus.CANCELLED
        await self.save_with_timestamp()
    
    async def reactivate(self):
        """Reactivate cancelled target"""
        if self.status == TargetStatus.CANCELLED:
            self.status = TargetStatus.ACTIVE
            await self.save_with_timestamp()
    
    async def extend_deadline(self, new_date: date):
        """Extend target deadline"""
        if new_date <= self.target_date:
            raise ValueError("Deadline baru harus lebih dari deadline saat ini")
        
        if new_date < date.today():
            raise ValueError("Deadline baru tidak boleh di masa lalu")
        
        self.target_date = new_date
        
        # Reactivate if expired
        if self.status == TargetStatus.EXPIRED:
            self.status = TargetStatus.ACTIVE
        
        await self.save_with_timestamp()
    
    @classmethod
    async def find_by_user(
        cls, 
        user_id: str, 
        status: Optional[TargetStatus] = None,
        is_achieved: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ):
        """Find targets by user dengan filter"""
        query = {
            "user_id": user_id,
            "is_deleted": {"$ne": True}
        }
        
        if status:
            query["status"] = status
        
        if is_achieved is not None:
            query["is_achieved"] = is_achieved
        
        return await cls.find(query).sort([("target_date", 1)]).skip(skip).limit(limit).to_list()
    
    @classmethod
    async def find_active_targets(cls, user_id: str):
        """Find active targets untuk user"""
        return await cls.find({
            "user_id": user_id,
            "status": TargetStatus.ACTIVE,
            "is_deleted": {"$ne": True}
        }).sort("target_date").to_list()
    
    @classmethod
    async def find_achieved_targets(cls, user_id: str):
        """Find achieved targets untuk user"""
        return await cls.find({
            "user_id": user_id,
            "is_achieved": True,
            "is_deleted": {"$ne": True}
        }).sort([("achieved_date", -1)]).to_list()
    
    @classmethod
    async def find_overdue_targets(cls, user_id: Optional[str] = None):
        """Find overdue targets"""
        query = {
            "target_date": {"$lt": date.today()},
            "is_achieved": False,
            "status": TargetStatus.ACTIVE,
            "is_deleted": {"$ne": True}
        }
        
        if user_id:
            query["user_id"] = user_id
        
        return await cls.find(query).to_list()
    
    @classmethod
    async def get_user_summary(cls, user_id: str) -> dict:
        """Get summary targets untuk user"""
        targets = await cls.find({
            "user_id": user_id,
            "is_deleted": {"$ne": True}
        }).to_list()
        
        total_targets = len(targets)
        achieved_targets = len([t for t in targets if t.is_achieved])
        active_targets = len([t for t in targets if t.status == TargetStatus.ACTIVE])
        total_target_amount = sum(t.target_amount for t in targets)
        total_saved_amount = sum(t.current_amount for t in targets)
        
        return {
            "total_targets": total_targets,
            "achieved_targets": achieved_targets,
            "active_targets": active_targets,
            "achievement_rate": (achieved_targets / total_targets * 100) if total_targets > 0 else 0,
            "total_target_amount": total_target_amount,
            "total_saved_amount": total_saved_amount,
            "savings_progress": (total_saved_amount / total_target_amount * 100) if total_target_amount > 0 else 0
        }
    
    @classmethod
    async def update_expired_targets(cls):
        """Update status target yang sudah expired (background job)"""
        overdue_targets = await cls.find({
            "target_date": {"$lt": date.today()},
            "is_achieved": False,
            "status": TargetStatus.ACTIVE
        }).to_list()
        
        for target in overdue_targets:
            target.status = TargetStatus.EXPIRED
            await target.save_with_timestamp()
        
        return len(overdue_targets)