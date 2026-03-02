"""Category repository."""

from typing import Any

from modules.db.repositories.base import BaseRepository
from modules.db.categories import (
    get_categories_df,
    add_category,
    update_category_emoji,
    update_category_fixed,
    delete_category,
    merge_categories,
)


class CategoryRepository(BaseRepository[dict]):
    """Repository for category operations."""

    def get_by_id(self, id: int) -> dict | None:
        """Get category by ID."""
        df = get_categories_df()
        cat = df[df["id"] == id]
        return cat.to_dict("records")[0] if not cat.empty else None

    def get_by_name(self, name: str) -> dict | None:
        """Get category by name."""
        df = get_categories_df()
        cat = df[df["name"] == name]
        return cat.to_dict("records")[0] if not cat.empty else None

    def get_all(self, filters: dict[str, Any] | None = None) -> list[dict]:
        """Get all categories."""
        df = get_categories_df()

        # Apply simple filters if provided
        if filters:
            for key, value in filters.items():
                if key in df.columns:
                    df = df[df[key] == value]

        return df.to_dict("records") if not df.empty else []

    def create(self, data: dict[str, Any]) -> dict:
        """Create new category."""
        name = data.get("name")
        emoji = data.get("emoji", "🏷️")
        is_fixed = data.get("is_fixed", 0)

        if not name:
            raise ValueError("Category name is required")

        success = add_category(name, emoji, is_fixed)
        if success:
            return self.get_by_name(name)
        raise ValueError(f"Category '{name}' already exists or could not be created")

    def update(self, id: int, data: dict[str, Any]) -> dict | None:
        """Update category."""
        current = self.get_by_id(id)
        if not current:
            return None

        # Update emoji if provided
        if "emoji" in data:
            update_category_emoji(id, data["emoji"])

        # Update is_fixed if provided
        if "is_fixed" in data:
            update_category_fixed(id, int(data["is_fixed"]))

        # Update suggested_tags if provided
        if "suggested_tags" in data:
            from modules.db.categories import update_category_suggested_tags

            update_category_suggested_tags(id, data["suggested_tags"])

        return self.get_by_id(id)

    def delete(self, id: int) -> bool:
        """Delete category by ID."""
        current = self.get_by_id(id)
        if not current:
            return False

        delete_category(id)
        return True

    def merge(self, source: str, target: str) -> dict:
        """Merge two categories."""
        return merge_categories(source, target)

    def get_names(self) -> list[str]:
        """Get list of all category names."""
        from modules.db.categories import get_categories

        return get_categories()

    def get_with_emojis(self) -> dict[str, str]:
        """Get dictionary of categories with their emojis."""
        from modules.db.categories import get_categories_with_emojis

        return get_categories_with_emojis()
