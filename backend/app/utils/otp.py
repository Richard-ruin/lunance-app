# app/utils/otp.py
"""OTP generation and verification utilities."""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from ..config.database import get_database
from ..models.otp_verification import OTPVerificationInDB, OTPType

logger = logging.getLogger(__name__)


class OTPError(Exception):
    """OTP related error."""
    pass


def generate_otp(length: int = 6) -> str:
    """
    Generate random OTP code.
    
    Args:
        length: OTP length (default 6)
        
    Returns:
        Generated OTP string
    """
    if length < 4 or length > 8:
        length = 6
    
    # Generate random digits
    otp = ''.join(secrets.choice(string.digits) for _ in range(length))
    
    # Ensure OTP doesn't start with 0 (for better user experience)
    if otp[0] == '0':
        otp = secrets.choice('123456789') + otp[1:]
    
    logger.debug(f"Generated OTP with length {length}")
    return otp


def generate_secure_otp() -> str:
    """
    Generate cryptographically secure 6-digit OTP.
    
    Returns:
        6-digit OTP string
    """
    # Use SystemRandom for cryptographic security
    secure_random = secrets.SystemRandom()
    
    # Generate 6-digit number between 100000 and 999999
    otp_number = secure_random.randint(100000, 999999)
    
    return str(otp_number)


async def create_otp_verification(
    email: str,
    otp_type: OTPType,
    expires_minutes: int = 5
) -> Dict[str, Any]:
    """
    Create OTP verification entry in database.
    
    Args:
        email: User email
        otp_type: Type of OTP
        expires_minutes: OTP expiration in minutes
        
    Returns:
        Dictionary with OTP details
        
    Raises:
        OTPError: If failed to create OTP
    """
    try:
        db = await get_database()
        collection = db.otp_verifications
        
        # Generate OTP
        otp_code = generate_secure_otp()
        
        # Check for existing active OTPs
        existing_otp = await collection.find_one({
            "email": email,
            "otp_type": otp_type.value,
            "is_used": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if existing_otp:
            # Update existing OTP instead of creating new one
            # to prevent OTP spam
            result = await collection.update_one(
                {"_id": existing_otp["_id"]},
                {
                    "$set": {
                        "otp_code": otp_code,
                        "expires_at": datetime.utcnow() + timedelta(minutes=expires_minutes),
                        "attempts": 0,
                        "created_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count == 0:
                raise OTPError("Failed to update existing OTP")
            
            otp_id = str(existing_otp["_id"])
            logger.info(f"Updated existing OTP for {email}, type: {otp_type.value}")
        else:
            # Create new OTP verification
            otp_verification = OTPVerificationInDB.create_otp(
                email=email,
                otp_type=otp_type,
                otp_code=otp_code,
                expires_minutes=expires_minutes
            )
            
            # Insert into database
            result = await collection.insert_one(otp_verification.model_dump(by_alias=True))
            otp_id = str(result.inserted_id)
            
            logger.info(f"Created new OTP for {email}, type: {otp_type.value}")
        
        return {
            "otp_id": otp_id,
            "otp_code": otp_code,
            "email": email,
            "otp_type": otp_type.value,
            "expires_at": datetime.utcnow() + timedelta(minutes=expires_minutes),
            "expires_in_seconds": expires_minutes * 60
        }
        
    except Exception as e:
        logger.error(f"Error creating OTP verification: {e}")
        raise OTPError("Failed to create OTP verification")


async def verify_otp(
    email: str,
    otp_code: str,
    otp_type: OTPType
) -> Dict[str, Any]:
    """
    Verify OTP code.
    
    Args:
        email: User email
        otp_code: OTP code to verify
        otp_type: Type of OTP
        
    Returns:
        Dictionary with verification result
        
    Raises:
        OTPError: If verification fails
    """
    try:
        db = await get_database()
        collection = db.otp_verifications
        
        # Find OTP verification
        otp_doc = await collection.find_one({
            "email": email,
            "otp_type": otp_type.value,
            "is_used": False
        })
        
        if not otp_doc:
            return {
                "success": False,
                "message": "No valid OTP found for this email",
                "error_code": "OTP_NOT_FOUND"
            }
        
        # Create OTP object for validation
        otp_verification = OTPVerificationInDB(**otp_doc)
        
        # Check if OTP is expired
        if otp_verification.is_expired():
            await collection.update_one(
                {"_id": otp_doc["_id"]},
                {"$set": {"is_used": True}}
            )
            return {
                "success": False,
                "message": "OTP has expired",
                "error_code": "OTP_EXPIRED"
            }
        
        # Check if max attempts exceeded
        if otp_verification.attempts >= otp_verification.max_attempts:
            await collection.update_one(
                {"_id": otp_doc["_id"]},
                {"$set": {"is_used": True}}
            )
            return {
                "success": False,
                "message": "Maximum verification attempts exceeded",
                "error_code": "MAX_ATTEMPTS_EXCEEDED"
            }
        
        # Verify OTP code
        if otp_verification.otp_code != otp_code:
            # Increment attempts
            new_attempts = otp_verification.attempts + 1
            await collection.update_one(
                {"_id": otp_doc["_id"]},
                {"$set": {"attempts": new_attempts}}
            )
            
            remaining_attempts = otp_verification.max_attempts - new_attempts
            return {
                "success": False,
                "message": "Invalid OTP code",
                "error_code": "INVALID_OTP",
                "remaining_attempts": max(0, remaining_attempts)
            }
        
        # Mark OTP as used
        await collection.update_one(
            {"_id": otp_doc["_id"]},
            {"$set": {"is_used": True}}
        )
        
        logger.info(f"OTP verified successfully for {email}, type: {otp_type.value}")
        
        return {
            "success": True,
            "message": "OTP verified successfully",
            "otp_id": str(otp_doc["_id"])
        }
        
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        raise OTPError("Failed to verify OTP")


async def cleanup_expired_otps() -> int:
    """
    Clean up expired OTP verifications.
    
    Returns:
        Number of deleted OTPs
    """
    try:
        db = await get_database()
        collection = db.otp_verifications
        
        # Delete expired OTPs
        result = await collection.delete_many({
            "$or": [
                {"expires_at": {"$lt": datetime.utcnow()}},
                {"is_used": True, "created_at": {"$lt": datetime.utcnow() - timedelta(days=1)}}
            ]
        })
        
        deleted_count = result.deleted_count
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired OTPs")
        
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error cleaning up expired OTPs: {e}")
        return 0


async def get_otp_stats(email: Optional[str] = None) -> Dict[str, int]:
    """
    Get OTP statistics.
    
    Args:
        email: Optional email filter
        
    Returns:
        Dictionary with OTP statistics
    """
    try:
        db = await get_database()
        collection = db.otp_verifications
        
        # Build query
        query = {}
        if email:
            query["email"] = email
        
        # Get counts
        total_otps = await collection.count_documents(query)
        
        used_otps = await collection.count_documents({
            **query,
            "is_used": True
        })
        
        expired_otps = await collection.count_documents({
            **query,
            "expires_at": {"$lt": datetime.utcnow()},
            "is_used": False
        })
        
        active_otps = await collection.count_documents({
            **query,
            "is_used": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        return {
            "total": total_otps,
            "used": used_otps,
            "expired": expired_otps,
            "active": active_otps
        }
        
    except Exception as e:
        logger.error(f"Error getting OTP stats: {e}")
        return {
            "total": 0,
            "used": 0,
            "expired": 0,
            "active": 0
        }


async def resend_otp_allowed(email: str, otp_type: OTPType) -> Dict[str, Any]:
    """
    Check if OTP resend is allowed for email.
    
    Args:
        email: User email
        otp_type: Type of OTP
        
    Returns:
        Dictionary with resend status
    """
    try:
        db = await get_database()
        collection = db.otp_verifications
        
        # Check for recent OTPs (within last minute)
        recent_cutoff = datetime.utcnow() - timedelta(minutes=1)
        
        recent_otp = await collection.find_one({
            "email": email,
            "otp_type": otp_type.value,
            "created_at": {"$gt": recent_cutoff}
        })
        
        if recent_otp:
            time_remaining = 60 - int((datetime.utcnow() - recent_otp["created_at"]).total_seconds())
            return {
                "allowed": False,
                "message": f"Please wait {time_remaining} seconds before requesting new OTP",
                "wait_seconds": max(0, time_remaining)
            }
        
        # Check daily limit (max 10 OTPs per email per day)
        daily_cutoff = datetime.utcnow() - timedelta(hours=24)
        
        daily_count = await collection.count_documents({
            "email": email,
            "otp_type": otp_type.value,
            "created_at": {"$gt": daily_cutoff}
        })
        
        if daily_count >= 10:
            return {
                "allowed": False,
                "message": "Daily OTP limit exceeded. Please try again tomorrow.",
                "wait_seconds": None
            }
        
        return {
            "allowed": True,
            "message": "OTP resend allowed",
            "remaining_today": 10 - daily_count
        }
        
    except Exception as e:
        logger.error(f"Error checking OTP resend: {e}")
        return {
            "allowed": False,
            "message": "Error checking resend status",
            "wait_seconds": None
        }