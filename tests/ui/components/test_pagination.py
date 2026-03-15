"""
Tests for the Pagination molecule component.
"""

from unittest.mock import Mock

import pytest

from modules.ui.molecules.pagination import Pagination


class TestPaginationCalculation:
    """Tests pagination calculations."""

    def test_calculate_total_pages_exact(self):
        """Calculate exact number of pages."""
        pagination = Pagination(total_items=100, items_per_page=20)
        assert pagination.total_pages == 5

    def test_calculate_total_pages_round_up(self):
        """Round up when items don't divide evenly."""
        pagination = Pagination(total_items=105, items_per_page=20)
        assert pagination.total_pages == 6

    def test_calculate_total_pages_single(self):
        """Single page when items less than per page."""
        pagination = Pagination(total_items=15, items_per_page=20)
        assert pagination.total_pages == 1

    def test_calculate_total_pages_empty(self):
        """Handle empty items."""
        pagination = Pagination(total_items=0, items_per_page=20)
        assert pagination.total_pages == 0


class TestPaginationRange:
    """Tests visible page range calculation."""

    def test_visible_range_start(self):
        """Range at the beginning."""
        pagination = Pagination(
            total_items=100,
            items_per_page=10,
            current_page=1,
            max_visible_pages=5
        )
        start, end = pagination._get_visible_page_range()
        assert start == 1
        assert end == 5

    def test_visible_range_middle(self):
        """Range in the middle."""
        pagination = Pagination(
            total_items=100,
            items_per_page=10,
            current_page=5,
            max_visible_pages=5
        )
        start, end = pagination._get_visible_page_range()
        assert start == 3
        assert end == 7

    def test_visible_range_end(self):
        """Range at the end."""
        pagination = Pagination(
            total_items=100,
            items_per_page=10,
            current_page=10,
            max_visible_pages=5
        )
        start, end = pagination._get_visible_page_range()
        assert end == 10
        assert start == 6

    def test_visible_range_small_total(self):
        """Range when total pages less than max visible."""
        pagination = Pagination(
            total_items=30,
            items_per_page=10,
            current_page=2,
            max_visible_pages=5
        )
        start, end = pagination._get_visible_page_range()
        assert start == 1
        assert end == 3


class TestPaginationSlice:
    """Tests item slicing."""

    def test_get_current_slice_first_page(self):
        """Get items for first page."""
        pagination = Pagination(
            total_items=50,
            items_per_page=20,
            current_page=1
        )
        items = list(range(50))
        slice_result = pagination.get_current_slice(items)
        
        assert len(slice_result) == 20
        assert slice_result[0] == 0
        assert slice_result[-1] == 19

    def test_get_current_slice_second_page(self):
        """Get items for second page."""
        pagination = Pagination(
            total_items=50,
            items_per_page=20,
            current_page=2
        )
        items = list(range(50))
        slice_result = pagination.get_current_slice(items)
        
        assert len(slice_result) == 20
        assert slice_result[0] == 20
        assert slice_result[-1] == 39

    def test_get_current_slice_last_page_partial(self):
        """Get items for last page with partial content."""
        pagination = Pagination(
            total_items=50,
            items_per_page=20,
            current_page=3
        )
        items = list(range(50))
        slice_result = pagination.get_current_slice(items)
        
        assert len(slice_result) == 10
        assert slice_result[0] == 40
        assert slice_result[-1] == 49


class TestPaginationProps:
    """Tests pagination properties."""

    def test_default_props(self):
        """Default props are set correctly."""
        pagination = Pagination(total_items=100)
        
        assert pagination.props.items_per_page == 20
        assert pagination.props.current_page == 1
        assert pagination.props.max_visible_pages == 5
        assert pagination.props.show_first_last is True
        assert pagination.props.show_item_count is True

    def test_custom_props(self):
        """Custom props override defaults."""
        callback = Mock()
        pagination = Pagination(
            total_items=100,
            items_per_page=10,
            current_page=3,
            on_page_change=callback,
            max_visible_pages=7,
            show_first_last=False,
            show_item_count=False
        )
        
        assert pagination.props.items_per_page == 10
        assert pagination.props.current_page == 3
        assert pagination.props.on_page_change is callback
        assert pagination.props.max_visible_pages == 7
        assert pagination.props.show_first_last is False
        assert pagination.props.show_item_count is False


class TestPaginationEdgeCases:
    """Tests edge cases."""

    def test_zero_items(self):
        """Handle zero items gracefully."""
        pagination = Pagination(total_items=0)
        assert pagination.total_pages == 0

    def test_single_item(self):
        """Handle single item."""
        pagination = Pagination(total_items=1, items_per_page=20)
        assert pagination.total_pages == 1

    def test_large_numbers(self):
        """Handle large numbers."""
        pagination = Pagination(total_items=1000000, items_per_page=20)
        assert pagination.total_pages == 50000

    def test_current_page_beyond_total(self):
        """Handle current page beyond total pages."""
        pagination = Pagination(
            total_items=50,
            items_per_page=20,
            current_page=100
        )
        # Should still work, though UI will show disabled next
        assert pagination.total_pages == 3
