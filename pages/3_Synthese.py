import streamlit as st
from modules.data_manager import get_all_transactions, init_db
from modules.ui import load_css, card_kpi
import pandas as pd
import plotly.express as px
import datetime
import calendar
from modules.analytics import detect_financial_profile
from modules.data_manager import get_budgets, get_categories_with_emojis, get_all_tags, get_categories_df
from modules.categorization import generate_financial_report

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

if df.empty:
    st.info("Aucune donnée disponible. Commencez par importer des relevés.")
else:
    # FILTERS
    st.sidebar.header("Filtres")
    
    # Account Filter
    # Check if 'account_label' exists (backward-compatibility/migration check done in data_manager but might be empty for old rows)
    if 'account_label' in df.columns:
        accounts = df['account_label'].unique().tolist()
        selected_accounts = st.sidebar.multiselect("Comptes", accounts, default=accounts)
        if selected_accounts:
            df = df[df['account_label'].isin(selected_accounts)]
            
    # Member Filter
    if 'member' in df.columns:
        members = df['member'].unique().tolist()
        # Clean 'None' or empty
        members = [m for m in members if m]
        selected_members = st.sidebar.multiselect("Membres (Carte)", members, default=members)
        if selected_members:
            df = df[df['member'].isin(selected_members)]
            
    # Beneficiary Filter
    if 'beneficiary' in df.columns:
        beneficiaries = df['beneficiary'].dropna().unique().tolist()
        if beneficiaries:
            selected_benefs = st.sidebar.multiselect("Bénéficiaires", beneficiaries, default=beneficiaries)
            if selected_benefs:
                df = df[df['beneficiary'].isin(selected_benefs)]
    
    # Tag Filter
    if 'tags' in df.columns:
        all_available_tags = get_all_tags()
        if all_available_tags:
            selected_tags = st.sidebar.multiselect("Filtrer par Tags 🏷️", all_available_tags)
            if selected_tags:
                # Mask where ANY of the selected tags matches one of the row's tags
                def match_tags(row_tags):
                    if not row_tags: return False
                    row_tags_list = [t.strip().lower() for t in str(row_tags).split(',')]
                    return any(tag.lower() in row_tags_list for tag in selected_tags)
                
                df = df[df['tags'].apply(match_tags)]
            
    st.sidebar.divider()
    show_internal = st.sidebar.checkbox("Afficher virements internes 🔄", value=False)
    show_hors_budget = st.sidebar.checkbox("Afficher hors budget 🚫", value=False)
    
    # Global exclusion for KPIs and Charts unless toggled
    if not show_internal:
        df = df[df['category_validated'] != 'Virement Interne']
    if not show_hors_budget:
        df = df[df['category_validated'] != 'Hors Budget']

    # KPI
    col1, col2, col3 = st.columns(3)
    
    total_depenses = df[df['amount'] < 0]['amount'].sum()
    total_revenus = df[df['amount'] > 0]['amount'].sum()
    solde = total_revenus + total_depenses
    
    with col1:
        card_kpi("Dépenses Totales", f"{total_depenses:,.2f} €", trend="Mois en cours", trend_color="negative")
    with col2:
        card_kpi("Revenus Totaux", f"{total_revenus:,.2f} €", trend="Stable", trend_color="positive")
    with col3:
        color = "positive" if solde >= 0 else "negative"
        card_kpi("Solde Période", f"{solde:,.2f} €", trend="Net", trend_color=color)
    
    st.divider()
    
    # Graphs
    col_chart1, col_chart2 = st.columns(2)
    
    # Logic for Fixed vs Variable
    cat_props = get_categories_df()
    FIXED_CATEGORIES = cat_props[cat_props['is_fixed'] == 1]['name'].tolist()
    
    df_expenses = df[df['amount'] < 0].copy()
    df_expenses['amount'] = df_expenses['amount'].abs()
    
    cat_emoji_map = get_categories_with_emojis()
    def get_cat_with_emoji(cat_name):
        emoji = cat_emoji_map.get(cat_name, "🏷️")
        return f"{emoji} {cat_name}"

    df_expenses['raw_category'] = df_expenses.apply(
        lambda x: x['category_validated'] if x['category_validated'] != 'Inconnu' else (x['original_category'] or "Inconnu"), 
        axis=1
    )
    df_expenses['display_category'] = df_expenses['raw_category'].apply(get_cat_with_emoji)
    
    df_expenses['type'] = df_expenses['raw_category'].apply(lambda x: 'Fixe' if x in FIXED_CATEGORIES else 'Variable')
    
    # Graphs
    curr_col1, curr_col2 = st.columns(2)
    
    with curr_col1:
        st.subheader("Fixe vs Variable")
        df_type = df_expenses.groupby('type')['amount'].sum().reset_index()
        df_type.columns = ['Type', 'Montant']  # French labels
        fig_type = px.pie(df_type, values='Montant', names='Type', hole=0.5, 
                          color_discrete_sequence=['#4F81BD', '#E5533D'])
        fig_type.update_traces(textposition='inside', textinfo='percent+label')
        fig_type.update_layout(showlegend=False)
        st.plotly_chart(fig_type, use_container_width=True)
        
    with curr_col2:
        st.subheader("Dépenses par Catégorie")
        df_cat = df_expenses.groupby('display_category')['amount'].sum().reset_index()
        df_cat.columns = ['Catégorie', 'Montant']  # French labels
        df_cat = df_cat.sort_values('Montant', ascending=True)  # Sort for better viz
        fig_cat = px.bar(df_cat, x='Montant', y='Catégorie', orientation='h',
                         color='Catégorie', color_discrete_sequence=px.colors.qualitative.Set2)
        fig_cat.update_layout(showlegend=False, xaxis_title='Montant (€)', yaxis_title='')
        st.plotly_chart(fig_cat, use_container_width=True)

    st.divider()

    # BUDGETS SECTION
    st.header("🎯 Suivi des Budgets")
    budgets = get_budgets()
    
    if budgets.empty:
        st.info("Aucun budget défini. Allez dans 'Règles' pour en configurer.")
    else:
        # Calculate spending per category for current month context
        # Check date context again
        # Reusing df_expenses (all time) -> need current month only
        
        # Determine "Current Month" based on Max date or Today
        today = pd.Timestamp.now().date()
        if not df.empty:
             max_date_data = df['date'].max()
             if isinstance(max_date_data, str):
                 max_date_data = pd.to_datetime(max_date_data).date()
             elif isinstance(max_date_data, pd.Timestamp):
                 max_date_data = max_date_data.date()
             
             if max_date_data.year == today.year and max_date_data.month == today.month:
                 target_month_str = today.strftime('%Y-%m')
             else:
                 target_month_str = max_date_data.strftime('%Y-%m')
        else:
             target_month_str = today.strftime('%Y-%m')

        mask_month = df_expenses['date'].apply(lambda x: x.strftime('%Y-%m')) == target_month_str
        df_month_exp = df_expenses[mask_month]
        
        spending_map = df_month_exp.groupby('display_category')['amount'].sum().to_dict()
        
        # Display Gauges
        # We use st.progress with custom label
        cols_b = st.columns(3)
        for index, row in budgets.iterrows():
            cat = row['category']
            limit = row['amount']
            spent = spending_map.get(cat, 0.0)
            
            if limit > 0:
                percent = min(spent / limit, 1.0)
                delta = limit - spent
                
                with cols_b[index % 3]:
                    st.caption(f"**{cat}**")
                    if delta < 0:
                        st.progress(1.0)
                        st.markdown(f"⚠️ Dépassé de **{abs(delta):.0f}€** ({spent:.0f}/{limit:.0f}€)")
                    else:
                        st.progress(percent)
                        st.markdown(f"✅ Reste **{delta:.0f}€** ({spent:.0f}/{limit:.0f}€)")
            
    st.divider()

    # FORECASTING SECTION
    st.header("🔮 Prévisions Fin de Mois")
    
    today = datetime.date.today()
    # Find active month in data or use today
    # We use max_date from data to know "current month context"
    if not df.empty:
        max_date = df['date'].max()
        # Ensure max_date is date object (could be string, Timestamp, or date)
        if isinstance(max_date, str):
            max_date = pd.to_datetime(max_date).date()
        elif isinstance(max_date, pd.Timestamp):
            max_date = max_date.date()
    else:
        max_date = today

    # Forecast only makes sense if we are looking at the *current* real month
    if max_date.year == today.year and max_date.month == today.month:
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        days_passed = today.day
        
        # Get variable expenses for current month
        # We assume Fixed expenses happen anyway, Variable accumulate daily.
        current_month_mask = (df['date'].apply(lambda x: x.year) == today.year) & (df['date'].apply(lambda x: x.month) == today.month)
        df_curr_fe = df[current_month_mask].copy()
        
        # Recalculate types here as logic serves both
        # Or better reuse df_expenses if filtered? 
        # df_expenses is ALL time expenses properly typed.
        # Filter df_expenses for current month
        df_curr_expenses = df_expenses[current_month_mask & df_expenses.index.isin(df_expenses.index)] 
        # (Actually better to filter df_expenses directly)
        
        df_curr_expenses = df_expenses[df_expenses['date'].apply(lambda x: x.strftime('%Y-%m')) == today.strftime('%Y-%m')]
        
        if not df_curr_expenses.empty:
            # Calculate Income for current month
            df_curr_income = df[current_month_mask & (df['amount'] > 0)]
            current_income = df_curr_income['amount'].sum() if not df_curr_income.empty else 0.0

            expenses_fixed = df_curr_expenses[df_curr_expenses['type'] == 'Fixe']['amount'].sum()
            expenses_variable = df_curr_expenses[df_curr_expenses['type'] == 'Variable']['amount'].sum()
            
            # Linear Projection of Variable
            if days_passed > 0:
                avg_daily_var = expenses_variable / days_passed
                projected_variable = avg_daily_var * days_in_month
                projected_total_expenses = expenses_fixed + projected_variable
                
                projected_balance = current_income - projected_total_expenses
                current_balance = current_income - (expenses_fixed + expenses_variable)
                
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    card_kpi("Solde Actuel", f"{current_balance:+.0f} €", trend=f"Recettes: {current_income:.0f}€", trend_color="positive" if current_balance>0 else "negative")
                with col_f2:
                    card_kpi("Dépenses Projetées", f"{projected_total_expenses:.0f} €", trend=f"soit {projected_variable:.0f}€ var.", trend_color="negative")
                with col_f3:
                    trend_txt = "Épargne" if projected_balance > 0 else "Déficit potentiel"
                    color = "positive" if projected_balance >= 0 else "negative"
                    card_kpi("Atterrissage Estimé", f"{projected_balance:+.0f} €", trend=trend_txt, trend_color=color)
                    
                st.info(f"💡 Basé sur une moyenne de **{avg_daily_var:.0f}€** par jour (variable). À ce rythme, l'estimation fin de mois est de **{projected_balance:+.0f}€**.")
            else:
                st.write("Début de mois, pas assez de données pour projeter.")
    else:
        st.caption(f"Prévisions disponibles pour le mois en cours ({today.strftime('%B %Y')}). Données actuelles : {max_date.strftime('%Y-%m')}")

    st.divider()
    
    st.subheader("Évolution Mensuelle par Catégorie")
    df['date'] = pd.to_datetime(df['date'])
    # Resample to month
    # We need to use valid categories
    df_monthly = df[df['amount'] < 0].copy()
    df_monthly['amount'] = df_monthly['amount'].abs()
    
    df_monthly['display_category'] = df_monthly.apply(
        lambda x: get_cat_with_emoji(x['category_validated'] if x['category_validated'] != 'Inconnu' else (x['original_category'] or "Inconnu")), 
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

    # NEW: Beneficiary and Tags Analysis
    col_new1, col_new2 = st.columns(2)
    
    with col_new1:
        st.subheader("Répartition par Bénéficiaire")
        if 'beneficiary' in df_expenses.columns and not df_expenses['beneficiary'].isna().all():
            df_benef = df_expenses.groupby('beneficiary')['amount'].sum().reset_index()
            df_benef.columns = ['Bénéficiaire', 'Montant']
            fig_benef = px.pie(df_benef, values='Montant', names='Bénéficiaire', hole=0.4,
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_benef, use_container_width=True)
        else:
            st.info("Aucune donnée bénéficiaire disponible.")

    with col_new2:
        st.subheader("Analyse des Tags")
        if 'tags' in df_expenses.columns and not df_expenses['tags'].isna().all():
            # Split tags (comma separated)
            all_tags = []
            for t in df_expenses['tags'].dropna():
                all_tags.extend([tag.strip().lower() for tag in t.split(',') if tag.strip()])
                
            if all_tags:
                df_tags = pd.Series(all_tags).value_counts().reset_index()
                df_tags.columns = ['Tag', 'Total']
                
                # Let's also calculate amount per tag
                tag_amounts = {}
                for idx, row in df_expenses.iterrows():
                    if pd.notna(row['tags']):
                        ts = [t.strip().lower() for t in str(row['tags']).split(',') if t.strip()]
                        for t in ts:
                            tag_amounts[t] = tag_amounts.get(t, 0) + row['amount']
                
                df_tag_money = pd.DataFrame(list(tag_amounts.items()), columns=['Tag', 'Montant']).sort_values('Montant', ascending=False)
                
                fig_tags = px.bar(df_tag_money.head(10), x='Montant', y='Tag', orientation='h',
                                  color='Tag', color_discrete_sequence=px.colors.qualitative.Safe)
                fig_tags.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'}, xaxis_title="Montant (€)")
                st.plotly_chart(fig_tags, use_container_width=True)
            else:
                st.info("Aucun tag utilisé pour le moment.")
        else:
            st.info("Aucune donnée de tag disponible.")

    st.divider()

    # AI Financial Report Section
    st.subheader("🔮 Analyse & Conseils IA")
    from modules.categorization import generate_financial_report
    import datetime

    # Prepare data for AI
    current_date = datetime.date.today()
    # If no data for current month, take last month with data
    if not df['date'].empty:
        max_date = df['date'].max().date()
    else:
        max_date = current_date

    # Define "Current Month" as the month of max_date
    current_month_str = max_date.strftime('%Y-%m')
    prev_month_date = max_date - datetime.timedelta(days=30)
    prev_month_str = prev_month_date.strftime('%Y-%m')
    current_year_str = str(max_date.year)

    # Calculate Stats
    
    # 1. Current Month Stats
    mask_curr = df['date'].dt.strftime('%Y-%m') == current_month_str
    df_curr = df[mask_curr]
    if not df_curr.empty:
        curr_expenses = df_curr[df_curr['amount'] < 0]['amount'].sum()
        curr_income = df_curr[df_curr['amount'] > 0]['amount'].sum()
        curr_top_cat = df_curr[df_curr['amount'] <0].groupby('category_validated')['amount'].sum().abs().nlargest(3).to_dict()
    else:
        curr_expenses = 0
        curr_income = 0
        curr_top_cat = {}

    # 2. Previous Month Stats
    mask_prev = df['date'].dt.strftime('%Y-%m') == prev_month_str
    df_prev = df[mask_prev]
    if not df_prev.empty:
        prev_expenses = df_prev[df_prev['amount'] < 0]['amount'].sum()
    else:
        prev_expenses = 0

    # 3. YTD Stats
    mask_ytd = df['date'].dt.year == max_date.year
    df_ytd = df[mask_ytd]
    ytd_expenses = df_ytd[df_ytd['amount'] < 0]['amount'].sum()
    ytd_income = df_ytd[df_ytd['amount'] > 0]['amount'].sum()
    ytd_savings = ytd_income + ytd_expenses # expenses are negative

    stats_payload = {
        "period": f"{current_month_str} (vs {prev_month_str})",
        "current_month": {
            "income": round(curr_income, 2),
            "expenses": round(curr_expenses, 2),
            "balance": round(curr_income + curr_expenses, 2),
            "top_expense_categories": {k: round(v, 2) for k,v in curr_top_cat.items()}
        },
        "previous_month": {
            "expenses": round(prev_expenses, 2),
            "evolution_percent": round(((curr_expenses - prev_expenses) / abs(prev_expenses) * 100), 1) if prev_expenses != 0 else 0
        },
        "ytd_stats": {
            "year": current_year_str,
            "total_income": round(ytd_income, 2),
            "total_expenses": round(ytd_expenses, 2),
            "total_savings": round(ytd_savings, 2),
            "savings_rate_percent": round((ytd_savings / ytd_income * 100), 1) if ytd_income > 0 else 0
        }
    }

    if st.button("Générer le rapport mensuel & conseils 🪄"):
        with st.spinner("L'IA analyse vos finances..."):
            report = generate_financial_report(stats_payload)
            st.markdown(report)
            st.success("Rapport généré avec succès !")
