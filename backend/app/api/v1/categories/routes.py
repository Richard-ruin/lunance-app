# app/api/v1/categories/routes.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.api.deps import get_current_user, get_database
from app.models.student import Student
from app.models.category import Category, CategoryCreate, CategoryUpdate, CategoryWithStats
from app.api.v1.categories.crud import CategoryCRUD

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=Category)
async def create_category(
    category_data: CategoryCreate,
    current_user: Student = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a new category"""
    try:
        crud = CategoryCRUD(db)
        category = await crud.create_category(category_data, str(current_user.id))
        return category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[Category])
async def get_categories(
    category_type: Optional[str] = Query(None, description="Filter by type: income or expense"),
    current_user: Student = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get all categories for the current user"""
    try:
        crud = CategoryCRUD(db)
        categories = await crud.get_categories_by_user(str(current_user.id), category_type)
        return categories
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/with-stats", response_model=List[CategoryWithStats])
async def get_categories_with_stats(
    category_type: Optional[str] = Query(None, description="Filter by type: income or expense"),
    current_user: Student = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get categories with transaction statistics"""
    try:
        crud = CategoryCRUD(db)
        categories = await crud.get_categories_with_stats(str(current_user.id), category_type)
        return categories
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/popular", response_model=List[CategoryWithStats])
async def get_popular_categories(
    category_type: Optional[str] = Query(None, description="Filter by type: income or expense"),
    limit: int = Query(10, ge=1, le=50, description="Number of categories to return"),
    current_user: Student = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get most popular categories based on usage"""
    try:
        crud = CategoryCRUD(db)
        categories = await crud.get_popular_categories(str(current_user.id), category_type, limit)
        return categories
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search", response_model=List[Category])
async def search_categories(
    q: str = Query(..., min_length=1, description="Search term"),
    category_type: Optional[str] = Query(None, description="Filter by type: income or expense"),
    current_user: Student = Depends(get_current_user),
    db = Depends(get_database)
):
    """Search categories by name or keywords"""
    try:
        crud = CategoryCRUD(db)
        categories = await crud.search_categories(str(current_user.id), q, category_type)
        return categories
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{category_id}", response_model=Category)
async def get_category(
    category_id: str,
    current_user: Student = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get a specific category by ID"""
    try:
        crud = CategoryCRUD(db)
        category = await crud.get_category_by_id(category_id, str(current_user.id))
        
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
            
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: str,
    update_data: CategoryUpdate,
    current_user: Student = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update a category"""
    try:
        crud = CategoryCRUD(db)
        category = await crud.update_category(category_id, str(current_user.id), update_data)
        
        if not category:
            raise HTTPException(
                status_code=404, 
                detail="Category not found or you don't have permission to update it"
            )
            
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    current_user: Student = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete a category"""
    try:
        crud = CategoryCRUD(db)
        success = await crud.delete_category(category_id, str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete category. It may be in use by transactions or is a system category."
            )
            
        return JSONResponse(
            status_code=200,
            content={"message": "Category deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Endpoint untuk mendapatkan default categories untuk student baru
@router.get("/defaults/student", response_model=List[Category])
async def get_default_student_categories(
    current_user: Student = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get default categories for students"""
    try:
        crud = CategoryCRUD(db)
        
        # Get system categories that are student-specific
        system_categories = await crud.get_categories_by_user("system")  # We'll need to adjust this
        
        # Filter for student-specific system categories
        student_categories = [cat for cat in system_categories if cat.is_system and cat.student_specific]
        
        return student_categories
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))