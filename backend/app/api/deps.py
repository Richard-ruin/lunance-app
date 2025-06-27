# app/api/deps.py
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.models.student import Student
from app.api.v1.students.crud import student_crud
from app.api.v1.auth.utils import auth_utils
from app.core.exceptions import (
    AuthenticationException, AccountNotVerifiedException,
    AccountInactiveException, UserNotFoundException,
    AccountLockedException, RateLimitExceededException
)
from app.core.security import get_client_ip, create_rate_limit_key
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Security scheme for extracting Bearer tokens
security = HTTPBearer(auto_error=False)

# Rate limiting storage (in production, use Redis)
rate_limit_storage: Dict[str, Dict[str, Any]] = {}


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database connection"""
    from app.config.database import get_database as get_db
    return get_db()


# Alias for backward compatibility
async def get_db() -> AsyncIOMotorDatabase:
    """Dependency to get database connection (alias)"""
    return await get_database()


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Student]:
    """
    Get current user from JWT token (optional - returns None if no token)
    Used for endpoints that work both with and without authentication
    """
    if not credentials:
        return None
    
    try:
        # Extract user info from token
        user_info = auth_utils.extract_user_from_token(credentials.credentials)
        
        # Get full user data from database
        student = await student_crud.get_student_by_email(user_info["email"])
        
        if not student:
            return None
        
        # Check if account is active
        if not student.is_active:
            return None
        
        return student
        
    except Exception as e:
        logger.warning(f"Failed to authenticate optional user: {str(e)}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Student:
    """
    Get current user from JWT token (required)
    Raises HTTPException if authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Extract user info from token
        user_info = auth_utils.extract_user_from_token(credentials.credentials)
        
        # Get full user data from database
        student = await student_crud.get_student_by_email(user_info["email"])
        
        if not student:
            raise UserNotFoundException(user_info["email"])
        
        # Check if account is active
        if not student.is_active:
            raise AccountInactiveException()
        
        # Check if account is locked
        if hasattr(student, 'is_account_locked') and student.is_account_locked():
            lockout_until = student.account_locked_until.strftime("%Y-%m-%d %H:%M:%S")
            raise AccountLockedException(lockout_until)
        
        return student
        
    except (UserNotFoundException, AccountInactiveException, AccountLockedException):
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Alias for transaction endpoints
async def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get current student as dict (for transaction endpoints compatibility)
    """
    student = await get_current_user(credentials)
    
    # Convert Student model to dict format expected by transaction routes
    return {
        "_id": str(student.id),
        "email": student.email,
        "full_name": student.profile.full_name,
        "university": student.profile.university,
        "is_active": student.is_active
    }


async def get_verified_user(current_user: Student = Depends(get_current_user)) -> Student:
    """
    Get current user and ensure email is verified
    """
    if not current_user.verification.email_verified:
        raise AccountNotVerifiedException()
    
    return current_user


async def get_admin_user(current_user: Student = Depends(get_verified_user)) -> Student:
    """
    Get current user and ensure they have admin privileges
    """
    # Check if user has admin role or is from specific universities
    admin_universities = ["Universitas Indonesia", "Institut Teknologi Bandung"]
    
    # Check if user has admin role (if implemented)
    if hasattr(current_user, 'role') and current_user.role == "admin":
        return current_user
    
    # Fallback: check university-based admin access
    if current_user.profile.university not in admin_universities:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return current_user


async def check_rate_limit(
    request: Request,
    action: str = "general",
    max_requests: int = None,
    window_minutes: int = 1
) -> None:
    """
    Rate limiting dependency
    """
    if max_requests is None:
        max_requests = getattr(settings, 'RATE_LIMIT_PER_MINUTE', 60)
    
    # Get client identifier (IP + User-Agent for better uniqueness)
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "")
    client_id = f"{client_ip}:{hash(user_agent)}"
    
    # Create rate limit key
    rate_key = create_rate_limit_key(client_id, action)
    
    # Get current time in minutes
    import time
    current_window = int(time.time() // (window_minutes * 60))
    
    # Initialize or clean old data
    if rate_key not in rate_limit_storage:
        rate_limit_storage[rate_key] = {"window": current_window, "count": 0}
    elif rate_limit_storage[rate_key]["window"] < current_window:
        rate_limit_storage[rate_key] = {"window": current_window, "count": 0}
    
    # Check and increment counter
    rate_limit_storage[rate_key]["count"] += 1
    
    if rate_limit_storage[rate_key]["count"] > max_requests:
        retry_after = (window_minutes * 60) - (int(time.time()) % (window_minutes * 60))
        raise RateLimitExceededException(retry_after)


async def check_auth_rate_limit(request: Request) -> None:
    """Rate limiting specifically for auth endpoints"""
    await check_rate_limit(
        request,
        action="auth",
        max_requests=10,  # More restrictive for auth
        window_minutes=5
    )


async def check_otp_rate_limit(request: Request) -> None:
    """Rate limiting specifically for OTP endpoints"""
    await check_rate_limit(
        request,
        action="otp",
        max_requests=5,   # Very restrictive for OTP
        window_minutes=10
    )


async def check_upload_rate_limit(request: Request) -> None:
    """Rate limiting specifically for file upload endpoints"""
    await check_rate_limit(
        request,
        action="upload",
        max_requests=20,  # Moderate restriction for uploads
        window_minutes=5
    )


def get_pagination_params(
    page: int = 1,
    size: int = 10,
    max_size: int = 100
) -> Dict[str, int]:
    """
    Pagination parameters dependency
    """
    if page < 1:
        page = 1
    if size < 1:
        size = 10
    if size > max_size:
        size = max_size
    
    skip = (page - 1) * size
    
    return {
        "skip": skip,
        "limit": size,
        "page": page,
        "size": size
    }


def get_search_params(
    q: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Search parameters dependency
    """
    # Validate sort order
    if sort_order.lower() not in ["asc", "desc"]:
        sort_order = "desc"
    
    # Clean search query
    if q:
        q = q.strip()
        if len(q) < 2:
            q = None
    
    return {
        "query": q,
        "sort_by": sort_by,
        "sort_order": sort_order
    }


async def validate_student_access(
    student_id: str,
    current_user: Student = Depends(get_verified_user)
) -> Student:
    """
    Validate that current user can access specific student data
    Returns the target student if access is allowed
    """
    # Users can always access their own data
    if str(current_user.id) == student_id:
        return current_user
    
    # For accessing other students' data, implement friendship/privacy rules
    target_student = await student_crud.get_student_by_id(student_id)
    if not target_student:
        raise UserNotFoundException(student_id)
    
    # Check privacy settings
    if not target_student.settings.privacy.show_in_leaderboard:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has disabled public profile access"
        )
    
    # Additional checks can be added here (e.g., friendship status)
    
    return target_student


class CommonQueryParams:
    """Common query parameters for list endpoints"""
    
    def __init__(
        self,
        page: int = 1,
        size: int = 10,
        q: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        include_inactive: bool = False
    ):
        self.page = max(1, page)
        self.size = max(1, min(100, size))
        self.skip = (self.page - 1) * self.size
        self.query = q.strip() if q else None
        self.sort_by = sort_by
        self.sort_order = sort_order if sort_order.lower() in ["asc", "desc"] else "desc"
        self.include_inactive = include_inactive


# Dependency for common query parameters
def get_common_query_params(
    page: int = 1,
    size: int = 10,
    q: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    include_inactive: bool = False
) -> CommonQueryParams:
    return CommonQueryParams(
        page=page,
        size=size,
        q=q,
        sort_by=sort_by,
        sort_order=sort_order,
        include_inactive=include_inactive
    )


# Utility function to check user permissions for specific operations
async def check_operation_permission(
    operation: str,
    current_user: Student,
    target_user: Optional[Student] = None
) -> bool:
    """
    Check if user has permission for specific operation
    """
    # Operations users can always do on their own account
    self_operations = [
        "read_profile", "update_profile", "delete_account",
        "read_transactions", "create_transaction", "update_transaction", "delete_transaction",
        "read_savings", "create_savings", "update_savings",
        "read_history", "export_data"
    ]
    
    # Operations that require verified account
    verified_operations = [
        "create_transaction", "update_transaction", "delete_transaction",
        "create_savings_goal", "join_expense_split", "create_expense_split",
        "upload_receipt", "bulk_delete_transactions"
    ]
    
    # Check if operation requires verification
    if operation in verified_operations and not current_user.verification.email_verified:
        return False
    
    # Check if operation is on self
    if target_user is None or str(current_user.id) == str(target_user.id):
        return operation in self_operations
    
    # Operations users can do on other users' data (with privacy checks)
    public_operations = ["read_profile", "read_public_transactions"]
    
    if operation in public_operations:
        # Check target user's privacy settings
        if operation == "read_profile":
            return target_user.settings.privacy.show_in_leaderboard
        elif operation == "read_public_transactions":
            return target_user.settings.privacy.show_in_leaderboard
    
    return False


# Helper function to get user context for logging/analytics
def get_user_context(current_user: Optional[Student] = None) -> Dict[str, Any]:
    """Get user context for logging and analytics"""
    if not current_user:
        return {"user_id": None, "anonymous": True}
    
    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "university": current_user.profile.university,
        "verified": current_user.verification.email_verified,
        "level": current_user.gamification.level,
        "anonymous": False
    }


# Transaction-specific dependencies
async def validate_transaction_owner(
    transaction_id: str,
    current_user: Student = Depends(get_current_user)
) -> str:
    """
    Validate that current user owns the transaction
    Returns transaction_id if valid
    """
    # This will be used in transaction update/delete endpoints
    # The actual validation is done in the CRUD layer
    return transaction_id


async def validate_bulk_transaction_access(
    transaction_ids: list,
    current_user: Student = Depends(get_current_user)
) -> list:
    """
    Validate that current user owns all transactions in bulk operation
    """
    # This will be used in bulk delete endpoints
    # The actual validation is done in the CRUD layer
    return transaction_ids


# Category-specific dependencies
async def validate_category_access(
    category_id: str,
    current_user: Student = Depends(get_current_user)
) -> str:
    """
    Validate that current user can access the category
    """
    # Categories are usually global or user-specific
    # The actual validation is done in the CRUD layer
    return category_id


# File upload dependencies
async def validate_file_upload(
    current_user: Student = Depends(get_verified_user),
    request: Request = None
) -> Student:
    """
    Validate user can upload files (must be verified)
    """
    if request:
        await check_upload_rate_limit(request)
    
    return current_user


# Achievement and gamification dependencies
async def check_achievement_trigger(
    action: str,
    current_user: Student = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check if action should trigger achievement
    Returns context for achievement processing
    """
    return {
        "user": current_user,
        "action": action,
        "timestamp": logger.info(f"Achievement trigger: {action} for user {current_user.email}")
    }


# Analytics dependencies
def get_analytics_params(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    granularity: str = "daily",
    include_metadata: bool = False
) -> Dict[str, Any]:
    """
    Parameters for analytics endpoints
    """
    from datetime import datetime, timedelta
    
    # Default date range (last 30 days)
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=30)).date()
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    
    if not end_date:
        end_date = datetime.utcnow().date()
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    # Validate granularity
    valid_granularities = ["hourly", "daily", "weekly", "monthly"]
    if granularity not in valid_granularities:
        granularity = "daily"
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "granularity": granularity,
        "include_metadata": include_metadata
    }


# Export dependencies
def get_export_params(
    format: str = "csv",
    include_metadata: bool = False,
    date_range: Optional[str] = None
) -> Dict[str, Any]:
    """
    Parameters for data export endpoints
    """
    # Validate export format
    valid_formats = ["csv", "excel", "json", "pdf"]
    if format not in valid_formats:
        format = "csv"
    
    return {
        "format": format,
        "include_metadata": include_metadata,
        "date_range": date_range
    }


# Budget and savings dependencies
async def validate_budget_access(
    budget_id: str,
    current_user: Student = Depends(get_verified_user)
) -> str:
    """
    Validate that current user can access the budget
    """
    return budget_id


async def validate_savings_goal_access(
    goal_id: str,
    current_user: Student = Depends(get_verified_user)
) -> str:
    """
    Validate that current user can access the savings goal
    """
    return goal_id


# University-specific dependencies
def validate_university_info(
    university: str,
    faculty: Optional[str] = None,
    major: Optional[str] = None
) -> Dict[str, str]:
    """
    Validate university information format
    """
    # Basic validation - more comprehensive validation in business logic
    if not university or len(university.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="University name is required and must be at least 3 characters"
        )
    
    return {
        "university": university.strip(),
        "faculty": faculty.strip() if faculty else None,
        "major": major.strip() if major else None
    }