# app/routers/categories.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from ..models.category import CategoryCreate, CategoryResponse, CategoryUpdate, Category
from ..models.user import User
from ..middleware.auth_middleware import get_current_verified_user, get_current_admin_user
from ..database import get_database
from ..utils.exceptions import NotFoundException, ForbiddenException
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    type: Optional[str] = Query(None, pattern="^(pemasukan|pengeluaran)$"),
    is_active: bool = Query(True),
    current_user: User = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """List categories (global + user personal categories)"""
    
    # Build filter
    filter_query = {
        "$or": [
            {"is_global": True, "is_active": is_active},
            {"created_by": ObjectId(current_user.id), "is_active": is_active}
        ]
    }
    
    if type:
        filter_query["type"] = type
    
    # Get categories
    cursor = db.categories.find(filter_query).sort("nama_kategori", 1)
    categories = await cursor.to_list(length=None)
    
    return [
        CategoryResponse(
            _id=str(cat["_id"]),
            nama_kategori=cat["nama_kategori"],
            icon=cat["icon"],
            color=cat["color"],
            type=cat["type"],
            is_global=cat["is_global"],
            is_active=cat["is_active"],
            created_at=cat["created_at"]
        )
        for cat in categories
    ]

@router.get("/global", response_model=List[CategoryResponse])
async def list_global_categories(
    type: Optional[str] = Query(None, pattern="^(pemasukan|pengeluaran)$"),
    current_user: User = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """List global categories only"""
    
    filter_query = {"is_global": True, "is_active": True}
    if type:
        filter_query["type"] = type
    
    cursor = db.categories.find(filter_query).sort("nama_kategori", 1)
    categories = await cursor.to_list(length=None)
    
    return [
        CategoryResponse(
            _id=str(cat["_id"]),
            nama_kategori=cat["nama_kategori"],
            icon=cat["icon"],
            color=cat["color"],
            type=cat["type"],
            is_global=cat["is_global"],
            is_active=cat["is_active"],
            created_at=cat["created_at"]
        )
        for cat in categories
    ]

@router.get("/personal", response_model=List[CategoryResponse])
async def list_personal_categories(
    type: Optional[str] = Query(None, pattern="^(pemasukan|pengeluaran)$"),
    current_user: User = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """List user personal categories"""
    
    filter_query = {
        "created_by": ObjectId(current_user.id),
        "is_active": True
    }
    if type:
        filter_query["type"] = type
    
    cursor = db.categories.find(filter_query).sort("nama_kategori", 1)
    categories = await cursor.to_list(length=None)
    
    return [
        CategoryResponse(
            _id=str(cat["_id"]),
            nama_kategori=cat["nama_kategori"],
            icon=cat["icon"],
            color=cat["color"],
            type=cat["type"],
            is_global=cat["is_global"],
            is_active=cat["is_active"],
            created_at=cat["created_at"]
        )
        for cat in categories
    ]

@router.post("/", response_model=CategoryResponse)
async def create_personal_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Create personal category"""
    
    # Check if category name already exists for this user
    existing = await db.categories.find_one({
        "nama_kategori": category_data.nama_kategori,
        "created_by": ObjectId(current_user.id),
        "is_active": True
    })
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Kategori dengan nama tersebut sudah ada"
        )
    
    # Create category
    category = Category(
        nama_kategori=category_data.nama_kategori,
        icon=category_data.icon,
        color=category_data.color,
        type=category_data.type,
        is_global=False,  # Personal category
        created_by=ObjectId(current_user.id),
        is_active=True
    )
    
    result = await db.categories.insert_one(category.model_dump(by_alias=True))
    
    # Get created category
    created_category = await db.categories.find_one({"_id": result.inserted_id})
    
    return CategoryResponse(
        _id=str(created_category["_id"]),
        nama_kategori=created_category["nama_kategori"],
        icon=created_category["icon"],
        color=created_category["color"],
        type=created_category["type"],
        is_global=created_category["is_global"],
        is_active=created_category["is_active"],
        created_at=created_category["created_at"]
    )

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_personal_category(
    category_id: str,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Update personal category"""
    
    # Check if category exists and belongs to user
    category = await db.categories.find_one({
        "_id": ObjectId(category_id),
        "created_by": ObjectId(current_user.id),
        "is_global": False
    })
    
    if not category:
        raise NotFoundException("Kategori tidak ditemukan")
    
    # Prepare update data
    update_data = {}
    if category_data.nama_kategori is not None:
        # Check name uniqueness
        existing = await db.categories.find_one({
            "nama_kategori": category_data.nama_kategori,
            "created_by": ObjectId(current_user.id),
            "_id": {"$ne": ObjectId(category_id)},
            "is_active": True
        })
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Kategori dengan nama tersebut sudah ada"
            )
        update_data["nama_kategori"] = category_data.nama_kategori
    
    if category_data.icon is not None:
        update_data["icon"] = category_data.icon
    if category_data.color is not None:
        update_data["color"] = category_data.color
    if category_data.is_active is not None:
        update_data["is_active"] = category_data.is_active
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.categories.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": update_data}
        )
    
    # Get updated category
    updated_category = await db.categories.find_one({"_id": ObjectId(category_id)})
    
    return CategoryResponse(
        _id=str(updated_category["_id"]),
        nama_kategori=updated_category["nama_kategori"],
        icon=updated_category["icon"],
        color=updated_category["color"],
        type=updated_category["type"],
        is_global=updated_category["is_global"],
        is_active=updated_category["is_active"],
        created_at=updated_category["created_at"]
    )

@router.delete("/{category_id}")
async def delete_personal_category(
    category_id: str,
    current_user: User = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Delete personal category (soft delete)"""
    
    # Check if category exists and belongs to user
    category = await db.categories.find_one({
        "_id": ObjectId(category_id),
        "created_by": ObjectId(current_user.id),
        "is_global": False
    })
    
    if not category:
        raise NotFoundException("Kategori tidak ditemukan")
    
    # Check if category is used in transactions
    transaction_count = await db.transactions.count_documents({
        "category_id": ObjectId(category_id),
        "user_id": ObjectId(current_user.id)
    })
    
    if transaction_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Kategori tidak dapat dihapus karena digunakan dalam {transaction_count} transaksi"
        )
    
    # Soft delete
    await db.categories.update_one(
        {"_id": ObjectId(category_id)},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Kategori berhasil dihapus"}

# Admin category management
@router.get("/admin", response_model=List[CategoryResponse])
async def admin_list_global_categories(
    type: Optional[str] = Query(None, pattern="^(pemasukan|pengeluaran)$"),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """Admin: List global categories"""
    
    filter_query = {"is_global": True}
    if type:
        filter_query["type"] = type
    if is_active is not None:
        filter_query["is_active"] = is_active
    
    cursor = db.categories.find(filter_query).sort("nama_kategori", 1)
    categories = await cursor.to_list(length=None)
    
    return [
        CategoryResponse(
            _id=str(cat["_id"]),
            nama_kategori=cat["nama_kategori"],
            icon=cat["icon"],
            color=cat["color"],
            type=cat["type"],
            is_global=cat["is_global"],
            is_active=cat["is_active"],
            created_at=cat["created_at"]
        )
        for cat in categories
    ]

@router.post("/admin", response_model=CategoryResponse)
async def admin_create_global_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """Admin: Create global category"""
    
    # Check if global category name already exists
    existing = await db.categories.find_one({
        "nama_kategori": category_data.nama_kategori,
        "is_global": True,
        "is_active": True
    })
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Kategori global dengan nama tersebut sudah ada"
        )
    
    # Create global category
    category = Category(
        nama_kategori=category_data.nama_kategori,
        icon=category_data.icon,
        color=category_data.color,
        type=category_data.type,
        is_global=True,  # Global category
        created_by=ObjectId(current_user.id),
        is_active=True
    )
    
    result = await db.categories.insert_one(category.model_dump(by_alias=True))
    
    # Get created category
    created_category = await db.categories.find_one({"_id": result.inserted_id})
    
    return CategoryResponse(
        _id=str(created_category["_id"]),
        nama_kategori=created_category["nama_kategori"],
        icon=created_category["icon"],
        color=created_category["color"],
        type=created_category["type"],
        is_global=created_category["is_global"],
        is_active=created_category["is_active"],
        created_at=created_category["created_at"]
    )