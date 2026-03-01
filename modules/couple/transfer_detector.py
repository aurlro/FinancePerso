"""Détection et gestion des virements internes entre comptes."""

from __future__ import annotations

from typing import Optional

import pandas as pd

from modules.db.connection import get_db_connection


def detect_internal_transfers(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    threshold_days: int = 3,
    min_amount: float = 10.0,
) -> list[dict]:
    """Détecte les virements internes entre comptes.
    
    Algorithme : même montant (opposé), dates proches, cartes différentes.
    
    Args:
        start_date: Date de début (YYYY-MM-DD), par défaut début du mois
        end_date: Date de fin (YYYY-MM-DD), par défaut aujourd'hui
        threshold_days: Fenêtre de détection en jours
        min_amount: Montant minimum à considérer
        
    Returns:
        Liste des virements détectés
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Dates par défaut
        if not start_date or not end_date:
            cursor.execute("""
                SELECT 
                    date('now', 'start of month') as start_date,
                    date('now') as end_date
            """)
            row = cursor.fetchone()
            start_date = start_date or row[0]
            end_date = end_date or row[1]
        
        # Requête de détection
        cursor.execute("""
            SELECT 
                t1.id as from_id,
                t2.id as to_id,
                t1.amount as from_amount,
                t2.amount as to_amount,
                t1.date as from_date,
                t2.date as to_date,
                t1.card_suffix as from_card,
                t2.card_suffix as to_card,
                t1.label as from_label,
                t2.label as to_label,
                ABS(JULIANDAY(t1.date) - JULIANDAY(t2.date)) as day_diff,
                cm1.account_type as from_account_type,
                cm2.account_type as to_account_type
            FROM transactions t1
            JOIN transactions t2 ON (
                -- Montants opposés (tolérance de 0.01 pour les arrondis)
                ABS(ABS(t1.amount) - ABS(t2.amount)) < 0.01
                -- Un débit, un crédit
                AND t1.amount < 0 
                AND t2.amount > 0
                -- Dates proches
                AND ABS(JULIANDAY(t1.date) - JULIANDAY(t2.date)) <= :threshold
                -- Cartes différentes
                AND t1.card_suffix != t2.card_suffix
            )
            LEFT JOIN card_member_mappings cm1 ON t1.card_suffix = cm1.card_suffix AND cm1.is_active = 1
            LEFT JOIN card_member_mappings cm2 ON t2.card_suffix = cm2.card_suffix AND cm2.is_active = 1
            WHERE t1.date BETWEEN :start AND :end
              AND ABS(t1.amount) >= :min_amount
              AND t1.status = 'validated'
              AND t2.status = 'validated'
              -- Exclure les déjà détectés
              AND t1.id NOT IN (SELECT from_transaction_id FROM detected_transfers)
              AND t2.id NOT IN (SELECT to_transaction_id FROM detected_transfers)
            ORDER BY t1.date DESC, ABS(t1.amount) DESC
        """, {
            'threshold': threshold_days,
            'start': start_date,
            'end': end_date,
            'min_amount': min_amount
        })
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def validate_transfer(from_id: int, to_id: int, is_valid: bool = True, notes: str = "") -> bool:
    """Valide ou invalide un virement détecté.
    
    Args:
        from_id: ID transaction source (débit)
        to_id: ID transaction destination (crédit)
        is_valid: True si c'est bien un virement interne
        notes: Notes optionnelles
        
    Returns:
        True si succès
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO detected_transfers 
                    (from_transaction_id, to_transaction_id, amount, is_validated, notes)
                SELECT 
                    t1.id, t2.id, ABS(t1.amount), ?, ?
                FROM transactions t1
                JOIN transactions t2 ON t2.id = ?
                WHERE t1.id = ?
                ON CONFLICT(from_transaction_id, to_transaction_id) DO UPDATE SET
                    is_validated = excluded.is_validated,
                    notes = excluded.notes,
                    validated_at = CURRENT_TIMESTAMP
            """, (1 if is_valid else 0, notes, to_id, from_id))
            conn.commit()
            return True
    except Exception as e:
        from modules.logger import logger
        logger.error(f"Erreur validation virement: {e}")
        return False


def get_pending_transfers() -> list[dict]:
    """Récupère les virements en attente de validation.
    
    Returns:
        Liste des virements détectés mais non validés
    """
    # D'abord, détecter les nouveaux virements
    detected = detect_internal_transfers()
    
    # Puis récupérer tous les non-validés
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                dt.*,
                t1.label as from_label,
                t2.label as to_label,
                t1.date as from_date,
                t2.date as to_date,
                t1.card_suffix as from_card,
                t2.card_suffix as to_card
            FROM detected_transfers dt
            JOIN transactions t1 ON dt.from_transaction_id = t1.id
            JOIN transactions t2 ON dt.to_transaction_id = t2.id
            WHERE dt.is_validated = 0
            ORDER BY dt.detected_at DESC
        """)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_validated_transfers(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> list[dict]:
    """Récupère les virements validés.
    
    Args:
        start_date: Date de début
        end_date: Date de fin
        
    Returns:
        Liste des virements validés
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        params = []
        date_filter = ""
        if start_date and end_date:
            date_filter = "AND t1.date BETWEEN ? AND ?"
            params = [start_date, end_date]
        
        cursor.execute(f"""
            SELECT 
                dt.*,
                t1.label as from_label,
                t2.label as to_label,
                t1.date as from_date,
                t2.date as to_date,
                t1.card_suffix as from_card,
                t2.card_suffix as to_card
            FROM detected_transfers dt
            JOIN transactions t1 ON dt.from_transaction_id = t1.id
            JOIN transactions t2 ON dt.to_transaction_id = t2.id
            WHERE dt.is_validated = 1
            {date_filter}
            ORDER BY t1.date DESC
        """, params)
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def exclude_transfers_from_stats(
    transactions_df: pd.DataFrame,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """Exclut les transactions de virements internes d'un DataFrame.
    
    Args:
        transactions_df: DataFrame des transactions
        start_date: Date de début pour chercher les virements
        end_date: Date de fin pour chercher les virements
        
    Returns:
        DataFrame sans les transactions de virements
    """
    if transactions_df.empty:
        return transactions_df
    
    # Récupérer les IDs des transactions à exclure
    transfers = get_validated_transfers(start_date, end_date)
    exclude_ids = set()
    for t in transfers:
        exclude_ids.add(t['from_transaction_id'])
        exclude_ids.add(t['to_transaction_id'])
    
    if not exclude_ids:
        return transactions_df
    
    # Filtrer le DataFrame
    return transactions_df[~transactions_df['id'].isin(exclude_ids)]


def get_transfer_summary(start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
    """Calcule un résumé des virements pour la période.
    
    Returns:
        Dict avec stats des virements
    """
    pending = get_pending_transfers()
    validated = get_validated_transfers(start_date, end_date)
    
    total_validated_amount = sum(t['amount'] for t in validated)
    
    return {
        'pending_count': len(pending),
        'validated_count': len(validated),
        'total_validated_amount': total_validated_amount,
        'pending_transfers': pending,
        'validated_transfers': validated,
    }


def auto_detect_and_save_transfers(threshold_days: int = 3) -> int:
    """Détecte automatiquement les virements et les sauvegarde en attente.
    
    Args:
        threshold_days: Fenêtre de détection
        
    Returns:
        Nombre de nouveaux virements détectés
    """
    detected = detect_internal_transfers(threshold_days=threshold_days)
    
    count = 0
    for transfer in detected:
        # Sauvegarder comme non-validé
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO detected_transfers 
                        (from_transaction_id, to_transaction_id, amount, is_validated)
                    VALUES (?, ?, ?, 0)
                """, (
                    transfer['from_id'],
                    transfer['to_id'],
                    abs(transfer['from_amount'])
                ))
                if cursor.rowcount > 0:
                    count += 1
                conn.commit()
        except Exception as e:
            from modules.logger import logger
            logger.error(f"Erreur sauvegarde virement détecté: {e}")
    
    return count
