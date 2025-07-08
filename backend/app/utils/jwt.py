# app/utils/jwt.py
"""JWT token utilities for authentication."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jose import JWTError, ExpiredSignatureError
import logging

from ..config.settings import settings
from ..models.auth import TokenPayload
from ..models.user import UserRole

logger = logging.getLogger(__name__)


class JWTError(Exception):
    """Custom JWT error."""
    pass


class TokenExpiredError(JWTError):
    """Token expired error."""
    pass


class InvalidTokenError(JWTError):
    """Invalid token error."""
    pass


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create access token.
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "token_type": "access"
    })
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        logger.debug(f"Access token created for user: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise JWTError("Failed to create access token")


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create refresh token.
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_refresh_token_expire_minutes
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "token_type": "refresh"
    })
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        logger.debug(f"Refresh token created for user: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise JWTError("Failed to create refresh token")


def verify_token(token: str) -> TokenPayload:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        TokenPayload with decoded data
        
    Raises:
        TokenExpiredError: If token is expired
        InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        # Validate required fields
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        token_type = payload.get("token_type")
        
        if not all([user_id, email, role, token_type]):
            raise InvalidTokenError("Token missing required fields")
        
        return TokenPayload(
            sub=user_id,
            email=email,
            role=UserRole(role),
            exp=payload.get("exp"),
            iat=payload.get("iat"),
            token_type=token_type
        )
        
    except ExpiredSignatureError:
        logger.warning("Token expired")
        raise TokenExpiredError("Token has expired")
    except JWTError as e:
        logger.warning(f"Invalid token: {e}")
        raise InvalidTokenError("Invalid token")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise InvalidTokenError("Token verification failed")


def create_token_pair(user_id: str, email: str, role: UserRole) -> Dict[str, Any]:
    """
    Create access and refresh token pair.
    
    Args:
        user_id: User ID
        email: User email
        role: User role
        
    Returns:
        Dictionary containing both tokens and metadata
    """
    token_data = {
        "sub": user_id,
        "email": email,
        "role": role.value
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,
        "refresh_expires_in": settings.jwt_refresh_token_expire_minutes * 60
    }


def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """
    Create new access token from refresh token.
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        New token pair
        
    Raises:
        InvalidTokenError: If refresh token is invalid or not refresh type
    """
    try:
        payload = verify_token(refresh_token)
        
        if payload.token_type != "refresh":
            raise InvalidTokenError("Invalid token type for refresh")
        
        # Create new token pair
        return create_token_pair(
            user_id=payload.sub,
            email=payload.email,
            role=payload.role
        )
        
    except (TokenExpiredError, InvalidTokenError):
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise InvalidTokenError("Failed to refresh token")


def get_token_expiry(token: str) -> Optional[datetime]:
    """
    Get token expiration time without verification.
    
    Args:
        token: JWT token
        
    Returns:
        Expiration datetime or None if cannot decode
    """
    try:
        # Decode without verification to get expiry
        payload = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp)
    except Exception as e:
        logger.warning(f"Could not decode token for expiry: {e}")
    
    return None


def is_token_expired(token: str) -> bool:
    """
    Check if token is expired without full verification.
    
    Args:
        token: JWT token
        
    Returns:
        True if expired, False otherwise
    """
    expiry = get_token_expiry(token)
    if expiry:
        return datetime.utcnow() > expiry
    return True  # Assume expired if cannot decode


def extract_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from token without verification.
    
    Args:
        token: JWT token
        
    Returns:
        User ID or None if cannot extract
    """
    try:
        payload = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        return payload.get("sub")
    except Exception:
        return None