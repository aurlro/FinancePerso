import streamlit as st
import pandas as pd
from modules.db.budgets import get_budgets

def render_budget_tracker(df_exp: pd.DataFrame, cat_emoji_map: dict):
    """
    Render budget tracking section with progress bars.
    
    Args:
        df_exp: Expense dataframe with 'Catégorie' column
        cat_emoji_map: Category to emoji mapping
    """
    st.header("🎯 Suivi des Budgets")
    
    budgets = get_budgets()
    
    if budgets.empty:
        st.info("Aucun budget défini. Allez dans 'Règles' pour en configurer.")
        return
    
    # Calculate number of months in selection for proportional budget
    if 'date_dt' in df_exp.columns:
        num_months = len(df_exp['date_dt'].dt.strftime('%Y-%m').unique())
        if num_months == 0:
            num_months = 1
    else:
        num_months = 1
    
    # Calculate spending by category
    spending_map = df_exp.groupby('Catégorie')['amount'].sum().to_dict()
    
    # Display budget progress cards
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
