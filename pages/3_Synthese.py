import streamlit as st
from modules.data_manager import get_all_transactions, init_db
from modules.ui import load_css, card_kpi
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import calendar
from modules.analytics import detect_financial_profile
from modules.categorization import generate_financial_report
from modules.data_manager import get_budgets, get_categories_with_emojis, get_all_tags, get_categories_df, get_orphan_labels, get_unique_members

st.set_page_config(page_title="Synthèse", page_icon="📊", layout="wide")
load_css()
init_db()  # Ensure migrations are run

st.title("📊 Tableau de bord")

df = get_all_transactions()

# SMART ONBOARDING NOTIFICATION
# Check if there are new suggestions (only once per session to avoid spam)
if 'onboarding_checked' not in st.session_state:
    st.session_state['onboarding_checked'] = False

if not st.session_state['onboarding_checked'] and not df.empty:
    suggestions = detect_financial_profile(df)
    
    if suggestions:
        st.session_state['onboarding_suggestions_count'] = len(suggestions)
        st.session_state['onboarding_checked'] = True # Avoid re-checking on every rerun
        
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
    # FILTERS
    # --- ADVANCED DATE FILTERS ---
    st.sidebar.subheader("📅 Période")
    
    # Extract available years and months from data
    df['date_dt'] = pd.to_datetime(df['date'])
    available_years = sorted(df['date_dt'].dt.year.unique().tolist(), reverse=True)
    
    selected_years = st.sidebar.multiselect("Années", available_years, default=[available_years[0]] if available_years else [])
    
    month_names = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                   "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    month_to_int = {name: i+1 for i, name in enumerate(month_names)}
    
    # Default to all months
    selected_month_names = st.sidebar.multiselect("Mois", month_names, default=month_names)
    selected_months = [month_to_int[m] for m in selected_month_names]
    
    # FILTERS
    st.sidebar.divider()
    st.sidebar.header("Filtres")
    
    # Filter by Year and Month first to get the "Current Period"
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
            
    # Member Filter
    official_list = get_unique_members()
    def consolidate_name(n):
        if not n or pd.isna(n): return "Inconnu"
        import unicodedata
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
    
    # Global exclusion for KPIs and Charts unless toggled
    if not show_internal:
        df_current = df_current[df_current['category_validated'] != 'Virement Interne']
    if not show_hors_budget:
        df_current = df_current[df_current['category_validated'] != 'Hors Budget']

    # --- PREVIOUS PERIOD CALCULATION ---
    # To calculate trends, we need the "Previous Period"
    # Logic: Offset the start of current period by its duration
    if not df_current.empty:
        min_date = df_current['date_dt'].min()
        max_date = df_current['date_dt'].max()
        duration = max_date - min_date
        
        # Approximate duration if only one day or one month
        if duration.days < 20: # Likely just one month selected
            prev_start = min_date - pd.DateOffset(months=1)
            prev_end = min_date - pd.Timedelta(days=1)
        else:
            prev_start = min_date - (duration + pd.Timedelta(days=1))
            prev_end = min_date - pd.Timedelta(days=1)
            
        df_prev = df[(df['date_dt'] >= prev_start) & (df['date_dt'] <= prev_end)].copy()
        
        # Apply the same exclusions to prev period
        if not show_internal:
            df_prev = df_prev[df_prev['category_validated'] != 'Virement Interne']
        if not show_hors_budget:
            df_prev = df_prev[df_prev['category_validated'] != 'Hors Budget']
    else:
        df_prev = pd.DataFrame()

    # --- KPI CALCULATION ---
    col1, col2, col3, col4 = st.columns(4)
    
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
            if prev == 0: return ("Stable", "positive")
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

    with col1:
        card_kpi("Dépenses", f"{cur_exp:,.0f} €", trend=exp_trend, trend_color=exp_color)
    with col2:
        card_kpi("Revenus", f"{cur_rev:,.0f} €", trend=rev_trend, trend_color=rev_color)
    with col3:
        card_kpi("Solde", f"{cur_solde:,.0f} €", trend=solde_trend, trend_color=solde_color)
    with col4:
        card_kpi("Épargne", f"{cur_saving_rate:.1f}%", trend="Taux", trend_color="positive" if cur_saving_rate > 10 else "negative")
    
    st.divider()
    
    # --- EVOLUTION CHART (Fixed) ---
    st.subheader("📉 Évolution des Flux")
    
    # Group by month
    df_evol = df_current.copy()
    df_evol['Mois'] = df_evol['date_dt'].dt.strftime('%Y-%m')
    
    # Complete the date range to avoid gaps
    all_months = pd.date_range(start=df_evol['date_dt'].min(), end=df_evol['date_dt'].max(), freq='MS').strftime('%Y-%m').tolist()
    
    monthly_data = []
    for m in all_months:
        g = df_evol[df_evol['Mois'] == m]
        inc = g[g['amount'] > 0]['amount'].sum()
        exp = abs(g[g['amount'] < 0]['amount'].sum())
        monthly_data.append({"Mois": m, "Revenus": inc, "Dépenses": exp})
    
    df_plot = pd.DataFrame(monthly_data)
    
    if not df_plot.empty:
        import numpy as np
        fig_evol = go.Figure()
        
        # Calculate min for the fill trick
        min_line = np.minimum(df_plot['Revenus'], df_plot['Dépenses'])
        
        # 1. Base trace for Surplus (Green area between min and Revenus)
        fig_evol.add_trace(go.Scatter(
            x=df_plot['Mois'], y=min_line,
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig_evol.add_trace(go.Scatter(
            x=df_plot['Mois'], y=df_plot['Revenus'],
            fill='tonexty',
            fillcolor='rgba(34, 197, 94, 0.3)',
            line=dict(width=0),
            name="Zone de Surplus (Épargne)",
            hoverinfo='skip'
        ))
        
        # 2. Base trace for Deficit (Red area between min and Dépenses)
        fig_evol.add_trace(go.Scatter(
            x=df_plot['Mois'], y=min_line,
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig_evol.add_trace(go.Scatter(
            x=df_plot['Mois'], y=df_plot['Dépenses'],
            fill='tonexty',
            fillcolor='rgba(239, 68, 68, 0.3)',
            line=dict(width=0),
            name="Zone de Déficit",
            hoverinfo='skip'
        ))
        
        # 3. Solid lines on top
        fig_evol.add_trace(go.Scatter(
            x=df_plot['Mois'], y=df_plot['Revenus'],
            name="Revenus",
            line=dict(color="#22c55e", width=4, shape='spline'),
            mode='lines+markers'
        ))
        fig_evol.add_trace(go.Scatter(
            x=df_plot['Mois'], y=df_plot['Dépenses'],
            name="Dépenses",
            line=dict(color="#ef4444", width=4, shape='spline'),
            mode='lines+markers'
        ))
        
        # 4. Solde Net (Line)
        df_net = df_plot.copy()
        df_net['Solde'] = df_net['Revenus'] - df_net['Dépenses']
        fig_evol.add_trace(go.Scatter(
            x=df_net['Mois'], y=df_net['Solde'],
            name="Caisse (Net)",
            line=dict(color="white" if not st.get_option("theme.base") == "light" else "black", width=2, dash='dot'),
            mode='lines'
        ))
        
        fig_evol.update_layout(
            xaxis_title="", 
            yaxis_title="Montant (€)", 
            height=450,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=50, b=0)
        )
        st.plotly_chart(fig_evol, use_container_width=True)
    else:
        st.info("Sélectionnez une période avec des données pour voir l'évolution.")

    # --- SAVINGS TREND ANALYTICS (Proposal 3) ---
    st.divider()
    st.subheader("📈 Tendance d'Épargne (12 derniers mois)")
    
    from modules.analytics import get_monthly_savings_trend
    df_trend = get_monthly_savings_trend(months=12)
    
    if not df_trend.empty:
        # Create combo chart: Bars for Cashflow, Line for Savings Rate
        fig_trend = go.Figure()
        
        # Bars for Savings Amount (Absolute)
        fig_trend.add_trace(go.Bar(
            x=df_trend['month'], 
            y=df_trend['Epargne'],
            name="Epargne (€)",
            marker_color=df_trend['Epargne'].apply(lambda x: '#22c55e' if x >= 0 else '#ef4444')
        ))
        
        # Line for Rate (%)
        fig_trend.add_trace(go.Scatter(
            x=df_trend['month'], 
            y=df_trend['Taux'],
            name="Taux (%)",
            yaxis="y2",
            line=dict(color="#3b82f6", width=3),
            mode='lines+markers'
        ))
        
        fig_trend.update_layout(
            xaxis_title="",
            yaxis=dict(title="Montant (€)", showgrid=False),
            yaxis2=dict(title="Taux (%)", overlaying="y", side="right", range=[-20, 80], showgrid=True),
            height=400,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Pas assez de données historiques pour la tendance d'épargne.")

    st.divider()

    # --- CATEGORY & DRILL DOWN ---
    col_c1, col_c2 = st.columns([1.2, 1])
    
    with col_c1:
        st.subheader("📊 Répartition par Catégorie")
        cat_props = get_categories_df()
        FIXED_CATEGORIES = cat_props[cat_props['is_fixed'] == 1]['name'].tolist()
        
        # Exclude 'Revenus', 'Virement Interne' and 'Hors Budget' from expense charts
        df_exp = df_current[
            (df_current['amount'] < 0) & 
            (~df_current['category_validated'].isin(['Revenus', 'Virement Interne', 'Hors Budget']))
        ].copy()
        df_exp['amount'] = df_exp['amount'].abs()
        cat_emoji_map = get_categories_with_emojis()
        
        df_exp['raw_cat'] = df_exp.apply(
            lambda x: x['category_validated'] if x['category_validated'] != 'Inconnu' else (x['original_category'] or "Inconnu"), 
            axis=1
        )
        df_exp['Catégorie'] = df_exp['raw_cat'].apply(lambda x: f"{cat_emoji_map.get(x, '🏷️')} {x}")
        
        df_cat_sum = df_exp.groupby('Catégorie')['amount'].sum().reset_index()
        df_cat_sum = df_cat_sum.sort_values('amount', ascending=True)
        
        fig_cat = px.bar(df_cat_sum, x="amount", y="Catégorie", orientation="h",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_cat.update_layout(showlegend=False, xaxis_title="Montant (€)", yaxis_title="", height=450)
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_c2:
        st.subheader("🔝 Top 10 Dépenses")
        top_10 = df_exp.sort_values('amount', ascending=False).head(10)
        if not top_10.empty:
            # Clean for display
            display_top = top_10[['date', 'label', 'Catégorie', 'amount']].copy()
            display_top.columns = ['Date', 'Libellé', 'Catégorie', 'Montant (€)']
            st.dataframe(display_top, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune dépense sur cette période.")

    st.divider()

    # BUDGETS SECTION
    st.header("🎯 Suivi des Budgets")
    budgets = get_budgets()
    
    if budgets.empty:
        st.info("Aucun budget défini. Allez dans 'Règles' pour en configurer.")
    else:
        # Calculate number of months in selection for proportional budget
        num_months = len(df_current['date_dt'].dt.strftime('%Y-%m').unique())
        if num_months == 0: num_months = 1
        
        spending_map = df_exp.groupby('Catégorie')['amount'].sum().to_dict()
        
        cols_b = st.columns(3)
        for index, row in budgets.iterrows():
            cat_name = row['category']
            display_cat = f"{cat_emoji_map.get(cat_name, '🏷️')} {cat_name}"
            limit = row['amount'] * num_months
            spent = spending_map.get(display_cat, 0.0)
            
            if limit > 0:
                percent = min(spent / limit, 1.0)
                delta = limit - spent
                
                with cols_b[index % 3]:
                    st.caption(f"**{display_cat}** ({num_months} mois)")
                    if delta < 0:
                        st.progress(1.0)
                        st.markdown(f"⚠️ Dépassé de **{abs(delta):.0f}€** ({spent:.0f}/{limit:.0f}€)")
                    else:
                        st.progress(percent)
                        st.markdown(f"✅ Reste **{delta:.0f}€** ({spent:.0f}/{limit:.0f}€)")
            
    st.divider()

    # FORECASTING SECTION
    today = datetime.date.today()
    if today.year in selected_years and today.month in selected_months:
        st.header("🔮 Prévisions Fin de Mois")
        
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        days_passed = today.day
        
        df_month = df[(df['date_dt'].dt.year == today.year) & (df['date_dt'].dt.month == today.month)].copy()
        if not df_month.empty:
            df_m_exp = df_month[df_month['amount'] < 0].copy()
            df_m_exp['amount'] = df_m_exp['amount'].abs()
            df_m_exp['raw_cat'] = df_m_exp.apply(lambda x: x['category_validated'] if x['category_validated'] != 'Inconnu' else (x['original_category'] or "Inconnu"), axis=1)
            df_m_exp['type'] = df_m_exp['raw_cat'].apply(lambda x: 'Fixe' if x in FIXED_CATEGORIES else 'Variable')
            
            exp_fixed = df_m_exp[df_m_exp['type'] == 'Fixe']['amount'].sum()
            exp_var = df_m_exp[df_m_exp['type'] == 'Variable']['amount'].sum()
            income = df_month[df_month['amount'] > 0]['amount'].sum()
            
            if days_passed > 0:
                avg_daily_var = exp_var / days_passed
                proj_var = avg_daily_var * days_in_month
                proj_total = exp_fixed + proj_var
                proj_bal = income - proj_total
                
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1: card_kpi("Solde Actuel", f"{income - (exp_fixed+exp_var):+.0f} €", trend=f"Recettes: {income:.0f}€", trend_color="positive")
                with col_f2: card_kpi("Dépenses Projetées", f"{proj_total:.0f} €", trend=f"soit {proj_var:.0f}€ var.", trend_color="negative")
                with col_f3: card_kpi("Atterrissage Estimé", f"{proj_bal:+.0f} €", trend="Épargne" if proj_bal > 0 else "Déficit", trend_color="positive" if proj_bal>0 else "negative")
                
                st.info(f"💡 Moyenne de **{avg_daily_var:.0f}€/jour** (variable). Estimation fin de mois : **{proj_bal:+.0f}€**.")
            else:
                st.write("Début de mois, pas assez de données pour projeter.")
        else:
            st.info("Aucune donnée pour le mois en cours pour les prévisions.")
    else:
        st.caption(f"Prévisions disponibles pour le mois en cours ({today.strftime('%B %Y')}).")

    st.divider()
    
    st.subheader("Évolution Mensuelle par Catégorie")
    df['date'] = pd.to_datetime(df['date'])
    # Resample to month - Exclude non-expense categories and only keep actual spending
    exclude_cats = ['Revenus', 'Virement Interne', 'Hors Budget']
    df_monthly = df[(df['amount'] < 0) & (~df['category_validated'].isin(exclude_cats))].copy()
    df_monthly['amount'] = df_monthly['amount'].abs()
    
    df_monthly['display_category'] = df_monthly.apply(
        lambda x: (
            lambda v: f"{cat_emoji_map.get(v, '🏷️')} {v}"
        )(x['category_validated'] if x['category_validated'] != 'Inconnu' else (x['original_category'] or "Inconnu")), 
        axis=1
    )
    # Extract Month-Year for grouping
    df_monthly['month_year'] = df_monthly['date'].dt.strftime('%Y-%m')
    
    df_stacked = df_monthly.groupby(['month_year', 'display_category'])['amount'].sum().reset_index()
    df_stacked.columns = ['Mois', 'Catégorie', 'Montant']  # French labels
    
    fig_stacked = px.bar(df_stacked, x='Mois', y='Montant', color='Catégorie', 
                         title="Dépenses mensuelles empilées", barmode='stack',
                         color_discrete_sequence=px.colors.qualitative.Set2)
    fig_stacked.update_layout(xaxis_title='', yaxis_title='Montant (€)', legend_title='Catégorie')
    st.plotly_chart(fig_stacked, use_container_width=True)

    st.divider()

    # BENEFICIARY & TAGS ANALYSIS
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if 'beneficiary_display' in df_current.columns:
            # 1. Household Members Chart
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

            # 2. Third-party Beneficiaries Chart
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

    # AI Financial Report Section
    st.subheader("🔮 Analyse & Conseils IA")

    # Prepare data for AI
    if not df_current.empty:
        # 1. Current Period Stats (from df_current)
        cur_inc = df_current[df_current['amount'] > 0]['amount'].sum()
        cur_exp_val = abs(df_current[df_current['amount'] < 0]['amount'].sum())
        cur_top_cat = df_current[df_current['amount'] < 0].groupby('category_validated')['amount'].sum().abs().nlargest(3).to_dict()
        
        # 2. Previous Period Stats (from df_prev calculated earlier)
        prev_exp_val = abs(df_prev[df_prev['amount'] < 0]['amount'].sum()) if not df_prev.empty else 0
        
        # 3. YTD context (all data for the latest year in selection)
        latest_year = max(selected_years) if selected_years else datetime.date.today().year
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
    else:
        st.info("Sélectionnez une période avec des données pour générer un rapport.")
