# app/models/common.py
"""Common models and schemas used across the application."""

from pydantic import BaseModel, Field, field_validator
from typing import Generic, TypeVar, List, Optional, Any
from enum import Enum
import math


class SortOrder(str, Enum):
    """Sort order enumeration."""
    ASC = "asc"
    DESC = "desc"


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(default=1, ge=1, description="Page number (starts from 1)")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")

    @field_validator('per_page')
    @classmethod
    def validate_per_page(cls, v: int) -> int:
        """Validate per_page limits."""
        if v > 100:
            return 100
        return v

    def get_skip(self) -> int:
        """Calculate number of items to skip for pagination."""
        return (self.page - 1) * self.per_page

    def get_limit(self) -> int:
        """Get limit for database query."""
        return self.per_page


T = TypeVar('T')


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    current_page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    has_next: bool = Field(..., description="Whether there is a next page")
    previous_page: Optional[int] = Field(None, description="Previous page number")
    next_page: Optional[int] = Field(None, description="Next page number")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T] = Field(..., description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        per_page: int
    ) -> 'PaginatedResponse[T]':
        """
        Create paginated response with calculated metadata.
        
        Args:
            items: List of items for current page
            total: Total number of items
            page: Current page number
            per_page: Items per page
            
        Returns:
            PaginatedResponse with metadata
        """
        total_pages = math.ceil(total / per_page) if total > 0 else 1
        has_previous = page > 1
        has_next = page < total_pages
        
        previous_page = page - 1 if has_previous else None
        next_page = page + 1 if has_next else None
        
        meta = PaginationMeta(
            current_page=page,
            per_page=per_page,
            total_items=total,
            total_pages=total_pages,
            has_previous=has_previous,
            has_next=has_next,
            previous_page=previous_page,
            next_page=next_page
        )
        
        return cls(items=items, meta=meta)


class ErrorDetail(BaseModel):
    """Error detail model."""
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    field: Optional[str] = Field(None, description="Field that caused the error")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: bool = Field(default=True, description="Whether this is an error response")
    message: str = Field(..., description="Main error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    timestamp: str = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")


class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = Field(default=True, description="Whether the operation was successful")
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: str = Field(..., description="Response timestamp")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")
    database: dict = Field(..., description="Database status")
    uptime: float = Field(..., description="Uptime in seconds")


class BulkOperationResult(BaseModel):
    """Result of bulk operations."""
    total_processed: int = Field(..., description="Total items processed")
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    errors: List[ErrorDetail] = Field(default=[], description="List of errors that occurred")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_processed == 0:
            return 0.0
        return (self.successful / self.total_processed) * 100


class DateRange(BaseModel):
    """Date range filter."""
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format."""
        if v is None:
            return v
        
        from datetime import datetime
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')


class TimeRange(BaseModel):
    """Time range filter."""
    start_time: Optional[str] = Field(None, description="Start time (HH:MM)")
    end_time: Optional[str] = Field(None, description="End time (HH:MM)")

    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate time format."""
        if v is None:
            return v
        
        from datetime import datetime
        try:
            datetime.strptime(v, '%H:%M')
            return v
        except ValueError:
            raise ValueError('Time must be in HH:MM format')


class AmountRange(BaseModel):
    """Amount range filter."""
    min_amount: Optional[float] = Field(None, ge=0, description="Minimum amount")
    max_amount: Optional[float] = Field(None, ge=0, description="Maximum amount")

    @field_validator('max_amount')
    @classmethod
    def validate_max_amount(cls, v: Optional[float], info) -> Optional[float]:
        """Validate that max_amount is greater than min_amount."""
        if v is not None and hasattr(info, 'data') and info.data and 'min_amount' in info.data:
            min_amount = info.data['min_amount']
            if min_amount is not None and v < min_amount:
                raise ValueError('Maximum amount must be greater than minimum amount')
        return v


class SearchParams(BaseModel):
    """Search parameters."""
    query: Optional[str] = Field(None, min_length=1, max_length=100, description="Search query")
    search_in: Optional[List[str]] = Field(default=[], description="Fields to search in")
    exact_match: bool = Field(default=False, description="Whether to use exact match")
    case_sensitive: bool = Field(default=False, description="Whether search is case sensitive")

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: Optional[str]) -> Optional[str]:
        """Validate search query."""
        if v is None:
            return v
        
        # Remove extra whitespace
        query = v.strip()
        if not query:
            return None
        
        # Basic sanitization - remove potentially harmful characters
        import re
        query = re.sub(r'[<>"\']', '', query)
        
        return query


class FilterParams(BaseModel):
    """Common filter parameters."""
    date_range: Optional[DateRange] = None
    amount_range: Optional[AmountRange] = None
    search: Optional[SearchParams] = None
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    created_after: Optional[str] = Field(None, description="Filter items created after this date")
    created_before: Optional[str] = Field(None, description="Filter items created before this date")


class ExportParams(BaseModel):
    """Export parameters."""
    format: str = Field(default="csv", description="Export format")
    include_headers: bool = Field(default=True, description="Include headers in export")
    fields: Optional[List[str]] = Field(None, description="Specific fields to export")
    filters: Optional[FilterParams] = Field(None, description="Filters to apply")

    @field_validator('format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate export format."""
        allowed_formats = ['csv', 'excel', 'json', 'pdf']
        if v.lower() not in allowed_formats:
            raise ValueError(f'Format must be one of: {", ".join(allowed_formats)}')
        return v.lower()


class ImportResult(BaseModel):
    """Import operation result."""
    total_rows: int = Field(..., description="Total rows in import file")
    processed_rows: int = Field(..., description="Number of rows processed")
    successful_rows: int = Field(..., description="Number of successfully imported rows")
    failed_rows: int = Field(..., description="Number of failed rows")
    warnings: List[str] = Field(default=[], description="Import warnings")
    errors: List[ErrorDetail] = Field(default=[], description="Import errors")
    
    @property
    def success_rate(self) -> float:
        """Calculate import success rate."""
        if self.total_rows == 0:
            return 0.0
        return (self.successful_rows / self.total_rows) * 100


class AuditLog(BaseModel):
    """Audit log entry."""
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="ID of affected resource")
    user_id: str = Field(..., description="User who performed the action")
    timestamp: str = Field(..., description="When the action was performed")
    ip_address: Optional[str] = Field(None, description="IP address of the user")
    user_agent: Optional[str] = Field(None, description="User agent string")
    changes: Optional[dict] = Field(None, description="What was changed")
    metadata: Optional[dict] = Field(None, description="Additional metadata")


class APIKeyInfo(BaseModel):
    """API key information."""
    key_id: str = Field(..., description="API key ID")
    name: str = Field(..., description="API key name")
    created_at: str = Field(..., description="Creation timestamp")
    last_used: Optional[str] = Field(None, description="Last used timestamp")
    is_active: bool = Field(..., description="Whether the key is active")
    permissions: List[str] = Field(..., description="Permissions granted to this key")
    rate_limit: Optional[int] = Field(None, description="Rate limit for this key")


class SystemInfo(BaseModel):
    """System information."""
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment (development, staging, production)")
    uptime: float = Field(..., description="System uptime in seconds")
    database_status: str = Field(..., description="Database connection status")
    cache_status: str = Field(..., description="Cache system status")
    queue_status: str = Field(..., description="Queue system status")
    total_users: int = Field(..., description="Total number of users")
    total_transactions: int = Field(..., description="Total number of transactions")
    disk_usage: Optional[dict] = Field(None, description="Disk usage information")
    memory_usage: Optional[dict] = Field(None, description="Memory usage information")