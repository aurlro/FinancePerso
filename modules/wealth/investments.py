# -*- coding: utf-8 -*-
"""
Suivi des investissements.
"""

from datetime import date
from typing import Any

from modules.db.connection import get_db_connection


def calculate_roi(
    initial_value: float,
    current_value: float,
    dividends: float = 0,
) -> dict[str, float]:
    """
    Calcule le ROI (Return on Investment).
    
    Args:
        initial_value: Valeur initiale
        current_value: Valeur actuelle
        dividends: Dividendes perçus
    
    Returns:
        Dict avec percentage et absolute
    """
    if initial_value == 0:
        return {"percentage": 0, "absolute": 0}
    
    total_return = current_value + dividends - initial_value
    percentage = (total_return / initial_value) * 100
    
    return {
        "percentage": round(percentage, 2),
        "absolute": round(total_return, 2),
    }


def calculate_annualized_return(
    initial_value: float,
    final_value: float,
    years: float,
) -> float:
    """
    Calcule le rendement annualisé (CAGR).
    
    Args:
        initial_value: Valeur initiale
        final_value: Valeur finale
        years: Nombre d'années
    
    Returns:
        Rendement annualisé (ex: 0.10 pour 10%)
    """
    if initial_value <= 0 or years <= 0:
        return 0
    
    cagr = (final_value / initial_value) ** (1 / years) - 1
    return round(cagr, 4)


def add_dividend(
    asset_id: int,
    amount: float,
    date_received: date,
    source: str = "",
) -> int:
    """
    Ajoute un dividende.
    
    Args:
        asset_id: ID de l'actif
        amount: Montant
        date_received: Date de réception
        source: Source du dividende
    
    Returns:
        ID du dividende
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO dividends (asset_id, amount, date_received, source)
            VALUES (?, ?, ?, ?)
        """,
            (asset_id, amount, date_received, source),
        )
        conn.commit()
        return cursor.lastrowid


def get_dividend_history() -> list[dict[str, Any]]:
    """
    Récupère l'historique des dividendes.
    
    Returns:
        Liste des dividendes
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM dividends ORDER BY date_received DESC"
        )
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def calculate_dividend_yield(
    annual_dividends: float,
    investment_value: float,
) -> float:
    """
    Calcule le rendement du dividende.
    
    Args:
        annual_dividends: Dividendes annuels
        investment_value: Valeur de l'investissement
    
    Returns:
        Rendement (ex: 0.035 pour 3.5%)
    """
    if investment_value == 0:
        return 0
    return annual_dividends / investment_value
