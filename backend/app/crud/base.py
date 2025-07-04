"""
Base CRUD Operations
CRUD operations dasar untuk semua models dengan Beanie ODM
"""

from typing import Any, Dict, List, Optional, Union, Type, TypeVar, Generic
from datetime import datetime
from pydantic import BaseModel
from beanie import Document
from bson import ObjectId

from ..models.base import BaseDocument

# Type variables
ModelType = TypeVar("ModelType", bound=BaseDocument)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class dengan operasi standar untuk semua models
    
    Menyediakan:
    - Create, Read, Update, Delete operations
    - Bulk operations
    - Filtering dan pagination
    - Soft delete support
    - Audit trail
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD dengan model class
        
        Args:
            model: Beanie Document model class
        """
        self.model = model
    
    # Basic CRUD Operations
    async def create(
        self, 
        *, 
        obj_in: CreateSchemaType,
        created_by: Optional[str] = None
    ) -> ModelType:
        """
        Create new document
        
        Args:
            obj_in: Pydantic schema dengan data untuk create
            created_by: User ID yang membuat document
            
        Returns:
            Created document
        """
        obj_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        
        # Create document instance
        db_obj = self.model(**obj_data)
        
        # Set audit fields jika model support
        if hasattr(db_obj, 'set_created_by') and created_by:
            db_obj.set_created_by(created_by)
        
        # Save document
        await db_obj.save()
        return db_obj
    
    async def get(self, id: Union[str, ObjectId]) -> Optional[ModelType]:
        """
        Get document by ID
        
        Args:
            id: Document ID
            
        Returns:
            Document atau None jika tidak ditemukan
        """
        try:
            if isinstance(id, str):
                id = ObjectId(id)
            return await self.model.get(id)
        except Exception:
            return None
    
    async def get_by_field(
        self, 
        field: str, 
        value: Any, 
        active_only: bool = True
    ) -> Optional[ModelType]:
        """
        Get document by specific field
        
        Args:
            field: Field name
            value: Field value
            active_only: Hanya ambil document yang tidak soft deleted
            
        Returns:
            Document atau None
        """
        query = {field: value}
        
        if active_only and hasattr(self.model, 'is_deleted'):
            query['is_deleted'] = {'$ne': True}
        
        return await self.model.find_one(query)
    
    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        query: Dict[str, Any] = None,
        sort_by: str = None,
        sort_order: int = -1,
        active_only: bool = True
    ) -> List[ModelType]:
        """
        Get multiple documents dengan filtering dan sorting
        
        Args:
            skip: Jumlah document yang dilewati
            limit: Maksimum jumlah document
            query: MongoDB query filter
            sort_by: Field untuk sorting
            sort_order: 1 untuk ascending, -1 untuk descending
            active_only: Hanya document yang tidak soft deleted
            
        Returns:
            List of documents
        """
        find_query = query or {}
        
        # Filter soft deleted documents
        if active_only and hasattr(self.model, 'is_deleted'):
            find_query['is_deleted'] = {'$ne': True}
        
        # Build query
        cursor = self.model.find(find_query)
        
        # Add sorting
        if sort_by:
            cursor = cursor.sort([(sort_by, sort_order)])
        
        # Apply pagination
        cursor = cursor.skip(skip).limit(limit)
        
        return await cursor.to_list()
    
    async def update(
        self,
        *,
        id: Union[str, ObjectId],
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        updated_by: Optional[str] = None
    ) -> Optional[ModelType]:
        """
        Update document by ID
        
        Args:
            id: Document ID
            obj_in: Update data (schema atau dict)
            updated_by: User ID yang update document
            
        Returns:
            Updated document atau None jika tidak ditemukan
        """
        # Get existing document
        db_obj = await self.get(id)
        if not db_obj:
            return None
        
        # Prepare update data
        if hasattr(obj_in, 'model_dump'):
            update_data = obj_in.model_dump(exclude_unset=True)
        elif hasattr(obj_in, 'dict'):
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = obj_in
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # Set audit fields
        if hasattr(db_obj, 'set_updated_by') and updated_by:
            db_obj.set_updated_by(updated_by)
        
        # Update timestamp
        if hasattr(db_obj, 'update_timestamp'):
            db_obj.update_timestamp()
        
        # Apply updates
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        # Save document
        await db_obj.save()
        return db_obj
    
    async def delete(self, *, id: Union[str, ObjectId]) -> bool:
        """
        Hard delete document
        
        Args:
            id: Document ID
            
        Returns:
            True jika berhasil dihapus
        """
        db_obj = await self.get(id)
        if not db_obj:
            return False
        
        await db_obj.delete()
        return True
    
    async def soft_delete(
        self, 
        *, 
        id: Union[str, ObjectId],
        deleted_by: Optional[str] = None
    ) -> bool:
        """
        Soft delete document (jika model support soft delete)
        
        Args:
            id: Document ID
            deleted_by: User ID yang menghapus
            
        Returns:
            True jika berhasil di-soft delete
        """
        db_obj = await self.get(id)
        if not db_obj:
            return False
        
        # Check if model supports soft delete
        if not hasattr(db_obj, 'soft_delete'):
            return False
        
        # Set deleted_by jika ada
        if hasattr(db_obj, 'set_updated_by') and deleted_by:
            db_obj.set_updated_by(deleted_by)
        
        await db_obj.soft_delete()
        return True
    
    async def restore(self, *, id: Union[str, ObjectId]) -> bool:
        """
        Restore soft deleted document
        
        Args:
            id: Document ID
            
        Returns:
            True jika berhasil direstore
        """
        # Get document termasuk yang soft deleted
        try:
            if isinstance(id, str):
                id = ObjectId(id)
            db_obj = await self.model.get(id)
        except Exception:
            return False
        
        if not db_obj or not hasattr(db_obj, 'restore'):
            return False
        
        await db_obj.restore()
        return True
    
    # Bulk Operations
    async def create_bulk(
        self,
        *,
        obj_list: List[CreateSchemaType],
        created_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Bulk create documents
        
        Args:
            obj_list: List of create schemas
            created_by: User ID yang membuat
            
        Returns:
            List of created documents
        """
        documents = []
        
        for obj_in in obj_list:
            obj_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
            db_obj = self.model(**obj_data)
            
            if hasattr(db_obj, 'set_created_by') and created_by:
                db_obj.set_created_by(created_by)
            
            documents.append(db_obj)
        
        # Bulk insert
        if documents:
            await self.model.insert_many(documents)
        
        return documents
    
    async def update_bulk(
        self,
        *,
        ids: List[Union[str, ObjectId]],
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        updated_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Bulk update documents
        
        Args:
            ids: List of document IDs
            obj_in: Update data
            updated_by: User ID yang update
            
        Returns:
            List of updated documents
        """
        # Prepare update data
        if hasattr(obj_in, 'model_dump'):
            update_data = obj_in.model_dump(exclude_unset=True)
        elif hasattr(obj_in, 'dict'):
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = obj_in
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # Add timestamp and audit info
        update_data['updated_at'] = datetime.utcnow()
        if updated_by:
            update_data['updated_by'] = updated_by
        
        # Convert string IDs to ObjectId
        object_ids = []
        for id in ids:
            if isinstance(id, str):
                try:
                    object_ids.append(ObjectId(id))
                except Exception:
                    continue
            else:
                object_ids.append(id)
        
        # Bulk update
        await self.model.find({'_id': {'$in': object_ids}}).update({'$set': update_data})
        
        # Return updated documents
        return await self.model.find({'_id': {'$in': object_ids}}).to_list()
    
    async def delete_bulk(
        self,
        *,
        ids: List[Union[str, ObjectId]],
        soft: bool = True,
        deleted_by: Optional[str] = None
    ) -> int:
        """
        Bulk delete documents
        
        Args:
            ids: List of document IDs
            soft: True untuk soft delete, False untuk hard delete
            deleted_by: User ID yang menghapus (untuk soft delete)
            
        Returns:
            Jumlah document yang berhasil dihapus
        """
        # Convert string IDs to ObjectId
        object_ids = []
        for id in ids:
            if isinstance(id, str):
                try:
                    object_ids.append(ObjectId(id))
                except Exception:
                    continue
            else:
                object_ids.append(id)
        
        if not object_ids:
            return 0
        
        if soft and hasattr(self.model, 'is_deleted'):
            # Soft delete
            update_data = {
                'is_deleted': True,
                'deleted_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            if deleted_by:
                update_data['updated_by'] = deleted_by
            
            result = await self.model.find({'_id': {'$in': object_ids}}).update({'$set': update_data})
            return result.modified_count if hasattr(result, 'modified_count') else len(object_ids)
        else:
            # Hard delete
            result = await self.model.find({'_id': {'$in': object_ids}}).delete()
            return result.deleted_count if hasattr(result, 'deleted_count') else 0
    
    # Utility Methods
    async def count(
        self,
        *,
        query: Dict[str, Any] = None,
        active_only: bool = True
    ) -> int:
        """
        Count documents
        
        Args:
            query: MongoDB query filter
            active_only: Hanya count document yang tidak soft deleted
            
        Returns:
            Jumlah document
        """
        find_query = query or {}
        
        if active_only and hasattr(self.model, 'is_deleted'):
            find_query['is_deleted'] = {'$ne': True}
        
        return await self.model.find(find_query).count()
    
    async def exists(
        self,
        *,
        query: Dict[str, Any],
        active_only: bool = True
    ) -> bool:
        """
        Check if document exists
        
        Args:
            query: MongoDB query
            active_only: Hanya check document yang tidak soft deleted
            
        Returns:
            True jika document exists
        """
        if active_only and hasattr(self.model, 'is_deleted'):
            query['is_deleted'] = {'$ne': True}
        
        doc = await self.model.find_one(query)
        return doc is not None
    
    async def paginate(
        self,
        *,
        page: int = 1,
        per_page: int = 10,
        query: Dict[str, Any] = None,
        sort_by: str = None,
        sort_order: int = -1,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """
        Paginate documents dengan informasi pagination lengkap
        
        Args:
            page: Halaman (mulai dari 1)
            per_page: Jumlah item per halaman
            query: MongoDB query filter
            sort_by: Field untuk sorting
            sort_order: 1 untuk ascending, -1 untuk descending
            active_only: Hanya document yang tidak soft deleted
            
        Returns:
            Dict dengan data dan pagination info
        """
        # Ensure page >= 1
        page = max(1, page)
        skip = (page - 1) * per_page
        
        # Get documents
        documents = await self.get_multi(
            skip=skip,
            limit=per_page,
            query=query,
            sort_by=sort_by,
            sort_order=sort_order,
            active_only=active_only
        )
        
        # Get total count
        total = await self.count(query=query, active_only=active_only)
        
        # Calculate pagination info
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            'data': [doc.to_dict() for doc in documents],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev,
                'next_page': page + 1 if has_next else None,
                'prev_page': page - 1 if has_prev else None
            }
        }
    
    async def get_or_create(
        self,
        *,
        defaults: Dict[str, Any],
        created_by: Optional[str] = None,
        **kwargs
    ) -> tuple[ModelType, bool]:
        """
        Get document atau create jika tidak ada
        
        Args:
            defaults: Default values untuk create
            created_by: User ID yang membuat
            **kwargs: Fields untuk lookup
            
        Returns:
            Tuple (document, created) dimana created=True jika document baru dibuat
        """
        # Try to get existing document
        existing = await self.model.find_one(kwargs)
        if existing:
            return existing, False
        
        # Create new document
        create_data = {**kwargs, **defaults}
        db_obj = self.model(**create_data)
        
        if hasattr(db_obj, 'set_created_by') and created_by:
            db_obj.set_created_by(created_by)
        
        await db_obj.save()
        return db_obj, True