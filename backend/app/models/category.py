"""
Category Model
Model untuk kategori transaksi dengan support global & personal categories
"""

from typing import Optional
from enum import Enum
from pydantic import Field, field_validator, model_validator
from beanie import Indexed

from .base import BaseDocument, SoftDeleteMixin, AuditMixin


class CategoryType(str, Enum):
    """Tipe kategori transaksi"""
    INCOME = "income"      # Pemasukan
    EXPENSE = "expense"    # Pengeluaran


class Category(BaseDocument, SoftDeleteMixin, AuditMixin):
    """
    Model Kategori untuk transaksi keuangan
    
    Features:
    - Global categories: Dibuat admin, bisa digunakan semua user
    - Personal categories: Dibuat user, hanya bisa digunakan user tersebut
    - Icon & color untuk UI
    - Validasi untuk memastikan consistency
    
    Fields:
    - name: Nama kategori
    - type: Tipe kategori (income/expense)
    - is_global: Flag global vs personal category
    - created_by: User yang membuat (None untuk system-generated)
    - icon: Icon name untuk UI
    - color: Hex color code
    - description: Deskripsi kategori
    - is_active: Status aktif kategori
    """
    
    name: Indexed(str) = Field(..., min_length=1, max_length=100, description="Nama kategori")
    type: CategoryType = Field(..., description="Tipe kategori")
    
    # Global vs Personal Category System
    is_global: bool = Field(default=False, description="Global category (admin managed)")
    created_by: Optional[str] = Field(default=None, description="User yang membuat (None untuk global)")
    
    # UI/UX Properties
    icon: Optional[str] = Field(default=None, max_length=50, description="Icon name")
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Hex color code")
    
    # Additional Properties
    description: Optional[str] = Field(default=None, max_length=500, description="Deskripsi kategori")
    is_active: bool = Field(default=True, description="Status aktif kategori")
    
    # Usage Statistics
    usage_count: int = Field(default=0, ge=0, description="Jumlah penggunaan")
    last_used: Optional[str] = Field(default=None, description="Terakhir digunakan oleh user")
    
    class Settings:
        name = "categories"
        indexes = [
            "name",
            "type",
            "is_global",
            "created_by",
            "is_active",
            [("is_global", 1), ("type", 1)],  # Compound index
            [("created_by", 1), ("type", 1)],  # User categories by type
            [("is_global", 1), ("name", 1)]   # Global categories by name
        ]
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validasi nama kategori"""
        if not v or not v.strip():
            raise ValueError("Nama kategori tidak boleh kosong")
        
        # Clean up name
        v = v.strip().title()  # Title case
        
        # Basic validation
        if len(v.replace(" ", "")) < 1:
            raise ValueError("Nama kategori harus memiliki minimal 1 karakter non-spasi")
        
        return v
    
    @field_validator("icon")
    @classmethod
    def validate_icon(cls, v):
        """Validasi icon name"""
        if not v:
            return v
        
        v = v.strip().lower()
        
        # Basic validation - hanya huruf, angka, dash, underscore
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Icon name hanya boleh berisi huruf, angka, dash, dan underscore")
        
        return v
    
    @field_validator("color")
    @classmethod
    def validate_color(cls, v):
        """Validasi hex color code"""
        if not v:
            return v
        
        v = v.strip().upper()
        
        # Ensure starts with #
        if not v.startswith("#"):
            v = "#" + v
        
        # Validate hex format
        if not v.match(r"^#[0-9A-F]{6}$"):
            raise ValueError("Color harus dalam format hex 6 digit (contoh: #FF5733)")
        
        return v
    
    @model_validator(mode="after")
    def validate_global_category_rules(self):
        """Validasi rules untuk global vs personal categories"""
        if self.is_global:
            # Global categories tidak boleh punya created_by
            if self.created_by is not None:
                raise ValueError("Global category tidak boleh memiliki created_by")
        else:
            # Personal categories harus punya created_by
            if self.created_by is None:
                raise ValueError("Personal category harus memiliki created_by")
        
        return self
    
    def is_personal(self) -> bool:
        """Check apakah ini personal category"""
        return not self.is_global
    
    def can_be_used_by(self, user_id: str) -> bool:
        """Check apakah kategori bisa digunakan oleh user"""
        if self.is_global and self.is_active:
            return True
        
        if self.is_personal() and self.created_by == user_id and self.is_active:
            return True
        
        return False
    
    def can_be_edited_by(self, user_id: str, is_admin: bool = False) -> bool:
        """Check apakah kategori bisa diedit oleh user"""
        # Admin bisa edit semua kategori
        if is_admin:
            return True
        
        # User hanya bisa edit personal category miliknya sendiri
        if self.is_personal() and self.created_by == user_id:
            return True
        
        return False
    
    async def increment_usage(self, user_id: str):
        """Increment usage count dan update last_used"""
        self.usage_count += 1
        self.last_used = user_id
        await self.save_with_timestamp()
    
    async def deactivate(self):
        """Deaktivasi kategori"""
        self.is_active = False
        await self.save_with_timestamp()
    
    async def activate(self):
        """Aktivasi kategori"""
        self.is_active = True
        await self.save_with_timestamp()
    
    @classmethod
    async def find_global_categories(cls, category_type: Optional[CategoryType] = None):
        """Find global categories"""
        query = {
            "is_global": True,
            "is_active": True,
            "is_deleted": {"$ne": True}
        }
        
        if category_type:
            query["type"] = category_type
        
        return await cls.find(query).to_list()
    
    @classmethod
    async def find_user_categories(
        cls, 
        user_id: str, 
        category_type: Optional[CategoryType] = None,
        include_global: bool = True
    ):
        """Find categories available untuk user (personal + global)"""
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
        
        # Global categories (jika diminta)
        if include_global:
            global_query = {
                "is_global": True,
                "is_active": True,
                "is_deleted": {"$ne": True}
            }
            
            if category_type:
                global_query["type"] = category_type
            
            queries.append(global_query)
        
        # Combine queries dengan $or
        if len(queries) == 1:
            final_query = queries[0]
        else:
            final_query = {"$or": queries}
        
        return await cls.find(final_query).sort("name").to_list()
    
    @classmethod
    async def find_personal_categories(cls, user_id: str, category_type: Optional[CategoryType] = None):
        """Find personal categories untuk user"""
        query = {
            "is_global": False,
            "created_by": user_id,
            "is_active": True,
            "is_deleted": {"$ne": True}
        }
        
        if category_type:
            query["type"] = category_type
        
        return await cls.find(query).sort("name").to_list()
    
    @classmethod
    async def category_name_exists(
        cls, 
        name: str, 
        category_type: CategoryType,
        user_id: Optional[str] = None,
        is_global: bool = False
    ) -> bool:
        """Check apakah nama kategori sudah exists"""
        query = {
            "name": name,
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
        
        category = await cls.find_one(query)
        return category is not None
    
    @classmethod
    async def get_popular_categories(
        cls, 
        category_type: Optional[CategoryType] = None,
        limit: int = 10
    ):
        """Get popular categories berdasarkan usage count"""
        query = {
            "is_active": True,
            "is_deleted": {"$ne": True}
        }
        
        if category_type:
            query["type"] = category_type
        
        return await cls.find(query).sort([("usage_count", -1)]).limit(limit).to_list()
    
    @classmethod
    async def create_default_categories(cls, admin_user_id: str):
        """Create default global categories untuk sistem"""
        default_categories = [
            # Income Categories
            {
                "name": "Gaji",
                "type": CategoryType.INCOME,
                "icon": "salary",
                "color": "#4CAF50",
                "description": "Gaji bulanan dari pekerjaan"
            },
            {
                "name": "Uang Saku",
                "type": CategoryType.INCOME,
                "icon": "pocket-money",
                "color": "#8BC34A",
                "description": "Uang saku dari orang tua"
            },
            {
                "name": "Beasiswa",
                "type": CategoryType.INCOME,
                "icon": "scholarship",
                "color": "#CDDC39",
                "description": "Beasiswa pendidikan"
            },
            {
                "name": "Kerja Sampingan",
                "type": CategoryType.INCOME,
                "icon": "part-time",
                "color": "#9C27B0",
                "description": "Penghasilan dari kerja paruh waktu"
            },
            
            # Expense Categories
            {
                "name": "Makanan & Minuman",
                "type": CategoryType.EXPENSE,
                "icon": "food",
                "color": "#FF5722",
                "description": "Pengeluaran untuk makanan dan minuman"
            },
            {
                "name": "Transportasi",
                "type": CategoryType.EXPENSE,
                "icon": "transport",
                "color": "#2196F3",
                "description": "Biaya transportasi"
            },
            {
                "name": "Pendidikan",
                "type": CategoryType.EXPENSE,
                "icon": "education",
                "color": "#3F51B5",
                "description": "Biaya pendidikan, buku, kursus"
            },
            {
                "name": "Hiburan",
                "type": CategoryType.EXPENSE,
                "icon": "entertainment",
                "color": "#E91E63",
                "description": "Biaya hiburan dan rekreasi"
            },
            {
                "name": "Belanja",
                "type": CategoryType.EXPENSE,
                "icon": "shopping",
                "color": "#FF9800",
                "description": "Belanja pakaian dan kebutuhan lainnya"
            },
            {
                "name": "Kesehatan",
                "type": CategoryType.EXPENSE,
                "icon": "health",
                "color": "#4CAF50",
                "description": "Biaya kesehatan dan obat-obatan"
            }
        ]
        
        created_categories = []
        for cat_data in default_categories:
            # Check if category already exists
            exists = await cls.category_name_exists(
                cat_data["name"], 
                cat_data["type"], 
                is_global=True
            )
            
            if not exists:
                category = cls(
                    **cat_data,
                    is_global=True,
                    created_by=None,  # System generated
                    set_updated_by=admin_user_id
                )
                await category.save()
                created_categories.append(category)
        
        return created_categories