import streamlit as st
from modules.data_manager import (
    get_all_transactions, init_db, get_budgets,
    get_categories_with_emojis, get_all_tags, get_categories_df,
    get_orphan_labels, get_unique_members
)
from modules.ui import load_css
from modules.analytics import detect_financial_profile
from modules.ui.dashboard.kpi_cards import render_kpi_cards, compute_previous_period
from modules.ui.dashboard.evolution_chart import render_evolution_chart, render_savings_trend_chart
from modules.ui.dashboard.category_charts import (
    render_category_bar_chart, render_monthly_stacked_chart, prepare_expense_dataframe
)
from modules.ui.dashboard.top_expenses import render_top_expenses
from modules.ui.dashboard.budget_tracker import render_budget_tracker
from modules.ui.dashboard.ai_insights import render_month_end_forecast, render_ai_financial_report
import pandas as pd
import plotly.express as px
import unicodedata

st.set_page_config(page_title="Synthèse", page_icon="📊", layout="wide")
load_css()
init_db()

st.title("📊 Tableau de bord")

df = get_all_transactions()

# SMART ONBOARDING NOTIFICATION
if 'onboarding_checked' not in st.session_state:
    st.session_state['onboarding_checked'] = False

if not st.session_state['onboarding_checked'] and not df.empty:
    suggestions = detect_financial_profile(df)
    if suggestions:
        st.session_state['onboarding_suggestions_count'] = len(suggestions)
        st.session_state['onboarding_checked'] = True

if st.session_state.get('onboarding_suggestions_count', 0) > 0:
    with st.expander("🔔 **Configuration Assistée** - Nouvelles suggestions détectées !", expanded=True):
        st.info(f"J'ai détecté **{st.session_state['onboarding_suggestions_count']}** éléments importants à configurer (Salaire, Loyer, Factures...).")
        col_n1, col_n2 = st.columns([1, 1])
        with col_n1:
            if st.button("Configurer maintenant ➡️", type="primary"):
                st.switch_page("pages/5_Assistant.py")
        with col_n2:
            if st.button("Me rappeler plus tard"):
                st.session_state['onboarding_suggestions_count'] = 0
                st.rerun()

# DATA HEALTH DEBT NOTIFICATION
orphans = get_orphan_labels()
if orphans and not df.empty:
    with st.sidebar:
        st.warning(f"🧹 **Nettoyage requis** : {len(orphans)} libellés incohérents détectés (ex: {', '.join(orphans[:2])}).")
        if st.button("Aller au nettoyage 🧼", use_container_width=True):
            st.switch_page("pages/9_Configuration.py")
    st.info(f"💡 Certains membres ou bénéficiaires semblent mal orthographiés (doublons avec/sans accents). [Régler le problème ici](9_Configuration)")

if df.empty:
    st.info("Aucune donnée disponible. Commencez par importer des relevés.")
else:
    # === FILTERS ===
    st.sidebar.subheader("📅 Période")
    
    df['date_dt'] = pd.to_datetime(df['date'])
    available_years = sorted(df['date_dt'].dt.year.unique().tolist(), reverse=True)
    
    selected_years = st.sidebar.multiselect("Années", available_years, default=[available_years[0]] if available_years else [])
    
    month_names = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                   "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    month_to_int = {name: i+1 for i, name in enumerate(month_names)}
    
    selected_month_names = st.sidebar.multiselect("Mois", month_names, default=month_names)
    selected_months = [month_to_int[m] for m in selected_month_names]
    
    st.sidebar.divider()
    st.sidebar.header("Filtres")
    
    # Filter by Year and Month
    df_current = df[
        (df['date_dt'].dt.year.isin(selected_years)) & 
        (df['date_dt'].dt.month.isin(selected_months))
    ].copy()
    
    # Account Filter
    if 'account_label' in df_current.columns:
        accounts = sorted(df_current['account_label'].unique().tolist())
        selected_accounts = st.sidebar.multiselect("Comptes", accounts, default=accounts)
        if selected_accounts:
            df_current = df_current[df_current['account_label'].isin(selected_accounts)]
    
    # Member Filter with consolidation
    official_list = get_unique_members()
    def consolidate_name(n):
        if not n or pd.isna(n): return "Inconnu"
        def norm(s): return "".join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn').lower()
        n_norm = norm(n)
        for official in official_list:
            if norm(official) == n_norm: return official
        return n

    if 'member' in df_current.columns:
        df_current['member_display'] = df_current['member'].apply(consolidate_name)
        members = sorted(df_current['member_display'].unique().tolist())
        selected_members = st.sidebar.multiselect("Membres (Carte)", members, default=members)
        if selected_members:
            df_current = df_current[df_current['member_display'].isin(selected_members)]
    
    # Beneficiary Filter
    if 'beneficiary' in df_current.columns:
        df_current['beneficiary_display'] = df_current['beneficiary'].apply(consolidate_name)
        beneficiaries = sorted(df_current['beneficiary_display'].unique().tolist())
        selected_benefs = st.sidebar.multiselect("Bénéficiaires", beneficiaries, default=beneficiaries)
        if selected_benefs:
            df_current = df_current[df_current['beneficiary_display'].isin(selected_benefs)]
    
    # Tag Filter
    if 'tags' in df_current.columns:
        all_available_tags = get_all_tags()
        if all_available_tags:
            selected_tags = st.sidebar.multiselect("Filtrer par Tags 🏷️", all_available_tags)
            if selected_tags:
                def match_tags(row_tags):
                    if not row_tags: return False
                    row_tags_list = [t.strip().lower() for t in str(row_tags).split(',')]
                    return any(tag.lower() in row_tags_list for tag in selected_tags)
                df_current = df_current[df_current['tags'].apply(match_tags)]
    
    st.sidebar.divider()
    show_internal = st.sidebar.checkbox("Afficher virements internes 🔄", value=False)
    show_hors_budget = st.sidebar.checkbox("Afficher hors budget 🚫", value=False)
    
    # Global exclusion for KPIs and Charts
    if not show_internal:
        df_current = df_current[df_current['category_validated'] != 'Virement Interne']
    if not show_hors_budget:
        df_current = df_current[df_current['category_validated'] != 'Hors Budget']

    # === PREVIOUS PERIOD CALCULATION ===
    df_prev = compute_previous_period(df, df_current, show_internal, show_hors_budget)

    # === KPI CARDS ===
    render_kpi_cards(df_current, df_prev)
    
    st.divider()
    
    # === EVOLUTION CHART ===
    render_evolution_chart(df_current)
    
    st.divider()
    
    # === SAVINGS TREND ===
    render_savings_trend_chart()
    
    st.divider()

    # === CATEGORY & TOP EXPENSES ===
    col_c1, col_c2 = st.columns([1.2, 1])
    
    cat_emoji_map = get_categories_with_emojis()
    
    with col_c1:
        render_category_bar_chart(df_current, cat_emoji_map)

    with col_c2:
        render_top_expenses(df_current, cat_emoji_map, limit=10)

    st.divider()

    # === BUDGETS ===
    df_exp = prepare_expense_dataframe(df_current, cat_emoji_map)
    render_budget_tracker(df_exp, cat_emoji_map)
    
    # === NEW: BUDGET PREDICTIONS ===
    st.subheader("📈 Alertes Budgétaires")
    budgets = get_budgets()
    if not budgets.empty:
        from modules.ai import predict_budget_overruns, get_budget_alerts_summary
        import datetime
        
        # Get current month data
        today = datetime.date.today()
        current_month = today.strftime('%Y-%m')
        df['date_dt'] = pd.to_datetime(df['date'])
        df_month = df[df['date_dt'].dt.strftime('%Y-%m') == current_month]
        
        predictions = predict_budget_overruns(df_month, budgets)
        
        if predictions:
            summary = get_budget_alerts_summary(predictions)
            
            col_alert1, col_alert2, col_alert3 = st.columns(3)
            with col_alert1:
                st.metric("🟢 OK", summary['ok_count'])
            with col_alert2:
                st.metric("🟠 Attention", summary['warning_count'])
            with col_alert3:
                st.metric("🔴 Dépassement", summary['overrun_count'])
            
            # Show predictions
            for pred in predictions:
                if pred['status'] != 'ok':  # Only show warnings and overruns
                    with st.expander(f"{pred['alert_level']} {pred['category']} - {pred['usage_percent']:.0f}% du budget"):
                        col_p1, col_p2 = st.columns(2)
                        with col_p1:
                            st.metric("Dépensé", f"{pred['current_spent']:.0f}€")
                            st.metric("Budget", f"{pred['budget']:.0f}€")
                        with col_p2:
                            st.metric("Projection fin de mois", f"{pred['projected_spent']:.0f}€")
                            st.metric("Moyenne journalière", f"{pred['daily_avg']:.0f}€/jour")
    else:
        st.info("Définissez des budgets pour activer les alertes prédictives.")
    
    st.divider()

    # === FORECASTING ===
    cat_props = get_categories_df()
    FIXED_CATEGORIES = cat_props[cat_props['is_fixed'] == 1]['name'].tolist()
    render_month_end_forecast(df, selected_years, selected_months, FIXED_CATEGORIES)
    
    st.divider()
    
    # === MONTHLY STACKED CHART ===
    render_monthly_stacked_chart(df, cat_emoji_map)

    st.divider()

    # === BENEFICIARY & TAGS ANALYSIS ===
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if 'beneficiary_display' in df_current.columns:
            # Household Members Chart
            household_members_only = official_list + ['Famille', 'Maison']
            df_members = df_current[df_current['amount'] < 0].copy()
            df_members = df_members[df_members['beneficiary_display'].isin(household_members_only)]
            df_members_sum = df_members.groupby('beneficiary_display')['amount'].sum().abs().reset_index()
            df_members_sum.columns = ['Membre', 'Montant']
            
            st.subheader("👥 Par Membre du Foyer")
            if not df_members_sum.empty:
                fig_members = px.pie(df_members_sum, values='Montant', names='Membre', hole=0.4,
                                     color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_members, use_container_width=True)
            else:
                st.info("Aucune dépense affectée aux membres sur cette période.")

            st.divider()

            # Third-party Beneficiaries Chart
            household_exclude = official_list + ['Famille', 'Maison', 'Inconnu', 'Anonyme', '']
            df_tiers = df_current[df_current['amount'] < 0].copy()
            df_tiers = df_tiers[~df_tiers['beneficiary_display'].isin(household_exclude)]
            df_tiers_sum = df_tiers.groupby('beneficiary_display')['amount'].sum().abs().reset_index()
            df_tiers_sum.columns = ['Bénéficiaire', 'Montant']
            
            st.subheader("🏢 Par Bénéficiaire (Tiers)")
            if not df_tiers_sum.empty:
                fig_tiers = px.pie(df_tiers_sum.head(15), values='Montant', names='Bénéficiaire', hole=0.4,
                                   color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_tiers, use_container_width=True)
            else:
                st.info("Aucun bénéficiaire tiers détecté sur cette période.")
                
    with col_a2:
        st.subheader("🏷️ Par Tags")
        if 'tags' in df_current.columns:
            tag_data = []
            for _, row in df_current[df_current['amount'] < 0].iterrows():
                if pd.notna(row['tags']):
                    ts = [t.strip() for t in str(row['tags']).split(',') if t.strip()]
                    for t in ts: tag_data.append({"Tag": t, "Montant": abs(row['amount'])})
            if tag_data:
                df_tags = pd.DataFrame(tag_data).groupby('Tag')['Montant'].sum().reset_index().sort_values('Montant', ascending=False)
                fig_tag = px.bar(df_tags.head(10), x='Montant', y='Tag', orientation='h', color='Tag',
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_tag.update_layout(showlegend=False, xaxis_title="Montant (€)", yaxis_title="")
                st.plotly_chart(fig_tag, use_container_width=True)
            else:
                st.info("Aucun tag sur cette période.")

    st.divider()

    # === AI FINANCIAL REPORT ===
    render_ai_financial_report(df_current, df_prev, df, selected_years, selected_months)

from modules.ui.layout import render_app_info
render_app_info()
