# app/routers/profile.py
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.security import HTTPBearer
from typing import Optional
from bson import ObjectId
from datetime import datetime
import os
import uuid
from PIL import Image
import io

from ..database import get_database
from ..models.user import (
    User, UserResponse, UserProfileUpdate, 
    InitialBalanceSet, NotificationSettings
)
from ..middleware.auth_middleware import get_current_verified_user
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/profile", tags=["User Profile"])
security = HTTPBearer()

@router.get("/", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Get current user profile"""
    try:
        user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        
        if not user:
            raise CustomHTTPException(
                status_code=404,
                detail="Profil pengguna tidak ditemukan"
            )
        
        return UserResponse(**user)
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mengambil profil pengguna: {str(e)}"
        )

@router.put("/", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Update user profile data"""
    try:
        # Build update query
        update_data = {}
        
        if profile_data.nama_lengkap:
            update_data["nama_lengkap"] = profile_data.nama_lengkap
        
        if profile_data.nomor_telepon:
            update_data["nomor_telepon"] = profile_data.nomor_telepon
        
        if profile_data.fakultas:
            update_data["fakultas"] = profile_data.fakultas
        
        if profile_data.prodi:
            update_data["prodi"] = profile_data.prodi
        
        if not update_data:
            raise CustomHTTPException(
                status_code=400,
                detail="Tidak ada data yang akan diperbarui"
            )
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update user profile
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise CustomHTTPException(
                status_code=400,
                detail="Gagal memperbarui profil pengguna"
            )
        
        # Get updated user
        updated_user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        
        return UserResponse(**updated_user)
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal memperbarui profil: {str(e)}"
        )

@router.post("/upload-avatar")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Upload profile picture"""
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise CustomHTTPException(
                status_code=400,
                detail="File harus berupa gambar"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size (max 2MB)
        if len(content) > 2 * 1024 * 1024:
            raise CustomHTTPException(
                status_code=400,
                detail="Ukuran file maksimal 2MB"
            )
        
        # Process image
        try:
            image = Image.open(io.BytesIO(content))
            
            # Resize image if too large
            if image.width > 500 or image.height > 500:
                image.thumbnail((500, 500), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            # Save processed image
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=85)
            content = output.getvalue()
            
        except Exception as e:
            raise CustomHTTPException(
                status_code=400,
                detail="File gambar tidak valid"
            )
        
        # Generate unique filename
        file_extension = "jpg"
        filename = f"{current_user['id']}_{uuid.uuid4()}.{file_extension}"
        
        # Create upload directory if not exists
        upload_dir = "uploads/profile_pictures"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Update user profile with new picture path
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {
                "$set": {
                    "profile_picture": f"/{file_path}",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            # Clean up uploaded file
            os.remove(file_path)
            raise CustomHTTPException(
                status_code=400,
                detail="Gagal menyimpan foto profil"
            )
        
        return {
            "message": "Foto profil berhasil diupload",
            "profile_picture": f"/{file_path}"
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mengupload foto profil: {str(e)}"
        )

@router.put("/initial-balance")
async def set_initial_balance(
    balance_data: InitialBalanceSet,
    current_user: dict = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Set initial balance (one-time only)"""
    try:
        # Check if user already has initial balance set
        user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        
        if user.get("tabungan_awal") is not None:
            raise CustomHTTPException(
                status_code=400,
                detail="Tabungan awal sudah pernah diatur sebelumnya"
            )
        
        # Set initial balance
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {
                "$set": {
                    "tabungan_awal": balance_data.tabungan_awal,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise CustomHTTPException(
                status_code=400,
                detail="Gagal mengatur tabungan awal"
            )
        
        return {
            "message": "Tabungan awal berhasil diatur",
            "tabungan_awal": balance_data.tabungan_awal
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mengatur tabungan awal: {str(e)}"
        )

@router.get("/notification-settings", response_model=NotificationSettings)
async def get_notification_settings(
    current_user: dict = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Get notification preferences"""
    try:
        user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        
        if not user:
            raise CustomHTTPException(
                status_code=404,
                detail="Pengguna tidak ditemukan"
            )
        
        # Return notification settings or default values
        notification_settings = user.get("notification_settings", {})
        return NotificationSettings(**notification_settings)
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal mengambil pengaturan notifikasi: {str(e)}"
        )

@router.put("/notification-settings", response_model=NotificationSettings)
async def update_notification_settings(
    settings: NotificationSettings,
    current_user: dict = Depends(get_current_verified_user),
    db = Depends(get_database)
):
    """Update notification preferences"""
    try:
        # Update notification settings
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {
                "$set": {
                    "notification_settings": settings.model_dump(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise CustomHTTPException(
                status_code=400,
                detail="Gagal memperbarui pengaturan notifikasi"
            )
        
        return settings
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal memperbarui pengaturan notifikasi: {str(e)}"
        )