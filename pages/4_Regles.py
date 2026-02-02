"""
Page: Règles & Mémoire

Gestion des règles de catégorisation automatique, budgets mensuels et audit IA.
Cette page utilise des fragments Streamlit pour optimiser les performances.

Architecture modulaire:
    - modules/ui/rules/rule_manager: Gestion CRUD des règles
    - modules/ui/rules/rule_audit: Analyse IA d'intégrité
    - modules/ui/rules/budget_manager: Gestion des budgets
"""

import streamlit as st

# Page configuration
st.set_page_config(page_title="Règles & Mémoire", page_icon="🧠", layout="wide")

# Imports - organisés selon les conventions du projet
# 1. Standard library
# (none needed)

# 2. Third-party imports
# (streamlit déjà importé)

# 3. Local imports
from modules.ui import load_css
from modules.ui.layout import render_app_info
from modules.ui.feedback import render_scroll_to_top
from modules.ui.rules import (
    render_rule_list,
    render_add_rule_form,
    render_audit_section,
    render_budget_section,
)
from modules.ui.feedback import (
    toast_success, toast_error, toast_warning, toast_info,
    show_success, show_error, show_warning, show_info
)
from modules.db.migrations import init_db
from modules.db.audit import auto_fix_common_inconsistencies
from modules.db.rules import get_learning_rules
from modules.ai.rules_auditor import analyze_rules_integrity
from modules.logger import logger

# Initialize
load_css()
init_db()  # Ensure migrations are applied

# =============================================================================
# PAGE HEADER
# =============================================================================
st.title("🧠 Mémoire de l'assistant")
st.markdown("Gérez les règles de catégorisation automatique, auditez leur qualité et définissez vos budgets mensuels.")

# =============================================================================
# QUICK ACTIONS BAR
# =============================================================================
def render_quick_actions():
    """Render the quick actions bar with apply button and health score."""
    rules_df = get_learning_rules()
    
    if rules_df.empty:
        return
    
    cols = st.columns([2, 1, 1])
    
    with cols[0]:
        st.markdown(f"**{len(rules_df)}** règles actives")
    
    with cols[1]:
        # Quick health score (lightweight)
        if 'quick_audit_score' not in st.session_state:
            try:
                audit = analyze_rules_integrity(rules_df)
                st.session_state['quick_audit_score'] = audit['score']
            except Exception:
                st.session_state['quick_audit_score'] = 100
        
        score = st.session_state.get('quick_audit_score', 100)
        score_color = "green" if score > 80 else "orange" if score > 50 else "red"
        st.markdown(f"Santé : :{score_color}[**{score}%**]")
    
    with cols[2]:
        help_text = "Relance la catégorisation automatique sur toutes les transactions en attente ou inconnues"
        if st.session_state.get('quick_audit_score', 100) < 50:
            help_text += " ⚠️ Vos règles ont des problèmes de santé, l'application pourrait être imprécise."
        
        if st.button("🪄 Appliquer les règles", help=help_text, use_container_width=True, type="secondary", key='button_88'):
            # Check for critical issues before applying
            try:
                audit = analyze_rules_integrity(rules_df)
                if audit.get('conflicts'):
                    st.warning(
                        f"🚨 **Attention** : {len(audit['conflicts'])} conflit(s) majeur(s) détecté(s). "
                        "L'application des règles risque d'être incohérente.",
                        icon="⚠️"
                    )
                    
                    # Show conflicts details with actions
                    st.markdown("**Détails des conflits :**")
                    for conflict in audit['conflicts'][:3]:  # Show first 3
                        cols = st.columns([3, 1])
                        with cols[0]:
                            st.markdown(f"- `{conflict['pattern']}` → {', '.join(conflict['categories'])}")
                        with cols[1]:
                            if st.button("🗑️ Supprimer", key=f"quick_del_{conflict['ids'][0]}"):
                                from modules.db.rules import delete_learning_rule
                                for rule_id in conflict['ids']:
                                    delete_learning_rule(rule_id)
                                st.success("✅ Règles supprimées")
                                st.rerun()
                    
                    # Option to go to audit tab
                    if st.button("🔍 Voir l'audit complet", type="primary"):
                        st.session_state['rules_active_tab'] = 'audit'
                        st.rerun()
                    
                    st.divider()
                    st.markdown("*Vous pouvez corriger les conflits ci-dessus ou continuer quand même.*")
                
                with st.spinner("Application des règles en cours..."):
                    count = auto_fix_common_inconsistencies()
                    if count > 0:
                        toast_success(f"✅ {count} transactions mises à jour !", icon="🪄")
                        show_success(f"{count} transactions ont été recatégorisées avec succès")
                    else:
                        toast_info("Aucune transaction n'a été modifiée (déjà à jour)", icon="ℹ️")
                        show_info("Toutes les transactions sont déjà à jour")
            except Exception as e:
                logger.error(f"Error applying rules: {e}")
                toast_error(f"Erreur lors de l'application des règles", icon="❌")
                show_error(f"Erreur lors de l'application des règles: {e}")

# =============================================================================
# MAIN PAGE LAYOUT - NAVIGATION PAR ONGLETS CONTRÔLABLE
# =============================================================================

# Initialize active tab in session state
if 'rules_active_tab' not in st.session_state:
    st.session_state['rules_active_tab'] = 'rules'

# Quick actions bar
render_quick_actions()
st.divider()

# Tab selector using radio styled as tabs (allows programmatic switching)
tab_options = {
    'rules': '📋 Règles de catégorisation',
    'audit': '🕵️ Audit IA',
    'budgets': '🎯 Budgets mensuels'
}

# CSS to make radio look like tabs
st.markdown("""
<style>
    div[data-testid="stHorizontalBlock"] div[data-testid="column"] [data-testid="stRadio"] {
        background-color: transparent;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"] [data-testid="stRadio"] > label {
        display: none;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"] [data-testid="stRadio"] div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        gap: 0;
        border-bottom: 2px solid #e0e0e0;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"] [data-testid="stRadio"] div[role="radiogroup"] label {
        padding: 0.75rem 1.5rem;
        margin: 0;
        border-bottom: 3px solid transparent;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.2s;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background-color: rgba(102, 126, 234, 0.1);
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="column"] [data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] input:checked + div {
        border-bottom: 3px solid #667eea;
        color: #667eea;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Tab selector
cols = st.columns([1, 1, 1, 3])
with cols[0]:
    if st.button('📋 Règles', use_container_width=True, 
                 type='primary' if st.session_state['rules_active_tab'] == 'rules' else 'secondary',
                 key='tab_btn_rules'):
        st.session_state['rules_active_tab'] = 'rules'
        st.rerun()
with cols[1]:
    if st.button('🕵️ Audit', use_container_width=True,
                 type='primary' if st.session_state['rules_active_tab'] == 'audit' else 'secondary',
                 key='tab_btn_audit'):
        st.session_state['rules_active_tab'] = 'audit'
        st.rerun()
with cols[2]:
    if st.button('🎯 Budgets', use_container_width=True,
                 type='primary' if st.session_state['rules_active_tab'] == 'budgets' else 'secondary',
                 key='tab_btn_budgets'):
        st.session_state['rules_active_tab'] = 'budgets'
        st.rerun()

st.divider()

# =============================================================================
# TAB CONTENT
# =============================================================================

active_tab = st.session_state.get('rules_active_tab', 'rules')

# TAB 1: RULES MANAGEMENT
if active_tab == 'rules':
    st.markdown("### Ajouter une nouvelle règle")
    render_add_rule_form()
    
    st.divider()
    st.markdown("### Liste des règles")
    render_rule_list()

# TAB 2: AI AUDIT
elif active_tab == 'audit':
    render_audit_section()

# TAB 3: BUDGETS
elif active_tab == 'budgets':
    render_budget_section()

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
render_scroll_to_top()
render_app_info()
