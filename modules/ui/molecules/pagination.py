"""
Pagination molecule for the Design System.

Usage:
    pagination = Pagination(
        total_items=150,
        items_per_page=20,
        current_page=1,
        on_page_change=lambda p: st.session_state.update(page=p)
    )
    pagination.render()
"""

from dataclasses import dataclass
from typing import Callable

import streamlit as st

from modules.ui.tokens.colors import Colors
from modules.ui.tokens.spacing import Spacing


@dataclass
class PaginationProps:
    """Props for the Pagination component."""

    total_items: int
    items_per_page: int = 20
    current_page: int = 1
    on_page_change: Callable[[int], None] | None = None
    max_visible_pages: int = 5
    show_first_last: bool = True
    show_item_count: bool = True


class Pagination:
    """Pagination component with Emerald Design System styling."""

    def __init__(
        self,
        total_items: int,
        items_per_page: int = 20,
        current_page: int = 1,
        on_page_change: Callable[[int], None] | None = None,
        max_visible_pages: int = 5,
        show_first_last: bool = True,
        show_item_count: bool = True,
    ):
        self.props = PaginationProps(
            total_items=total_items,
            items_per_page=items_per_page,
            current_page=current_page,
            on_page_change=on_page_change,
            max_visible_pages=max_visible_pages,
            show_first_last=show_first_last,
            show_item_count=show_item_count,
        )
        self.total_pages = self._calculate_total_pages()

    def _calculate_total_pages(self) -> int:
        """Calculate total number of pages."""
        return (self.props.total_items + self.props.items_per_page - 1) // self.props.items_per_page

    def _get_visible_page_range(self) -> tuple[int, int]:
        """Calculate the range of visible page numbers."""
        half_visible = self.props.max_visible_pages // 2
        
        if self.total_pages <= self.props.max_visible_pages:
            return 1, self.total_pages
        
        # Calculate start and end
        start = max(1, self.props.current_page - half_visible)
        end = min(self.total_pages, start + self.props.max_visible_pages - 1)
        
        # Adjust if we're at the end
        if end - start + 1 < self.props.max_visible_pages:
            start = max(1, end - self.props.max_visible_pages + 1)
        
        return start, end

    def _render_page_button(self, page_num: int, is_current: bool = False) -> None:
        """Render a single page button."""
        label = str(page_num)
        key = f"pagination_page_{page_num}"
        
        if is_current:
            # Current page - Emerald styling
            st.button(
                label,
                key=key,
                type="primary",
                disabled=True,
                use_container_width=False,
            )
        else:
            # Other page
            if st.button(
                label,
                key=key,
                type="secondary",
                use_container_width=False,
            ):
                if self.props.on_page_change:
                    self.props.on_page_change(page_num)

    def _render_first_button(self) -> None:
        """Render first page button."""
        disabled = self.props.current_page == 1
        
        if st.button(
            "⟪",
            key="pagination_first",
            disabled=disabled,
            help="Première page",
        ):
            if self.props.on_page_change:
                self.props.on_page_change(1)

    def _render_prev_button(self) -> None:
        """Render previous page button."""
        disabled = self.props.current_page == 1
        
        if st.button(
            "◀",
            key="pagination_prev",
            disabled=disabled,
            help="Page précédente",
        ):
            if self.props.on_page_change:
                self.props.on_page_change(self.props.current_page - 1)

    def _render_next_button(self) -> None:
        """Render next page button."""
        disabled = self.props.current_page >= self.total_pages
        
        if st.button(
            "▶",
            key="pagination_next",
            disabled=disabled,
            help="Page suivante",
        ):
            if self.props.on_page_change:
                self.props.on_page_change(self.props.current_page + 1)

    def _render_last_button(self) -> None:
        """Render last page button."""
        disabled = self.props.current_page >= self.total_pages
        
        if st.button(
            "⟫",
            key="pagination_last",
            disabled=disabled,
            help="Dernière page",
        ):
            if self.props.on_page_change:
                self.props.on_page_change(self.total_pages)

    def _render_item_count(self) -> None:
        """Render item count information."""
        start_item = (self.props.current_page - 1) * self.props.items_per_page + 1
        end_item = min(
            self.props.current_page * self.props.items_per_page,
            self.props.total_items
        )
        
        st.caption(
            f"Affichage {start_item}-{end_item} sur {self.props.total_items} éléments"
        )

    def render(self) -> None:
        """Render the pagination component."""
        if self.total_pages <= 1:
            if self.props.show_item_count:
                self._render_item_count()
            return

        # Use columns for layout
        cols = st.columns([1, 6, 1])
        
        with cols[0]:
            if self.props.show_item_count:
                self._render_item_count()
        
        with cols[1]:
            # Pagination controls
            nav_cols = st.columns(
                [0.5, 0.5]  # First, Prev
                + [0.5] * min(self.props.max_visible_pages, self.total_pages)  # Pages
                + [0.5, 0.5]  # Next, Last
            )
            
            col_idx = 0
            
            # First button
            if self.props.show_first_last:
                with nav_cols[col_idx]:
                    self._render_first_button()
                col_idx += 1
            
            # Previous button
            with nav_cols[col_idx]:
                self._render_prev_button()
            col_idx += 1
            
            # Page numbers
            start_page, end_page = self._get_visible_page_range()
            for page_num in range(start_page, end_page + 1):
                with nav_cols[col_idx]:
                    self._render_page_button(
                        page_num,
                        is_current=(page_num == self.props.current_page)
                    )
                col_idx += 1
            
            # Next button
            with nav_cols[col_idx]:
                self._render_next_button()
            col_idx += 1
            
            # Last button
            if self.props.show_first_last:
                with nav_cols[col_idx]:
                    self._render_last_button()

    def get_current_slice(self, items: list) -> list:
        """Get the current slice of items for the current page."""
        start = (self.props.current_page - 1) * self.props.items_per_page
        end = start + self.props.items_per_page
        return items[start:end]


def render_pagination(
    total_items: int,
    items_per_page: int = 20,
    current_page: int = 1,
    on_page_change: Callable[[int], None] | None = None,
    key: str = "pagination",
) -> Pagination:
    """
    Convenience function to render pagination.
    
    Returns the Pagination instance for accessing current slice.
    """
    pagination = Pagination(
        total_items=total_items,
        items_per_page=items_per_page,
        current_page=current_page,
        on_page_change=on_page_change,
    )
    pagination.render()
    return pagination
