# app/utils/exceptions.py (fixed)
from fastapi import HTTPException
from typing import Optional, Any, Dict

class CustomHTTPException(HTTPException):
    """Custom HTTP exception with Indonesian error messages"""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code

class ValidationException(CustomHTTPException):
    """Validation error exception"""
    
    def __init__(self, detail: str, field: str = None):
        super().__init__(
            status_code=422,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )
        self.field = field

class AuthenticationException(CustomHTTPException):
    """Authentication error exception"""
    
    def __init__(self, detail: str = "Kredensial tidak valid"):
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="AUTHENTICATION_ERROR"
        )

class AuthorizationException(CustomHTTPException):
    """Authorization error exception"""
    
    def __init__(self, detail: str = "Akses ditolak"):
        super().__init__(
            status_code=403,
            detail=detail,
            error_code="AUTHORIZATION_ERROR"
        )

class NotFoundException(CustomHTTPException):
    """Resource not found exception - ADDED THIS"""
    
    def __init__(self, detail: str = "Sumber daya tidak ditemukan"):
        super().__init__(
            status_code=404,
            detail=detail,
            error_code="RESOURCE_NOT_FOUND"
        )

# Alias for backward compatibility
ResourceNotFoundException = NotFoundException

class BusinessLogicException(CustomHTTPException):
    """Business logic error exception"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code="BUSINESS_LOGIC_ERROR"
        )

class DatabaseException(CustomHTTPException):
    """Database error exception"""
    
    def __init__(self, detail: str = "Terjadi kesalahan pada database"):
        super().__init__(
            status_code=500,
            detail=detail,
            error_code="DATABASE_ERROR"
        )

class EmailServiceException(CustomHTTPException):
    """Email service error exception"""
    
    def __init__(self, detail: str = "Gagal mengirim email"):
        super().__init__(
            status_code=500,
            detail=detail,
            error_code="EMAIL_SERVICE_ERROR"
        )

class FileUploadException(CustomHTTPException):
    """File upload error exception"""
    
    def __init__(self, detail: str = "Gagal mengupload file"):
        super().__init__(
            status_code=400,
            detail=detail,
            error_code="FILE_UPLOAD_ERROR"
        )