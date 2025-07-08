# app/services/university_request_service.py
"""University request management service."""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from ..config.database import get_database
from ..models.university_request import (
    UniversityRequestInDB, UniversityRequestCreate, UniversityRequestUpdate,
    UniversityRequestResponse, UniversityRequestWithUser, UniversityRequestListResponse,
    UniversityRequestStats, UniversityRequestFilter, BulkUniversityRequestUpdate,
    BulkUniversityRequestResponse, UniversityRequestSummary, UniversityDataSuggestion,
    RequestStatus
)
from ..models.common import PaginatedResponse, PaginationParams
from ..services.email_service import email_service

logger = logging.getLogger(__name__)


class UniversityRequestServiceError(Exception):
    """University request service related error."""
    pass


class UniversityRequestService:
    """University request management service."""
    
    def __init__(self):
        self.collection_name = "university_requests"
    
    async def create_request(
        self,
        user_id: str,
        request_data: UniversityRequestCreate
    ) -> UniversityRequestResponse:
        """
        Create new university request.
        
        Args:
            user_id: User ID making the request
            request_data: Request creation data
            
        Returns:
            Created request response
            
        Raises:
            UniversityRequestServiceError: If creation fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check for existing pending request from same user
            existing_request = await collection.find_one({
                "user_id": ObjectId(user_id),
                "status": RequestStatus.PENDING.value
            })
            
            if existing_request:
                raise UniversityRequestServiceError("You already have a pending university request")
            
            # Check for exact duplicate request (same university, faculty, major)
            duplicate_request = await collection.find_one({
                "user_id": ObjectId(user_id),
                "university_name": request_data.university_name,
                "faculty_name": request_data.faculty_name,
                "major_name": request_data.major_name,
                "status": {"$in": [RequestStatus.PENDING.value, RequestStatus.APPROVED.value]}
            })
            
            if duplicate_request:
                raise UniversityRequestServiceError("You have already requested this university/faculty/major combination")
            
            # Create request document
            request_doc = UniversityRequestInDB(
                user_id=ObjectId(user_id),
                university_name=request_data.university_name,
                faculty_name=request_data.faculty_name,
                major_name=request_data.major_name,
                status=RequestStatus.PENDING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Insert request
            result = await collection.insert_one(
                request_doc.model_dump(by_alias=True, exclude={"id"})
            )
            
            request_id = str(result.inserted_id)
            
            # Get created request
            created_request_doc = await collection.find_one({"_id": result.inserted_id})
            created_request = UniversityRequestInDB(**created_request_doc)
            
            logger.info(f"University request created: {request_id} by user {user_id}")
            
            return UniversityRequestResponse(
                id=created_request.id,
                user_id=created_request.user_id,
                university_name=created_request.university_name,
                faculty_name=created_request.faculty_name,
                major_name=created_request.major_name,
                status=created_request.status,
                admin_notes=created_request.admin_notes,
                created_at=created_request.created_at,
                updated_at=created_request.updated_at
            )
            
        except UniversityRequestServiceError:
            raise
        except Exception as e:
            logger.error(f"Error creating university request: {e}")
            raise UniversityRequestServiceError("Failed to create university request")
    
    async def get_request_by_id(self, request_id: str) -> Optional[UniversityRequestResponse]:
        """
        Get request by ID.
        
        Args:
            request_id: Request ID
            
        Returns:
            Request response or None if not found
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            request_doc = await collection.find_one({"_id": ObjectId(request_id)})
            if not request_doc:
                return None
            
            request_obj = UniversityRequestInDB(**request_doc)
            
            return UniversityRequestResponse(
                id=request_obj.id,
                user_id=request_obj.user_id,
                university_name=request_obj.university_name,
                faculty_name=request_obj.faculty_name,
                major_name=request_obj.major_name,
                status=request_obj.status,
                admin_notes=request_obj.admin_notes,
                created_at=request_obj.created_at,
                updated_at=request_obj.updated_at
            )
            
        except Exception as e:
            logger.error(f"Error getting request {request_id}: {e}")
            return None
    
    async def list_requests(
        self,
        pagination: PaginationParams,
        filters: Optional[UniversityRequestFilter] = None
    ) -> UniversityRequestListResponse:
        """
        List requests with pagination and filters.
        
        Args:
            pagination: Pagination parameters
            filters: Request filters
            
        Returns:
            Paginated request list response
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build query
            query = {}
            
            if filters:
                # Status filter
                if filters.status:
                    query["status"] = filters.status.value
                
                # University name filter
                if filters.university_name:
                    query["university_name"] = {"$regex": filters.university_name, "$options": "i"}
                
                # Faculty name filter
                if filters.faculty_name:
                    query["faculty_name"] = {"$regex": filters.faculty_name, "$options": "i"}
                
                # Major name filter
                if filters.major_name:
                    query["major_name"] = {"$regex": filters.major_name, "$options": "i"}
                
                # User email filter (requires aggregation)
                if filters.user_email:
                    # We'll handle this in the aggregation pipeline
                    pass
                
                # Date range filter
                if filters.start_date or filters.end_date:
                    date_query = {}
                    if filters.start_date:
                        date_query["$gte"] = filters.start_date
                    if filters.end_date:
                        date_query["$lte"] = filters.end_date
                    query["created_at"] = date_query
            
            # Build aggregation pipeline for user details
            pipeline = [
                {"$match": query},
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "user_id",
                        "foreignField": "_id",
                        "as": "user"
                    }
                },
                {"$unwind": "$user"},
                {
                    "$addFields": {
                        "user_email": "$user.email",
                        "user_full_name": "$user.full_name",
                        "user_phone_number": "$user.phone_number"
                    }
                }
            ]
            
            # Add user email filter if specified
            if filters and filters.user_email:
                pipeline.append({
                    "$match": {
                        "user_email": {"$regex": filters.user_email, "$options": "i"}
                    }
                })
            
            # Get total count
            count_pipeline = pipeline + [{"$count": "total"}]
            count_result = await collection.aggregate(count_pipeline).to_list(1)
            total = count_result[0]["total"] if count_result else 0
            
            # Add sorting and pagination
            sort_field = pagination.sort_by or "created_at"
            sort_direction = DESCENDING if pagination.sort_order.value == "desc" else ASCENDING
            
            pipeline.extend([
                {"$sort": {sort_field: sort_direction}},
                {"$skip": (pagination.page - 1) * pagination.per_page},
                {"$limit": pagination.per_page}
            ])
            
            # Execute aggregation
            requests_docs = await collection.aggregate(pipeline).to_list(pagination.per_page)
            
            # Convert to response format
            requests = []
            for request_doc in requests_docs:
                requests.append(UniversityRequestWithUser(
                    id=request_doc["_id"],
                    user_id=request_doc["user_id"],
                    university_name=request_doc["university_name"],
                    faculty_name=request_doc["faculty_name"],
                    major_name=request_doc["major_name"],
                    status=RequestStatus(request_doc["status"]),
                    admin_notes=request_doc.get("admin_notes"),
                    created_at=request_doc["created_at"],
                    updated_at=request_doc["updated_at"],
                    user_email=request_doc["user_email"],
                    user_full_name=request_doc["user_full_name"],
                    user_phone_number=request_doc.get("user_phone_number")
                ))
            
            # Get status counts
            status_counts = await self._get_status_counts()
            
            return UniversityRequestListResponse(
                requests=requests,
                total=total,
                page=pagination.page,
                per_page=pagination.per_page,
                pages=(total + pagination.per_page - 1) // pagination.per_page,
                pending_count=status_counts.get("pending", 0),
                approved_count=status_counts.get("approved", 0),
                rejected_count=status_counts.get("rejected", 0)
            )
            
        except Exception as e:
            logger.error(f"Error listing requests: {e}")
            raise UniversityRequestServiceError("Failed to list requests")
    
    async def update_request(
        self,
        request_id: str,
        update_data: UniversityRequestUpdate,
        admin_user_id: str
    ) -> Optional[UniversityRequestResponse]:
        """
        Update request (admin only).
        
        Args:
            request_id: Request ID
            update_data: Update data
            admin_user_id: Admin user performing the update
            
        Returns:
            Updated request response
            
        Raises:
            UniversityRequestServiceError: If update fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check if request exists
            existing_request = await collection.find_one({"_id": ObjectId(request_id)})
            if not existing_request:
                raise UniversityRequestServiceError("Request not found")
            
            request_obj = UniversityRequestInDB(**existing_request)
            
            # Prepare update data
            update_fields = {}
            for field, value in update_data.model_dump(exclude_none=True).items():
                if value is not None:
                    update_fields[field] = value
            
            if not update_fields:
                # No updates provided
                return await self.get_request_by_id(request_id)
            
            # Add updated timestamp
            update_fields["updated_at"] = datetime.utcnow()
            
            # Store old status for email notification
            old_status = request_obj.status
            new_status = update_fields.get("status", old_status)
            
            # Update request
            result = await collection.update_one(
                {"_id": ObjectId(request_id)},
                {"$set": update_fields}
            )
            
            if result.modified_count == 0:
                raise UniversityRequestServiceError("Failed to update request")
            
            # Send email notification if status changed
            if old_status != new_status and new_status in [RequestStatus.APPROVED, RequestStatus.REJECTED]:
                await self._send_status_change_email(request_obj, new_status, update_fields.get("admin_notes"))
            
            logger.info(f"Request {request_id} updated by admin {admin_user_id}")
            
            return await self.get_request_by_id(request_id)
            
        except UniversityRequestServiceError:
            raise
        except Exception as e:
            logger.error(f"Error updating request {request_id}: {e}")
            raise UniversityRequestServiceError("Failed to update request")
    
    async def bulk_update_requests(
        self,
        bulk_update: BulkUniversityRequestUpdate,
        admin_user_id: str
    ) -> BulkUniversityRequestResponse:
        """
        Bulk update multiple requests.
        
        Args:
            bulk_update: Bulk update data
            admin_user_id: Admin user performing the update
            
        Returns:
            Bulk update response
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Convert request IDs to ObjectIds
            object_ids = [ObjectId(str(req_id)) for req_id in bulk_update.request_ids]
            
            # Get existing requests for email notifications
            existing_requests = await collection.find(
                {"_id": {"$in": object_ids}}
            ).to_list(length=len(object_ids))
            
            # Prepare update data
            update_fields = {
                "status": bulk_update.status.value,
                "updated_at": datetime.utcnow()
            }
            
            if bulk_update.admin_notes:
                update_fields["admin_notes"] = bulk_update.admin_notes
            
            # Perform bulk update
            result = await collection.update_many(
                {"_id": {"$in": object_ids}},
                {"$set": update_fields}
            )
            
            # Send email notifications for status changes
            for request_doc in existing_requests:
                request_obj = UniversityRequestInDB(**request_doc)
                if request_obj.status != bulk_update.status:
                    await self._send_status_change_email(
                        request_obj, 
                        bulk_update.status, 
                        bulk_update.admin_notes
                    )
            
            # Get updated requests
            updated_requests_docs = await collection.find(
                {"_id": {"$in": object_ids}}
            ).to_list(length=len(object_ids))
            
            updated_requests = []
            for request_doc in updated_requests_docs:
                request_obj = UniversityRequestInDB(**request_doc)
                updated_requests.append(UniversityRequestResponse(
                    id=request_obj.id,
                    user_id=request_obj.user_id,
                    university_name=request_obj.university_name,
                    faculty_name=request_obj.faculty_name,
                    major_name=request_obj.major_name,
                    status=request_obj.status,
                    admin_notes=request_obj.admin_notes,
                    created_at=request_obj.created_at,
                    updated_at=request_obj.updated_at
                ))
            
            logger.info(f"Bulk updated {result.modified_count} requests by admin {admin_user_id}")
            
            return BulkUniversityRequestResponse(
                updated_count=result.modified_count,
                failed_count=len(object_ids) - result.modified_count,
                updated_requests=updated_requests,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            return BulkUniversityRequestResponse(
                updated_count=0,
                failed_count=len(bulk_update.request_ids),
                updated_requests=[],
                errors=[str(e)]
            )
    
    async def get_user_requests(
        self,
        user_id: str,
        pagination: PaginationParams
    ) -> PaginatedResponse[UniversityRequestResponse]:
        """
        Get requests for specific user.
        
        Args:
            user_id: User ID
            pagination: Pagination parameters
            
        Returns:
            Paginated user requests
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build query for user requests
            query = {"user_id": ObjectId(user_id)}
            
            # Get total count
            total = await collection.count_documents(query)
            
            # Build sort
            sort_field = pagination.sort_by or "created_at"
            sort_direction = DESCENDING if pagination.sort_order.value == "desc" else ASCENDING
            
            # Get paginated results
            skip = (pagination.page - 1) * pagination.per_page
            cursor = collection.find(query).sort(sort_field, sort_direction)
            cursor = cursor.skip(skip).limit(pagination.per_page)
            
            requests_docs = await cursor.to_list(length=pagination.per_page)
            
            # Convert to response format
            requests = []
            for request_doc in requests_docs:
                request_obj = UniversityRequestInDB(**request_doc)
                requests.append(UniversityRequestResponse(
                    id=request_obj.id,
                    user_id=request_obj.user_id,
                    university_name=request_obj.university_name,
                    faculty_name=request_obj.faculty_name,
                    major_name=request_obj.major_name,
                    status=request_obj.status,
                    admin_notes=request_obj.admin_notes,
                    created_at=request_obj.created_at,
                    updated_at=request_obj.updated_at
                ))
            
            return PaginatedResponse.create(
                items=requests,
                total=total,
                page=pagination.page,
                per_page=pagination.per_page
            )
            
        except Exception as e:
            logger.error(f"Error getting user requests for {user_id}: {e}")
            raise UniversityRequestServiceError("Failed to get user requests")
    
    async def get_request_stats(self) -> UniversityRequestStats:
        """
        Get request statistics.
        
        Returns:
            Request statistics
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Total requests
            total_requests = await collection.count_documents({})
            
            # Status counts
            status_counts = await self._get_status_counts()
            
            # Time-based counts
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=7)
            month_start = today_start - timedelta(days=30)
            
            requests_today = await collection.count_documents({
                "created_at": {"$gte": today_start}
            })
            
            requests_this_week = await collection.count_documents({
                "created_at": {"$gte": week_start}
            })
            
            requests_this_month = await collection.count_documents({
                "created_at": {"$gte": month_start}
            })
            
            return UniversityRequestStats(
                total_requests=total_requests,
                pending_requests=status_counts.get("pending", 0),
                approved_requests=status_counts.get("approved", 0),
                rejected_requests=status_counts.get("rejected", 0),
                requests_today=requests_today,
                requests_this_week=requests_this_week,
                requests_this_month=requests_this_month
            )
            
        except Exception as e:
            logger.error(f"Error getting request stats: {e}")
            return UniversityRequestStats()
    
    async def get_request_summary(self) -> UniversityRequestSummary:
        """
        Get request summary for admin dashboard.
        
        Returns:
            Request summary
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Get stats
            stats = await self.get_request_stats()
            
            # Recent requests (last 10)
            recent_pipeline = [
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "user_id",
                        "foreignField": "_id",
                        "as": "user"
                    }
                },
                {"$unwind": "$user"},
                {
                    "$addFields": {
                        "user_email": "$user.email",
                        "user_full_name": "$user.full_name",
                        "user_phone_number": "$user.phone_number"
                    }
                },
                {"$sort": {"created_at": -1}},
                {"$limit": 10}
            ]
            
            recent_docs = await collection.aggregate(recent_pipeline).to_list(10)
            recent_requests = []
            
            for doc in recent_docs:
                recent_requests.append(UniversityRequestWithUser(
                    id=doc["_id"],
                    user_id=doc["user_id"],
                    university_name=doc["university_name"],
                    faculty_name=doc["faculty_name"],
                    major_name=doc["major_name"],
                    status=RequestStatus(doc["status"]),
                    admin_notes=doc.get("admin_notes"),
                    created_at=doc["created_at"],
                    updated_at=doc["updated_at"],
                    user_email=doc["user_email"],
                    user_full_name=doc["user_full_name"],
                    user_phone_number=doc.get("user_phone_number")
                ))
            
            # Pending requests (last 5)
            pending_docs = await collection.aggregate([
                {"$match": {"status": RequestStatus.PENDING.value}},
                *recent_pipeline[1:],  # Skip the lookup, it's already included
                {"$limit": 5}
            ]).to_list(5)
            
            pending_requests = []
            for doc in pending_docs:
                pending_requests.append(UniversityRequestWithUser(
                    id=doc["_id"],
                    user_id=doc["user_id"],
                    university_name=doc["university_name"],
                    faculty_name=doc["faculty_name"],
                    major_name=doc["major_name"],
                    status=RequestStatus(doc["status"]),
                    admin_notes=doc.get("admin_notes"),
                    created_at=doc["created_at"],
                    updated_at=doc["updated_at"],
                    user_email=doc["user_email"],
                    user_full_name=doc["user_full_name"],
                    user_phone_number=doc.get("user_phone_number")
                ))
            
            return UniversityRequestSummary(
                stats=stats,
                recent_requests=recent_requests,
                pending_requests=pending_requests
            )
            
        except Exception as e:
            logger.error(f"Error getting request summary: {e}")
            raise UniversityRequestServiceError("Failed to get request summary")
    
    async def get_university_suggestions(self, limit: int = 20) -> List[UniversityDataSuggestion]:
        """
        Get university data suggestions based on requests.
        
        Args:
            limit: Maximum suggestions to return
            
        Returns:
            List of university suggestions
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Aggregate request data to suggest new universities
            pipeline = [
                {
                    "$group": {
                        "_id": {
                            "university_name": "$university_name",
                            "faculty_name": "$faculty_name",
                            "major_name": "$major_name"
                        },
                        "request_count": {"$sum": 1},
                        "first_requested": {"$min": "$created_at"},
                        "last_requested": {"$max": "$created_at"}
                    }
                },
                {"$sort": {"request_count": -1, "last_requested": -1}},
                {"$limit": limit}
            ]
            
            suggestions_docs = await collection.aggregate(pipeline).to_list(limit)
            
            suggestions = []
            for doc in suggestions_docs:
                suggestions.append(UniversityDataSuggestion(
                    university_name=doc["_id"]["university_name"],
                    faculty_name=doc["_id"]["faculty_name"],
                    major_name=doc["_id"]["major_name"],
                    request_count=doc["request_count"],
                    first_requested=doc["first_requested"],
                    last_requested=doc["last_requested"]
                ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting university suggestions: {e}")
            return []
    
    async def delete_request(self, request_id: str, admin_user_id: str) -> bool:
        """
        Delete request (admin only).
        
        Args:
            request_id: Request ID
            admin_user_id: Admin user performing the deletion
            
        Returns:
            True if successful
            
        Raises:
            UniversityRequestServiceError: If deletion fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check if request exists
            existing_request = await collection.find_one({"_id": ObjectId(request_id)})
            if not existing_request:
                raise UniversityRequestServiceError("Request not found")
            
            # Delete request
            result = await collection.delete_one({"_id": ObjectId(request_id)})
            
            if result.deleted_count == 0:
                raise UniversityRequestServiceError("Failed to delete request")
            
            logger.info(f"Request {request_id} deleted by admin {admin_user_id}")
            return True
            
        except UniversityRequestServiceError:
            raise
        except Exception as e:
            logger.error(f"Error deleting request {request_id}: {e}")
            raise UniversityRequestServiceError("Failed to delete request")
    
    async def _get_status_counts(self) -> Dict[str, int]:
        """
        Get request counts by status.
        
        Returns:
            Dictionary with status counts
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            pipeline = [
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            status_docs = await collection.aggregate(pipeline).to_list(10)
            
            status_counts = {}
            for doc in status_docs:
                status_counts[doc["_id"]] = doc["count"]
            
            return status_counts
            
        except Exception as e:
            logger.error(f"Error getting status counts: {e}")
            return {}
    
    async def _send_status_change_email(
        self,
        request_obj: UniversityRequestInDB,
        new_status: RequestStatus,
        admin_notes: Optional[str] = None
    ) -> bool:
        """
        Send email notification for status change.
        
        Args:
            request_obj: Request object
            new_status: New status
            admin_notes: Admin notes
            
        Returns:
            True if email sent successfully
        """
        try:
            # Get user email
            db = await get_database()
            users_collection = db.users
            
            user_doc = await users_collection.find_one({"_id": request_obj.user_id})
            if not user_doc:
                logger.warning(f"User not found for request notification: {request_obj.user_id}")
                return False
            
            user_email = user_doc["email"]
            user_name = user_doc["full_name"]
            
            # Prepare email content based on status
            if new_status == RequestStatus.APPROVED:
                subject = "🎉 Permintaan Universitas Anda Disetujui - Lunance"
                status_message = "disetujui"
                status_color = "#28a745"
                action_message = "Data universitas, fakultas, dan jurusan yang Anda minta telah ditambahkan ke sistem dan dapat Anda pilih saat mengupdate profil."
            else:  # REJECTED
                subject = "📝 Permintaan Universitas Anda Ditinjau - Lunance"
                status_message = "ditinjau ulang"
                status_color = "#dc3545"
                action_message = "Silakan periksa catatan admin di bawah untuk informasi lebih lanjut dan ajukan permintaan baru jika diperlukan."
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Status Permintaan Universitas</title>
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .status-badge {{
                        display: inline-block;
                        background-color: {status_color};
                        color: white;
                        padding: 12px 25px;
                        border-radius: 25px;
                        font-weight: bold;
                        margin: 20px 0;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    }}
                    .request-details {{
                        background-color: #f8f9fa;
                        border-radius: 10px;
                        padding: 25px;
                        margin: 25px 0;
                        border-left: 5px solid #667eea;
                    }}
                    .admin-notes {{
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        border-radius: 10px;
                        padding: 20px;
                        margin: 25px 0;
                        border-left: 5px solid #ffc107;
                    }}
                    .footer {{
                        background-color: #f8f9fa;
                        padding: 25px;
                        text-align: center;
                        color: #6c757d;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🌙 Lunance</h1>
                        <h2>Status Permintaan Universitas</h2>
                    </div>
                    <div class="content">
                        <h2>Hai {user_name}!</h2>
                        <p>Permintaan universitas Anda telah <strong>{status_message}</strong>.</p>
                        
                        <div class="status-badge">
                            Status: {status_message.upper()}
                        </div>
                        
                        <div class="request-details">
                            <h3>📋 Detail Permintaan:</h3>
                            <p><strong>🏫 Universitas:</strong> {request_obj.university_name}</p>
                            <p><strong>🎓 Fakultas:</strong> {request_obj.faculty_name}</p>
                            <p><strong>📚 Jurusan:</strong> {request_obj.major_name}</p>
                            <p><strong>📅 Tanggal Permintaan:</strong> {request_obj.created_at.strftime('%d %B %Y, %H:%M')}</p>
                        </div>
                        
                        <p>{action_message}</p>
            """
            
            # Add admin notes if available
            if admin_notes:
                html_content += f"""
                        <div class="admin-notes">
                            <h3>💬 Catatan Admin:</h3>
                            <p>{admin_notes}</p>
                        </div>
                """
            
            html_content += """
                        <p>Jika Anda memiliki pertanyaan, silakan hubungi tim support kami.</p>
                    </div>
                    <div class="footer">
                        <p><strong>© 2024 Lunance App</strong> - Smart Personal Finance Management</p>
                        <p>Email ini dikirim secara otomatis, mohon jangan balas.</p>
                        <p>Butuh bantuan? Hubungi support@lunance.app</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email
            email_sent = await email_service.send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content
            )
            
            if email_sent:
                logger.info(f"Status change email sent to {user_email} for request {request_obj.id}")
            else:
                logger.warning(f"Failed to send status change email to {user_email}")
            
            return email_sent
            
        except Exception as e:
            logger.error(f"Error sending status change email: {e}")
            return False


# Global university request service instance
university_request_service = UniversityRequestService()