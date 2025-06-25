from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from bson import ObjectId


class Faculty(BaseModel):
    name: str = Field(..., description="Faculty name")
    majors: List[str] = Field(default_factory=list, description="List of majors in this faculty")


class University(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(None, alias="_id")
    name: str = Field(..., description="Full university name")
    short_name: str = Field(..., description="University abbreviation")
    city: str = Field(..., description="City where university is located")
    province: str = Field(..., description="Province where university is located")
    type: str = Field(..., description="University type: negeri, swasta")
    
    faculties: List[Faculty] = Field(default_factory=list, description="List of faculties")
    
    # For student community features
    student_count: int = Field(0, description="Number of active users from this university")
    average_monthly_expense: float = Field(0.0, description="Average monthly expense of students")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Example Indonesian universities data
INDONESIAN_UNIVERSITIES = [
    {
        "name": "Universitas Indonesia",
        "short_name": "UI",
        "city": "Depok",
        "province": "Jawa Barat",
        "type": "negeri",
        "faculties": [
            {
                "name": "Fakultas Teknik",
                "majors": ["Teknik Informatika", "Teknik Elektro", "Teknik Sipil", "Teknik Mesin"]
            },
            {
                "name": "Fakultas Ekonomi dan Bisnis",
                "majors": ["Manajemen", "Akuntansi", "Ekonomi"]
            },
            {
                "name": "Fakultas Ilmu Komputer",
                "majors": ["Ilmu Komputer", "Sistem Informasi"]
            }
        ]
    },
    {
        "name": "Institut Teknologi Bandung",
        "short_name": "ITB",
        "city": "Bandung",
        "province": "Jawa Barat",
        "type": "negeri",
        "faculties": [
            {
                "name": "Sekolah Teknik Elektro dan Informatika",
                "majors": ["Teknik Informatika", "Teknik Elektro", "Teknik Telekomunikasi"]
            },
            {
                "name": "Fakultas Teknologi Industri",
                "majors": ["Teknik Industri", "Teknik Kimia"]
            }
        ]
    },
    {
        "name": "Universitas Gadjah Mada",
        "short_name": "UGM",
        "city": "Yogyakarta",
        "province": "Daerah Istimewa Yogyakarta",
        "type": "negeri",
        "faculties": [
            {
                "name": "Fakultas Teknik",
                "majors": ["Teknik Informatika", "Teknik Sipil", "Teknik Mesin"]
            },
            {
                "name": "Fakultas Ekonomika dan Bisnis",
                "majors": ["Manajemen", "Akuntansi", "Ekonomi Pembangunan"]
            }
        ]
    }
]