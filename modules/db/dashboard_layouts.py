"""
Dashboard Layouts Database Operations
Gestion des layouts de dashboard en base de données.
"""

import json
from datetime import datetime

from modules.db.connection import get_db_connection
from modules.logger import logger


def get_layout(name: str = "default") -> list[dict] | None:
    """
    Récupère un layout par son nom.

    Args:
        name: Nom du layout (default: "default")

    Returns:
        Liste des widgets ou None si non trouvé
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT layout_json FROM dashboard_layouts WHERE name = ?", (name,))
            result = cursor.fetchone()

            if result:
                return json.loads(result[0])
            return None
    except Exception as e:
        logger.error(f"Error loading layout '{name}': {e}")
        return None


def get_active_layout() -> list[dict] | None:
    """
    Récupère le layout actuellement actif.

    Returns:
        Liste des widgets ou None
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT layout_json FROM dashboard_layouts WHERE is_active = 1 ORDER BY updated_at DESC LIMIT 1"
            )
            result = cursor.fetchone()

            if result:
                return json.loads(result[0])

            # Fallback: try to get 'default' layout
            cursor.execute(
                "SELECT layout_json FROM dashboard_layouts WHERE name = 'default' LIMIT 1"
            )
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])

            return None
    except Exception as e:
        logger.error(f"Error loading active layout: {e}")
        return None


def save_layout(name: str, layout: list[dict], set_active: bool = False) -> bool:
    """
    Sauvegarde un layout dans la base de données.

    Args:
        name: Nom du layout
        layout: Liste des widgets
        set_active: Si True, définit ce layout comme actif

    Returns:
        True si succès
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            layout_json = json.dumps(layout, ensure_ascii=False)

            # Check if layout exists
            cursor.execute("SELECT id FROM dashboard_layouts WHERE name = ?", (name,))
            existing = cursor.fetchone()

            if existing:
                # Update
                cursor.execute(
                    """UPDATE dashboard_layouts 
                       SET layout_json = ?, updated_at = ?, is_active = CASE WHEN ? THEN 1 ELSE is_active END
                       WHERE name = ?""",
                    (layout_json, datetime.now().isoformat(), set_active, name),
                )
            else:
                # Insert
                cursor.execute(
                    """INSERT INTO dashboard_layouts (name, layout_json, is_active, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        name,
                        layout_json,
                        1 if set_active else 0,
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                    ),
                )

            # If setting this as active, deactivate others
            if set_active:
                cursor.execute(
                    "UPDATE dashboard_layouts SET is_active = 0 WHERE name != ?", (name,)
                )

            conn.commit()
            logger.info(f"Layout '{name}' saved successfully (active={set_active})")
            return True

    except Exception as e:
        logger.error(f"Error saving layout '{name}': {e}")
        return False


def set_active_layout(name: str) -> bool:
    """
    Définit un layout comme actif.

    Args:
        name: Nom du layout à activer

    Returns:
        True si succès
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Deactivate all
            cursor.execute("UPDATE dashboard_layouts SET is_active = 0")

            # Activate specified
            cursor.execute(
                "UPDATE dashboard_layouts SET is_active = 1, updated_at = ? WHERE name = ?",
                (datetime.now().isoformat(), name),
            )

            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"Layout '{name}' is now active")
                return True
            else:
                logger.warning(f"Layout '{name}' not found")
                return False

    except Exception as e:
        logger.error(f"Error setting active layout '{name}': {e}")
        return False


def delete_layout(name: str) -> bool:
    """
    Supprime un layout.

    Args:
        name: Nom du layout à supprimer

    Returns:
        True si succès
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dashboard_layouts WHERE name = ?", (name,))

            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"Layout '{name}' deleted")
                return True
            return False

    except Exception as e:
        logger.error(f"Error deleting layout '{name}': {e}")
        return False


def list_layouts() -> list[dict]:
    """
    Liste tous les layouts disponibles.

    Returns:
        Liste des infos des layouts
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT name, is_active, created_at, updated_at 
                   FROM dashboard_layouts 
                   ORDER BY updated_at DESC"""
            )

            layouts = []
            for row in cursor.fetchall():
                layouts.append(
                    {
                        "name": row[0],
                        "is_active": bool(row[1]),
                        "created_at": row[2],
                        "updated_at": row[3],
                    }
                )
            return layouts

    except Exception as e:
        logger.error(f"Error listing layouts: {e}")
        return []


def layout_exists(name: str) -> bool:
    """
    Vérifie si un layout existe.

    Args:
        name: Nom du layout

    Returns:
        True si existe
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM dashboard_layouts WHERE name = ?", (name,))
            return cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Error checking layout existence: {e}")
        return False


def duplicate_layout(source_name: str, new_name: str) -> bool:
    """
    Duplique un layout existant.

    Args:
        source_name: Nom du layout source
        new_name: Nom du nouveau layout

    Returns:
        True si succès
    """
    try:
        layout = get_layout(source_name)
        if layout:
            return save_layout(new_name, layout, set_active=False)
        return False
    except Exception as e:
        logger.error(f"Error duplicating layout '{source_name}' to '{new_name}': {e}")
        return False


__all__ = [
    "get_layout",
    "get_active_layout",
    "save_layout",
    "set_active_layout",
    "delete_layout",
    "list_layouts",
    "layout_exists",
    "duplicate_layout",
]
