"""
University CRUD Operations
CRUD operations untuk University, Faculty, Department models
"""

from typing import Optional, List, Dict, Any

from .base import CRUDBase
from ..models.university import University, Faculty, Department, ApprovalStatus
from ..schemas.university import (
    UniversityCreate, UniversityUpdate,
    FacultyCreate, FacultyUpdate,
    DepartmentCreate, DepartmentUpdate
)


class CRUDUniversity(CRUDBase[University, UniversityCreate, UniversityUpdate]):
    """CRUD operations untuk University model"""
    
    async def create_university(
        self,
        *,
        obj_in: UniversityCreate,
        created_by: Optional[str] = None
    ) -> University:
        """
        Create university dengan validasi domain unik
        
        Args:
            obj_in: University create schema
            created_by: User ID yang membuat
            
        Returns:
            Created university
            
        Raises:
            ValueError: Jika domain sudah exists
        """
        # Check if domain already exists
        existing = await self.get_by_domain(obj_in.domain)
        if existing:
            raise ValueError(f"Domain {obj_in.domain} sudah terdaftar")
        
        return await self.create(obj_in=obj_in, created_by=created_by)
    
    async def get_by_domain(self, domain: str) -> Optional[University]:
        """Get university by domain"""
        return await self.get_by_field("domain", domain.lower())
    
    async def get_approved_universities(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[University]:
        """Get approved universities"""
        query = {
            "approval_status": ApprovalStatus.APPROVED,
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="name"
        )
    
    async def get_pending_approval(self) -> List[University]:
        """Get universities pending approval"""
        query = {
            "approval_status": ApprovalStatus.PENDING,
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(query=query, sort_by="created_at")
    
    async def approve_university(
        self,
        *,
        university_id: str,
        approved_by: str
    ) -> Optional[University]:
        """Approve university"""
        university = await self.get(university_id)
        if not university:
            return None
        
        await university.approve(approved_by)
        return university
    
    async def reject_university(
        self,
        *,
        university_id: str,
        rejected_by: str,
        reason: str
    ) -> Optional[University]:
        """Reject university"""
        university = await self.get(university_id)
        if not university:
            return None
        
        await university.reject(rejected_by, reason)
        return university
    
    async def suspend_university(
        self,
        *,
        university_id: str,
        suspended_by: str,
        reason: str
    ) -> Optional[University]:
        """Suspend university"""
        university = await self.get(university_id)
        if not university:
            return None
        
        await university.suspend(suspended_by, reason)
        return university
    
    async def bulk_approve(
        self,
        *,
        university_ids: List[str],
        approved_by: str
    ) -> List[University]:
        """Bulk approve universities"""
        approved = []
        for university_id in university_ids:
            university = await self.approve_university(
                university_id=university_id,
                approved_by=approved_by
            )
            if university:
                approved.append(university)
        return approved
    
    async def search_universities(
        self,
        *,
        search_term: str,
        approval_status: Optional[ApprovalStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[University]:
        """Search universities"""
        query = {
            "$or": [
                {"name": {"$pattern": search_term, "$options": "i"}},
                {"domain": {"$pattern": search_term, "$options": "i"}},
                {"city": {"$pattern": search_term, "$options": "i"}}
            ],
            "is_deleted": {"$ne": True}
        }
        
        if approval_status:
            query["approval_status"] = approval_status
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="name"
        )
    
    async def get_university_stats(self) -> Dict[str, Any]:
        """Get university statistics"""
        total = await self.count()
        approved = await self.count(query={"approval_status": ApprovalStatus.APPROVED})
        pending = await self.count(query={"approval_status": ApprovalStatus.PENDING})
        rejected = await self.count(query={"approval_status": ApprovalStatus.REJECTED})
        suspended = await self.count(query={"approval_status": ApprovalStatus.SUSPENDED})
        
        return {
            "total_universities": total,
            "approved": approved,
            "pending_approval": pending,
            "rejected": rejected,
            "suspended": suspended,
            "approval_rate": (approved / total * 100) if total > 0 else 0
        }
    
    async def get_universities_by_province(self, province: str) -> List[University]:
        """Get universities by province"""
        query = {
            "province": {"$pattern": f"^{province}$", "$options": "i"},
            "approval_status": ApprovalStatus.APPROVED,
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(query=query, sort_by="name")


class CRUDFaculty(CRUDBase[Faculty, FacultyCreate, FacultyUpdate]):
    """CRUD operations untuk Faculty model"""
    
    async def create_faculty(
        self,
        *,
        obj_in: FacultyCreate,
        created_by: Optional[str] = None
    ) -> Faculty:
        """
        Create faculty dengan validasi university dan nama unik
        
        Args:
            obj_in: Faculty create schema
            created_by: User ID yang membuat
            
        Returns:
            Created faculty
            
        Raises:
            ValueError: Jika university tidak ada atau nama sudah exists
        """
        # Check if university exists and approved
        university = await crud_university.get(obj_in.university_id)
        if not university:
            raise ValueError("Universitas tidak ditemukan")
        
        if not university.is_active():
            raise ValueError("Universitas belum disetujui")
        
        # Check if faculty name exists in university
        existing = await self.exists_in_university(obj_in.university_id, obj_in.name)
        if existing:
            raise ValueError(f"Fakultas {obj_in.name} sudah ada di universitas ini")
        
        return await self.create(obj_in=obj_in, created_by=created_by)
    
    async def get_by_university(self, university_id: str) -> List[Faculty]:
        """Get faculties by university"""
        query = {
            "university_id": university_id,
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(query=query, sort_by="name")
    
    async def exists_in_university(self, university_id: str, name: str) -> bool:
        """Check if faculty name exists in university"""
        query = {
            "university_id": university_id,
            "name": {"$pattern": f"^{name}$", "$options": "i"},
            "is_deleted": {"$ne": True}
        }
        return await self.exists(query=query)
    
    async def search_faculties(
        self,
        *,
        search_term: str,
        university_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Faculty]:
        """Search faculties"""
        query = {
            "$or": [
                {"name": {"$pattern": search_term, "$options": "i"}},
                {"code": {"$pattern": search_term, "$options": "i"}}
            ],
            "is_deleted": {"$ne": True}
        }
        
        if university_id:
            query["university_id"] = university_id
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="name"
        )
    
    async def get_faculty_with_university(self, faculty_id: str) -> Optional[Dict[str, Any]]:
        """Get faculty dengan informasi university"""
        faculty = await self.get(faculty_id)
        if not faculty:
            return None
        
        result = faculty.to_dict()
        
        # Add university info
        university = await crud_university.get(faculty.university_id)
        if university:
            result["university_name"] = university.name
            result["university_domain"] = university.domain
        
        return result


class CRUDDepartment(CRUDBase[Department, DepartmentCreate, DepartmentUpdate]):
    """CRUD operations untuk Department model"""
    
    async def create_department(
        self,
        *,
        obj_in: DepartmentCreate,
        created_by: Optional[str] = None
    ) -> Department:
        """
        Create department dengan validasi faculty dan nama unik
        
        Args:
            obj_in: Department create schema
            created_by: User ID yang membuat
            
        Returns:
            Created department
            
        Raises:
            ValueError: Jika faculty tidak ada atau nama sudah exists
        """
        # Check if faculty exists
        faculty = await crud_faculty.get(obj_in.faculty_id)
        if not faculty:
            raise ValueError("Fakultas tidak ditemukan")
        
        # Check if department name exists in faculty
        existing = await self.exists_in_faculty(obj_in.faculty_id, obj_in.name)
        if existing:
            raise ValueError(f"Jurusan {obj_in.name} sudah ada di fakultas ini")
        
        return await self.create(obj_in=obj_in, created_by=created_by)
    
    async def get_by_faculty(self, faculty_id: str) -> List[Department]:
        """Get departments by faculty"""
        query = {
            "faculty_id": faculty_id,
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(query=query, sort_by="name")
    
    async def get_by_university(self, university_id: str) -> List[Department]:
        """Get departments by university (via faculty)"""
        # Get all faculties for the university
        faculties = await crud_faculty.get_by_university(university_id)
        faculty_ids = [faculty.id for faculty in faculties]
        
        if not faculty_ids:
            return []
        
        query = {
            "faculty_id": {"$in": faculty_ids},
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(query=query, sort_by="name")
    
    async def exists_in_faculty(self, faculty_id: str, name: str) -> bool:
        """Check if department name exists in faculty"""
        query = {
            "faculty_id": faculty_id,
            "name": {"$pattern": f"^{name}$", "$options": "i"},
            "is_deleted": {"$ne": True}
        }
        return await self.exists(query=query)
    
    async def search_departments(
        self,
        *,
        search_term: str,
        faculty_id: Optional[str] = None,
        university_id: Optional[str] = None,
        degree_level: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Department]:
        """Search departments"""
        query = {
            "$or": [
                {"name": {"$pattern": search_term, "$options": "i"}},
                {"code": {"$pattern": search_term, "$options": "i"}}
            ],
            "is_deleted": {"$ne": True}
        }
        
        if faculty_id:
            query["faculty_id"] = faculty_id
        elif university_id:
            # Get faculty IDs for university
            faculties = await crud_faculty.get_by_university(university_id)
            faculty_ids = [faculty.id for faculty in faculties]
            if faculty_ids:
                query["faculty_id"] = {"$in": faculty_ids}
            else:
                return []  # No faculties found
        
        if degree_level:
            query["degree_level"] = degree_level
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="name"
        )
    
    async def get_department_with_hierarchy(self, department_id: str) -> Optional[Dict[str, Any]]:
        """Get department dengan informasi faculty dan university"""
        department = await self.get(department_id)
        if not department:
            return None
        
        result = department.to_dict()
        
        # Add faculty info
        faculty = await crud_faculty.get(department.faculty_id)
        if faculty:
            result["faculty_name"] = faculty.name
            result["faculty_code"] = faculty.code
            
            # Add university info
            university = await crud_university.get(faculty.university_id)
            if university:
                result["university_id"] = university.id
                result["university_name"] = university.name
                result["university_domain"] = university.domain
        
        return result
    
    async def get_departments_by_degree(self, degree_level: str) -> List[Department]:
        """Get departments by degree level"""
        query = {
            "degree_level": degree_level,
            "is_deleted": {"$ne": True}
        }
        return await self.get_multi(query=query, sort_by="name")


# Create instances
crud_university = CRUDUniversity(University)
crud_faculty = CRUDFaculty(Faculty)
crud_department = CRUDDepartment(Department)