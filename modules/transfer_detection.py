"""
Module de détection automatique des transferts et contributions.

Ce module permet d'identifier automatiquement :
1. Les transferts internes (entre comptes A et B)
2. Les contributions partenaires (apports externes, ex: compte C vers B)

La détection se base sur :
- Les patterns configurés dans les settings
- Les règles d'apprentissage existantes
- L'analyse du libellé de la transaction
"""

import pandas as pd
import streamlit as st

from modules.db.connection import get_db_connection
from modules.db.settings import (
    get_internal_transfer_targets,
    get_partner_contribution_patterns,
)
from modules.logger import logger


def detect_transfer_type(label: str | None, account_label: str | None = None) -> str | None:
    """
    Détecte le type de transfert à partir du libellé.
    
    Args:
        label: Libellé de la transaction
        account_label: Compte sur lequel la transaction est enregistrée
        
    Returns:
        'Virement Interne' si transfert entre mes comptes
        'Contribution Partenaire' si apport externe
        None si ce n'est pas un transfert
        
    Examples:
        >>> detect_transfer_type("Virement de AURELIEN")
        'Virement Interne'
        >>> detect_transfer_type("Virement de ELISE")
        'Contribution Partenaire'
        >>> detect_transfer_type("Courses Leclerc")
        None
    """
    if not label:
        return None
    
    label_upper = label.upper()
    
    # Patterns de virements internes (prioritaire)
    internal_patterns = get_internal_transfer_targets()
    
    # Patterns de contributions partenaires
    partner_patterns = get_partner_contribution_patterns()
    
    # Détection des virements internes
    # Un virement interne est identifié si le libellé contient mes propres références
    # mais PAS celles du partenaire
    for pattern in internal_patterns:
        if pattern in label_upper:
            # Vérifier que ce n'est pas un pattern ambigu (présent dans les deux listes)
            if pattern not in partner_patterns:
                logger.debug(f"Détecté comme virement interne: '{label}' (pattern: {pattern})")
                return "Virement Interne"
    
    # Détection des contributions partenaires
    # Une contribution est un virement provenant du partenaire (compte externe)
    for pattern in partner_patterns:
        if pattern in label_upper:
            logger.debug(f"Détecté comme contribution partenaire: '{label}' (pattern: {pattern})")
            return "Contribution Partenaire"
    
    return None


def is_transfer_between_accounts(
    from_account: str, 
    to_account: str, 
    my_accounts: list[str] | None = None
) -> bool:
    """
    Détermine si un transfert est entre mes propres comptes.
    
    Args:
        from_account: Compte émetteur
        to_account: Compte destinataire
        my_accounts: Liste de mes comptes (si None, utilise les patterns configurés)
        
    Returns:
        True si c'est un transfert interne (A ↔ B), False si c'est un apport externe (C → B)
    """
    if my_accounts is None:
        my_accounts = get_internal_transfer_targets()
    
    my_accounts_upper = [acc.upper() for acc in my_accounts]
    from_upper = from_account.upper() if from_account else ""
    to_upper = to_account.upper() if to_account else ""
    
    # Si les deux comptes sont dans ma liste de comptes = transfert interne
    is_from_mine = any(acc in from_upper for acc in my_accounts_upper)
    is_to_mine = any(acc in to_upper for acc in my_accounts_upper)
    
    return is_from_mine and is_to_mine


def auto_categorize_transfers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique la catégorisation automatique des transferts sur un DataFrame.
    
    Cette fonction ajoute/modifie la colonne 'category_validated' pour les
    transactions identifiées comme transferts ou contributions.
    
    Args:
        df: DataFrame avec colonnes 'label' et optionnellement 'account_label'
        
    Returns:
        DataFrame avec catégories mises à jour
        
    Note:
        Ne modifie que les transactions dont la catégorie est 'Inconnu' ou vide
    """
    if df.empty or "label" not in df.columns:
        return df
    
    df = df.copy()
    
    # S'assurer que category_validated existe
    if "category_validated" not in df.columns:
        df["category_validated"] = "Inconnu"
    
    # Masque des transactions à auto-catégoriser (non encore catégorisées)
    mask_to_categorize = (
        df["category_validated"].isna() | 
        (df["category_validated"] == "Inconnu") |
        (df["category_validated"] == "Revenus")  # Permet de corriger les faux revenus
    )
    
    # Appliquer la détection sur chaque ligne éligible
    for idx in df[mask_to_categorize].index:
        label = df.at[idx, "label"]
        account = df.at[idx, "account_label"] if "account_label" in df.columns else None
        
        detected_category = detect_transfer_type(label, account)
        if detected_category:
            df.at[idx, "category_validated"] = detected_category
            logger.debug(f"Auto-catégorisé: '{label}' → {detected_category}")
    
    return df


@st.cache_data(ttl=300)
def get_transfer_summary(month: str | None = None) -> dict:
    """
    Récupère un résumé des transferts pour une période donnée.
    
    Args:
        month: Mois au format 'YYYY-MM' (None = tous les mois)
        
    Returns:
        Dict avec:
            - internal_transfers: liste des virements internes
            - partner_contributions: liste des contributions partenaires
            - total_internal: montant total des transferts internes
            - total_contributions: montant total des contributions
    """
    with get_db_connection() as conn:
        query = """
            SELECT 
                category_validated,
                label,
                amount,
                date,
                account_label
            FROM transactions
            WHERE category_validated IN ('Virement Interne', 'Contribution Partenaire')
        """
        params = []
        
        if month:
            query += " AND strftime('%Y-%m', date) = ?"
            params.append(month)
        
        query += " ORDER BY date DESC"
        
        df = pd.read_sql(query, conn, params=params)
    
    if df.empty:
        return {
            "internal_transfers": pd.DataFrame(),
            "partner_contributions": pd.DataFrame(),
            "total_internal": 0.0,
            "total_contributions": 0.0,
        }
    
    internal_df = df[df["category_validated"] == "Virement Interne"]
    contribution_df = df[df["category_validated"] == "Contribution Partenaire"]
    
    return {
        "internal_transfers": internal_df,
        "partner_contributions": contribution_df,
        "total_internal": internal_df["amount"].sum(),
        "total_contributions": contribution_df["amount"].sum(),
    }


def update_transfer_settings(
    internal_patterns: list[str] | None = None,
    partner_patterns: list[str] | None = None,
) -> None:
    """
    Met à jour les settings de détection des transferts.
    
    Args:
        internal_patterns: Nouveaux patterns pour les virements internes
        partner_patterns: Nouveaux patterns pour les contributions partenaires
    """
    from modules.db.settings import (
        set_internal_transfer_targets,
        set_partner_contribution_patterns,
    )
    
    if internal_patterns is not None:
        set_internal_transfer_targets(internal_patterns)
        logger.info(f"Updated internal transfer patterns: {internal_patterns}")
    
    if partner_patterns is not None:
        set_partner_contribution_patterns(partner_patterns)
        logger.info(f"Updated partner contribution patterns: {partner_patterns}")


def apply_transfer_detection_to_pending() -> int:
    """
    Applique la détection des transferts à toutes les transactions en attente.
    
    Returns:
        Nombre de transactions catégorisées
    """
    from modules.db.transactions import bulk_update_transaction_status, get_pending_transactions
    
    pending_df = get_pending_transactions()
    
    if pending_df.empty:
        return 0
    
    categorized_count = 0
    updates = []
    
    for idx, row in pending_df.iterrows():
        detected = detect_transfer_type(row.get("label"), row.get("account_label"))
        if detected and detected != row.get("category_validated"):
            updates.append((row["id"], detected))
    
    # Appliquer les mises à jour par lot
    if updates:
        for tx_id, new_category in updates:
            bulk_update_transaction_status([tx_id], new_category)
        categorized_count = len(updates)
        logger.info(f"Applied transfer detection to {categorized_count} pending transactions")
    
    return categorized_count
