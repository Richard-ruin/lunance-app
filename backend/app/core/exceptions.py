"""
Custom Exceptions
Exception classes untuk handling error dengan baik
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class LunanceException(Exception):
    """Base exception untuk Lunance application"""
    
    def __init__(
        self,
        message: str = "An error occurred",
        details: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        self.message = message
        self.details = details or {}
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(LunanceException):
    """Exception untuk validation errors"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details, "VALIDATION_ERROR")
        self.field = field


class NotFoundError(LunanceException):
    """Exception untuk resource not found"""
    
    def __init__(
        self,
        resource: str = "Resource",
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource} not found"
        if resource_id:
            message += f" with ID: {resource_id}"
        
        super().__init__(message, details, "NOT_FOUND")
        self.resource = resource
        self.resource_id = resource_id


class PermissionError(LunanceException):
    """Exception untuk permission denied"""
    
    def __init__(
        self,
        message: str = "Permission denied",
        required_permission: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details, "PERMISSION_DENIED")
        self.required_permission = required_permission


class AuthenticationError(LunanceException):
    """Exception untuk authentication errors"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details, "AUTHENTICATION_ERROR")


class BusinessLogicError(LunanceException):
    """Exception untuk business logic violations"""
    
    def __init__(
        self,
        message: str = "Business logic violation",
        rule: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details, "BUSINESS_LOGIC_ERROR")
        self.rule = rule


class DatabaseError(LunanceException):
    """Exception untuk database errors"""
    
    def __init__(
        self,
        message: str = "Database error occurred",
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details, "DATABASE_ERROR")
        self.operation = operation


class ExternalServiceError(LunanceException):
    """Exception untuk external service errors"""
    
    def __init__(
        self,
        service: str,
        message: str = "External service error",
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details, "EXTERNAL_SERVICE_ERROR")
        self.service = service
        self.status_code = status_code


class RateLimitError(LunanceException):
    """Exception untuk rate limiting"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details, "RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after


class FileUploadError(LunanceException):
    """Exception untuk file upload errors"""
    
    def __init__(
        self,
        message: str = "File upload failed",
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details, "FILE_UPLOAD_ERROR")
        self.filename = filename
        self.file_size = file_size


# HTTP Exception Mappers
def map_exception_to_http(exc: LunanceException) -> HTTPException:
    """
    Map custom exceptions ke HTTP exceptions
    
    Args:
        exc: Custom exception
        
    Returns:
        HTTPException dengan status code dan detail yang sesuai
    """
    status_code_map = {
        ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        NotFoundError: status.HTTP_404_NOT_FOUND,
        PermissionError: status.HTTP_403_FORBIDDEN,
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        BusinessLogicError: status.HTTP_400_BAD_REQUEST,
        DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ExternalServiceError: status.HTTP_503_SERVICE_UNAVAILABLE,
        RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
        FileUploadError: status.HTTP_400_BAD_REQUEST,
    }
    
    status_code = status_code_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    detail = {
        "success": False,
        "message": exc.message,
        "error_code": exc.error_code,
        "details": exc.details
    }
    
    # Add specific headers untuk rate limiting
    headers = {}
    if isinstance(exc, RateLimitError) and exc.retry_after:
        headers["Retry-After"] = str(exc.retry_after)
    
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers if headers else None
    )


# Specific Domain Exceptions
class UserNotFoundError(NotFoundError):
    """Exception untuk user not found"""
    
    def __init__(self, user_id: Optional[str] = None, email: Optional[str] = None):
        identifier = user_id or email or "unknown"
        super().__init__("User", identifier)


class UniversityNotFoundError(NotFoundError):
    """Exception untuk university not found"""
    
    def __init__(self, university_id: Optional[str] = None, domain: Optional[str] = None):
        identifier = university_id or domain or "unknown"
        super().__init__("University", identifier)


class CategoryNotFoundError(NotFoundError):
    """Exception untuk category not found"""
    
    def __init__(self, category_id: str):
        super().__init__("Category", category_id)


class TransactionNotFoundError(NotFoundError):
    """Exception untuk transaction not found"""
    
    def __init__(self, transaction_id: str):
        super().__init__("Transaction", transaction_id)


class SavingsTargetNotFoundError(NotFoundError):
    """Exception untuk savings target not found"""
    
    def __init__(self, target_id: str):
        super().__init__("Savings Target", target_id)


class EmailAlreadyExistsError(ValidationError):
    """Exception untuk email already exists"""
    
    def __init__(self, email: str):
        super().__init__(
            message=f"Email {email} sudah terdaftar",
            field="email",
            details={"email": email}
        )


class DomainAlreadyExistsError(ValidationError):
    """Exception untuk domain already exists"""
    
    def __init__(self, domain: str):
        super().__init__(
            message=f"Domain {domain} sudah terdaftar",
            field="domain",
            details={"domain": domain}
        )


class CategoryNameExistsError(ValidationError):
    """Exception untuk category name already exists"""
    
    def __init__(self, name: str, scope: str = "personal"):
        super().__init__(
            message=f"Kategori {scope} '{name}' sudah ada",
            field="name",
            details={"name": name, "scope": scope}
        )


class InsufficientPermissionError(PermissionError):
    """Exception untuk insufficient permission"""
    
    def __init__(self, action: str, resource: str):
        super().__init__(
            message=f"Tidak memiliki permission untuk {action} {resource}",
            details={"action": action, "resource": resource}
        )


class UniversityNotApprovedError(BusinessLogicError):
    """Exception untuk university not approved"""
    
    def __init__(self, university_name: str):
        super().__init__(
            message=f"Universitas {university_name} belum disetujui",
            rule="university_approval_required",
            details={"university_name": university_name}
        )


class InvalidTransactionCategoryError(BusinessLogicError):
    """Exception untuk invalid transaction category"""
    
    def __init__(self, transaction_type: str, category_type: str):
        super().__init__(
            message=f"Kategori {category_type} tidak sesuai untuk transaksi {transaction_type}",
            rule="transaction_category_consistency",
            details={
                "transaction_type": transaction_type,
                "category_type": category_type
            }
        )


class SavingsTargetCompletedError(BusinessLogicError):
    """Exception untuk operations pada completed savings target"""
    
    def __init__(self, target_name: str):
        super().__init__(
            message=f"Target '{target_name}' sudah tercapai dan tidak bisa dimodifikasi",
            rule="completed_target_immutable",
            details={"target_name": target_name}
        )


class InsufficientSavingsError(BusinessLogicError):
    """Exception untuk insufficient savings"""
    
    def __init__(self, requested: float, available: float):
        super().__init__(
            message=f"Saldo tidak mencukupi. Diminta: {requested}, Tersedia: {available}",
            rule="sufficient_savings_required",
            details={
                "requested_amount": requested,
                "available_amount": available
            }
        )


# Utility functions untuk error handling
def create_validation_error_from_pydantic(exc) -> ValidationError:
    """Create ValidationError dari Pydantic validation error"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append({"field": field, "message": message})
    
    return ValidationError(
        message="Input validation failed",
        details={"validation_errors": errors}
    )


def create_database_error(operation: str, original_error: Exception) -> DatabaseError:
    """Create DatabaseError dari original database error"""
    return DatabaseError(
        message=f"Database {operation} failed",
        operation=operation,
        details={
            "original_error": str(original_error),
            "error_type": type(original_error).__name__
        }
    )