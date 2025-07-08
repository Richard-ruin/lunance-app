# app/services/university_service.py
"""University management service with comprehensive CRUD operations."""

from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from ..config.database import get_database
from ..models.university import (
    UniversityInDB, UniversityCreate, UniversityUpdate, UniversityResponse,
    UniversityListResponse, UniversityStats, Faculty, Major, FacultyCreate,
    FacultyUpdate, MajorCreate, MajorUpdate
)
from ..models.common import PaginatedResponse, PaginationParams

logger = logging.getLogger(__name__)


class UniversityServiceError(Exception):
    """University service related error."""
    pass


class UniversityService:
    """University management service."""
    
    def __init__(self):
        self.collection_name = "universities"
    
    async def create_university(
        self,
        university_data: UniversityCreate,
        admin_user_id: str
    ) -> UniversityResponse:
        """
        Create new university.
        
        Args:
            university_data: University creation data
            admin_user_id: Admin user creating the university
            
        Returns:
            Created university response
            
        Raises:
            UniversityServiceError: If creation fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check if university name already exists
            existing_university = await collection.find_one(
                {"name": {"$regex": f"^{university_data.name}$", "$options": "i"}}
            )
            
            if existing_university:
                raise UniversityServiceError("University with this name already exists")
            
            # Generate unique IDs for faculties and majors
            faculties_with_ids = []
            for faculty in university_data.faculties:
                faculty_id = ObjectId()
                majors_with_ids = []
                
                for major in faculty.majors:
                    major_id = ObjectId()
                    majors_with_ids.append({
                        "_id": major_id,
                        "id": str(major_id),
                        "name": major.name
                    })
                
                faculties_with_ids.append({
                    "_id": faculty_id,
                    "id": str(faculty_id),
                    "name": faculty.name,
                    "majors": majors_with_ids
                })
            
            # Create university document
            university_doc = UniversityInDB(
                name=university_data.name,
                is_active=university_data.is_active,
                faculties=faculties_with_ids,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Insert university
            result = await collection.insert_one(
                university_doc.model_dump(by_alias=True, exclude={"id"})
            )
            
            university_id = str(result.inserted_id)
            
            # Get created university
            created_university_doc = await collection.find_one({"_id": result.inserted_id})
            created_university = UniversityInDB(**created_university_doc)
            
            logger.info(f"University created: {university_data.name} by admin {admin_user_id}")
            
            return UniversityResponse(
                id=university_id,
                name=created_university.name,
                is_active=created_university.is_active,
                faculties=created_university.faculties,
                created_at=created_university.created_at,
                updated_at=created_university.updated_at
            )
            
        except UniversityServiceError:
            raise
        except Exception as e:
            logger.error(f"Error creating university: {e}")
            raise UniversityServiceError("Failed to create university")
    
    async def get_university_by_id(self, university_id: str) -> Optional[UniversityResponse]:
        """
        Get university by ID.
        
        Args:
            university_id: University ID
            
        Returns:
            University response or None if not found
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            university_doc = await collection.find_one({"_id": ObjectId(university_id)})
            if not university_doc:
                return None
            
            university = UniversityInDB(**university_doc)
            
            return UniversityResponse(
                id=str(university.id),
                name=university.name,
                is_active=university.is_active,
                faculties=university.faculties,
                created_at=university.created_at,
                updated_at=university.updated_at
            )
            
        except Exception as e:
            logger.error(f"Error getting university {university_id}: {e}")
            return None
    
    async def list_universities(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> PaginatedResponse[UniversityListResponse]:
        """
        List universities with pagination and filters.
        
        Args:
            pagination: Pagination parameters
            search: Search term for university name
            is_active: Filter by active status
            
        Returns:
            Paginated university list response
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build query
            query = {}
            
            # Search filter
            if search:
                query["name"] = {"$regex": search, "$options": "i"}
            
            # Active status filter
            if is_active is not None:
                query["is_active"] = is_active
            
            # Get total count
            total = await collection.count_documents(query)
            
            # Build sort
            sort_field = pagination.sort_by or "created_at"
            sort_direction = DESCENDING if pagination.sort_order.value == "desc" else ASCENDING
            
            # Get paginated results
            skip = (pagination.page - 1) * pagination.per_page
            cursor = collection.find(query).sort(sort_field, sort_direction)
            cursor = cursor.skip(skip).limit(pagination.per_page)
            
            universities_docs = await cursor.to_list(length=pagination.per_page)
            
            # Convert to list response format
            universities = []
            for university_doc in universities_docs:
                university = UniversityInDB(**university_doc)
                
                # Count faculties and majors
                faculty_count = len(university.faculties)
                major_count = sum(len(faculty.get("majors", [])) for faculty in university.faculties)
                
                universities.append(UniversityListResponse(
                    id=str(university.id),
                    name=university.name,
                    is_active=university.is_active,
                    faculty_count=faculty_count,
                    major_count=major_count,
                    created_at=university.created_at
                ))
            
            return PaginatedResponse.create(
                items=universities,
                total=total,
                page=pagination.page,
                per_page=pagination.per_page
            )
            
        except Exception as e:
            logger.error(f"Error listing universities: {e}")
            raise UniversityServiceError("Failed to list universities")
    
    async def update_university(
        self,
        university_id: str,
        update_data: UniversityUpdate,
        admin_user_id: str
    ) -> Optional[UniversityResponse]:
        """
        Update university.
        
        Args:
            university_id: University ID
            update_data: Update data
            admin_user_id: Admin user performing the update
            
        Returns:
            Updated university response
            
        Raises:
            UniversityServiceError: If update fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check if university exists
            existing_university = await collection.find_one({"_id": ObjectId(university_id)})
            if not existing_university:
                raise UniversityServiceError("University not found")
            
            # Prepare update data
            update_fields = {}
            for field, value in update_data.model_dump(exclude_none=True).items():
                if value is not None:
                    update_fields[field] = value
            
            if not update_fields:
                # No updates provided, return current university
                return await self.get_university_by_id(university_id)
            
            # Check name uniqueness if name is being updated
            if "name" in update_fields:
                name_conflict = await collection.find_one({
                    "_id": {"$ne": ObjectId(university_id)},
                    "name": {"$regex": f"^{update_fields['name']}$", "$options": "i"}
                })
                if name_conflict:
                    raise UniversityServiceError("University with this name already exists")
            
            # Add updated timestamp
            update_fields["updated_at"] = datetime.utcnow()
            
            # Update university
            result = await collection.update_one(
                {"_id": ObjectId(university_id)},
                {"$set": update_fields}
            )
            
            if result.modified_count == 0:
                raise UniversityServiceError("Failed to update university")
            
            logger.info(f"University {university_id} updated by admin {admin_user_id}")
            
            return await self.get_university_by_id(university_id)
            
        except UniversityServiceError:
            raise
        except Exception as e:
            logger.error(f"Error updating university {university_id}: {e}")
            raise UniversityServiceError("Failed to update university")
    
    async def delete_university(
        self,
        university_id: str,
        admin_user_id: str
    ) -> bool:
        """
        Soft delete university (deactivate instead of actual deletion).
        
        Args:
            university_id: University ID
            admin_user_id: Admin user performing the deletion
            
        Returns:
            True if successful
            
        Raises:
            UniversityServiceError: If deletion fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check if university exists
            existing_university = await collection.find_one({"_id": ObjectId(university_id)})
            if not existing_university:
                raise UniversityServiceError("University not found")
            
            # Check if university has users
            users_collection = db.users
            user_count = await users_collection.count_documents({"university_id": university_id})
            
            if user_count > 0:
                # Soft delete by deactivating instead of removing
                result = await collection.update_one(
                    {"_id": ObjectId(university_id)},
                    {
                        "$set": {
                            "is_active": False,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                logger.info(f"University {university_id} deactivated (has {user_count} users) by admin {admin_user_id}")
            else:
                # Actually delete if no users
                result = await collection.delete_one({"_id": ObjectId(university_id)})
                logger.info(f"University {university_id} deleted by admin {admin_user_id}")
            
            return result.modified_count > 0 or result.deleted_count > 0
            
        except UniversityServiceError:
            raise
        except Exception as e:
            logger.error(f"Error deleting university {university_id}: {e}")
            raise UniversityServiceError("Failed to delete university")
    
    async def add_faculty(
        self,
        university_id: str,
        faculty_data: FacultyCreate,
        admin_user_id: str
    ) -> Optional[UniversityResponse]:
        """
        Add faculty to university.
        
        Args:
            university_id: University ID
            faculty_data: Faculty creation data
            admin_user_id: Admin user performing the action
            
        Returns:
            Updated university response
            
        Raises:
            UniversityServiceError: If operation fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check if university exists
            university_doc = await collection.find_one({"_id": ObjectId(university_id)})
            if not university_doc:
                raise UniversityServiceError("University not found")
            
            university = UniversityInDB(**university_doc)
            
            # Check if faculty name already exists in this university
            for faculty in university.faculties:
                if faculty.get("name", "").lower() == faculty_data.name.lower():
                    raise UniversityServiceError("Faculty with this name already exists in this university")
            
            # Create faculty with ID
            faculty_id = ObjectId()
            majors_with_ids = []
            
            for major in faculty_data.majors:
                major_id = ObjectId()
                majors_with_ids.append({
                    "_id": major_id,
                    "id": str(major_id),
                    "name": major.name
                })
            
            new_faculty = {
                "_id": faculty_id,
                "id": str(faculty_id),
                "name": faculty_data.name,
                "majors": majors_with_ids
            }
            
            # Add faculty to university
            result = await collection.update_one(
                {"_id": ObjectId(university_id)},
                {
                    "$push": {"faculties": new_faculty},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count == 0:
                raise UniversityServiceError("Failed to add faculty")
            
            logger.info(f"Faculty {faculty_data.name} added to university {university_id} by admin {admin_user_id}")
            
            return await self.get_university_by_id(university_id)
            
        except UniversityServiceError:
            raise
        except Exception as e:
            logger.error(f"Error adding faculty to university {university_id}: {e}")
            raise UniversityServiceError("Failed to add faculty")
    
    async def update_faculty(
        self,
        university_id: str,
        faculty_id: str,
        update_data: FacultyUpdate,
        admin_user_id: str
    ) -> Optional[UniversityResponse]:
        """
        Update faculty in university.
        
        Args:
            university_id: University ID
            faculty_id: Faculty ID
            update_data: Faculty update data
            admin_user_id: Admin user performing the action
            
        Returns:
            Updated university response
            
        Raises:
            UniversityServiceError: If operation fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Prepare update fields
            update_fields = {}
            for field, value in update_data.model_dump(exclude_none=True).items():
                if value is not None:
                    update_fields[f"faculties.$.{field}"] = value
            
            if not update_fields:
                # No updates provided
                return await self.get_university_by_id(university_id)
            
            # Add updated timestamp
            update_fields["updated_at"] = datetime.utcnow()
            
            # Update faculty
            result = await collection.update_one(
                {
                    "_id": ObjectId(university_id),
                    "faculties._id": ObjectId(faculty_id)
                },
                {"$set": update_fields}
            )
            
            if result.matched_count == 0:
                raise UniversityServiceError("University or faculty not found")
            
            if result.modified_count == 0:
                raise UniversityServiceError("Failed to update faculty")
            
            logger.info(f"Faculty {faculty_id} updated in university {university_id} by admin {admin_user_id}")
            
            return await self.get_university_by_id(university_id)
            
        except UniversityServiceError:
            raise
        except Exception as e:
            logger.error(f"Error updating faculty {faculty_id} in university {university_id}: {e}")
            raise UniversityServiceError("Failed to update faculty")
    
    async def delete_faculty(
        self,
        university_id: str,
        faculty_id: str,
        admin_user_id: str
    ) -> Optional[UniversityResponse]:
        """
        Delete faculty from university.
        
        Args:
            university_id: University ID
            faculty_id: Faculty ID
            admin_user_id: Admin user performing the action
            
        Returns:
            Updated university response
            
        Raises:
            UniversityServiceError: If operation fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check if any users are associated with this faculty
            users_collection = db.users
            user_count = await users_collection.count_documents({"faculty_id": faculty_id})
            
            if user_count > 0:
                raise UniversityServiceError(f"Cannot delete faculty: {user_count} users are associated with it")
            
            # Remove faculty
            result = await collection.update_one(
                {"_id": ObjectId(university_id)},
                {
                    "$pull": {"faculties": {"_id": ObjectId(faculty_id)}},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.matched_count == 0:
                raise UniversityServiceError("University not found")
            
            if result.modified_count == 0:
                raise UniversityServiceError("Faculty not found or failed to delete")
            
            logger.info(f"Faculty {faculty_id} deleted from university {university_id} by admin {admin_user_id}")
            
            return await self.get_university_by_id(university_id)
            
        except UniversityServiceError:
            raise
        except Exception as e:
            logger.error(f"Error deleting faculty {faculty_id} from university {university_id}: {e}")
            raise UniversityServiceError("Failed to delete faculty")
    
    async def add_major(
        self,
        university_id: str,
        faculty_id: str,
        major_data: MajorCreate,
        admin_user_id: str
    ) -> Optional[UniversityResponse]:
        """
        Add major to faculty.
        
        Args:
            university_id: University ID
            faculty_id: Faculty ID
            major_data: Major creation data
            admin_user_id: Admin user performing the action
            
        Returns:
            Updated university response
            
        Raises:
            UniversityServiceError: If operation fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Create major with ID
            major_id = ObjectId()
            new_major = {
                "_id": major_id,
                "id": str(major_id),
                "name": major_data.name
            }
            
            # Add major to faculty
            result = await collection.update_one(
                {
                    "_id": ObjectId(university_id),
                    "faculties._id": ObjectId(faculty_id)
                },
                {
                    "$push": {"faculties.$.majors": new_major},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.matched_count == 0:
                raise UniversityServiceError("University or faculty not found")
            
            if result.modified_count == 0:
                raise UniversityServiceError("Failed to add major")
            
            logger.info(f"Major {major_data.name} added to faculty {faculty_id} by admin {admin_user_id}")
            
            return await self.get_university_by_id(university_id)
            
        except UniversityServiceError:
            raise
        except Exception as e:
            logger.error(f"Error adding major to faculty {faculty_id}: {e}")
            raise UniversityServiceError("Failed to add major")
    
    async def get_university_stats(self) -> UniversityStats:
        """
        Get university system statistics.
        
        Returns:
            University statistics
        """
        try:
            db = await get_database()
            universities_collection = db[self.collection_name]
            users_collection = db.users
            
            # Total universities
            total_universities = await universities_collection.count_documents({})
            
            # Active universities
            active_universities = await universities_collection.count_documents({"is_active": True})
            
            # Total faculties and majors
            pipeline = [
                {"$unwind": "$faculties"},
                {"$group": {
                    "_id": None,
                    "total_faculties": {"$sum": 1},
                    "total_majors": {"$sum": {"$size": "$faculties.majors"}}
                }}
            ]
            
            stats_result = await universities_collection.aggregate(pipeline).to_list(1)
            
            if stats_result:
                total_faculties = stats_result[0]["total_faculties"]
                total_majors = stats_result[0]["total_majors"]
            else:
                total_faculties = 0
                total_majors = 0
            
            # Students per university
            students_pipeline = [
                {"$match": {"university_id": {"$ne": None}}},
                {"$group": {
                    "_id": "$university_id",
                    "student_count": {"$sum": 1}
                }},
                {"$lookup": {
                    "from": "universities",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "university"
                }},
                {"$unwind": "$university"},
                {"$project": {
                    "university_name": "$university.name",
                    "student_count": 1
                }},
                {"$sort": {"student_count": -1}},
                {"$limit": 10}
            ]
            
            students_result = await users_collection.aggregate(students_pipeline).to_list(10)
            
            students_per_university = [
                {
                    "university_name": item["university_name"],
                    "student_count": item["student_count"]
                }
                for item in students_result
            ]
            
            return UniversityStats(
                total_universities=total_universities,
                active_universities=active_universities,
                total_faculties=total_faculties,
                total_majors=total_majors,
                students_per_university=students_per_university
            )
            
        except Exception as e:
            logger.error(f"Error getting university stats: {e}")
            return UniversityStats(
                total_universities=0,
                active_universities=0,
                total_faculties=0,
                total_majors=0,
                students_per_university=[]
            )
    
    async def search_universities(
        self,
        search_term: str,
        limit: int = 10
    ) -> List[UniversityListResponse]:
        """
        Search universities by name.
        
        Args:
            search_term: Search term
            limit: Maximum results
            
        Returns:
            List of matching universities
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build search query
            query = {
                "$and": [
                    {"is_active": True},
                    {"name": {"$regex": search_term, "$options": "i"}}
                ]
            }
            
            # Execute search
            cursor = collection.find(query).limit(limit)
            universities_docs = await cursor.to_list(length=limit)
            
            # Convert to list response format
            universities = []
            for university_doc in universities_docs:
                university = UniversityInDB(**university_doc)
                
                faculty_count = len(university.faculties)
                major_count = sum(len(faculty.get("majors", [])) for faculty in university.faculties)
                
                universities.append(UniversityListResponse(
                    id=str(university.id),
                    name=university.name,
                    is_active=university.is_active,
                    faculty_count=faculty_count,
                    major_count=major_count,
                    created_at=university.created_at
                ))
            
            return universities
            
        except Exception as e:
            logger.error(f"Error searching universities: {e}")
            return []


# Global university service instance
university_service = UniversityService()