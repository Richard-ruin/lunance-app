# app/routers/admin_users.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timedelta

from ..database import get_database
from ..models.user import User, UserResponse, UserStats
from ..middleware.auth_middleware import get_current_admin_user
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/admin/users", tags=["Admin - User Management"])
security = HTTPBearer()

@router.get("/", response_model=List[UserResponse])
async def list_users(
    current_admin: dict = Depends(get_current_admin_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db = Depends(get_database)
):
    """List all users with pagination and filters"""
    try:
        # Build filter query
        filter_query = {}
        
        if search:
            filter_query["$or"] = [
                {"nama_lengkap": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        
        if role:
            filter_query["role"] = role
            
        if status == "active":
            filter_query["is_active"] = True
        elif status == "inactive":
            filter_query["is_active"] = False
        
        # Get users with pagination
        users_cursor = db.users.find(filter_query).skip(skip).limit(limit)
        users = await users_cursor.to_list(length=limit)
        
        return [UserResponse(**user) for user in users]
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mengambil data pengguna: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_detail(
    user_id: str,
    current_admin: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """Get user detail by ID"""
    try:
        if not ObjectId.is_valid(user_id):
            raise CustomHTTPException(
                status_code=400,
                detail="ID pengguna tidak valid"
            )
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise CustomHTTPException(
                status_code=404,
                detail="Pengguna tidak ditemukan"
            )
        
        return UserResponse(**user)
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mengambil detail pengguna: {str(e)}"
        )

@router.put("/{user_id}/status")
async def update_user_status(
    user_id: str,
    is_active: bool,
    current_admin: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """Activate or deactivate user"""
    try:
        if not ObjectId.is_valid(user_id):
            raise CustomHTTPException(
                status_code=400,
                detail="ID pengguna tidak valid"
            )
        
        # Check if user exists
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise CustomHTTPException(
                status_code=404,
                detail="Pengguna tidak ditemukan"
            )
        
        # Update user status
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "is_active": is_active,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise CustomHTTPException(
                status_code=400,
                detail="Gagal memperbarui status pengguna"
            )
        
        return {
            "message": f"Status pengguna berhasil {'diaktifkan' if is_active else 'dinonaktifkan'}",
            "user_id": user_id,
            "is_active": is_active
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal memperbarui status pengguna: {str(e)}"
        )

@router.delete("/{user_id}")
async def soft_delete_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """Soft delete user (deactivate)"""
    try:
        if not ObjectId.is_valid(user_id):
            raise CustomHTTPException(
                status_code=400,
                detail="ID pengguna tidak valid"
            )
        
        # Check if user exists and is not admin
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise CustomHTTPException(
                status_code=404,
                detail="Pengguna tidak ditemukan"
            )
        
        if user["role"] == "admin":
            raise CustomHTTPException(
                status_code=403,
                detail="Tidak dapat menghapus pengguna admin"
            )
        
        # Soft delete (deactivate)
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise CustomHTTPException(
                status_code=400,
                detail="Gagal menghapus pengguna"
            )
        
        return {
            "message": "Pengguna berhasil dihapus",
            "user_id": user_id
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal menghapus pengguna: {str(e)}"
        )

@router.get("/stats/overview", response_model=UserStats)
async def get_user_stats(
    current_admin: dict = Depends(get_current_admin_user),
    db = Depends(get_database)
):
    """Get user statistics for admin dashboard"""
    try:
        # Get basic counts
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({"is_active": True})
        verified_users = await db.users.count_documents({"is_verified": True})
        pending_verifications = await db.users.count_documents({"is_verified": False})
        total_admins = await db.users.count_documents({"role": "admin"})
        
        # Get recent registrations (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_registrations = await db.users.count_documents({
            "created_at": {"$gte": week_ago}
        })
        
        return UserStats(
            total_users=total_users,
            active_users=active_users,
            verified_users=verified_users,
            pending_verifications=pending_verifications,
            total_admins=total_admins,
            recent_registrations=recent_registrations
        )
        
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mengambil statistik pengguna: {str(e)}"
        )