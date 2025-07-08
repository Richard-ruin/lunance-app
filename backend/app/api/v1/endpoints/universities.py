# app/api/v1/endpoints/universities.py
"""University management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
import logging

from app.models.university import (
    UniversityCreate, UniversityUpdate, UniversityResponse, UniversityListResponse,
    UniversityStats, FacultyCreate, FacultyUpdate, MajorCreate, MajorUpdate
)
from app.models.common import (
    PaginatedResponse, PaginationParams, SuccessResponse
)
from app.services.university_service import (
    UniversityService, UniversityServiceError, university_service
)
from app.middleware.auth import (
    require_admin, get_optional_user, rate_limit_dependency
)
from app.models.user import UserInDB

logger = logging.getLogger(__name__)

router = APIRouter()


# Public endpoints (accessible to all users)
@router.get("", response_model=PaginatedResponse[UniversityListResponse])
async def list_universities(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="Search term"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    current_user: Optional[UserInDB] = Depends(get_optional_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    List all universities with pagination and filters.
    Public endpoint accessible to all users.
    """
    try:
        pagination = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # For non-admin users, only show active universities
        if not current_user or current_user.role.value != "admin":
            is_active = True
        
        result = await university_service.list_universities(
            pagination=pagination,
            search=search,
            is_active=is_active
        )
        
        return result
        
    except UniversityServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing universities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list universities"
        )


@router.get("/search", response_model=List[UniversityListResponse])
async def search_universities(
    q: str = Query(..., min_length=1, max_length=100, description="Search term"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    current_user: Optional[UserInDB] = Depends(get_optional_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    Search universities by name.
    Public endpoint accessible to all users.
    """
    try:
        universities = await university_service.search_universities(q, limit)
        return universities
        
    except Exception as e:
        logger.error(f"Error searching universities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search universities"
        )


@router.get("/{university_id}", response_model=UniversityResponse)
async def get_university_detail(
    university_id: str,
    current_user: Optional[UserInDB] = Depends(get_optional_user)
):
    """
    Get university detail by ID.
    Public endpoint accessible to all users.
    """
    try:
        university = await university_service.get_university_by_id(university_id)
        
        if not university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="University not found"
            )
        
        # For non-admin users, only show active universities
        if not current_user or current_user.role.value != "admin":
            if not university.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="University not found"
                )
        
        return university
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting university detail {university_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get university detail"
        )


# Admin-only endpoints
@router.post("", response_model=UniversityResponse, status_code=status.HTTP_201_CREATED)
async def create_university(
    university_data: UniversityCreate,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Create new university (admin only).
    """
    try:
        university = await university_service.create_university(
            university_data,
            str(current_user.id)
        )
        
        return university
        
    except UniversityServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating university: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create university"
        )


@router.put("/{university_id}", response_model=UniversityResponse)
async def update_university(
    university_id: str,
    update_data: UniversityUpdate,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Update university by ID (admin only).
    """
    try:
        updated_university = await university_service.update_university(
            university_id,
            update_data,
            str(current_user.id)
        )
        
        if not updated_university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="University not found"
            )
        
        return updated_university
        
    except UniversityServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating university {university_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update university"
        )


@router.delete("/{university_id}", response_model=SuccessResponse)
async def delete_university(
    university_id: str,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Delete (deactivate) university by ID (admin only).
    """
    try:
        success = await university_service.delete_university(
            university_id,
            str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="University not found"
            )
        
        return SuccessResponse(
            message="University deleted successfully"
        )
        
    except UniversityServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting university {university_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete university"
        )


# Faculty management endpoints
@router.post("/{university_id}/faculties", response_model=UniversityResponse, status_code=status.HTTP_201_CREATED)
async def add_faculty(
    university_id: str,
    faculty_data: FacultyCreate,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Add faculty to university (admin only).
    """
    try:
        updated_university = await university_service.add_faculty(
            university_id,
            faculty_data,
            str(current_user.id)
        )
        
        if not updated_university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="University not found"
            )
        
        return updated_university
        
    except UniversityServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding faculty to university {university_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add faculty"
        )


@router.put("/{university_id}/faculties/{faculty_id}", response_model=UniversityResponse)
async def update_faculty(
    university_id: str,
    faculty_id: str,
    update_data: FacultyUpdate,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Update faculty in university (admin only).
    """
    try:
        updated_university = await university_service.update_faculty(
            university_id,
            faculty_id,
            update_data,
            str(current_user.id)
        )
        
        if not updated_university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="University or faculty not found"
            )
        
        return updated_university
        
    except UniversityServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating faculty {faculty_id} in university {university_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update faculty"
        )


@router.delete("/{university_id}/faculties/{faculty_id}", response_model=UniversityResponse)
async def delete_faculty(
    university_id: str,
    faculty_id: str,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Delete faculty from university (admin only).
    """
    try:
        updated_university = await university_service.delete_faculty(
            university_id,
            faculty_id,
            str(current_user.id)
        )
        
        if not updated_university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="University or faculty not found"
            )
        
        return updated_university
        
    except UniversityServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting faculty {faculty_id} from university {university_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete faculty"
        )


# Major management endpoints
@router.post("/{university_id}/faculties/{faculty_id}/majors", response_model=UniversityResponse, status_code=status.HTTP_201_CREATED)
async def add_major(
    university_id: str,
    faculty_id: str,
    major_data: MajorCreate,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Add major to faculty (admin only).
    """
    try:
        updated_university = await university_service.add_major(
            university_id,
            faculty_id,
            major_data,
            str(current_user.id)
        )
        
        if not updated_university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="University or faculty not found"
            )
        
        return updated_university
        
    except UniversityServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding major to faculty {faculty_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add major"
        )


# Statistics and admin endpoints
@router.get("/admin/stats", response_model=UniversityStats)
async def get_university_stats(
    current_user: UserInDB = Depends(require_admin())
):
    """
    Get university system statistics (admin only).
    """
    try:
        stats = await university_service.get_university_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting university stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get university statistics"
        )


@router.get("/admin/dashboard-stats", response_model=dict)
async def get_admin_dashboard_stats(
    current_user: UserInDB = Depends(require_admin())
):
    """
    Get university statistics for admin dashboard.
    """
    try:
        from ..config.database import get_database
        
        db = await get_database()
        universities_collection = db.universities
        users_collection = db.users
        
        # Basic stats
        stats = await university_service.get_university_stats()
        
        # Additional dashboard stats
        
        # Universities by status
        active_universities = await universities_collection.count_documents({"is_active": True})
        inactive_universities = await universities_collection.count_documents({"is_active": False})
        
        # Recent additions (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_universities = await universities_collection.count_documents({
            "created_at": {"$gte": thirty_days_ago}
        })
        
        # Universities without students
        universities_with_students_pipeline = [
            {
                "$lookup": {
                    "from": "users",
                    "localField": "_id",
                    "foreignField": "university_id",
                    "as": "students"
                }
            },
            {
                "$addFields": {
                    "student_count": {"$size": "$students"}
                }
            },
            {
                "$match": {
                    "student_count": 0,
                    "is_active": True
                }
            },
            {"$count": "total"}
        ]
        
        empty_universities_result = await universities_collection.aggregate(
            universities_with_students_pipeline
        ).to_list(1)
        
        empty_universities = empty_universities_result[0]["total"] if empty_universities_result else 0
        
        # Faculty and major distribution
        distribution_pipeline = [
            {"$match": {"is_active": True}},
            {
                "$project": {
                    "name": 1,
                    "faculty_count": {"$size": "$faculties"},
                    "major_count": {
                        "$sum": {
                            "$map": {
                                "input": "$faculties",
                                "as": "faculty",
                                "in": {"$size": "$$faculty.majors"}
                            }
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_faculties_per_university": {"$avg": "$faculty_count"},
                    "avg_majors_per_university": {"$avg": "$major_count"},
                    "universities_with_no_faculties": {
                        "$sum": {"$cond": [{"$eq": ["$faculty_count", 0]}, 1, 0]}
                    }
                }
            }
        ]
        
        distribution_result = await universities_collection.aggregate(distribution_pipeline).to_list(1)
        
        if distribution_result:
            avg_faculties = round(distribution_result[0]["avg_faculties_per_university"], 2)
            avg_majors = round(distribution_result[0]["avg_majors_per_university"], 2)
            universities_no_faculties = distribution_result[0]["universities_with_no_faculties"]
        else:
            avg_faculties = 0
            avg_majors = 0
            universities_no_faculties = 0
        
        return {
            "total_universities": stats.total_universities,
            "active_universities": active_universities,
            "inactive_universities": inactive_universities,
            "total_faculties": stats.total_faculties,
            "total_majors": stats.total_majors,
            "recent_additions": recent_universities,
            "empty_universities": empty_universities,
            "universities_no_faculties": universities_no_faculties,
            "avg_faculties_per_university": avg_faculties,
            "avg_majors_per_university": avg_majors,
            "students_per_university": stats.students_per_university[:5],  # Top 5
            "activity_rate": round((active_universities / stats.total_universities * 100) if stats.total_universities > 0 else 0, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting admin dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard statistics"
        )


@router.post("/admin/import", response_model=SuccessResponse)
async def import_universities(
    import_data: dict,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Import universities from data (admin only).
    """
    try:
        # This is a placeholder for import functionality
        # In a real implementation, you would:
        # 1. Validate the import data format
        # 2. Process and create universities with faculties and majors
        # 3. Handle duplicates and errors
        # 4. Return detailed import results
        
        return SuccessResponse(
            message="Import functionality not yet implemented",
            data=import_data
        )
        
    except Exception as e:
        logger.error(f"Error importing universities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to import universities"
        )


@router.post("/export", response_model=SuccessResponse)
async def export_universities(
    format: str = Query("csv", regex="^(csv|excel|json)$", description="Export format"),
    include_faculties: bool = Query(True, description="Include faculties data"),
    include_majors: bool = Query(True, description="Include majors data"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: UserInDB = Depends(require_admin())
):
    """
    Export universities data (admin only).
    """
    try:
        # This is a placeholder for export functionality
        # In a real implementation, you would:
        # 1. Get filtered university data
        # 2. Generate the export file (CSV/Excel/JSON)
        # 3. Store it temporarily
        # 4. Return download URL or send via email
        
        return SuccessResponse(
            message="Export functionality not yet implemented",
            data={
                "format": format,
                "include_faculties": include_faculties,
                "include_majors": include_majors,
                "filters": {
                    "is_active": is_active
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting universities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export universities"
        )