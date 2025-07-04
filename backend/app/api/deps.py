"""
API Dependencies
Dependencies untuk FastAPI endpoints (database, authentication, etc.)
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..config.database import database, get_database


# Database Dependencies
async def get_db() -> AsyncIOMotorDatabase:
    """
    Dependency untuk mendapatkan database instance
    
    Returns:
        Database instance
    """
    return await get_database()


# Utility Dependencies
def get_skip_limit(skip: int = 0, limit: int = 100) -> tuple[int, int]:
    """
    Dependency untuk pagination parameters dengan validasi
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        Validated (skip, limit) tuple
        
    Raises:
        HTTPException: Jika parameter tidak valid
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Skip parameter must be >= 0"
        )
    
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Limit parameter must be between 1 and 1000"
        )
    
    return skip, limit


def get_pagination_params(page: int = 1, per_page: int = 10) -> tuple[int, int]:
    """
    Dependency untuk pagination dengan page-based parameters
    
    Args:
        page: Page number (starts from 1)
        per_page: Number of items per page
        
    Returns:
        (skip, limit) tuple untuk database query
        
    Raises:
        HTTPException: Jika parameter tidak valid
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Page parameter must be >= 1"
        )
    
    if per_page < 1 or per_page > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Per_page parameter must be between 1 and 100"
        )
    
    skip = (page - 1) * per_page
    return skip, per_page


# Common validation dependencies
def validate_object_id(object_id: str) -> str:
    """
    Dependency untuk validasi MongoDB ObjectId
    
    Args:
        object_id: String representation of ObjectId
        
    Returns:
        Validated ObjectId string
        
    Raises:
        HTTPException: Jika ObjectId tidak valid
    """
    from bson import ObjectId
    from bson.errors import InvalidId
    
    try:
        ObjectId(object_id)
        return object_id
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid ObjectId format: {object_id}"
        )


def validate_user_id(user_id: str = Depends(validate_object_id)) -> str:
    """Dependency untuk validasi user ID"""
    return user_id


def validate_category_id(category_id: str = Depends(validate_object_id)) -> str:
    """Dependency untuk validasi category ID"""
    return category_id


def validate_transaction_id(transaction_id: str = Depends(validate_object_id)) -> str:
    """Dependency untuk validasi transaction ID"""
    return transaction_id


def validate_target_id(target_id: str = Depends(validate_object_id)) -> str:
    """Dependency untuk validasi savings target ID"""
    return target_id


def validate_university_id(university_id: str = Depends(validate_object_id)) -> str:
    """Dependency untuk validasi university ID"""
    return university_id


def validate_faculty_id(faculty_id: str = Depends(validate_object_id)) -> str:
    """Dependency untuk validasi faculty ID"""
    return faculty_id


def validate_department_id(department_id: str = Depends(validate_object_id)) -> str:
    """Dependency untuk validasi department ID"""
    return department_id


# Search and filter dependencies
def get_search_params(
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> dict:
    """
    Dependency untuk search dan sorting parameters
    
    Args:
        search: Search term
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        Dictionary containing search parameters
        
    Raises:
        HTTPException: Jika parameter tidak valid
    """
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Sort order must be 'asc' or 'desc'"
        )
    
    # Convert sort_order to MongoDB format
    sort_order_int = 1 if sort_order == "asc" else -1
    
    return {
        "search": search.strip() if search else None,
        "sort_by": sort_by,
        "sort_order": sort_order_int
    }


# Future Authentication Dependencies (untuk implementasi nanti)
# Ini adalah placeholder untuk authentication system yang akan diimplementasi

class CurrentUser:
    """Placeholder class untuk current user"""
    def __init__(self, user_id: str, email: str, role: str, is_verified: bool = True):
        self.id = user_id
        self.email = email
        self.role = role
        self.is_verified = is_verified
        self.is_admin = role == "admin"
        self.is_student = role == "student"


async def get_current_user() -> CurrentUser:
    """
    Placeholder dependency untuk getting current authenticated user
    Akan diimplementasi nanti dengan JWT token validation
    
    Returns:
        Current user instance
        
    Raises:
        HTTPException: Jika authentication gagal
    """
    # TODO: Implement JWT token validation
    # For now, return a mock user for development
    
    # In real implementation:
    # 1. Extract JWT token from Authorization header
    # 2. Validate and decode token
    # 3. Get user from database
    # 4. Check if user is active and verified
    # 5. Return user instance
    
    # Mock user untuk development
    return CurrentUser(
        user_id="507f1f77bcf86cd799439011",  # Sample ObjectId
        email="student@ui.ac.id",
        role="student"
    )


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency untuk getting current active user
    
    Args:
        current_user: Current user dari get_current_user
        
    Returns:
        Active user instance
        
    Raises:
        HTTPException: Jika user tidak aktif atau tidak verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User email not verified"
        )
    
    # TODO: Add additional checks like user status, etc.
    
    return current_user


async def get_current_admin_user(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> CurrentUser:
    """
    Dependency untuk admin-only endpoints
    
    Args:
        current_user: Current active user
        
    Returns:
        Admin user instance
        
    Raises:
        HTTPException: Jika user bukan admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


async def get_current_student_user(
    current_user: CurrentUser = Depends(get_current_active_user)
) -> CurrentUser:
    """
    Dependency untuk student-only endpoints
    
    Args:
        current_user: Current active user
        
    Returns:
        Student user instance
        
    Raises:
        HTTPException: Jika user bukan student
    """
    if not current_user.is_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    
    return current_user


# Resource ownership dependencies
async def verify_user_ownership(
    resource_user_id: str,
    current_user: CurrentUser = Depends(get_current_active_user)
) -> bool:
    """
    Dependency untuk verifikasi ownership resource
    
    Args:
        resource_user_id: User ID yang memiliki resource
        current_user: Current user
        
    Returns:
        True jika user memiliki akses
        
    Raises:
        HTTPException: Jika user tidak memiliki akses
    """
    # Admin dapat akses semua resource
    if current_user.is_admin:
        return True
    
    # User hanya bisa akses resource miliknya sendiri
    if current_user.id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources"
        )
    
    return True


# Health check dependency
async def verify_database_connection() -> bool:
    """
    Dependency untuk verifikasi koneksi database
    
    Returns:
        True jika database terhubung
        
    Raises:
        HTTPException: Jika database tidak terhubung
    """
    try:
        is_connected = await database.ping_db()
        if not is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection failed"
            )
        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database health check failed: {str(e)}"
        )


# File upload dependencies
def validate_file_upload(
    max_size: int = 5 * 1024 * 1024,  # 5MB default
    allowed_types: list = None
):
    """
    Factory function untuk file upload validation dependency
    
    Args:
        max_size: Maximum file size in bytes
        allowed_types: List of allowed MIME types
        
    Returns:
        Dependency function
    """
    if allowed_types is None:
        allowed_types = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
    
    def _validate_file_upload(file):
        """Internal validation function"""
        if file.size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {max_size} bytes"
            )
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"File type {file.content_type} not allowed. Allowed types: {allowed_types}"
            )
        
        return file
    
    return _validate_file_upload


# Rate limiting helper (will be used with slowapi)
def get_client_ip(request) -> str:
    """
    Get client IP address for rate limiting
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check for forwarded headers (if behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"