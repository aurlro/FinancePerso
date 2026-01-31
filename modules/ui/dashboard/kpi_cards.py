import streamlit as st
import pandas as pd
from modules.ui import card_kpi


def _ensure_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """S'assure que la colonne date_dt existe (idempotent)."""
    if 'date_dt' not in df.columns and 'date' in df.columns:
        df = df.copy()
        df['date_dt'] = pd.to_datetime(df['date'])
    return df

def calculate_trends(df_current: pd.DataFrame, df_prev: pd.DataFrame) -> dict:
    """
    Calculate KPI trends between current and previous periods.
    
    Args:
        df_current: Current period transactions
        df_prev: Previous period transactions
        
    Returns:
        Dict with trend data for each KPI
    """
    # Current Stats
    cur_exp = abs(df_current[df_current['amount'] < 0]['amount'].sum())
    cur_rev = df_current[df_current['amount'] > 0]['amount'].sum()
    cur_solde = cur_rev - cur_exp
    cur_saving_rate = (cur_solde / cur_rev * 100) if cur_rev > 0 else 0
    
    # Previous Stats for Trends
    if not df_prev.empty:
        prev_exp = abs(df_prev[df_prev['amount'] < 0]['amount'].sum())
        prev_rev = df_prev[df_prev['amount'] > 0]['amount'].sum()
        prev_solde = prev_rev - prev_exp
        
        def get_trend(cur, prev, inverse=False):
            if prev == 0: return ("-", "positive")
            diff = ((cur - prev) / prev) * 100
            color = "positive" if (diff > 0 if not inverse else diff < 0) else "negative"
            return (f"{diff:+.1f}%", color)

        exp_trend, exp_color = get_trend(cur_exp, prev_exp, inverse=True)
        rev_trend, rev_color = get_trend(cur_rev, prev_rev)
        solde_trend, solde_color = get_trend(cur_solde, prev_solde)
    else:
        exp_trend, exp_color = ("-", "positive")
        rev_trend, rev_color = ("-", "positive")
        solde_trend, solde_color = ("-", "positive")
    
    return {
        'expenses': {
            'value': cur_exp,
            'trend': exp_trend,
            'color': exp_color
        },
        'revenue': {
            'value': cur_rev,
            'trend': rev_trend,
            'color': rev_color
        },
        'balance': {
            'value': cur_solde,
            'trend': solde_trend,
            'color': solde_color
        },
        'savings_rate': {
            'value': cur_saving_rate,
            'trend': "Taux",
            'color': "positive" if cur_saving_rate > 10 else "negative"
        }
    }

def compute_previous_period(df: pd.DataFrame, df_current: pd.DataFrame, 
                           show_internal: bool, show_hors_budget: bool) -> pd.DataFrame:
    """
    Calculate the previous period dataframe for trend comparison.
    
    Args:
        df: Full transaction dataset (avec date_dt déjà converti)
        df_current: Current period filtered transactions (avec date_dt)
        show_internal: Whether to show internal transfers
        show_hors_budget: Whether to show off-budget items
        
    Returns:
        DataFrame of previous period transactions
    """
    if df_current.empty:
        return pd.DataFrame()
    
    # date_dt est déjà présent grâce au cache dans la page principale
    min_date = df_current['date_dt'].min()
    max_date = df_current['date_dt'].max()
    duration = max_date - min_date
    
    # Approximate duration if only one day or one month
    if duration.days < 20:  # Likely just one month selected
        prev_start = min_date - pd.DateOffset(months=1)
        prev_end = min_date - pd.Timedelta(days=1)
    else:
        prev_start = min_date - (duration + pd.Timedelta(days=1))
        prev_end = min_date - pd.Timedelta(days=1)
    
    # df a déjà date_dt depuis la page principale
    df_prev = df[(df['date_dt'] >= prev_start) & (df['date_dt'] <= prev_end)].copy()
    
    # Apply the same exclusions to prev period
    if not show_internal:
        df_prev = df_prev[df_prev['category_validated'] != 'Virement Interne']
    if not show_hors_budget:
        df_prev = df_prev[df_prev['category_validated'] != 'Hors Budget']
    
    return df_prev

def render_kpi_cards(df_current: pd.DataFrame, df_prev: pd.DataFrame = None):
    """
    Render 4 KPI cards with trend indicators.
    
    Args:
        df_current: Current period transactions
        df_prev: Previous period transactions (optional, for trends)
    """
    if df_current.empty:
        st.info("Aucune donnée disponible pour cette période.")
        return
    
    if df_prev is None:
        df_prev = pd.DataFrame()
    
    # Calculate trends
    trends = calculate_trends(df_current, df_prev)
    
    # Render cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        card_kpi(
            "Dépenses", 
            f"{trends['expenses']['value']:,.0f} €", 
            trend=trends['expenses']['trend'], 
            trend_color=trends['expenses']['color']
        )
    
    with col2:
        card_kpi(
            "Revenus", 
            f"{trends['revenue']['value']:,.0f} €", 
            trend=trends['revenue']['trend'], 
            trend_color=trends['revenue']['color']
        )
    
    with col3:
        card_kpi(
            "Solde", 
            f"{trends['balance']['value']:,.0f} €", 
            trend=trends['balance']['trend'], 
            trend_color=trends['balance']['color']
        )
    
    with col4:
        card_kpi(
            "Épargne", 
            f"{trends['savings_rate']['value']:.1f}%", 
            trend=trends['savings_rate']['trend'], 
            trend_color=trends['savings_rate']['color']
        )
