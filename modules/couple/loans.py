"""Gestion des emprunts pour la Couple Edition."""

from __future__ import annotations

import json
from typing import Optional

import pandas as pd

from modules.db.connection import get_db_connection


def get_all_loans(active_only: bool = True) -> list[dict]:
    """Récupère tous les emprunts.
    
    Args:
        active_only: Si True, n'affiche que les emprunts actifs
        
    Returns:
        Liste des emprunts avec infos membres
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT 
                l.*,
                m.name as member_name,
                CASE 
                    WHEN l.total_amount > 0 THEN ROUND((l.paid_capital / l.principal_amount) * 100, 2)
                    ELSE 0 
                END as repayment_progress_pct,
                CASE 
                    WHEN l.remaining_months > 0 THEN l.remaining_months
                    WHEN l.total_duration_months > 0 THEN l.total_duration_months - 
                        (CAST((julianday('now') - julianday(l.start_date)) / 30 AS INTEGER))
                    ELSE 0
                END as calculated_remaining_months
            FROM loans l
            LEFT JOIN members m ON l.member_id = m.id
        """
        if active_only:
            query += " WHERE l.is_active = 1"
        query += " ORDER BY l.created_at DESC"
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_loan(loan_id: int) -> Optional[dict]:
    """Récupère un emprunt par son ID.
    
    Args:
        loan_id: ID de l'emprunt
        
    Returns:
        L'emprunt ou None si non trouvé
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                l.*,
                m.name as member_name,
                CASE 
                    WHEN l.total_amount > 0 THEN ROUND((l.paid_capital / l.principal_amount) * 100, 2)
                    ELSE 0 
                END as repayment_progress_pct
            FROM loans l
            LEFT JOIN members m ON l.member_id = m.id
            WHERE l.id = ?
        """, (loan_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None


def create_loan(
    name: str,
    monthly_payment: float,
    principal_amount: float = 0,
    lender: str = "",
    interest_rate: Optional[float] = None,
    total_duration_months: Optional[int] = None,
    start_date: Optional[str] = None,
    member_id: Optional[int] = None,
    account_type: str = "JOINT",
    notes: str = "",
) -> Optional[int]:
    """Crée un nouvel emprunt.
    
    Args:
        name: Nom de l'emprunt (ex: "Prêt Maison")
        monthly_payment: Mensualité
        principal_amount: Capital emprunté
        lender: Organisme prêteur
        interest_rate: Taux d'intérêt annuel (%)
        total_duration_months: Durée totale en mois
        start_date: Date de début (YYYY-MM-DD)
        member_id: Membre concerné (None = commun)
        account_type: Type de compte (PERSONAL_A, PERSONAL_B, JOINT)
        notes: Notes libres
        
    Returns:
        ID de l'emprunt créé ou None en cas d'erreur
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Calculer le montant total si on a toutes les infos
            total_amount = None
            if principal_amount > 0 and interest_rate and total_duration_months:
                # Calcul simplifié : capital + intérêts (sans tenir compte de l'amortissement exact)
                monthly_rate = interest_rate / 100 / 12
                if monthly_rate > 0:
                    total_amount = monthly_payment * total_duration_months
            
            cursor.execute("""
                INSERT INTO loans (
                    name, lender, principal_amount, total_amount, remaining_capital,
                    paid_capital, paid_interest, interest_rate, monthly_payment,
                    total_duration_months, remaining_months, start_date,
                    member_id, account_type, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                lender,
                principal_amount,
                total_amount,
                principal_amount,  # remaining_capital = principal au début
                0,  # paid_capital
                0,  # paid_interest
                interest_rate,
                monthly_payment,
                total_duration_months,
                total_duration_months,  # remaining_months = total au début
                start_date,
                member_id,
                account_type,
                notes
            ))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        from modules.logger import logger
        logger.error(f"Erreur création emprunt: {e}")
        return None


def update_loan(loan_id: int, **kwargs) -> bool:
    """Met à jour un emprunt.
    
    Args:
        loan_id: ID de l'emprunt
        **kwargs: Champs à mettre à jour
        
    Returns:
        True si succès
    """
    allowed_fields = [
        'name', 'lender', 'principal_amount', 'total_amount', 'remaining_capital',
        'paid_capital', 'paid_interest', 'interest_rate', 'monthly_payment',
        'total_duration_months', 'remaining_months', 'start_date', 'end_date',
        'member_id', 'account_type', 'is_active', 'notes'
    ]
    
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
    
    if not updates:
        return False
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
            query = f"UPDATE loans SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            cursor.execute(query, list(updates.values()) + [loan_id])
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        from modules.logger import logger
        logger.error(f"Erreur mise à jour emprunt {loan_id}: {e}")
        return False


def delete_loan(loan_id: int, soft: bool = True) -> bool:
    """Supprime ou désactive un emprunt.
    
    Args:
        loan_id: ID de l'emprunt
        soft: Si True, désactive seulement (is_active = 0)
        
    Returns:
        True si succès
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if soft:
                cursor.execute("""
                    UPDATE loans SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (loan_id,))
            else:
                cursor.execute("DELETE FROM loans WHERE id = ?", (loan_id,))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        from modules.logger import logger
        logger.error(f"Erreur suppression emprunt {loan_id}: {e}")
        return False


def link_transaction_to_loan(
    loan_id: int,
    transaction_id: int,
    period: Optional[str] = None,
    capital_amount: Optional[float] = None,
    interest_amount: Optional[float] = None,
    insurance_amount: Optional[float] = None,
) -> bool:
    """Lie une transaction à un emprunt.
    
    Args:
        loan_id: ID de l'emprunt
        transaction_id: ID de la transaction
        period: Période concernée (ex: "2024-02")
        capital_amount: Part capital du remboursement
        interest_amount: Part intérêts
        insurance_amount: Part assurance
        
    Returns:
        True si succès
    """
    try:
        breakdown = {}
        if capital_amount is not None:
            breakdown['capital'] = capital_amount
        if interest_amount is not None:
            breakdown['interest'] = interest_amount
        if insurance_amount is not None:
            breakdown['insurance'] = insurance_amount
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO loan_transactions (loan_id, transaction_id, amount_breakdown, period)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(loan_id, transaction_id) DO UPDATE SET
                    amount_breakdown = excluded.amount_breakdown,
                    period = excluded.period
            """, (loan_id, transaction_id, json.dumps(breakdown) if breakdown else None, period))
            conn.commit()
            
            # Mettre à jour les totaux de l'emprunt
            _update_loan_totals(loan_id)
            
            return True
    except Exception as e:
        from modules.logger import logger
        logger.error(f"Erreur liaison transaction {transaction_id} à emprunt {loan_id}: {e}")
        return False


def unlink_transaction_from_loan(loan_id: int, transaction_id: int) -> bool:
    """Supprime le lien entre une transaction et un emprunt.
    
    Args:
        loan_id: ID de l'emprunt
        transaction_id: ID de la transaction
        
    Returns:
        True si succès
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM loan_transactions WHERE loan_id = ? AND transaction_id = ?",
                (loan_id, transaction_id)
            )
            conn.commit()
            
            # Mettre à jour les totaux de l'emprunt
            _update_loan_totals(loan_id)
            
            return cursor.rowcount > 0
    except Exception as e:
        from modules.logger import logger
        logger.error(f"Erreur suppression liaison: {e}")
        return False


def _update_loan_totals(loan_id: int) -> None:
    """Met à jour les totaux d'un emprunt basé sur les transactions liées.
    
    Cette fonction est interne et ne doit pas être appelée directement.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Récupérer toutes les transactions liées
        cursor.execute("""
            SELECT amount_breakdown FROM loan_transactions
            WHERE loan_id = ?
        """, (loan_id,))
        
        total_capital = 0
        total_interest = 0
        total_insurance = 0
        
        for row in cursor.fetchall():
            if row[0]:
                try:
                    breakdown = json.loads(row[0])
                    total_capital += breakdown.get('capital', 0)
                    total_interest += breakdown.get('interest', 0)
                    total_insurance += breakdown.get('insurance', 0)
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # Récupérer le capital initial
        cursor.execute("SELECT principal_amount FROM loans WHERE id = ?", (loan_id,))
        row = cursor.fetchone()
        if row:
            principal_amount = row[0]
            remaining_capital = max(0, principal_amount - total_capital)
            
            # Mettre à jour l'emprunt
            cursor.execute("""
                UPDATE loans 
                SET paid_capital = ?, 
                    paid_interest = ?,
                    remaining_capital = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (total_capital, total_interest, remaining_capital, loan_id))
            conn.commit()


def get_loan_transactions(loan_id: int) -> list[dict]:
    """Récupère les transactions liées à un emprunt.
    
    Args:
        loan_id: ID de l'emprunt
        
    Returns:
        Liste des transactions avec détails
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                lt.*,
                t.date,
                t.label,
                t.amount,
                t.category_validated as category
            FROM loan_transactions lt
            JOIN transactions t ON lt.transaction_id = t.id
            WHERE lt.loan_id = ?
            ORDER BY t.date DESC
        """, (loan_id,))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def detect_loan_payments(loan_id: int, lookback_months: int = 12) -> list[dict]:
    """Détecte automatiquement les paiements potentiels pour un emprunt.
    
    Recherche les transactions avec le même montant que la mensualité.
    
    Args:
        loan_id: ID de l'emprunt
        lookback_months: Nombre de mois à regarder en arrière
        
    Returns:
        Liste des transactions potentielles
    """
    loan = get_loan(loan_id)
    if not loan:
        return []
    
    monthly_payment = loan['monthly_payment']
    lender = loan.get('lender', '')
    
    # Tolérance de 1€ pour les arrondis
    tolerance = 1.0
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Rechercher des transactions avec le bon montant (négatif car débit)
        cursor.execute("""
            SELECT 
                t.id,
                t.date,
                t.label,
                t.amount,
                ABS(t.amount + ?) as diff
            FROM transactions t
            WHERE t.amount < 0
              AND ABS(ABS(t.amount) - ?) < ?
              AND t.date >= date('now', ?)
              AND t.id NOT IN (
                  SELECT transaction_id FROM loan_transactions WHERE loan_id = ?
              )
            ORDER BY t.date DESC
        """, (monthly_payment, monthly_payment, tolerance, f'-{lookback_months} months', loan_id))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_loans_summary() -> dict:
    """Calcule un résumé global de tous les emprunts.
    
    Returns:
        Dict avec statistiques globales
    """
    loans = get_all_loans(active_only=True)
    
    total_principal = sum(l.get('principal_amount', 0) or 0 for l in loans)
    total_remaining = sum(l.get('remaining_capital', 0) or 0 for l in loans)
    total_paid = sum(l.get('paid_capital', 0) or 0 for l in loans)
    total_monthly = sum(l.get('monthly_payment', 0) or 0 for l in loans)
    total_interest_paid = sum(l.get('paid_interest', 0) or 0 for l in loans)
    
    # Progression moyenne
    avg_progress = 0
    if total_principal > 0:
        avg_progress = (total_paid / total_principal) * 100
    
    return {
        'total_loans': len(loans),
        'total_principal': total_principal,
        'total_remaining': total_remaining,
        'total_paid': total_paid,
        'total_monthly': total_monthly,
        'total_interest_paid': total_interest_paid,
        'average_progress': round(avg_progress, 2),
        'by_account_type': {
            'JOINT': sum(1 for l in loans if l.get('account_type') == 'JOINT'),
            'PERSONAL_A': sum(1 for l in loans if l.get('account_type') == 'PERSONAL_A'),
            'PERSONAL_B': sum(1 for l in loans if l.get('account_type') == 'PERSONAL_B'),
        }
    }
