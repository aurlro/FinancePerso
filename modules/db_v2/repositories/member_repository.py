"""
Member Repository
=================

Repository for Member and MemberMapping entities.
Handles CRUD operations and domain-specific member management.
"""

import sqlite3
from typing import Optional, Any

import pandas as pd
import streamlit as st

from modules.db_v2.base.repository import BaseRepository
from modules.db_v2.models.member import Member, MemberMapping, MemberType
from modules.db.connection import get_db_connection
from modules.core.events import EventBus
from modules.logger import logger


class MemberRepository(BaseRepository[Member]):
    """
    Repository for managing Member entities.

    Provides CRUD operations and domain-specific methods for member management,
    including member mappings (card suffix associations) and member type handling.

    Example:
        >>> repo = MemberRepository()
        >>> member = Member(name="John Doe", member_type=MemberType.HOUSEHOLD.value)
        >>> member_id = repo.create(member)
        >>> member = repo.get_by_id(member_id)
    """

    _table: str = "members"
    _entity_class: type = Member

    # --------------------------------------------------------------------------
    # CRUD Methods
    # --------------------------------------------------------------------------

    @st.cache_data(ttl=300)
    def get_by_id(_self, entity_id: int) -> Optional[Member]:
        """
        Get member by primary key.

        Args:
            entity_id: Primary key value

        Returns:
            Member if found, None otherwise

        Example:
            >>> repo = MemberRepository()
            >>> member = repo.get_by_id(1)
            >>> if member:
            ...     print(f"Found: {member.name}")
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM members WHERE id = ?",
                (entity_id,)
            )
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                series = pd.Series(dict(zip(columns, row)))
                return Member.from_series(series)
            return None

    @st.cache_data(ttl=300)
    def get_all(
        _self,
        filters: Optional[dict[str, Any]] = None,
        order_by: Optional[str] = "name",
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> pd.DataFrame:
        """
        Get all members with optional filtering.

        Args:
            filters: Column-value pairs for filtering (e.g., {"member_type": "HOUSEHOLD"})
            order_by: SQL ORDER BY clause (default: "name")
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            DataFrame with matching members

        Example:
            >>> repo = MemberRepository()
            >>> # Get all household members
            >>> df = repo.get_all(filters={"member_type": "HOUSEHOLD"})
            >>> # Get first 10 members ordered by creation date
            >>> df = repo.get_all(order_by="created_at DESC", limit=10)
        """
        with get_db_connection() as conn:
            query = f"SELECT * FROM members"
            params = []

            # Apply filters
            if filters:
                conditions = []
                for col, val in filters.items():
                    conditions.append(f"{col} = ?")
                    params.append(val)
                query += " WHERE " + " AND ".join(conditions)

            # Apply ordering
            if order_by:
                query += f" ORDER BY {order_by}"

            # Apply limit and offset
            if limit is not None:
                query += f" LIMIT ? OFFSET ?"
                params.extend([limit, offset])

            return pd.read_sql_query(query, conn, params=params)

    def create(self, entity: Member) -> int:
        """
        Create a new member.

        Args:
            entity: Member to create

        Returns:
            ID of created member

        Raises:
            sqlite3.IntegrityError: If member name already exists

        Example:
            >>> repo = MemberRepository()
            >>> member = Member(name="Jane Doe", member_type=MemberType.HOUSEHOLD.value)
            >>> member_id = repo.create(member)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO members (name, member_type, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    """,
                    (entity.name, entity.member_type)
                )
                conn.commit()
                entity_id = cursor.lastrowid
                entity.id = entity_id
                logger.info(f"Member created: {entity.name} ({entity.member_type})")
                EventBus.emit("members.changed", action="created", member_id=entity_id)
                return entity_id
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to create member '{entity.name}': {e}")
                raise

    def update(self, entity_id: int, data: dict[str, Any]) -> bool:
        """
        Update member fields.

        Args:
            entity_id: ID of member to update
            data: Field-value pairs to update (e.g., {"name": "New Name"})

        Returns:
            True if updated, False if not found

        Raises:
            sqlite3.IntegrityError: If updating to a duplicate name

        Example:
            >>> repo = MemberRepository()
            >>> updated = repo.update(1, {"name": "John Smith"})
            >>> updated = repo.update(1, {"member_type": MemberType.EXTERNAL.value})
        """
        if not data:
            return False

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if member exists
            cursor.execute("SELECT 1 FROM members WHERE id = ?", (entity_id,))
            if not cursor.fetchone():
                return False

            # Build update query
            fields = []
            params = []
            for key, value in data.items():
                if key != "id":  # Prevent updating ID
                    fields.append(f"{key} = ?")
                    params.append(value)
            params.append(entity_id)

            try:
                cursor.execute(
                    f"UPDATE members SET {', '.join(fields)} WHERE id = ?",
                    params
                )
                conn.commit()
                logger.info(f"Member {entity_id} updated: {data}")
                EventBus.emit("members.changed", action="updated", member_id=entity_id)
                return True
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to update member {entity_id}: {e}")
                raise

    def delete(self, entity_id: int) -> bool:
        """
        Delete member by ID.

        Args:
            entity_id: ID of member to delete

        Returns:
            True if deleted, False if not found

        Example:
            >>> repo = MemberRepository()
            >>> deleted = repo.delete(1)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if member exists
            cursor.execute("SELECT 1 FROM members WHERE id = ?", (entity_id,))
            if not cursor.fetchone():
                return False

            cursor.execute("DELETE FROM members WHERE id = ?", (entity_id,))
            conn.commit()
            logger.info(f"Member {entity_id} deleted")
            EventBus.emit("members.changed", action="deleted", member_id=entity_id)
            return True

    @st.cache_data(ttl=300)
    def exists(_self, entity_id: int) -> bool:
        """
        Check if member exists.

        Args:
            entity_id: ID to check

        Returns:
            True if exists, False otherwise

        Example:
            >>> repo = MemberRepository()
            >>> if repo.exists(1):
            ...     print("Member exists")
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM members WHERE id = ?", (entity_id,))
            return cursor.fetchone() is not None

    # --------------------------------------------------------------------------
    # Domain-specific Methods
    # --------------------------------------------------------------------------

    @st.cache_data(ttl=300)
    def get_by_name(_self, name: str) -> Optional[Member]:
        """
        Get member by name.

        Args:
            name: Member name to search for

        Returns:
            Member if found, None otherwise

        Example:
            >>> repo = MemberRepository()
            >>> member = repo.get_by_name("John Doe")
            >>> if member:
            ...     print(f"Found member ID: {member.id}")
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM members WHERE name = ?",
                (name,)
            )
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                series = pd.Series(dict(zip(columns, row)))
                return Member.from_series(series)
            return None

    def rename_member(self, old_name: str, new_name: str) -> int:
        """
        Rename a member and propagate changes to all related tables.

        Updates:
        - members.name
        - transactions.member
        - transactions.beneficiary
        - member_mappings.member_name

        Args:
            old_name: Current member name
            new_name: New member name

        Returns:
            Total number of affected transactions

        Example:
            >>> repo = MemberRepository()
            >>> count = repo.rename_member("John", "Johnny")
            >>> print(f"Updated {count} transactions")
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Update members table
            cursor.execute(
                "UPDATE members SET name = ? WHERE name = ?",
                (new_name, old_name)
            )

            # Update transactions (member field)
            cursor.execute(
                "UPDATE transactions SET member = ? WHERE member = ?",
                (new_name, old_name)
            )
            tx_count = cursor.rowcount

            # Update transactions (beneficiary field)
            cursor.execute(
                "UPDATE transactions SET beneficiary = ? WHERE beneficiary = ?",
                (new_name, old_name)
            )
            tx_count += cursor.rowcount

            # Update member mappings
            cursor.execute(
                "UPDATE member_mappings SET member_name = ? WHERE member_name = ?",
                (new_name, old_name)
            )

            conn.commit()

        # Invalidate both member and transaction caches
        EventBus.emit("members.changed", action="renamed", old_name=old_name, new_name=new_name)
        EventBus.emit("transactions.changed", action="member_renamed")

        logger.info(f"Renamed member '{old_name}' → '{new_name}': {tx_count} transactions updated")
        return tx_count

    def update_member_type(self, entity_id: int, member_type: str) -> bool:
        """
        Update the type of a member (HOUSEHOLD or EXTERNAL).

        Args:
            entity_id: ID of member to update
            member_type: New member type (MemberType.HOUSEHOLD or MemberType.EXTERNAL)

        Returns:
            True if updated, False if not found

        Example:
            >>> repo = MemberRepository()
            >>> updated = repo.update_member_type(1, MemberType.EXTERNAL.value)
        """
        return self.update(entity_id, {"member_type": member_type})

    @st.cache_data(ttl=300)
    def get_household_members(_self) -> pd.DataFrame:
        """
        Get only household members.

        Returns:
            DataFrame with household members only

        Example:
            >>> repo = MemberRepository()
            >>> household_df = repo.get_household_members()
            >>> print(f"Household has {len(household_df)} members")
        """
        return self.get_all(filters={"member_type": MemberType.HOUSEHOLD.value})

    @st.cache_data(ttl=300)
    def get_external_entities(_self) -> pd.DataFrame:
        """
        Get only external entities.

        Returns:
            DataFrame with external entities only

        Example:
            >>> repo = MemberRepository()
            >>> external_df = repo.get_external_entities()
            >>> print(f"Found {len(external_df)} external entities")
        """
        return self.get_all(filters={"member_type": MemberType.EXTERNAL.value})

    # --------------------------------------------------------------------------
    # Member Mapping Methods (Card Suffix Mappings)
    # --------------------------------------------------------------------------

    @st.cache_data(ttl=300)
    def get_mappings(_self, member_name: Optional[str] = None) -> pd.DataFrame:
        """
        Get all member mappings or filter by member name.

        Args:
            member_name: Optional member name to filter by

        Returns:
            DataFrame with columns: id, card_suffix, member_name, created_at

        Example:
            >>> repo = MemberRepository()
            >>> # Get all mappings
            >>> all_mappings = repo.get_mappings()
            >>> # Get mappings for specific member
            >>> john_mappings = repo.get_mappings(member_name="John")
        """
        with get_db_connection() as conn:
            query = "SELECT * FROM member_mappings"
            params = []

            if member_name:
                query += " WHERE member_name = ?"
                params.append(member_name)

            query += " ORDER BY member_name, card_suffix"

            return pd.read_sql_query(query, conn, params=params)

    def add_mapping(self, card_suffix: str, member_name: str) -> bool:
        """
        Add a new card suffix to member mapping.

        Args:
            card_suffix: Last digits of card/account number
            member_name: Member name to associate with this card

        Returns:
            True if mapping was added/updated, False otherwise

        Example:
            >>> repo = MemberRepository()
            >>> repo.add_mapping("1234", "John Doe")
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO member_mappings 
                    (card_suffix, member_name, created_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    """,
                    (card_suffix, member_name)
                )
                conn.commit()
                logger.info(f"Member mapping added: {card_suffix} -> {member_name}")
                EventBus.emit(
                    "members.changed",
                    action="mapping_added",
                    card_suffix=card_suffix,
                    member_name=member_name
                )
                return True
            except sqlite3.Error as e:
                logger.error(f"Failed to add mapping {card_suffix} -> {member_name}: {e}")
                return False

    def delete_mapping(self, mapping_id: int) -> bool:
        """
        Delete a member mapping by ID.

        Args:
            mapping_id: ID of the mapping to delete

        Returns:
            True if deleted, False if not found

        Example:
            >>> repo = MemberRepository()
            >>> deleted = repo.delete_mapping(1)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if mapping exists
            cursor.execute("SELECT 1 FROM member_mappings WHERE id = ?", (mapping_id,))
            if not cursor.fetchone():
                return False

            cursor.execute("DELETE FROM member_mappings WHERE id = ?", (mapping_id,))
            conn.commit()
            logger.info(f"Member mapping {mapping_id} deleted")
            EventBus.emit("members.changed", action="mapping_deleted", mapping_id=mapping_id)
            return True

    @st.cache_data(ttl=300)
    def get_member_by_card_suffix(_self, suffix: str) -> Optional[str]:
        """
        Detect member name from card suffix.

        Args:
            suffix: Card suffix to look up

        Returns:
            Member name if found, None otherwise

        Example:
            >>> repo = MemberRepository()
            >>> member = repo.get_member_by_card_suffix("1234")
            >>> if member:
            ...     print(f"Card belongs to {member}")
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT member_name FROM member_mappings WHERE card_suffix = ?",
                (suffix,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
