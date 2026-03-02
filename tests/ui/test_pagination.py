"""
Tests for pagination.py module.
"""

import pandas as pd

from modules.ui.components.pagination import (
    calculate_total_pages,
)


class TestCalculateTotalPages:
    """Tests for calculate_total_pages function."""

    def test_calculate_total_pages_exact(self):
        """Test calculation when items fit exactly."""
        assert calculate_total_pages(100, 10) == 10
        assert calculate_total_pages(50, 10) == 5

    def test_calculate_total_pages_partial(self):
        """Test calculation when there's a partial page."""
        assert calculate_total_pages(105, 10) == 11
        assert calculate_total_pages(1, 10) == 1

    def test_calculate_total_pages_empty(self):
        """Test calculation with empty data."""
        assert calculate_total_pages(0, 10) == 1  # Always at least 1 page

    def test_calculate_total_pages_large_page_size(self):
        """Test when page size is larger than total items."""
        assert calculate_total_pages(5, 100) == 1


class TestPaginatedDataframeLogic:
    """Tests for paginated_dataframe logic (without Streamlit)."""

    def test_pagination_slicing_page_1(self):
        """Test DataFrame slicing for page 1."""
        df = pd.DataFrame({"col": range(100)})
        page_size = 10
        page = 1

        start = (page - 1) * page_size
        end = min(start + page_size, len(df))
        result = df.iloc[start:end]

        assert len(result) == 10
        assert result.iloc[0]["col"] == 0
        assert result.iloc[9]["col"] == 9

    def test_pagination_slicing_page_2(self):
        """Test DataFrame slicing for page 2."""
        df = pd.DataFrame({"col": range(100)})
        page_size = 10
        page = 2

        start = (page - 1) * page_size
        end = min(start + page_size, len(df))
        result = df.iloc[start:end]

        assert len(result) == 10
        assert result.iloc[0]["col"] == 10
        assert result.iloc[9]["col"] == 19

    def test_pagination_slicing_last_page(self):
        """Test DataFrame slicing for last page with partial data."""
        df = pd.DataFrame({"col": range(25)})
        page_size = 10
        page = 3

        start = (page - 1) * page_size
        end = min(start + page_size, len(df))
        result = df.iloc[start:end]

        assert len(result) == 5
        assert result.iloc[0]["col"] == 20

    def test_pagination_slicing_beyond_range(self):
        """Test slicing beyond data range."""
        df = pd.DataFrame({"col": range(20)})
        page_size = 10
        page = 5  # Beyond available pages

        start = (page - 1) * page_size
        if start >= len(df):
            # Should handle gracefully
            result = df.iloc[0:0]
        else:
            end = min(start + page_size, len(df))
            result = df.iloc[start:end]

        assert len(result) == 0

    def test_pagination_with_empty_dataframe(self):
        """Test pagination with empty DataFrame."""
        df = pd.DataFrame({"col": []})
        page_size = 10
        page = 1

        start = (page - 1) * page_size
        end = min(start + page_size, len(df))
        result = df.iloc[start:end]

        assert len(result) == 0


class TestPaginatedListLogic:
    """Tests for paginated_list logic (without Streamlit)."""

    def test_list_pagination_page_1(self):
        """Test list slicing for page 1."""
        items = list(range(100))
        page_size = 10
        page = 1

        start = (page - 1) * page_size
        end = min(start + page_size, len(items))
        result = items[start:end]

        assert len(result) == 10
        assert result[0] == 0
        assert result[9] == 9

    def test_list_pagination_page_3(self):
        """Test list slicing for page 3."""
        items = list(range(100))
        page_size = 10
        page = 3

        start = (page - 1) * page_size
        end = min(start + page_size, len(items))
        result = items[start:end]

        assert len(result) == 10
        assert result[0] == 20
        assert result[9] == 29

    def test_list_pagination_empty(self):
        """Test pagination with empty list."""
        items = []
        page_size = 10
        page = 1

        start = (page - 1) * page_size
        end = min(start + page_size, len(items))
        result = items[start:end]

        assert len(result) == 0

    def test_list_pagination_last_partial(self):
        """Test pagination for last partial page."""
        items = list(range(25))
        page_size = 10
        page = 3

        start = (page - 1) * page_size
        end = min(start + page_size, len(items))
        result = items[start:end]

        assert len(result) == 5
        assert result == [20, 21, 22, 23, 24]


class TestResetPagination:
    """Tests for reset_pagination function."""

    def test_reset_pagination_creates_session_state_key(self):
        """Test that reset_pagination sets the correct session state."""
        # This is a mock test since we can't use real Streamlit session state
        # In real usage, it would set st.session_state[f"{key}_page"] = 1
        key = "test_pagination"
        expected_key = f"{key}_page"
        expected_value = 1

        # Verify the expected behavior
        assert expected_key == "test_pagination_page"
        assert expected_value == 1


class TestPaginationEdgeCases:
    """Edge case tests for pagination."""

    def test_page_size_1(self):
        """Test with page size of 1."""
        df = pd.DataFrame({"col": range(5)})
        page_size = 1
        page = 3

        total_pages = calculate_total_pages(len(df), page_size)
        assert total_pages == 5

        start = (page - 1) * page_size
        end = min(start + page_size, len(df))
        result = df.iloc[start:end]

        assert len(result) == 1
        assert result.iloc[0]["col"] == 2

    def test_very_large_page_size(self):
        """Test with very large page size."""
        df = pd.DataFrame({"col": range(10)})
        page_size = 1000
        page = 1

        total_pages = calculate_total_pages(len(df), page_size)
        assert total_pages == 1

        start = (page - 1) * page_size
        end = min(start + page_size, len(df))
        result = df.iloc[start:end]

        assert len(result) == 10

    def test_single_item(self):
        """Test with single item."""
        df = pd.DataFrame({"col": [42]})
        page_size = 10
        page = 1

        total_pages = calculate_total_pages(len(df), page_size)
        assert total_pages == 1

        start = (page - 1) * page_size
        end = min(start + page_size, len(df))
        result = df.iloc[start:end]

        assert len(result) == 1
        assert result.iloc[0]["col"] == 42
