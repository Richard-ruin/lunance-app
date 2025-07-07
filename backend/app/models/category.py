from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field, field_validator
from app.models.base import BaseModel, PyObjectId
from app.config.database import get_db

class Category(BaseModel):
    nama: str = Field(..., min_length=1, max_length=50)
    icon: str = Field(..., min_length=1, max_length=100)  # nama icon atau path
    warna: str = Field(..., pattern=r'^#[0-9a-fA-F]{6}$')  # hex color validation
    tipe: str = Field(..., pattern=r'^(pemasukan|pengeluaran)$')
    is_global: bool = Field(default=False)  # True=admin managed, False=user managed
    created_by: Optional[PyObjectId] = Field(default=None)  # user_id, null jika global
    is_active: bool = Field(default=True)
    
    @field_validator('nama')
    @classmethod
    def validate_nama(cls, v):
        return v.strip().title()
    
    @field_validator('warna')
    @classmethod
    def validate_warna(cls, v):
        return v.upper()
    
    @field_validator('tipe')
    @classmethod
    def validate_tipe(cls, v):
        return v.lower()
    
    def save(self):
        return super().save('categories')
    
    @classmethod
    def find_by_id(cls, category_id: str):
        return super().find_by_id('categories', category_id)
    
    @classmethod
    def find_all(cls, **kwargs):
        return super().find_all('categories', **kwargs)
    
    @classmethod
    def find_global_categories(cls, tipe: str = None, is_active: bool = True):
        """Find all global categories"""
        try:
            filter_dict = {'is_global': True}
            if tipe:
                filter_dict['tipe'] = tipe
            if is_active is not None:
                filter_dict['is_active'] = is_active
            
            return super().find_all('categories', filter_dict, sort=[('nama', 1)])
        except Exception:
            return []
    
    @classmethod
    def find_user_categories(cls, user_id: str, tipe: str = None, is_active: bool = True):
        """Find user's personal categories"""
        try:
            filter_dict = {
                'is_global': False,
                'created_by': PyObjectId(user_id)
            }
            if tipe:
                filter_dict['tipe'] = tipe
            if is_active is not None:
                filter_dict['is_active'] = is_active
            
            return super().find_all('categories', filter_dict, sort=[('nama', 1)])
        except Exception:
            return []
    
    @classmethod
    def find_accessible_categories(cls, user_id: str, tipe: str = None, is_active: bool = True):
        """Find categories accessible by user (global + personal)"""
        try:
            # Global categories
            global_filter = {'is_global': True}
            if tipe:
                global_filter['tipe'] = tipe
            if is_active is not None:
                global_filter['is_active'] = is_active
            
            # Personal categories
            personal_filter = {
                'is_global': False,
                'created_by': PyObjectId(user_id)
            }
            if tipe:
                personal_filter['tipe'] = tipe
            if is_active is not None:
                personal_filter['is_active'] = is_active
            
            # Combine results
            global_categories = super().find_all('categories', global_filter)
            personal_categories = super().find_all('categories', personal_filter)
            
            all_categories = global_categories + personal_categories
            # Sort by nama
            all_categories.sort(key=lambda x: x.nama)
            
            return all_categories
        except Exception:
            return []
    
    @classmethod
    def find_by_name_and_user(cls, nama: str, user_id: str = None, is_global: bool = False):
        """Check if category name exists for user or globally"""
        try:
            db = get_db()
            
            if is_global:
                filter_dict = {
                    'nama': nama.strip().title(),
                    'is_global': True
                }
            else:
                filter_dict = {
                    'nama': nama.strip().title(),
                    'is_global': False,
                    'created_by': PyObjectId(user_id) if user_id else None
                }
            
            doc = db.categories.find_one(filter_dict)
            if doc:
                return cls(**doc)
            return None
        except Exception:
            return None
    
    @classmethod
    def get_category_usage_analytics(cls):
        """Get category usage analytics for admin"""
        try:
            db = get_db()
            
            # Aggregate categories with transaction count
            pipeline = [
                {
                    '$lookup': {
                        'from': 'transactions',
                        'localField': '_id',
                        'foreignField': 'category_id',
                        'as': 'transactions'
                    }
                },
                {
                    '$addFields': {
                        'usage_count': {'$size': '$transactions'}
                    }
                },
                {
                    '$project': {
                        'nama': 1,
                        'tipe': 1,
                        'is_global': 1,
                        'is_active': 1,
                        'created_by': 1,
                        'usage_count': 1,
                        'created_at': 1
                    }
                },
                {
                    '$sort': {'usage_count': -1}
                }
            ]
            
            results = list(db.categories.aggregate(pipeline))
            return results
        except Exception:
            return []
    
    def is_accessible_by_user(self, user_id: str) -> bool:
        """Check if category is accessible by user"""
        if self.is_global:
            return True
        
        if self.created_by and str(self.created_by) == user_id:
            return True
        
        return False
    
    def can_be_modified_by_user(self, user_id: str, is_admin: bool = False) -> bool:
        """Check if category can be modified by user"""
        if is_admin:
            return True
        
        # Only personal categories can be modified by non-admin users
        if not self.is_global and self.created_by and str(self.created_by) == user_id:
            return True
        
        return False