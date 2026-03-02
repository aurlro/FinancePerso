"""Gestion des paramètres couple et du contexte utilisateur."""

from __future__ import annotations

import json
from typing import Optional

from modules.db.connection import get_db_connection


def get_couple_settings() -> dict:
    """Récupère les paramètres couple (singleton).

    Returns:
        Dict avec tous les paramètres, valeurs par défaut si non configuré
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                cs.*,
                ma.name as member_a_name,
                mb.name as member_b_name,
                mc.name as current_user_name
            FROM couple_settings cs
            LEFT JOIN members ma ON cs.member_a_id = ma.id
            LEFT JOIN members mb ON cs.member_b_id = mb.id
            LEFT JOIN members mc ON cs.current_user_id = mc.id
        """)
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            settings = dict(zip(columns, row))
            # Parser le JSON
            try:
                settings["joint_account_labels"] = json.loads(
                    settings.get("joint_account_labels", "[]")
                )
            except (json.JSONDecodeError, TypeError):
                settings["joint_account_labels"] = []
            return settings

        # Créer la ligne par défaut
        cursor.execute("INSERT INTO couple_settings (id) VALUES (1)")
        conn.commit()
        return get_couple_settings()


def save_couple_settings(
    member_a_id: Optional[int] = None,
    member_b_id: Optional[int] = None,
    current_user_id: Optional[int] = None,
    joint_account_labels: Optional[list] = None,
    show_partner_details: Optional[bool] = None,
    transfer_detection_days: Optional[int] = None,
) -> bool:
    """Met à jour les paramètres couple.

    Args:
        member_a_id: ID du membre A
        member_b_id: ID du membre B
        current_user_id: ID de l'utilisateur actuel
        joint_account_labels: Liste des libellés de comptes joints
        show_partner_details: Pour debug, permet de voir les détails du partenaire
        transfer_detection_days: Fenêtre de détection des virements (jours)

    Returns:
        True si succès
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Construire la requête dynamiquement
            updates = []
            params = []

            if member_a_id is not None:
                updates.append("member_a_id = ?")
                params.append(member_a_id)
            if member_b_id is not None:
                updates.append("member_b_id = ?")
                params.append(member_b_id)
            if current_user_id is not None:
                updates.append("current_user_id = ?")
                params.append(current_user_id)
            if joint_account_labels is not None:
                updates.append("joint_account_labels = ?")
                params.append(json.dumps(joint_account_labels))
            if show_partner_details is not None:
                updates.append("show_partner_details = ?")
                params.append(1 if show_partner_details else 0)
            if transfer_detection_days is not None:
                updates.append("transfer_detection_days = ?")
                params.append(transfer_detection_days)

            if updates:
                query = f"UPDATE couple_settings SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = 1"
                cursor.execute(query, params)
                conn.commit()
            return True
    except Exception as e:
        from modules.logger import logger

        logger.error(f"Erreur sauvegarde paramètres couple: {e}")
        return False


def set_current_user(member_id: int) -> bool:
    """Définit l'utilisateur actuellement connecté.

    Args:
        member_id: ID du membre

    Returns:
        True si succès
    """
    return save_couple_settings(current_user_id=member_id)


def get_current_user_role() -> str:
    """Détermine le rôle de l'utilisateur actuel.

    Returns:
        'A', 'B', ou 'UNKNOWN'
    """
    settings = get_couple_settings()
    current_id = settings.get("current_user_id")

    if current_id is None:
        return "UNKNOWN"
    if current_id == settings.get("member_a_id"):
        return "A"
    if current_id == settings.get("member_b_id"):
        return "B"
    return "UNKNOWN"


def is_couple_configured() -> bool:
    """Vérifie si la configuration couple est complète.

    Returns:
        True si les deux membres sont définis et l'utilisateur actuel est défini
    """
    settings = get_couple_settings()
    return (
        settings.get("member_a_id") is not None
        and settings.get("member_b_id") is not None
        and settings.get("current_user_id") is not None
    )


def get_partner_id() -> Optional[int]:
    """Récupère l'ID du partenaire de l'utilisateur actuel.

    Returns:
        ID du membre partenaire ou None
    """
    settings = get_couple_settings()
    current_id = settings.get("current_user_id")

    if current_id == settings.get("member_a_id"):
        return settings.get("member_b_id")
    if current_id == settings.get("member_b_id"):
        return settings.get("member_a_id")
    return None


def get_setup_progress() -> dict:
    """Calcule la progression de la configuration couple.

    Returns:
        Dict avec étapes et pourcentage
    """
    settings = get_couple_settings()
    from modules.couple.card_mappings import get_cards_summary

    steps = {
        "members_defined": {
            "done": settings.get("member_a_id") is not None
            and settings.get("member_b_id") is not None,
            "label": "Membres définis",
        },
        "current_user_set": {
            "done": settings.get("current_user_id") is not None,
            "label": "Utilisateur actuel défini",
        },
        "cards_mapped": {
            "done": False,
            "label": "Cartes configurées",
        },
        "joint_accounts": {
            "done": len(settings.get("joint_account_labels", [])) > 0,
            "label": "Comptes joints identifiés",
        },
    }

    # Vérifier si au moins une carte est mappée
    card_summary = get_cards_summary()
    steps["cards_mapped"]["done"] = (
        card_summary.get("PERSONAL_A", {}).get("count", 0) > 0
        or card_summary.get("PERSONAL_B", {}).get("count", 0) > 0
        or card_summary.get("JOINT", {}).get("count", 0) > 0
    )

    completed = sum(1 for s in steps.values() if s["done"])
    total = len(steps)

    return {
        "steps": steps,
        "completed": completed,
        "total": total,
        "percentage": int((completed / total) * 100),
        "is_complete": completed == total,
    }
