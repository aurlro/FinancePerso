"""Gestion des mappings Carte → Membre pour la Couple Edition."""

from __future__ import annotations

from modules.db.connection import get_db_connection


def get_all_card_mappings(active_only: bool = True) -> list[dict]:
    """Récupère tous les mappings carte → membre.

    Args:
        active_only: Si True, n'affiche que les mappings actifs

    Returns:
        Liste des mappings avec infos membres
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT 
                cm.id,
                cm.card_suffix,
                cm.member_id,
                cm.account_type,
                cm.label,
                cm.is_active,
                cm.created_at,
                m.name as member_name
            FROM card_member_mappings cm
            LEFT JOIN members m ON cm.member_id = m.id
        """
        if active_only:
            query += " WHERE cm.is_active = 1"
        query += " ORDER BY cm.account_type, cm.card_suffix"

        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_card_mapping(card_suffix: str) -> dict | None:
    """Récupère le mapping pour une carte spécifique.

    Args:
        card_suffix: Les 4 derniers chiffres de la carte

    Returns:
        Le mapping ou None si non trouvé
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                cm.*,
                m.name as member_name
            FROM card_member_mappings cm
            LEFT JOIN members m ON cm.member_id = m.id
            WHERE cm.card_suffix = ? AND cm.is_active = 1
        """,
            (card_suffix,),
        )
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None


def save_card_mapping(
    card_suffix: str,
    account_type: str,
    member_id: int | None = None,
    label: str | None = None,
) -> bool:
    """Crée ou met à jour un mapping carte → membre.

    Args:
        card_suffix: Les 4 derniers chiffres de la carte
        account_type: 'PERSONAL_A', 'PERSONAL_B', 'JOINT', ou 'UNKNOWN'
        member_id: ID du membre (None pour JOINT ou UNKNOWN)
        label: Libellé lisible (ex: "CB Perso Aurélien")

    Returns:
        True si succès
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO card_member_mappings 
                    (card_suffix, member_id, account_type, label)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(card_suffix) DO UPDATE SET
                    member_id = excluded.member_id,
                    account_type = excluded.account_type,
                    label = excluded.label,
                    is_active = 1,
                    updated_at = CURRENT_TIMESTAMP
            """,
                (card_suffix, member_id, account_type, label),
            )
            conn.commit()
            return True
    except Exception as e:
        from modules.logger import logger

        logger.error(f"Erreur sauvegarde mapping carte: {e}")
        return False


def delete_card_mapping(card_suffix: str, soft: bool = True) -> bool:
    """Supprime ou désactive un mapping.

    Args:
        card_suffix: Les 4 derniers chiffres de la carte
        soft: Si True, désactive seulement (is_active = 0)

    Returns:
        True si succès
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if soft:
                cursor.execute(
                    """
                    UPDATE card_member_mappings 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE card_suffix = ?
                """,
                    (card_suffix,),
                )
            else:
                cursor.execute(
                    "DELETE FROM card_member_mappings WHERE card_suffix = ?", (card_suffix,)
                )
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        from modules.logger import logger

        logger.error(f"Erreur suppression mapping carte: {e}")
        return False


def get_unknown_cards() -> list[dict]:
    """Récupère les cartes non encore mappées.

    Returns:
        Liste des cartes avec leurs statistiques d'utilisation
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                t.card_suffix,
                COUNT(*) as transaction_count,
                MIN(t.date) as first_seen,
                MAX(t.date) as last_seen,
                SUM(CASE WHEN t.amount < 0 THEN -t.amount ELSE 0 END) as total_debits,
                GROUP_CONCAT(DISTINCT t.account_label) as account_labels
            FROM transactions t
            WHERE t.card_suffix IS NOT NULL 
              AND t.card_suffix != ''
              AND t.card_suffix NOT IN (
                  SELECT card_suffix FROM card_member_mappings WHERE is_active = 1
              )
            GROUP BY t.card_suffix
            ORDER BY transaction_count DESC
        """)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def detect_cards_from_transactions() -> list[dict]:
    """Détecte automatiquement les cartes présentes dans les transactions.
    Crée des mappings "UNKNOWN" pour les nouvelles cartes.

    Returns:
        Liste des nouvelles cartes détectées
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Récupérer les cartes non mappées
        cursor.execute("""
            SELECT DISTINCT card_suffix
            FROM transactions
            WHERE card_suffix IS NOT NULL 
              AND card_suffix != ''
              AND card_suffix NOT IN (
                  SELECT card_suffix FROM card_member_mappings WHERE is_active = 1
              )
        """)
        new_cards = [row[0] for row in cursor.fetchall()]

        # Créer les mappings UNKNOWN
        for card_suffix in new_cards:
            cursor.execute(
                """
                INSERT INTO card_member_mappings 
                    (card_suffix, account_type, label)
                VALUES (?, 'UNKNOWN', ?)
                ON CONFLICT(card_suffix) DO UPDATE SET
                    is_active = 1
            """,
                (card_suffix, f"Carte ****{card_suffix} (à configurer)"),
            )

        conn.commit()

        # Retourner les infos des nouvelles cartes
        if new_cards:
            placeholders = ",".join("?" * len(new_cards))
            cursor.execute(
                f"""  # nosec B608
                SELECT
                    card_suffix,
                    COUNT(*) as transaction_count,
                    MIN(date) as first_seen
                FROM transactions
                WHERE card_suffix IN ({placeholders})
                GROUP BY card_suffix
            """,
                tuple(new_cards),
            )
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

        return []


def get_cards_summary() -> dict:
    """Récupère un résumé des cartes configurées.

    Returns:
        Dict avec stats par type de compte
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                account_type,
                COUNT(*) as count,
                COUNT(CASE WHEN member_id IS NOT NULL THEN 1 END) as mapped_to_member
            FROM card_member_mappings
            WHERE is_active = 1
            GROUP BY account_type
        """)
        result = {
            "total": 0,
            "PERSONAL_A": {"count": 0, "mapped": 0},
            "PERSONAL_B": {"count": 0, "mapped": 0},
            "JOINT": {"count": 0, "mapped": 0},
            "UNKNOWN": {"count": 0, "mapped": 0},
        }
        for row in cursor.fetchall():
            account_type, count, mapped = row
            result[account_type] = {"count": count, "mapped": mapped}
            result["total"] += count
        return result
