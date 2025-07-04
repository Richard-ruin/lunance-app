"""
Category CRUD Operations
CRUD operations untuk Category model dengan support global & personal categories
"""

from typing import Optional, List, Dict, Any

from .base import CRUDBase
from ..models.category import Category, CategoryType
from ..schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    """CRUD operations untuk Category model"""
    
    async def create_category(
        self,
        *,
        obj_in: CategoryCreate,
        created_by: Optional[str] = None,
        is_admin: bool = False
    ) -> Category:
        """
        Create category dengan validasi business rules
        
        Args:
            obj_in: Category create schema
            created_by: User ID yang membuat (None untuk global category)
            is_admin: Apakah user adalah admin
            
        Returns:
            Created category
            
        Raises:
            ValueError: Jika validasi gagal
        """
        # Validate global category rules
        if obj_in.is_global and not is_admin:
            raise ValueError("Hanya admin yang bisa membuat global category")
        
        if obj_in.is_global:
            created_by = None  # Global categories tidak punya owner
        elif not created_by:
            raise ValueError("Personal category harus memiliki created_by")
        
        # Check if category name exists
        exists = await self.category_name_exists(
            name=obj_in.name,
            category_type=obj_in.type,
            user_id=created_by,
            is_global=obj_in.is_global
        )
        
        if exists:
            scope = "global" if obj_in.is_global else "personal"
            raise ValueError(f"Kategori {scope} '{obj_in.name}' sudah ada")
        
        # Create category
        category_data = obj_in.model_dump()
        category_data["created_by"] = created_by
        
        category = self.model(**category_data)
        await category.save()
        
        return category
    
    async def get_global_categories(
        self,
        category_type: Optional[CategoryType] = None
    ) -> List[Category]:
        """Get global categories"""
        query = {
            "is_global": True,
            "is_active": True,
            "is_deleted": {"$ne": True}
        }
        
        if category_type:
            query["type"] = category_type
        
        return await self.get_multi(query=query, sort_by="name")
    
    async def get_user_categories(
        self,
        user_id: str,
        category_type: Optional[CategoryType] = None,
        include_global: bool = True
    ) -> List[Category]:
        """Get categories available untuk user (personal + global)"""
        queries = []
        
        # Personal categories
        personal_query = {
            "is_global": False,
            "created_by": user_id,
            "is_active": True,
            "is_deleted": {"$ne": True}
        }
        
        if category_type:
            personal_query["type"] = category_type
        
        queries.append(personal_query)
        
        # Global categories
        if include_global:
            global_query = {
                "is_global": True,
                "is_active": True,
                "is_deleted": {"$ne": True}
            }
            
            if category_type:
                global_query["type"] = category_type
            
            queries.append(global_query)
        
        # Combine queries
        if len(queries) == 1:
            final_query = queries[0]
        else:
            final_query = {"$or": queries}
        
        return await self.get_multi(query=final_query, sort_by="name")
    
    async def get_personal_categories(
        self,
        user_id: str,
        category_type: Optional[CategoryType] = None
    ) -> List[Category]:
        """Get personal categories untuk user"""
        query = {
            "is_global": False,
            "created_by": user_id,
            "is_active": True,
            "is_deleted": {"$ne": True}
        }
        
        if category_type:
            query["type"] = category_type
        
        return await self.get_multi(query=query, sort_by="name")
    
    async def category_name_exists(
        self,
        name: str,
        category_type: CategoryType,
        user_id: Optional[str] = None,
        is_global: bool = False,
        exclude_id: Optional[str] = None
    ) -> bool:
        """Check apakah nama kategori sudah exists"""
        query = {
            "name": {"$pattern": f"^{name}$", "$options": "i"},
            "type": category_type,
            "is_deleted": {"$ne": True}
        }
        
        if is_global:
            query["is_global"] = True
        else:
            query.update({
                "is_global": False,
                "created_by": user_id
            })
        
        if exclude_id:
            query["_id"] = {"$ne": exclude_id}
        
        return await self.exists(query=query)
    
    async def update_category(
        self,
        *,
        category_id: str,
        obj_in: CategoryUpdate,
        user_id: str,
        is_admin: bool = False
    ) -> Optional[Category]:
        """
        Update category dengan validasi permission
        
        Args:
            category_id: ID kategori
            obj_in: Update data
            user_id: User ID yang update
            is_admin: Apakah user adalah admin
            
        Returns:
            Updated category atau None
            
        Raises:
            ValueError: Jika tidak ada permission atau validasi gagal
        """
        category = await self.get(category_id)
        if not category:
            return None
        
        # Check permission
        if not category.can_be_edited_by(user_id, is_admin):
            raise ValueError("Anda tidak memiliki permission untuk mengedit kategori ini")
        
        # Validate name uniqueness jika name diupdate
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if "name" in update_data:
            exists = await self.category_name_exists(
                name=update_data["name"],
                category_type=category.type,
                user_id=category.created_by,
                is_global=category.is_global,
                exclude_id=category_id
            )
            
            if exists:
                scope = "global" if category.is_global else "personal"
                raise ValueError(f"Nama kategori {scope} sudah ada")
        
        return await self.update(
            id=category_id,
            obj_in=obj_in,
            updated_by=user_id
        )
    
    async def delete_category(
        self,
        *,
        category_id: str,
        user_id: str,
        is_admin: bool = False,
        soft: bool = True
    ) -> bool:
        """
        Delete category dengan validasi permission
        
        Args:
            category_id: ID kategori
            user_id: User ID yang delete
            is_admin: Apakah user adalah admin
            soft: Soft delete atau hard delete
            
        Returns:
            True jika berhasil dihapus
            
        Raises:
            ValueError: Jika tidak ada permission
        """
        category = await self.get(category_id)
        if not category:
            return False
        
        # Check permission
        if not category.can_be_edited_by(user_id, is_admin):
            raise ValueError("Anda tidak memiliki permission untuk menghapus kategori ini")
        
        # Check if category is being used (implement this based on your needs)
        # You might want to check if there are transactions using this category
        
        if soft:
            return await self.soft_delete(id=category_id, deleted_by=user_id)
        else:
            return await self.delete(id=category_id)
    
    async def increment_usage(self, category_id: str, user_id: str) -> bool:
        """Increment usage count untuk kategori"""
        category = await self.get(category_id)
        if not category:
            return False
        
        await category.increment_usage(user_id)
        return True
    
    async def activate_category(self, category_id: str) -> bool:
        """Aktivasi kategori"""
        category = await self.get(category_id)
        if not category:
            return False
        
        await category.activate()
        return True
    
    async def deactivate_category(self, category_id: str) -> bool:
        """Deaktivasi kategori"""
        category = await self.get(category_id)
        if not category:
            return False
        
        await category.deactivate()
        return True
    
    async def get_popular_categories(
        self,
        category_type: Optional[CategoryType] = None,
        limit: int = 10,
        global_only: bool = False
    ) -> List[Category]:
        """Get popular categories berdasarkan usage count"""
        query = {
            "is_active": True,
            "is_deleted": {"$ne": True}
        }
        
        if category_type:
            query["type"] = category_type
        
        if global_only:
            query["is_global"] = True
        
        return await self.get_multi(
            query=query,
            sort_by="usage_count",
            sort_order=-1,
            limit=limit
        )
    
    async def search_categories(
        self,
        *,
        search_term: str,
        user_id: Optional[str] = None,
        category_type: Optional[CategoryType] = None,
        is_global: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Category]:
        """Search categories"""
        query = {
            "$or": [
                {"name": {"$pattern": search_term, "$options": "i"}},
                {"description": {"$pattern": search_term, "$options": "i"}}
            ],
            "is_active": True,
            "is_deleted": {"$ne": True}
        }
        
        if category_type:
            query["type"] = category_type
        
        if is_global is not None:
            query["is_global"] = is_global
            
            if not is_global and user_id:
                query["created_by"] = user_id
        
        return await self.get_multi(
            skip=skip,
            limit=limit,
            query=query,
            sort_by="name"
        )
    
    async def get_category_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get category statistics"""
        # Global stats
        global_stats = {
            "total_global": await self.count(query={"is_global": True}),
            "active_global": await self.count(query={"is_global": True, "is_active": True}),
            "global_income": await self.count(query={"is_global": True, "type": CategoryType.INCOME}),
            "global_expense": await self.count(query={"is_global": True, "type": CategoryType.EXPENSE})
        }
        
        result = {"global": global_stats}
        
        # User-specific stats jika user_id diberikan
        if user_id:
            user_stats = {
                "total_personal": await self.count(query={"is_global": False, "created_by": user_id}),
                "active_personal": await self.count(query={
                    "is_global": False, 
                    "created_by": user_id, 
                    "is_active": True
                }),
                "personal_income": await self.count(query={
                    "is_global": False, 
                    "created_by": user_id, 
                    "type": CategoryType.INCOME
                }),
                "personal_expense": await self.count(query={
                    "is_global": False, 
                    "created_by": user_id, 
                    "type": CategoryType.EXPENSE
                })
            }
            result["user"] = user_stats
        
        return result
    
    async def create_default_categories(self, admin_user_id: str) -> List[Category]:
        """Create default global categories"""
        return await Category.create_default_categories(admin_user_id)
    
    async def bulk_create_user_categories(
        self,
        *,
        user_id: str,
        categories_data: List[CategoryCreate]
    ) -> List[Category]:
        """Bulk create personal categories untuk user"""
        created_categories = []
        
        for category_data in categories_data:
            try:
                category = await self.create_category(
                    obj_in=category_data,
                    created_by=user_id,
                    is_admin=False
                )
                created_categories.append(category)
            except ValueError:
                # Skip if category already exists
                continue
        
        return created_categories
    
    async def transfer_to_global(
        self,
        *,
        category_id: str,
        admin_user_id: str
    ) -> Optional[Category]:
        """Transfer personal category menjadi global category"""
        category = await self.get(category_id)
        if not category or category.is_global:
            return None
        
        # Check if global category dengan nama yang sama sudah ada
        exists = await self.category_name_exists(
            name=category.name,
            category_type=category.type,
            is_global=True
        )
        
        if exists:
            raise ValueError("Global category dengan nama yang sama sudah ada")
        
        # Update category
        update_data = {
            "is_global": True,
            "created_by": None
        }
        
        return await self.update(
            id=category_id,
            obj_in=update_data,
            updated_by=admin_user_id
        )


# Create instance
crud_category = CRUDCategory(Category)