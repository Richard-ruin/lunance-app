from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union
from datetime import datetime
from datetime import date as date_type  # Alias to avoid conflicts
from enum import Enum
from decimal import Decimal


class TransactionType(str, Enum):
    """Transaction type enumeration."""
    INCOME = "income"
    EXPENSE = "expense"


class TransactionBase(BaseModel):
    """Base transaction model."""
    category_id: str = Field(..., description="Category ID")
    transaction_type: TransactionType = Field(..., description="Transaction type (income/expense)")
    amount: float = Field(..., gt=0, description="Transaction amount")
    description: str = Field(..., min_length=1, max_length=255, description="Transaction description")
    transaction_date: date_type = Field(..., description="Transaction date")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate transaction amount."""
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 999999999.99:  # Max 999 million
            raise ValueError('Amount is too large')
        # Round to 2 decimal places
        return round(v, 2)

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate and clean description."""
        description = v.strip()
        if not description:
            raise ValueError('Description cannot be empty')
        return description

    @field_validator('transaction_date')
    @classmethod
    def validate_date(cls, v: date_type) -> date_type:
        """Validate transaction date."""
        from datetime import date as date_class
        today = date_class.today()
        if v > today:
            raise ValueError('Transaction date cannot be in the future')
        # Allow transactions up to 5 years in the past
        if (today - v).days > 5 * 365:
            raise ValueError('Transaction date cannot be more than 5 years in the past')
        return v

    model_config = {
        # Updated for Pydantic v2
        'populate_by_name': True,  # Replaces allow_population_by_field_name
        'json_encoders': {
            date_type: lambda v: v.isoformat() if v else None
        }
    }


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating transaction information."""
    category_id: Optional[str] = Field(None, description="Category ID")
    transaction_type: Optional[TransactionType] = Field(None, description="Transaction type")
    amount: Optional[float] = Field(None, gt=0, description="Transaction amount")
    description: Optional[str] = Field(None, min_length=1, max_length=255, description="Description")
    transaction_date: Optional[date_type] = Field(None, description="Transaction date")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Optional[float]) -> Optional[float]:
        """Validate amount if provided."""
        if v is None:
            return v
        return TransactionBase.validate_amount(v)

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description if provided."""
        if v is None:
            return v
        return TransactionBase.validate_description(v)

    @field_validator('transaction_date')
    @classmethod
    def validate_date(cls, v: Optional[date_type]) -> Optional[date_type]:
        """Validate date if provided."""
        if v is None:
            return v
        return TransactionBase.validate_date(v)


class TransactionInDB(TransactionBase):
    """Transaction model as stored in database."""
    id: Optional[str] = Field(None, alias="_id", description="Transaction ID")
    user_id: str = Field(..., description="User ID who created the transaction")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    model_config = {
        'populate_by_name': True,  # Updated for Pydantic v2
        'json_schema_extra': {
            'example': {
                'user_id': '507f1f77bcf86cd799439011',
                'category_id': '507f1f77bcf86cd799439012',
                'transaction_type': 'expense',
                'amount': 25000.0,
                'description': 'Lunch at campus cafeteria',
                'transaction_date': '2024-01-15'
            }
        }
    }


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""
    id: Optional[str] = Field(None, alias="_id", description="Transaction ID")
    user_id: str = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        'populate_by_name': True,  # Updated for Pydantic v2
        'from_attributes': True
    }


class TransactionWithCategory(TransactionResponse):
    """Transaction response with category information."""
    category_name: str = Field(..., description="Category name")
    category_icon: str = Field(..., description="Category icon")
    category_color: str = Field(..., description="Category color")

    model_config = {
        'populate_by_name': True,  # Updated for Pydantic v2
        'from_attributes': True
    }


class TransactionSummary(BaseModel):
    """Transaction summary for dashboard."""
    total_income: float = Field(..., description="Total income amount")
    total_expense: float = Field(..., description="Total expense amount")
    net_amount: float = Field(..., description="Net amount (income - expense)")
    transaction_count: int = Field(..., description="Total number of transactions")
    average_transaction: float = Field(..., description="Average transaction amount")
    largest_expense: Optional[float] = Field(None, description="Largest single expense")
    largest_income: Optional[float] = Field(None, description="Largest single income")

    model_config = {
        'json_schema_extra': {
            'example': {
                'total_income': 2500000.0,
                'total_expense': 1800000.0,
                'net_amount': 700000.0,
                'transaction_count': 45,
                'average_transaction': 95555.56,
                'largest_expense': 500000.0,
                'largest_income': 1000000.0
            }
        }
    }


class MonthlyTransactionSummary(BaseModel):
    """Monthly transaction summary."""
    year: int = Field(..., description="Year")
    month: int = Field(..., ge=1, le=12, description="Month")
    month_name: str = Field(..., description="Month name")
    total_income: float = Field(..., description="Total income for the month")
    total_expense: float = Field(..., description="Total expense for the month")
    net_amount: float = Field(..., description="Net amount for the month")
    transaction_count: int = Field(..., description="Number of transactions")

    model_config = {
        'json_schema_extra': {
            'example': {
                'year': 2024,
                'month': 1,
                'month_name': 'January',
                'total_income': 1000000.0,
                'total_expense': 750000.0,
                'net_amount': 250000.0,
                'transaction_count': 25
            }
        }
    }


class CategoryTransactionSummary(BaseModel):
    """Transaction summary by category."""
    category_id: str = Field(..., description="Category ID")
    category_name: str = Field(..., description="Category name")
    category_icon: str = Field(..., description="Category icon")
    category_color: str = Field(..., description="Category color")
    total_amount: float = Field(..., description="Total amount for this category")
    transaction_count: int = Field(..., description="Number of transactions")
    percentage: float = Field(..., description="Percentage of total expenses/income")
    average_amount: float = Field(..., description="Average transaction amount")

    model_config = {
        'json_schema_extra': {
            'example': {
                'category_id': '507f1f77bcf86cd799439012',
                'category_name': 'Food & Dining',
                'category_icon': 'restaurant',
                'category_color': '#FF5733',
                'total_amount': 450000.0,
                'transaction_count': 18,
                'percentage': 25.5,
                'average_amount': 25000.0
            }
        }
    }


class DailyTransactionSummary(BaseModel):
    """Daily transaction summary."""
    transaction_date: date_type = Field(..., description="Transaction date")
    total_income: float = Field(..., description="Total income for the day")
    total_expense: float = Field(..., description="Total expense for the day")
    net_amount: float = Field(..., description="Net amount for the day")
    transaction_count: int = Field(..., description="Number of transactions")

    model_config = {
        'json_schema_extra': {
            'example': {
                'transaction_date': '2024-01-15',
                'total_income': 0.0,
                'total_expense': 75000.0,
                'net_amount': -75000.0,
                'transaction_count': 3
            }
        }
    }


class TransactionFilters(BaseModel):
    """Filters for transaction queries."""
    start_date: Optional[date_type] = Field(None, description="Start date filter")
    end_date: Optional[date_type] = Field(None, description="End date filter")
    category_id: Optional[str] = Field(None, description="Category ID filter")
    transaction_type: Optional[TransactionType] = Field(None, description="Transaction type filter")
    min_amount: Optional[float] = Field(None, ge=0, description="Minimum amount filter")
    max_amount: Optional[float] = Field(None, ge=0, description="Maximum amount filter")
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="Search in description")

    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v: Optional[date_type], info) -> Optional[date_type]:
        """Validate that end_date is after start_date."""
        if v is not None and hasattr(info, 'data') and info.data and 'start_date' in info.data and info.data['start_date'] is not None:
            if v < info.data['start_date']:
                raise ValueError('End date must be after start date')
        return v

    @field_validator('max_amount')
    @classmethod
    def validate_amount_range(cls, v: Optional[float], info) -> Optional[float]:
        """Validate that max_amount is greater than min_amount."""
        if v is not None and hasattr(info, 'data') and info.data and 'min_amount' in info.data and info.data['min_amount'] is not None:
            if v < info.data['min_amount']:
                raise ValueError('Maximum amount must be greater than minimum amount')
        return v


class TransactionBulkCreate(BaseModel):
    """Schema for bulk transaction creation."""
    transactions: List[TransactionCreate] = Field(..., max_length=100, description="List of transactions to create")

    @field_validator('transactions')
    @classmethod
    def validate_transactions(cls, v: List[TransactionCreate]) -> List[TransactionCreate]:
        """Validate transactions list."""
        if len(v) == 0:
            raise ValueError('At least one transaction is required')
        if len(v) > 100:
            raise ValueError('Cannot create more than 100 transactions at once')
        return v


class TransactionExport(BaseModel):
    """Schema for transaction export."""
    export_format: str = Field(default="csv", description="Export format (csv, excel)")
    filters: Optional[TransactionFilters] = Field(None, description="Export filters")

    @field_validator('export_format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate export format."""
        if v not in ['csv', 'excel']:
            raise ValueError('Format must be either csv or excel')
        return v.lower()