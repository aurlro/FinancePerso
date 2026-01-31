"""
Error tracking and monitoring module.
Integrates with Sentry for production error tracking.
Provides local fallback for development.
"""

import os
import sys
import traceback
from typing import Optional, Dict, Any, Callable
from functools import wraps
from modules.logger import logger


class ErrorTracker:
    """Error tracking with Sentry integration."""
    
    _instance = None
    _sentry_initialized = False
    _local_errors = []  # Fallback for development
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def init_sentry(self, dsn: Optional[str] = None, environment: str = "development"):
        """Initialize Sentry if DSN is available."""
        if self._sentry_initialized:
            return
        
        dsn = dsn or os.getenv("SENTRY_DSN")
        
        if not dsn:
            logger.info("Sentry DSN not configured, using local error tracking")
            return
        
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            sentry_logging = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
            
            sentry_sdk.init(
                dsn=dsn,
                environment=environment,
                integrations=[sentry_logging],
                traces_sample_rate=0.1,  # 10% performance monitoring
                profiles_sample_rate=0.1,
                before_send=self._before_send,
            )
            
            self._sentry_initialized = True
            logger.info(f"Sentry initialized for environment: {environment}")
            
        except ImportError:
            logger.warning("Sentry SDK not installed, using local error tracking")
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")
    
    def _before_send(self, event, hint):
        """Filter events before sending to Sentry."""
        # Filter out specific exceptions
        if 'exc_info' in hint:
            exc_type, exc_value, tb = hint['exc_info']
            
            # Ignore KeyboardInterrupt
            if exc_type is KeyboardInterrupt:
                return None
            
            # Ignore certain validation errors
            if exc_type.__name__ == 'ValidationError':
                # Still log but don't send to Sentry
                return None
        
        return event
    
    def capture_exception(self, exception: Exception, context: Optional[Dict] = None):
        """Capture an exception for tracking."""
        error_info = {
            'type': type(exception).__name__,
            'message': str(exception),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        if self._sentry_initialized:
            try:
                import sentry_sdk
                with sentry_sdk.push_scope() as scope:
                    if context:
                        for key, value in context.items():
                            scope.set_extra(key, value)
                    sentry_sdk.capture_exception(exception)
            except Exception as e:
                logger.error(f"Failed to send to Sentry: {e}")
        
        # Always store locally for development/debugging
        self._local_errors.append(error_info)
        
        # Limit local storage
        if len(self._local_errors) > 100:
            self._local_errors.pop(0)
        
        logger.error(f"Exception captured: {exception}", exc_info=True)
    
    def capture_message(self, message: str, level: str = "info", context: Optional[Dict] = None):
        """Capture a message for tracking."""
        if self._sentry_initialized:
            try:
                import sentry_sdk
                with sentry_sdk.push_scope() as scope:
                    if context:
                        for key, value in context.items():
                            scope.set_extra(key, value)
                    sentry_sdk.capture_message(message, level=level)
            except Exception as e:
                logger.error(f"Failed to send message to Sentry: {e}")
        
        log_func = getattr(logger, level, logger.info)
        log_func(message)
    
    def set_user(self, user_id: Optional[str] = None, email: Optional[str] = None, 
                username: Optional[str] = None):
        """Set user context for error tracking."""
        if self._sentry_initialized and user_id:
            try:
                import sentry_sdk
                sentry_sdk.set_user({
                    'id': user_id,
                    'email': email,
                    'username': username
                })
            except Exception:
                pass
    
    def clear_user(self):
        """Clear user context."""
        if self._sentry_initialized:
            try:
                import sentry_sdk
                sentry_sdk.set_user(None)
            except Exception:
                pass
    
    def get_local_errors(self, limit: int = 50) -> list:
        """Get recent errors stored locally."""
        return self._local_errors[-limit:]
    
    def clear_local_errors(self):
        """Clear local error storage."""
        self._local_errors.clear()


# Global instance
_tracker = None

def get_tracker() -> ErrorTracker:
    """Get singleton error tracker."""
    global _tracker
    if _tracker is None:
        _tracker = ErrorTracker()
    return _tracker


def init_error_tracking(dsn: Optional[str] = None, environment: str = "development"):
    """Initialize error tracking."""
    get_tracker().init_sentry(dsn, environment)


def capture_exception(exception: Exception, context: Optional[Dict] = None):
    """Capture an exception."""
    get_tracker().capture_exception(exception, context)


def capture_message(message: str, level: str = "info", context: Optional[Dict] = None):
    """Capture a message."""
    get_tracker().capture_message(message, level, context)


def set_user_context(user_id: Optional[str] = None, email: Optional[str] = None, 
                    username: Optional[str] = None):
    """Set user context."""
    get_tracker().set_user(user_id, email, username)


# Decorators

def track_errors(context: Optional[Dict] = None, fallback_value: Any = None):
    """Decorator to track errors in functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_context = context or {}
                error_context['function'] = func.__name__
                error_context['args'] = str(args)
                error_context['kwargs'] = str(kwargs)
                
                capture_exception(e, error_context)
                
                if fallback_value is not None:
                    return fallback_value
                raise
        return wrapper
    return decorator


def with_retry(max_attempts: int = 3, exceptions: tuple = (Exception,), 
               on_retry: Optional[Callable] = None):
    """Decorator to retry function on failure."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}"
                        )
                        if on_retry:
                            on_retry(attempt + 1, e)
                    else:
                        capture_exception(e, {
                            'function': func.__name__,
                            'attempt': attempt + 1,
                            'max_attempts': max_attempts
                        })
            
            raise last_exception
        return wrapper
    return decorator


def with_fallback(default_value: Any, exceptions: tuple = (Exception,)):
    """Decorator to return default value on exception."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                capture_exception(e, {
                    'function': func.__name__,
                    'fallback_used': True
                })
                return default_value
        return wrapper
    return decorator


__all__ = [
    'ErrorTracker',
    'get_tracker',
    'init_error_tracking',
    'capture_exception',
    'capture_message',
    'set_user_context',
    'track_errors',
    'with_retry',
    'with_fallback',
]


# Import logging at module level for Sentry integration
import logging
logging.basicConfig(level=logging.INFO)
