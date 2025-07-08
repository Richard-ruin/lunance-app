# app/api/v1/endpoints/auth.py
"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from typing import Dict, Any
import logging

from app.models.auth import (
    RegisterRequest, LoginRequest, LoginResponse, TokenResponse,
    PasswordResetRequest, PasswordResetConfirm, ChangePasswordRequest,
    EmailVerificationRequest, EmailVerificationConfirm, RefreshTokenRequest,
    LogoutRequest, AuthResponse
)
from app.models.user import UserResponse, UserInDB
from app.services.auth_service import AuthService, AuthenticationError
from app.middleware.auth import (
    get_current_user, get_current_verified_user, rate_limit_dependency,
    security, token_blacklist
)
from app.utils.otp import resend_otp_allowed
from app.models.otp_verification import OTPType

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(),
    _: None = Depends(rate_limit_dependency)
):
    """
    Register new user account.
    
    Requires prior OTP verification sent to email.
    """
    try:
        result = await auth_service.register_user(register_data)
        
        return AuthResponse(
            success=True,
            message=result["message"],
            data={
                "user_id": result["user_id"],
                "tokens": result["tokens"]
            }
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/send-registration-otp", response_model=AuthResponse)
async def send_registration_otp(
    request: EmailVerificationRequest,
    auth_service: AuthService = Depends(),
    _: None = Depends(rate_limit_dependency)
):
    """
    Send OTP code for user registration.
    
    Email must be from academic domain (.ac.id).
    """
    try:
        # Check resend limits
        resend_check = await resend_otp_allowed(request.email, OTPType.REGISTER)
        if not resend_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=resend_check["message"]
            )
        
        result = await auth_service.send_registration_otp(request.email)
        
        return AuthResponse(
            success=True,
            message=result["message"],
            data={
                "expires_in_seconds": result["expires_in_seconds"]
            }
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send registration OTP error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send registration OTP"
        )


@router.post("/login", response_model=LoginResponse)
async def login_user(
    login_data: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(),
    _: None = Depends(rate_limit_dependency)
):
    """
    Authenticate user and return access tokens.
    """
    try:
        result = await auth_service.login_user(login_data)
        
        # Log successful login
        logger.info(f"Successful login for: {login_data.email} from IP: {request.client.host}")
        
        return result
        
    except AuthenticationError as e:
        # Log failed login attempt
        logger.warning(f"Failed login attempt for: {login_data.email} from IP: {request.client.host}")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(),
    _: None = Depends(rate_limit_dependency)
):
    """
    Refresh access token using valid refresh token.
    """
    try:
        # Check if token is blacklisted
        if token_blacklist.is_blacklisted(refresh_data.refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        tokens = await auth_service.refresh_token(refresh_data.refresh_token)
        
        return tokens
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout", response_model=AuthResponse)
async def logout_user(
    logout_data: LogoutRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Logout user and invalidate tokens.
    """
    try:
        # Add current access token to blacklist
        if credentials:
            token_blacklist.add_token(credentials.credentials)
        
        # Add refresh token to blacklist if provided
        if logout_data.refresh_token:
            token_blacklist.add_token(logout_data.refresh_token)
        
        logger.info(f"User logged out: {current_user.email}")
        
        return AuthResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(
    reset_data: PasswordResetRequest,
    auth_service: AuthService = Depends(),
    _: None = Depends(rate_limit_dependency)
):
    """
    Send password reset OTP to user email.
    
    Returns success message regardless of whether email exists for security.
    """
    try:
        # Check resend limits
        resend_check = await resend_otp_allowed(reset_data.email, OTPType.RESET_PASSWORD)
        if not resend_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=resend_check["message"]
            )
        
        result = await auth_service.send_password_reset_otp(reset_data)
        
        return AuthResponse(
            success=True,
            message=result["message"],
            data={
                "expires_in_seconds": result["expires_in_seconds"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        # Return generic success message for security
        return AuthResponse(
            success=True,
            message="If this email exists, a password reset code has been sent",
            data={
                "expires_in_seconds": 300
            }
        )


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    auth_service: AuthService = Depends(),
    _: None = Depends(rate_limit_dependency)
):
    """
    Reset user password using OTP verification.
    """
    try:
        result = await auth_service.reset_password(reset_data)
        
        return AuthResponse(
            success=True,
            message=result["message"]
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/change-password", response_model=AuthResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: UserInDB = Depends(get_current_verified_user)
):
    """
    Change user password (requires authentication).
    """
    try:
        auth_service = AuthService()
        result = await auth_service.change_password(
            user_id=str(current_user.id),
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        return AuthResponse(
            success=True,
            message=result["message"]
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/send-email-verification", response_model=AuthResponse)
async def send_email_verification(
    current_user: UserInDB = Depends(get_current_user),
    _: None = Depends(rate_limit_dependency)
):
    """
    Send email verification OTP to current user.
    """
    try:
        # Check resend limits
        resend_check = await resend_otp_allowed(current_user.email, OTPType.EMAIL_VERIFICATION)
        if not resend_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=resend_check["message"]
            )
        
        auth_service = AuthService()
        result = await auth_service.send_email_verification_otp(current_user.email)
        
        return AuthResponse(
            success=True,
            message=result["message"],
            data={
                "expires_in_seconds": result.get("expires_in_seconds")
            }
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email verification"
        )


@router.post("/verify-email", response_model=AuthResponse)
async def verify_email(
    verification_data: EmailVerificationConfirm,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Verify user email using OTP code.
    """
    try:
        # Ensure user is verifying their own email
        if current_user.email != verification_data.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot verify email for another user"
            )
        
        auth_service = AuthService()
        result = await auth_service.verify_user_email(
            email=verification_data.email,
            otp_code=verification_data.otp_code
        )
        
        return AuthResponse(
            success=True,
            message=result["message"]
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    try:
        return UserResponse(
            id=str(current_user.id),
            email=current_user.email,
            full_name=current_user.full_name,
            phone_number=current_user.phone_number,
            university_id=current_user.university_id,
            faculty_id=current_user.faculty_id,
            major_id=current_user.major_id,
            role=current_user.role,
            initial_savings=current_user.initial_savings,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )
        
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.post("/validate-token", response_model=AuthResponse)
async def validate_token(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Validate current authentication token.
    """
    try:
        return AuthResponse(
            success=True,
            message="Token is valid",
            data={
                "user_id": str(current_user.id),
                "email": current_user.email,
                "role": current_user.role.value,
                "is_verified": current_user.is_verified
            }
        )
        
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token validation failed"
        )


# Background task for cleanup
async def cleanup_expired_tokens():
    """Background task to clean up expired tokens and OTPs."""
    try:
        from ...utils.otp import cleanup_expired_otps
        
        # Clean up expired OTPs
        deleted_otps = await cleanup_expired_otps()
        if deleted_otps > 0:
            logger.info(f"Cleaned up {deleted_otps} expired OTPs")
        
        # Note: In production, you'd want to use Redis or database
        # for token blacklist instead of in-memory storage
        
    except Exception as e:
        logger.error(f"Cleanup task error: {e}")


@router.post("/admin/cleanup", response_model=AuthResponse)
async def admin_cleanup(
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Admin endpoint to trigger cleanup tasks.
    """
    try:
        # Check admin permissions
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Add cleanup task to background
        background_tasks.add_task(cleanup_expired_tokens)
        
        return AuthResponse(
            success=True,
            message="Cleanup task scheduled"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin cleanup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cleanup task failed"
        )