# app/routers/admin_ai.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from bson import ObjectId

from ..middleware.auth_middleware import get_current_admin_user
from ..models.ai_intent import (
    AIIntent, AIIntentCreate, AIIntentResponse, IntentPattern, IntentResponse
)
from ..database import get_database
from ..services.intent_classifier import intent_classifier
from ..utils.exceptions import CustomHTTPException

router = APIRouter(prefix="/admin/ai", tags=["AI Management (Admin)"])
logger = logging.getLogger(__name__)

@router.get("/intents", response_model=List[AIIntentResponse])
async def get_ai_intents(
    current_admin: Dict[str, Any] = Depends(get_current_admin_user),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 50,
    skip: int = 0
):
    """Get all AI intents (Admin only)"""
    try:
        db = await get_database()
        
        # Build query filter
        query_filter = {}
        if category:
            query_filter["intent_category"] = category
        if is_active is not None:
            query_filter["is_active"] = is_active
        
        intents = await db.ai_intents.find(query_filter).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        return [
            AIIntentResponse(
                _id=str(intent["_id"]),
                intent_name=intent["intent_name"],
                intent_category=intent["intent_category"],
                patterns=intent["patterns"],
                responses=intent["responses"],
                required_entities=intent["required_entities"],
                actions=intent["actions"],
                confidence_threshold=intent["confidence_threshold"],
                is_active=intent["is_active"],
                usage_count=intent.get("usage_count", 0),
                created_at=intent["created_at"],
                updated_at=intent["updated_at"]
            )
            for intent in intents
        ]
        
    except Exception as e:
        logger.error(f"Error getting AI intents: {e}")
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to get AI intents",
            error_code="GET_INTENTS_ERROR"
        )

@router.post("/intents", response_model=AIIntentResponse)
async def create_ai_intent(
    intent_data: AIIntentCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin_user)
):
    """Create new AI intent (Admin only)"""
    try:
        db = await get_database()
        
        # Check if intent name already exists
        existing = await db.ai_intents.find_one({"intent_name": intent_data.intent_name})
        if existing:
            raise CustomHTTPException(
                status_code=400,
                detail="Intent name already exists",
                error_code="INTENT_NAME_EXISTS"
            )
        
        intent = AIIntent(**intent_data.model_dump())
        
        intent_doc = intent.model_dump()
        intent_doc["created_at"] = datetime.utcnow()
        intent_doc["updated_at"] = datetime.utcnow()
        
        result = await db.ai_intents.insert_one(intent_doc)
        intent_doc["_id"] = result.inserted_id
        
        # Reload intent classifier cache
        await intent_classifier.load_intents()
        
        return AIIntentResponse(
            _id=str(intent_doc["_id"]),
            intent_name=intent_doc["intent_name"],
            intent_category=intent_doc["intent_category"],
            patterns=intent_doc["patterns"],
            responses=intent_doc["responses"],
            required_entities=intent_doc["required_entities"],
            actions=intent_doc["actions"],
            confidence_threshold=intent_doc["confidence_threshold"],
            is_active=intent_doc["is_active"],
            usage_count=intent_doc.get("usage_count", 0),
            created_at=intent_doc["created_at"],
            updated_at=intent_doc["updated_at"]
        )
        
    except CustomHTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating AI intent: {e}")
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to create AI intent",
            error_code="CREATE_INTENT_ERROR"
        )

@router.put("/intents/{intent_id}", response_model=AIIntentResponse)
async def update_ai_intent(
    intent_id: str,
    intent_data: AIIntentCreate,
    current_admin: Dict[str, Any] = Depends(get_current_admin_user)
):
    """Update AI intent (Admin only)"""
    try:
        db = await get_database()
        
        # Check if intent exists
        existing = await db.ai_intents.find_one({"_id": ObjectId(intent_id)})
        if not existing:
            raise CustomHTTPException(
                status_code=404,
                detail="Intent not found",
                error_code="INTENT_NOT_FOUND"
            )
        
        # Check if new name conflicts with other intents
        if intent_data.intent_name != existing["intent_name"]:
            name_conflict = await db.ai_intents.find_one({
                "intent_name": intent_data.intent_name,
                "_id": {"$ne": ObjectId(intent_id)}
            })
            if name_conflict:
                raise CustomHTTPException(
                    status_code=400,
                    detail="Intent name already exists",
                    error_code="INTENT_NAME_EXISTS"
                )
        
        # Update intent
        update_data = intent_data.model_dump()
        update_data["updated_at"] = datetime.utcnow()
        
        await db.ai_intents.update_one(
            {"_id": ObjectId(intent_id)},
            {"$set": update_data}
        )
        
        # Get updated intent
        updated_intent = await db.ai_intents.find_one({"_id": ObjectId(intent_id)})
        
        # Reload intent classifier cache
        await intent_classifier.load_intents()
        
        return AIIntentResponse(
            _id=str(updated_intent["_id"]),
            intent_name=updated_intent["intent_name"],
            intent_category=updated_intent["intent_category"],
            patterns=updated_intent["patterns"],
            responses=updated_intent["responses"],
            required_entities=updated_intent["required_entities"],
            actions=updated_intent["actions"],
            confidence_threshold=updated_intent["confidence_threshold"],
            is_active=updated_intent["is_active"],
            usage_count=updated_intent.get("usage_count", 0),
            created_at=updated_intent["created_at"],
            updated_at=updated_intent["updated_at"]
        )
        
    except CustomHTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating AI intent: {e}")
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to update AI intent",
            error_code="UPDATE_INTENT_ERROR"
        )

@router.delete("/intents/{intent_id}")
async def delete_ai_intent(
    intent_id: str,
    current_admin: Dict[str, Any] = Depends(get_current_admin_user)
):
    """Delete AI intent (Admin only)"""
    try:
        db = await get_database()
        
        # Check if intent exists
        existing = await db.ai_intents.find_one({"_id": ObjectId(intent_id)})
        if not existing:
            raise CustomHTTPException(
                status_code=404,
                detail="Intent not found",
                error_code="INTENT_NOT_FOUND"
            )
        
        # Delete intent
        await db.ai_intents.delete_one({"_id": ObjectId(intent_id)})
        
        # Reload intent classifier cache
        await intent_classifier.load_intents()
        
        return {"message": "AI intent deleted successfully"}
        
    except CustomHTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting AI intent: {e}")
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to delete AI intent",
            error_code="DELETE_INTENT_ERROR"
        )

@router.get("/analytics")
async def get_ai_analytics(
    current_admin: Dict[str, Any] = Depends(get_current_admin_user),
    days: int = 30
):
    """Get AI performance analytics (Admin only)"""
    try:
        db = await get_database()
        
        # Date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total messages processed
        total_messages = await db.chat_messages.count_documents({
            "created_at": {"$gte": start_date}
        })
        
        # Messages by intent
        intent_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}, "intent": {"$ne": None}}},
            {"$group": {"_id": "$intent", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        intent_stats = await db.chat_messages.aggregate(intent_pipeline).to_list(None)
        
        # Average confidence score
        confidence_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}, "confidence_score": {"$gt": 0}}},
            {"$group": {"_id": None, "avg_confidence": {"$avg": "$confidence_score"}}}
        ]
        
        confidence_result = await db.chat_messages.aggregate(confidence_pipeline).to_list(1)
        avg_confidence = confidence_result[0]["avg_confidence"] if confidence_result else 0
        
        # Processing time stats
        processing_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}, "processing_time": {"$gt": 0}}},
            {"$group": {
                "_id": None,
                "avg_time": {"$avg": "$processing_time"},
                "max_time": {"$max": "$processing_time"},
                "min_time": {"$min": "$processing_time"}
            }}
        ]
        
        processing_result = await db.chat_messages.aggregate(processing_pipeline).to_list(1)
        processing_stats = processing_result[0] if processing_result else {
            "avg_time": 0, "max_time": 0, "min_time": 0
        }
        
        # Daily message volume
        daily_pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        daily_stats = await db.chat_messages.aggregate(daily_pipeline).to_list(None)
        
        # Failed classifications (fallback responses)
        failed_classifications = await db.chat_messages.count_documents({
            "created_at": {"$gte": start_date},
            "intent": None,
            "message_type": "user"
        })
        
        return {
            "period_days": days,
            "total_messages": total_messages,
            "average_confidence": round(avg_confidence, 3),
            "failed_classifications": failed_classifications,
            "success_rate": round((1 - failed_classifications / max(total_messages, 1)) * 100, 2),
            "processing_stats": {
                "average_time_seconds": round(processing_stats["avg_time"], 3),
                "max_time_seconds": round(processing_stats["max_time"], 3),
                "min_time_seconds": round(processing_stats["min_time"], 3)
            },
            "intent_distribution": [
                {"intent": stat["_id"], "count": stat["count"]}
                for stat in intent_stats
            ],
            "daily_volume": [
                {"date": stat["_id"], "messages": stat["count"]}
                for stat in daily_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting AI analytics: {e}")
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to get AI analytics",
            error_code="GET_AI_ANALYTICS_ERROR"
        )

@router.post("/retrain")
async def retrain_ai_model(
    current_admin: Dict[str, Any] = Depends(get_current_admin_user)
):
    """Retrain AI models (Admin only)"""
    try:
        # Reload intent classifier
        await intent_classifier.load_intents()
        
        # Initialize NLP models
        from ..services.indonesian_nlp import nlp_service
        await nlp_service.initialize_models()
        
        return {
            "message": "AI models retrained successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retraining AI models: {e}")
        raise CustomHTTPException(
            status_code=500,
            detail="Failed to retrain AI models",
            error_code="RETRAIN_ERROR"
        )