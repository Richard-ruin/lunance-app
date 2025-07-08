# app/api/v1/endpoints/categories.py
"""Category management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
import logging

from app.models.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithStats,
    CategoryStats, GlobalCategoryCreate
)
from app.models.common import (
    PaginatedResponse, PaginationParams, SuccessResponse
)
from app.services.category_service import (
    CategoryService, CategoryServiceError, category_service
)
from app.middleware.auth import (
    get_current_verified_user, require_admin, rate_limit_dependency
)
from app.models.user import UserInDB

logger = logging.getLogger(__name__)

router = APIRouter()


# User endpoints for category management
@router.get("", response_model=PaginatedResponse[CategoryResponse])
async def list_categories(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    category_type: Optional[str] = Query(None, regex="^(global|personal|all)$", description="Category type filter"),
    search: Optional[str] = Query(None, min_length=1, max_length=50, description="Search term"),
    current_user: UserInDB = Depends(get_current_verified_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    List categories (global + personal) for current user.
    """
    try:
        pagination = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        result = await category_service.list_categories(
            user_id=str(current_user.id),
            pagination=pagination,
            category_type=category_type,
            search=search
        )
        
        return result
        
    except CategoryServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list categories"
        )


@router.get("/global", response_model=PaginatedResponse[CategoryResponse])
async def list_global_categories(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(None, min_length=1, max_length=50, description="Search term"),
    current_user: UserInDB = Depends(get_current_verified_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    List global categories only.
    """
    try:
        pagination = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        result = await category_service.list_categories(
            user_id=str(current_user.id),
            pagination=pagination,
            category_type="global",
            search=search
        )
        
        return result
        
    except CategoryServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing global categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list global categories"
        )


@router.get("/personal", response_model=PaginatedResponse[CategoryResponse])
async def list_personal_categories(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    search: Optional[str] = Query(None, min_length=1, max_length=50, description="Search term"),
    current_user: UserInDB = Depends(get_current_verified_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    List personal categories only.
    """
    try:
        pagination = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        result = await category_service.list_categories(
            user_id=str(current_user.id),
            pagination=pagination,
            category_type="personal",
            search=search
        )
        
        return result
        
    except CategoryServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing personal categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list personal categories"
        )


@router.get("/with-stats", response_model=List[CategoryWithStats])
async def get_categories_with_stats(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get categories with usage statistics.
    """
    try:
        from datetime import datetime
        
        start_datetime = None
        end_datetime = None
        
        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        
        categories = await category_service.get_categories_with_stats(
            user_id=str(current_user.id),
            start_date=start_datetime,
            end_date=end_datetime
        )
        
        return categories
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        logger.error(f"Error getting categories with stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get categories with statistics"
        )


@router.get("/search", response_model=List[CategoryResponse])
async def search_categories(
    q: str = Query(..., min_length=1, max_length=50, description="Search term"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    current_user: UserInDB = Depends(get_current_verified_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    Search categories by name.
    """
    try:
        categories = await category_service.search_categories(
            user_id=str(current_user.id),
            search_term=q,
            limit=limit
        )
        
        return categories
        
    except Exception as e:
        logger.error(f"Error searching categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search categories"
        )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_detail(
    category_id: str,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Get category detail by ID.
    """
    try:
        category = await category_service.get_category_by_id(
            category_id=category_id,
            user_id=str(current_user.id)
        )
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category detail {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get category detail"
        )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_personal_category(
    category_data: CategoryCreate,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Create new personal category.
    """
    try:
        # Ensure this is a personal category
        category_data.is_global = False
        category_data.user_id = str(current_user.id)
        
        category = await category_service.create_category(
            category_data=category_data,
            user_id=str(current_user.id)
        )
        
        return category
        
    except CategoryServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating personal category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create category"
        )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_personal_category(
    category_id: str,
    update_data: CategoryUpdate,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Update personal category (only owner can update personal categories).
    """
    try:
        updated_category = await category_service.update_category(
            category_id=category_id,
            update_data=update_data,
            user_id=str(current_user.id),
            is_admin=False
        )
        
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return updated_category
        
    except CategoryServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update category"
        )


@router.delete("/{category_id}", response_model=SuccessResponse)
async def delete_personal_category(
    category_id: str,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Delete personal category (only owner can delete personal categories).
    """
    try:
        success = await category_service.delete_category(
            category_id=category_id,
            user_id=str(current_user.id),
            is_admin=False
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return SuccessResponse(
            message="Category deleted successfully"
        )
        
    except CategoryServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete category"
        )


# Admin endpoints for global category management
@router.post("/global", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_global_category(
    category_data: GlobalCategoryCreate,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Create new global category (admin only).
    """
    try:
        # Convert to CategoryCreate with global flag
        global_category_data = CategoryCreate(
            name=category_data.name,
            icon=category_data.icon,
            color=category_data.color,
            is_global=True,
            user_id=None
        )
        
        category = await category_service.create_category(
            category_data=global_category_data,
            user_id=None
        )
        
        return category
        
    except CategoryServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating global category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create global category"
        )


@router.put("/global/{category_id}", response_model=CategoryResponse)
async def update_global_category(
    category_id: str,
    update_data: CategoryUpdate,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Update global category (admin only).
    """
    try:
        updated_category = await category_service.update_category(
            category_id=category_id,
            update_data=update_data,
            user_id=str(current_user.id),
            is_admin=True
        )
        
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Global category not found"
            )
        
        return updated_category
        
    except CategoryServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating global category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update global category"
        )


@router.delete("/global/{category_id}", response_model=SuccessResponse)
async def delete_global_category(
    category_id: str,
    current_user: UserInDB = Depends(require_admin())
):
    """
    Delete global category (admin only).
    """
    try:
        success = await category_service.delete_category(
            category_id=category_id,
            user_id=str(current_user.id),
            is_admin=True
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Global category not found"
            )
        
        return SuccessResponse(
            message="Global category deleted successfully"
        )
        
    except CategoryServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting global category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete global category"
        )


@router.get("/admin/stats", response_model=CategoryStats)
async def get_category_stats(
    current_user: UserInDB = Depends(require_admin())
):
    """
    Get category system statistics (admin only).
    """
    try:
        stats = await category_service.get_category_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting category stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get category statistics"
        )


@router.post("/admin/initialize-defaults", response_model=SuccessResponse)
async def initialize_default_categories(
    current_user: UserInDB = Depends(require_admin())
):
    """
    Initialize default global categories (admin only).
    """
    try:
        created_count = await category_service.create_default_global_categories()
        
        return SuccessResponse(
            message=f"Successfully created {created_count} default global categories",
            data={"created_count": created_count}
        )
        
    except Exception as e:
        logger.error(f"Error initializing default categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize default categories"
        )