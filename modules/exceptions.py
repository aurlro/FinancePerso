"""
Custom exception classes for FinancePerso application.
Provides specific exception types for better error handling and debugging.
"""

class FinancePersoException(Exception):
    """Base exception for all FinancePerso-specific errors."""
    pass


class DatabaseError(FinancePersoException):
    """Raised when database operations fail."""
    pass


class ValidationError(FinancePersoException):
    """Raised when input validation fails."""
    pass


class ImportError(FinancePersoException):
    """Raised when CSV/file import operations fail."""
    pass


class AIProviderError(FinancePersoException):
    """Raised when AI provider API calls fail."""
    pass


class ConfigurationError(FinancePersoException):
    """Raised when configuration is invalid or missing."""
    pass


class CategorizationError(FinancePersoException):
    """Raised when transaction categorization fails."""
    pass


class RuleError(FinancePersoException):
    """Raised when learning rule operations fail."""
    pass
