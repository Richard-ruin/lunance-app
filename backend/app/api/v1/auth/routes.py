from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, validator

from app.models.student import (
    Student, StudentCreate, StudentResponse, 
    OTPRequest, OTPVerification, OTPResponse, OTPType,
    ForgotPasswordRequest, ResetPasswordRequest,
    VerificationStatusResponse
)
from app.api.v1.students.crud import student_crud
from app.api.v1.auth.utils import auth_utils, otp_service
from app.api.deps import (
    check_auth_rate_limit, check_otp_rate_limit, 
    get_current_user, get_current_user_optional
)
from app.core.security import (
    validate_password_strength, validate_student_email, 
    validate_phone_number
)
from app.core.exceptions import (
    UserAlreadyExistsException, InvalidCredentialsException,
    UserNotFoundException, WeakPasswordException,
    InvalidStudentEmailException, ValidationException,
    AccountLockedException, InvalidOTPException,
    OTPExpiredException, TooManyOTPAttemptsException,
    AccountNotVerifiedException, AccountNotVerifiedException
)
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: StudentResponse
    message: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError('; '.join(errors))
        return v

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    full_name: str
    university: str
    faculty: str
    major: str
    student_id: str
    semester: int
    graduation_year: int
    phone_number: str = None
    
    @validator('email')
    def validate_email_domain(cls, v):
        is_valid, message = validate_student_email(v)
        if not is_valid:
            raise ValueError(message)
        return v
    
    @validator('password')
    def validate_password(cls, v):
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError('; '.join(errors))
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v:
            is_valid, error = validate_phone_number(v)
            if not is_valid:
                raise ValueError(error)
        return v
    
    @validator('semester')
    def validate_semester(cls, v):
        if v < 1 or v > 14:
            raise ValueError('Semester must be between 1 and 14')
        return v
    
    @validator('graduation_year')
    def validate_graduation_year(cls, v):
        current_year = datetime.now().year
        if v < current_year or v > current_year + 8:
            raise ValueError(f'Graduation year must be between {current_year} and {current_year + 8}')
        return v

class RegisterResponse(BaseModel):
    message: str
    email: str
    verification_required: bool = True


@router.post("/register", response_model=RegisterResponse)
async def register_student(
    register_data: RegisterRequest,
    background_tasks: BackgroundTasks,
    request: Request = None,
    _: None = Depends(check_auth_rate_limit)
):
    """Register a new student account"""
    try:
        # Validate university (you can expand this with actual university validation)
        if register_data.university not in settings.SUPPORTED_UNIVERSITIES:
            # Allow registration but log for review
            logger.info(f"Registration from unsupported university: {register_data.university}")
        
        # Create student profile from registration data
        from app.models.student import Profile, AcademicInfo
        
        # Create academic info (with default values for now)
        academic_info = AcademicInfo(
            university=register_data.university,
            semester_start=datetime.now(),  # You can calculate based on current date
            semester_end=datetime.now() + timedelta(days=120),
            exam_periods=[],
            holiday_periods=[]
        )
        
        profile = Profile(
            full_name=register_data.full_name,
            phone_number=register_data.phone_number,
            university=register_data.university,
            faculty=register_data.faculty,
            major=register_data.major,
            student_id=register_data.student_id,
            semester=register_data.semester,
            graduation_year=register_data.graduation_year,
            academic_info=academic_info,
            monthly_allowance=0.0,
            income_sources=[],
            accommodation="kos",  # Default value
            transportation="public_transport",  # Default value
            savings_goals=[]
        )
        
        student_create = StudentCreate(
            email=register_data.email,
            password=register_data.password,
            profile=profile
        )
        
        # Create student in database
        student = await student_crud.create_student(student_create)
        
        # Generate and send OTP for email verification
        background_tasks.add_task(send_registration_otp, register_data.email)
        
        return RegisterResponse(
            message="Registration successful! Please check your email for verification code.",
            email=register_data.email,
            verification_required=True
        )
        
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/login", response_model=LoginResponse)
async def login_student(
    login_data: LoginRequest,
    request: Request = None,
    _: None = Depends(check_auth_rate_limit)
):
    """
    Authenticate student and return tokens with user data
    """
    try:
        # Authenticate student
        student = await student_crud.authenticate_student(
            login_data.email, 
            login_data.password
        )
        
        if not student:
            raise InvalidCredentialsException()
        
        # Check if account is active
        if not student.is_active:
            logger.warning(f"Inactive account login attempt: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akun Anda tidak aktif. Silakan hubungi admin."
            )
        
        # Check if account is locked
        if student.is_account_locked():
            logger.warning(f"Locked account login attempt: {login_data.email}")
            raise AccountLockedException()
        
        # Check email verification
        if not student.verification.email_verified:
            logger.warning(f"Unverified email login attempt: {login_data.email}")
            
            # Reset failed login attempts karena credentials benar
            if student.failed_login_attempts > 0:
                await student_crud.reset_failed_login_attempts(student.email)
            
            # Return specific error untuk email not verified
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "EMAIL_NOT_VERIFIED",
                    "message": "Email Anda belum diverifikasi. Silakan verifikasi email terlebih dahulu.",
                    "email": student.email,
                    "verification_required": True
                }
            )
        
        # Reset failed login attempts on successful authentication
        if student.failed_login_attempts > 0:
            await student_crud.reset_failed_login_attempts(student.email)
        
        # Update last login timestamp
        await student_crud.update_last_login(student.email)
        
        # Generate tokens
        tokens = auth_utils.create_tokens_for_student(student)
        
        # Create response dengan user data - INI YANG PENTING!
        student_response = StudentResponse(
            _id=str(student.id),  # Use _id as per model
            email=student.email,
            profile=student.profile,
            verification=student.verification,
            settings=student.settings,
            gamification=student.gamification,
            created_at=student.created_at,
            last_login=student.last_login,
            is_active=student.is_active
        )
        
        logger.info(f"Successful login: {login_data.email}")
        
        # RETURN FORMAT YANG BENAR - INCLUDE USER DATA
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "user": student_response.model_dump(by_alias=True),  # TAMBAH INI!
            "message": "Login berhasil"
        }
        
    except HTTPException:
        # Re-raise HTTPException as is
        raise
    except (
        InvalidCredentialsException, 
        AccountLockedException
    ) as e:
        # Increment failed login attempts for authentication failures
        if isinstance(e, InvalidCredentialsException):
            try:
                await student_crud.increment_failed_login_attempts(login_data.email)
            except:
                pass  # Don't fail login if we can't update attempts
        
        logger.warning(f"Failed login attempt for {login_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah"
        )
    except Exception as e:
        logger.error(f"Login error for {login_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan sistem. Silakan coba lagi."
        )
@router.post("/refresh", response_model=Dict[str, str])
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    _: None = Depends(check_auth_rate_limit)
):
    """Refresh access token using refresh token"""
    try:
        tokens = auth_utils.refresh_access_token(refresh_data.refresh_token)
        return tokens
        
    except Exception as e:
        logger.warning(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout_student(
    current_user: Student = Depends(get_current_user)
):
    """Logout student (invalidate tokens on client side)"""
    # In a production system, you might want to blacklist tokens
    # For now, we just return success and let client handle token removal
    
    logger.info(f"User logout: {current_user.email}")
    
    return {"message": "Logged out successfully"}


@router.post("/request-otp", response_model=OTPResponse)
async def request_otp(
    otp_request: OTPRequest,
    background_tasks: BackgroundTasks,
    _: None = Depends(check_otp_rate_limit)
):
    """Request OTP for email verification or password reset"""
    try:
        # Check if user exists for certain OTP types
        if otp_request.type in [OTPType.FORGOT_PASSWORD, OTPType.EMAIL_VERIFICATION]:
            student = await student_crud.get_student_by_email(otp_request.email)
            if not student:
                raise UserNotFoundException(otp_request.email)
        
        # Generate and send OTP
        otp_code = await otp_service.generate_and_send_otp(
            otp_request.email, 
            otp_request.type
        )
        
        # Add OTP record to student (if user exists)
        student = await student_crud.get_student_by_email(otp_request.email)
        if student:
            await student_crud.add_otp_record(
                otp_request.email, 
                otp_code, 
                otp_request.type
            )
        
        return OTPResponse(
            message="OTP sent successfully to your email",
            expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
            attempts_remaining=settings.OTP_MAX_ATTEMPTS
        )
        
    except UserNotFoundException:
        # For security, don't reveal if email exists for forgot password
        if otp_request.type == OTPType.FORGOT_PASSWORD:
            return OTPResponse(
                message="If the email exists, OTP has been sent",
                expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
                attempts_remaining=settings.OTP_MAX_ATTEMPTS
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"OTP request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again."
        )


@router.post("/verify-otp")
async def verify_otp(
    otp_verification: OTPVerification,
    _: None = Depends(check_otp_rate_limit)
):
    """Verify OTP code"""
    try:
        # Get student
        student = await student_crud.get_student_by_email(otp_verification.email)
        if not student:
            raise UserNotFoundException(otp_verification.email)
        
        # Verify OTP
        is_valid = await student_crud.verify_otp(
            otp_verification.email,
            otp_verification.code,
            otp_verification.type
        )
        
        if is_valid:
            message = "OTP verified successfully"
            
            # Additional actions based on OTP type
            if otp_verification.type == OTPType.REGISTRATION:
                message += ". Registration completed!"
            elif otp_verification.type == OTPType.EMAIL_VERIFICATION:
                message += ". Email verified!"
            elif otp_verification.type == OTPType.FORGOT_PASSWORD:
                message += ". You can now reset your password."
            
            return {"message": message, "verified": True}
        
    except (InvalidOTPException, OTPExpiredException, TooManyOTPAttemptsException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"OTP verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OTP verification failed. Please try again."
        )


@router.post("/forgot-password")
async def forgot_password(
    forgot_request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    _: None = Depends(check_otp_rate_limit)
):
    """Initiate password reset process"""
    try:
        # Check if user exists
        student = await student_crud.get_student_by_email(forgot_request.email)
        
        if student:
            # Generate and send OTP
            otp_code = await otp_service.generate_and_send_otp(
                forgot_request.email, 
                OTPType.FORGOT_PASSWORD
            )
            
            # Add OTP record
            await student_crud.add_otp_record(
                forgot_request.email, 
                otp_code, 
                OTPType.FORGOT_PASSWORD
            )
        
        # Always return success for security (don't reveal if email exists)
        return {
            "message": "If the email exists in our system, you will receive a password reset code."
        }
        
    except Exception as e:
        logger.error(f"Forgot password failed: {str(e)}")
        # Still return success for security
        return {
            "message": "If the email exists in our system, you will receive a password reset code."
        }


@router.post("/reset-password")
async def reset_password(
    reset_request: ResetPasswordRequest,
    _: None = Depends(check_auth_rate_limit)
):
    """Reset password using OTP"""
    try:
        # Validate new password
        is_valid, errors = validate_password_strength(reset_request.new_password)
        if not is_valid:
            raise WeakPasswordException(errors)
        
        # Get student
        student = await student_crud.get_student_by_email(reset_request.email)
        if not student:
            raise UserNotFoundException(reset_request.email)
        
        # Verify OTP
        is_valid = await student_crud.verify_otp(
            reset_request.email,
            reset_request.otp_code,
            OTPType.FORGOT_PASSWORD
        )
        
        if not is_valid:
            raise InvalidOTPException()
        
        # Update password
        await student_crud.update_password(reset_request.email, reset_request.new_password)
        
        logger.info(f"Password reset successful for: {reset_request.email}")
        
        return {"message": "Password reset successful. You can now login with your new password."}
        
    except (InvalidOTPException, OTPExpiredException, TooManyOTPAttemptsException, WeakPasswordException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Password reset failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed. Please try again."
        )


@router.post("/change-password")
async def change_password(
    change_request: ChangePasswordRequest,
    current_user: Student = Depends(get_current_user)
):
    """Change password for authenticated user"""
    try:
        # Verify current password
        from app.core.security import verify_password
        if not verify_password(change_request.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Check if new password is different
        if change_request.current_password == change_request.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password"
            )
        
        # Update password
        await student_crud.update_password(current_user.email, change_request.new_password)
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed. Please try again."
        )


@router.get("/me", response_model=StudentResponse)
async def get_current_user_info(
    current_user: Student = Depends(get_current_user)
):
    """Get current user information"""
    return StudentResponse(
        id=str(current_user.id),
        email=current_user.email,
        profile=current_user.profile,
        verification=current_user.verification,
        settings=current_user.settings,
        gamification=current_user.gamification,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        is_active=current_user.is_active
    )


@router.get("/verification-status", response_model=VerificationStatusResponse)
async def get_verification_status(
    current_user: Student = Depends(get_current_user)
):
    """Get user verification status"""
    return VerificationStatusResponse(
        email_verified=current_user.verification.email_verified,
        phone_verified=current_user.verification.phone_verified,
        registration_completed=current_user.verification.registration_completed
    )


@router.post("/resend-verification")
async def resend_verification_email(
    background_tasks: BackgroundTasks,
    current_user: Student = Depends(get_current_user),
    _: None = Depends(check_otp_rate_limit)
):
    """Resend email verification OTP"""
    try:
        if current_user.verification.email_verified:
            return {"message": "Email is already verified"}
        
        # Generate and send new OTP
        otp_code = await otp_service.generate_and_send_otp(
            current_user.email, 
            OTPType.EMAIL_VERIFICATION
        )
        
        # Add OTP record
        await student_crud.add_otp_record(
            current_user.email, 
            otp_code, 
            OTPType.EMAIL_VERIFICATION
        )
        
        return {"message": "Verification email sent successfully"}
        
    except Exception as e:
        logger.error(f"Resend verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again."
        )


# Background task functions
async def send_registration_otp(email: str):
    """Background task to send registration OTP"""
    try:
        otp_code = await otp_service.generate_and_send_otp(email, OTPType.REGISTRATION)
        await student_crud.add_otp_record(email, otp_code, OTPType.REGISTRATION)
        logger.info(f"Registration OTP sent to: {email}")
    except Exception as e:
        logger.error(f"Failed to send registration OTP to {email}: {str(e)}")


# Health check endpoint
@router.get("/health")
async def auth_health_check():
    """Health check for auth service"""
    return {"status": "healthy", "service": "auth", "timestamp": datetime.utcnow()}