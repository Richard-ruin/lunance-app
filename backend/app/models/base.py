from datetime import datetime
from bson import ObjectId
from typing import Optional, Dict, Any, List
from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue
from pydantic._internal._model_construction import complete_model_class
from app.config.database import get_db

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        def validate_from_str(input_value: str) -> ObjectId:
            if not ObjectId.is_valid(input_value):
                raise ValueError('Invalid ObjectId')
            return ObjectId(input_value)

        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.no_info_plain_validator_function(validate_from_str),
        ])

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: Any
    ) -> JsonSchemaValue:
        return {'type': 'string'}

class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='_id')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def save(self, collection_name: str) -> 'BaseModel':
        """Save document to MongoDB"""
        db = get_db()
        collection = db[collection_name]
        
        self.updated_at = datetime.utcnow()
        doc_dict = self.model_dump(by_alias=True, exclude_unset=True)
        
        if self.id:
            # Update existing document
            result = collection.update_one(
                {'_id': self.id},
                {'$set': doc_dict}
            )
        else:
            # Create new document
            result = collection.insert_one(doc_dict)
            self.id = result.inserted_id
            
        return self

    @classmethod
    def find_by_id(cls, collection_name: str, doc_id: str) -> Optional['BaseModel']:
        """Find document by ID"""
        try:
            db = get_db()
            collection = db[collection_name]
            
            doc = collection.find_one({'_id': ObjectId(doc_id)})
            if doc:
                return cls(**doc)
            return None
        except Exception:
            return None

    @classmethod
    def find_all(cls, collection_name: str, filter_dict: Dict[str, Any] = None, 
                 limit: int = None, skip: int = None, sort: List[tuple] = None) -> List['BaseModel']:
        """Find all documents matching filter"""
        try:
            db = get_db()
            collection = db[collection_name]
            
            cursor = collection.find(filter_dict or {})
            
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
                
            return [cls(**doc) for doc in cursor]
        except Exception:
            return []

    @classmethod
    def count_documents(cls, collection_name: str, filter_dict: Dict[str, Any] = None) -> int:
        """Count documents matching filter"""
        try:
            db = get_db()
            collection = db[collection_name]
            return collection.count_documents(filter_dict or {})
        except Exception:
            return 0

    def delete(self, collection_name: str) -> bool:
        """Delete document from MongoDB"""
        if not self.id:
            return False
            
        try:
            db = get_db()
            collection = db[collection_name]
            
            result = collection.delete_one({'_id': self.id})
            return result.deleted_count > 0
        except Exception:
            return False