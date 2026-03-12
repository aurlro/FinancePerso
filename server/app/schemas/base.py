"""
Base schemas shared across all models
"""

from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampedSchema(BaseSchema):
    """Schema with timestamp fields."""

    id: str = Field(..., description="Unique identifier (UUID)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response."""

    items: list[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")


class SuccessResponse(BaseSchema):
    """Standard success response."""

    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseSchema):
    """Standard error response."""

    success: bool = False
    error: str
    code: Optional[str] = None
    details: Optional[dict] = None


class HealthCheck(BaseSchema):
    """Health check response."""

    status: str = "ok"
    version: str
    timestamp: datetime
    database: str = "connected"
