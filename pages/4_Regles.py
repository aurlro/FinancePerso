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
                        "L'application des règles risque d'être incohérente. Vérifiez l'audit ci-dessous.",
                        icon="⚠️"
                    )
                
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
# MAIN PAGE LAYOUT
# =============================================================================

# Quick actions bar
render_quick_actions()
st.divider()

# Create tabs for better organization
tab_rules, tab_audit, tab_budgets = st.tabs([
    "📋 Règles de catégorisation",
    "🕵️ Audit IA",
    "🎯 Budgets mensuels"
])

# =============================================================================
# TAB 1: RULES MANAGEMENT
# =============================================================================
with tab_rules:
    st.markdown("### Ajouter une nouvelle règle")
    render_add_rule_form()
    
    st.divider()
    st.markdown("### Liste des règles")
    render_rule_list()

# =============================================================================
# TAB 2: AI AUDIT
# =============================================================================
with tab_audit:
    render_audit_section()

# =============================================================================
# TAB 3: BUDGETS
# =============================================================================
with tab_budgets:
    render_budget_section()

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
render_scroll_to_top()
render_app_info()
