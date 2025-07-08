from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class Major(BaseModel):
    """Major model."""
    id: Optional[str] = Field(None, alias="_id", description="Major ID")
    name: str = Field(..., min_length=2, max_length=100, description="Major name")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean major name."""
        return v.strip().title()

    model_config = {
        'populate_by_name': True,
        'json_schema_extra': {
            'example': {
                'name': 'Computer Science'
            }
        }
    }


class Faculty(BaseModel):
    """Faculty model."""
    id: Optional[str] = Field(None, alias="_id", description="Faculty ID")
    name: str = Field(..., min_length=2, max_length=100, description="Faculty name")
    majors: List[Major] = Field(default_factory=list, description="List of majors in this faculty")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean faculty name."""
        return v.strip().title()

    model_config = {
        'populate_by_name': True,
        'json_schema_extra': {
            'example': {
                'name': 'Faculty of Computer Science',
                'majors': [
                    {'name': 'Computer Science'},
                    {'name': 'Information Systems'},
                    {'name': 'Software Engineering'}
                ]
            }
        }
    }


class UniversityBase(BaseModel):
    """Base university model."""
    name: str = Field(..., min_length=2, max_length=150, description="University name")
    is_active: bool = Field(default=True, description="Whether university is active")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean university name."""
        return v.strip().title()


class UniversityCreate(UniversityBase):
    """Schema for creating a new university."""
    faculties: List[Faculty] = Field(default_factory=list, description="List of faculties")


class UniversityUpdate(BaseModel):
    """Schema for updating university information."""
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    is_active: Optional[bool] = Field(None)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate university name if provided."""
        if v is None:
            return v
        return v.strip().title()


class UniversityInDB(UniversityBase):
    """University model as stored in database."""
    id: Optional[str] = Field(None, alias="_id", description="University ID")
    faculties: List[Faculty] = Field(default_factory=list, description="List of faculties")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    model_config = {
        'populate_by_name': True,
        'json_schema_extra': {
            'example': {
                'name': 'University of Indonesia',
                'is_active': True,
                'faculties': [
                    {
                        'name': 'Faculty of Computer Science',
                        'majors': [
                            {'name': 'Computer Science'},
                            {'name': 'Information Systems'}
                        ]
                    }
                ]
            }
        }
    }


class UniversityResponse(UniversityBase):
    """Schema for university response."""
    id: Optional[str] = Field(None, alias="_id", description="University ID")
    faculties: List[Faculty] = Field(..., description="List of faculties")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        'populate_by_name': True,
        'from_attributes': True
    }


class FacultyCreate(BaseModel):
    """Schema for creating a new faculty."""
    name: str = Field(..., min_length=2, max_length=100, description="Faculty name")
    majors: List[Major] = Field(default_factory=list, description="List of majors")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean faculty name."""
        return v.strip().title()


class FacultyUpdate(BaseModel):
    """Schema for updating faculty information."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate faculty name if provided."""
        if v is None:
            return v
        return v.strip().title()


class MajorCreate(BaseModel):
    """Schema for creating a new major."""
    name: str = Field(..., min_length=2, max_length=100, description="Major name")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean major name."""
        return v.strip().title()


class MajorUpdate(BaseModel):
    """Schema for updating major information."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate major name if provided."""
        if v is None:
            return v
        return v.strip().title()


class UniversityListResponse(BaseModel):
    """Schema for university list response."""
    id: str = Field(..., alias="_id", description="University ID")
    name: str = Field(..., description="University name")
    is_active: bool = Field(..., description="Whether university is active")
    faculty_count: int = Field(..., description="Number of faculties")
    major_count: int = Field(..., description="Total number of majors")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {
        'populate_by_name': True,
        'from_attributes': True
    }


class UniversityStats(BaseModel):
    """Schema for university statistics."""
    total_universities: int = Field(..., description="Total number of universities")
    active_universities: int = Field(..., description="Number of active universities")
    total_faculties: int = Field(..., description="Total number of faculties")
    total_majors: int = Field(..., description="Total number of majors")
    students_per_university: List[dict] = Field(..., description="Student count per university")

    model_config = {
        'json_schema_extra': {
            'example': {
                'total_universities': 25,
                'active_universities': 23,
                'total_faculties': 150,
                'total_majors': 450,
                'students_per_university': [
                    {'university_name': 'University of Indonesia', 'student_count': 1250},
                    {'university_name': 'Gadjah Mada University', 'student_count': 980}
                ]
            }
        }
    }