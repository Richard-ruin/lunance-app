"""
User Endpoints
API endpoints untuk user management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ....core.middleware import standard_rate_limit
from ....core.exceptions import (
    UserNotFoundError,
    EmailAlreadyExistsError,
    ValidationError,
    PermissionError
)
from ....crud.user import crud_user
from ....schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserDetailResponse,
    UserPublicResponse,
    UserStatsResponse,
    UserFilter
)
from ....schemas.base import (
    DataResponse,
    SuccessResponse,
    PaginatedResponse,
    ErrorResponse
)
from ....models.user import UserRole, UserStatus
from ..deps import (
    get_pagination_params,
    get_search_params,
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    validate_user_id,
    CurrentUser
)

router = APIRouter()


@router.post(
    "/",
    response_model=DataResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new user account (admin only for now)"
)
@standard_rate_limit()
async def create_user(
    *,
    user_in: UserCreate,
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> DataResponse[UserResponse]:
    """
    Create new user account
    
    **Admin only endpoint**
    
    - Creates new user dengan validasi email dan institusi
    - Validates university/faculty/department untuk student
    - Checks email uniqueness
    """
    try:
        user = await crud_user.create_user(
            obj_in=user_in,
            created_by=current_user.id
        )
        
        return DataResponse(
            message="User berhasil dibuat",
            data=UserResponse.model_validate(user)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/me",
    response_model=DataResponse[UserDetailResponse],
    summary="Get current user profile",
    description="Get detailed profile information untuk current user"
)
@standard_rate_limit()
async def get_current_user_profile(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[UserDetailResponse]:
    """
    Get current user's detailed profile information
    
    - Returns user data dengan informasi institusi lengkap
    - Includes university, faculty, department names
    """
    user_detail = await crud_user.get_user_with_institution_info(current_user.id)
    
    if not user_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return DataResponse(
        message="User profile retrieved successfully", 
        data=UserDetailResponse.model_validate(user_detail)
    )


@router.put(
    "/me",
    response_model=DataResponse[UserResponse],
    summary="Update current user profile",
    description="Update current user's profile information"
)
@standard_rate_limit()
async def update_current_user_profile(
    *,
    user_update: UserUpdate,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[UserResponse]:
    """
    Update current user's profile
    
    - Users can update their own profile information
    - Validates university/faculty/department jika diupdate
    """
    try:
        updated_user = await crud_user.update_profile(
            user_id=current_user.id,
            obj_in=user_update
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return DataResponse(
            message="Profile berhasil diupdate",
            data=UserResponse.model_validate(updated_user)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="Get users list",
    description="Get paginated list of users dengan filtering (admin only)"
)
@standard_rate_limit()
async def get_users(
    *,
    pagination: tuple = Depends(get_pagination_params),
    search_params: dict = Depends(get_search_params),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    status: Optional[UserStatus] = Query(None, description="Filter by user status"),
    university_id: Optional[str] = Query(None, description="Filter by university"),
    email_verified: Optional[bool] = Query(None, description="Filter by email verification"),
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> PaginatedResponse:
    """
    Get paginated list of users dengan filtering options
    
    **Admin only endpoint**
    
    - Supports search by name and email
    - Filtering by role, status, university, verification status
    - Includes pagination and sorting
    """
    skip, limit = pagination
    
    # Build filter query
    query = {}
    
    if role:
        query["role"] = role
    
    if status:
        query["status"] = status
    
    if university_id:
        query["university_id"] = university_id
    
    if email_verified is not None:
        query["email_verified"] = email_verified
    
    if search_params["search"]:
        query["$or"] = [
            {"full_name": {"$pattern": search_params["search"], "$options": "i"}},
            {"email": {"$pattern": search_params["search"], "$options": "i"}}
        ]
    
    # Get paginated results
    result = await crud_user.paginate(
        page=(skip // limit) + 1,
        per_page=limit,
        query=query,
        sort_by=search_params["sort_by"] or "created_at",
        sort_order=search_params["sort_order"]
    )
    
    return PaginatedResponse(**result)


@router.get(
    "/stats",
    response_model=DataResponse[UserStatsResponse],
    summary="Get user statistics",
    description="Get user statistics for admin dashboard"
)
@standard_rate_limit()
async def get_user_stats(
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> DataResponse[UserStatsResponse]:
    """
    Get comprehensive user statistics
    
    **Admin only endpoint**
    
    - Total users, students, admins
    - Active, verified, pending users count
    - Recent registrations
    """
    stats = await crud_user.get_user_stats()
    
    return DataResponse(
        message="User statistics retrieved successfully",
        data=UserStatsResponse.model_validate(stats)
    )


@router.get(
    "/{user_id}",
    response_model=DataResponse[UserDetailResponse],
    summary="Get user by ID",
    description="Get detailed user information by ID (admin only)"
)
@standard_rate_limit()
async def get_user_by_id(
    *,
    user_id: str = Depends(validate_user_id),
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> DataResponse[UserDetailResponse]:
    """
    Get user by ID dengan informasi lengkap
    
    **Admin only endpoint**
    
    - Returns detailed user information
    - Includes institution hierarchy
    """
    user_detail = await crud_user.get_user_with_institution_info(user_id)
    
    if not user_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return DataResponse(
        message="User retrieved successfully",
        data=UserDetailResponse.model_validate(user_detail)
    )


@router.put(
    "/{user_id}",
    response_model=DataResponse[UserResponse],
    summary="Update user by ID",
    description="Update user information by ID (admin only)"
)
@standard_rate_limit()
async def update_user_by_id(
    *,
    user_id: str = Depends(validate_user_id),
    user_update: UserUpdate,
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> DataResponse[UserResponse]:
    """
    Update user by ID
    
    **Admin only endpoint**
    
    - Admin can update any user's information
    - Validates data consistency
    """
    try:
        updated_user = await crud_user.update_profile(
            user_id=user_id,
            obj_in=user_update
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return DataResponse(
            message="User berhasil diupdate",
            data=UserResponse.model_validate(updated_user)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{user_id}/verify-email",
    response_model=SuccessResponse,
    summary="Verify user email",
    description="Mark user email as verified (admin only)"
)
@standard_rate_limit()
async def verify_user_email(
    *,
    user_id: str = Depends(validate_user_id),
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> SuccessResponse:
    """
    Verify user email manually
    
    **Admin only endpoint**
    
    - Marks user email as verified
    - Updates user status if needed
    """
    success = await crud_user.verify_email(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return SuccessResponse(message="Email berhasil diverifikasi")


@router.patch(
    "/{user_id}/activate",
    response_model=SuccessResponse,
    summary="Activate user",
    description="Activate user account (admin only)"
)
@standard_rate_limit()
async def activate_user(
    *,
    user_id: str = Depends(validate_user_id),
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> SuccessResponse:
    """
    Activate user account
    
    **Admin only endpoint**
    """
    success = await crud_user.activate_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return SuccessResponse(message="User berhasil diaktivasi")


@router.patch(
    "/{user_id}/deactivate",
    response_model=SuccessResponse,
    summary="Deactivate user",
    description="Deactivate user account (admin only)"
)
@standard_rate_limit()
async def deactivate_user(
    *,
    user_id: str = Depends(validate_user_id),
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> SuccessResponse:
    """
    Deactivate user account
    
    **Admin only endpoint**
    """
    success = await crud_user.deactivate_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return SuccessResponse(message="User berhasil dinonaktifkan")


@router.patch(
    "/{user_id}/suspend",
    response_model=SuccessResponse,
    summary="Suspend user",
    description="Suspend user account (admin only)"
)
@standard_rate_limit()
async def suspend_user(
    *,
    user_id: str = Depends(validate_user_id),
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> SuccessResponse:
    """
    Suspend user account
    
    **Admin only endpoint**
    """
    success = await crud_user.suspend_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return SuccessResponse(message="User berhasil disuspend")


@router.delete(
    "/{user_id}",
    response_model=SuccessResponse,
    summary="Delete user",
    description="Soft delete user account (admin only)"
)
@standard_rate_limit()
async def delete_user(
    *,
    user_id: str = Depends(validate_user_id),
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> SuccessResponse:
    """
    Soft delete user account
    
    **Admin only endpoint**
    
    - Performs soft delete (data preserved)
    - User account becomes inaccessible
    """
    success = await crud_user.soft_delete(
        id=user_id,
        deleted_by=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return SuccessResponse(message="User berhasil dihapus")


@router.get(
    "/university/{university_id}/students",
    response_model=PaginatedResponse,
    summary="Get students by university",
    description="Get students dari universitas tertentu"
)
@standard_rate_limit()
async def get_students_by_university(
    *,
    university_id: str = Depends(validate_user_id),
    pagination: tuple = Depends(get_pagination_params),
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> PaginatedResponse:
    """
    Get students from specific university
    
    **Admin only endpoint**
    
    - Returns paginated list of students
    - Filtered by university
    """
    skip, limit = pagination
    
    students = await crud_user.get_students(
        university_id=university_id,
        skip=skip,
        limit=limit
    )
    
    # Get total count
    total = await crud_user.count(query={
        "role": UserRole.STUDENT,
        "university_id": university_id,
        "is_deleted": {"$ne": True}
    })
    
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        data=[UserPublicResponse.model_validate(user.to_dict()) for user in students],
        pagination={
            "page": page,
            "per_page": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None
        }
    )