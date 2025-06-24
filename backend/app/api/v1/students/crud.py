from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorCollection

from app.models.student import (
    Student, StudentCreate, StudentUpdate, StudentResponse,
    OTPType, OTPStatus, OTPRecord
)
from app.config.database import get_students_collection
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import (
    UserNotFoundException, UserAlreadyExistsException,
    DatabaseException, InvalidOTPException, OTPExpiredException,
    TooManyOTPAttemptsException, AccountLockedException
)
from app.config.settings import settings


class StudentCRUD:
    """CRUD operations for Student model"""
    
    def __init__(self):
        self.collection: Optional[AsyncIOMotorCollection] = None
    
    async def get_collection(self) -> AsyncIOMotorCollection:
        """Get students collection"""
        if self.collection is None:
            self.collection = await get_students_collection()
        return self.collection
    
    async def create_student(self, student_data: StudentCreate) -> Student:
        """Create new student account"""
        try:
            collection = await self.get_collection()
            
            # Check if user already exists
            existing_user = await collection.find_one({"email": student_data.email})
            if existing_user:
                raise UserAlreadyExistsException(email=student_data.email)
            
            # Hash password
            password_hash = get_password_hash(student_data.password)
            
            # Create student document
            student_dict = {
                "email": student_data.email,
                "password_hash": password_hash,
                "profile": student_data.profile.dict(),
                "verification": {
                    "email_verified": False,
                    "phone_verified": False,
                    "registration_completed": False
                },
                "otp_records": [],
                "settings": {
                    "notifications": {
                        "budget_alerts": True,
                        "savings_reminders": True,
                        "expense_sharing_updates": True,
                        "achievement_notifications": True
                    },
                    "display": {
                        "currency": "IDR",
                        "theme": "light",
                        "language": "id"
                    },
                    "privacy": {
                        "show_in_leaderboard": True,
                        "allow_expense_sharing": True
                    }
                },
                "gamification": {
                    "level": 1,
                    "experience_points": 0,
                    "badges": [],
                    "achievements": []
                },
                "failed_login_attempts": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True
            }
            
            # Insert into database
            result = await collection.insert_one(student_dict)
            
            # Retrieve created student
            created_student = await collection.find_one({"_id": result.inserted_id})
            return Student(**created_student)
            
        except DuplicateKeyError:
            raise UserAlreadyExistsException(email=student_data.email)
        except Exception as e:
            raise DatabaseException(f"Failed to create student: {str(e)}")
    
    async def get_student_by_email(self, email: str) -> Optional[Student]:
        """Get student by email"""
        try:
            collection = await self.get_collection()
            student_data = await collection.find_one({"email": email})
            
            if student_data:
                return Student(**student_data)
            return None
            
        except Exception as e:
            raise DatabaseException(f"Failed to get student: {str(e)}")
    
    async def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """Get student by ID"""
        try:
            collection = await self.get_collection()
            student_data = await collection.find_one({"_id": ObjectId(student_id)})
            
            if student_data:
                return Student(**student_data)
            return None
            
        except Exception as e:
            raise DatabaseException(f"Failed to get student: {str(e)}")
    
    async def update_student(self, student_id: str, update_data: StudentUpdate) -> Student:
        """Update student information"""
        try:
            collection = await self.get_collection()
            
            update_dict = {}
            if update_data.profile:
                update_dict["profile"] = update_data.profile.dict()
            if update_data.settings:
                update_dict["settings"] = update_data.settings.dict()
            
            update_dict["updated_at"] = datetime.utcnow()
            
            result = await collection.update_one(
                {"_id": ObjectId(student_id)},
                {"$set": update_dict}
            )
            
            if result.matched_count == 0:
                raise UserNotFoundException(student_id)
            
            # Return updated student
            updated_student = await self.get_student_by_id(student_id)
            return updated_student
            
        except UserNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to update student: {str(e)}")
    
    async def update_last_login(self, email: str) -> None:
        """Update last login timestamp"""
        try:
            collection = await self.get_collection()
            await collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "last_login": datetime.utcnow(),
                        "failed_login_attempts": 0,
                        "account_locked_until": None
                    }
                }
            )
        except Exception as e:
            raise DatabaseException(f"Failed to update last login: {str(e)}")
    
    async def increment_failed_login_attempts(self, email: str) -> int:
        """Increment failed login attempts and return new count"""
        try:
            collection = await self.get_collection()
            
            # Get current count
            student = await self.get_student_by_email(email)
            if not student:
                raise UserNotFoundException(email)
            
            new_count = student.failed_login_attempts + 1
            update_data = {
                "failed_login_attempts": new_count,
                "updated_at": datetime.utcnow()
            }
            
            # Lock account if too many attempts
            if new_count >= settings.MAX_LOGIN_ATTEMPTS:
                update_data["account_locked_until"] = (
                    datetime.utcnow() + timedelta(minutes=settings.ACCOUNT_LOCKOUT_DURATION)
                )
            
            await collection.update_one(
                {"email": email},
                {"$set": update_data}
            )
            
            return new_count
            
        except UserNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to update failed login attempts: {str(e)}")
    
    async def add_otp_record(self, email: str, otp_code: str, otp_type: OTPType) -> OTPRecord:
        """Add OTP record to student"""
        try:
            collection = await self.get_collection()
            
            # Create OTP record
            otp_record = OTPRecord(code=otp_code, type=otp_type)
            
            # Deactivate previous OTPs of same type and add new one
            await collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "otp_records.$[elem].status": OTPStatus.EXPIRED,
                        "updated_at": datetime.utcnow()
                    }
                },
                array_filters=[{"elem.type": otp_type, "elem.status": OTPStatus.PENDING}]
            )
            
            # Add new OTP record
            await collection.update_one(
                {"email": email},
                {
                    "$push": {"otp_records": otp_record.dict()},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return otp_record
            
        except Exception as e:
            raise DatabaseException(f"Failed to add OTP record: {str(e)}")
    
    async def verify_otp(self, email: str, otp_code: str, otp_type: OTPType) -> bool:
        """Verify OTP code and update verification status"""
        try:
            collection = await self.get_collection()
            
            # Get student with current OTP records
            student = await self.get_student_by_email(email)
            if not student:
                raise UserNotFoundException(email)
            
            # Find active OTP of specified type
            active_otp = None
            otp_index = None
            
            for i, otp_record in enumerate(reversed(student.otp_records)):
                if (otp_record.type == otp_type and 
                    otp_record.status == OTPStatus.PENDING and
                    not otp_record.is_expired()):
                    active_otp = otp_record
                    otp_index = len(student.otp_records) - 1 - i
                    break
            
            if not active_otp:
                raise OTPExpiredException()
            
            # Check attempts
            if active_otp.attempts >= active_otp.max_attempts:
                raise TooManyOTPAttemptsException()
            
            # Increment attempts
            update_data = {
                f"otp_records.{otp_index}.attempts": active_otp.attempts + 1,
                "updated_at": datetime.utcnow()
            }
            
            # Verify code
            if active_otp.code == otp_code:
                # Mark OTP as verified
                update_data[f"otp_records.{otp_index}.status"] = OTPStatus.VERIFIED
                update_data[f"otp_records.{otp_index}.verified_at"] = datetime.utcnow()
                
                # Update verification status based on OTP type
                if otp_type == OTPType.REGISTRATION:
                    update_data["verification.email_verified"] = True
                    update_data["verification.email_verified_at"] = datetime.utcnow()
                    update_data["verification.registration_completed"] = True
                    update_data["verification.registration_completed_at"] = datetime.utcnow()
                elif otp_type == OTPType.EMAIL_VERIFICATION:
                    update_data["verification.email_verified"] = True
                    update_data["verification.email_verified_at"] = datetime.utcnow()
                
                await collection.update_one(
                    {"email": email},
                    {"$set": update_data}
                )
                return True
            else:
                # Check if max attempts reached
                if active_otp.attempts + 1 >= active_otp.max_attempts:
                    update_data[f"otp_records.{otp_index}.status"] = OTPStatus.EXPIRED
                
                await collection.update_one(
                    {"email": email},
                    {"$set": update_data}
                )
                
                attempts_remaining = max(0, active_otp.max_attempts - (active_otp.attempts + 1))
                raise InvalidOTPException(attempts_remaining)
                
        except (UserNotFoundException, OTPExpiredException, TooManyOTPAttemptsException, InvalidOTPException):
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to verify OTP: {str(e)}")
    
    async def update_password(self, email: str, new_password: str) -> None:
        """Update student password"""
        try:
            collection = await self.get_collection()
            
            password_hash = get_password_hash(new_password)
            
            result = await collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "password_hash": password_hash,
                        "password_reset_token": None,
                        "password_reset_expires": None,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count == 0:
                raise UserNotFoundException(email)
                
        except UserNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to update password: {str(e)}")
    
    async def set_password_reset_token(self, email: str, token: str) -> None:
        """Set password reset token"""
        try:
            collection = await self.get_collection()
            
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            result = await collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "password_reset_token": token,
                        "password_reset_expires": expires_at,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count == 0:
                raise UserNotFoundException(email)
                
        except UserNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to set password reset token: {str(e)}")
    
    async def verify_password_reset_token(self, email: str, token: str) -> bool:
        """Verify password reset token"""
        try:
            student = await self.get_student_by_email(email)
            if not student:
                raise UserNotFoundException(email)
            
            if (student.password_reset_token != token or
                not student.password_reset_expires or
                datetime.utcnow() > student.password_reset_expires):
                return False
            
            return True
            
        except UserNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to verify password reset token: {str(e)}")
    
    async def deactivate_student(self, student_id: str) -> None:
        """Deactivate student account"""
        try:
            collection = await self.get_collection()
            
            result = await collection.update_one(
                {"_id": ObjectId(student_id)},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count == 0:
                raise UserNotFoundException(student_id)
                
        except UserNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to deactivate student: {str(e)}")
    
    async def authenticate_student(self, email: str, password: str) -> Optional[Student]:
        """Authenticate student with email and password"""
        try:
            student = await self.get_student_by_email(email)
            if not student:
                return None
            
            # Check if account is locked
            if student.is_account_locked():
                lockout_until = student.account_locked_until.strftime("%Y-%m-%d %H:%M:%S")
                raise AccountLockedException(lockout_until)
            
            # Verify password
            if not verify_password(password, student.password_hash):
                # Increment failed attempts
                await self.increment_failed_login_attempts(email)
                return None
            
            # Update last login and reset failed attempts
            await self.update_last_login(email)
            
            # Return fresh student data
            return await self.get_student_by_email(email)
            
        except AccountLockedException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to authenticate student: {str(e)}")
    
    async def get_students_by_university(self, university: str, limit: int = 10) -> List[Student]:
        """Get students by university"""
        try:
            collection = await self.get_collection()
            
            cursor = collection.find(
                {"profile.university": university, "is_active": True}
            ).limit(limit)
            
            students = []
            async for student_data in cursor:
                students.append(Student(**student_data))
            
            return students
            
        except Exception as e:
            raise DatabaseException(f"Failed to get students by university: {str(e)}")
    
    async def search_students(self, query: str, limit: int = 10) -> List[Student]:
        """Search students by name or email"""
        try:
            collection = await self.get_collection()
            
            search_filter = {
                "$and": [
                    {"is_active": True},
                    {"verification.email_verified": True},
                    {
                        "$or": [
                            {"profile.full_name": {"$regex": query, "$options": "i"}},
                            {"profile.nickname": {"$regex": query, "$options": "i"}},
                            {"email": {"$regex": query, "$options": "i"}}
                        ]
                    }
                ]
            }
            
            cursor = collection.find(search_filter).limit(limit)
            
            students = []
            async for student_data in cursor:
                students.append(Student(**student_data))
            
            return students
            
        except Exception as e:
            raise DatabaseException(f"Failed to search students: {str(e)}")


# Create global CRUD instance
student_crud = StudentCRUD()