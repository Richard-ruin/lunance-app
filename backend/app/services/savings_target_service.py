# app/services/savings_target_service.py
"""Savings target management service with projections and analytics."""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import logging
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from ..config.database import get_database
from ..models.savings_target import (
    SavingsTargetInDB, SavingsTargetCreate, SavingsTargetUpdate, SavingsTargetResponse,
    SavingsTargetWithProjection, SavingsContribution, SavingsWithdrawal,
    SavingsTargetSummary, SavingsTargetHistory, SavingsTargetAnalytics
)
from ..models.common import PaginatedResponse, PaginationParams

logger = logging.getLogger(__name__)


class SavingsTargetServiceError(Exception):
    """Savings target service related error."""
    pass


class SavingsTargetService:
    """Savings target management service."""
    
    def __init__(self):
        self.collection_name = "savings_targets"
        self.history_collection_name = "savings_target_history"
    
    async def create_savings_target(
        self,
        user_id: str,
        target_data: SavingsTargetCreate
    ) -> SavingsTargetResponse:
        """
        Create new savings target.
        
        Args:
            user_id: User ID
            target_data: Savings target creation data
            
        Returns:
            Created savings target response
            
        Raises:
            SavingsTargetServiceError: If creation fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check for duplicate target name for the same user
            existing_target = await collection.find_one({
                "user_id": user_id,
                "target_name": {"$regex": f"^{target_data.target_name}$", "$options": "i"}
            })
            
            if existing_target:
                raise SavingsTargetServiceError("A savings target with this name already exists")
            
            # Create savings target document
            target_doc = SavingsTargetInDB(
                user_id=user_id,
                target_name=target_data.target_name,
                target_amount=target_data.target_amount,
                current_amount=target_data.current_amount or 0.0,
                target_date=target_data.target_date,
                is_achieved=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Insert savings target
            result = await collection.insert_one(
                target_doc.model_dump(by_alias=True, exclude={"id"})
            )
            
            target_id = str(result.inserted_id)
            
            # Create initial history entry if there's an initial amount
            if target_data.current_amount and target_data.current_amount > 0:
                await self._add_history_entry(
                    target_id,
                    "initial_deposit",
                    target_data.current_amount,
                    0.0,
                    target_data.current_amount,
                    "Initial savings amount"
                )
            
            # Get created target with calculations
            created_target = await self.get_savings_target_by_id(target_id, user_id)
            
            logger.info(f"Savings target created: {target_id} by user {user_id}")
            
            return created_target
            
        except SavingsTargetServiceError:
            raise
        except Exception as e:
            logger.error(f"Error creating savings target: {e}")
            raise SavingsTargetServiceError("Failed to create savings target")
    
    async def get_savings_target_by_id(
        self,
        target_id: str,
        user_id: str
    ) -> Optional[SavingsTargetResponse]:
        """
        Get savings target by ID with calculations.
        
        Args:
            target_id: Savings target ID
            user_id: User ID for access control
            
        Returns:
            Savings target response with calculations
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            target_doc = await collection.find_one({
                "_id": ObjectId(target_id),
                "user_id": user_id
            })
            
            if not target_doc:
                return None
            
            target = SavingsTargetInDB(**target_doc)
            
            # Calculate progress and days remaining
            progress_percentage = (target.current_amount / target.target_amount * 100) if target.target_amount > 0 else 0
            days_remaining = (target.target_date - date.today()).days
            
            return SavingsTargetResponse(
                id=str(target.id),
                user_id=target.user_id,
                target_name=target.target_name,
                target_amount=target.target_amount,
                current_amount=target.current_amount,
                target_date=target.target_date,
                is_achieved=target.is_achieved,
                progress_percentage=round(progress_percentage, 2),
                days_remaining=max(0, days_remaining),
                created_at=target.created_at,
                updated_at=target.updated_at
            )
            
        except Exception as e:
            logger.error(f"Error getting savings target {target_id}: {e}")
            return None
    
    async def get_savings_target_with_projection(
        self,
        target_id: str,
        user_id: str
    ) -> Optional[SavingsTargetWithProjection]:
        """
        Get savings target with projection calculations.
        
        Args:
            target_id: Savings target ID
            user_id: User ID for access control
            
        Returns:
            Savings target with projections
        """
        try:
            # Get basic target data
            target = await self.get_savings_target_by_id(target_id, user_id)
            if not target:
                return None
            
            # Calculate projections
            remaining_amount = target.target_amount - target.current_amount
            days_remaining = max(1, target.days_remaining)  # Avoid division by zero
            
            # Calculate required savings rates
            daily_target = remaining_amount / days_remaining
            weekly_target = daily_target * 7
            monthly_target = daily_target * 30.44  # Average days per month
            
            # Calculate if on track (based on time elapsed vs progress)
            total_days = (target.target_date - target.created_at.date()).days
            elapsed_days = total_days - days_remaining
            expected_progress = (elapsed_days / total_days * 100) if total_days > 0 else 0
            is_on_track = target.progress_percentage >= expected_progress * 0.9  # 90% tolerance
            
            # Estimate completion date based on current savings rate
            projected_completion_date = None
            if target.current_amount > 0:
                # Calculate average savings rate from history
                savings_rate = await self._calculate_average_savings_rate(target_id)
                if savings_rate > 0:
                    days_to_complete = remaining_amount / savings_rate
                    projected_completion_date = date.today() + timedelta(days=days_to_complete)
            
            return SavingsTargetWithProjection(
                id=target.id,
                user_id=target.user_id,
                target_name=target.target_name,
                target_amount=target.target_amount,
                current_amount=target.current_amount,
                target_date=target.target_date,
                is_achieved=target.is_achieved,
                progress_percentage=target.progress_percentage,
                days_remaining=target.days_remaining,
                created_at=target.created_at,
                updated_at=target.updated_at,
                monthly_target=round(monthly_target, 2),
                weekly_target=round(weekly_target, 2),
                daily_target=round(daily_target, 2),
                projected_completion_date=projected_completion_date,
                is_on_track=is_on_track,
                savings_rate_needed=round(monthly_target, 2)
            )
            
        except Exception as e:
            logger.error(f"Error getting savings target with projection {target_id}: {e}")
            return None
    
    async def list_savings_targets(
        self,
        user_id: str,
        pagination: PaginationParams,
        is_achieved: Optional[bool] = None
    ) -> PaginatedResponse[SavingsTargetResponse]:
        """
        List user's savings targets.
        
        Args:
            user_id: User ID
            pagination: Pagination parameters
            is_achieved: Filter by achievement status
            
        Returns:
            Paginated savings targets response
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build query
            query = {"user_id": user_id}
            
            if is_achieved is not None:
                query["is_achieved"] = is_achieved
            
            # Get total count
            total = await collection.count_documents(query)
            
            # Build sort
            sort_field = pagination.sort_by or "created_at"
            sort_direction = DESCENDING if pagination.sort_order.value == "desc" else ASCENDING
            
            # Get paginated results
            skip = (pagination.page - 1) * pagination.per_page
            cursor = collection.find(query).sort(sort_field, sort_direction)
            cursor = cursor.skip(skip).limit(pagination.per_page)
            
            targets_docs = await cursor.to_list(length=pagination.per_page)
            
            # Convert to response format with calculations
            targets = []
            for target_doc in targets_docs:
                target = SavingsTargetInDB(**target_doc)
                
                # Calculate progress and days remaining
                progress_percentage = (target.current_amount / target.target_amount * 100) if target.target_amount > 0 else 0
                days_remaining = (target.target_date - date.today()).days
                
                targets.append(SavingsTargetResponse(
                    id=str(target.id),
                    user_id=target.user_id,
                    target_name=target.target_name,
                    target_amount=target.target_amount,
                    current_amount=target.current_amount,
                    target_date=target.target_date,
                    is_achieved=target.is_achieved,
                    progress_percentage=round(progress_percentage, 2),
                    days_remaining=max(0, days_remaining),
                    created_at=target.created_at,
                    updated_at=target.updated_at
                ))
            
            return PaginatedResponse.create(
                items=targets,
                total=total,
                page=pagination.page,
                per_page=pagination.per_page
            )
            
        except Exception as e:
            logger.error(f"Error listing savings targets: {e}")
            raise SavingsTargetServiceError("Failed to list savings targets")
    
    async def update_savings_target(
        self,
        target_id: str,
        user_id: str,
        update_data: SavingsTargetUpdate
    ) -> Optional[SavingsTargetResponse]:
        """
        Update savings target.
        
        Args:
            target_id: Savings target ID
            user_id: User ID
            update_data: Update data
            
        Returns:
            Updated savings target response
            
        Raises:
            SavingsTargetServiceError: If update fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Check if target exists and belongs to user
            existing_target = await collection.find_one({
                "_id": ObjectId(target_id),
                "user_id": user_id
            })
            
            if not existing_target:
                raise SavingsTargetServiceError("Savings target not found")
            
            target = SavingsTargetInDB(**existing_target)
            
            # Prepare update data
            update_fields = {}
            for field, value in update_data.model_dump(exclude_none=True).items():
                if value is not None:
                    update_fields[field] = value
            
            if not update_fields:
                # No updates provided, return current target
                return await self.get_savings_target_by_id(target_id, user_id)
            
            # Check for name conflicts if name is being updated
            if "target_name" in update_fields:
                name_conflict = await collection.find_one({
                    "_id": {"$ne": ObjectId(target_id)},
                    "user_id": user_id,
                    "target_name": {"$regex": f"^{update_fields['target_name']}$", "$options": "i"}
                })
                if name_conflict:
                    raise SavingsTargetServiceError("A savings target with this name already exists")
            
            # Check achievement status if current_amount is being updated
            if "current_amount" in update_fields:
                new_current_amount = update_fields["current_amount"]
                target_amount = update_fields.get("target_amount", target.target_amount)
                
                # Record the change in history
                amount_change = new_current_amount - target.current_amount
                if amount_change != 0:
                    action = "contribution" if amount_change > 0 else "withdrawal"
                    description = f"Manual adjustment: {abs(amount_change)}"
                    
                    await self._add_history_entry(
                        target_id,
                        action,
                        abs(amount_change),
                        target.current_amount,
                        new_current_amount,
                        description
                    )
                
                # Update achievement status
                if new_current_amount >= target_amount and not target.is_achieved:
                    update_fields["is_achieved"] = True
                    await self._add_history_entry(
                        target_id,
                        "achievement",
                        0,
                        new_current_amount,
                        new_current_amount,
                        "Savings target achieved!"
                    )
                elif new_current_amount < target_amount and target.is_achieved:
                    update_fields["is_achieved"] = False
            
            # Add updated timestamp
            update_fields["updated_at"] = datetime.utcnow()
            
            # Update target
            result = await collection.update_one(
                {"_id": ObjectId(target_id)},
                {"$set": update_fields}
            )
            
            if result.modified_count == 0:
                raise SavingsTargetServiceError("Failed to update savings target")
            
            logger.info(f"Savings target updated: {target_id} by user {user_id}")
            
            return await self.get_savings_target_by_id(target_id, user_id)
            
        except SavingsTargetServiceError:
            raise
        except Exception as e:
            logger.error(f"Error updating savings target {target_id}: {e}")
            raise SavingsTargetServiceError("Failed to update savings target")
    
    async def delete_savings_target(
        self,
        target_id: str,
        user_id: str
    ) -> bool:
        """
        Delete savings target and its history.
        
        Args:
            target_id: Savings target ID
            user_id: User ID
            
        Returns:
            True if successful
            
        Raises:
            SavingsTargetServiceError: If deletion fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            history_collection = db[self.history_collection_name]
            
            # Delete target (only if belongs to user)
            result = await collection.delete_one({
                "_id": ObjectId(target_id),
                "user_id": user_id
            })
            
            if result.deleted_count == 0:
                raise SavingsTargetServiceError("Savings target not found")
            
            # Delete associated history
            await history_collection.delete_many({"savings_target_id": target_id})
            
            logger.info(f"Savings target deleted: {target_id} by user {user_id}")
            return True
            
        except SavingsTargetServiceError:
            raise
        except Exception as e:
            logger.error(f"Error deleting savings target {target_id}: {e}")
            raise SavingsTargetServiceError("Failed to delete savings target")
    
    async def add_contribution(
        self,
        target_id: str,
        user_id: str,
        contribution: SavingsContribution
    ) -> Optional[SavingsTargetResponse]:
        """
        Add contribution to savings target.
        
        Args:
            target_id: Savings target ID
            user_id: User ID
            contribution: Contribution data
            
        Returns:
            Updated savings target response
            
        Raises:
            SavingsTargetServiceError: If contribution fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Get current target
            target_doc = await collection.find_one({
                "_id": ObjectId(target_id),
                "user_id": user_id
            })
            
            if not target_doc:
                raise SavingsTargetServiceError("Savings target not found")
            
            target = SavingsTargetInDB(**target_doc)
            
            # Calculate new amount
            old_amount = target.current_amount
            new_amount = old_amount + contribution.amount
            
            # Check if target is achieved
            is_achieved = new_amount >= target.target_amount
            
            # Update target
            update_fields = {
                "current_amount": new_amount,
                "updated_at": datetime.utcnow()
            }
            
            if is_achieved and not target.is_achieved:
                update_fields["is_achieved"] = True
            
            result = await collection.update_one(
                {"_id": ObjectId(target_id)},
                {"$set": update_fields}
            )
            
            if result.modified_count == 0:
                raise SavingsTargetServiceError("Failed to add contribution")
            
            # Add history entry
            await self._add_history_entry(
                target_id,
                "contribution",
                contribution.amount,
                old_amount,
                new_amount,
                contribution.description or "Contribution added"
            )
            
            # Add achievement history if target is achieved
            if is_achieved and not target.is_achieved:
                await self._add_history_entry(
                    target_id,
                    "achievement",
                    0,
                    new_amount,
                    new_amount,
                    "Savings target achieved!"
                )
            
            logger.info(f"Contribution added to savings target {target_id}: {contribution.amount}")
            
            return await self.get_savings_target_by_id(target_id, user_id)
            
        except SavingsTargetServiceError:
            raise
        except Exception as e:
            logger.error(f"Error adding contribution to target {target_id}: {e}")
            raise SavingsTargetServiceError("Failed to add contribution")
    
    async def add_withdrawal(
        self,
        target_id: str,
        user_id: str,
        withdrawal: SavingsWithdrawal
    ) -> Optional[SavingsTargetResponse]:
        """
        Add withdrawal from savings target.
        
        Args:
            target_id: Savings target ID
            user_id: User ID
            withdrawal: Withdrawal data
            
        Returns:
            Updated savings target response
            
        Raises:
            SavingsTargetServiceError: If withdrawal fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Get current target
            target_doc = await collection.find_one({
                "_id": ObjectId(target_id),
                "user_id": user_id
            })
            
            if not target_doc:
                raise SavingsTargetServiceError("Savings target not found")
            
            target = SavingsTargetInDB(**target_doc)
            
            # Check if withdrawal amount is valid
            if withdrawal.amount > target.current_amount:
                raise SavingsTargetServiceError("Withdrawal amount cannot exceed current savings")
            
            # Calculate new amount
            old_amount = target.current_amount
            new_amount = old_amount - withdrawal.amount
            
            # Update achievement status if necessary
            is_achieved = new_amount >= target.target_amount
            
            # Update target
            update_fields = {
                "current_amount": new_amount,
                "updated_at": datetime.utcnow()
            }
            
            if not is_achieved and target.is_achieved:
                update_fields["is_achieved"] = False
            
            result = await collection.update_one(
                {"_id": ObjectId(target_id)},
                {"$set": update_fields}
            )
            
            if result.modified_count == 0:
                raise SavingsTargetServiceError("Failed to process withdrawal")
            
            # Add history entry
            await self._add_history_entry(
                target_id,
                "withdrawal",
                withdrawal.amount,
                old_amount,
                new_amount,
                withdrawal.description or "Withdrawal processed"
            )
            
            logger.info(f"Withdrawal processed from savings target {target_id}: {withdrawal.amount}")
            
            return await self.get_savings_target_by_id(target_id, user_id)
            
        except SavingsTargetServiceError:
            raise
        except Exception as e:
            logger.error(f"Error processing withdrawal from target {target_id}: {e}")
            raise SavingsTargetServiceError("Failed to process withdrawal")
    
    async def get_savings_target_history(
        self,
        target_id: str,
        user_id: str,
        pagination: PaginationParams
    ) -> PaginatedResponse[SavingsTargetHistory]:
        """
        Get savings target transaction history.
        
        Args:
            target_id: Savings target ID
            user_id: User ID for access control
            pagination: Pagination parameters
            
        Returns:
            Paginated history response
        """
        try:
            db = await get_database()
            targets_collection = db[self.collection_name]
            history_collection = db[self.history_collection_name]
            
            # Verify user owns the target
            target_exists = await targets_collection.find_one({
                "_id": ObjectId(target_id),
                "user_id": user_id
            })
            
            if not target_exists:
                raise SavingsTargetServiceError("Savings target not found")
            
            # Build query
            query = {"savings_target_id": target_id}
            
            # Get total count
            total = await history_collection.count_documents(query)
            
            # Build sort (most recent first)
            sort_field = pagination.sort_by or "created_at"
            sort_direction = DESCENDING if pagination.sort_order.value == "desc" else ASCENDING
            
            # Get paginated results
            skip = (pagination.page - 1) * pagination.per_page
            cursor = history_collection.find(query).sort(sort_field, sort_direction)
            cursor = cursor.skip(skip).limit(pagination.per_page)
            
            history_docs = await cursor.to_list(length=pagination.per_page)
            
            # Convert to response format
            history_entries = []
            for history_doc in history_docs:
                history_entries.append(SavingsTargetHistory(
                    id=str(history_doc["_id"]),
                    savings_target_id=history_doc["savings_target_id"],
                    action=history_doc["action"],
                    amount=history_doc["amount"],
                    balance_before=history_doc["balance_before"],
                    balance_after=history_doc["balance_after"],
                    description=history_doc.get("description"),
                    created_at=history_doc["created_at"]
                ))
            
            return PaginatedResponse.create(
                items=history_entries,
                total=total,
                page=pagination.page,
                per_page=pagination.per_page
            )
            
        except SavingsTargetServiceError:
            raise
        except Exception as e:
            logger.error(f"Error getting savings target history {target_id}: {e}")
            raise SavingsTargetServiceError("Failed to get savings target history")
    
    async def get_user_savings_summary(self, user_id: str) -> SavingsTargetSummary:
        """
        Get user's savings targets summary.
        
        Args:
            user_id: User ID
            
        Returns:
            Savings targets summary
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Aggregation pipeline for summary
            pipeline = [
                {"$match": {"user_id": user_id}},
                {
                    "$group": {
                        "_id": None,
                        "total_targets": {"$sum": 1},
                        "active_targets": {
                            "$sum": {"$cond": [{"$eq": ["$is_achieved", False]}, 1, 0]}
                        },
                        "achieved_targets": {
                            "$sum": {"$cond": [{"$eq": ["$is_achieved", True]}, 1, 0]}
                        },
                        "total_target_amount": {"$sum": "$target_amount"},
                        "total_current_amount": {"$sum": "$current_amount"},
                        "nearest_target_date": {"$min": "$target_date"}
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            
            if not result:
                return SavingsTargetSummary(
                    total_targets=0,
                    active_targets=0,
                    achieved_targets=0,
                    total_target_amount=0.0,
                    total_current_amount=0.0,
                    overall_progress=0.0,
                    nearest_target_date=None,
                    monthly_savings_needed=0.0
                )
            
            data = result[0]
            total_target_amount = data["total_target_amount"]
            total_current_amount = data["total_current_amount"]
            
            # Calculate overall progress
            overall_progress = (total_current_amount / total_target_amount * 100) if total_target_amount > 0 else 0
            
            # Calculate monthly savings needed for active targets
            monthly_savings_needed = 0.0
            if data["active_targets"] > 0:
                active_targets = await collection.find({
                    "user_id": user_id,
                    "is_achieved": False
                }).to_list(None)
                
                for target_doc in active_targets:
                    target = SavingsTargetInDB(**target_doc)
                    remaining_amount = target.target_amount - target.current_amount
                    days_remaining = max(1, (target.target_date - date.today()).days)
                    monthly_needed = (remaining_amount / days_remaining) * 30.44  # Average days per month
                    monthly_savings_needed += monthly_needed
            
            return SavingsTargetSummary(
                total_targets=data["total_targets"],
                active_targets=data["active_targets"],
                achieved_targets=data["achieved_targets"],
                total_target_amount=total_target_amount,
                total_current_amount=total_current_amount,
                overall_progress=round(overall_progress, 2),
                nearest_target_date=data["nearest_target_date"],
                monthly_savings_needed=round(monthly_savings_needed, 2)
            )
            
        except Exception as e:
            logger.error(f"Error getting user savings summary: {e}")
            return SavingsTargetSummary(
                total_targets=0,
                active_targets=0,
                achieved_targets=0,
                total_target_amount=0.0,
                total_current_amount=0.0,
                overall_progress=0.0,
                nearest_target_date=None,
                monthly_savings_needed=0.0
            )
    
    async def get_savings_analytics(self) -> SavingsTargetAnalytics:
        """
        Get savings target analytics (admin function).
        
        Returns:
            Savings target analytics
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Get basic stats
            total_targets = await collection.count_documents({})
            achieved_targets = await collection.count_documents({"is_achieved": True})
            
            # Calculate completion rate
            completion_rate = (achieved_targets / total_targets * 100) if total_targets > 0 else 0
            
            # Get average target amount
            avg_amount_pipeline = [
                {"$group": {"_id": None, "avg_amount": {"$avg": "$target_amount"}}}
            ]
            avg_result = await collection.aggregate(avg_amount_pipeline).to_list(1)
            most_common_target_amount = avg_result[0]["avg_amount"] if avg_result else 0
            
            # Get average completion time for achieved targets
            avg_time_pipeline = [
                {"$match": {"is_achieved": True}},
                {
                    "$addFields": {
                        "completion_days": {
                            "$dateDiff": {
                                "startDate": "$created_at",
                                "endDate": "$updated_at",
                                "unit": "day"
                            }
                        }
                    }
                },
                {"$group": {"_id": None, "avg_days": {"$avg": "$completion_days"}}}
            ]
            time_result = await collection.aggregate(avg_time_pipeline).to_list(1)
            average_time_to_complete = int(time_result[0]["avg_days"]) if time_result else 0
            
            # Calculate success rate (achieved / total)
            success_rate = completion_rate
            
            # Get total saved amount
            total_saved_pipeline = [
                {"$group": {"_id": None, "total_saved": {"$sum": "$current_amount"}}}
            ]
            saved_result = await collection.aggregate(total_saved_pipeline).to_list(1)
            total_saved = saved_result[0]["total_saved"] if saved_result else 0
            
            # Count active savers
            active_savers = await collection.distinct("user_id", {"is_achieved": False})
            
            return SavingsTargetAnalytics(
                average_completion_rate=round(completion_rate, 2),
                most_common_target_amount=round(most_common_target_amount, 2),
                average_time_to_complete=average_time_to_complete,
                success_rate=round(success_rate, 2),
                total_saved=total_saved,
                active_savers=len(active_savers)
            )
            
        except Exception as e:
            logger.error(f"Error getting savings analytics: {e}")
            return SavingsTargetAnalytics(
                average_completion_rate=0.0,
                most_common_target_amount=0.0,
                average_time_to_complete=0,
                success_rate=0.0,
                total_saved=0.0,
                active_savers=0
            )
    
    async def _add_history_entry(
        self,
        target_id: str,
        action: str,
        amount: float,
        balance_before: float,
        balance_after: float,
        description: Optional[str] = None
    ):
        """
        Add entry to savings target history.
        
        Args:
            target_id: Savings target ID
            action: Action type
            amount: Amount involved
            balance_before: Balance before action
            balance_after: Balance after action
            description: Optional description
        """
        try:
            db = await get_database()
            history_collection = db[self.history_collection_name]
            
            history_entry = {
                "_id": ObjectId(),
                "savings_target_id": target_id,
                "action": action,
                "amount": amount,
                "balance_before": balance_before,
                "balance_after": balance_after,
                "description": description,
                "created_at": datetime.utcnow()
            }
            
            await history_collection.insert_one(history_entry)
            
        except Exception as e:
            logger.error(f"Error adding history entry: {e}")
    
    async def _calculate_average_savings_rate(self, target_id: str) -> float:
        """
        Calculate average daily savings rate for a target.
        
        Args:
            target_id: Savings target ID
            
        Returns:
            Average daily savings rate
        """
        try:
            db = await get_database()
            history_collection = db[self.history_collection_name]
            
            # Get contributions only
            contributions = await history_collection.find({
                "savings_target_id": target_id,
                "action": "contribution"
            }).sort("created_at", 1).to_list(None)
            
            if len(contributions) < 2:
                return 0.0
            
            # Calculate rate based on contributions over time
            first_contribution = contributions[0]
            last_contribution = contributions[-1]
            
            time_diff = (last_contribution["created_at"] - first_contribution["created_at"]).days
            if time_diff <= 0:
                return 0.0
            
            total_contributed = sum(contrib["amount"] for contrib in contributions)
            daily_rate = total_contributed / time_diff
            
            return daily_rate
            
        except Exception as e:
            logger.error(f"Error calculating savings rate: {e}")
            return 0.0


# Global savings target service instance
savings_target_service = SavingsTargetService()