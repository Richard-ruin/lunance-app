# app/services/user_service.py
"""User management service with comprehensive CRUD operations."""

from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
import logging
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from ..config.database import get_database
from ..models.user import (
    UserInDB, UserCreate, UserUpdate, UserResponse, UserProfile, UserStats
)
from ..models.common import PaginatedResponse, PaginationParams
from ..utils.password import hash_password, verify_password, validate_password_strength
from ..services.email_service import email_service

logger = logging.getLogger(__name__)


class UserServiceError(Exception):
    """User service related error."""
    pass


class UserService:
    """User management service."""
    
    def __init__(self):
        self.collection_name = "users"
    
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
            collection = db[self.collection_name]
            
            user_doc = await collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                return UserInDB(**user_doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
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
            collection = db[self.collection_name]
            
            user_doc = await collection.find_one({"email": email.lower()})
            if user_doc:
                return UserInDB(**user_doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user profile with enriched data.
        
        Args:
            user_id: User ID
            
        Returns:
            User profile or None if not found
        """
        try:
            db = await get_database()
            users_collection = db[self.collection_name]
            universities_collection = db.universities
            
            # Get user data
            user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                return None
            
            user = UserInDB(**user_doc)
            
            # Get university, faculty, and major names
            university_name = None
            faculty_name = None
            major_name = None
            
            if user.university_id:
                university_doc = await universities_collection.find_one(
                    {"_id": ObjectId(user.university_id)}
                )
                if university_doc:
                    university_name = university_doc.get("name")
                    
                    # Find faculty and major names
                    if user.faculty_id:
                        for faculty in university_doc.get("faculties", []):
                            if str(faculty.get("_id", faculty.get("id"))) == user.faculty_id:
                                faculty_name = faculty.get("name")
                                
                                if user.major_id:
                                    for major in faculty.get("majors", []):
                                        if str(major.get("_id", major.get("id"))) == user.major_id:
                                            major_name = major.get("name")
                                            break
                                break
            
            return UserProfile(
                id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                phone_number=user.phone_number,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                university_name=university_name,
                faculty_name=faculty_name,
                major_name=major_name,
                initial_savings=user.initial_savings,
                created_at=user.created_at
            )
            
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            return None
    
    async def update_user_profile(
        self, 
        user_id: str, 
        update_data: UserUpdate
    ) -> Optional[UserResponse]:
        """
        Update user profile.
        
        Args:
            user_id: User ID
            update_data: Update data
            
        Returns:
            Updated user response or None if failed
            
        Raises:
            UserServiceError: If update fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check if user exists
            existing_user = await collection.find_one({"_id": ObjectId(user_id)})
            if not existing_user:
                raise UserServiceError("User not found")
            
            # Prepare update data
            update_fields = {}
            for field, value in update_data.model_dump(exclude_none=True).items():
                if value is not None:
                    update_fields[field] = value
            
            if not update_fields:
                # No updates provided, return current user
                return UserResponse(**existing_user)
            
            # Add updated timestamp
            update_fields["updated_at"] = datetime.utcnow()
            
            # Update user
            result = await collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_fields}
            )
            
            if result.modified_count == 0:
                raise UserServiceError("Failed to update user profile")
            
            # Get updated user
            updated_user_doc = await collection.find_one({"_id": ObjectId(user_id)})
            updated_user = UserInDB(**updated_user_doc)
            
            logger.info(f"User profile updated: {user_id}")
            
            return UserResponse(
                id=str(updated_user.id),
                email=updated_user.email,
                full_name=updated_user.full_name,
                phone_number=updated_user.phone_number,
                university_id=updated_user.university_id,
                faculty_id=updated_user.faculty_id,
                major_id=updated_user.major_id,
                role=updated_user.role,
                initial_savings=updated_user.initial_savings,
                is_active=updated_user.is_active,
                is_verified=updated_user.is_verified,
                created_at=updated_user.created_at,
                updated_at=updated_user.updated_at
            )
            
        except UserServiceError:
            raise
        except Exception as e:
            logger.error(f"Error updating user profile {user_id}: {e}")
            raise UserServiceError("Failed to update user profile")
    
    async def list_users(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        university_id: Optional[str] = None
    ) -> PaginatedResponse[UserResponse]:
        """
        List users with pagination and filters.
        
        Args:
            pagination: Pagination parameters
            search: Search term for name/email
            role: Filter by role
            is_active: Filter by active status
            is_verified: Filter by verification status
            university_id: Filter by university
            
        Returns:
            Paginated user response
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build query
            query = {}
            
            # Search filter
            if search:
                query["$or"] = [
                    {"full_name": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}}
                ]
            
            # Role filter
            if role:
                query["role"] = role
            
            # Active status filter
            if is_active is not None:
                query["is_active"] = is_active
            
            # Verification status filter
            if is_verified is not None:
                query["is_verified"] = is_verified
            
            # University filter
            if university_id:
                query["university_id"] = university_id
            
            # Get total count
            total = await collection.count_documents(query)
            
            # Build sort
            sort_field = pagination.sort_by or "created_at"
            sort_direction = DESCENDING if pagination.sort_order.value == "desc" else ASCENDING
            
            # Get paginated results
            skip = (pagination.page - 1) * pagination.per_page
            cursor = collection.find(query).sort(sort_field, sort_direction)
            cursor = cursor.skip(skip).limit(pagination.per_page)
            
            users_docs = await cursor.to_list(length=pagination.per_page)
            
            # Convert to response format
            users = []
            for user_doc in users_docs:
                user = UserInDB(**user_doc)
                users.append(UserResponse(
                    id=str(user.id),
                    email=user.email,
                    full_name=user.full_name,
                    phone_number=user.phone_number,
                    university_id=user.university_id,
                    faculty_id=user.faculty_id,
                    major_id=user.major_id,
                    role=user.role,
                    initial_savings=user.initial_savings,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                ))
            
            return PaginatedResponse.create(
                items=users,
                total=total,
                page=pagination.page,
                per_page=pagination.per_page
            )
            
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise UserServiceError("Failed to list users")
    
    async def update_user(
        self,
        user_id: str,
        update_data: UserUpdate,
        admin_user_id: str
    ) -> Optional[UserResponse]:
        """
        Admin update user (with more permissions than self-update).
        
        Args:
            user_id: Target user ID
            update_data: Update data
            admin_user_id: Admin user performing the update
            
        Returns:
            Updated user response
            
        Raises:
            UserServiceError: If update fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check if target user exists
            existing_user = await collection.find_one({"_id": ObjectId(user_id)})
            if not existing_user:
                raise UserServiceError("User not found")
            
            # Prepare update data
            update_fields = {}
            for field, value in update_data.model_dump(exclude_none=True).items():
                if value is not None:
                    update_fields[field] = value
            
            if not update_fields:
                # No updates provided, return current user
                return UserResponse(**existing_user)
            
            # Add updated timestamp and admin reference
            update_fields["updated_at"] = datetime.utcnow()
            
            # Update user
            result = await collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_fields}
            )
            
            if result.modified_count == 0:
                raise UserServiceError("Failed to update user")
            
            # Get updated user
            updated_user_doc = await collection.find_one({"_id": ObjectId(user_id)})
            updated_user = UserInDB(**updated_user_doc)
            
            logger.info(f"User {user_id} updated by admin {admin_user_id}")
            
            return UserResponse(
                id=str(updated_user.id),
                email=updated_user.email,
                full_name=updated_user.full_name,
                phone_number=updated_user.phone_number,
                university_id=updated_user.university_id,
                faculty_id=updated_user.faculty_id,
                major_id=updated_user.major_id,
                role=updated_user.role,
                initial_savings=updated_user.initial_savings,
                is_active=updated_user.is_active,
                is_verified=updated_user.is_verified,
                created_at=updated_user.created_at,
                updated_at=updated_user.updated_at
            )
            
        except UserServiceError:
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise UserServiceError("Failed to update user")
    
    async def delete_user(self, user_id: str, admin_user_id: str) -> bool:
        """
        Soft delete user (deactivate instead of actual deletion).
        
        Args:
            user_id: User ID to delete
            admin_user_id: Admin user performing the deletion
            
        Returns:
            True if successful
            
        Raises:
            UserServiceError: If deletion fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check if user exists
            existing_user = await collection.find_one({"_id": ObjectId(user_id)})
            if not existing_user:
                raise UserServiceError("User not found")
            
            # Soft delete by deactivating
            result = await collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count == 0:
                raise UserServiceError("Failed to delete user")
            
            logger.info(f"User {user_id} deleted (deactivated) by admin {admin_user_id}")
            return True
            
        except UserServiceError:
            raise
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise UserServiceError("Failed to delete user")
    
    async def get_user_stats(self, user_id: str) -> Optional[UserStats]:
        """
        Get user statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            User statistics or None if user not found
        """
        try:
            db = await get_database()
            
            # Check if user exists
            user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                return None
            
            # Get transaction stats
            transactions_collection = db.transactions
            
            # Total transactions
            total_transactions = await transactions_collection.count_documents(
                {"user_id": user_id}
            )
            
            # Income and expense totals
            income_pipeline = [
                {"$match": {"user_id": user_id, "type": "income"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            
            expense_pipeline = [
                {"$match": {"user_id": user_id, "type": "expense"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            
            income_result = await transactions_collection.aggregate(income_pipeline).to_list(1)
            expense_result = await transactions_collection.aggregate(expense_pipeline).to_list(1)
            
            total_income = income_result[0]["total"] if income_result else 0.0
            total_expense = expense_result[0]["total"] if expense_result else 0.0
            
            # Current balance (income - expense + initial savings)
            initial_savings = user_doc.get("initial_savings", 0.0)
            current_balance = total_income - total_expense + initial_savings
            
            # Savings targets stats
            savings_targets_collection = db.savings_targets
            
            active_savings_targets = await savings_targets_collection.count_documents({
                "user_id": user_id,
                "is_achieved": False
            })
            
            achieved_savings_targets = await savings_targets_collection.count_documents({
                "user_id": user_id,
                "is_achieved": True
            })
            
            # Categories used
            categories_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$category_id"}},
                {"$count": "total"}
            ]
            
            categories_result = await transactions_collection.aggregate(categories_pipeline).to_list(1)
            categories_used = categories_result[0]["total"] if categories_result else 0
            
            # Last transaction date
            last_transaction = await transactions_collection.find_one(
                {"user_id": user_id},
                sort=[("created_at", -1)]
            )
            
            last_transaction_date = last_transaction["created_at"] if last_transaction else None
            
            return UserStats(
                total_transactions=total_transactions,
                total_income=total_income,
                total_expense=total_expense,
                current_balance=current_balance,
                active_savings_targets=active_savings_targets,
                achieved_savings_targets=achieved_savings_targets,
                categories_used=categories_used,
                last_transaction_date=last_transaction_date
            )
            
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return None
    
    async def search_users(
        self,
        search_term: str,
        limit: int = 10
    ) -> List[UserResponse]:
        """
        Search users by name or email.
        
        Args:
            search_term: Search term
            limit: Maximum results
            
        Returns:
            List of matching users
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build search query
            query = {
                "$and": [
                    {"is_active": True},
                    {
                        "$or": [
                            {"full_name": {"$regex": search_term, "$options": "i"}},
                            {"email": {"$regex": search_term, "$options": "i"}}
                        ]
                    }
                ]
            }
            
            # Execute search
            cursor = collection.find(query).limit(limit)
            users_docs = await cursor.to_list(length=limit)
            
            # Convert to response format
            users = []
            for user_doc in users_docs:
                user = UserInDB(**user_doc)
                users.append(UserResponse(
                    id=str(user.id),
                    email=user.email,
                    full_name=user.full_name,
                    phone_number=user.phone_number,
                    university_id=user.university_id,
                    faculty_id=user.faculty_id,
                    major_id=user.major_id,
                    role=user.role,
                    initial_savings=user.initial_savings,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                ))
            
            return users
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    async def change_user_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if successful
            
        Raises:
            UserServiceError: If password change fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Get user
            user_doc = await collection.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                raise UserServiceError("User not found")
            
            user = UserInDB(**user_doc)
            
            # Verify current password
            if not verify_password(current_password, user.password_hash):
                raise UserServiceError("Current password is incorrect")
            
            # Validate new password strength
            is_strong, password_errors = validate_password_strength(new_password)
            if not is_strong:
                raise UserServiceError(f"New password not strong enough: {', '.join(password_errors)}")
            
            # Check if new password is different from current
            if verify_password(new_password, user.password_hash):
                raise UserServiceError("New password must be different from current password")
            
            # Hash new password
            new_password_hash = hash_password(new_password)
            
            # Update password
            result = await collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "password_hash": new_password_hash,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count == 0:
                raise UserServiceError("Failed to update password")
            
            logger.info(f"Password changed successfully for user: {user_id}")
            return True
            
        except UserServiceError:
            raise
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {e}")
            raise UserServiceError("Password change failed")
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """
        Send welcome email to new user.
        
        Args:
            user_email: User email
            user_name: User full name
            
        Returns:
            True if email sent successfully
        """
        try:
            return await email_service.send_welcome_email(user_email, user_name)
        except Exception as e:
            logger.error(f"Error sending welcome email to {user_email}: {e}")
            return False
    
    async def bulk_update_users(
        self,
        user_ids: List[str],
        update_data: Dict[str, Any],
        admin_user_id: str
    ) -> Dict[str, Any]:
        """
        Bulk update multiple users.
        
        Args:
            user_ids: List of user IDs to update
            update_data: Update data
            admin_user_id: Admin performing the update
            
        Returns:
            Update results
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Prepare update data
            update_fields = {**update_data, "updated_at": datetime.utcnow()}
            
            # Convert user IDs to ObjectIds
            object_ids = [ObjectId(user_id) for user_id in user_ids]
            
            # Perform bulk update
            result = await collection.update_many(
                {"_id": {"$in": object_ids}},
                {"$set": update_fields}
            )
            
            logger.info(f"Bulk updated {result.modified_count} users by admin {admin_user_id}")
            
            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "success": result.modified_count > 0
            }
            
        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            raise UserServiceError("Bulk update failed")


# Global user service instance
user_service = UserService()