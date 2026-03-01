"""Filtres de confidentialité pour la Couple Edition.

Implémente les règles de visibilité entre partenaires.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd

from modules.couple.couple_settings import get_couple_settings, get_current_user_role
from modules.couple.card_mappings import get_card_mapping
from modules.db.connection import get_db_connection


# Règles de confidentialité par rôle
COUPLE_PRIVACY_RULES = {
    'ME': {
        'can_see_details': True,
        'can_see_transactions': True,
        'can_see_categories': True,
        'can_see_trends': True,
        'can_see_labels': True,
        'can_see_amounts': True,
    },
    'PARTNER': {
        'can_see_details': False,
        'can_see_transactions': False,
        'can_see_categories': True,
        'can_see_trends': True,
        'can_see_labels': False,  # 🔒 Pas les libellés individuels
        'can_see_amounts': True,  # ✅ Mais les montants agrégés
    },
    'JOINT': {
        'can_see_details': True,
        'can_see_transactions': True,
        'can_see_categories': True,
        'can_see_trends': True,
        'can_see_labels': True,
        'can_see_amounts': True,
    },
    'UNKNOWN': {
        'can_see_details': False,
        'can_see_transactions': False,
        'can_see_categories': True,
        'can_see_trends': False,
        'can_see_labels': False,
        'can_see_amounts': True,
    }
}


def get_transaction_visibility_role(
    transaction,
    current_user_id: Optional[int] = None,
) -> str:
    """Détermine le rôle de visibilité pour une transaction.
    
    Args:
        transaction: Transaction (dict ou Series)
        current_user_id: ID de l'utilisateur actuel (auto-détecté si None)
        
    Returns:
        'ME', 'PARTNER', 'JOINT', ou 'UNKNOWN'
    """
    if current_user_id is None:
        settings = get_couple_settings()
        current_user_id = settings.get('current_user_id')
    
    if current_user_id is None:
        return 'UNKNOWN'
    
    # Récupérer le suffixe de carte
    card_suffix = None
    if isinstance(transaction, dict):
        card_suffix = transaction.get('card_suffix')
    elif isinstance(transaction, pd.Series):
        card_suffix = transaction.get('card_suffix')
    
    if card_suffix:
        mapping = get_card_mapping(str(card_suffix))
        if mapping:
            member_id = mapping.get('member_id')
            account_type = mapping.get('account_type')
            
            if member_id == current_user_id:
                return 'ME'
            elif member_id is not None:
                return 'PARTNER'
            elif account_type == 'JOINT':
                return 'JOINT'
    
    # Fallback sur le libellé du compte
    account_label = ""
    if isinstance(transaction, dict):
        account_label = transaction.get('account_label', '')
    elif isinstance(transaction, pd.Series):
        account_label = transaction.get('account_label', '')
    
    settings = get_couple_settings()
    joint_labels = settings.get('joint_account_labels', [])
    if any(label.upper() in account_label.upper() for label in joint_labels):
        return 'JOINT'
    
    return 'UNKNOWN'


def get_transactions_with_privacy(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    exclude_transfers: bool = True,
) -> dict[str, pd.DataFrame]:
    """Récupère les transactions filtrées par confidentialité.
    
    Args:
        start_date: Date de début
        end_date: Date de fin
        exclude_transfers: Si True, exclut les virements internes
        
    Returns:
        Dict avec 'me', 'partner', 'joint', 'unknown'
    """
    from modules.db.transactions import get_all_transactions
    from modules.couple.transfer_detector import exclude_transfers_from_stats
    
    # Récupérer toutes les transactions
    df = get_all_transactions()
    if df.empty:
        return {'me': df, 'partner': df, 'joint': df, 'unknown': df}
    
    # Filtrer par date si spécifié
    if start_date:
        df = df[df['date'] >= start_date]
    if end_date:
        df = df[df['date'] <= end_date]
    
    # Exclure les virements si demandé
    if exclude_transfers:
        df = exclude_transfers_from_stats(df, start_date, end_date)
    
    # Ajouter la colonne de visibilité
    df['visibility_role'] = df.apply(get_transaction_visibility_role, axis=1)
    
    # Séparer par rôle
    return {
        'me': df[df['visibility_role'] == 'ME'],
        'partner': df[df['visibility_role'] == 'PARTNER'],
        'joint': df[df['visibility_role'] == 'JOINT'],
        'unknown': df[df['visibility_role'] == 'UNKNOWN'],
    }


def get_aggregated_partner_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    group_by: str = 'category',
) -> pd.DataFrame:
    """Récupère les données agrégées du partenaire (vue confidentielle).
    
    Args:
        start_date: Date de début
        end_date: Date de fin
        group_by: Colonne de regroupement ('category', 'month', etc.)
        
    Returns:
        DataFrame avec données agrégées (pas de détails)
    """
    data = get_transactions_with_privacy(start_date, end_date)
    partner_df = data.get('partner', pd.DataFrame())
    
    if partner_df.empty:
        return pd.DataFrame()
    
    # Agréger par catégorie
    if group_by == 'category':
        agg = partner_df.groupby('category').agg({
            'amount': ['count', 'sum'],
        }).reset_index()
        agg.columns = ['category', 'transaction_count', 'total_amount']
        return agg.sort_values('total_amount', ascending=False)
    
    # Agréger par mois
    if group_by == 'month':
        partner_df['month'] = pd.to_datetime(partner_df['date']).dt.to_period('M')
        agg = partner_df.groupby('month').agg({
            'amount': ['count', 'sum'],
        }).reset_index()
        agg.columns = ['month', 'transaction_count', 'total_amount']
        return agg.sort_values('month')
    
    return partner_df


def get_personal_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """Calcule le résumé personnel avec distinction Me/Partner/Joint.
    
    Args:
        start_date: Date de début
        end_date: Date de fin
        
    Returns:
        Dict avec métriques pour chaque rôle
    """
    data = get_transactions_with_privacy(start_date, end_date)
    
    def calc_metrics(df: pd.DataFrame) -> dict:
        if df.empty:
            return {
                'transaction_count': 0,
                'total_income': 0.0,
                'total_expenses': 0.0,
                'net': 0.0,
            }
        
        income = df[df['amount'] > 0]['amount'].sum()
        expenses = df[df['amount'] < 0]['amount'].sum()
        
        return {
            'transaction_count': len(df),
            'total_income': income,
            'total_expenses': expenses,
            'net': income + expenses,
        }
    
    return {
        'me': calc_metrics(data['me']),
        'partner': calc_metrics(data['partner']),
        'joint': calc_metrics(data['joint']),
        'unknown': calc_metrics(data['unknown']),
        'total': calc_metrics(pd.concat([data['me'], data['partner'], data['joint']])),
    }


def get_couple_dashboard_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """Récupère toutes les données nécessaires au dashboard couple.
    
    Args:
        start_date: Date de début
        end_date: Date de fin
        
    Returns:
        Dict structuré pour le dashboard
    """
    summary = get_personal_summary(start_date, end_date)
    partner_by_category = get_aggregated_partner_data(start_date, end_date, 'category')
    
    # Récupérer mes transactions détaillées
    data = get_transactions_with_privacy(start_date, end_date)
    my_transactions = data['me']
    
    # Calculer mes catégories
    my_by_category = pd.DataFrame()
    if not my_transactions.empty:
        my_by_category = my_transactions.groupby('category').agg({
            'amount': ['count', 'sum'],
        }).reset_index()
        my_by_category.columns = ['category', 'transaction_count', 'total_amount']
        my_by_category = my_by_category.sort_values('total_amount', ascending=False)
    
    # Récupérer les virements
    from modules.couple.transfer_detector import get_transfer_summary
    transfers = get_transfer_summary(start_date, end_date)
    
    return {
        'summary': summary,
        'my_categories': my_by_category,
        'partner_categories': partner_by_category,
        'joint_transactions': data['joint'],
        'pending_transfers': transfers['pending_count'],
        'validated_transfers_amount': transfers['total_validated_amount'],
    }


def can_see_partner_details() -> bool:
    """Vérifie si l'utilisateur peut voir les détails du partenaire.
    
    Returns:
        True si le mode debug est activé ou si les règles le permettent
    """
    settings = get_couple_settings()
    return settings.get('show_partner_details', False)


def anonymize_partner_data(df: pd.DataFrame) -> pd.DataFrame:
    """Anonymise les données du partenaire pour affichage.
    
    Remplace les libellés sensibles par des placeholders.
    
    Args:
        df: DataFrame avec données du partenaire
        
    Returns:
        DataFrame anonymisé
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # Anonymiser les libellés
    if 'label' in df.columns:
        df['label'] = df.apply(
            lambda row: f"Transaction {row.name + 1}" if pd.notna(row.get('category')) else "Anonyme",
            axis=1
        )
    
    # Masquer le bénéficiaire
    if 'beneficiary' in df.columns:
        df['beneficiary'] = "🔒 Confidentiel"
    
    # Garder uniquement les colonnes non sensibles
    safe_columns = ['amount', 'category', 'date', 'month', 'visibility_role']
    available_cols = [c for c in safe_columns if c in df.columns]
    
    return df[available_cols]
