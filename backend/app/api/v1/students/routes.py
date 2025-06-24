from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from pydantic import BaseModel, EmailStr, validator

from app.models.student import (
    Student, StudentUpdate, StudentResponse, Profile, Settings,
    NotificationSettings, DisplaySettings, PrivacySettings,
    SavingsGoal, IncomeSource
)
from app.api.v1.students.crud import student_crud
from app.api.deps import (
    get_current_user, get_verified_user, get_pagination_params,
    get_common_query_params, CommonQueryParams, validate_student_access
)
from app.core.exceptions import (
    UserNotFoundException, ValidationException, FileUploadException,
    UnsupportedFileTypeException, FileSizeExceededException
)
from app.config.settings import settings
from app.utils.student_helpers import (
    process_profile_picture, validate_university_info,
    calculate_user_level, update_user_achievements
)
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    nickname: Optional[str] = None
    phone_number: Optional[str] = None
    university: Optional[str] = None
    faculty: Optional[str] = None
    major: Optional[str] = None
    semester: Optional[int] = None
    graduation_year: Optional[int] = None
    monthly_allowance: Optional[float] = None
    accommodation: Optional[str] = None
    transportation: Optional[str] = None
    
    @validator('semester')
    def validate_semester(cls, v):
        if v and (v < 1 or v > 14):
            raise ValueError('Semester must be between 1 and 14')
        return v
    
    @validator('graduation_year')
    def validate_graduation_year(cls, v):
        if v:
            current_year = datetime.now().year
            if v < current_year or v > current_year + 8:
                raise ValueError(f'Graduation year must be between {current_year} and {current_year + 8}')
        return v
    
    @validator('monthly_allowance')
    def validate_allowance(cls, v):
        if v and v < 0:
            raise ValueError('Monthly allowance cannot be negative')
        return v

class SettingsUpdateRequest(BaseModel):
    notifications: Optional[NotificationSettings] = None
    display: Optional[DisplaySettings] = None
    privacy: Optional[PrivacySettings] = None

class SavingsGoalRequest(BaseModel):
    name: str
    target_amount: float
    target_date: datetime
    priority: str = "medium"
    category: str = "general"
    
    @validator('target_amount')
    def validate_target_amount(cls, v):
        if v <= 0:
            raise ValueError('Target amount must be greater than 0')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ["high", "medium", "low"]:
            raise ValueError('Priority must be high, medium, or low')
        return v
    
    @validator('target_date')
    def validate_target_date(cls, v):
        if v <= datetime.now():
            raise ValueError('Target date must be in the future')
        return v

class IncomeSourceRequest(BaseModel):
    type: str
    amount: float
    frequency: str = "monthly"
    
    @validator('type')
    def validate_type(cls, v):
        allowed_types = ["allowance", "part_time", "scholarship", "freelance", "other"]
        if v not in allowed_types:
            raise ValueError(f'Income type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Income amount must be greater than 0')
        return v
    
    @validator('frequency')
    def validate_frequency(cls, v):
        if v not in ["weekly", "monthly"]:
            raise ValueError('Frequency must be weekly or monthly')
        return v

class ProfilePictureResponse(BaseModel):
    message: str
    profile_picture_url: str

class UniversitySearchResponse(BaseModel):
    universities: List[str]
    total: int

class StudentSearchResponse(BaseModel):
    students: List[StudentResponse]
    total: int
    page: int
    size: int


@router.get("/me", response_model=StudentResponse)
async def get_my_profile(
    current_user: Student = Depends(get_current_user)
):
    """Get current user's profile"""
    return StudentResponse(
        id=str(current_user.id),
        email=current_user.email,
        profile=current_user.profile,
        verification=current_user.verification,
        settings=current_user.settings,
        gamification=current_user.gamification,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        is_active=current_user.is_active
    )


@router.put("/me/profile", response_model=StudentResponse)
async def update_my_profile(
    profile_update: ProfileUpdateRequest,
    current_user: Student = Depends(get_verified_user)
):
    """Update current user's profile"""
    try:
        # Validate university info if provided
        if profile_update.university:
            is_valid = await validate_university_info(
                profile_update.university,
                profile_update.faculty,
                profile_update.major
            )
            if not is_valid:
                raise ValidationException("Invalid university, faculty, or major combination")
        
        # Create updated profile
        current_profile = current_user.profile
        update_data = profile_update.dict(exclude_unset=True)
        
        # Update profile fields
        for field, value in update_data.items():
            if hasattr(current_profile, field) and value is not None:
                setattr(current_profile, field, value)
        
        # Update student
        student_update = StudentUpdate(profile=current_profile)
        updated_student = await student_crud.update_student(
            str(current_user.id), 
            student_update
        )
        
        # Update gamification based on profile completeness
        await update_user_achievements(updated_student, "profile_completion")
        
        logger.info(f"Profile updated for user: {current_user.email}")
        
        return StudentResponse(
            id=str(updated_student.id),
            email=updated_student.email,
            profile=updated_student.profile,
            verification=updated_student.verification,
            settings=updated_student.settings,
            gamification=updated_student.gamification,
            created_at=updated_student.created_at,
            last_login=updated_student.last_login,
            is_active=updated_student.is_active
        )
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.put("/me/settings", response_model=StudentResponse)
async def update_my_settings(
    settings_update: SettingsUpdateRequest,
    current_user: Student = Depends(get_verified_user)
):
    """Update current user's settings"""
    try:
        # Update settings
        current_settings = current_user.settings
        
        if settings_update.notifications:
            current_settings.notifications = settings_update.notifications
        if settings_update.display:
            current_settings.display = settings_update.display
        if settings_update.privacy:
            current_settings.privacy = settings_update.privacy
        
        # Update student
        student_update = StudentUpdate(settings=current_settings)
        updated_student = await student_crud.update_student(
            str(current_user.id), 
            student_update
        )
        
        logger.info(f"Settings updated for user: {current_user.email}")
        
        return StudentResponse(
            id=str(updated_student.id),
            email=updated_student.email,
            profile=updated_student.profile,
            verification=updated_student.verification,
            settings=updated_student.settings,
            gamification=updated_student.gamification,
            created_at=updated_student.created_at,
            last_login=updated_student.last_login,
            is_active=updated_student.is_active
        )
        
    except Exception as e:
        logger.error(f"Settings update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Settings update failed"
        )


@router.post("/me/profile-picture", response_model=ProfilePictureResponse)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: Student = Depends(get_verified_user)
):
    """Upload and update profile picture"""
    try:
        # Validate file
        if not file.content_type.startswith('image/'):
            raise UnsupportedFileTypeException(
                file.content_type, 
                ["image/jpeg", "image/png", "image/jpg"]
            )
        
        # Check file size
        if file.size > settings.MAX_FILE_SIZE:
            raise FileSizeExceededException(settings.MAX_FILE_SIZE)
        
        # Process and save profile picture
        picture_url = await process_profile_picture(file, str(current_user.id))
        
        # Update user profile
        current_profile = current_user.profile
        current_profile.avatar_url = picture_url
        
        student_update = StudentUpdate(profile=current_profile)
        await student_crud.update_student(str(current_user.id), student_update)
        
        logger.info(f"Profile picture updated for user: {current_user.email}")
        
        return ProfilePictureResponse(
            message="Profile picture updated successfully",
            profile_picture_url=picture_url
        )
        
    except (UnsupportedFileTypeException, FileSizeExceededException):
        raise
    except Exception as e:
        logger.error(f"Profile picture upload failed: {str(e)}")
        raise FileUploadException("Failed to upload profile picture")


@router.post("/me/savings-goals", response_model=dict)
async def add_savings_goal(
    goal_request: SavingsGoalRequest,
    current_user: Student = Depends(get_verified_user)
):
    """Add new savings goal"""
    try:
        from app.models.student import SavingsGoal
        
        # Create new savings goal
        new_goal = SavingsGoal(
            name=goal_request.name,
            target_amount=goal_request.target_amount,
            target_date=goal_request.target_date,
            priority=goal_request.priority,
            category=goal_request.category,
            current_amount=0.0,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Add to user's profile
        current_profile = current_user.profile
        current_profile.savings_goals.append(new_goal)
        
        # Update student
        student_update = StudentUpdate(profile=current_profile)
        await student_crud.update_student(str(current_user.id), student_update)
        
        # Update achievements
        await update_user_achievements(current_user, "savings_goal_created")
        
        logger.info(f"Savings goal added for user: {current_user.email}")
        
        return {
            "message": "Savings goal added successfully",
            "goal_id": str(new_goal.id)
        }
        
    except Exception as e:
        logger.error(f"Add savings goal failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add savings goal"
        )


@router.post("/me/income-sources", response_model=dict)
async def add_income_source(
    income_request: IncomeSourceRequest,
    current_user: Student = Depends(get_verified_user)
):
    """Add new income source"""
    try:
        # Create new income source
        new_income = IncomeSource(
            type=income_request.type,
            amount=income_request.amount,
            frequency=income_request.frequency
        )
        
        # Add to user's profile
        current_profile = current_user.profile
        current_profile.income_sources.append(new_income)
        
        # Update monthly allowance if this is primary income
        if income_request.type == "allowance" and income_request.frequency == "monthly":
            current_profile.monthly_allowance = income_request.amount
        
        # Update student
        student_update = StudentUpdate(profile=current_profile)
        await student_crud.update_student(str(current_user.id), student_update)
        
        logger.info(f"Income source added for user: {current_user.email}")
        
        return {"message": "Income source added successfully"}
        
    except Exception as e:
        logger.error(f"Add income source failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add income source"
        )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student_profile(
    student_id: str,
    current_user: Student = Depends(get_current_user),
    target_student: Student = Depends(validate_student_access)
):
    """Get student profile by ID"""
    return StudentResponse(
        id=str(target_student.id),
        email=target_student.email,
        profile=target_student.profile,
        verification=target_student.verification,
        settings=target_student.settings,
        gamification=target_student.gamification,
        created_at=target_student.created_at,
        last_login=target_student.last_login,
        is_active=target_student.is_active
    )


@router.get("/search/students", response_model=StudentSearchResponse)
async def search_students(
    q: str = Query(..., min_length=2, description="Search query"),
    params: CommonQueryParams = Depends(get_common_query_params),
    current_user: Student = Depends(get_verified_user)
):
    """Search for students"""
    try:
        students = await student_crud.search_students(q, params.size)
        
        # Convert to response format
        student_responses = [
            StudentResponse(
                id=str(student.id),
                email=student.email,
                profile=student.profile,
                verification=student.verification,
                settings=student.settings,
                gamification=student.gamification,
                created_at=student.created_at,
                last_login=student.last_login,
                is_active=student.is_active
            )
            for student in students
            if student.settings.privacy.show_in_leaderboard  # Respect privacy settings
        ]
        
        return StudentSearchResponse(
            students=student_responses,
            total=len(student_responses),
            page=params.page,
            size=params.size
        )
        
    except Exception as e:
        logger.error(f"Student search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@router.get("/search/universities", response_model=UniversitySearchResponse)
async def search_universities(
    q: str = Query(..., min_length=2, description="University search query")
):
    """Search for universities"""
    try:
        # Filter supported universities
        matching_universities = [
            uni for uni in settings.SUPPORTED_UNIVERSITIES
            if q.lower() in uni.lower()
        ]
        
        return UniversitySearchResponse(
            universities=matching_universities[:20],  # Limit to 20 results
            total=len(matching_universities)
        )
        
    except Exception as e:
        logger.error(f"University search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="University search failed"
        )


@router.get("/by-university/{university}", response_model=StudentSearchResponse)
async def get_students_by_university(
    university: str,
    params: CommonQueryParams = Depends(get_common_query_params),
    current_user: Student = Depends(get_verified_user)
):
    """Get students from same university"""
    try:
        students = await student_crud.get_students_by_university(university, params.size)
        
        # Convert to response format and respect privacy
        student_responses = [
            StudentResponse(
                id=str(student.id),
                email=student.email,
                profile=student.profile,
                verification=student.verification,
                settings=student.settings,
                gamification=student.gamification,
                created_at=student.created_at,
                last_login=student.last_login,
                is_active=student.is_active
            )
            for student in students
            if (student.settings.privacy.show_in_leaderboard and 
                str(student.id) != str(current_user.id))  # Exclude self
        ]
        
        return StudentSearchResponse(
            students=student_responses,
            total=len(student_responses),
            page=params.page,
            size=params.size
        )
        
    except Exception as e:
        logger.error(f"Get students by university failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get students"
        )


@router.delete("/me", response_model=dict)
async def deactivate_my_account(
    current_user: Student = Depends(get_verified_user)
):
    """Deactivate current user's account"""
    try:
        await student_crud.deactivate_student(str(current_user.id))
        
        logger.info(f"Account deactivated for user: {current_user.email}")
        
        return {"message": "Account deactivated successfully"}
        
    except Exception as e:
        logger.error(f"Account deactivation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deactivation failed"
        )


# Analytics endpoints for student profile
@router.get("/me/analytics/profile-completion", response_model=dict)
async def get_profile_completion(
    current_user: Student = Depends(get_verified_user)
):
    """Get profile completion percentage"""
    try:
        profile = current_user.profile
        
        # Calculate completion percentage
        total_fields = 15
        completed_fields = 0
        
        if profile.full_name: completed_fields += 1
        if profile.nickname: completed_fields += 1
        if profile.phone_number: completed_fields += 1
        if profile.university: completed_fields += 1
        if profile.faculty: completed_fields += 1
        if profile.major: completed_fields += 1
        if profile.student_id: completed_fields += 1
        if profile.semester: completed_fields += 1
        if profile.graduation_year: completed_fields += 1
        if profile.monthly_allowance > 0: completed_fields += 1
        if profile.income_sources: completed_fields += 1
        if profile.accommodation: completed_fields += 1
        if profile.transportation: completed_fields += 1
        if profile.savings_goals: completed_fields += 1
        if profile.avatar_url: completed_fields += 1
        
        completion_percentage = (completed_fields / total_fields) * 100
        
        return {
            "completion_percentage": round(completion_percentage, 1),
            "completed_fields": completed_fields,
            "total_fields": total_fields,
            "missing_fields": total_fields - completed_fields
        }
        
    except Exception as e:
        logger.error(f"Profile completion calculation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate profile completion"
        )