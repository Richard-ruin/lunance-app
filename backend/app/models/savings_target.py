from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class SavingsTargetBase(BaseModel):
    """Base savings target model."""
    target_name: str = Field(..., min_length=2, max_length=100, description="Savings target name")
    target_amount: float = Field(..., gt=0, description="Target amount to save")
    target_date: date = Field(..., description="Target completion date")

    @field_validator('target_name')
    @classmethod
    def validate_target_name(cls, v: str) -> str:
        """Validate and clean target name."""
        name = v.strip()
        if not name:
            raise ValueError('Target name cannot be empty')
        return name

    @field_validator('target_amount')
    @classmethod
    def validate_target_amount(cls, v: float) -> float:
        """Validate target amount."""
        if v <= 0:
            raise ValueError('Target amount must be greater than 0')
        if v > 9999999999.99:  # Max 9.9 billion
            raise ValueError('Target amount is too large')
        # Round to 2 decimal places
        return round(v, 2)

    @field_validator('target_date')
    @classmethod
    def validate_target_date(cls, v: date) -> date:
        """Validate target date."""
        today = date.today()
        if v <= today:
            raise ValueError('Target date must be in the future')
        # Allow targets up to 10 years in the future
        if (v - today).days > 10 * 365:
            raise ValueError('Target date cannot be more than 10 years in the future')
        return v


class SavingsTargetCreate(SavingsTargetBase):
    """Schema for creating a new savings target."""
    current_amount: Optional[float] = Field(default=0.0, ge=0, description="Current saved amount")

    @field_validator('current_amount')
    @classmethod
    def validate_current_amount(cls, v: Optional[float]) -> float:
        """Validate current amount."""
        if v is None:
            return 0.0
        if v < 0:
            raise ValueError('Current amount cannot be negative')
        return round(v, 2)

    @model_validator(mode='after')
    def validate_amounts(self):
        """Validate that current amount doesn't exceed target amount."""
        if self.current_amount > self.target_amount:
            raise ValueError('Current amount cannot be greater than target amount')
        return self


class SavingsTargetUpdate(BaseModel):
    """Schema for updating savings target information."""
    target_name: Optional[str] = Field(None, min_length=2, max_length=100)
    target_amount: Optional[float] = Field(None, gt=0)
    current_amount: Optional[float] = Field(None, ge=0)
    target_date: Optional[date] = Field(None)

    @field_validator('target_name')
    @classmethod
    def validate_target_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate target name if provided."""
        if v is None:
            return v
        return SavingsTargetBase.validate_target_name(v)

    @field_validator('target_amount')
    @classmethod
    def validate_target_amount(cls, v: Optional[float]) -> Optional[float]:
        """Validate target amount if provided."""
        if v is None:
            return v
        return SavingsTargetBase.validate_target_amount(v)

    @field_validator('current_amount')
    @classmethod
    def validate_current_amount(cls, v: Optional[float]) -> Optional[float]:
        """Validate current amount if provided."""
        if v is None:
            return v
        if v < 0:
            raise ValueError('Current amount cannot be negative')
        return round(v, 2)

    @field_validator('target_date')
    @classmethod
    def validate_target_date(cls, v: Optional[date]) -> Optional[date]:
        """Validate target date if provided."""
        if v is None:
            return v
        return SavingsTargetBase.validate_target_date(v)


class SavingsTargetInDB(SavingsTargetBase):
    """Savings target model as stored in database."""
    id: Optional[str] = Field(None, alias="_id", description="Savings target ID")
    user_id: str = Field(..., description="User ID who created the target")
    current_amount: float = Field(default=0.0, ge=0, description="Current saved amount")
    is_achieved: bool = Field(default=False, description="Whether target is achieved")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    model_config = {
        'populate_by_name': True,
        'json_schema_extra': {
            'example': {
                'user_id': '507f1f77bcf86cd799439011',
                'target_name': 'New Laptop',
                'target_amount': 15000000.0,
                'current_amount': 5000000.0,
                'target_date': '2024-12-31',
                'is_achieved': False
            }
        }
    }


class SavingsTargetResponse(SavingsTargetBase):
    """Schema for savings target response."""
    id: Optional[str] = Field(None, alias="_id", description="Savings target ID")
    user_id: str = Field(..., description="User ID")
    current_amount: float = Field(..., description="Current saved amount")
    is_achieved: bool = Field(..., description="Whether target is achieved")
    progress_percentage: float = Field(..., description="Progress percentage")
    days_remaining: int = Field(..., description="Days remaining to target date")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        'populate_by_name': True,
        'from_attributes': True
    }


class SavingsTargetWithProjection(SavingsTargetResponse):
    """Savings target with projection calculations."""
    monthly_target: float = Field(..., description="Monthly savings needed")
    weekly_target: float = Field(..., description="Weekly savings needed")
    daily_target: float = Field(..., description="Daily savings needed")
    projected_completion_date: Optional[date] = Field(None, description="Projected completion date based on current savings rate")
    is_on_track: bool = Field(..., description="Whether on track to meet target")
    savings_rate_needed: float = Field(..., description="Monthly savings rate needed")

    model_config = {
        'json_schema_extra': {
            'example': {
                'target_name': 'Emergency Fund',
                'target_amount': 10000000.0,
                'current_amount': 3000000.0,
                'target_date': '2024-12-31',
                'progress_percentage': 30.0,
                'days_remaining': 180,
                'monthly_target': 1166666.67,
                'weekly_target': 269230.77,
                'daily_target': 38461.54,
                'is_on_track': True,
                'savings_rate_needed': 1166666.67
            }
        }
    }


class SavingsContribution(BaseModel):
    """Schema for adding money to savings target."""
    amount: float = Field(..., gt=0, description="Amount to add to savings")
    description: Optional[str] = Field(None, max_length=255, description="Optional note about the contribution")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate contribution amount."""
        if v <= 0:
            raise ValueError('Contribution amount must be greater than 0')
        if v > 999999999.99:  # Max 999 million
            raise ValueError('Contribution amount is too large')
        return round(v, 2)

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description if provided."""
        if v is None:
            return v
        description = v.strip()
        return description if description else None


class SavingsWithdrawal(BaseModel):
    """Schema for withdrawing money from savings target."""
    amount: float = Field(..., gt=0, description="Amount to withdraw from savings")
    description: Optional[str] = Field(None, max_length=255, description="Reason for withdrawal")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate withdrawal amount."""
        if v <= 0:
            raise ValueError('Withdrawal amount must be greater than 0')
        return round(v, 2)

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description if provided."""
        if v is None:
            return v
        description = v.strip()
        return description if description else None


class SavingsTargetSummary(BaseModel):
    """Summary of all savings targets for a user."""
    total_targets: int = Field(..., description="Total number of savings targets")
    active_targets: int = Field(..., description="Number of active (not achieved) targets")
    achieved_targets: int = Field(..., description="Number of achieved targets")
    total_target_amount: float = Field(..., description="Sum of all target amounts")
    total_current_amount: float = Field(..., description="Sum of all current amounts")
    overall_progress: float = Field(..., description="Overall progress percentage")
    nearest_target_date: Optional[date] = Field(None, description="Date of nearest target")
    monthly_savings_needed: float = Field(..., description="Total monthly savings needed for all targets")

    model_config = {
        'json_schema_extra': {
            'example': {
                'total_targets': 5,
                'active_targets': 3,
                'achieved_targets': 2,
                'total_target_amount': 50000000.0,
                'total_current_amount': 25000000.0,
                'overall_progress': 50.0,
                'nearest_target_date': '2024-06-30',
                'monthly_savings_needed': 4166666.67
            }
        }
    }


class SavingsTargetHistory(BaseModel):
    """Savings target transaction history."""
    id: str = Field(..., description="History entry ID")
    savings_target_id: str = Field(..., description="Savings target ID")
    action: str = Field(..., description="Action type (contribution/withdrawal/achievement)")
    amount: float = Field(..., description="Amount involved")
    balance_before: float = Field(..., description="Balance before transaction")
    balance_after: float = Field(..., description="Balance after transaction")
    description: Optional[str] = Field(None, description="Transaction description")
    created_at: datetime = Field(..., description="Transaction timestamp")

    model_config = {
        'json_schema_extra': {
            'example': {
                'savings_target_id': '507f1f77bcf86cd799439012',
                'action': 'contribution',
                'amount': 500000.0,
                'balance_before': 2500000.0,
                'balance_after': 3000000.0,
                'description': 'Monthly salary savings',
                'created_at': '2024-01-15T10:30:00'
            }
        }
    }


class SavingsTargetAnalytics(BaseModel):
    """Analytics data for savings targets."""
    average_completion_rate: float = Field(..., description="Average completion rate across all targets")
    most_common_target_amount: float = Field(..., description="Most common target amount range")
    average_time_to_complete: int = Field(..., description="Average days to complete targets")
    success_rate: float = Field(..., description="Percentage of targets successfully completed")
    total_saved: float = Field(..., description="Total amount saved across all targets")
    active_savers: int = Field(..., description="Number of users with active savings targets")

    model_config = {
        'json_schema_extra': {
            'example': {
                'average_completion_rate': 67.5,
                'most_common_target_amount': 5000000.0,
                'average_time_to_complete': 245,
                'success_rate': 73.2,
                'total_saved': 125000000.0,
                'active_savers': 150
            }
        }
    }