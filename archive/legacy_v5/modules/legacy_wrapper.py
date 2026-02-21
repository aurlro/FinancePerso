"""
Legacy DB Module Wrappers
=========================

⚠️ DEPRECATED: These functions are kept for backward compatibility.
Use modules.db_v2.repositories instead.

Migration guide:
    OLD: from modules.db.transactions import get_transaction_by_id
    NEW: from modules.db_v2 import TransactionRepository
         repo = TransactionRepository()
         tx = repo.get_by_id(1)

    OLD: from modules.db.categories import add_category
    NEW: from modules.db_v2 import CategoryRepository
         repo = CategoryRepository()
         repo.create(Category(name="Food", emoji="🍔"))
"""

import warnings
from functools import wraps


def _deprecated(new_way: str):
    """Decorator to mark functions as deprecated."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__module__}.{func.__name__} is deprecated. Use {new_way}",
                DeprecationWarning,
                stacklevel=3,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


# =============================================================================
# Transaction Wrappers
# =============================================================================


@_deprecated("TransactionRepository from modules.db_v2")
def get_transaction_by_id(tx_id: int):
    """Legacy wrapper - use TransactionRepository.get_by_id()"""
    from modules.db_v2 import TransactionRepository

    repo = TransactionRepository()
    tx = repo.get_by_id(tx_id)
    return tx.to_dict() if tx else None


@_deprecated("TransactionRepository from modules.db_v2")
def get_all_transactions(limit: int = None, filters: dict = None):
    """Legacy wrapper - use TransactionRepository.get_all()"""
    from modules.db_v2 import TransactionRepository

    repo = TransactionRepository()
    return repo.get_all(limit=limit, filters=filters)


@_deprecated("TransactionRepository from modules.db_v2")
def update_transaction_category(tx_id: int, category: str) -> bool:
    """Legacy wrapper - use TransactionRepository.update_category()"""
    from modules.db_v2 import TransactionRepository

    repo = TransactionRepository()
    return repo.update_category(tx_id, category)


# =============================================================================
# Category Wrappers
# =============================================================================


@_deprecated("CategoryRepository from modules.db_v2")
def add_category(name: str, emoji: str = "🏷️", is_fixed: int = 0) -> bool:
    """Legacy wrapper - use CategoryRepository.create()"""
    from modules.db_v2 import Category, CategoryRepository

    repo = CategoryRepository()
    try:
        cat = Category(name=name, emoji=emoji, is_fixed=bool(is_fixed))
        repo.create(cat)
        return True
    except Exception:
        return False


@_deprecated("CategoryRepository from modules.db_v2")
def get_categories() -> list[str]:
    """Legacy wrapper - use CategoryRepository.get_names()"""
    from modules.db_v2 import CategoryRepository

    repo = CategoryRepository()
    return repo.get_names()


@_deprecated("CategoryRepository from modules.db_v2")
def get_categories_with_emojis() -> dict[str, str]:
    """Legacy wrapper - use CategoryRepository.get_with_emojis()"""
    from modules.db_v2 import CategoryRepository

    repo = CategoryRepository()
    return repo.get_with_emojis()


@_deprecated("CategoryRepository from modules.db_v2")
def delete_category(cat_id: int) -> None:
    """Legacy wrapper - use CategoryRepository.delete()"""
    from modules.db_v2 import CategoryRepository

    repo = CategoryRepository()
    repo.delete(cat_id)


# =============================================================================
# Member Wrappers
# =============================================================================


@_deprecated("MemberRepository from modules.db_v2")
def add_member(name: str, member_type: str = "HOUSEHOLD") -> bool:
    """Legacy wrapper - use MemberRepository.create()"""
    from modules.db_v2 import Member, MemberRepository

    repo = MemberRepository()
    try:
        member = Member(name=name, member_type=member_type)
        repo.create(member)
        return True
    except Exception:
        return False


@_deprecated("MemberRepository from modules.db_v2")
def get_members():
    """Legacy wrapper - use MemberRepository.get_all()"""
    from modules.db_v2 import MemberRepository

    repo = MemberRepository()
    return repo.get_all()


@_deprecated("MemberRepository from modules.db_v2")
def rename_member(old_name: str, new_name: str) -> int:
    """Legacy wrapper - use MemberRepository.rename_member()"""
    from modules.db_v2 import MemberRepository

    repo = MemberRepository()
    return repo.rename_member(old_name, new_name)


@_deprecated("MemberRepository from modules.db_v2")
def delete_member(member_id: int) -> None:
    """Legacy wrapper - use MemberRepository.delete()"""
    from modules.db_v2 import MemberRepository

    repo = MemberRepository()
    repo.delete(member_id)


# =============================================================================
# Budget Wrappers
# =============================================================================


@_deprecated("BudgetRepository from modules.db_v2")
def set_budget(category: str, amount: float) -> None:
    """Legacy wrapper - use BudgetRepository.set_budget_amount()"""
    from modules.db_v2 import BudgetRepository

    repo = BudgetRepository()
    repo.set_budget_amount(category, amount)


@_deprecated("BudgetRepository from modules.db_v2")
def get_budgets():
    """Legacy wrapper - use BudgetRepository.get_all()"""
    from modules.db_v2 import BudgetRepository

    repo = BudgetRepository()
    return repo.get_all()


@_deprecated("BudgetRepository from modules.db_v2")
def delete_budget(category: str) -> bool:
    """Legacy wrapper - use BudgetRepository.delete_by_category()"""
    from modules.db_v2 import BudgetRepository

    repo = BudgetRepository()
    return repo.delete_by_category(category)
