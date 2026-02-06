import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from modules.transaction_types import (
    filter_expense_transactions,
    is_excluded_category,
    EXCLUDED_CATEGORIES
)

def prepare_expense_dataframe(df_current: pd.DataFrame, cat_emoji_map: dict) -> pd.DataFrame:
    """
    Prepare expense dataframe with category emojis.
    Filtre les dépenses en utilisant les catégories (pas le signe du montant).
    
    Args:
        df_current: Current period transactions
        cat_emoji_map: Category to emoji mapping
        
    Returns:
        Prepared dataframe with categorized expenses
    """
    # Filter expenses only using categories
    df_exp = filter_expense_transactions(df_current).copy()
    
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
    Render horizontal bar chart of expenses by category with clickable buttons.
    
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
    df_cat_sum = df_exp.groupby(['Catégorie', 'raw_cat'])['amount'].sum().reset_index()
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
    
    # Clickable category buttons
    st.caption("🔍 Cliquez sur une catégorie pour voir le détail des opérations :")
    
    # Import explorer launcher
    from modules.ui.explorer import launch_explorer
    
    # Create buttons in rows of 4
    categories_sorted = df_cat_sum.sort_values('amount', ascending=False)
    num_cols = 4
    
    for i in range(0, len(categories_sorted), num_cols):
        cols = st.columns(num_cols)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(categories_sorted):
                row = categories_sorted.iloc[idx]
                raw_cat = row['raw_cat']
                display_cat = row['Catégorie']
                amount = row['amount']
                
                with col:
                    if st.button(
                        f"{display_cat}\n{amount:,.0f} €",
                        key=f"cat_btn_{raw_cat}_{idx}",
                        use_container_width=True
                    ):
                        launch_explorer('category', raw_cat, '6_Explorer')


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
    Render stacked bar chart of monthly expenses by category with income line.
    
    Args:
        df: Full transaction dataset (avec date_dt déjà présent)
        cat_emoji_map: Category to emoji mapping
    """
    st.subheader("📊 Évolution Mensuelle par Catégorie")
    
    # Utiliser les données en cache
    df_stacked = _prepare_monthly_stacked_data(df, cat_emoji_map)
    
    if df_stacked.empty:
        st.info("Aucune donnée disponible.")
        return
    
    # Préparer les données des revenus
    df_revenus = df[df['amount'] > 0].copy()
    if not df_revenus.empty:
        df_revenus['month_year'] = df_revenus['date_dt'].dt.strftime('%Y-%m')
        df_revenus_mensuel = df_revenus.groupby('month_year')['amount'].sum().reset_index()
        df_revenus_mensuel.columns = ['Mois', 'Revenus']
    else:
        df_revenus_mensuel = pd.DataFrame()
    
    # Créer le graphique combiné avec double axe Y
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Ajouter les barres empilées des dépenses par catégorie
    categories = df_stacked['Catégorie'].unique()
    colors = px.colors.qualitative.Set2
    
    for i, cat in enumerate(categories):
        df_cat = df_stacked[df_stacked['Catégorie'] == cat]
        fig.add_trace(
            go.Bar(
                x=df_cat['Mois'],
                y=df_cat['Montant'],
                name=cat,
                marker_color=colors[i % len(colors)],
                opacity=0.8
            ),
            secondary_y=False
        )
    
    # Ajouter la courbe des revenus
    if not df_revenus_mensuel.empty:
        fig.add_trace(
            go.Scatter(
                x=df_revenus_mensuel['Mois'],
                y=df_revenus_mensuel['Revenus'],
                name='💰 Revenus',
                mode='lines+markers',
                line=dict(color='#22c55e', width=4, dash='solid'),
                marker=dict(size=10, symbol='diamond'),
            ),
            secondary_y=False
        )
        
        # Calculer et ajouter le solde (revenus - dépenses totaux)
        df_depenses_totales = df_stacked.groupby('Mois')['Montant'].sum().reset_index()
        df_combined = df_revenus_mensuel.merge(df_depenses_totales, on='Mois', how='outer').fillna(0)
        df_combined['Solde'] = df_combined['Revenus'] - df_combined['Montant']
        
        fig.add_trace(
            go.Scatter(
                x=df_combined['Mois'],
                y=df_combined['Solde'],
                name='📈 Solde Net',
                mode='lines+markers',
                line=dict(color='white', width=3, dash='dot'),
                marker=dict(size=6),
            ),
            secondary_y=True
        )
    
    # Mise à jour du layout
    fig.update_layout(
        title="Dépenses par catégorie vs Revenus",
        barmode='stack',
        xaxis_title='',
        yaxis_title='Montant (€)',
        legend_title='Légende',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_yaxes(title_text="Montant (€)", secondary_y=False)
    fig.update_yaxes(title_text="Solde Net (€)", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajouter une légende explicative
    st.caption("💡 **Lecture**: Les barres empilées représentent les dépenses par catégorie. La ligne verte 💰 montre les revenus. La ligne pointillée blanche 📈 montre le solde (revenus - dépenses).")
