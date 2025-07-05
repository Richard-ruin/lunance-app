# app/middleware/auth_middleware.py (updated)
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from bson import ObjectId
from datetime import datetime

from ..auth.jwt_handler import verify_token
from ..database import get_database
from ..models.user import User
from ..utils.exceptions import CustomHTTPException

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if not payload:
            raise CustomHTTPException(
                status_code=401,
                detail="Token tidak valid",
                error_code="INVALID_TOKEN"
            )
        
        if payload.get("type") != "access":
            raise CustomHTTPException(
                status_code=401,
                detail="Tipe token tidak valid",
                error_code="INVALID_TOKEN_TYPE"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise CustomHTTPException(
                status_code=401,
                detail="Token tidak mengandung ID pengguna",
                error_code="MISSING_USER_ID"
            )
        
        db = await get_database()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise CustomHTTPException(
                status_code=401,
                detail="Pengguna tidak ditemukan",
                error_code="USER_NOT_FOUND"
            )
        
        if not user.get("is_active", True):
            raise CustomHTTPException(
                status_code=401,
                detail="Akun tidak aktif",
                error_code="ACCOUNT_INACTIVE"
            )
        
        # Return user data as dict for easier access
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "nama_lengkap": user["nama_lengkap"],
            "role": user["role"],
            "is_verified": user.get("is_verified", False),
            "is_active": user.get("is_active", True),
            "universitas_id": str(user.get("universitas_id", "")),
            "fakultas": user.get("fakultas", ""),
            "prodi": user.get("prodi", "")
        }
        
    except CustomHTTPException:
        raise
    except Exception as e:
        raise CustomHTTPException(
            status_code=500,
            detail=f"Gagal memverifikasi token: {str(e)}",
            error_code="TOKEN_VERIFICATION_ERROR"
        )

async def get_current_verified_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current verified user"""
    if not current_user.get("is_verified", False):
        raise CustomHTTPException(
            status_code=403,
            detail="Email belum diverifikasi. Silakan verifikasi email terlebih dahulu.",
            error_code="EMAIL_NOT_VERIFIED"
        )
    return current_user

async def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_verified_user)):
    """Get current admin user"""
    if current_user.get("role") != "admin":
        raise CustomHTTPException(
            status_code=403,
            detail="Akses ditolak. Hanya admin yang dapat mengakses endpoint ini.",
            error_code="ADMIN_ACCESS_REQUIRED"
        )
    return current_user

# Legacy support for User model return
async def get_current_user_model(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user as User model (for backward compatibility)"""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        db = await get_database()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return User(**user)
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_verified_user_model(current_user: User = Depends(get_current_user_model)):
    """Get current verified user as User model (for backward compatibility)"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user

async def get_current_admin_user_model(current_user: User = Depends(get_current_verified_user_model)):
    """Get current admin user as User model (for backward compatibility)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Request logging middleware
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.utcnow()
    
    # Log request
    print(f"[{start_time}] {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = (datetime.utcnow() - start_time).total_seconds()
    print(f"[{datetime.utcnow()}] Response: {response.status_code} - {process_time:.2f}s")
    
    return response