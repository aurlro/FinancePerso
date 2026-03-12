"""
Member schemas
"""

from typing import Optional

from pydantic import Field, field_validator

from .base import BaseSchema, TimestampedSchema


class MemberBase(BaseSchema):
    """Base member fields."""

    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    color: str = Field(default="#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    share_percentage: float = Field(default=50.0, ge=0, le=100)
    monthly_income: Optional[float] = Field(default=None, ge=0)


class MemberCreate(MemberBase):
    """Schema for creating a member."""

    pass


class MemberUpdate(BaseSchema):
    """Schema for updating a member."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    share_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    monthly_income: Optional[float] = Field(default=None, ge=0)


class Member(TimestampedSchema, MemberBase):
    """Full member schema."""

    is_primary: bool = Field(default=False)
    is_active: bool = Field(default=True)
    avatar: Optional[str] = None

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.lower()
        return v


class MemberResponse(BaseSchema):
    """Member API response."""

    data: Member


class MemberStats(BaseSchema):
    """Statistics for a member."""

    total_contributed: float
    share_amount: float
    percentage_of_household: float
