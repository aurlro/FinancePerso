import streamlit as st
import pandas as pd

def render_top_expenses(df_current: pd.DataFrame, cat_emoji_map: dict, limit: int = 10):
    """
    Render table of top expenses.
    
    Args:
        df_current: Current period transactions
        cat_emoji_map: Category to emoji mapping
        limit: Number of top expenses to show (default: 10)
    """
    st.subheader("🔝 Top 10 Dépenses")
    
    # Filter expenses only, exclude certain categories
    df_exp = df_current[
        (df_current['amount'] < 0) & 
        (~df_current['category_validated'].isin(['Revenus', 'Virement Interne', 'Hors Budget']))
    ].copy()
    
    if df_exp.empty:
        st.info("Aucune dépense sur cette période.")
        return
    
    df_exp['amount'] = df_exp['amount'].abs()
    
    # Add display category with emoji
    df_exp['raw_cat'] = df_exp.apply(
        lambda x: x['category_validated'] if x['category_validated'] != 'Inconnu' else (x['original_category'] or "Inconnu"), 
        axis=1
    )
    df_exp['Catégorie'] = df_exp['raw_cat'].apply(lambda x: f"{cat_emoji_map.get(x, '🏷️')} {x}")
    
    # Get top N
    top_expenses = df_exp.sort_values('amount', ascending=False).head(limit)
    
    # Clean for display
    display_top = top_expenses[['date', 'label', 'Catégorie', 'amount']].copy()
    display_top.columns = ['Date', 'Libellé', 'Catégorie', 'Montant (€)']
    
    st.dataframe(display_top, use_container_width=True, hide_index=True)
