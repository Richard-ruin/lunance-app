# app/services/auth_service.py
"""Complete Authentication service for user management."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import logging
from bson import ObjectId

from ..config.database import get_database
from ..models.user import UserCreate, UserInDB, UserRole
from ..models.auth import (
    RegisterRequest, LoginRequest, PasswordResetRequest, 
    PasswordResetConfirm, TokenResponse, LoginResponse
)
from ..models.otp_verification import OTPType
from ..utils.password import hash_password, verify_password, validate_password_strength
from ..utils.jwt import create_token_pair, verify_token, TokenExpiredError, InvalidTokenError
from ..utils.otp import create_otp_verification, verify_otp
from ..utils.email_templates import get_otp_email_template
from ..services.email_service import EmailService

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Authentication related error."""
    pass


class AuthService:
    """Authentication service class."""
    
    def __init__(self):
        self.email_service = EmailService()
    
    async def register_user(self, register_data: RegisterRequest) -> Dict[str, Any]:
        """
        Register new user with OTP verification.
        
        Args:
            register_data: Registration data
            
        Returns:
            Registration result
            
        Raises:
            AuthenticationError: If registration fails
        """
        try:
            db = await get_database()
            users_collection = db.users
            
            # Check if user already exists
            existing_user = await users_collection.find_one(
                {"email": register_data.email}
            )
            
            if existing_user:
                raise AuthenticationError("User with this email already exists")
            
            # Verify OTP first
            otp_result = await verify_otp(
                email=register_data.email,
                otp_code=register_data.otp_code,
                otp_type=OTPType.REGISTER
            )
            
            if not otp_result["success"]:
                raise AuthenticationError(otp_result["message"])
            
            # Validate password strength
            is_strong, password_errors = validate_password_strength(register_data.password)
            if not is_strong:
                raise AuthenticationError(f"Password not strong enough: {', '.join(password_errors)}")
            
            # Create user data
            user_data = UserCreate(
                email=register_data.email,
                password=register_data.password,
                full_name=register_data.full_name,
                phone_number=register_data.phone_number or "",
                university_id=str(register_data.university_id) if register_data.university_id else None,
                faculty_id=str(register_data.faculty_id) if register_data.faculty_id else None,
                major_id=str(register_data.major_id) if register_data.major_id else None,
                initial_savings=register_data.initial_savings,
                role=UserRole.STUDENT
            )
            
            # Hash password
            password_hash = hash_password(user_data.password)
            
            # Create user document
            user_doc = UserInDB(
                **user_data.model_dump(exclude={"password"}),
                password_hash=password_hash,
                is_active=True,
                is_verified=True,  # Verified via OTP
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Insert user
            result = await users_collection.insert_one(
                user_doc.model_dump(by_alias=True, exclude={"id"})
            )
            
            user_id = str(result.inserted_id)
            
            # Create tokens
            tokens = create_token_pair(
                user_id=user_id,
                email=user_data.email,
                role=user_data.role
            )
            
            logger.info(f"User registered successfully: {user_data.email}")
            
            return {
                "success": True,
                "message": "User registered successfully",
                "user_id": user_id,
                "tokens": tokens
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise AuthenticationError("Registration failed")
    
    async def send_registration_otp(self, email: str) -> Dict[str, Any]:
        """
        Send OTP for registration.
        
        Args:
            email: User email
            
        Returns:
            OTP send result
        """
        try:
            # Check if user already exists
            db = await get_database()
            users_collection = db.users
            
            existing_user = await users_collection.find_one({"email": email})
            if existing_user:
                raise AuthenticationError("User with this email already exists")
            
            # Create OTP
            otp_data = await create_otp_verification(
                email=email,
                otp_type=OTPType.REGISTER,
                expires_minutes=5
            )
            
            # Get email template
            template = get_otp_email_template(
                otp_code=otp_data["otp_code"],
                otp_type="register",
                user_name="New User",
                expires_minutes=5
            )
            
            # Send email
            email_sent = await self.email_service.send_email_with_retry(
                to_email=email,
                subject=template["subject"],
                html_content=template["html_content"],
                text_content=template["text_content"]
            )
            
            if not email_sent:
                raise AuthenticationError("Failed to send verification email")
            
            logger.info(f"Registration OTP sent to: {email}")
            
            return {
                "success": True,
                "message": "Registration OTP sent successfully",
                "expires_in_seconds": 300  # 5 minutes
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Send registration OTP error: {e}")
            raise AuthenticationError("Failed to send registration OTP")
    
    async def login_user(self, login_data: LoginRequest) -> LoginResponse:
        """
        Authenticate user login.
        
        Args:
            login_data: Login credentials
            
        Returns:
            Login response with tokens and user data
            
        Raises:
            AuthenticationError: If login fails
        """
        try:
            db = await get_database()
            users_collection = db.users
            
            # Find user by email
            user_doc = await users_collection.find_one({"email": login_data.email})
            
            if not user_doc:
                raise AuthenticationError("Invalid email or password")
            
            user = UserInDB(**user_doc)
            
            # Check if user is active
            if not user.is_active:
                raise AuthenticationError("Account is deactivated")
            
            # Verify password
            if not verify_password(login_data.password, user.password_hash):
                logger.warning(f"Failed login attempt for: {login_data.email}")
                raise AuthenticationError("Invalid email or password")
            
            # Create tokens
            tokens_data = create_token_pair(
                user_id=str(user.id),
                email=user.email,
                role=user.role
            )
            
            tokens = TokenResponse(**tokens_data)
            
            # Update last login
            await users_collection.update_one(
                {"_id": ObjectId(str(user.id))},
                {"$set": {"updated_at": datetime.utcnow()}}
            )
            
            # Prepare user response data
            user_response = {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "role": user.role.value,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
            
            logger.info(f"User logged in successfully: {user.email}")
            
            return LoginResponse(
                user=user_response,
                tokens=tokens,
                message="Login successful"
            )
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise AuthenticationError("Login failed")
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token response
            
        Raises:
            AuthenticationError: If refresh fails
        """
        try:
            # Verify refresh token
            payload = verify_token(refresh_token)
            
            if payload.token_type != "refresh":
                raise AuthenticationError("Invalid token type")
            
            # Check if user still exists and is active
            db = await get_database()
            users_collection = db.users
            
            user_doc = await users_collection.find_one({
                "_id": ObjectId(payload.sub),
                "is_active": True
            })
            
            if not user_doc:
                raise AuthenticationError("User not found or inactive")
            
            # Create new token pair
            tokens_data = create_token_pair(
                user_id=payload.sub,
                email=payload.email,
                role=payload.role
            )
            
            logger.info(f"Token refreshed for user: {payload.email}")
            
            return TokenResponse(**tokens_data)
            
        except (TokenExpiredError, InvalidTokenError) as e:
            raise AuthenticationError(str(e))
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise AuthenticationError("Token refresh failed")
    
    async def send_password_reset_otp(self, reset_data: PasswordResetRequest) -> Dict[str, Any]:
        """
        Send password reset OTP.
        
        Args:
            reset_data: Password reset request
            
        Returns:
            OTP send result
        """
        try:
            db = await get_database()
            users_collection = db.users
            
            # Check if user exists
            user_doc = await users_collection.find_one({"email": reset_data.email})
            if not user_doc:
                # Don't reveal if email exists or not for security
                return {
                    "success": True,
                    "message": "If this email exists, a password reset code has been sent",
                    "expires_in_seconds": 300
                }
            
            user = UserInDB(**user_doc)
            
            # Create OTP
            otp_data = await create_otp_verification(
                email=reset_data.email,
                otp_type=OTPType.RESET_PASSWORD,
                expires_minutes=5
            )
            
            # Get email template
            template = get_otp_email_template(
                otp_code=otp_data["otp_code"],
                otp_type="reset_password",
                user_name=user.full_name,
                expires_minutes=5
            )
            
            # Send email
            email_sent = await self.email_service.send_email_with_retry(
                to_email=reset_data.email,
                subject=template["subject"],
                html_content=template["html_content"],
                text_content=template["text_content"]
            )
            
            if not email_sent:
                logger.error(f"Failed to send password reset email to: {reset_data.email}")
            
            logger.info(f"Password reset OTP sent to: {reset_data.email}")
            
            return {
                "success": True,
                "message": "If this email exists, a password reset code has been sent",
                "expires_in_seconds": 300
            }
            
        except Exception as e:
            logger.error(f"Send password reset OTP error: {e}")
            # Don't reveal internal errors for security
            return {
                "success": True,
                "message": "If this email exists, a password reset code has been sent",
                "expires_in_seconds": 300
            }
    
    async def reset_password(self, reset_data: PasswordResetConfirm) -> Dict[str, Any]:
        """
        Reset user password with OTP verification.
        
        Args:
            reset_data: Password reset confirmation data
            
        Returns:
            Reset result
            
        Raises:
            AuthenticationError: If reset fails
        """
        try:
            db = await get_database()
            users_collection = db.users
            
            # Check if user exists
            user_doc = await users_collection.find_one({"email": reset_data.email})
            if not user_doc:
                raise AuthenticationError("Invalid request")
            
            # Verify OTP
            otp_result = await verify_otp(
                email=reset_data.email,
                otp_code=reset_data.otp_code,
                otp_type=OTPType.RESET_PASSWORD
            )
            
            if not otp_result["success"]:
                raise AuthenticationError(otp_result["message"])
            
            # Validate new password strength
            is_strong, password_errors = validate_password_strength(reset_data.new_password)
            if not is_strong:
                raise AuthenticationError(f"Password not strong enough: {', '.join(password_errors)}")
            
            # Hash new password
            new_password_hash = hash_password(reset_data.new_password)
            
            # Update password
            result = await users_collection.update_one(
                {"email": reset_data.email},
                {
                    "$set": {
                        "password_hash": new_password_hash,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count == 0:
                raise AuthenticationError("Failed to update password")
            
            logger.info(f"Password reset successfully for: {reset_data.email}")
            
            return {
                "success": True,
                "message": "Password reset successfully"
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            raise AuthenticationError("Password reset failed")
    
    async def change_password(
        self, 
        user_id: str, 
        current_password: str, 
        new_password: str
    ) -> Dict[str, Any]:
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            Change result
            
        Raises:
            AuthenticationError: If change fails
        """
        try:
            db = await get_database()
            users_collection = db.users
            
            # Get user
            user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                raise AuthenticationError("User not found")
            
            user = UserInDB(**user_doc)
            
            # Verify current password
            if not verify_password(current_password, user.password_hash):
                raise AuthenticationError("Current password is incorrect")
            
            # Validate new password strength
            is_strong, password_errors = validate_password_strength(new_password)
            if not is_strong:
                raise AuthenticationError(f"New password not strong enough: {', '.join(password_errors)}")
            
            # Check if new password is different from current
            if verify_password(new_password, user.password_hash):
                raise AuthenticationError("New password must be different from current password")
            
            # Hash new password
            new_password_hash = hash_password(new_password)
            
            # Update password
            result = await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "password_hash": new_password_hash,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count == 0:
                raise AuthenticationError("Failed to update password")
            
            logger.info(f"Password changed successfully for user: {user_id}")
            
            return {
                "success": True,
                "message": "Password changed successfully"
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Change password error: {e}")
            raise AuthenticationError("Password change failed")
    
    async def verify_user_email(self, email: str, otp_code: str) -> Dict[str, Any]:
        """
        Verify user email with OTP.
        
        Args:
            email: User email
            otp_code: OTP code
            
        Returns:
            Verification result
            
        Raises:
            AuthenticationError: If verification fails
        """
        try:
            # Verify OTP
            otp_result = await verify_otp(
                email=email,
                otp_code=otp_code,
                otp_type=OTPType.EMAIL_VERIFICATION
            )
            
            if not otp_result["success"]:
                raise AuthenticationError(otp_result["message"])
            
            # Update user verification status
            db = await get_database()
            users_collection = db.users
            
            result = await users_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "is_verified": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count == 0:
                raise AuthenticationError("User not found")
            
            logger.info(f"Email verified successfully for: {email}")
            
            return {
                "success": True,
                "message": "Email verified successfully"
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Email verification error: {e}")
            raise AuthenticationError("Email verification failed")
    
    async def send_email_verification_otp(self, email: str) -> Dict[str, Any]:
        """
        Send email verification OTP.
        
        Args:
            email: User email
            
        Returns:
            OTP send result
        """
        try:
            db = await get_database()
            users_collection = db.users
            
            # Check if user exists
            user_doc = await users_collection.find_one({"email": email})
            if not user_doc:
                raise AuthenticationError("User not found")
            
            user = UserInDB(**user_doc)
            
            if user.is_verified:
                return {
                    "success": True,
                    "message": "Email is already verified"
                }
            
            # Create OTP
            otp_data = await create_otp_verification(
                email=email,
                otp_type=OTPType.EMAIL_VERIFICATION,
                expires_minutes=5
            )
            
            # Get email template
            template = get_otp_email_template(
                otp_code=otp_data["otp_code"],
                otp_type="email_verification",
                user_name=user.full_name,
                expires_minutes=5
            )
            
            # Send email
            email_sent = await self.email_service.send_email_with_retry(
                to_email=email,
                subject=template["subject"],
                html_content=template["html_content"],
                text_content=template["text_content"]
            )
            
            if not email_sent:
                raise AuthenticationError("Failed to send verification email")
            
            logger.info(f"Email verification OTP sent to: {email}")
            
            return {
                "success": True,
                "message": "Email verification code sent successfully",
                "expires_in_seconds": 300
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Send email verification OTP error: {e}")
            raise AuthenticationError("Failed to send email verification code")
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        try:
            db = await get_database()
            users_collection = db.users
            
            user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                return UserInDB(**user_doc)
            return None
            
        except Exception as e:
            logger.error(f"Get user by ID error: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User object or None if not found
        """
        try:
            db = await get_database()
            users_collection = db.users
            
            user_doc = await users_collection.find_one({"email": email})
            if user_doc:
                return UserInDB(**user_doc)
            return None
            
        except Exception as e:
            logger.error(f"Get user by email error: {e}")
            return None
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token and return user data.
        
        Args:
            token: JWT token
            
        Returns:
            Validation result with user data
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            # Verify token
            payload = verify_token(token)
            
            # Get user to ensure they still exist and are active
            user = await self.get_user_by_id(payload.sub)
            if not user or not user.is_active:
                raise AuthenticationError("User not found or inactive")
            
            return {
                "valid": True,
                "user_id": payload.sub,
                "email": payload.email,
                "role": payload.role.value,
                "token_type": payload.token_type
            }
            
        except (TokenExpiredError, InvalidTokenError) as e:
            raise AuthenticationError(str(e))
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise AuthenticationError("Token validation failed")