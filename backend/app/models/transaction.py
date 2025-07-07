from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import Field, field_validator
from app.models.base import BaseModel, PyObjectId
from app.config.database import get_db
from bson import ObjectId

class Transaction(BaseModel):
    user_id: PyObjectId = Field(...)
    jumlah: float = Field(..., gt=0)  # Amount must be positive
    deskripsi: str = Field(..., min_length=1, max_length=200)
    category_id: PyObjectId = Field(...)
    tipe: str = Field(..., pattern=r'^(pemasukan|pengeluaran)$')
    tanggal: datetime = Field(default_factory=datetime.utcnow)
    bukti_foto: Optional[str] = None  # Path to uploaded file
    is_deleted: bool = Field(default=False)  # Soft delete
    
    @field_validator('deskripsi')
    @classmethod
    def validate_deskripsi(cls, v):
        return v.strip()
    
    @field_validator('tipe')
    @classmethod
    def validate_tipe(cls, v):
        return v.lower()
    
    @field_validator('jumlah')
    @classmethod
    def validate_jumlah(cls, v):
        if v <= 0:
            raise ValueError('Jumlah harus lebih besar dari 0')
        # Round to 2 decimal places
        return round(v, 2)
    
    def save(self):
        return super().save('transactions')
    
    @classmethod
    def find_by_id(cls, transaction_id: str):
        return super().find_by_id('transactions', transaction_id)
    
    @classmethod
    def find_by_user(cls, user_id: str, page: int = 1, limit: int = 10, **filters):
        """Find transactions by user with pagination and filters"""
        try:
            skip = (page - 1) * limit
            filter_dict = {
                'user_id': PyObjectId(user_id),
                'is_deleted': False
            }
            
            # Apply additional filters
            if filters.get('tipe'):
                filter_dict['tipe'] = filters['tipe']
            
            if filters.get('category_id'):
                filter_dict['category_id'] = PyObjectId(filters['category_id'])
            
            if filters.get('date_from') or filters.get('date_to'):
                date_filter = {}
                if filters.get('date_from'):
                    date_filter['$gte'] = filters['date_from']
                if filters.get('date_to'):
                    date_filter['$lte'] = filters['date_to']
                filter_dict['tanggal'] = date_filter
            
            if filters.get('amount_min') or filters.get('amount_max'):
                amount_filter = {}
                if filters.get('amount_min'):
                    amount_filter['$gte'] = filters['amount_min']
                if filters.get('amount_max'):
                    amount_filter['$lte'] = filters['amount_max']
                filter_dict['jumlah'] = amount_filter
            
            if filters.get('search'):
                filter_dict['deskripsi'] = {
                    '$regex': filters['search'],
                    '$options': 'i'
                }
            
            transactions = super().find_all(
                'transactions', 
                filter_dict, 
                limit, 
                skip, 
                [('tanggal', -1)]
            )
            total = super().count_documents('transactions', filter_dict)
            
            return {
                'transactions': transactions,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit,
                    'has_next': page * limit < total,
                    'has_prev': page > 1
                }
            }
        except Exception:
            return {'transactions': [], 'pagination': {}}
    
    @classmethod
    def get_recent_transactions(cls, user_id: str, limit: int = 5):
        """Get recent transactions for user"""
        try:
            filter_dict = {
                'user_id': PyObjectId(user_id),
                'is_deleted': False
            }
            
            return super().find_all(
                'transactions',
                filter_dict,
                limit,
                sort=[('tanggal', -1)]
            )
        except Exception:
            return []
    
    @classmethod
    def get_monthly_summary(cls, user_id: str, year: int = None, month: int = None):
        """Get monthly summary for user"""
        try:
            db = get_db()
            
            # Default to current month if not specified
            if not year or not month:
                now = datetime.utcnow()
                year = year or now.year
                month = month or now.month
            
            # Date range for the month
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            pipeline = [
                {
                    '$match': {
                        'user_id': ObjectId(user_id),
                        'is_deleted': False,
                        'tanggal': {
                            '$gte': start_date,
                            '$lt': end_date
                        }
                    }
                },
                {
                    '$group': {
                        '_id': '$tipe',
                        'total': {'$sum': '$jumlah'},
                        'count': {'$sum': 1}
                    }
                }
            ]
            
            results = list(db.transactions.aggregate(pipeline))
            
            summary = {
                'pemasukan': {'total': 0, 'count': 0},
                'pengeluaran': {'total': 0, 'count': 0},
                'saldo': 0,
                'periode': {
                    'year': year,
                    'month': month,
                    'month_name': datetime(year, month, 1).strftime('%B %Y')
                }
            }
            
            for result in results:
                tipe = result['_id']
                summary[tipe] = {
                    'total': round(result['total'], 2),
                    'count': result['count']
                }
            
            summary['saldo'] = round(
                summary['pemasukan']['total'] - summary['pengeluaran']['total'], 2
            )
            
            return summary
        except Exception:
            return None
    
    @classmethod
    def get_chart_data(cls, user_id: str, period: str = 'monthly', year: int = None, month: int = None):
        """Get chart data for different periods"""
        try:
            db = get_db()
            
            now = datetime.utcnow()
            year = year or now.year
            month = month or now.month
            
            if period == 'daily':
                # Daily data for current month
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1)
                else:
                    end_date = datetime(year, month + 1, 1)
                
                pipeline = [
                    {
                        '$match': {
                            'user_id': ObjectId(user_id),
                            'is_deleted': False,
                            'tanggal': {'$gte': start_date, '$lt': end_date}
                        }
                    },
                    {
                        '$group': {
                            '_id': {
                                'day': {'$dayOfMonth': '$tanggal'},
                                'tipe': '$tipe'
                            },
                            'total': {'$sum': '$jumlah'}
                        }
                    },
                    {
                        '$sort': {'_id.day': 1}
                    }
                ]
            
            elif period == 'weekly':
                # Weekly data for current month
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1)
                else:
                    end_date = datetime(year, month + 1, 1)
                
                pipeline = [
                    {
                        '$match': {
                            'user_id': ObjectId(user_id),
                            'is_deleted': False,
                            'tanggal': {'$gte': start_date, '$lt': end_date}
                        }
                    },
                    {
                        '$group': {
                            '_id': {
                                'week': {'$week': '$tanggal'},
                                'tipe': '$tipe'
                            },
                            'total': {'$sum': '$jumlah'}
                        }
                    },
                    {
                        '$sort': {'_id.week': 1}
                    }
                ]
            
            else:  # monthly
                # Monthly data for current year
                start_date = datetime(year, 1, 1)
                end_date = datetime(year + 1, 1, 1)
                
                pipeline = [
                    {
                        '$match': {
                            'user_id': ObjectId(user_id),
                            'is_deleted': False,
                            'tanggal': {'$gte': start_date, '$lt': end_date}
                        }
                    },
                    {
                        '$group': {
                            '_id': {
                                'month': {'$month': '$tanggal'},
                                'tipe': '$tipe'
                            },
                            'total': {'$sum': '$jumlah'}
                        }
                    },
                    {
                        '$sort': {'_id.month': 1}
                    }
                ]
            
            results = list(db.transactions.aggregate(pipeline))
            return results
        except Exception:
            return []
    
    @classmethod
    def get_spending_by_category(cls, user_id: str, year: int = None, month: int = None):
        """Get spending breakdown by category"""
        try:
            db = get_db()
            
            now = datetime.utcnow()
            year = year or now.year
            month = month or now.month
            
            # Date range for the month
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            pipeline = [
                {
                    '$match': {
                        'user_id': ObjectId(user_id),
                        'is_deleted': False,
                        'tipe': 'pengeluaran',
                        'tanggal': {'$gte': start_date, '$lt': end_date}
                    }
                },
                {
                    '$lookup': {
                        'from': 'categories',
                        'localField': 'category_id',
                        'foreignField': '_id',
                        'as': 'category'
                    }
                },
                {
                    '$unwind': '$category'
                },
                {
                    '$group': {
                        '_id': '$category_id',
                        'category_name': {'$first': '$category.nama'},
                        'category_color': {'$first': '$category.warna'},
                        'category_icon': {'$first': '$category.icon'},
                        'total': {'$sum': '$jumlah'},
                        'count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'total': -1}
                }
            ]
            
            results = list(db.transactions.aggregate(pipeline))
            return results
        except Exception:
            return []
    
    @classmethod
    def get_user_balance(cls, user_id: str):
        """Calculate user's current balance"""
        try:
            db = get_db()
            
            # Get user's initial savings
            from app.models.user import User
            user = User.find_by_id(user_id)
            initial_balance = user.tabungan_awal if user else 0
            
            # Calculate total from transactions
            pipeline = [
                {
                    '$match': {
                        'user_id': ObjectId(user_id),
                        'is_deleted': False
                    }
                },
                {
                    '$group': {
                        '_id': '$tipe',
                        'total': {'$sum': '$jumlah'}
                    }
                }
            ]
            
            results = list(db.transactions.aggregate(pipeline))
            
            pemasukan = 0
            pengeluaran = 0
            
            for result in results:
                if result['_id'] == 'pemasukan':
                    pemasukan = result['total']
                elif result['_id'] == 'pengeluaran':
                    pengeluaran = result['total']
            
            current_balance = initial_balance + pemasukan - pengeluaran
            
            return {
                'initial_balance': round(initial_balance, 2),
                'total_income': round(pemasukan, 2),
                'total_expense': round(pengeluaran, 2),
                'current_balance': round(current_balance, 2)
            }
        except Exception:
            return None
    
    def soft_delete(self):
        """Soft delete transaction"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
        return self.save()
    
    def belongs_to_user(self, user_id: str) -> bool:
        """Check if transaction belongs to user"""
        return str(self.user_id) == user_id