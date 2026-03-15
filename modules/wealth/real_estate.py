# -*- coding: utf-8 -*-
"""
Suivi immobilier.
"""

from typing import Any

from modules.db.connection import get_db_connection


def add_property(
    name: str,
    address: str,
    purchase_price: float,
    current_value: float,
    mortgage_remaining: float = 0,
) -> int:
    """
    Ajoute un bien immobilier.
    
    Args:
        name: Nom du bien
        address: Adresse
        purchase_price: Prix d'achat
        current_value: Valeur actuelle
        mortgage_remaining: Reste du prêt
    
    Returns:
        ID du bien
    """
    from datetime import date
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO real_estate (name, address, purchase_price, current_value, mortgage_remaining, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (name, address, purchase_price, current_value, mortgage_remaining, date.today()),
        )
        conn.commit()
        return cursor.lastrowid


def get_properties() -> list[dict[str, Any]]:
    """
    Récupère tous les biens immobiliers.
    
    Returns:
        Liste des biens
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM real_estate ORDER BY created_at DESC")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def calculate_equity(current_value: float, mortgage_remaining: float) -> float:
    """
    Calcule la plus-value (equity).
    
    Args:
        current_value: Valeur actuelle
        mortgage_remaining: Reste du prêt
    
    Returns:
        Plus-value
    """
    return current_value - mortgage_remaining


def calculate_rental_yield(
    annual_rent: float,
    property_value: float,
    expenses: float = 0,
) -> float:
    """
    Calcule le rendement locatif.
    
    Args:
        annual_rent: Loyer annuel
        property_value: Valeur du bien
        expenses: Charges annuelles
    
    Returns:
        Rendement (ex: 0.05 pour 5%)
    """
    if property_value == 0:
        return 0
    
    net_rent = annual_rent - expenses
    return net_rent / property_value


def calculate_cap_rate(
    net_operating_income: float,
    property_value: float,
) -> float:
    """
    Calcule le taux de capitalisation (Cap Rate).
    
    Args:
        net_operating_income: Revenu net d'exploitation
        property_value: Valeur du bien
    
    Returns:
        Cap rate
    """
    if property_value == 0:
        return 0
    return net_operating_income / property_value
