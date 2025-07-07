from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.auth_service import AuthService
from app.models.user import User

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Middleware to get current authenticated user from JWT token
    """
    try:
        # Extract token from Authorization header
        token = credentials.credentials
        
        # Verify token and get user
        user = AuthService.get_current_user(token)
        
        # Check if user is active
        if user.status != "approved":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akun belum disetujui atau tidak aktif"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau telah kedaluwarsa",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Middleware to ensure current user is an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Hanya admin yang diizinkan."
        )
    
    return current_user

async def get_optional_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[User]:
    """
    Optional authentication - returns user if token is provided and valid, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = AuthService.get_current_user(token)
        
        if user.status != "approved":
            return None
        
        return user
        
    except Exception:
        return None

class RoleRequired:
    """
    Role-based access control decorator
    """
    def __init__(self, required_role: str):
        self.required_role = required_role
    
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != self.required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak. Role {self.required_role} diperlukan."
            )
        return current_user

# Role dependency instances
require_admin = RoleRequired("admin")
require_mahasiswa = RoleRequired("mahasiswa")

def verify_user_access(target_user_id: str, current_user: User) -> bool:
    """
    Verify if current user can access target user data
    - Admin can access all users
    - Regular users can only access their own data
    """
    if current_user.role == "admin":
        return True
    
    return str(current_user.id) == target_user_id

async def get_user_with_access_check(user_id: str, current_user: User = Depends(get_current_user)) -> User:
    """
    Get user with access permission check
    """
    if not verify_user_access(user_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Anda tidak memiliki izin untuk mengakses data user ini."
        )
    
    if user_id == str(current_user.id):
        return current_user
    
    # If admin accessing other user
    target_user = User.find_by_id(user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User tidak ditemukan"
        )
    
    return target_user