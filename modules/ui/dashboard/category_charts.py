import streamlit as st
import pandas as pd
import plotly.express as px

def prepare_expense_dataframe(df_current: pd.DataFrame, cat_emoji_map: dict) -> pd.DataFrame:
    """
    Prepare expense dataframe with category emojis.
    
    Args:
        df_current: Current period transactions
        cat_emoji_map: Category to emoji mapping
        
    Returns:
        Prepared dataframe with categorized expenses
    """
    # Filter expenses only, exclude certain categories
    df_exp = df_current[
        (df_current['amount'] < 0) & 
        (~df_current['category_validated'].isin(['Revenus', 'Virement Interne', 'Hors Budget']))
    ].copy()
    
    if df_exp.empty:
        return pd.DataFrame()
    
    df_exp['amount'] = df_exp['amount'].abs()
    
    # Add display category with emoji
    df_exp['raw_cat'] = df_exp.apply(
        lambda x: x['category_validated'] if x['category_validated'] != 'Inconnu' else (x['original_category'] or "Inconnu"), 
        axis=1
    )
    df_exp['Catégorie'] = df_exp['raw_cat'].apply(lambda x: f"{cat_emoji_map.get(x, '🏷️')} {x}")
    
    return df_exp

def render_category_bar_chart(df_current: pd.DataFrame, cat_emoji_map: dict):
    """
    Render horizontal bar chart of expenses by category.
    
    Args:
        df_current: Current period transactions
        cat_emoji_map: Category to emoji mapping
    """
    st.subheader("📊 Répartition par Catégorie")
    
    df_exp = prepare_expense_dataframe(df_current, cat_emoji_map)
    
    if df_exp.empty:
        st.info("Aucune dépense sur cette période.")
        return
    
    # Group by category and sum
    df_cat_sum = df_exp.groupby('Catégorie')['amount'].sum().reset_index()
    df_cat_sum = df_cat_sum.sort_values('amount', ascending=True)
    
    # Create bar chart
    fig_cat = px.bar(
        df_cat_sum, 
        x="amount", 
        y="Catégorie", 
        orientation="h",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_cat.update_layout(
        showlegend=False, 
        xaxis_title="Montant (€)", 
        yaxis_title="", 
        height=450
    )
    
    st.plotly_chart(fig_cat, use_container_width=True)

def render_category_pie_chart(df_current: pd.DataFrame, cat_emoji_map: dict, 
                              title: str = "Répartition des Dépenses"):
    """
    Render pie chart of expenses by category.
    
    Args:
        df_current: Current period transactions
        cat_emoji_map: Category to emoji mapping
        title: Chart title
    """
    df_exp = prepare_expense_dataframe(df_current, cat_emoji_map)
    
    if df_exp.empty:
        st.info("Aucune dépense sur cette période.")
        return
    
    # Group by category
    df_cat_sum = df_exp.groupby('Catégorie')['amount'].sum().reset_index()
    
    # Create pie chart
    fig_pie = px.pie(
        df_cat_sum, 
        values='amount', 
        names='Catégorie',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_layout(title=title)
    
    st.plotly_chart(fig_pie, use_container_width=True)

@st.cache_data(ttl=300)
def _prepare_monthly_stacked_data(df: pd.DataFrame, cat_emoji_map: dict) -> pd.DataFrame:
    """Prépare les données pour le graphique empilé (avec cache)."""
    if df.empty:
        return pd.DataFrame()
    
    # date_dt est déjà présent depuis la page principale
    exclude_cats = ['Revenus', 'Virement Interne', 'Hors Budget']
    df_monthly = df[(df['amount'] < 0) & (~df['category_validated'].isin(exclude_cats))].copy()
    
    if df_monthly.empty:
        return pd.DataFrame()
    
    df_monthly['amount'] = df_monthly['amount'].abs()
    
    # Add display category
    df_monthly['display_category'] = df_monthly.apply(
        lambda x: (
            lambda v: f"{cat_emoji_map.get(v, '🏷️')} {v}"
        )(x['category_validated'] if x['category_validated'] != 'Inconnu' else (x['original_category'] or "Inconnu")),
        axis=1
    )
    
    # Extract Month-Year for grouping
    df_monthly['month_year'] = df_monthly['date_dt'].dt.strftime('%Y-%m')
    
    # Group and aggregate
    df_stacked = df_monthly.groupby(['month_year', 'display_category'])['amount'].sum().reset_index()
    df_stacked.columns = ['Mois', 'Catégorie', 'Montant']
    
    return df_stacked


def render_monthly_stacked_chart(df: pd.DataFrame, cat_emoji_map: dict):
    """
    Render stacked bar chart of monthly expenses by category.
    
    Args:
        df: Full transaction dataset (avec date_dt déjà présent)
        cat_emoji_map: Category to emoji mapping
    """
    st.subheader("Évolution Mensuelle par Catégorie")
    
    # Utiliser les données en cache
    df_stacked = _prepare_monthly_stacked_data(df, cat_emoji_map)
    
    if df_stacked.empty:
        st.info("Aucune donnée disponible.")
        return
    
    # Create stacked bar chart
    fig_stacked = px.bar(
        df_stacked, 
        x='Mois', 
        y='Montant', 
        color='Catégorie', 
        title="Dépenses mensuelles empilées", 
        barmode='stack',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_stacked.update_layout(
        xaxis_title='', 
        yaxis_title='Montant (€)', 
        legend_title='Catégorie'
    )
    
    st.plotly_chart(fig_stacked, use_container_width=True)
