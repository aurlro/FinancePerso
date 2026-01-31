"""
Tests for input validation module.
"""

import pytest
from datetime import date, timedelta
from pydantic import ValidationError

from modules.validators import (
    TransactionInput,
    CategoryInput,
    LearningRuleInput,
    BudgetInput,
    MemberInput,
    TagInput,
    validate_transaction,
    sanitize_string_input,
    validate_sql_identifier,
    ValidationUtils,
)


class TestTransactionInput:
    """Test transaction input validation."""
    
    def test_valid_transaction(self):
        """Test valid transaction data."""
        tx = TransactionInput(
            label="CARREFOUR MARKET",
            amount=-45.50,
            date=date.today()
        )
        assert tx.label == "CARREFOUR MARKET"
        assert tx.amount == -45.50
    
    def test_label_sanitization(self):
        """Test that labels are sanitized."""
        tx = TransactionInput(
            label="  <script>alert('xss')</script>CARREFOUR  ",
            amount=-45.50,
            date=date.today()
        )
        assert "<script>" not in tx.label
        assert "&lt;script&gt;" in tx.label
    
    def test_amount_precision(self):
        """Test amount is rounded to 2 decimals."""
        tx = TransactionInput(
            label="TEST",
            amount=-45.55555,
            date=date.today()
        )
        assert tx.amount == -45.56
    
    def test_amount_too_large(self):
        """Test amount cannot be too large."""
        with pytest.raises(ValidationError):
            TransactionInput(
                label="TEST",
                amount=1e10,
                date=date.today()
            )
    
    def test_date_too_old(self):
        """Test date cannot be before 2000."""
        with pytest.raises(ValidationError):
            TransactionInput(
                label="TEST",
                amount=-50.0,
                date=date(1999, 12, 31)
            )
    
    def test_date_too_far_future(self):
        """Test date cannot be more than 1 year in future."""
        with pytest.raises(ValidationError):
            TransactionInput(
                label="TEST",
                amount=-50.0,
                date=date.today() + timedelta(days=400)
            )
    
    def test_empty_label(self):
        """Test empty label is rejected."""
        with pytest.raises(ValidationError):
            TransactionInput(
                label="",
                amount=-50.0,
                date=date.today()
            )
    
    def test_label_too_long(self):
        """Test label max length."""
        with pytest.raises(ValidationError):
            TransactionInput(
                label="A" * 501,
                amount=-50.0,
                date=date.today()
            )


class TestCategoryInput:
    """Test category input validation."""
    
    def test_valid_category(self):
        """Test valid category."""
        cat = CategoryInput(name="Alimentation", emoji="🍽️")
        assert cat.name == "Alimentation"
        assert cat.emoji == "🍽️"
    
    def test_reserved_category_name(self):
        """Test reserved names are rejected."""
        with pytest.raises(ValidationError):
            CategoryInput(name="Inconnu")
        
        with pytest.raises(ValidationError):
            CategoryInput(name="unknown")
    
    def test_invalid_characters(self):
        """Test invalid characters in category name."""
        with pytest.raises(ValidationError):
            CategoryInput(name="Test<script>")


class TestLearningRuleInput:
    """Test learning rule input validation."""
    
    def test_valid_pattern(self):
        """Test valid regex pattern."""
        rule = LearningRuleInput(pattern="CARREFOUR", category="Alimentation")
        assert rule.pattern == "CARREFOUR"
        assert rule.category == "Alimentation"
    
    def test_invalid_regex(self):
        """Test invalid regex is rejected."""
        with pytest.raises(ValidationError):
            LearningRuleInput(pattern="[invalid(", category="Test")
    
    def test_dangerous_regex(self):
        """Test dangerous regex patterns are rejected."""
        with pytest.raises(ValidationError):
            LearningRuleInput(pattern="(a+)+$", category="Test")


class TestBudgetInput:
    """Test budget input validation."""
    
    def test_valid_budget(self):
        """Test valid budget."""
        budget = BudgetInput(category="Alimentation", amount=500.0)
        assert budget.category == "Alimentation"
        assert budget.amount == 500.0
    
    def test_negative_budget(self):
        """Test negative budget is rejected."""
        with pytest.raises(ValidationError):
            BudgetInput(category="Test", amount=-100)
    
    def test_unrealistic_budget(self):
        """Test unrealistic budget is rejected."""
        with pytest.raises(ValidationError):
            BudgetInput(category="Test", amount=2_000_000)


class TestMemberInput:
    """Test member input validation."""
    
    def test_valid_member(self):
        """Test valid member."""
        member = MemberInput(name="Aurélien", member_type="HOUSEHOLD")
        assert member.name == "Aurélien"
        assert member.member_type == "HOUSEHOLD"
    
    def test_html_in_name(self):
        """Test HTML is escaped in member name."""
        member = MemberInput(name="<b>Test</b>", member_type="HOUSEHOLD")
        assert "<b>" not in member.name


class TestTagInput:
    """Test tag input validation."""
    
    def test_valid_tag(self):
        """Test valid tag."""
        tag = TagInput(name="Urgent")
        assert tag.name == "urgent"  # Lowercase
    
    def test_tag_normalization(self):
        """Test tag normalization."""
        tag = TagInput(name="  URGENT-TAG!  ")
        assert tag.name == "urgent-tag"


class TestHelperFunctions:
    """Test helper validation functions."""
    
    def test_validate_transaction_success(self):
        """Test successful transaction validation."""
        is_valid, error = validate_transaction(
            label="TEST",
            amount=-50.0,
            tx_date=date.today()
        )
        assert is_valid
        assert error is None
    
    def test_validate_transaction_failure(self):
        """Test failed transaction validation."""
        is_valid, error = validate_transaction(
            label="",
            amount=-50.0,
            tx_date=date.today()
        )
        assert not is_valid
        assert error is not None
    
    def test_sanitize_string_input(self):
        """Test string sanitization."""
        result = sanitize_string_input("  <b>Test</b>  ")
        assert result == "&lt;b&gt;Test&lt;/b&gt;"
    
    def test_sanitize_string_allow_html(self):
        """Test string sanitization with HTML allowed."""
        result = sanitize_string_input("<b>Test</b>", allow_html=True)
        assert result == "<b>Test</b>"
    
    def test_validate_sql_identifier_valid(self):
        """Test valid SQL identifier."""
        is_valid, error = validate_sql_identifier("valid_column")
        assert is_valid
        assert error is None
    
    def test_validate_sql_identifier_keyword(self):
        """Test SQL keyword rejection."""
        is_valid, error = validate_sql_identifier("SELECT")
        assert not is_valid
        assert "reserved" in error.lower()
    
    def test_validate_sql_identifier_invalid_chars(self):
        """Test invalid characters rejection."""
        is_valid, error = validate_sql_identifier("column-name!")
        assert not is_valid


class TestValidationUtils:
    """Test validation utilities."""
    
    def test_validate_file_extension(self):
        """Test file extension validation."""
        assert ValidationUtils.validate_file_extension("test.csv", [".csv", ".txt"])
        assert not ValidationUtils.validate_file_extension("test.pdf", [".csv"])
    
    def test_validate_file_size(self):
        """Test file size validation."""
        is_valid, error = ValidationUtils.validate_file_size(5 * 1024 * 1024, max_size_mb=10)
        assert is_valid
        
        is_valid, error = ValidationUtils.validate_file_size(15 * 1024 * 1024, max_size_mb=10)
        assert not is_valid
        assert "too large" in error.lower()
    
    def test_sanitize_search_query(self):
        """Test search query sanitization."""
        result = ValidationUtils.sanitize_search_query("test[abc]+")
        assert "[" not in result
        assert "+" not in result
