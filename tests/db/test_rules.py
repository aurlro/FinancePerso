"""
Tests for rules.py module.
"""

import pytest
import pandas as pd
from modules.db.rules import (
    add_learning_rule,
    delete_learning_rule,
    get_learning_rules,
    get_rules_for_category,
    get_compiled_learning_rules,
)


class TestGetRules:
    """Tests for fetching rules."""

    def test_get_learning_rules(self, temp_db):
        """Test getting learning rules."""
        df = get_learning_rules()
        assert isinstance(df, pd.DataFrame)

    def test_get_rules_for_category(self, temp_db):
        """Test getting rules for specific category."""
        add_learning_rule("TEST_PATTERN", "Alimentation")
        df = get_rules_for_category("Alimentation")
        assert isinstance(df, pd.DataFrame)


class TestAddRule:
    """Tests for adding rules."""

    def test_add_learning_rule_basic(self, temp_db):
        """Test adding a basic learning rule."""
        result = add_learning_rule("CARREFOUR", "Alimentation")
        assert result is True

    def test_add_learning_rule_with_priority(self, temp_db):
        """Test adding rule with custom priority."""
        result = add_learning_rule("AMAZON", "Achats", priority=5)
        assert result is True


class TestCompiledRules:
    """Tests for compiled rules."""

    def test_get_compiled_learning_rules(self, temp_db):
        """Test getting compiled rules."""
        add_learning_rule("SNCF", "Transport")
        rules = get_compiled_learning_rules()
        assert isinstance(rules, list)
        # Each rule should be a tuple of (pattern, category, priority, original_pattern)
        for rule in rules:
            assert len(rule) == 4


class TestDeleteRule:
    """Tests for deleting rules."""

    def test_delete_learning_rule(self, temp_db):
        """Test deleting a rule."""
        add_learning_rule("TO_DELETE", "Category")
        df = get_learning_rules()
        if not df.empty:
            # Find the rule we just added
            rule_row = df[df["pattern"] == "TO_DELETE"]
            if not rule_row.empty:
                rule_id = int(rule_row.iloc[0]["id"])
                result = delete_learning_rule(rule_id)
                assert result is True

                # Verify it's gone
                df_after = get_learning_rules()
                assert "TO_DELETE" not in df_after["pattern"].values

    def test_delete_nonexistent_rule(self, temp_db):
        """Test deleting a non-existent rule."""
        result = delete_learning_rule(99999)
        assert result is False
