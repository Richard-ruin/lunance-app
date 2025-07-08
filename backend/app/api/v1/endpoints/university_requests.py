# app/api/v1/endpoints/university_requests.py
"""University request management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
import logging

from app.models.university_request import (
    UniversityRequestCreate, UniversityRequestUpdate, UniversityRequestResponse,
    UniversityRequestListResponse, UniversityRequestStats, UniversityRequestFilter,
    BulkUniversityRequestUpdate, BulkUniversityRequestResponse, UniversityRequestSummary,
    UniversityDataSuggestion, RequestStatus
)
from app.models.common import PaginatedResponse, PaginationParams, SuccessResponse
from app.services.university_request_service import (
    UniversityRequestService, UniversityRequestServiceError, university_request_service
)
from app.middleware.auth import (
    get_current_verified_user, require_admin, rate_limit_dependency
)
from app.models.user import UserInDB

logger = logging.getLogger(__name__)

router = APIRouter()


# Student endpoints
@router.post("", response_model=UniversityRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_university_request(
    request_data: UniversityRequestCreate,
    current_user: UserInDB = Depends(get_current_verified_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    Create new university request (student only).
    """
    try:
        request = await university_request_service.create_request(
            str(current_user.id),
            request_data
        )
        
        return request
        
    except UniversityRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating university request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create university request"
        )


@router.get("/my-requests", response_model=PaginatedResponse[UniversityRequestResponse])
async def get_my_requests(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get current user's university requests.
    """
    try:
        pagination = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        result = await university_request_service.get_user_requests(
            str(current_user.id),
            pagination
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting user requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user requests"
        )


@router.get("/{request_id}", response_model=UniversityRequestResponse)
async def get_request_detail(
    request_id: str,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get university request detail.
    Students can only view their own requests, admins can view all.
    """
    try:
        request = await university_request_service.get_request_by_id(request_id)
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        # Check if user can access this request
        if current_user.role.value != "admin" and str(request.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own requests"
            )
        
        return request
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting request detail {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get request detail"
        )


# Admin endpoints
@router.get("", response_model=UniversityRequestListResponse)
async def list_university_requests(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    status_filter: Optional[RequestStatus] = Query(None, description="Filter by status"),
    university_name: Optional[str] = Query(None, description="Filter by university name"),
    faculty_name: Optional[str] = Query(None, description="Filter by faculty name"),
    major_name: Optional[str] = Query(None, description="Filter by major name"),
    user_email: Optional[str] = Query(None, description="Filter by user email"),
    current_user: UserInDB = Depends(require_admin()),
    _: None = Depends(rate_limit_dependency)
):
    """
    List all university requests with filters (admin only).
    """
    try:
        pagination = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        filters = UniversityRequestFilter(
            status=status_filter,
            university_name=university_name,
            faculty_name=faculty_name,
            major_name=major_name,
            user_email=user_email
        )
        
        result = await university_request_service.list_requests(
            pagination,
            filters
        )
        
        return result
        
    except UniversityRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing university requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list university requests"
        )


@router.put("/{request_id}", response_model=UniversityRequestResponse)
async def update_university_request(
    request_id: str,
    update_data: UniversityRequestUpdate,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Update university request status (admin only).
    """
    try:
        updated_request = await university_request_service.update_request(
            request_id,
            update_data,
            str(current_user.id)
        )
        
        if not updated_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        return updated_request
        
    except UniversityRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating university request {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update university request"
        )


@router.delete("/{request_id}", response_model=SuccessResponse)
async def delete_university_request(
    request_id: str,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Delete university request (admin only).
    """
    try:
        success = await university_request_service.delete_request(
            request_id,
            str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        
        return SuccessResponse(
            message="University request deleted successfully"
        )
        
    except UniversityRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting university request {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete university request"
        )


@router.post("/bulk-update", response_model=BulkUniversityRequestResponse)
async def bulk_update_requests(
    bulk_update: BulkUniversityRequestUpdate,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Bulk update multiple university requests (admin only).
    """
    try:
        result = await university_request_service.bulk_update_requests(
            bulk_update,
            str(current_user.id)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in bulk update requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk update requests"
        )


@router.get("/admin/stats", response_model=UniversityRequestStats)
async def get_request_stats(
    current_user: UserInDB = Depends(require_admin())
):
    """
    Get university request statistics (admin only).
    """
    try:
        stats = await university_request_service.get_request_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting request stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get request statistics"
        )


@router.get("/admin/summary", response_model=UniversityRequestSummary)
async def get_request_summary(
    current_user: UserInDB = Depends(require_admin())
):
    """
    Get university request summary for admin dashboard.
    """
    try:
        summary = await university_request_service.get_request_summary()
        return summary
        
    except UniversityRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting request summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get request summary"
        )


@router.get("/admin/suggestions", response_model=list[UniversityDataSuggestion])
async def get_university_suggestions(
    limit: int = Query(20, ge=1, le=100, description="Maximum suggestions"),
    current_user: UserInDB = Depends(require_admin())
):
    """
    Get university data suggestions based on requests (admin only).
    """
    try:
        suggestions = await university_request_service.get_university_suggestions(limit)
        return suggestions
        
    except Exception as e:
        logger.error(f"Error getting university suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get university suggestions"
        )