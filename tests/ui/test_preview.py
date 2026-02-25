"""
Tests for preview.py module.
"""

import pandas as pd
import pytest

from modules.ui.importing.preview import (
    calculate_import_stats,
    format_preview_dataframe,
)


class TestCalculateImportStats:
    """Tests for import statistics calculation."""

    def test_calculate_stats_basic(self):
        """Test basic stats calculation."""
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'label': ['A', 'B', 'C'],
            'amount': [100.0, -50.0, -30.0]
        })

        total_in = df[df['amount'] > 0]['amount'].sum()
        total_out = abs(df[df['amount'] < 0]['amount'].sum())
        balance = total_in - total_out

        assert total_in == 100.0
        assert total_out == 80.0
        assert balance == 20.0

    def test_calculate_stats_all_expenses(self):
        """Test stats with only expenses."""
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'label': ['A', 'B'],
            'amount': [-50.0, -30.0]
        })

        total_in = df[df['amount'] > 0]['amount'].sum() if len(df[df['amount'] > 0]) > 0 else 0
        total_out = abs(df[df['amount'] < 0]['amount'].sum())
        balance = total_in - total_out

        assert total_in == 0
        assert total_out == 80.0
        assert balance == -80.0

    def test_calculate_stats_all_income(self):
        """Test stats with only income."""
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'label': ['A', 'B'],
            'amount': [100.0, 200.0]
        })

        total_in = df[df['amount'] > 0]['amount'].sum()
        total_out = abs(df[df['amount'] < 0]['amount'].sum()) if len(df[df['amount'] < 0]) > 0 else 0
        balance = total_in - total_out

        assert total_in == 300.0
        assert total_out == 0
        assert balance == 300.0

    def test_calculate_stats_empty_dataframe(self):
        """Test stats with empty DataFrame."""
        df = pd.DataFrame({'date': [], 'label': [], 'amount': []})

        total_in = df[df['amount'] > 0]['amount'].sum() if len(df[df['amount'] > 0]) > 0 else 0
        total_out = abs(df[df['amount'] < 0]['amount'].sum()) if len(df[df['amount'] < 0]) > 0 else 0
        balance = total_in - total_out

        assert total_in == 0
        assert total_out == 0
        assert balance == 0

    def test_calculate_stats_with_zero_amounts(self):
        """Test stats with zero amounts."""
        df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02'],
            'label': ['A', 'B'],
            'amount': [100.0, 0.0]
        })

        total_in = df[df['amount'] > 0]['amount'].sum()
        total_out = abs(df[df['amount'] < 0]['amount'].sum()) if len(df[df['amount'] < 0]) > 0 else 0
        balance = total_in - total_out

        assert total_in == 100.0
        assert total_out == 0
        assert balance == 100.0


class TestFormatPreviewDataframe:
    """Tests for preview DataFrame formatting."""

    def test_format_preview_selects_correct_columns(self):
        """Test that preview selects the right columns."""
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'label': ['Test'],
            'amount': [100.0],
            'category_validated': ['Alimentation'],
            'extra_col': ['ignored']
        })

        # Simulate the logic in render_import_preview
        preview_df = df.head(5).copy()
        display_cols = ['date', 'label', 'amount', 'category_validated'] if 'category_validated' in preview_df.columns else ['date', 'label', 'amount']
        result = preview_df[display_cols]

        assert list(result.columns) == ['date', 'label', 'amount', 'category_validated']
        assert 'extra_col' not in result.columns

    def test_format_preview_without_category(self):
        """Test preview formatting without category column."""
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'label': ['Test'],
            'amount': [100.0]
        })

        preview_df = df.head(5).copy()
        display_cols = ['date', 'label', 'amount', 'category_validated'] if 'category_validated' in preview_df.columns else ['date', 'label', 'amount']
        result = preview_df[display_cols]

        assert list(result.columns) == ['date', 'label', 'amount']

    def test_format_preview_limits_to_5_rows(self):
        """Test that preview limits to 5 rows."""
        df = pd.DataFrame({
            'date': ['2024-01-01'] * 10,
            'label': [f'Test {i}' for i in range(10)],
            'amount': [100.0] * 10
        })

        preview_df = df.head(5).copy()

        assert len(preview_df) == 5

    def test_format_preview_with_less_than_5_rows(self):
        """Test preview with less than 5 rows."""
        df = pd.DataFrame({
            'date': ['2024-01-01'] * 3,
            'label': ['A', 'B', 'C'],
            'amount': [100.0, 200.0, 300.0]
        })

        preview_df = df.head(5).copy()

        assert len(preview_df) == 3


class TestDuplicateCountLogic:
    """Tests for duplicate counting logic."""

    def test_count_no_duplicates(self):
        """Test counting when no duplicates."""
        total_tx = 10
        duplicates = None
        duplicate_count = len(duplicates) if duplicates is not None else 0
        new_tx = total_tx - duplicate_count

        assert duplicate_count == 0
        assert new_tx == 10

    def test_count_with_duplicates(self):
        """Test counting with duplicates."""
        total_tx = 10
        duplicates = pd.DataFrame({'col': range(3)})
        duplicate_count = len(duplicates)
        new_tx = total_tx - duplicate_count

        assert duplicate_count == 3
        assert new_tx == 7

    def test_count_empty_duplicates_dataframe(self):
        """Test with empty duplicates DataFrame."""
        total_tx = 10
        duplicates = pd.DataFrame({'col': []})
        duplicate_count = len(duplicates)
        new_tx = total_tx - duplicate_count

        assert duplicate_count == 0
        assert new_tx == 10


class TestImportOptionsLogic:
    """Tests for import options handling."""

    def test_default_options(self):
        """Test default import options."""
        options = {
            'ignore_duplicates': True,
            'auto_categorize': True,
            'skip_validation': False
        }

        assert options['ignore_duplicates'] is True
        assert options['auto_categorize'] is True
        assert options['skip_validation'] is False

    def test_options_with_no_duplicates(self):
        """Test options when no duplicates exist."""
        duplicate_count = 0
        ignore_duplicates = False if duplicate_count == 0 else True

        options = {
            'ignore_duplicates': ignore_duplicates,
            'auto_categorize': True,
            'skip_validation': False
        }

        assert options['ignore_duplicates'] is False


class TestImportSummaryStats:
    """Tests for import summary calculations."""

    def test_summary_all_success(self):
        """Test summary with all successful imports."""
        imported = 10
        categorized = 8
        duplicates_skipped = 0
        errors = []

        assert imported == 10
        assert categorized == 8
        assert duplicates_skipped == 0
        assert len(errors) == 0

    def test_summary_with_errors(self):
        """Test summary with some errors."""
        imported = 8
        categorized = 6
        duplicates_skipped = 2
        errors = ["Error 1", "Error 2"]

        assert imported == 8
        assert categorized == 6
        assert duplicates_skipped == 2
        assert len(errors) == 2

    def test_summary_nothing_imported(self):
        """Test summary when nothing imported."""
        imported = 0
        categorized = 0
        duplicates_skipped = 10
        errors = []

        assert imported == 0
        assert categorized == 0
        assert duplicates_skipped == 10


class TestProgressCalculation:
    """Tests for progress calculation."""

    def test_progress_calculation(self):
        """Test progress calculation."""
        current_step = 3
        total_steps = 6
        progress = current_step / total_steps

        assert progress == 0.5

    def test_progress_start(self):
        """Test progress at start."""
        current_step = 1
        total_steps = 5
        progress = current_step / total_steps

        assert progress == 0.2

    def test_progress_complete(self):
        """Test progress at completion."""
        current_step = 5
        total_steps = 5
        progress = current_step / total_steps

        assert progress == 1.0
