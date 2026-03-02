"""Transaction repository."""

from typing import Any

import pandas as pd

from modules.db.repositories.base import BaseRepository
from modules.db.transactions import (
    get_transaction_by_id,
    get_all_transactions,
    save_transactions,
    delete_transaction,
    get_pending_transactions,
)


class TransactionRepository(BaseRepository[dict]):
    """Repository for transaction operations."""

    def get_by_id(self, id: int) -> dict | None:
        """Get transaction by ID."""
        return get_transaction_by_id(id)

    def get_all(self, filters: dict[str, Any] | None = None) -> list[dict]:
        """Get all transactions with optional filters."""
        df = get_all_transactions(filters=filters)
        return df.to_dict("records") if not df.empty else []

    def create(self, data: dict[str, Any]) -> dict:
        """Create new transaction."""
        df = pd.DataFrame([data])
        new_count, _ = save_transactions(df)
        if new_count > 0:
            return data
        raise ValueError("Transaction already exists or could not be created")

    def update(self, id: int, data: dict[str, Any]) -> dict | None:
        """Update transaction by ID."""
        from modules.db.transactions import update_transaction_category

        # Get current transaction
        current = self.get_by_id(id)
        if not current:
            return None

        # Extract fields to update
        new_category = data.get("category_validated", current.get("category_validated"))
        tags = data.get("tags", current.get("tags"))
        beneficiary = data.get("beneficiary", current.get("beneficiary"))
        notes = data.get("notes", current.get("notes"))

        update_transaction_category(id, new_category, tags, beneficiary, notes)
        return self.get_by_id(id)

    def delete(self, id: int) -> bool:
        """Delete transaction by ID."""
        deleted = delete_transaction(id)
        return deleted > 0

    def get_pending(self) -> list[dict]:
        """Get pending transactions."""
        df = get_pending_transactions()
        return df.to_dict("records") if not df.empty else []

    def get_by_period(self, month_str: str) -> list[dict]:
        """Get transactions for a specific period (YYYY-MM)."""
        filters = {"date": ("LIKE", f"{month_str}%")}
        return self.get_all(filters=filters)

    def bulk_update_category(
        self,
        tx_ids: list[int],
        new_category: str,
        tags: str | None = None,
        beneficiary: str | None = None,
        notes: str | None = None,
    ) -> bool:
        """Update multiple transactions' category."""
        from modules.db.transactions import bulk_update_transaction_status

        bulk_update_transaction_status(tx_ids, new_category, tags, beneficiary, notes)
        return True
