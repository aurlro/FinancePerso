"""
Rules management UI components.

This package provides specialized UI components for managing learning rules,
budgets, and rule auditing in the FinancePerso application.

Components:
    - rule_manager: CRUD operations for learning rules with search/filter
    - rule_validator: Regex pattern validation utilities
    - rule_audit: AI-powered rules integrity analysis
    - budget_manager: Monthly budget management by category
"""

from .rule_manager import render_rule_list, render_add_rule_form
from .rule_validator import test_pattern_against_transactions
from .rule_audit import render_audit_section
from .budget_manager import render_budget_section

__all__ = [
    'render_rule_list',
    'render_add_rule_form',
    'test_pattern_against_transactions',
    'render_audit_section',
    'render_budget_section',
]
