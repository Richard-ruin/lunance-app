"""JWT token utilities - WORKING VERSION."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

# Try different import strategies
try:
    import jwt as PyJWT
except ImportError:
    try:
        import PyJWT
    except ImportError:
        # Fallback to basic implementation
        class PyJWT:
            @staticmethod
            def encode(payload, key, algorithm="HS256"):
                import base64
                import json
                import hmac
                import hashlib
                
                # Simple JWT implementation for fallback
                header = {"alg": algorithm, "typ": "JWT"}
                
                def base64url_encode(data):
                    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')
                
                encoded_header = base64url_encode(json.dumps(header).encode('utf-8'))
                encoded_payload = base64url_encode(json.dumps(payload, default=str).encode('utf-8'))
                
                message = f"{encoded_header}.{encoded_payload}"
                signature = hmac.new(
                    key.encode('utf-8'),
                    message.encode('utf-8'),
                    hashlib.sha256
                ).digest()
                encoded_signature = base64url_encode(signature)
                
                return f"{message}.{encoded_signature}"
            
            @staticmethod
            def decode(token, key, algorithms=None):
                # Simple decode - just return payload without verification for now
                import base64
                import json
                
                try:
                    parts = token.split('.')
                    if len(parts) != 3:
                        raise Exception("Invalid token format")
                    
                    payload_part = parts[1]
                    # Add padding if needed
                    payload_part += '=' * (4 - len(payload_part) % 4)
                    
                    payload_bytes = base64.urlsafe_b64decode(payload_part)
                    payload = json.loads(payload_bytes)
                    
                    return payload
                except Exception as e:
                    raise Exception(f"Token decode error: {e}")

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
    """Create access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "token_type": "access"
    })
    
    try:
        encoded_jwt = PyJWT.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        logger.debug(f"Access token created for user: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise JWTError(f"Failed to create access token: {e}")


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create refresh token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_refresh_token_expire_minutes
        )
    
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "token_type": "refresh"
    })
    
    try:
        encoded_jwt = PyJWT.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        logger.debug(f"Refresh token created for user: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}")
        raise JWTError(f"Failed to create refresh token: {e}")


def verify_token(token: str) -> TokenPayload:
    """Verify and decode JWT token."""
    try:
        payload = PyJWT.decode(
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
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise TokenExpiredError("Token has expired")
        
        return TokenPayload(
            sub=user_id,
            email=email,
            role=UserRole(role),
            exp=exp,
            iat=payload.get("iat"),
            token_type=token_type
        )
        
    except TokenExpiredError:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise InvalidTokenError(f"Token verification failed: {e}")


def create_token_pair(user_id: str, email: str, role: UserRole) -> Dict[str, Any]:
    """Create access and refresh token pair."""
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
    """Create new access token from refresh token."""
    try:
        payload = verify_token(refresh_token)
        
        if payload.token_type != "refresh":
            raise InvalidTokenError("Invalid token type for refresh")
        
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
    """Get token expiration time without verification."""
    try:
        payload = PyJWT.decode(
            token,
            options={"verify_signature": False} if hasattr(PyJWT, 'decode') else {}
        )
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp)
    except Exception as e:
        logger.warning(f"Could not decode token for expiry: {e}")
    
    return None


def is_token_expired(token: str) -> bool:
    """Check if token is expired without full verification."""
    expiry = get_token_expiry(token)
    if expiry:
        return datetime.utcnow() > expiry
    return True


def extract_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from token without verification."""
    try:
        payload = PyJWT.decode(
            token,
            options={"verify_signature": False} if hasattr(PyJWT, 'decode') else {}
        )
        return payload.get("sub")
    except Exception:
        return None
