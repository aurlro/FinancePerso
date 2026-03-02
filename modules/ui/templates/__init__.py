"""Templates - Layouts de pages réutilisables.

Les templates définissent la structure générale des pages :
- PageLayout
- SidebarLayout
- ModalLayout

Usage:
    from modules.ui.templates import PageLayout

    PageLayout.render(
        title="Ma Page",
        content=render_content,
        actions=[{"label": "Sauver", "on_click": save}]
    )
"""

from .page_layout import PageLayout

__all__ = ["PageLayout"]
