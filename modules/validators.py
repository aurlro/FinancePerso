"""
Input validation module for FinancePerso.
Provides strict validation and sanitization for all user inputs.
Uses Pydantic v2 for robust validation with clear error messages.
"""

import re
import html
from datetime import date, datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ValidationError


class TransactionInput(BaseModel):
    """Validation schema for transaction inputs."""
    label: str = Field(..., min_length=1, max_length=500)
    amount: float = Field(..., gt=-1e9, lt=1e9)
    date: date
    category: Optional[str] = Field(None, max_length=100)
    account_label: Optional[str] = Field(None, max_length=100)
    member: Optional[str] = Field(None, max_length=100)
    
    @field_validator('label')
    @classmethod
    def sanitize_label(cls, v):
        """Sanitize label to prevent XSS and normalize."""
        # Remove control characters
        v = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', v)
        # Strip whitespace
        v = v.strip()
        # Escape HTML
        v = html.escape(v, quote=True)
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount_precision(cls, v):
        """Ensure amount has reasonable decimal precision."""
        # Round to 2 decimal places (currency)
        return round(v, 2)
    
    @field_validator('date')
    @classmethod
    def validate_date_range(cls, v):
        """Ensure date is within reasonable range."""
        min_date = date(2000, 1, 1)
        max_date = date.today() + timedelta(days=365)  # Max 1 year in future
        
        if v < min_date:
            raise ValueError(f"Date cannot be before {min_date}")
        if v > max_date:
            raise ValueError(f"Date cannot be more than 1 year in the future")
        return v


class CategoryInput(BaseModel):
    """Validation schema for category creation."""
    name: str = Field(..., min_length=1, max_length=50)
    emoji: str = Field(default='🏷️', max_length=10)
    is_fixed: int = Field(default=0, ge=0, le=1)
    
    @field_validator('name')
    @classmethod
    def validate_category_name(cls, v):
        """Ensure category name is valid."""
        # Strip and normalize
        v = v.strip()
        
        # Check for reserved names
        reserved = ['inconnu', 'unknown', 'none', 'null', '']
        if v.lower() in reserved:
            raise ValueError(f"'{v}' is a reserved category name")
        
        # Only allow alphanumeric, spaces, and common punctuation
        if not re.match(r'^[\w\s\-\'()]+$', v, re.UNICODE):
            raise ValueError("Category name contains invalid characters")
        
        return v
    
    @field_validator('emoji')
    @classmethod
    def validate_emoji(cls, v):
        """Ensure emoji is valid (basic check)."""
        if len(v) > 10:
            raise ValueError("Emoji too long")
        return v


class LearningRuleInput(BaseModel):
    """Validation schema for learning rules."""
    pattern: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=50)
    priority: int = Field(default=1, ge=1, le=100)
    
    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v):
        """Validate regex pattern safety."""
        v = v.strip()
        
        # Check for dangerous regex patterns
        dangerous_patterns = [
            r'\(.*\*.*\)\+',  # (.*)*+ pattern
            r'\(.*\+.*\)\*',  # (.+)* pattern
            r'\([^)]*\+\)\+',  # (a+)+ pattern
            r'(\(\?\:.*){5,}',  # Too many nested groups
            r'\\',  # Backslash escape attempts
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v):
                raise ValueError("Pattern contains potentially dangerous regex constructs")
        
        # Try to compile
        try:
            re.compile(v, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        
        return v


class BudgetInput(BaseModel):
    """Validation schema for budget inputs."""
    category: str = Field(..., min_length=1, max_length=50)
    amount: float = Field(..., gt=0, lt=1e9)
    
    @field_validator('amount')
    @classmethod
    def validate_budget_amount(cls, v):
        """Ensure budget amount is reasonable."""
        if v > 1_000_000:
            raise ValueError("Budget amount seems unrealistic (> 1M)")
        return round(v, 2)


class MemberInput(BaseModel):
    """Validation schema for member creation."""
    name: str = Field(..., min_length=1, max_length=50)
    member_type: str = Field(default='HOUSEHOLD', pattern='^(HOUSEHOLD|EXTERNAL)$')
    
    @field_validator('name')
    @classmethod
    def validate_member_name(cls, v):
        """Sanitize member name."""
        v = v.strip()
        # Remove HTML tags
        v = re.sub(r'<[^>]+>', '', v)
        # Escape HTML entities
        v = html.escape(v, quote=True)
        return v


class TagInput(BaseModel):
    """Validation schema for tags."""
    name: str = Field(..., min_length=1, max_length=30)
    
    @field_validator('name')
    @classmethod
    def validate_tag(cls, v):
        """Normalize and validate tag."""
        v = v.strip().lower()
        
        # Remove special characters
        v = re.sub(r'[^\w\-]', '', v)
        
        if len(v) < 1:
            raise ValueError("Tag cannot be empty after sanitization")
        
        return v


def validate_transaction(label: str, amount: float, tx_date: date, 
                        category: Optional[str] = None) -> tuple[bool, Optional[str]]:
    """
    Validate transaction data.
    
    Args:
        label: Transaction label
        amount: Transaction amount
        tx_date: Transaction date
        category: Optional category
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        TransactionInput(
            label=label,
            amount=amount,
            date=tx_date,
            category=category
        )
        return True, None
    except ValidationError as e:
        # Get first error message
        error_msg = e.errors()[0]['msg']
        return False, error_msg


def sanitize_string_input(value: str, max_length: int = 255, 
                         allow_html: bool = False) -> str:
    """
    Sanitize any string input.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        allow_html: Whether to allow HTML (default: False)
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Strip whitespace
    value = value.strip()
    
    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length]
    
    # Remove control characters
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    
    if not allow_html:
        # Escape HTML
        value = html.escape(value, quote=True)
    
    return value


def validate_sql_identifier(identifier: str) -> tuple[bool, Optional[str]]:
    """
    Validate that a string is safe to use as SQL identifier (table/column name).
    
    Args:
        identifier: String to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not identifier:
        return False, "Identifier cannot be empty"
    
    # Only allow alphanumeric and underscore
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        return False, "Invalid SQL identifier format"
    
    # Check for SQL keywords
    sql_keywords = {
        'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter',
        'table', 'from', 'where', 'and', 'or', 'not', 'null', 'true', 'false'
    }
    
    if identifier.lower() in sql_keywords:
        return False, f"'{identifier}' is a reserved SQL keyword"
    
    return True, None


class ValidationUtils:
    """Utility class for common validation operations."""
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """Validate file extension."""
        if not filename:
            return False
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        return ext in [e.lower().strip('.') for e in allowed_extensions]
    
    @staticmethod
    def validate_file_size(size_bytes: int, max_size_mb: int = 10) -> tuple[bool, str]:
        """Validate file size."""
        max_bytes = max_size_mb * 1024 * 1024
        if size_bytes > max_bytes:
            return False, f"File too large ({size_bytes / 1024 / 1024:.1f} MB > {max_size_mb} MB)"
        return True, ""
    
    @staticmethod
    def sanitize_search_query(query: str) -> str:
        """Sanitize search query input."""
        # Remove special regex characters that could cause issues
        query = re.sub(r'[+*?{}[\]\\]', '', query)
        # Limit length
        query = query[:100]
        return query.strip()


# Export all validators
__all__ = [
    'TransactionInput',
    'CategoryInput',
    'LearningRuleInput',
    'BudgetInput',
    'MemberInput',
    'TagInput',
    'validate_transaction',
    'sanitize_string_input',
    'validate_sql_identifier',
    'ValidationUtils',
]
