import streamlit as st
from modules.data_manager import get_all_transactions
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Synthèse", page_icon="📊", layout="wide")

st.title("📊 Tableau de bord")

df = get_all_transactions()

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
            
    # KPI
    col1, col2, col3 = st.columns(3)
    
    total_depenses = df[df['amount'] < 0]['amount'].sum()
    total_revenus = df[df['amount'] > 0]['amount'].sum()
    solde = total_revenus + total_depenses
    
    col1.metric("Dépenses Totales", f"{total_depenses:.2f} €")
    col2.metric("Revenus Totaux", f"{total_revenus:.2f} €")
    col3.metric("Solde Période", f"{solde:.2f} €")
    
    st.divider()
    
    # Graphs
    col_chart1, col_chart2 = st.columns(2)
    
    # Logic for Fixed vs Variable
    FIXED_CATEGORIES = ["Abonnements", "Logement", "Impôts", "Assurances", "Emprunt immobilier"]
    # We could allow user to configure this later in "Rules" or "Config"
    
    df_expenses = df[df['amount'] < 0].copy()
    df_expenses['amount'] = df_expenses['amount'].abs()
    df_expenses['display_category'] = df_expenses.apply(lambda x: x['category_validated'] if x['category_validated'] != 'Inconnu' else (x['original_category'] or "Inconnu"), axis=1)
    
    df_expenses['type'] = df_expenses['display_category'].apply(lambda x: 'Fixe' if x in FIXED_CATEGORIES else 'Variable')
    
    # Graphs
    curr_col1, curr_col2 = st.columns(2)
    
    with curr_col1:
        st.subheader("Fixe vs Variable")
        df_type = df_expenses.groupby('type')['amount'].sum().reset_index()
        fig_type = px.pie(df_type, values='amount', names='type', hole=0.5, color_discrete_sequence=['#4F81BD', '#E5533D'])
        st.plotly_chart(fig_type, use_container_width=True)
        
    with curr_col2:
        st.subheader("Dépenses par Catégorie")
        df_cat = df_expenses.groupby('display_category')['amount'].sum().reset_index()
        fig_cat = px.bar(df_cat, x='display_category', y='amount', color='display_category')
        st.plotly_chart(fig_cat, use_container_width=True)

    st.divider()
    
    st.subheader("Évolution Mensuelle par Catégorie")
    df['date'] = pd.to_datetime(df['date'])
    # Resample to month
    # We need to use valid categories
    df_monthly = df[df['amount'] < 0].copy()
    df_monthly['amount'] = df_monthly['amount'].abs()
    df_monthly['display_category'] = df_monthly.apply(lambda x: x['category_validated'] if x['category_validated'] != 'Inconnu' else (x['original_category'] or "Inconnu"), axis=1)
    # Extract Month-Year for grouping
    df_monthly['month_year'] = df_monthly['date'].dt.strftime('%Y-%m')
    
    df_stacked = df_monthly.groupby(['month_year', 'display_category'])['amount'].sum().reset_index()
    
    fig_stacked = px.bar(df_stacked, x='month_year', y='amount', color='display_category', 
                         title="Dépenses mensuelles empilées", barmode='stack')
    st.plotly_chart(fig_stacked, use_container_width=True)

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
