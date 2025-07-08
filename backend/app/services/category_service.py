# app/services/category_service.py
"""Category management service with global and personal categories."""

from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from ..config.database import get_database
from ..models.category import (
    CategoryInDB, CategoryCreate, CategoryUpdate, CategoryResponse,
    CategoryWithStats, GlobalCategoryCreate, CategoryStats, DEFAULT_GLOBAL_CATEGORIES
)
from ..models.common import PaginatedResponse, PaginationParams

logger = logging.getLogger(__name__)


class CategoryServiceError(Exception):
    """Category service related error."""
    pass


class CategoryService:
    """Category management service."""
    
    def __init__(self):
        self.collection_name = "categories"
    
    async def create_category(
        self,
        category_data: CategoryCreate,
        user_id: Optional[str] = None
    ) -> CategoryResponse:
        """
        Create new category (personal or global).
        
        Args:
            category_data: Category creation data
            user_id: User ID for personal categories
            
        Returns:
            Created category response
            
        Raises:
            CategoryServiceError: If creation fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Determine category type and ownership
            if category_data.is_global:
                if user_id:
                    raise CategoryServiceError("Global categories cannot have a user_id")
                final_user_id = None
            else:
                if not user_id:
                    raise CategoryServiceError("Personal categories require a user_id")
                final_user_id = user_id
            
            # Check for duplicate category name for the same user/global scope
            query = {
                "name": {"$regex": f"^{category_data.name}$", "$options": "i"},
                "user_id": final_user_id
            }
            
            existing_category = await collection.find_one(query)
            if existing_category:
                scope = "global" if category_data.is_global else "personal"
                raise CategoryServiceError(f"A {scope} category with this name already exists")
            
            # Create category document
            category_doc = CategoryInDB(
                name=category_data.name,
                icon=category_data.icon,
                color=category_data.color,
                is_global=category_data.is_global,
                user_id=final_user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Insert category
            result = await collection.insert_one(
                category_doc.model_dump(by_alias=True, exclude={"id"})
            )
            
            category_id = str(result.inserted_id)
            
            # Get created category
            created_category_doc = await collection.find_one({"_id": result.inserted_id})
            created_category = CategoryInDB(**created_category_doc)
            
            scope = "global" if category_data.is_global else "personal"
            logger.info(f"Category created: {category_data.name} ({scope}) - ID: {category_id}")
            
            return CategoryResponse(
                id=category_id,
                name=created_category.name,
                icon=created_category.icon,
                color=created_category.color,
                is_global=created_category.is_global,
                user_id=created_category.user_id,
                created_at=created_category.created_at,
                updated_at=created_category.updated_at
            )
            
        except CategoryServiceError:
            raise
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            raise CategoryServiceError("Failed to create category")
    
    async def get_category_by_id(self, category_id: str, user_id: Optional[str] = None) -> Optional[CategoryResponse]:
        """
        Get category by ID.
        
        Args:
            category_id: Category ID
            user_id: User ID for access control
            
        Returns:
            Category response or None if not found/no access
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            category_doc = await collection.find_one({"_id": ObjectId(category_id)})
            if not category_doc:
                return None
            
            category = CategoryInDB(**category_doc)
            
            # Check access permissions
            if not category.is_global and category.user_id != user_id:
                return None  # User can't access other users' personal categories
            
            return CategoryResponse(
                id=str(category.id),
                name=category.name,
                icon=category.icon,
                color=category.color,
                is_global=category.is_global,
                user_id=category.user_id,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
            
        except Exception as e:
            logger.error(f"Error getting category {category_id}: {e}")
            return None
    
    async def list_categories(
        self,
        user_id: str,
        pagination: PaginationParams,
        category_type: Optional[str] = None,  # "global", "personal", or None for all
        search: Optional[str] = None
    ) -> PaginatedResponse[CategoryResponse]:
        """
        List categories for user (global + personal).
        
        Args:
            user_id: User ID
            pagination: Pagination parameters
            category_type: Filter by category type
            search: Search term for category name
            
        Returns:
            Paginated category response
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build query
            query = {
                "$or": [
                    {"is_global": True},  # Global categories
                    {"user_id": user_id}  # User's personal categories
                ]
            }
            
            # Filter by category type
            if category_type == "global":
                query = {"is_global": True}
            elif category_type == "personal":
                query = {"user_id": user_id, "is_global": False}
            
            # Search filter
            if search:
                query["name"] = {"$regex": search, "$options": "i"}
            
            # Get total count
            total = await collection.count_documents(query)
            
            # Build sort
            sort_field = pagination.sort_by or "name"
            sort_direction = ASCENDING if pagination.sort_order.value == "asc" else DESCENDING
            
            # Get paginated results
            skip = (pagination.page - 1) * pagination.per_page
            cursor = collection.find(query).sort(sort_field, sort_direction)
            cursor = cursor.skip(skip).limit(pagination.per_page)
            
            categories_docs = await cursor.to_list(length=pagination.per_page)
            
            # Convert to response format
            categories = []
            for category_doc in categories_docs:
                category = CategoryInDB(**category_doc)
                categories.append(CategoryResponse(
                    id=str(category.id),
                    name=category.name,
                    icon=category.icon,
                    color=category.color,
                    is_global=category.is_global,
                    user_id=category.user_id,
                    created_at=category.created_at,
                    updated_at=category.updated_at
                ))
            
            return PaginatedResponse.create(
                items=categories,
                total=total,
                page=pagination.page,
                per_page=pagination.per_page
            )
            
        except Exception as e:
            logger.error(f"Error listing categories: {e}")
            raise CategoryServiceError("Failed to list categories")
    
    async def update_category(
        self,
        category_id: str,
        update_data: CategoryUpdate,
        user_id: str,
        is_admin: bool = False
    ) -> Optional[CategoryResponse]:
        """
        Update category.
        
        Args:
            category_id: Category ID
            update_data: Update data
            user_id: User ID performing update
            is_admin: Whether user is admin
            
        Returns:
            Updated category response
            
        Raises:
            CategoryServiceError: If update fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Get existing category
            existing_category = await collection.find_one({"_id": ObjectId(category_id)})
            if not existing_category:
                raise CategoryServiceError("Category not found")
            
            category = CategoryInDB(**existing_category)
            
            # Check permissions
            if category.is_global and not is_admin:
                raise CategoryServiceError("Only admins can update global categories")
            
            if not category.is_global and category.user_id != user_id:
                raise CategoryServiceError("You can only update your own categories")
            
            # Prepare update data
            update_fields = {}
            for field, value in update_data.model_dump(exclude_none=True).items():
                if value is not None:
                    update_fields[field] = value
            
            if not update_fields:
                # No updates provided, return current category
                return await self.get_category_by_id(category_id, user_id)
            
            # Check for name conflicts if name is being updated
            if "name" in update_fields:
                name_query = {
                    "_id": {"$ne": ObjectId(category_id)},
                    "name": {"$regex": f"^{update_fields['name']}$", "$options": "i"},
                    "user_id": category.user_id
                }
                
                name_conflict = await collection.find_one(name_query)
                if name_conflict:
                    scope = "global" if category.is_global else "personal"
                    raise CategoryServiceError(f"Another {scope} category with this name already exists")
            
            # Add updated timestamp
            update_fields["updated_at"] = datetime.utcnow()
            
            # Update category
            result = await collection.update_one(
                {"_id": ObjectId(category_id)},
                {"$set": update_fields}
            )
            
            if result.modified_count == 0:
                raise CategoryServiceError("Failed to update category")
            
            logger.info(f"Category updated: {category_id} by user {user_id}")
            
            return await self.get_category_by_id(category_id, user_id)
            
        except CategoryServiceError:
            raise
        except Exception as e:
            logger.error(f"Error updating category {category_id}: {e}")
            raise CategoryServiceError("Failed to update category")
    
    async def delete_category(
        self,
        category_id: str,
        user_id: str,
        is_admin: bool = False
    ) -> bool:
        """
        Delete category.
        
        Args:
            category_id: Category ID
            user_id: User ID performing deletion
            is_admin: Whether user is admin
            
        Returns:
            True if successful
            
        Raises:
            CategoryServiceError: If deletion fails
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Get existing category
            existing_category = await collection.find_one({"_id": ObjectId(category_id)})
            if not existing_category:
                raise CategoryServiceError("Category not found")
            
            category = CategoryInDB(**existing_category)
            
            # Check permissions
            if category.is_global and not is_admin:
                raise CategoryServiceError("Only admins can delete global categories")
            
            if not category.is_global and category.user_id != user_id:
                raise CategoryServiceError("You can only delete your own categories")
            
            # Check if category is being used in transactions
            transactions_collection = db.transactions
            transaction_count = await transactions_collection.count_documents(
                {"category_id": category_id}
            )
            
            if transaction_count > 0:
                raise CategoryServiceError(
                    f"Cannot delete category: it is used in {transaction_count} transaction(s). "
                    "Please reassign those transactions to another category first."
                )
            
            # Delete category
            result = await collection.delete_one({"_id": ObjectId(category_id)})
            
            if result.deleted_count == 0:
                raise CategoryServiceError("Failed to delete category")
            
            scope = "global" if category.is_global else "personal"
            logger.info(f"Category deleted: {category_id} ({scope}) by user {user_id}")
            
            return True
            
        except CategoryServiceError:
            raise
        except Exception as e:
            logger.error(f"Error deleting category {category_id}: {e}")
            raise CategoryServiceError("Failed to delete category")
    
    async def get_categories_with_stats(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[CategoryWithStats]:
        """
        Get categories with usage statistics.
        
        Args:
            user_id: User ID
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            List of categories with statistics
        """
        try:
            db = await get_database()
            categories_collection = db[self.collection_name]
            transactions_collection = db.transactions
            
            # Get user's accessible categories
            categories_query = {
                "$or": [
                    {"is_global": True},
                    {"user_id": user_id}
                ]
            }
            
            categories_cursor = categories_collection.find(categories_query)
            categories_docs = await categories_cursor.to_list(length=None)
            
            # Build transaction query for stats
            transaction_query = {"user_id": user_id}
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                transaction_query["date"] = date_filter
            
            # Get transaction statistics per category
            stats_pipeline = [
                {"$match": transaction_query},
                {
                    "$group": {
                        "_id": "$category_id",
                        "transaction_count": {"$sum": 1},
                        "total_amount": {"$sum": "$amount"},
                        "last_used": {"$max": "$created_at"}
                    }
                }
            ]
            
            stats_cursor = transactions_collection.aggregate(stats_pipeline)
            stats_docs = await stats_cursor.to_list(length=None)
            
            # Create stats lookup
            stats_lookup = {stat["_id"]: stat for stat in stats_docs}
            
            # Combine categories with stats
            categories_with_stats = []
            for category_doc in categories_docs:
                category = CategoryInDB(**category_doc)
                category_id = str(category.id)
                
                stats = stats_lookup.get(category_id, {})
                
                categories_with_stats.append(CategoryWithStats(
                    id=category_id,
                    name=category.name,
                    icon=category.icon,
                    color=category.color,
                    is_global=category.is_global,
                    user_id=category.user_id,
                    created_at=category.created_at,
                    updated_at=category.updated_at,
                    transaction_count=stats.get("transaction_count", 0),
                    total_amount=stats.get("total_amount", 0.0),
                    last_used=stats.get("last_used")
                ))
            
            # Sort by usage (most used first)
            categories_with_stats.sort(key=lambda x: x.transaction_count, reverse=True)
            
            return categories_with_stats
            
        except Exception as e:
            logger.error(f"Error getting categories with stats: {e}")
            return []
    
    async def get_category_stats(self) -> CategoryStats:
        """
        Get category system statistics.
        
        Returns:
            Category statistics
        """
        try:
            db = await get_database()
            categories_collection = db[self.collection_name]
            transactions_collection = db.transactions
            
            # Total categories
            total_categories = await categories_collection.count_documents({})
            
            # Global vs personal categories
            global_categories = await categories_collection.count_documents({"is_global": True})
            personal_categories = total_categories - global_categories
            
            # Most used categories
            most_used_pipeline = [
                {
                    "$group": {
                        "_id": "$category_id",
                        "usage_count": {"$sum": 1}
                    }
                },
                {
                    "$lookup": {
                        "from": "categories",
                        "localField": "_id",
                        "foreignField": "_id",
                        "as": "category"
                    }
                },
                {"$unwind": "$category"},
                {
                    "$project": {
                        "name": "$category.name",
                        "usage_count": 1
                    }
                },
                {"$sort": {"usage_count": -1}},
                {"$limit": 10}
            ]
            
            most_used_cursor = transactions_collection.aggregate(most_used_pipeline)
            most_used_docs = await most_used_cursor.to_list(10)
            
            most_used_categories = [
                {"name": doc["name"], "usage_count": doc["usage_count"]}
                for doc in most_used_docs
            ]
            
            # Average categories per user
            users_with_categories_pipeline = [
                {"$match": {"is_global": False}},
                {
                    "$group": {
                        "_id": "$user_id",
                        "category_count": {"$sum": 1}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "avg_categories": {"$avg": "$category_count"}
                    }
                }
            ]
            
            avg_result = await categories_collection.aggregate(users_with_categories_pipeline).to_list(1)
            categories_by_user = round(avg_result[0]["avg_categories"], 1) if avg_result else 0
            
            return CategoryStats(
                total_categories=total_categories,
                global_categories=global_categories,
                personal_categories=personal_categories,
                most_used_categories=most_used_categories,
                categories_by_user=categories_by_user
            )
            
        except Exception as e:
            logger.error(f"Error getting category stats: {e}")
            return CategoryStats(
                total_categories=0,
                global_categories=0,
                personal_categories=0,
                most_used_categories=[],
                categories_by_user=0
            )
    
    async def create_default_global_categories(self) -> int:
        """
        Create default global categories if they don't exist.
        
        Returns:
            Number of categories created
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            created_count = 0
            
            for category_data in DEFAULT_GLOBAL_CATEGORIES:
                # Check if category already exists
                existing = await collection.find_one({
                    "name": category_data["name"],
                    "is_global": True
                })
                
                if not existing:
                    # Create category
                    category_doc = CategoryInDB(
                        **category_data,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    await collection.insert_one(
                        category_doc.model_dump(by_alias=True, exclude={"id"})
                    )
                    
                    created_count += 1
                    logger.info(f"Created default global category: {category_data['name']}")
            
            if created_count > 0:
                logger.info(f"Created {created_count} default global categories")
            
            return created_count
            
        except Exception as e:
            logger.error(f"Error creating default global categories: {e}")
            return 0
    
    async def search_categories(
        self,
        user_id: str,
        search_term: str,
        limit: int = 10
    ) -> List[CategoryResponse]:
        """
        Search categories by name.
        
        Args:
            user_id: User ID
            search_term: Search term
            limit: Maximum results
            
        Returns:
            List of matching categories
        """
        try:
            db = await get_database()
            collection = db[self.collection_name]
            
            # Build search query
            query = {
                "$and": [
                    {
                        "$or": [
                            {"is_global": True},
                            {"user_id": user_id}
                        ]
                    },
                    {"name": {"$regex": search_term, "$options": "i"}}
                ]
            }
            
            # Execute search
            cursor = collection.find(query).limit(limit)
            categories_docs = await cursor.to_list(length=limit)
            
            # Convert to response format
            categories = []
            for category_doc in categories_docs:
                category = CategoryInDB(**category_doc)
                categories.append(CategoryResponse(
                    id=str(category.id),
                    name=category.name,
                    icon=category.icon,
                    color=category.color,
                    is_global=category.is_global,
                    user_id=category.user_id,
                    created_at=category.created_at,
                    updated_at=category.updated_at
                ))
            
            return categories
            
        except Exception as e:
            logger.error(f"Error searching categories: {e}")
            return []


# Global category service instance
category_service = CategoryService()