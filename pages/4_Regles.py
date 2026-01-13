import streamlit as st
from modules.data_manager import get_learning_rules, delete_learning_rule, add_learning_rule
from modules.ui import load_css
import pandas as pd

st.set_page_config(page_title="Règles & Mémoire", page_icon="🧠", layout="wide")
load_css()

st.title("🧠 Mémoire de l'assistant")
st.markdown("Gérez ici les règles de catégorisation automatique.")

# --- ADD RULE SECTION ---
with st.expander("➕ Ajouter une nouvelle règle", expanded=False):
    with st.form("add_rule_form"):
        col_pat, col_cat = st.columns([3, 2])
        with col_pat:
            new_pattern = st.text_input("Mot-clé ou Pattern (Regex)", placeholder="Ex: UBER ou ^UBER.*TRIP")
        with col_cat:
            CATEGORIES = [
                "Alimentation", "Transport", "Logement", "Santé", "Loisirs", 
                "Achats", "Abonnements", "Restaurants", "Services", "Virements", "Inconnu"
            ]
            new_category = st.selectbox("Catégorie cible", CATEGORIES)
            
        submitted = st.form_submit_button("Ajouter la règle")
        if submitted:
            if new_pattern and new_category:
                if add_learning_rule(new_pattern, new_category):
                    st.success(f"Règle '{new_pattern}' -> '{new_category}' ajoutée !")
                    st.rerun()
                else:
                    st.error("Erreur lors de l'ajout (peut-être que ce pattern existe déjà ?)")
            else:
                st.warning("Veuillez remplir le pattern.")

st.divider()

# --- EXISTING RULES SECTION ---
rules_df = get_learning_rules()

if rules_df.empty:
    st.info("Aucune règle apprise pour le moment. Ajoutez-en une ci-dessus ou cochez 'Mém.' lors de la validation !")
else:
    st.markdown(f"**{len(rules_df)}** règles actives.")
    
    # Display as table with delete action
    for index, row in rules_df.iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.code(row['pattern'], language="text")
        with col2:
            st.markdown(f"**{row['category']}**")
        with col3:
            st.caption(f"Créé le {row['created_at']}")
        with col4:
            if st.button("🗑️", key=f"del_{row['id']}", help="Supprimer cette règle"):
                delete_learning_rule(row['id'])
                st.rerun()
        st.divider()
        st.divider()

st.header("🎯 Budgets Mensuels")
st.markdown("Définissez vos objectifs de dépenses mensuelles par catégorie.")
from modules.data_manager import set_budget, get_budgets

# Load existing budgets
budgets_df = get_budgets()
budget_map = dict(zip(budgets_df['category'], budgets_df['amount']))

CATEGORIES = [
    "Alimentation", "Transport", "Logement", "Santé", "Loisirs", 
    "Achats", "Abonnements", "Restaurants", "Services", "Virements"
]

with st.form("budget_form"):
    cols = st.columns(3)
    new_budgets = {}
    
    for i, cat in enumerate(CATEGORIES):
        with cols[i % 3]:
            # Default to existing logic
            val = budget_map.get(cat, 0.0)
            new_val = st.number_input(f"{cat} (€)", min_value=0.0, value=float(val), step=10.0, key=f"bud_{cat}")
            new_budgets[cat] = new_val

    if st.form_submit_button("Sauvegarder les budgets", type="primary"):
        for cat, amount in new_budgets.items():
            if amount > 0 or cat in budget_map: # Only save if > 0 or if updating existing
                set_budget(cat, amount)
        st.success("Budgets mis à jour !")
        st.rerun()

st.divider()
