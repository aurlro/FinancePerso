# -*- coding: utf-8 -*-
"""
Gestion des actifs.
"""

from datetime import date
from typing import Any

from modules.db.connection import get_db_connection


def add_asset(
    name: str,
    asset_type: str,
    value: float,
    acquisition_date: date | None = None,
    category: str = "Autre",
) -> int:
    """
    Ajoute un nouvel actif.
    
    Args:
        name: Nom de l'actif
        asset_type: Type (real_estate, savings, investment, etc.)
        value: Valeur
        acquisition_date: Date d'acquisition
        category: Catégorie
    
    Returns:
        ID de l'actif créé
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO assets (name, type, value, acquisition_date, category, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (name, asset_type, value, acquisition_date, category, date.today()),
        )
        conn.commit()
        return cursor.lastrowid


def get_assets() -> list[dict[str, Any]]:
    """
    Récupère tous les actifs.
    
    Returns:
        Liste des actifs
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assets ORDER BY created_at DESC")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_asset(asset_id: int) -> dict[str, Any] | None:
    """
    Récupère un actif par ID.
    
    Args:
        asset_id: ID de l'actif
    
    Returns:
        Actif ou None
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None


def update_asset_value(
    asset_id: int,
    new_value: float,
    valuation_date: date | None = None,
) -> bool:
    """
    Met à jour la valeur d'un actif.
    
    Args:
        asset_id: ID de l'actif
        new_value: Nouvelle valeur
        valuation_date: Date de valorisation
    
    Returns:
        True si succès
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE assets SET value = ?, updated_at = ? WHERE id = ?",
            (new_value, valuation_date or date.today(), asset_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_asset(asset_id: int) -> bool:
    """
    Supprime un actif.
    
    Args:
        asset_id: ID de l'actif
    
    Returns:
        True si supprimé
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
        conn.commit()
        return cursor.rowcount > 0
