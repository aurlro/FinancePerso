import pandas as pd
import streamlit as st

from modules.transaction_types import (
    calculate_savings_rate,
    calculate_true_expenses,
    calculate_true_income,
    filter_excluded_transactions,
)

# Import conditionnel pour éviter les dépendances circulaires
try:
    from modules.ui import card_kpi as _external_card_kpi
except ImportError:
    _external_card_kpi = None


def _ensure_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """S'assure que la colonne date_dt existe (idempotent)."""
    if "date_dt" not in df.columns and "date" in df.columns:
        df = df.copy()
        df["date_dt"] = pd.to_datetime(df["date"])
    return df


def calculate_reste_a_vivre(df: pd.DataFrame) -> float:
    """
    Calcule le reste à vivre: argent disponible (revenus - dépenses).
    
    C'est l'argent réellement disponible après toutes les dépenses.
    Équivalent au solde (Revenus - Dépenses totales).
    
    Args:
        df: DataFrame avec transactions
        
    Returns:
        Montant du reste à vivre en euros
    """
    if df.empty:
        return 0.0
    
    revenus = calculate_true_income(df, include_refunds=False)
    depenses = calculate_true_expenses(df, include_refunds=True)
    
    return revenus - depenses


def calculate_savings_amount(df: pd.DataFrame) -> float:
    """
    Calcule le montant épargné (revenus - dépenses).
    
    Args:
        df: DataFrame avec transactions
        
    Returns:
        Montant épargné en euros (peut être négatif si déficit)
    """
    return calculate_reste_a_vivre(df)


def calculate_trends(df_current: pd.DataFrame, df_prev: pd.DataFrame) -> dict:
    """
    Calculate KPI trends between current and previous periods.
    Utilise les catégories pour déterminer revenus vs dépenses (pas le signe du montant).

    Args:
        df_current: Current period transactions
        df_prev: Previous period transactions

    Returns:
        Dict with trend data for each KPI
    """
    # Exclure les virements internes pour les calculs
    df_current_clean = filter_excluded_transactions(df_current)
    df_prev_clean = filter_excluded_transactions(df_prev) if not df_prev.empty else df_prev

    # Current Stats - utilisation des catégories, pas du signe
    cur_exp = calculate_true_expenses(df_current_clean, include_refunds=True)
    cur_rev = calculate_true_income(df_current_clean, include_refunds=False)
    cur_solde = cur_rev - cur_exp
    cur_saving_rate = calculate_savings_rate(df_current_clean)
    cur_reste_a_vivre = calculate_reste_a_vivre(df_current_clean)
    cur_savings_amount = calculate_savings_amount(df_current_clean)

    # Previous Stats for Trends
    if not df_prev_clean.empty:
        prev_exp = calculate_true_expenses(df_prev_clean, include_refunds=True)
        prev_rev = calculate_true_income(df_prev_clean, include_refunds=False)
        prev_solde = prev_rev - prev_exp
        prev_reste_a_vivre = calculate_reste_a_vivre(df_prev_clean)
        prev_savings_amount = calculate_savings_amount(df_prev_clean)

        def get_trend(cur, prev, inverse=False):
            if prev == 0:
                return ("-", "positive", 0.0)
            diff = ((cur - prev) / abs(prev)) * 100
            # Pour le reste à vivre et épargne, positif = bien (vert)
            # Pour les dépenses, négatif = bien (vert)
            is_positive = (diff > 0) if not inverse else (diff < 0)
            color = "positive" if is_positive else "negative"
            return (f"{diff:+.1f}%", color, diff)

        exp_trend, exp_color, _ = get_trend(cur_exp, prev_exp, inverse=True)
        rev_trend, rev_color, _ = get_trend(cur_rev, prev_rev, inverse=False)
        solde_trend, solde_color, _ = get_trend(cur_solde, prev_solde, inverse=False)
        reste_trend, reste_color, reste_diff = get_trend(cur_reste_a_vivre, prev_reste_a_vivre, inverse=False)
        
        # Pour l'épargne: détecter si premier versement (passage de <=0 à >0)
        if prev_savings_amount <= 0 and cur_savings_amount > 0:
            savings_trend = "🎉 Premier versement !"
            savings_color = "positive"
        elif prev_savings_amount == 0 and cur_savings_amount == 0:
            savings_trend = "-"
            savings_color = "neutral"
        else:
            savings_diff = ((cur_savings_amount - prev_savings_amount) / abs(prev_savings_amount)) * 100
            savings_color = "positive" if savings_diff > 0 else "negative"
            savings_trend = f"{savings_diff:+.1f}%"
    else:
        exp_trend, exp_color = ("-", "positive")
        rev_trend, rev_color = ("-", "positive")
        solde_trend, solde_color = ("-", "positive")
        reste_trend, reste_color = ("-", "positive")
        savings_trend, savings_color = ("-", "positive")

    return {
        "expenses": {"value": cur_exp, "trend": exp_trend, "color": exp_color},
        "revenue": {"value": cur_rev, "trend": rev_trend, "color": rev_color},
        "balance": {"value": cur_solde, "trend": solde_trend, "color": solde_color},
        "reste_a_vivre": {
            "value": cur_reste_a_vivre,
            "trend": reste_trend,
            "color": reste_color,
        },
        "savings_rate": {
            "value": cur_saving_rate,
            "trend": "Taux",
            "color": "positive" if cur_saving_rate > 10 else "neutral" if cur_saving_rate > 0 else "negative",
        },
        "savings_amount": {
            "value": cur_savings_amount,
            "trend": savings_trend,
            "color": savings_color,
        },
    }


def compute_previous_period(
    df: pd.DataFrame, df_current: pd.DataFrame, show_internal: bool, show_hors_budget: bool
) -> pd.DataFrame:
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
    min_date = df_current["date_dt"].min()
    max_date = df_current["date_dt"].max()
    duration = max_date - min_date

    # Approximate duration if only one day or one month
    if duration.days < 20:  # Likely just one month selected
        prev_start = min_date - pd.DateOffset(months=1)
        prev_end = min_date - pd.Timedelta(days=1)
    else:
        prev_start = min_date - (duration + pd.Timedelta(days=1))
        prev_end = min_date - pd.Timedelta(days=1)

    # df a déjà date_dt depuis la page principale
    df_prev = df[(df["date_dt"] >= prev_start) & (df["date_dt"] <= prev_end)].copy()

    # Apply the same exclusions to prev period
    if not show_internal:
        df_prev = df_prev[df_prev["category_validated"] != "Virement Interne"]
    if not show_hors_budget:
        df_prev = df_prev[df_prev["category_validated"] != "Hors Budget"]

    return df_prev


def _render_kpi_card_html(title: str, value: str, icon: str, trend: str = None, 
                          trend_color: str = "positive", subtitle: str = "Ce mois-ci"):
    """
    Rend une carte KPI avec HTML/CSS personnalisé (style FinCouple).
    
    Args:
        title: Titre de la métrique
        value: Valeur à afficher
        icon: Icône emoji
        trend: Tendance optionnelle (ex: "+12%" ou "🎉 Premier versement !")
        trend_color: "positive" (vert), "negative" (rouge) ou "neutral" (gris)
        subtitle: Sous-titre (défaut: "Ce mois-ci")
    """
    # Définir les couleurs selon le trend_color
    color_map = {
        "positive": "#10B981",  # Vert
        "negative": "#EF4444",  # Rouge
        "neutral": "#6B7280",   # Gris
    }
    trend_color_hex = color_map.get(trend_color, "#6B7280")
    
    # Flèche pour la tendance
    arrow = ""
    if trend and trend != "-":
        if "Premier" in trend or "🎉" in trend:
            arrow = ""
        elif trend_color == "positive":
            arrow = "↑ "
        elif trend_color == "negative":
            arrow = "↓ "
        else:
            arrow = "→ "
    
    trend_html = ""
    if trend and trend != "-":
        trend_html = f'''
        <div style="
            font-size: 0.875rem;
            font-weight: 500;
            color: {trend_color_hex};
            margin-top: 0.25rem;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        ">
            {arrow}{trend}
        </div>
        '''
    
    html = f'''
    <div style="
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.25rem;
        height: 100%;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    " onmouseover="this.style.boxShadow='0 4px 6px -1px rgba(0, 0, 0, 0.1)'" 
       onmouseout="this.style.boxShadow='0 1px 3px 0 rgba(0, 0, 0, 0.1)'">
        <div style="
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            font-weight: 500;
            color: #374151;
            margin-bottom: 0.75rem;
        ">
            <span style="font-size: 1.125rem;">{icon}</span>
            <span>{title}</span>
        </div>
        <div style="
            font-size: 1.75rem;
            font-weight: 700;
            color: #111827;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.2;
        ">
            {value}
        </div>
        {trend_html}
        <div style="
            font-size: 0.75rem;
            color: #9CA3AF;
            margin-top: 0.5rem;
        ">
            {subtitle}
        </div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)


def render_kpi_cards(df_current: pd.DataFrame, df_prev: pd.DataFrame = None):
    """
    Render 4 KPI cards with trend indicators in a 2x2 grid layout.
    
    Layout:
    ┌───────────────────┐  ┌───────────────────┐
    │ 💚 Reste à vivre  │  │ 💳 Dépenses       │
    │                   │  │                   │
    │ 1 847.52 €        │  │ -2 152.48 €       │
    │ ↑ 13.8% vs janv.  │  │ ↓ 9.4% vs janv.   │
    │ Ce mois-ci        │  │ Ce mois-ci        │
    └───────────────────┘  └───────────────────┘
    ┌───────────────────┐  ┌───────────────────┐
    │ 💶 Revenus        │  │ 🎯 Épargne        │
    │                   │  │                   │
    │ 4 200.00 €        │  │ 200.00 €          │
    │ ↑ 5.0% vs janv.   │  │ 🎉 1er versement! │
    │ Ce mois-ci        │  │ Ce mois-ci        │
    └───────────────────┘  └───────────────────┘

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

    # Layout 2x2 grid
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    # Ligne 1: Reste à vivre (le plus important) + Dépenses
    with row1_col1:
        _render_kpi_card_html(
            title="Reste à vivre",
            value=f"{trends['reste_a_vivre']['value']:,.2f} €".replace(",", " "),
            icon="💚",
            trend=trends["reste_a_vivre"]["trend"],
            trend_color=trends["reste_a_vivre"]["color"],
            subtitle="Ce mois-ci"
        )

    with row1_col2:
        _render_kpi_card_html(
            title="Dépenses",
            value=f"{trends['expenses']['value']:,.2f} €".replace(",", " "),
            icon="💳",
            trend=trends["expenses"]["trend"],
            trend_color=trends["expenses"]["color"],
            subtitle="Ce mois-ci"
        )

    # Ligne 2: Revenus + Épargne (montant, pas %)
    with row2_col1:
        _render_kpi_card_html(
            title="Revenus",
            value=f"{trends['revenue']['value']:,.2f} €".replace(",", " "),
            icon="💶",
            trend=trends["revenue"]["trend"],
            trend_color=trends["revenue"]["color"],
            subtitle="Ce mois-ci"
        )

    with row2_col2:
        _render_kpi_card_html(
            title="Épargne",
            value=f"{trends['savings_amount']['value']:,.2f} €".replace(",", " "),
            icon="🎯",
            trend=trends["savings_amount"]["trend"],
            trend_color=trends["savings_amount"]["color"],
            subtitle="Ce mois-ci"
        )


# Alias pour compatibilité avec l'ancien code qui pourrait importer card_kpi
# Le vrai card_kpi est dans modules.ui.design_system
def card_kpi(title, value, trend=None, trend_color="positive"):
    """
    Rend une carte KPI (wrapper vers le design system).
    
    Cette fonction est conservée pour compatibilité.
    Utilise _render_kpi_card_html en interne.
    """
    # Déterminer une icône par défaut selon le titre
    icon_map = {
        "Dépenses": "💳",
        "Revenus": "💶",
        "Solde": "💰",
        "Épargne": "🎯",
        "Reste à vivre": "💚",
    }
    icon = icon_map.get(title, "📊")
    
    _render_kpi_card_html(
        title=title,
        value=value,
        icon=icon,
        trend=trend,
        trend_color=trend_color,
        subtitle="Ce mois-ci"
    )
