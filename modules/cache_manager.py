"""Cache management utilities for selective invalidation.

Provides targeted cache clearing instead of global st.cache_data.clear().
Uses EventBus pattern to avoid circular dependencies with database modules.
"""

from functools import wraps

import streamlit as st

from modules.core.events import EventBus, on_event
from modules.logger import logger


# ============================================================================
# EVENT HANDLERS - Automatically clear caches when data changes
# ============================================================================

@on_event("transactions.changed")
def _on_transactions_changed(**kwargs):
    """Handle transaction changes by clearing related caches."""
    try:
        # Import inside handler to avoid circular dependency at module level
        from modules.db.transactions import get_all_transactions, get_all_hashes
        get_all_transactions.clear()
        get_all_hashes.clear()
        logger.debug("Transaction caches cleared via event")
    except Exception as e:
        logger.warning(f"Failed to clear transaction caches: {e}")


@on_event("transactions.batch_changed")
def _on_transactions_batch_changed(**kwargs):
    """Handle batch transaction changes."""
    try:
        from modules.db.transactions import (
            get_all_transactions,
            get_all_hashes,
            get_transactions_count,
        )

        get_all_transactions.clear()
        get_all_hashes.clear()
        get_transactions_count.clear()
        logger.debug("Transaction batch caches cleared via event")
    except Exception as e:
        logger.warning(f"Failed to clear batch transaction caches: {e}")


@on_event("rules.changed")
def _on_rules_changed(**kwargs):
    """Handle rule changes by clearing rule caches."""
    try:
        from modules.db.rules import get_compiled_learning_rules, get_learning_rules

        get_compiled_learning_rules.clear()
        get_learning_rules.clear()
        logger.debug("Rule caches cleared via event")
    except Exception as e:
        logger.warning(f"Failed to clear rule caches: {e}")


@on_event("categories.changed")
def _on_categories_changed(**kwargs):
    """Handle category changes by clearing category caches."""
    try:
        from modules.db.categories import get_categories, get_categories_with_emojis

        get_categories.clear()
        get_categories_with_emojis.clear()
        logger.debug("Category caches cleared via event")
    except Exception as e:
        logger.warning(f"Failed to clear category caches: {e}")


@on_event("members.changed")
def _on_members_changed(**kwargs):
    """Handle member changes by clearing member caches."""
    try:
        from modules.db.members import get_members

        get_members.clear()
        logger.debug("Member caches cleared via event")
    except Exception as e:
        logger.warning(f"Failed to clear member caches: {e}")


@on_event("tags.changed")
def _on_tags_changed(**kwargs):
    """Handle tag changes.

    Note: Tags are stored in the transactions table, so we must also
    invalidate transaction caches to reflect tag changes.
    """
    try:
        from modules.db.transactions import get_all_transactions

        get_all_transactions.clear()
        logger.debug("Tag caches cleared via event")
    except Exception as e:
        logger.warning(f"Failed to clear tag caches: {e}")


@on_event("audit.changed")
def _on_audit_changed(**kwargs):
    """Handle audit log changes.

    Note: Audit operations typically don't have heavy caching
    but this provides consistency in the API.
    """
    # Audit operations don't have specific caches to clear
    logger.debug("Audit change event received (no caches to clear)")


# ============================================================================
# PUBLIC API - Cache invalidation functions
# ============================================================================

def invalidate_transaction_caches():
    """Invalidate only transaction-related caches.

    Call this after any transaction modification.
    Emits 'transactions.changed' event.
    """
    EventBus.emit("transactions.changed")


def invalidate_rule_caches():
    """Invalidate rule-related caches.

    Call this after adding/deleting learning rules.
    Emits 'rules.changed' event and clears Streamlit caches.
    """
    EventBus.emit("rules.changed")
    
    # Clear Streamlit caches for rules
    try:
        from modules.db.rules import get_learning_rules, get_compiled_learning_rules, get_rules_for_category
        get_learning_rules.clear()
        get_compiled_learning_rules.clear()
        get_rules_for_category.clear()
    except Exception:
        pass  # Ignore if cache clearing fails


def invalidate_category_caches():
    """Invalidate category-related caches.

    Call this after category modifications.
    Emits 'categories.changed' event.
    """
    EventBus.emit("categories.changed")


def invalidate_member_caches():
    """Invalidate member-related caches.

    Call this after member modifications.
    Emits 'members.changed' event.
    """
    EventBus.emit("members.changed")


def invalidate_tag_caches():
    """Invalidate tag-related caches.

    Call this after tag modifications.
    Emits 'tags.changed' event.
    """
    EventBus.emit("tags.changed")


def invalidate_audit_caches():
    """Invalidate audit-related caches.

    Call this after audit log modifications.
    Emits 'audit.changed' event.
    """
    EventBus.emit("audit.changed")


def invalidate_all_caches():
    """Nuclear option: clear all Streamlit caches.

    Use only when necessary (profile changes, etc.).
    """
    st.cache_data.clear()
    logger.info("All caches cleared")


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

def clear_transaction_cache():
    """Legacy function name - delegates to invalidate_transaction_caches()."""
    invalidate_transaction_caches()


# ============================================================================
# UTILITY DECORATORS
# ============================================================================

def cache_with_key(key_prefix: str):
    """Decorator for caching with a specific key prefix.

    Allows targeted invalidation by key.

    Usage:
        @cache_with_key("transactions")
        def get_user_transactions(user_id):
            ...

    Args:
        key_prefix: Prefix for the cache key.

    Returns:
        Decorated function with cache key metadata.
    """

    def decorator(func):
        @wraps(func)
        @st.cache_data
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._cache_key_prefix = key_prefix
        return wrapper

    return decorator


def emit_after(event: str):
    """Decorator that emits an event after function execution.

    Usage:
        @emit_after("transactions.changed")
        def save_transaction(tx_data):
            # ... save logic ...
            pass

    Args:
        event: Event name to emit after function execution.

    Returns:
        Decorated function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            EventBus.emit(event)
            return result

        return wrapper

    return decorator
