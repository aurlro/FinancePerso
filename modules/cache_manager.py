"""
Cache management utilities for selective invalidation.
Provides targeted cache clearing instead of global st.cache_data.clear().
"""
import streamlit as st
from functools import wraps


def invalidate_transaction_caches():
    """
    Invalidate only transaction-related caches.
    Call this after any transaction modification.
    """
    # Clear specific cached functions
    from modules.db.transactions import (
        get_all_transactions,
        get_all_hashes,
        get_transactions_count
    )

    try:
        get_all_transactions.clear()
    except AttributeError:
        pass

    try:
        get_all_hashes.clear()
    except AttributeError:
        pass

    try:
        get_transactions_count.clear()
    except AttributeError:
        pass

    # Note: get_pending_transactions is NOT cached (real-time data)
    # so no need to clear it


def invalidate_rule_caches():
    """
    Invalidate rule-related caches.
    Call this after adding/deleting learning rules.
    """
    from modules.db.rules import get_learning_rules, get_compiled_learning_rules

    try:
        get_learning_rules.clear()
    except AttributeError:
        pass

    try:
        get_compiled_learning_rules.clear()
    except AttributeError:
        pass


def invalidate_category_caches():
    """
    Invalidate category-related caches.
    Call this after category modifications.
    """
    from modules.db.categories import get_categories, get_categories_with_emojis

    try:
        get_categories.clear()
    except AttributeError:
        pass
    
    try:
        get_categories_with_emojis.clear()
    except AttributeError:
        pass


def invalidate_member_caches():
    """
    Invalidate member-related caches.
    Call this after member modifications.
    """
    from modules.db.members import get_members

    try:
        get_members.clear()
    except AttributeError:
        pass


def invalidate_tag_caches():
    """
    Invalidate tag-related caches.
    Call this after tag modifications.

    Note: Tags are stored in the transactions table, so we must also
    invalidate transaction caches to reflect tag changes.
    """
    from modules.db.transactions import get_all_transactions

    # Tags are computed from transactions, so invalidate transaction cache
    try:
        get_all_transactions.clear()
    except AttributeError:
        pass


def invalidate_audit_caches():
    """
    Invalidate audit-related caches.
    Call this after audit log modifications.
    """
    # Audit operations typically don't have heavy caching
    # but this provides consistency in the API
    pass


def invalidate_all_caches():
    """
    Nuclear option: clear all Streamlit caches.
    Use only when necessary (profile changes, etc.).
    """
    st.cache_data.clear()


def cache_with_key(key_prefix: str):
    """
    Decorator for caching with a specific key prefix.
    Allows targeted invalidation by key.

    Usage:
        @cache_with_key("transactions")
        def get_user_transactions(user_id):
            ...
    """
    def decorator(func):
        @wraps(func)
        @st.cache_data
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper._cache_key_prefix = key_prefix
        return wrapper
    return decorator


# Convenience function for backward compatibility
def clear_transaction_cache():
    """Legacy function name - delegates to invalidate_transaction_caches()"""
    invalidate_transaction_caches()
