"""
User Model
Model untuk manajemen user (admin & mahasiswa) dengan validasi lengkap
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import Field, EmailStr, field_validator, model_validator
from beanie import Indexed

from .base import BaseDocument, SoftDeleteMixin, AuditMixin
from ..config.settings import settings


class UserRole(str, Enum):
    """Enum untuk role user"""
    ADMIN = "admin"
    STUDENT = "student"  # mahasiswa


class UserStatus(str, Enum):
    """Enum untuk status user"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(BaseDocument, SoftDeleteMixin, AuditMixin):
    """
    User model untuk admin dan mahasiswa
    
    Fields:
    - email: Email user (wajib .ac.id untuk mahasiswa)
    - full_name: Nama lengkap
    - phone_number: Nomor telepon
    - university_id: Reference ke University
    - faculty_id: Reference ke Faculty  
    - department_id: Reference ke Department (jurusan)
    - role: Role user (admin/student)
    - status: Status aktif user
    - initial_savings: Saldo awal tabungan
    - profile_picture: URL foto profil
    - email_verified: Status verifikasi email
    - last_login: Timestamp login terakhir
    """
    
    # Basic Information
    email: Indexed(EmailStr, unique=True) = Field(..., description="Email user")
    full_name: str = Field(..., min_length=2, max_length=100, description="Nama lengkap")
    phone_number: Optional[str] = Field(
        default=None, 
        pattern=r"^(\+62|62|0)[0-9]{9,13}$",
        description="Nomor telepon Indonesia"
    )
    
    # University Information (required for students)
    university_id: Optional[str] = Field(default=None, description="ID Universitas")
    faculty_id: Optional[str] = Field(default=None, description="ID Fakultas")
    department_id: Optional[str] = Field(default=None, description="ID Jurusan")
    
    # User Management
    role: UserRole = Field(default=UserRole.STUDENT, description="Role user")
    status: UserStatus = Field(default=UserStatus.PENDING_VERIFICATION, description="Status user")
    
    # Financial Information
    initial_savings: float = Field(default=0.0, ge=0, description="Saldo awal tabungan")
    
    # Profile Information
    profile_picture: Optional[str] = Field(default=None, description="URL foto profil")
    bio: Optional[str] = Field(default=None, max_length=500, description="Biografi singkat")
    
    # Verification & Security
    email_verified: bool = Field(default=False, description="Status verifikasi email")
    email_verified_at: Optional[datetime] = Field(default=None, description="Waktu verifikasi email")
    last_login: Optional[datetime] = Field(default=None, description="Login terakhir")
    login_count: int = Field(default=0, description="Jumlah login")
    
    # Password hash akan ditambahkan nanti saat implementasi auth
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "university_id",
            "faculty_id", 
            "department_id",
            "role",
            "status",
            "email_verified"
        ]
    
    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, v, info):
        """Validasi domain email untuk mahasiswa harus .ac.id"""
        if not v:
            return v
            
        # Get role from values, default to STUDENT
        role = info.data.get("role", UserRole.STUDENT) if info.data else UserRole.STUDENT
        
        # Jika role adalah student, email harus .ac.id
        if role == UserRole.STUDENT:
            if not any(v.endswith(f".{domain}") for domain in settings.valid_university_domains):
                raise ValueError(
                    f"Email mahasiswa harus menggunakan domain universitas: {settings.valid_university_domains}"
                )
        
        return v.lower()
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        """Validasi nama lengkap"""
        if not v or not v.strip():
            raise ValueError("Nama lengkap tidak boleh kosong")
        
        # Remove extra spaces and title case
        v = " ".join(v.strip().split())
        
        # Basic validation untuk karakter
        if not all(c.isalpha() or c.isspace() or c in "'.,-" for c in v):
            raise ValueError("Nama lengkap hanya boleh berisi huruf, spasi, dan karakter khusus (', ., -, ')")
        
        return v
    
    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        """Validasi nomor telepon Indonesia"""
        if not v:
            return v
        
        # Remove spaces and dashes
        v = v.replace(" ", "").replace("-", "")
        
        # Normalize Indonesian phone numbers
        if v.startswith("0"):
            v = "+62" + v[1:]
        elif v.startswith("62"):
            v = "+" + v
        elif not v.startswith("+62"):
            v = "+62" + v
        
        return v
    
    @model_validator(mode="after")
    def validate_student_requirements(self):
        """Validasi requirements untuk mahasiswa"""
        if self.role == UserRole.STUDENT:
            # Mahasiswa harus punya university_id, faculty_id, department_id
            required_fields = ["university_id", "faculty_id", "department_id"]
            missing_fields = [field for field in required_fields if not getattr(self, field)]
            
            if missing_fields:
                raise ValueError(
                    f"Mahasiswa harus memiliki: {', '.join(missing_fields)}"
                )
        
        return self
    
    @field_validator("initial_savings")
    @classmethod
    def validate_initial_savings(cls, v):
        """Validasi saldo awal"""
        if v < 0:
            raise ValueError("Saldo awal tidak boleh negatif")
        
        # Limit maksimum untuk mencegah input yang tidak realistis
        if v > 1_000_000_000:  # 1 Milyar
            raise ValueError("Saldo awal terlalu besar")
        
        return round(v, 2)  # Round to 2 decimal places
    
    def is_student(self) -> bool:
        """Check apakah user adalah mahasiswa"""
        return self.role == UserRole.STUDENT
    
    def is_admin(self) -> bool:
        """Check apakah user adalah admin"""
        return self.role == UserRole.ADMIN
    
    def is_active(self) -> bool:
        """Check apakah user aktif"""
        return self.status == UserStatus.ACTIVE and not self.is_deleted
    
    def is_verified(self) -> bool:
        """Check apakah email sudah diverifikasi"""
        return self.email_verified
    
    async def verify_email(self):
        """Verifikasi email user"""
        self.email_verified = True
        self.email_verified_at = datetime.utcnow()
        if self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE
        await self.save_with_timestamp()
    
    async def activate(self):
        """Aktivasi user"""
        self.status = UserStatus.ACTIVE
        await self.save_with_timestamp()
    
    async def deactivate(self):
        """Deaktivasi user"""
        self.status = UserStatus.INACTIVE
        await self.save_with_timestamp()
    
    async def suspend(self):
        """Suspend user"""
        self.status = UserStatus.SUSPENDED
        await self.save_with_timestamp()
    
    async def update_login(self):
        """Update informasi login terakhir"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        await self.save_with_timestamp()
    
    def get_display_name(self) -> str:
        """Get nama untuk display"""
        return self.full_name or self.email.split("@")[0]
    
    def get_university_info(self) -> dict:
        """Get informasi universitas (akan diimplementasi dengan join nanti)"""
        return {
            "university_id": self.university_id,
            "faculty_id": self.faculty_id,
            "department_id": self.department_id
        }
    
    @classmethod
    async def find_by_email(cls, email: str) -> Optional["User"]:
        """Find user by email"""
        return await cls.find_one({"email": email.lower()})
    
    @classmethod
    async def find_active_students(cls, skip: int = 0, limit: int = 100):
        """Find active students"""
        return await cls.find(
            {
                "role": UserRole.STUDENT,
                "status": UserStatus.ACTIVE,
                "is_deleted": {"$ne": True}
            }
        ).skip(skip).limit(limit).to_list()
    
    @classmethod
    async def find_by_university(cls, university_id: str, skip: int = 0, limit: int = 100):
        """Find users by university"""
        return await cls.find(
            {
                "university_id": university_id,
                "is_deleted": {"$ne": True}
            }
        ).skip(skip).limit(limit).to_list()
    
    @classmethod
    async def count_by_role(cls) -> dict:
        """Count users by role"""
        pipeline = [
            {"$match": {"is_deleted": {"$ne": True}}},
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ]
        
        result = await cls.aggregate(pipeline).to_list()
        counts = {item["_id"]: item["count"] for item in result}
        
        return {
            "total": sum(counts.values()),
            "students": counts.get(UserRole.STUDENT, 0),
            "admins": counts.get(UserRole.ADMIN, 0)
        }
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert to dict dengan option untuk include sensitive data"""
        data = super().to_dict()
        
        if not include_sensitive:
            # Remove sensitive fields
            sensitive_fields = ["created_by", "updated_by"]
            for field in sensitive_fields:
                data.pop(field, None)
        
        return data