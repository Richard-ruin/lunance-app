from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum

class MessageType(str, Enum):
    """Tipe pesan chat"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    FINANCIAL_DATA = "financial_data"
    SYSTEM = "system"

class MessageStatus(str, Enum):
    """Status pesan"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class Message(BaseModel):
    """Model untuk pesan individual"""
    id: Optional[str] = Field(default=None, alias="_id")
    conversation_id: str
    sender_id: Optional[str] = None  # None untuk pesan dari Luna
    sender_type: str = "user"  # "user" atau "luna"
    content: str
    message_type: MessageType = MessageType.TEXT
    status: MessageStatus = MessageStatus.SENT
    metadata: Optional[Dict[str, Any]] = None  # Untuk data tambahan
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Message":
        """Mengkonversi data dari MongoDB ke Message model"""
        if data is None:
            return None
        
        if "_id" in data and data["_id"] is not None:
            data["_id"] = str(data["_id"])
        elif "_id" not in data:
            data["_id"] = None
            
        return cls(**data)
    
    def to_mongo(self, exclude_id: bool = False) -> Dict[str, Any]:
        """Mengkonversi Message model ke format MongoDB"""
        data = self.dict(by_alias=True, exclude_unset=True)
        
        # Always exclude _id for updates or when explicitly requested
        if exclude_id or ("_id" in data and data["_id"] is None):
            data.pop("_id", None)
            
        return data
    
    def to_mongo_update(self) -> Dict[str, Any]:
        """Generate safe update data for MongoDB (excludes _id)"""
        data = self.dict(exclude_unset=True)
        # Remove id field completely for updates
        data.pop("id", None)
        return data

class ConversationStatus(str, Enum):
    """Status percakapan"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class Conversation(BaseModel):
    """Model untuk percakapan chat"""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    title: Optional[str] = None  # Auto-generated dari pesan pertama
    status: ConversationStatus = ConversationStatus.ACTIVE
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    message_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Conversation":
        """Mengkonversi data dari MongoDB ke Conversation model"""
        if data is None:
            return None
        
        if "_id" in data and data["_id"] is not None:
            data["_id"] = str(data["_id"])
        elif "_id" not in data:
            data["_id"] = None
            
        return cls(**data)
    
    def to_mongo(self, exclude_id: bool = False) -> Dict[str, Any]:
        """Mengkonversi Conversation model ke format MongoDB"""
        data = self.dict(by_alias=True, exclude_unset=True)
        
        # Always exclude _id for updates or when explicitly requested
        if exclude_id or ("_id" in data and data["_id"] is None):
            data.pop("_id", None)
            
        return data
    
    def to_mongo_update(self) -> Dict[str, Any]:
        """Generate safe update data for MongoDB (excludes _id and id)"""
        data = self.dict(exclude_unset=True)
        # Remove id field completely for updates
        data.pop("id", None)
        return data
    
    def update_last_message(self, message_content: str):
        """Update pesan terakhir"""
        self.last_message = message_content
        self.last_message_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.message_count += 1
        
        # Auto-generate title dari pesan pertama
        if not self.title and self.message_count == 1:
            self.title = message_content[:50] + "..." if len(message_content) > 50 else message_content

# WebSocket Message Models
class WSMessageType(str, Enum):
    """Tipe pesan WebSocket"""
    CHAT_MESSAGE = "chat_message"
    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    ERROR = "error"
    SUCCESS = "success"

class WSMessage(BaseModel):
    """Model untuk pesan WebSocket"""
    type: WSMessageType
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }