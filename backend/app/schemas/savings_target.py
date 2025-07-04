"""
SavingsTarget Schemas
Schemas untuk target tabungan dan pencapaian finansial
"""

from datetime import datetime, date
from typing import Optional
from pydantic import Field, field_validator
from enum import Enum

from .base import BaseSchema, BaseResponse, BaseCreate, BaseUpdate, BaseFilter
from ..models.savings_target import TargetStatus, TargetPriority


# Enums for schemas
class TargetStatusSchema(str, Enum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class TargetPrioritySchema(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Base SavingsTarget Schema
class SavingsTargetBase(BaseSchema):
    """Base savings target schema"""
    target_name: str = Field(..., min_length=1, max_length=200, description="Nama target")
    target_amount: float = Field(..., gt=0, description="Nominal target")
    target_date: date = Field(..., description="Target deadline")
    priority: TargetPrioritySchema = Field(default=TargetPrioritySchema.MEDIUM, description="Prioritas target")
    description: Optional[str] = Field(default=None, max_length=1000, description="Deskripsi target")
    category: Optional[str] = Field(default=None, max_length=100, description="Kategori target")
    icon: Optional[str] = Field(default=None, max_length=50, description="Icon target")
    color: Optional[str] = Field(default=None, description="Warna target")
    motivation_note: Optional[str] = Field(default=None, max_length=500, description="Catatan motivasi")
    reminder_enabled: bool = Field(default=True, description="Enable reminder")
    reminder_frequency: Optional[str] = Field(default="weekly", description="Frekuensi reminder")
    
    @field_validator("target_name")
    @classmethod
    def validate_target_name(cls, v):
        """Validasi nama target"""
        if not v or not v.strip():
            raise ValueError("Nama target tidak boleh kosong")
        
        return " ".join(v.strip().split())
    
    @field_validator("target_amount")
    @classmethod
    def validate_target_amount(cls, v):
        """Validasi nominal target"""
        if v <= 0:
            raise ValueError("Nominal target harus lebih dari 0")
        
        if v > 10_000_000_000:  # 10 Milyar
            raise ValueError("Nominal target terlalu besar")
        
        return round(v, 2)
    
    @field_validator("target_date")
    @classmethod
    def validate_target_date(cls, v):
        """Validasi target deadline"""
        if v < date.today():
            raise ValueError("Target deadline tidak boleh di masa lalu")
        
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
        
        if not v.startswith("#"):
            v = "#" + v
        
        if len(v) != 7 or not all(c in "0123456789ABCDEF" for c in v[1:]):
            raise ValueError("Color harus dalam format hex 6 digit")
        
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
    @validator("target_amount")
    def validate_target_amount(cls, v):
        """Validasi nominal target"""
        if v <= 0:
            raise ValueError("Nominal target harus lebih dari 0")
        
        if v > 10_000_000_000:  # 10 Milyar
            raise ValueError("Nominal target terlalu besar")
        
        return round(v, 2)
    
    @validator("target_date")
    def validate_target_date(cls, v):
        """Validasi target deadline"""
        if v < date.today():
            raise ValueError("Target deadline tidak boleh di masa lalu")
        
        max_date = date.today().replace(year=date.today().year + 20)
        if v > max_date:
            raise ValueError("Target deadline terlalu jauh di masa depan")
        
        return v
    
    @validator("color")
    def validate_color(cls, v):
        """Validasi hex color code"""
        if not v:
            return v
        
        v = v.strip().upper()
        
        if not v.startswith("#"):
            v = "#" + v
        
        if len(v) != 7 or not all(c in "0123456789ABCDEF" for c in v[1:]):
            raise ValueError("Color harus dalam format hex 6 digit")
        
        return v
    
    @validator("reminder_frequency")
    def validate_reminder_frequency(cls, v):
        """Validasi frekuensi reminder"""
        if not v:
            return v
        
        valid_frequencies = ["daily", "weekly", "monthly"]
        if v not in valid_frequencies:
            raise ValueError(f"Frekuensi reminder harus salah satu dari: {valid_frequencies}")
        
        return v


class SavingsTargetCreate(SavingsTargetBase):
    """Schema untuk create savings target"""
    current_amount: float = Field(default=0.0, ge=0, description="Jumlah awal terkumpul")
    
    @validator("current_amount")
    def validate_current_amount(cls, v):
        """Validasi jumlah awal"""
        if v < 0:
            raise ValueError("Jumlah awal tidak boleh negatif")
        
        return round(v, 2)


class SavingsTargetUpdate(BaseSchema):
    """Schema untuk update savings target"""
    target_name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="Nama target")
    target_amount: Optional[float] = Field(default=None, gt=0, description="Nominal target")
    target_date: Optional[date] = Field(default=None, description="Target deadline")
    priority: Optional[TargetPrioritySchema] = Field(default=None, description="Prioritas")
    description: Optional[str] = Field(default=None, max_length=1000, description="Deskripsi")
    category: Optional[str] = Field(default=None, max_length=100, description="Kategori")
    icon: Optional[str] = Field(default=None, max_length=50, description="Icon")
    color: Optional[str] = Field(default=None, description="Warna")
    motivation_note: Optional[str] = Field(default=None, max_length=500, description="Catatan motivasi")
    reminder_enabled: Optional[bool] = Field(default=None, description="Enable reminder")
    reminder_frequency: Optional[str] = Field(default=None, description="Frekuensi reminder")
    
    @field_validator("target_amount")
    @classmethod
    def validate_target_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError("Nominal target harus lebih dari 0")
            if v > 10_000_000_000:
                raise ValueError("Nominal target terlalu besar")
            return round(v, 2)
        return v
    
    @field_validator("target_date")
    @classmethod
    def validate_target_date(cls, v):
        if v is not None:
            if v < date.today():
                raise ValueError("Target deadline tidak boleh di masa lalu")
        return v


class SavingsTargetResponse(SavingsTargetBase, BaseResponse):
    """Schema untuk response savings target"""
    user_id: str = Field(..., description="ID User")
    current_amount: float = Field(..., description="Jumlah terkumpul")
    is_achieved: bool = Field(..., description="Status pencapaian")
    achieved_date: Optional[datetime] = Field(default=None, description="Tanggal tercapai")
    status: TargetStatusSchema = Field(..., description="Status target")
    last_contribution: Optional[datetime] = Field(default=None, description="Kontribusi terakhir")
    contribution_count: int = Field(..., description="Jumlah kontribusi")


class SavingsTargetDetailResponse(SavingsTargetResponse):
    """Schema untuk response savings target detail dengan analytics"""
    progress_percentage: float = Field(..., description="Persentase progress")
    remaining_amount: float = Field(..., description="Sisa nominal")
    days_remaining: int = Field(..., description="Sisa hari")
    daily_savings_needed: float = Field(..., description="Nominal per hari yang dibutuhkan")
    is_overdue: bool = Field(..., description="Apakah overdue")
    is_near_deadline: bool = Field(..., description="Apakah mendekati deadline")
    status_color: str = Field(..., description="Warna status")
    motivation_message: str = Field(..., description="Pesan motivasi")


# Contribution Operations
class SavingsContribution(BaseSchema):
    """Schema untuk kontribusi savings"""
    target_id: str = Field(..., description="ID target")
    amount: float = Field(..., gt=0, description="Nominal kontribusi")
    description: Optional[str] = Field(default=None, max_length=500, description="Deskripsi kontribusi")
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Nominal kontribusi harus lebih dari 0")
        
        if v > 100_000_000:  # 100 Juta per kontribusi
            raise ValueError("Nominal kontribusi terlalu besar")
        
        return round(v, 2)


class SavingsWithdrawal(BaseSchema):
    """Schema untuk penarikan dari savings"""
    target_id: str = Field(..., description="ID target")
    amount: float = Field(..., gt=0, description="Nominal penarikan")
    reason: str = Field(..., min_length=1, max_length=500, description="Alasan penarikan")
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Nominal penarikan harus lebih dari 0")
        
        return round(v, 2)


class SavingsTargetExtend(BaseSchema):
    """Schema untuk extend deadline target"""
    target_id: str = Field(..., description="ID target")
    new_date: date = Field(..., description="Deadline baru")
    reason: Optional[str] = Field(default=None, max_length=500, description="Alasan perpanjangan")
    
    @field_validator("new_date")
    @classmethod
    def validate_new_date(cls, v):
        if v < date.today():
            raise ValueError("Deadline baru tidak boleh di masa lalu")
        
        return v


# Filter Schemas
class SavingsTargetFilter(BaseFilter):
    """Schema untuk filter savings target"""
    user_id: Optional[str] = Field(default=None, description="Filter user")
    status: Optional[TargetStatusSchema] = Field(default=None, description="Filter status")
    priority: Optional[TargetPrioritySchema] = Field(default=None, description="Filter prioritas")
    is_achieved: Optional[bool] = Field(default=None, description="Filter pencapaian")
    category: Optional[str] = Field(default=None, description="Filter kategori")
    start_date: Optional[date] = Field(default=None, description="Target date mulai")
    end_date: Optional[date] = Field(default=None, description="Target date akhir")
    min_amount: Optional[float] = Field(default=None, ge=0, description="Nominal minimum")
    max_amount: Optional[float] = Field(default=None, ge=0, description="Nominal maksimum")


class SavingsTargetUserFilter(BaseSchema):
    """Schema untuk filter savings target user"""
    status: Optional[TargetStatusSchema] = Field(default=None, description="Filter status")
    is_achieved: Optional[bool] = Field(default=None, description="Filter pencapaian")
    page: int = Field(default=1, ge=1, description="Halaman")
    per_page: int = Field(default=10, ge=1, le=100, description="Item per halaman")


# Bulk Operations
class SavingsTargetBulkUpdate(BaseSchema):
    """Schema untuk bulk update savings targets"""
    target_ids: list[str] = Field(..., min_length=1, description="List ID target")
    data: SavingsTargetUpdate = Field(..., description="Data untuk update")


class SavingsTargetBulkStatusUpdate(BaseSchema):
    """Schema untuk bulk update status targets"""
    target_ids: list[str] = Field(..., min_length=1, description="List ID target")
    status: TargetStatusSchema = Field(..., description="Status baru")
    reason: Optional[str] = Field(default=None, description="Alasan perubahan")


class SavingsTargetBulkDelete(BaseSchema):
    """Schema untuk bulk delete targets"""
    target_ids: list[str] = Field(..., min_length=1, description="List ID target")
    permanent: bool = Field(default=False, description="Hapus permanen")


# Statistics & Analytics
class SavingsTargetStatsResponse(BaseSchema):
    """Schema untuk statistik savings target"""
    total_targets: int = Field(..., description="Total target")
    active_targets: int = Field(..., description="Target aktif")
    achieved_targets: int = Field(..., description="Target tercapai")
    expired_targets: int = Field(..., description="Target kadaluarsa")
    total_target_amount: float = Field(..., description="Total nominal target")
    total_saved_amount: float = Field(..., description="Total nominal terkumpul")
    achievement_rate: float = Field(..., description="Tingkat pencapaian (%)")
    average_target_amount: float = Field(..., description="Rata-rata nominal target")


class SavingsTargetUserSummary(BaseSchema):
    """Schema untuk summary savings target user"""
    total_targets: int = Field(..., description="Total target")
    achieved_targets: int = Field(..., description="Target tercapai")
    active_targets: int = Field(..., description="Target aktif")
    achievement_rate: float = Field(..., description="Tingkat pencapaian")
    total_target_amount: float = Field(..., description="Total target amount")
    total_saved_amount: float = Field(..., description="Total saved amount")
    savings_progress: float = Field(..., description="Progress tabungan keseluruhan")
    upcoming_deadlines: list[SavingsTargetResponse] = Field(..., description="Target dengan deadline terdekat")


class SavingsProgress(BaseSchema):
    """Schema untuk progress savings"""
    target_id: str = Field(..., description="ID target")
    target_name: str = Field(..., description="Nama target")
    target_amount: float = Field(..., description="Nominal target")
    current_amount: float = Field(..., description="Nominal terkumpul")
    progress_percentage: float = Field(..., description="Persentase progress")
    days_remaining: int = Field(..., description="Sisa hari")
    daily_savings_needed: float = Field(..., description="Nominal harian yang dibutuhkan")
    status: TargetStatusSchema = Field(..., description="Status")
    priority: TargetPrioritySchema = Field(..., description="Prioritas")


class SavingsAnalytics(BaseSchema):
    """Schema untuk analytics savings"""
    period: str = Field(..., description="Periode analisis")
    total_contributions: float = Field(..., description="Total kontribusi")
    average_contribution: float = Field(..., description="Rata-rata kontribusi")
    contribution_frequency: float = Field(..., description="Frekuensi kontribusi")
    savings_rate: float = Field(..., description="Tingkat menabung")
    category_breakdown: list[dict] = Field(..., description="Breakdown per kategori")
    monthly_trend: list[dict] = Field(..., description="Trend bulanan")
    achievement_patterns: dict = Field(..., description="Pola pencapaian")


# Achievement & Rewards
class SavingsAchievement(BaseSchema):
    """Schema untuk achievement/badge"""
    achievement_id: str = Field(..., description="ID achievement")
    name: str = Field(..., description="Nama achievement")
    description: str = Field(..., description="Deskripsi achievement")
    icon: str = Field(..., description="Icon achievement")
    earned_at: datetime = Field(..., description="Waktu mendapat achievement")
    target_id: Optional[str] = Field(default=None, description="ID target terkait")


class SavingsReward(BaseSchema):
    """Schema untuk reward"""
    reward_id: str = Field(..., description="ID reward")
    name: str = Field(..., description="Nama reward")
    description: str = Field(..., description="Deskripsi reward")
    points_required: int = Field(..., description="Poin yang dibutuhkan")
    is_claimed: bool = Field(..., description="Apakah sudah diklaim")


# Templates & Suggestions
class SavingsTargetTemplate(BaseSchema):
    """Schema untuk template target"""
    template_id: str = Field(..., description="ID template")
    name: str = Field(..., description="Nama template")
    description: str = Field(..., description="Deskripsi template")
    suggested_amount: float = Field(..., description="Nominal yang disarankan")
    suggested_duration_months: int = Field(..., description="Durasi yang disarankan (bulan)")
    category: str = Field(..., description="Kategori template")
    icon: str = Field(..., description="Icon template")
    color: str = Field(..., description="Warna template")


class SavingsTargetSuggestion(BaseSchema):
    """Schema untuk suggestion target berdasarkan analisis"""
    suggestion_type: str = Field(..., description="Tipe suggestion")
    title: str = Field(..., description="Judul suggestion")
    description: str = Field(..., description="Deskripsi suggestion")
    suggested_amount: float = Field(..., description="Nominal yang disarankan")
    suggested_deadline: date = Field(..., description="Deadline yang disarankan")
    reason: str = Field(..., description="Alasan suggestion")
    confidence_score: float = Field(..., ge=0, le=1, description="Skor confidence (0-1)")
    template: Optional[SavingsTargetTemplate] = Field(default=None, description="Template terkait")


# Reminders & Notifications
class SavingsReminder(BaseSchema):
    """Schema untuk reminder settings"""
    target_id: str = Field(..., description="ID target")
    reminder_type: str = Field(..., description="Tipe reminder")
    frequency: str = Field(..., description="Frekuensi reminder")
    next_reminder: datetime = Field(..., description="Waktu reminder berikutnya")
    is_enabled: bool = Field(..., description="Status reminder")


class SavingsNotification(BaseSchema):
    """Schema untuk notification"""
    notification_id: str = Field(..., description="ID notification")
    target_id: str = Field(..., description="ID target")
    type: str = Field(..., description="Tipe notification")
    title: str = Field(..., description="Judul notification")
    message: str = Field(..., description="Pesan notification")
    is_read: bool = Field(..., description="Status dibaca")
    created_at: datetime = Field(..., description="Waktu dibuat")