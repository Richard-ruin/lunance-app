"""
University, Faculty, Department Models
Model untuk manajemen data institusi pendidikan dengan approval system
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import Field, field_validator, HttpUrl
from beanie import Indexed

from .base import BaseDocument, SoftDeleteMixin, AuditMixin


class ApprovalStatus(str, Enum):
    """Status approval untuk institusi"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class University(BaseDocument, SoftDeleteMixin, AuditMixin):
    """
    Model Universitas dengan approval system
    
    Fields:
    - name: Nama universitas
    - domain: Domain email universitas (contoh: ui.ac.id)
    - is_approved: Status approval
    - approval_status: Status approval detail
    - website: Website resmi
    - address: Alamat lengkap
    - phone: Nomor telepon
    - logo_url: URL logo universitas
    """
    
    name: Indexed(str) = Field(..., min_length=3, max_length=200, description="Nama universitas")
    domain: Indexed(str, unique=True) = Field(..., description="Domain email universitas")
    
    # Approval System
    is_approved: bool = Field(default=False, description="Status approval (backward compatibility)")
    approval_status: ApprovalStatus = Field(default=ApprovalStatus.PENDING, description="Status approval detail")
    approved_by: Optional[str] = Field(default=None, description="ID admin yang approve")
    approved_at: Optional[datetime] = Field(default=None, description="Waktu approval")
    rejection_reason: Optional[str] = Field(default=None, description="Alasan penolakan")
    
    # Contact Information
    website: Optional[HttpUrl] = Field(default=None, description="Website resmi")
    email: Optional[str] = Field(default=None, description="Email kontak resmi")
    phone: Optional[str] = Field(default=None, description="Nomor telepon")
    
    # Address
    address: Optional[str] = Field(default=None, max_length=500, description="Alamat lengkap")
    city: Optional[str] = Field(default=None, description="Kota")
    province: Optional[str] = Field(default=None, description="Provinsi")
    postal_code: Optional[str] = Field(default=None, description="Kode pos")
    
    # Additional Info
    logo_url: Optional[str] = Field(default=None, description="URL logo universitas")
    description: Optional[str] = Field(default=None, max_length=1000, description="Deskripsi singkat")
    established_year: Optional[int] = Field(default=None, ge=1900, le=2030, description="Tahun berdiri")
    
    # Statistics
    student_count: int = Field(default=0, ge=0, description="Jumlah mahasiswa terdaftar")
    faculty_count: int = Field(default=0, ge=0, description="Jumlah fakultas")
    
    class Settings:
        name = "universities"
        indexes = [
            "name",
            "domain",
            "is_approved",
            "approval_status",
            "city",
            "province"
        ]
    
    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v):
        """Validasi format domain universitas"""
        if not v:
            raise ValueError("Domain tidak boleh kosong")
        
        v = v.lower().strip()
        
        # Harus berakhiran .ac.id untuk universitas Indonesia
        if not v.endswith(".ac.id"):
            raise ValueError("Domain universitas harus berakhiran .ac.id")
        
        # Basic domain format validation
        if not v.replace(".", "").replace("-", "").isalnum():
            raise ValueError("Domain hanya boleh berisi huruf, angka, titik, dan dash")
        
        # Minimal format: xxx.ac.id
        parts = v.split(".")
        if len(parts) < 3:
            raise ValueError("Format domain tidak valid")
        
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validasi nama universitas"""
        if not v or not v.strip():
            raise ValueError("Nama universitas tidak boleh kosong")
        
        # Clean up name
        v = " ".join(v.strip().split())
        
        # Check minimum length
        if len(v) < 3:
            raise ValueError("Nama universitas minimal 3 karakter")
        
        return v
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        """Validasi nomor telepon"""
        if not v:
            return v
        
        # Remove spaces and dashes
        v = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Basic validation untuk nomor Indonesia
        if not v.replace("+", "").isdigit():
            raise ValueError("Nomor telepon hanya boleh berisi angka")
        
        return v
    
    @field_validator("established_year")
    @classmethod
    def validate_established_year(cls, v):
        """Validasi tahun berdiri"""
        if v is None:
            return v
        
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError("Tahun berdiri tidak boleh di masa depan")
        
        return v
    
    async def approve(self, approved_by: str, admin_note: Optional[str] = None):
        """Approve universitas"""
        self.is_approved = True
        self.approval_status = ApprovalStatus.APPROVED
        self.approved_by = approved_by
        self.approved_at = datetime.utcnow()
        self.rejection_reason = None
        await self.save_with_timestamp()
    
    async def reject(self, rejected_by: str, reason: str):
        """Reject universitas"""
        self.is_approved = False
        self.approval_status = ApprovalStatus.REJECTED
        self.approved_by = rejected_by
        self.approved_at = datetime.utcnow()
        self.rejection_reason = reason
        await self.save_with_timestamp()
    
    async def suspend(self, suspended_by: str, reason: str):
        """Suspend universitas"""
        self.is_approved = False
        self.approval_status = ApprovalStatus.SUSPENDED
        self.approved_by = suspended_by
        self.approved_at = datetime.utcnow()
        self.rejection_reason = reason
        await self.save_with_timestamp()
    
    def is_active(self) -> bool:
        """Check apakah universitas aktif"""
        return (
            self.approval_status == ApprovalStatus.APPROVED and 
            not self.is_deleted
        )
    
    @classmethod
    async def find_by_domain(cls, domain: str) -> Optional["University"]:
        """Find university by domain"""
        return await cls.find_one({"domain": domain.lower()})
    
    @classmethod
    async def find_approved(cls, skip: int = 0, limit: int = 100):
        """Find approved universities"""
        return await cls.find(
            {
                "approval_status": ApprovalStatus.APPROVED,
                "is_deleted": {"$ne": True}
            }
        ).skip(skip).limit(limit).to_list()
    
    @classmethod
    async def find_pending_approval(cls):
        """Find universities pending approval"""
        return await cls.find(
            {
                "approval_status": ApprovalStatus.PENDING,
                "is_deleted": {"$ne": True}
            }
        ).to_list()


class Faculty(BaseDocument, SoftDeleteMixin, AuditMixin):
    """
    Model Fakultas
    
    Fields:
    - university_id: Reference ke University
    - name: Nama fakultas
    - code: Kode fakultas (opsional)
    - description: Deskripsi fakultas
    """
    
    university_id: Indexed(str) = Field(..., description="ID Universitas")
    name: str = Field(..., min_length=2, max_length=200, description="Nama fakultas")
    code: Optional[str] = Field(default=None, max_length=10, description="Kode fakultas")
    description: Optional[str] = Field(default=None, max_length=1000, description="Deskripsi fakultas")
    
    # Statistics
    department_count: int = Field(default=0, ge=0, description="Jumlah jurusan")
    student_count: int = Field(default=0, ge=0, description="Jumlah mahasiswa")
    
    class Settings:
        name = "faculties"
        indexes = [
            "university_id",
            "name",
            "code",
            [("university_id", 1), ("name", 1)]  # Compound index untuk unique per university
        ]
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validasi nama fakultas"""
        if not v or not v.strip():
            raise ValueError("Nama fakultas tidak boleh kosong")
        
        v = " ".join(v.strip().split())
        return v
    
    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        """Validasi kode fakultas"""
        if not v:
            return v
        
        v = v.upper().strip()
        
        # Kode hanya boleh huruf dan angka
        if not v.replace(" ", "").isalnum():
            raise ValueError("Kode fakultas hanya boleh berisi huruf dan angka")
        
        return v
    
    @classmethod
    async def find_by_university(cls, university_id: str):
        """Find faculties by university"""
        return await cls.find(
            {
                "university_id": university_id,
                "is_deleted": {"$ne": True}
            }
        ).to_list()
    
    @classmethod
    async def exists_in_university(cls, university_id: str, name: str) -> bool:
        """Check if faculty name exists in university"""
        faculty = await cls.find_one({
            "university_id": university_id,
            "name": name,
            "is_deleted": {"$ne": True}
        })
        return faculty is not None


class Department(BaseDocument, SoftDeleteMixin, AuditMixin):
    """
    Model Jurusan/Department (ganti dari Program Studi)
    
    Fields:
    - faculty_id: Reference ke Faculty
    - name: Nama jurusan
    - code: Kode jurusan
    - description: Deskripsi jurusan
    """
    
    faculty_id: Indexed(str) = Field(..., description="ID Fakultas")
    name: str = Field(..., min_length=2, max_length=200, description="Nama jurusan")
    code: Optional[str] = Field(default=None, max_length=10, description="Kode jurusan")
    description: Optional[str] = Field(default=None, max_length=1000, description="Deskripsi jurusan")
    
    # Academic Information
    degree_level: Optional[str] = Field(default=None, description="Jenjang (S1/S2/S3/D3/D4)")
    accreditation: Optional[str] = Field(default=None, description="Akreditasi (A/B/C)")
    
    # Statistics
    student_count: int = Field(default=0, ge=0, description="Jumlah mahasiswa")
    
    class Settings:
        name = "departments"
        indexes = [
            "faculty_id",
            "name",
            "code",
            "degree_level",
            [("faculty_id", 1), ("name", 1)]  # Compound index untuk unique per faculty
        ]
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validasi nama jurusan"""
        if not v or not v.strip():
            raise ValueError("Nama jurusan tidak boleh kosong")
        
        v = " ".join(v.strip().split())
        return v
    
    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        """Validasi kode jurusan"""
        if not v:
            return v
        
        v = v.upper().strip()
        
        if not v.replace(" ", "").isalnum():
            raise ValueError("Kode jurusan hanya boleh berisi huruf dan angka")
        
        return v
    
    @field_validator("degree_level")
    @classmethod
    def validate_degree_level(cls, v):
        """Validasi jenjang pendidikan"""
        if not v:
            return v
        
        valid_levels = ["D3", "D4", "S1", "S2", "S3"]
        v = v.upper()
        
        if v not in valid_levels:
            raise ValueError(f"Jenjang harus salah satu dari: {valid_levels}")
        
        return v
    
    @field_validator("accreditation")
    @classmethod
    def validate_accreditation(cls, v):
        """Validasi akreditasi"""
        if not v:
            return v
        
        valid_grades = ["A", "B", "C", "Baik Sekali", "Baik", "Unggul"]
        v = v.upper()
        
        if v not in [grade.upper() for grade in valid_grades]:
            raise ValueError(f"Akreditasi harus salah satu dari: {valid_grades}")
        
        return v
    
    @classmethod
    async def find_by_faculty(cls, faculty_id: str):
        """Find departments by faculty"""
        return await cls.find(
            {
                "faculty_id": faculty_id,
                "is_deleted": {"$ne": True}
            }
        ).to_list()
    
    @classmethod
    async def exists_in_faculty(cls, faculty_id: str, name: str) -> bool:
        """Check if department name exists in faculty"""
        department = await cls.find_one({
            "faculty_id": faculty_id,
            "name": name,
            "is_deleted": {"$ne": True}
        })
        return department is not None
    
    @classmethod
    async def find_by_university(cls, university_id: str):
        """Find departments by university (via faculty)"""
        # Perlu join dengan Faculty untuk mendapatkan university_id
        pipeline = [
            {
                "$lookup": {
                    "from": "faculties",
                    "localField": "faculty_id",
                    "foreignField": "_id",
                    "as": "faculty"
                }
            },
            {
                "$match": {
                    "faculty.university_id": university_id,
                    "is_deleted": {"$ne": True}
                }
            }
        ]
        
        return await cls.aggregate(pipeline).to_list()