"""
Error handling utilities for FinancePerso.
Provides consistent error handling and user-friendly error messages.
"""
import streamlit as st
from functools import wraps
from typing import Callable, Any, Optional, Type, Tuple
import logging

logger = logging.getLogger(__name__)


# User-friendly error messages for common errors
ERROR_MESSAGES = {
    # Database errors
    "database_locked": "🔒 La base de données est temporairement verrouillée. Réessayez dans quelques secondes.",
    "database_busy": "⏳ La base de données est occupée. Veuillez patienter un instant.",
    "unique_constraint": "🚫 Cet élément existe déjà. Veuillez choisir un nom différent.",
    "foreign_key": "🔗 Cet élément est utilisé ailleurs et ne peut pas être supprimé.",
    "not_found": "🔍 Élément introuvable. Il a peut-être été supprimé.",
    
    # File errors
    "file_not_found": "📁 Fichier introuvable. Vérifiez le chemin du fichier.",
    "permission_denied": "🔒 Permission refusée. Vérifiez les droits d'accès.",
    "file_too_large": "📄 Le fichier est trop volumineux. Limite: 10 Mo.",
    "invalid_format": "📄 Format de fichier invalide. Vérifiez le type de fichier.",
    
    # AI/Service errors
    "ai_not_available": "🤖 Le service IA n'est pas disponible. Utilisation du mode hors ligne.",
    "ai_quota_exceeded": "⚡ Quota IA dépassé. Réessayez plus tard.",
    "ai_auth_error": "🔑 Erreur d'authentification IA. Vérifiez votre clé API.",
    "network_error": "🌐 Erreur de connexion. Vérifiez votre connexion internet.",
    "timeout": "⏱️ Délai d'attente dépassé. L'opération a pris trop de temps.",
    
    # Validation errors
    "invalid_date": "📅 Date invalide. Format attendu: JJ/MM/AAAA ou AAAA-MM-JJ.",
    "invalid_amount": "💰 Montant invalide. Vérifiez le format numérique.",
    "required_field": "⚠️ Champ obligatoire manquant. Veuillez remplir tous les champs requis.",
    "invalid_email": "📧 Adresse email invalide.",
    
    # Generic errors
    "unknown": "❌ Une erreur inattendue s'est produite. Veuillez réessayer.",
    "not_implemented": "🔧 Cette fonctionnalité n'est pas encore implémentée.",
}


def get_error_message(error: Exception, context: str = "") -> str:
    """
    Get a user-friendly error message for an exception.
    
    Args:
        error: The exception that occurred
        context: Optional context about where the error occurred
        
    Returns:
        User-friendly error message
    """
    error_str = str(error).lower()
    error_type = type(error).__name__
    
    # Database errors
    if "database is locked" in error_str or "sqlite3.operationalerror" in error_type.lower():
        return ERROR_MESSAGES["database_locked"]
    elif "busy" in error_str and "database" in error_str:
        return ERROR_MESSAGES["database_busy"]
    elif "unique constraint failed" in error_str:
        return ERROR_MESSAGES["unique_constraint"]
    elif "foreign key constraint failed" in error_str:
        return ERROR_MESSAGES["foreign_key"]
    
    # File errors
    elif "no such file" in error_str or "filenotfound" in error_type.lower():
        return ERROR_MESSAGES["file_not_found"]
    elif "permission denied" in error_str:
        return ERROR_MESSAGES["permission_denied"]
    elif "file is too large" in error_str or "overflow" in error_str:
        return ERROR_MESSAGES["file_too_large"]
    
    # Network/AI errors
    elif "connection" in error_str or "connect" in error_str:
        return ERROR_MESSAGES["network_error"]
    elif "timeout" in error_str:
        return ERROR_MESSAGES["timeout"]
    elif "quota" in error_str or "rate limit" in error_str:
        return ERROR_MESSAGES["ai_quota_exceeded"]
    elif "authentication" in error_str or "api key" in error_str or "401" in error_str:
        return ERROR_MESSAGES["ai_auth_error"]
    
    # Validation errors
    elif "date" in error_str and ("invalid" in error_str or "parse" in error_str):
        return ERROR_MESSAGES["invalid_date"]
    elif "amount" in error_str and ("invalid" in error_str or "convert" in error_str):
        return ERROR_MESSAGES["invalid_amount"]
    elif "required" in error_str:
        return ERROR_MESSAGES["required_field"]
    
    # If no specific message, return generic with details
    if context:
        return f"❌ Erreur lors de {context}: {str(error)[:100]}"
    return f"❌ {str(error)[:150]}"


def handle_error(
    error: Exception,
    context: str = "",
    show_user: bool = True,
    log_error: bool = True
) -> str:
    """
    Handle an error by logging it and optionally showing a user-friendly message.
    
    Args:
        error: The exception to handle
        context: Context about where the error occurred
        show_user: Whether to show the error to the user
        log_error: Whether to log the error
        
    Returns:
        The user-friendly error message
    """
    message = get_error_message(error, context)
    
    if log_error:
        logger.error(f"Error in {context}: {error}", exc_info=True)
    
    if show_user:
        st.error(message)
    
    return message


def safe_operation(
    operation: Callable,
    *args,
    context: str = "",
    default_return: Any = None,
    show_error: bool = True,
    **kwargs
) -> Any:
    """
    Safely execute an operation with error handling.
    
    Args:
        operation: Function to execute
        *args: Positional arguments
        context: Context for error messages
        default_return: Value to return on error
        show_error: Whether to show error to user
        **kwargs: Keyword arguments
        
    Returns:
        Operation result or default_return on error
    """
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        handle_error(e, context, show_user=show_error)
        return default_return


def with_error_handling(
    context: str = "",
    default_return: Any = None,
    show_error: bool = True
):
    """
    Decorator to add error handling to a function.
    
    Args:
        context: Context for error messages
        default_return: Value to return on error
        show_error: Whether to show error to user
        
    Example:
        @with_error_handling("création de catégorie", default_return=False)
        def create_category(name):
            # ... operation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handle_error(e, context or func.__name__, show_user=show_error)
                return default_return
        return wrapper
    return decorator


def validate_required(value: Any, field_name: str) -> bool:
    """
    Validate that a required field has a value.
    
    Args:
        value: The value to check
        field_name: Name of the field for error message
        
    Returns:
        True if valid, False otherwise
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        st.error(f"⚠️ Le champ '{field_name}' est obligatoire")
        return False
    return True


def validate_date_format(date_str: str, formats: list = None) -> bool:
    """
    Validate a date string format.
    
    Args:
        date_str: Date string to validate
        formats: List of allowed formats
        
    Returns:
        True if valid, False otherwise
    """
    from datetime import datetime
    
    if formats is None:
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"]
    
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    
    st.error(ERROR_MESSAGES["invalid_date"])
    return False


def validate_numeric(value: str, field_name: str = "valeur") -> bool:
    """
    Validate that a string can be converted to a number.
    
    Args:
        value: String to validate
        field_name: Name of the field for error message
        
    Returns:
        True if valid, False otherwise
    """
    try:
        float(value.replace(',', '.').replace(' ', ''))
        return True
    except ValueError:
        st.error(f"💰 {field_name} doit être un nombre valide")
        return False


class ErrorContext:
    """
    Context manager for error handling.
    
    Example:
        with ErrorContext("import de fichier"):
            df = load_transaction_file(file)
    """
    
    def __init__(self, context: str, show_error: bool = True, reraise: bool = False):
        self.context = context
        self.show_error = show_error
        self.reraise = reraise
        self.error_occurred = False
        self.error_message = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.error_occurred = True
            self.error_message = handle_error(exc_val, self.context, show_user=self.show_error)
            
            if self.reraise:
                return False  # Re-raise the exception
            return True  # Suppress the exception
        return False


# Export all utilities
__all__ = [
    'ERROR_MESSAGES',
    'get_error_message',
    'handle_error',
    'safe_operation',
    'with_error_handling',
    'validate_required',
    'validate_date_format',
    'validate_numeric',
    'ErrorContext',
]
