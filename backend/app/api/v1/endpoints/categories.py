"""
Category Endpoints
API endpoints untuk category management (global & personal)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ....core.middleware import standard_rate_limit, auth_rate_limit
from ....crud.category import crud_category
from ....schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryPublicResponse,
    CategoryStatsResponse,
    CategoryUserFilter,
    DefaultCategoryCreate,
    DefaultCategoriesResponse
)
from ....schemas.base import (
    DataResponse,
    SuccessResponse,
    PaginatedResponse
)
from ....models.category import CategoryType
from ..deps import (
    get_pagination_params,
    get_search_params,
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    validate_category_id,
    CurrentUser
)

router = APIRouter()


@router.get(
    "/",
    response_model=DataResponse[List[CategoryPublicResponse]],
    summary="Get user categories",
    description="Get categories available untuk current user (personal + global)"
)
@standard_rate_limit()
async def get_user_categories(
    *,
    category_type: Optional[CategoryType] = Query(None, description="Filter by category type"),
    include_global: bool = Query(True, description="Include global categories"),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[List[CategoryPublicResponse]]:
    """
    Get categories available untuk user
    
    - Returns personal categories + global categories
    - Can filter by type (income/expense)
    - Can exclude global categories
    """
    categories = await crud_category.get_user_categories(
        user_id=current_user.id,
        category_type=category_type,
        include_global=include_global
    )
    
    return DataResponse(
        message="Categories retrieved successfully",
        data=[CategoryPublicResponse.model_validate(cat.model_dump()) for cat in categories]
    )


@router.post(
    "/",
    response_model=DataResponse[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create personal category",
    description="Create new personal category untuk current user"
)
@auth_rate_limit()
async def create_personal_category(
    *,
    category_in: CategoryCreate,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[CategoryResponse]:
    """
    Create personal category
    
    - Category akan menjadi personal category milik user
    - Nama harus unik dalam scope personal user
    """
    try:
        # Ensure it's personal category
        category_data = category_in.model_dump()
        category_data["is_global"] = False
        category_create = CategoryCreate.model_validate(category_data)
        
        category = await crud_category.create_category(
            obj_in=category_create,
            created_by=current_user.id,
            is_admin=False
        )
        
        return DataResponse(
            message="Kategori personal berhasil dibuat",
            data=CategoryResponse.model_validate(category.model_dump())
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/global",
    response_model=DataResponse[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create global category",
    description="Create new global category (admin only)"
)
@auth_rate_limit()
async def create_global_category(
    *,
    category_in: CategoryCreate,
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> DataResponse[CategoryResponse]:
    """
    Create global category
    
    **Admin only endpoint**
    
    - Category akan menjadi global category
    - Bisa digunakan oleh semua user
    """
    try:
        # Ensure it's global category
        category_data = category_in.model_dump()
        category_data["is_global"] = True
        category_create = CategoryCreate.model_validate(category_data)
        
        category = await crud_category.create_category(
            obj_in=category_create,
            created_by=None,  # Global categories don't have owner
            is_admin=True
        )
        
        return DataResponse(
            message="Kategori global berhasil dibuat",
            data=CategoryResponse.model_validate(category.model_dump())
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/global",
    response_model=DataResponse[List[CategoryPublicResponse]],
    summary="Get global categories",
    description="Get all global categories"
)
@standard_rate_limit()
async def get_global_categories(
    category_type: Optional[CategoryType] = Query(None, description="Filter by category type")
) -> DataResponse[List[CategoryPublicResponse]]:
    """Get all global categories"""
    categories = await crud_category.get_global_categories(category_type)
    
    return DataResponse(
        message="Global categories retrieved successfully",
        data=[CategoryPublicResponse.model_validate(cat.model_dump()) for cat in categories]
    )


@router.get(
    "/personal",
    response_model=DataResponse[List[CategoryResponse]],
    summary="Get personal categories",
    description="Get personal categories untuk current user"
)
@standard_rate_limit()
async def get_personal_categories(
    *,
    category_type: Optional[CategoryType] = Query(None, description="Filter by category type"),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[List[CategoryResponse]]:
    """Get personal categories untuk current user"""
    categories = await crud_category.get_personal_categories(
        user_id=current_user.id,
        category_type=category_type
    )
    
    return DataResponse(
        message="Personal categories retrieved successfully",
        data=[CategoryResponse.model_validate(cat.model_dump()) for cat in categories]
    )


@router.get(
    "/popular",
    response_model=DataResponse[List[CategoryPublicResponse]],
    summary="Get popular categories",
    description="Get popular categories berdasarkan usage"
)
@standard_rate_limit()
async def get_popular_categories(
    *,
    category_type: Optional[CategoryType] = Query(None, description="Filter by category type"),
    limit: int = Query(10, ge=1, le=50, description="Number of categories"),
    global_only: bool = Query(False, description="Only global categories")
) -> DataResponse[List[CategoryPublicResponse]]:
    """Get popular categories berdasarkan usage count"""
    categories = await crud_category.get_popular_categories(
        category_type=category_type,
        limit=limit,
        global_only=global_only
    )
    
    return DataResponse(
        message="Popular categories retrieved successfully",
        data=[CategoryPublicResponse.model_validate(cat.model_dump()) for cat in categories]
    )


@router.get(
    "/stats",
    response_model=DataResponse[CategoryStatsResponse],
    summary="Get category statistics",
    description="Get category statistics"
)
@standard_rate_limit()
async def get_category_stats(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[CategoryStatsResponse]:
    """
    Get category statistics
    
    - For regular users: includes personal stats
    - For admins: includes global stats
    """
    user_id = current_user.id if not current_user.is_admin else None
    stats = await crud_category.get_category_stats(user_id)
    
    return DataResponse(
        message="Category statistics retrieved successfully",
        data=CategoryStatsResponse.model_validate(stats)
    )


@router.get(
    "/{category_id}",
    response_model=DataResponse[CategoryResponse],
    summary="Get category by ID",
    description="Get category details by ID"
)
@standard_rate_limit()
async def get_category_by_id(
    *,
    category_id: str = Depends(validate_category_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[CategoryResponse]:
    """Get category by ID"""
    category = await crud_category.get(category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategori tidak ditemukan"
        )
    
    # Check if user can access this category
    if not category.can_be_used_by(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki akses ke kategori ini"
        )
    
    return DataResponse(
        message="Category retrieved successfully",
        data=CategoryResponse.model_validate(category.model_dump())
    )


@router.put(
    "/{category_id}",
    response_model=DataResponse[CategoryResponse],
    summary="Update category",
    description="Update category by ID"
)
@auth_rate_limit()
async def update_category(
    *,
    category_id: str = Depends(validate_category_id),
    category_update: CategoryUpdate,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> DataResponse[CategoryResponse]:
    """
    Update category
    
    - Users can only update their personal categories
    - Admins can update any category
    """
    try:
        category = await crud_category.update_category(
            category_id=category_id,
            obj_in=category_update,
            user_id=current_user.id,
            is_admin=current_user.is_admin
        )
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kategori tidak ditemukan"
            )
        
        return DataResponse(
            message="Kategori berhasil diupdate",
            data=CategoryResponse.model_validate(category.model_dump())
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{category_id}",
    response_model=SuccessResponse,
    summary="Delete category",
    description="Delete category by ID"
)
@auth_rate_limit()
async def delete_category(
    *,
    category_id: str = Depends(validate_category_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> SuccessResponse:
    """
    Delete category
    
    - Users can only delete their personal categories
    - Admins can delete any category
    - Performs soft delete
    """
    try:
        success = await crud_category.delete_category(
            category_id=category_id,
            user_id=current_user.id,
            is_admin=current_user.is_admin,
            soft=True
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kategori tidak ditemukan"
            )
        
        return SuccessResponse(message="Kategori berhasil dihapus")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{category_id}/activate",
    response_model=SuccessResponse,
    summary="Activate category",
    description="Activate category"
)
@auth_rate_limit()
async def activate_category(
    *,
    category_id: str = Depends(validate_category_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> SuccessResponse:
    """Activate category"""
    category = await crud_category.get(category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategori tidak ditemukan"
        )
    
    if not category.can_be_edited_by(current_user.id, current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki permission untuk mengaktifkan kategori ini"
        )
    
    await crud_category.activate_category(category_id)
    
    return SuccessResponse(message="Kategori berhasil diaktifkan")


@router.patch(
    "/{category_id}/deactivate",
    response_model=SuccessResponse,
    summary="Deactivate category",
    description="Deactivate category"
)
@auth_rate_limit()
async def deactivate_category(
    *,
    category_id: str = Depends(validate_category_id),
    current_user: CurrentUser = Depends(get_current_active_user)
) -> SuccessResponse:
    """Deactivate category"""
    category = await crud_category.get(category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategori tidak ditemukan"
        )
    
    if not category.can_be_edited_by(current_user.id, current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki permission untuk menonaktifkan kategori ini"
        )
    
    await crud_category.deactivate_category(category_id)
    
    return SuccessResponse(message="Kategori berhasil dinonaktifkan")


@router.post(
    "/default",
    response_model=DataResponse[DefaultCategoriesResponse],
    summary="Create default categories",
    description="Create default global categories (admin only)"
)
@auth_rate_limit()
async def create_default_categories(
    *,
    current_user: CurrentUser = Depends(get_current_admin_user)
) -> DataResponse[DefaultCategoriesResponse]:
    """
    Create default global categories
    
    **Admin only endpoint**
    
    - Creates predefined global categories for income & expense
    - Skips categories that already exist
    """
    try:
        categories = await crud_category.create_default_categories(current_user.id)
        
        return DataResponse(
            message="Default categories creation completed",
            data=DefaultCategoriesResponse(
                success=True,
                message="Default categories berhasil dibuat",
                created_count=len(categories),
                existing_count=0,  # Will be calculated in real implementation
                categories=[CategoryResponse.model_validate(cat.model_dump()) for cat in categories]
            )
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create default categories: {str(e)}"
        )