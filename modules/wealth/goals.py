# -*- coding: utf-8 -*-
"""
Gestion des objectifs d'épargne.
"""

from datetime import date
from typing import Any

from modules.db.connection import get_db_connection


def create_savings_goal(
    name: str,
    target_amount: float,
    deadline: date | None = None,
    current_amount: float = 0,
    category: str = "Général",
) -> int:
    """
    Crée un objectif d'épargne.
    
    Args:
        name: Nom de l'objectif
        target_amount: Montant cible
        deadline: Date butoir
        current_amount: Montant actuel
        category: Catégorie
    
    Returns:
        ID de l'objectif
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO savings_goals (name, target_amount, current_amount, deadline, category, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (name, target_amount, current_amount, deadline, category, date.today()),
        )
        conn.commit()
        return cursor.lastrowid


def get_savings_goals() -> list[dict[str, Any]]:
    """
    Récupère tous les objectifs.
    
    Returns:
        Liste des objectifs
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM savings_goals ORDER BY created_at DESC")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def calculate_goal_progress(
    target_amount: float,
    current_amount: float,
) -> dict[str, Any]:
    """
    Calcule la progression vers un objectif.
    
    Args:
        target_amount: Montant cible
        current_amount: Montant actuel
    
    Returns:
        Dict avec percentage, remaining, is_achieved
    """
    if target_amount <= 0:
        return {
            "percentage": 0,
            "remaining": 0,
            "is_achieved": False,
        }
    
    percentage = min(100, (current_amount / target_amount) * 100)
    remaining = max(0, target_amount - current_amount)
    is_achieved = current_amount >= target_amount
    
    return {
        "percentage": round(percentage, 2),
        "remaining": round(remaining, 2),
        "is_achieved": is_achieved,
    }


def estimate_completion_date(
    target_amount: float,
    current_amount: float,
    monthly_saving_rate: float,
) -> dict[str, Any]:
    """
    Estime la date de complétion.
    
    Args:
        target_amount: Montant cible
        current_amount: Montant actuel
        monthly_saving_rate: Taux d'épargne mensuel
    
    Returns:
        Dict avec months_remaining et estimated_date
    """
    if monthly_saving_rate <= 0:
        return {
            "months_remaining": -1,
            "estimated_date": None,
        }
    
    remaining = target_amount - current_amount
    if remaining <= 0:
        return {
            "months_remaining": 0,
            "estimated_date": date.today(),
        }
    
    months_remaining = int(remaining / monthly_saving_rate) + 1
    
    # Calculer la date estimée
    estimated_month = date.today().month + months_remaining
    estimated_year = date.today().year + (estimated_month - 1) // 12
    estimated_month = (estimated_month - 1) % 12 + 1
    
    estimated_date = date(estimated_year, estimated_month, 1)
    
    return {
        "months_remaining": months_remaining,
        "estimated_date": estimated_date,
    }


def update_goal_progress(goal_id: int, new_amount: float) -> bool:
    """
    Met à jour la progression d'un objectif.
    
    Args:
        goal_id: ID de l'objectif
        new_amount: Nouveau montant
    
    Returns:
        True si succès
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE savings_goals SET current_amount = ? WHERE id = ?",
            (new_amount, goal_id),
        )
        conn.commit()
        return cursor.rowcount > 0
