import streamlit as st
import pandas as pd
import datetime
import calendar
from modules.ui import card_kpi
from modules.categorization import generate_financial_report

def render_month_end_forecast(df: pd.DataFrame, selected_years: list, selected_months: list, 
                               fixed_categories: list):
    """
    Render month-end forecasting for current month.
    
    Args:
        df: Full transaction dataset
        selected_years: List of selected years
        selected_months: List of selected month numbers
        fixed_categories: List of fixed expense categories
    """
    st.header("🔮 Prévisions Fin de Mois")
    
    today = datetime.date.today()
    
    if today.year not in selected_years or today.month not in selected_months:
        st.caption(f"Prévisions disponibles pour le mois en cours ({today.strftime('%B %Y')}).")
        return
    
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_passed = today.day
    
    # date_dt est déjà présent depuis la page principale (cache)
    df_month = df[(df['date_dt'].dt.year == today.year) & (df['date_dt'].dt.month == today.month)].copy()
    
    if df_month.empty:
        st.info("Aucune donnée pour le mois en cours pour les prévisions.")
        return
    
    # Prepare expense data
    df_m_exp = df_month[df_month['amount'] < 0].copy()
    df_m_exp['amount'] = df_m_exp['amount'].abs()
    df_m_exp['raw_cat'] = df_m_exp.apply(
        lambda x: x['category_validated'] if x['category_validated'] != 'Inconnu' else (x['original_category'] or "Inconnu"), 
        axis=1
    )
    df_m_exp['type'] = df_m_exp['raw_cat'].apply(lambda x: 'Fixe' if x in fixed_categories else 'Variable')
    
    exp_fixed = df_m_exp[df_m_exp['type'] == 'Fixe']['amount'].sum()
    exp_var = df_m_exp[df_m_exp['type'] == 'Variable']['amount'].sum()
    income = df_month[df_month['amount'] > 0]['amount'].sum()
    
    if days_passed > 0:
        avg_daily_var = exp_var / days_passed
        proj_var = avg_daily_var * days_in_month
        proj_total = exp_fixed + proj_var
        proj_bal = income - proj_total
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            card_kpi(
                "Solde Actuel", 
                f"{income - (exp_fixed+exp_var):+.0f} €", 
                trend=f"Recettes: {income:.0f}€", 
                trend_color="positive"
            )
        with col_f2:
            card_kpi(
                "Dépenses Projetées", 
                f"{proj_total:.0f} €", 
                trend=f"soit {proj_var:.0f}€ var.", 
                trend_color="negative"
            )
        with col_f3:
            card_kpi(
                "Atterrissage Estimé", 
                f"{proj_bal:+.0f} €", 
                trend="Épargne" if proj_bal > 0 else "Déficit", 
                trend_color="positive" if proj_bal > 0 else "negative"
            )
        
        st.info(f"💡 Moyenne de **{avg_daily_var:.0f}€/jour** (variable). Estimation fin de mois : **{proj_bal:+.0f}€**.")
    else:
        st.write("Début de mois, pas assez de données pour projeter.")

def render_ai_financial_report(df_current: pd.DataFrame, df_prev: pd.DataFrame, 
                                df: pd.DataFrame, selected_years: list, selected_months: list):
    """
    Render AI-powered financial report and recommendations.
    
    Args:
        df_current: Current period transactions
        df_prev: Previous period transactions
        df: Full transaction dataset
        selected_years: List of selected years
        selected_months: List of selected month numbers
    """
    st.subheader("🔮 Analyse & Conseils IA")
    
    if df_current.empty:
        st.info("Sélectionnez une période avec des données pour générer un rapport.")
        return
    
    # 1. Current Period Stats (from df_current)
    cur_inc = df_current[df_current['amount'] > 0]['amount'].sum()
    cur_exp_val = abs(df_current[df_current['amount'] < 0]['amount'].sum())
    cur_top_cat = df_current[df_current['amount'] < 0].groupby('category_validated')['amount'].sum().abs().nlargest(3).to_dict()
    
    # 2. Previous Period Stats (from df_prev)
    prev_exp_val = abs(df_prev[df_prev['amount'] < 0]['amount'].sum()) if not df_prev.empty else 0
    
    # 3. YTD context (all data for the latest year in selection)
    latest_year = max(selected_years) if selected_years else datetime.date.today().year
    # date_dt est déjà présent depuis la page principale (cache)
    df_ytd = df[df['date_dt'].dt.year == latest_year]
    ytd_inc = df_ytd[df_ytd['amount'] > 0]['amount'].sum()
    ytd_exp = abs(df_ytd[df_ytd['amount'] < 0]['amount'].sum())
    ytd_sav = ytd_inc - ytd_exp

    stats_payload = {
        "period_label": f"Sélection: {', '.join(map(str, selected_years))} ({len(selected_months)} mois)",
        "current_period": {
            "income": round(cur_inc, 2),
            "expenses": round(cur_exp_val, 2),
            "balance": round(cur_inc - cur_exp_val, 2),
            "top_categories": {k: round(v, 2) for k, v in cur_top_cat.items()}
        },
        "previous_period": {
            "expenses": round(prev_exp_val, 2),
            "evolution_percent": round(((cur_exp_val - prev_exp_val) / prev_exp_val * 100), 1) if prev_exp_val > 0 else 0
        },
        "ytd_context": {
            "year": latest_year,
            "total_income": round(ytd_inc, 2),
            "total_expenses": round(ytd_exp, 2),
            "total_savings": round(ytd_sav, 2),
            "savings_rate_percent": round((ytd_sav / ytd_inc * 100), 1) if ytd_inc > 0 else 0
        }
    }

    if st.button("Générer le rapport & conseils 🪄"):
        with st.spinner("L'IA analyse vos finances sur cette période..."):
            report = generate_financial_report(stats_payload)
            st.markdown(report)
            st.success("Rapport généré avec succès !")
