from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class LunanceException(Exception):
    """Base exception for Lunance application"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# Authentication & Authorization Exceptions
class AuthenticationException(LunanceException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationException(LunanceException):
    """Raised when user doesn't have permission"""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class InvalidCredentialsException(AuthenticationException):
    """Raised when login credentials are invalid"""
    
    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message="Invalid email or password",
            details=details
        )

class AccountNotVerifiedException(AuthenticationException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email belum diverifikasi. Silakan verifikasi email terlebih dahulu.",
            headers={"X-Error-Code": "EMAIL_NOT_VERIFIED"}
        )


class AccountLockedException(AuthenticationException):
    """Raised when account is locked due to failed attempts"""
    
    def __init__(self, lockout_until: str, details: Optional[Dict[str, Any]] = None):
        message = f"Account locked due to too many failed attempts. Try again after {lockout_until}"
        super().__init__(
            message=message,
            details=details
        )


class TokenExpiredException(AuthenticationException):
    """Raised when JWT token has expired"""
    
    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message="Token has expired",
            details=details
        )


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid"""
    
    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message="Invalid token",
            details=details
        )


# User & Account Exceptions
class UserNotFoundException(LunanceException):
    """Raised when user is not found"""
    
    def __init__(self, identifier: str = "", details: Optional[Dict[str, Any]] = None):
        message = f"User not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class UserAlreadyExistsException(LunanceException):
    """Raised when trying to create user that already exists"""
    
    def __init__(self, email: str = "", details: Optional[Dict[str, Any]] = None):
        message = "User already exists"
        if email:
            message += f" with email: {email}"
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class AccountNotVerifiedException(AuthenticationException):
    """Raised when account email is not verified"""
    
    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message="Account email not verified. Please check your email for verification link.",
            details=details
        )


class AccountInactiveException(AuthenticationException):
    """Raised when account is inactive"""
    
    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message="Account is inactive. Please contact support.",
            details=details
        )


# OTP Exceptions
class OTPException(LunanceException):
    """Base class for OTP-related exceptions"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class InvalidOTPException(OTPException):
    """Raised when OTP code is invalid"""
    
    def __init__(self, attempts_remaining: int = 0, details: Optional[Dict[str, Any]] = None):
        message = "Invalid OTP code"
        if attempts_remaining > 0:
            message += f". {attempts_remaining} attempts remaining"
        else:
            message += ". No attempts remaining"
        super().__init__(message=message, details=details)


class OTPExpiredException(OTPException):
    """Raised when OTP has expired"""
    
    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message="OTP code has expired. Please request a new one.",
            details=details
        )


class OTPNotSentException(OTPException):
    """Raised when OTP could not be sent"""
    
    def __init__(self, reason: str = "", details: Optional[Dict[str, Any]] = None):
        message = "Could not send OTP"
        if reason:
            message += f": {reason}"
        super().__init__(message=message, details=details)


class TooManyOTPAttemptsException(OTPException):
    """Raised when too many OTP attempts have been made"""
    
    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message="Too many OTP attempts. Please request a new OTP code.",
            details=details
        )


# Validation Exceptions
class ValidationException(LunanceException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: str = "", details: Optional[Dict[str, Any]] = None):
        self.field = field
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class WeakPasswordException(ValidationException):
    """Raised when password doesn't meet security requirements"""
    
    def __init__(self, errors: list, details: Optional[Dict[str, Any]] = None):
        message = "Password does not meet security requirements: " + "; ".join(errors)
        super().__init__(
            message=message,
            field="password",
            details=details
        )


class InvalidEmailFormatException(ValidationException):
    """Raised when email format is invalid"""
    
    def __init__(self, email: str = "", details: Optional[Dict[str, Any]] = None):
        message = "Invalid email format"
        if email:
            message += f": {email}"
        super().__init__(
            message=message,
            field="email",
            details=details
        )


class InvalidStudentEmailException(ValidationException):
    """Raised when email is not from academic institution"""
    
    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message="Email must be from an academic institution (.ac.id, .edu, etc.)",
            field="email",
            details=details
        )


# Database Exceptions
class DatabaseException(LunanceException):
    """Raised when database operation fails"""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class DuplicateRecordException(DatabaseException):
    """Raised when trying to create duplicate record"""
    
    def __init__(self, field: str = "", value: str = "", details: Optional[Dict[str, Any]] = None):
        message = "Record already exists"
        if field and value:
            message += f" with {field}: {value}"
        super().__init__(
            message=message,
            details=details
        )


# Business Logic Exceptions
class InsufficientBalanceException(LunanceException):
    """Raised when user has insufficient balance for operation"""
    
    def __init__(self, available: float = 0, required: float = 0, details: Optional[Dict[str, Any]] = None):
        message = f"Insufficient balance. Available: {available}, Required: {required}"
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class InvalidTransactionException(LunanceException):
    """Raised when transaction data is invalid"""
    
    def __init__(self, reason: str = "", details: Optional[Dict[str, Any]] = None):
        message = "Invalid transaction"
        if reason:
            message += f": {reason}"
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


# Rate Limiting Exceptions
class RateLimitExceededException(LunanceException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, retry_after: int = 60, details: Optional[Dict[str, Any]] = None):
        message = f"Rate limit exceeded. Try again in {retry_after} seconds"
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


# File Upload Exceptions
class FileUploadException(LunanceException):
    """Raised when file upload fails"""
    
    def __init__(self, reason: str = "", details: Optional[Dict[str, Any]] = None):
        message = "File upload failed"
        if reason:
            message += f": {reason}"
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class FileSizeExceededException(FileUploadException):
    """Raised when uploaded file is too large"""
    
    def __init__(self, max_size: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            reason=f"File size exceeds maximum allowed size of {max_size} bytes",
            details=details
        )


class UnsupportedFileTypeException(FileUploadException):
    """Raised when uploaded file type is not supported"""
    
    def __init__(self, file_type: str, allowed_types: list, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            reason=f"File type '{file_type}' not supported. Allowed types: {', '.join(allowed_types)}",
            details=details
        )


# External Service Exceptions
class EmailServiceException(LunanceException):
    """Raised when email service fails"""
    
    def __init__(self, reason: str = "", details: Optional[Dict[str, Any]] = None):
        message = "Email service error"
        if reason:
            message += f": {reason}"
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


class BankAPIException(LunanceException):
    """Raised when bank API integration fails"""
    
    def __init__(self, reason: str = "", details: Optional[Dict[str, Any]] = None):
        message = "Bank API error"
        if reason:
            message += f": {reason}"
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


# Utility function to convert exceptions to HTTP exceptions
def to_http_exception(exc: LunanceException) -> HTTPException:
    """Convert LunanceException to FastAPI HTTPException"""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "message": exc.message,
            "details": exc.details,
            "type": exc.__class__.__name__
        }
    )