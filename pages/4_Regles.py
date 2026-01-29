import streamlit as st
import pandas as pd
from modules.data_manager import get_learning_rules, delete_learning_rule, add_learning_rule, set_budget, get_budgets, get_categories, init_db
from modules.ui import load_css

st.set_page_config(page_title="Règles & Mémoire", page_icon="🧠", layout="wide")
load_css()
init_db()  # Ensure migrations are applied

st.title("🧠 Mémoire de l'assistant")
st.markdown("Gérez ici les règles de catégorisation automatique.")

# --- ADD RULE SECTION ---
with st.expander("➕ Ajouter une nouvelle règle", expanded=False):
    with st.form("add_rule_form"):
        col_pat, col_cat = st.columns([3, 2])
        with col_pat:
            new_pattern = st.text_input("Mot-clé ou Pattern (Regex)", placeholder="Ex: UBER ou ^UBER.*TRIP")
        with col_cat:
            CATEGORIES = get_categories()
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
    col_header, col_apply = st.columns([3, 1])
    with col_header:
        st.markdown(f"**{len(rules_df)}** règles actives.")
    with col_apply:
        if st.button("🪄 Appliquer aux transactions", help="Relance la catégorisation automatique sur toutes les transactions en attente ou inconnues", use_container_width=True):
            from modules.db.audit import auto_fix_common_inconsistencies
            with st.spinner("Application des règles en cours..."):
                count = auto_fix_common_inconsistencies()
                if count > 0:
                    st.success(f"Fait ! {count} transactions mises à jour.")
                else:
                    st.info("Aucune transaction n'a été modifiée (déjà à jour).")
                st.rerun()
    
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

# --- RULE AUDIT SECTION ---
st.header("🕵️ Audit & Optimisation")
st.markdown("L'IA analyse vos règles pour détecter incohérences et doublons.")

col_audit, col_last_update = st.columns([1, 3])
with col_audit:
    if st.button("Lancer l'audit IA", type="primary", use_container_width=True):
        from modules.ai.rules_auditor import analyze_rules_integrity
        from datetime import datetime
        
        # Analyze
        issues = analyze_rules_integrity(rules_df)
        st.session_state['audit_last_run'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state['audit_results'] = issues
        st.rerun()

with col_last_update:
    if 'audit_last_run' in st.session_state:
        st.markdown(f"**Dernière mise à jour :** {st.session_state['audit_last_run']}")
    else:
        st.caption("Aucune analyse récente.")

# Display Results
if 'audit_results' in st.session_state:
    issues = st.session_state['audit_results']
    has_issues = any(issues.values())
    
    if not has_issues:
        st.success("✅ Aucune incohérence détectée ! Vos règles sont propres.")
    else:
        # 1. Conflicts
        if issues['conflicts']:
            st.error(f"⚠️ **{len(issues['conflicts'])} Conflits majeurs** (Même pattern, catégories différentes)")
            for conflict in issues['conflicts']:
                with st.expander(f"❌ '{conflict['pattern']}' → {', '.join(conflict['categories'])}"):
                    st.write(conflict['message'])
                    st.warning("Il est recommandé de supprimer ces règles et d'en recréer une unique.")
                    # We could add specific fix buttons here later
        
        # 2. Duplicates
        if issues['duplicates']:
            st.warning(f"♻️ **{len(issues['duplicates'])} Doublons** (Même pattern, même catégorie)")
            for dup in issues['duplicates']:
                st.markdown(f"- **{dup['pattern']}** ({dup['category']}) : _Redondant_")

        # 3. Overlaps
        if issues['overlaps']:
            st.info(f"ℹ️ **{len(issues['overlaps'])} Chevauchements** (Un pattern est inclus dans un autre)")
            for ov in issues['overlaps']:
                st.caption(f"Le pattern `{ov['shorter_pattern']}` ({ov['shorter_category']}) est inclus dans `{ov['longer_pattern']}` ({ov['longer_category']})")

        # 4. Vague
        if issues['vague']:
            st.warning(f"❓ **{len(issues['vague'])} Patterns vagues** (Risque de faux positifs)")
            st.write(", ".join([f"`{v['pattern']}`" for v in issues['vague']]))

st.divider()


st.header("🎯 Budgets Mensuels")
st.markdown("Définissez vos objectifs de dépenses mensuelles par catégorie.")

# Load existing budgets
budgets_df = get_budgets()
budget_map = dict(zip(budgets_df['category'], budgets_df['amount']))

CATEGORIES = get_categories()

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

from modules.ui.layout import render_app_info
render_app_info()
