"""
Module de gestion des filtres pour le tableau de bord Synthèse.
Centralise toute la logique de filtrage pour éviter la duplication.
"""

import streamlit as st
import pandas as pd
import unicodedata
from typing import Dict, List, Tuple, Optional
from functools import lru_cache

from modules.db.members import get_unique_members
from modules.db.tags import get_all_tags


@st.cache_data(ttl=300)
def get_filter_options(df: pd.DataFrame) -> Dict:
    """
    Extraire toutes les options de filtrage disponibles.
    
    Args:
        df: DataFrame des transactions avec date_dt
        
    Returns:
        Dict avec années, mois, comptes, membres, bénéficiaires, tags
    """
    if df.empty:
        return {
            'years': [],
            'months': [],
            'accounts': [],
            'members': [],
            'beneficiaries': [],
            'tags': []
        }
    
    available_years = sorted(df['date_dt'].dt.year.unique().tolist(), reverse=True)
    
    month_names = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                   "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    
    accounts = sorted(df['account_label'].unique().tolist()) if 'account_label' in df.columns else []
    
    return {
        'years': available_years,
        'months': month_names,
        'accounts': accounts,
    }


def normalize_name(name: str) -> str:
    """
    Normaliser un nom pour la comparaison (supprime les accents, minuscules).
    
    Args:
        name: Nom à normaliser
        
    Returns:
        Nom normalisé
    """
    if not name or pd.isna(name):
        return ""
    return "".join(
        c for c in unicodedata.normalize('NFD', str(name))
        if unicodedata.category(c) != 'Mn'
    ).lower()


def consolidate_names(names: pd.Series, official_list: List[str]) -> pd.Series:
    """
    Consolider une série de noms avec la liste officielle.
    
    Args:
        names: Série de noms à consolider
        official_list: Liste des noms officiels
        
    Returns:
        Série avec noms consolidés
    """
    official_norm = {normalize_name(o): o for o in official_list}
    
    def consolidate(n):
        if not n or pd.isna(n):
            return "Inconnu"
        n_norm = normalize_name(n)
        return official_norm.get(n_norm, n)
    
    return names.apply(consolidate)


def render_filter_sidebar(df: pd.DataFrame) -> Dict:
    """
    Rendre le panneau de filtres dans la sidebar.
    Retourne les filtres sélectionnés.
    
    Args:
        df: DataFrame des transactions avec date_dt
        
    Returns:
        Dict avec les filtres sélectionnés
    """
    options = get_filter_options(df)
    
    st.sidebar.subheader("📅 Période")
    
    # Années
    available_years = options['years']
    default_years = [available_years[0]] if available_years else []
    selected_years = st.sidebar.multiselect(
        "Années", 
        available_years, 
        default=default_years,
        key="filter_years"
    )
    
    # Mois
    month_names = options['months']
    month_to_int = {name: i + 1 for i, name in enumerate(month_names)}
    selected_month_names = st.sidebar.multiselect(
        "Mois", 
        month_names, 
        default=month_names,
        key="filter_months"
    )
    selected_months = [month_to_int[m] for m in selected_month_names]
    
    st.sidebar.divider()
    st.sidebar.header("Filtres")
    
    # Filtrage initial par date
    df_filtered = df[
        (df['date_dt'].dt.year.isin(selected_years)) &
        (df['date_dt'].dt.month.isin(selected_months))
    ].copy()
    
    # Filtre Comptes
    selected_accounts = []
    if 'account_label' in df_filtered.columns and not df_filtered.empty:
        accounts = sorted(df_filtered['account_label'].unique().tolist())
        selected_accounts = st.sidebar.multiselect(
            "Comptes", 
            accounts, 
            default=accounts,
            key="filter_accounts"
        )
        if selected_accounts:
            df_filtered = df_filtered[df_filtered['account_label'].isin(selected_accounts)]
    
    # Filtre Membres (avec consolidation)
    selected_members = []
    official_list = get_unique_members()
    
    if 'member' in df_filtered.columns and not df_filtered.empty:
        df_filtered['member_display'] = consolidate_names(df_filtered['member'], official_list)
        members = sorted(df_filtered['member_display'].unique().tolist())
        selected_members = st.sidebar.multiselect(
            "Membres (Carte)", 
            members, 
            default=members,
            key="filter_members"
        )
        if selected_members:
            df_filtered = df_filtered[df_filtered['member_display'].isin(selected_members)]
    
    # Filtre Bénéficiaires
    selected_benefs = []
    if 'beneficiary' in df_filtered.columns and not df_filtered.empty:
        df_filtered['beneficiary_display'] = consolidate_names(df_filtered['beneficiary'], official_list)
        beneficiaries = sorted(df_filtered['beneficiary_display'].unique().tolist())
        selected_benefs = st.sidebar.multiselect(
            "Bénéficiaires", 
            beneficiaries, 
            default=beneficiaries,
            key="filter_beneficiaries"
        )
        if selected_benefs:
            df_filtered = df_filtered[df_filtered['beneficiary_display'].isin(selected_benefs)]
    
    # Filtre Tags
    selected_tags = []
    if 'tags' in df_filtered.columns:
        all_available_tags = get_all_tags()
        if all_available_tags:
            selected_tags = st.sidebar.multiselect(
                "Filtrer par Tags 🏷️", 
                all_available_tags,
                key="filter_tags"
            )
            if selected_tags:
                def match_tags(row_tags):
                    if not row_tags:
                        return False
                    row_tags_list = [t.strip().lower() for t in str(row_tags).split(',')]
                    return any(tag.lower() in row_tags_list for tag in selected_tags)
                df_filtered = df_filtered[df_filtered['tags'].apply(match_tags)]
    
    st.sidebar.divider()
    
    # Options d'affichage
    show_internal = st.sidebar.checkbox(
        "Afficher virements internes 🔄", 
        value=False,
        key="filter_show_internal"
    )
    show_hors_budget = st.sidebar.checkbox(
        "Afficher hors budget 🚫", 
        value=False,
        key="filter_show_hors_budget"
    )
    
    # Exclusions globales
    if not show_internal:
        df_filtered = df_filtered[df_filtered['category_validated'] != 'Virement Interne']
    if not show_hors_budget:
        df_filtered = df_filtered[df_filtered['category_validated'] != 'Hors Budget']
    
    return {
        'df_filtered': df_filtered,
        'selected_years': selected_years,
        'selected_months': selected_months,
        'selected_accounts': selected_accounts,
        'selected_members': selected_members,
        'selected_beneficiaries': selected_benefs,
        'selected_tags': selected_tags,
        'show_internal': show_internal,
        'show_hors_budget': show_hors_budget
    }


def render_filter_info(df_full: pd.DataFrame, filter_result: Dict):
    """
    Affiche un résumé des filtres actifs et des alertes sur les données exclues.
    """
    df_filtered = filter_result['df_filtered']
    years = filter_result['selected_years']
    months = filter_result['selected_months']
    
    if not years:
        return

    # 1. Résumé de la période
    month_names = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    if len(months) == 12:
        period_text = f"Année(s) : {', '.join(map(str, sorted(years)))}"
    else:
        month_text = ", ".join([month_names[m-1] for m in sorted(months)])
        period_text = f"{month_text} {', '.join(map(str, sorted(years)))}"
    
    st.info(f"📅 **Période active** : {period_text}")

    # 2. Alerte sur les grosses transactions exclues (Hors période ou filtres)
    # On cherche des transactions > 500€ qui ne sont pas dans le df filtré
    if not df_full.empty:
        # Transactions importantes (> 500€) non présentes dans le filtre actuel
        # mais présentes dans la base complète
        important_threshold = -500
        
        # On ne compare que par ID pour être sûr
        filtered_ids = set(df_filtered['id'].tolist()) if 'id' in df_filtered.columns else set()
        
        important_excluded = df_full[
            (df_full['amount'] <= important_threshold) & 
            (~df_full['id'].isin(filtered_ids)) &
            (df_full['category_validated'] != 'Virement Interne')
        ].copy()
        
        if not important_excluded.empty:
            count = len(important_excluded)
            latest = important_excluded.sort_values('date', ascending=False).iloc[0]
            
            with st.expander(f"⚠️ **{count} opérations majeures** sont exclues par vos filtres", expanded=False):
                st.warning(f"Dernière exclue : **{latest['label']}** ({latest['amount']}€) le {latest['date']}.")
                st.caption("Ajustez vos filtres (Année, Comptes, Hors Budget) pour les inclure dans vos analyses.")

def compute_previous_period(
    df: pd.DataFrame,
    df_current: pd.DataFrame,
    show_internal: bool,
    show_hors_budget: bool
) -> pd.DataFrame:
    """
    Calculer le DataFrame de la période précédente pour comparaison.
    
    Args:
        df: Dataset complet
        df_current: Période actuelle filtrée
        show_internal: Afficher virements internes
        show_hors_budget: Afficher hors budget
        
    Returns:
        DataFrame de la période précédente
    """
    if df_current.empty:
        return pd.DataFrame()
    
    min_date = df_current['date_dt'].min()
    max_date = df_current['date_dt'].max()
    duration = max_date - min_date
    
    # Approximation si un seul mois sélectionné
    if duration.days < 20:
        prev_start = min_date - pd.DateOffset(months=1)
        prev_end = min_date - pd.Timedelta(days=1)
    else:
        prev_start = min_date - (duration + pd.Timedelta(days=1))
        prev_end = min_date - pd.Timedelta(days=1)
    
    df_prev = df[(df['date_dt'] >= prev_start) & (df['date_dt'] <= prev_end)].copy()
    
    # Appliquer mêmes exclusions
    if not show_internal:
        df_prev = df_prev[df_prev['category_validated'] != 'Virement Interne']
    if not show_hors_budget:
        df_prev = df_prev[df_prev['category_validated'] != 'Hors Budget']
    
    return df_prev
