from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class CategoryBase(BaseModel):
    """Base category model."""
    name: str = Field(..., min_length=2, max_length=50, description="Category name")
    icon: str = Field(..., min_length=1, max_length=50, description="Category icon")
    color: str = Field(..., description="Category color in hex format")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean category name."""
        name = v.strip().title()
        if not re.match(r'^[a-zA-Z\s&-]+$', name):
            raise ValueError('Category name must only contain letters, spaces, & and -')
        return name

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate hex color format."""
        v = v.strip().upper()
        if not re.match(r'^#[0-9A-F]{6}$', v):
            raise ValueError('Color must be in valid hex format (e.g., #FF5733)')
        return v

    @field_validator('icon')
    @classmethod
    def validate_icon(cls, v: str) -> str:
        """Validate icon name."""
        icon = v.strip().lower()
        # You can add specific icon validation here if needed
        if len(icon) < 1:
            raise ValueError('Icon cannot be empty')
        return icon


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    is_global: bool = Field(default=False, description="Whether category is global or personal")
    user_id: Optional[str] = Field(None, description="User ID for personal categories")

    def __init__(self, **data):
        super().__init__(**data)
        # If not global, user_id is required
        if not self.is_global and not self.user_id:
            raise ValueError('user_id is required for personal categories')
        # If global, user_id should be None
        if self.is_global and self.user_id:
            raise ValueError('user_id should be None for global categories')


class CategoryUpdate(BaseModel):
    """Schema for updating category information."""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    icon: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate category name if provided."""
        if v is None:
            return v
        return CategoryBase.validate_name(v)

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color if provided."""
        if v is None:
            return v
        return CategoryBase.validate_color(v)

    @field_validator('icon')
    @classmethod
    def validate_icon(cls, v: Optional[str]) -> Optional[str]:
        """Validate icon if provided."""
        if v is None:
            return v
        return CategoryBase.validate_icon(v)


class CategoryInDB(CategoryBase):
    """Category model as stored in database."""
    id: Optional[str] = Field(None, alias="_id", description="Category ID")
    is_global: bool = Field(default=False, description="Whether category is global or personal")
    user_id: Optional[str] = Field(None, description="User ID for personal categories")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    model_config = {
        'populate_by_name': True,
        'json_schema_extra': {
            'example': {
                'name': 'Food & Dining',
                'icon': 'restaurant',
                'color': '#FF5733',
                'is_global': True,
                'user_id': None
            }
        }
    }


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: Optional[str] = Field(None, alias="_id", description="Category ID")
    is_global: bool = Field(..., description="Whether category is global or personal")
    user_id: Optional[str] = Field(None, description="User ID for personal categories")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        'populate_by_name': True,
        'from_attributes': True
    }


class CategorySimple(BaseModel):
    """Simple category schema for references."""
    id: str = Field(..., alias="_id", description="Category ID")
    name: str = Field(..., description="Category name")
    icon: str = Field(..., description="Category icon")
    color: str = Field(..., description="Category color")

    model_config = {
        'populate_by_name': True,
        'from_attributes': True
    }


class CategoryWithStats(CategoryResponse):
    """Category schema with usage statistics."""
    transaction_count: int = Field(default=0, description="Number of transactions in this category")
    total_amount: float = Field(default=0.0, description="Total amount in this category")
    last_used: Optional[datetime] = Field(None, description="Last time category was used")

    model_config = {
        'populate_by_name': True,
        'from_attributes': True
    }


class GlobalCategoryCreate(BaseModel):
    """Schema for creating global categories (admin only)."""
    name: str = Field(..., min_length=2, max_length=50, description="Category name")
    icon: str = Field(..., min_length=1, max_length=50, description="Category icon")
    color: str = Field(..., description="Category color in hex format")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean category name."""
        return CategoryBase.validate_name(v)

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate hex color format."""
        return CategoryBase.validate_color(v)

    @field_validator('icon')
    @classmethod
    def validate_icon(cls, v: str) -> str:
        """Validate icon name."""
        return CategoryBase.validate_icon(v)


class CategoryStats(BaseModel):
    """Schema for category statistics."""
    total_categories: int = Field(..., description="Total number of categories")
    global_categories: int = Field(..., description="Number of global categories")
    personal_categories: int = Field(..., description="Number of personal categories")
    most_used_categories: list = Field(..., description="Most frequently used categories")
    categories_by_user: int = Field(..., description="Average categories per user")

    model_config = {
        'json_schema_extra': {
            'example': {
                'total_categories': 45,
                'global_categories': 15,
                'personal_categories': 30,
                'most_used_categories': [
                    {'name': 'Food & Dining', 'usage_count': 1250},
                    {'name': 'Transportation', 'usage_count': 980},
                    {'name': 'Education', 'usage_count': 750}
                ],
                'categories_by_user': 8
            }
        }
    }


# Default global categories that should be created
DEFAULT_GLOBAL_CATEGORIES = [
    {
        'name': 'Food & Dining',
        'icon': 'restaurant',
        'color': '#FF5733',
        'is_global': True,
        'user_id': None
    },
    {
        'name': 'Transportation',
        'icon': 'directions_car',
        'color': '#3498DB',
        'is_global': True,
        'user_id': None
    },
    {
        'name': 'Education',
        'icon': 'school',
        'color': '#2ECC71',
        'is_global': True,
        'user_id': None
    },
    {
        'name': 'Healthcare',
        'icon': 'local_hospital',
        'color': '#E74C3C',
        'is_global': True,
        'user_id': None
    },
    {
        'name': 'Entertainment',
        'icon': 'movie',
        'color': '#9B59B6',
        'is_global': True,
        'user_id': None
    },
    {
        'name': 'Shopping',
        'icon': 'shopping_cart',
        'color': '#F39C12',
        'is_global': True,
        'user_id': None
    },
    {
        'name': 'Bills & Utilities',
        'icon': 'receipt',
        'color': '#34495E',
        'is_global': True,
        'user_id': None
    },
    {
        'name': 'Salary & Income',
        'icon': 'attach_money',
        'color': '#27AE60',
        'is_global': True,
        'user_id': None
    },
    {
        'name': 'Freelance',
        'icon': 'work',
        'color': '#8E44AD',
        'is_global': True,
        'user_id': None
    },
    {
        'name': 'Investment',
        'icon': 'trending_up',
        'color': '#16A085',
        'is_global': True,
        'user_id': None
    }
]