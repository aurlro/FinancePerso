"""
Wrapper de migration DB - Compatibilité temporaire
====================================================

Ce module fournit une couche de compatibilité entre l'ancien modules/db/
et le nouveau modules/db_v2/ pendant la transition.

Usage:
    from modules.db_migration_wrapper import get_db_connection
    # Fonctionne avec ancien et nouveau code
"""

import warnings

# Essayer d'importer depuis db_v2 (nouveau), sinon db (ancien)
try:
    from modules.db_v2 import (
        TransactionRepository,
        CategoryRepository,
        MemberRepository,
        BudgetRepository,
    )
    from modules.db_v2.base import get_db_connection
    
    USING_NEW_DB = True
    
except ImportError:
    from modules.db.connection import get_db_connection
    from modules.db.transactions import (
        get_all_transactions,
        get_transaction_by_id,
        add_transaction,
        update_transaction,
        delete_transaction,
    )
    from modules.db.categories import (
        get_categories,
        add_category,
        update_category,
        delete_category,
    )
    from modules.db.members import (
        get_members,
        add_member,
        update_member,
        delete_member,
    )
    from modules.db.budgets import (
        get_budgets,
        set_budget,
        delete_budget,
    )
    
    USING_NEW_DB = False


# Wrapper pour transactions
def get_all_transactions_wrapper(*args, **kwargs):
    """Wrapper compatible pour get_all_transactions"""
    if USING_NEW_DB:
        # Utiliser le nouveau Repository
        repo = TransactionRepository()
        return repo.get_all(*args, **kwargs)
    else:
        # Utiliser l'ancienne fonction
        return get_all_transactions(*args, **kwargs)


def get_transaction_by_id_wrapper(transaction_id, *args, **kwargs):
    """Wrapper compatible pour get_transaction_by_id"""
    if USING_NEW_DB:
        repo = TransactionRepository()
        return repo.get_by_id(transaction_id, *args, **kwargs)
    else:
        return get_transaction_by_id(transaction_id, *args, **kwargs)


def add_transaction_wrapper(transaction, *args, **kwargs):
    """Wrapper compatible pour add_transaction"""
    if USING_NEW_DB:
        repo = TransactionRepository()
        return repo.add(transaction, *args, **kwargs)
    else:
        return add_transaction(transaction, *args, **kwargs)


# Wrapper pour catégories
def get_categories_wrapper(*args, **kwargs):
    """Wrapper compatible pour get_categories"""
    if USING_NEW_DB:
        repo = CategoryRepository()
        return repo.get_all(*args, **kwargs)
    else:
        return get_categories(*args, **kwargs)


def add_category_wrapper(category, *args, **kwargs):
    """Wrapper compatible pour add_category"""
    if USING_NEW_DB:
        repo = CategoryRepository()
        return repo.add(category, *args, **kwargs)
    else:
        return add_category(category, *args, **kwargs)


# Wrapper pour membres
def get_members_wrapper(*args, **kwargs):
    """Wrapper compatible pour get_members"""
    if USING_NEW_DB:
        repo = MemberRepository()
        return repo.get_all(*args, **kwargs)
    else:
        return get_members(*args, **kwargs)


def add_member_wrapper(member, *args, **kwargs):
    """Wrapper compatible pour add_member"""
    if USING_NEW_DB:
        repo = MemberRepository()
        return repo.add(member, *args, **kwargs)
    else:
        return add_member(member, *args, **kwargs)


# Wrapper pour budgets
def get_budgets_wrapper(*args, **kwargs):
    """Wrapper compatible pour get_budgets"""
    if USING_NEW_DB:
        repo = BudgetRepository()
        return repo.get_all(*args, **kwargs)
    else:
        return get_budgets(*args, **kwargs)


def set_budget_wrapper(category, amount, *args, **kwargs):
    """Wrapper compatible pour set_budget"""
    if USING_NEW_DB:
        repo = BudgetRepository()
        return repo.set_budget(category, amount, *args, **kwargs)
    else:
        return set_budget(category, amount, *args, **kwargs)


# Exports pour compatibilité
__all__ = [
    'get_db_connection',
    'get_all_transactions_wrapper',
    'get_transaction_by_id_wrapper',
    'add_transaction_wrapper',
    'get_categories_wrapper',
    'add_category_wrapper',
    'get_members_wrapper',
    'add_member_wrapper',
    'get_budgets_wrapper',
    'set_budget_wrapper',
    'USING_NEW_DB',
]


# Avertissement si on utilise encore l'ancien système
if not USING_NEW_DB:
    warnings.warn(
        "Using legacy modules/db/. Please migrate to modules/db_v2/",
        DeprecationWarning,
        stacklevel=2
    )
