"""
Base Model Classes
Model dasar untuk semua entities dengan field umum dan utilities
"""

from datetime import datetime
from typing import Optional, Any
from beanie import Document
from pydantic import Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId class untuk Pydantic validation"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class TimestampMixin:
    """Mixin untuk timestamp fields"""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    def update_timestamp(self):
        """Update timestamp saat model diupdate"""
        self.updated_at = datetime.utcnow()


class BaseDocument(Document, TimestampMixin):
    """
    Base document class untuk semua MongoDB documents
    Menyediakan field id, created_at, updated_at dan utility methods
    """
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    class Settings:
        # Beanie settings
        use_state_management = True
        validate_on_save = True
        
        # Pydantic settings
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True
    
    async def save_with_timestamp(self, **kwargs) -> "BaseDocument":
        """Save document dengan update timestamp"""
        self.update_timestamp()
        return await self.save(**kwargs)
    
    async def update_with_timestamp(self, update_data: dict, **kwargs) -> "BaseDocument":
        """Update document dengan timestamp"""
        update_data["updated_at"] = datetime.utcnow()
        return await self.update({"$set": update_data}, **kwargs)
    
    def to_dict(self, exclude_none: bool = True) -> dict:
        """Convert document to dictionary"""
        data = self.model_dump(exclude_none=exclude_none, by_alias=False)
        
        # Convert ObjectId to string
        if "id" in data and isinstance(data["id"], ObjectId):
            data["id"] = str(data["id"])
        
        # Convert datetime to ISO string
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        
        return data
    
    @classmethod
    async def find_by_id(cls, document_id: str) -> Optional["BaseDocument"]:
        """Find document by ID string"""
        try:
            object_id = ObjectId(document_id)
            return await cls.get(object_id)
        except Exception:
            return None
    
    @classmethod
    async def exists_by_id(cls, document_id: str) -> bool:
        """Check if document exists by ID"""
        doc = await cls.find_by_id(document_id)
        return doc is not None
    
    @classmethod
    async def delete_by_id(cls, document_id: str) -> bool:
        """Delete document by ID"""
        try:
            doc = await cls.find_by_id(document_id)
            if doc:
                await doc.delete()
                return True
            return False
        except Exception:
            return False
    
    @classmethod
    async def count_documents(cls, query: dict = None) -> int:
        """Count documents dengan query optional"""
        if query:
            return await cls.find(query).count()
        return await cls.find_all().count()
    
    @classmethod
    async def paginate(
        cls, 
        page: int = 1, 
        per_page: int = 10, 
        query: dict = None,
        sort_by: str = None,
        sort_order: int = -1
    ) -> dict:
        """
        Paginate documents dengan sorting
        
        Args:
            page: Halaman (mulai dari 1)
            per_page: Jumlah item per halaman
            query: MongoDB query filter
            sort_by: Field untuk sorting
            sort_order: 1 untuk ascending, -1 untuk descending
        
        Returns:
            Dict dengan data, pagination info
        """
        skip = (page - 1) * per_page
        
        # Build query
        find_query = cls.find(query or {})
        
        # Add sorting
        if sort_by:
            find_query = find_query.sort([(sort_by, sort_order)])
        
        # Get total count
        total = await find_query.count()
        
        # Get paginated results
        documents = await find_query.skip(skip).limit(per_page).to_list()
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "data": [doc.to_dict() for doc in documents],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
                "next_page": page + 1 if has_next else None,
                "prev_page": page - 1 if has_prev else None
            }
        }


class SoftDeleteMixin:
    """Mixin untuk soft delete functionality"""
    
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)
    
    async def soft_delete(self):
        """Soft delete document"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.update_timestamp()
        await self.save()
    
    async def restore(self):
        """Restore soft deleted document"""
        self.is_deleted = False
        self.deleted_at = None
        self.update_timestamp()
        await self.save()
    
    @classmethod
    async def find_active(cls, query: dict = None):
        """Find only non-deleted documents"""
        active_query = {"is_deleted": {"$ne": True}}
        if query:
            active_query.update(query)
        return cls.find(active_query)


class AuditMixin:
    """Mixin untuk audit trail"""
    
    created_by: Optional[str] = Field(default=None)
    updated_by: Optional[str] = Field(default=None)
    
    def set_created_by(self, user_id: str):
        """Set created_by field"""
        self.created_by = user_id
    
    def set_updated_by(self, user_id: str):
        """Set updated_by field"""
        self.updated_by = user_id
        self.update_timestamp()