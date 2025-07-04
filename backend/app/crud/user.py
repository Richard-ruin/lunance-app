"""
User CRUD Operations
CRUD operations untuk User model dengan validasi dan business logic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from .base import CRUDBase
from ..models.user import User, UserRole, UserStatus
from ..schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations untuk User model"""
    
    async def create_user(
        self,
        *,
        obj_in: UserCreate,
        created_by: Optional[str] = None
    ) -> User:
        """
        Create user dengan validasi tambahan
        
        Args:
            obj_in: User create schema
            created_by: Admin ID yang membuat user (opsional)
            
        Returns:
            Created user
            
        Raises:
            ValueError: Jika email sudah exists atau validasi gagal
        """
        # Check if email already exists
        existing_user = await self.get_by_email(obj_in.email)
        if existing_user:
            raise ValueError(f"Email {obj_in.email} sudah terdaftar")
        
        # Validate university data untuk student
        if obj_in.role == UserRole.STUDENT:
            await self._validate_university_data(
                obj_in.university_id,
                obj_in.faculty_id, 
                obj_in.department_id
            )
        
        # Create user
        user = await self.create(obj_in=obj_in, created_by=created_by)
        
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.get_by_field("email", email.lower())
    
    async def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get active users"""
        query = {
            "status": UserStatus.ACTIVE,
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="created_at"
        )
    
    async def get_students(
        self,
        university_id: Optional[str] = None,
        faculty_id: Optional[str] = None,
        department_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get students dengan filter institusi"""
        query = {
            "role": UserRole.STUDENT,
            "status": UserStatus.ACTIVE,
            "is_deleted": {"$ne": True}
        }
        
        if university_id:
            query["university_id"] = university_id
        
        if faculty_id:
            query["faculty_id"] = faculty_id
        
        if department_id:
            query["department_id"] = department_id
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="full_name"
        )
    
    async def get_admins(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get admin users"""
        query = {
            "role": UserRole.ADMIN,
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="created_at"
        )
    
    async def update_profile(
        self,
        *,
        user_id: str,
        obj_in: UserUpdate
    ) -> Optional[User]:
        """Update user profile dengan validasi"""
        user = await self.get(user_id)
        if not user:
            return None
        
        # Validate university data jika diupdate
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if any(field in update_data for field in ["university_id", "faculty_id", "department_id"]):
            # Get current or new values
            university_id = update_data.get("university_id") or user.university_id
            faculty_id = update_data.get("faculty_id") or user.faculty_id
            department_id = update_data.get("department_id") or user.department_id
            
            if user.role == UserRole.STUDENT:
                await self._validate_university_data(university_id, faculty_id, department_id)
        
        return await self.update(id=user_id, obj_in=obj_in)
    
    async def verify_email(self, user_id: str) -> bool:
        """Verify user email"""
        user = await self.get(user_id)
        if not user:
            return False
        
        await user.verify_email()
        return True
    
    async def activate_user(self, user_id: str) -> bool:
        """Activate user"""
        user = await self.get(user_id)
        if not user:
            return False
        
        await user.activate()
        return True
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user"""
        user = await self.get(user_id)
        if not user:
            return False
        
        await user.deactivate()
        return True
    
    async def suspend_user(self, user_id: str) -> bool:
        """Suspend user"""
        user = await self.get(user_id)
        if not user:
            return False
        
        await user.suspend()
        return True
    
    async def update_login(self, user_id: str) -> bool:
        """Update login information"""
        user = await self.get(user_id)
        if not user:
            return False
        
        await user.update_login()
        return True
    
    async def bulk_update_status(
        self,
        *,
        user_ids: List[str],
        status: UserStatus,
        updated_by: Optional[str] = None
    ) -> List[User]:
        """Bulk update user status"""
        update_data = {"status": status}
        return await self.update_bulk(
            ids=user_ids,
            obj_in=update_data,
            updated_by=updated_by
        )
    
    async def search_users(
        self,
        *,
        search_term: str,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        university_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[User]:
        """Search users dengan berbagai filter"""
        query = {
            "$or": [
                {"full_name": {"$pattern": search_term, "$options": "i"}},
                {"email": {"$pattern": search_term, "$options": "i"}}
            ],
            "is_deleted": {"$ne": True}
        }
        
        if role:
            query["role"] = role
        
        if status:
            query["status"] = status
        
        if university_id:
            query["university_id"] = university_id
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="full_name"
        )
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        total_users = await self.count()
        
        # Count by role
        students_count = await self.count(query={"role": UserRole.STUDENT})
        admins_count = await self.count(query={"role": UserRole.ADMIN})
        
        # Count by status
        active_count = await self.count(query={"status": UserStatus.ACTIVE})
        pending_count = await self.count(query={"status": UserStatus.PENDING_VERIFICATION})
        suspended_count = await self.count(query={"status": UserStatus.SUSPENDED})
        
        # Count verified users
        verified_count = await self.count(query={"email_verified": True})
        
        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow().replace(day=1)  # Simplified for demo
        recent_count = await self.count(query={"created_at": {"$gte": thirty_days_ago}})
        
        return {
            "total_users": total_users,
            "students": students_count,
            "admins": admins_count,
            "active_users": active_count,
            "pending_verification": pending_count,
            "suspended_users": suspended_count,
            "verified_users": verified_count,
            "recent_registrations": recent_count,
            "verification_rate": (verified_count / total_users * 100) if total_users > 0 else 0
        }
    
    async def get_users_by_university(
        self,
        university_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users dari universitas tertentu"""
        query = {
            "university_id": university_id,
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="created_at"
        )
    
    async def check_email_available(self, email: str, exclude_user_id: Optional[str] = None) -> bool:
        """Check apakah email tersedia untuk digunakan"""
        query = {"email": email.lower()}
        
        if exclude_user_id:
            query["_id"] = {"$ne": exclude_user_id}
        
        existing = await self.model.find_one(query)
        return existing is None
    
    async def get_unverified_users(
        self,
        days_old: int = 7,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users yang belum verifikasi email dalam X hari"""
        cutoff_date = datetime.utcnow().replace(day=datetime.utcnow().day - days_old)
        
        query = {
            "email_verified": False,
            "status": UserStatus.PENDING_VERIFICATION,
            "created_at": {"$lte": cutoff_date},
            "is_deleted": {"$ne": True}
        }
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="created_at"
        )
    
    async def _validate_university_data(
        self,
        university_id: Optional[str],
        faculty_id: Optional[str],
        department_id: Optional[str]
    ):
        """Validate university, faculty, department relationship"""
        if not all([university_id, faculty_id, department_id]):
            raise ValueError("University, Faculty, dan Department harus diisi untuk mahasiswa")
        
        # Import disini untuk menghindari circular import
        from .university import crud_university, crud_faculty, crud_department
        
        # Check university exists and approved
        university = await crud_university.get(university_id)
        if not university or not university.is_active():
            raise ValueError("Universitas tidak ditemukan atau belum disetujui")
        
        # Check faculty exists and belongs to university
        faculty = await crud_faculty.get(faculty_id)
        if not faculty or faculty.university_id != university_id:
            raise ValueError("Fakultas tidak ditemukan atau tidak terkait dengan universitas")
        
        # Check department exists and belongs to faculty
        department = await crud_department.get(department_id)
        if not department or department.faculty_id != faculty_id:
            raise ValueError("Jurusan tidak ditemukan atau tidak terkait dengan fakultas")
    
    async def get_user_with_institution_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user dengan informasi institusi lengkap"""
        user = await self.get(user_id)
        if not user:
            return None
        
        result = user.to_dict()
        
        # Add institution info jika user adalah student
        if user.is_student() and user.university_id:
            from .university import crud_university, crud_faculty, crud_department
            
            university = await crud_university.get(user.university_id)
            if university:
                result["university_name"] = university.name
                result["university_domain"] = university.domain
            
            if user.faculty_id:
                faculty = await crud_faculty.get(user.faculty_id)
                if faculty:
                    result["faculty_name"] = faculty.name
            
            if user.department_id:
                department = await crud_department.get(user.department_id)
                if department:
                    result["department_name"] = department.name
        
        return result


# Create instance
crud_user = CRUDUser(User)