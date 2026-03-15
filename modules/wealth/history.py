# -*- coding: utf-8 -*-
"""
Historique du patrimoine.
"""

from datetime import date
from typing import Any

from modules.db.connection import get_db_connection


def record_wealth_snapshot(
    total_wealth: float,
    snapshot_date: date | None = None,
) -> int:
    """
    Enregistre un snapshot du patrimoine.
    
    Args:
        total_wealth: Valeur totale
        snapshot_date: Date du snapshot
    
    Returns:
        ID du snapshot
    """
    snapshot_date = snapshot_date or date.today()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO wealth_history (total_wealth, snapshot_date)
            VALUES (?, ?)
        """,
            (total_wealth, snapshot_date),
        )
        conn.commit()
        return cursor.lastrowid


def get_wealth_history() -> list[dict[str, Any]]:
    """
    Récupère l'historique du patrimoine.
    
    Returns:
        Liste des snapshots
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM wealth_history ORDER BY snapshot_date ASC"
        )
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def calculate_wealth_growth(history: list[dict]) -> dict[str, float]:
    """
    Calcule la croissance du patrimoine.
    
    Args:
        history: Liste des snapshots
    
    Returns:
        Dict avec absolute et percentage
    """
    if len(history) < 2:
        return {"absolute": 0, "percentage": 0}
    
    first = history[0].get('total', 0)
    last = history[-1].get('total', 0)
    
    absolute = last - first
    percentage = (absolute / first * 100) if first != 0 else 0
    
    return {
        "absolute": round(absolute, 2),
        "percentage": round(percentage, 2),
    }


def get_latest_wealth() -> float:
    """
    Récupère la dernière valeur du patrimoine.
    
    Returns:
        Dernière valeur ou 0
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT total_wealth FROM wealth_history ORDER BY snapshot_date DESC LIMIT 1"
        )
        row = cursor.fetchone()
        return row[0] if row else 0
