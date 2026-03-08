"""
Configuration des paramètres de détection des transferts.

Permet de configurer les patterns utilisés pour détecter automatiquement :
- Les virements internes (entre mes comptes)
- Les contributions partenaires (apports externes)
"""

import streamlit as st

from modules.db.settings import (
    get_internal_transfer_targets,
    get_partner_contribution_patterns,
    set_internal_transfer_targets,
    set_partner_contribution_patterns,
)
from modules.transfer_detection import get_transfer_summary
from modules.ui.feedback import toast_success


def render_transfer_settings():
    """
    Rend la section de configuration des transferts.
    """
    st.subheader("🔄 Détection des Transferts", divider="blue")
    
    st.markdown("""
    Configurez les mots-clés utilisés pour détecter automatiquement les transferts d'argent.
    Ces paramètres permettent d'exclure les mouvements internes de vos statistiques de revenus et dépenses.
    """)
    
    # Récupère les valeurs actuelles
    current_internal = get_internal_transfer_targets()
    current_partner = get_partner_contribution_patterns()
    
    # Colonnes pour les deux types de patterns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💼 Virements Internes")
        st.caption("Mots-clés pour identifier les transferts entre VOS comptes (A ↔ B)")
        
        internal_text = st.text_area(
            "Patterns (séparés par des virgules)",
            value=", ".join(current_internal),
            help="Exemple: AURELIEN, DUO, JOINT, EPARGNE, LDDS",
            key="internal_patterns_input",
        )
        
        st.info("""
        📝 **Exemples de libellés détectés:**
        - "Virement de AURELIEN"
        - "Virement vers COMPTE JOINT"
        """)
    
    with col2:
        st.markdown("#### 🤝 Contributions Partenaire")
        st.caption("Mots-clés pour identifier les apports externes (C → B)")
        
        partner_text = st.text_area(
            "Patterns (séparés par des virgules)",
            value=", ".join(current_partner),
            help="Exemple: ELISE, COMPAGNE, PARTENAIRE",
            key="partner_patterns_input",
        )
        
        st.info("""
        📝 **Exemples de libellés détectés:**
        - "Virement de ELISE"
        - "Virement PARTENAIRE"
        """)
    
    # Boutons d'action
    col_save, col_preview = st.columns([1, 1])
    
    with col_save:
        if st.button("💾 Sauvegarder les paramètres", use_container_width=True, type="primary"):
            # Parse et sauvegarde les patterns
            new_internal = [p.strip() for p in internal_text.split(",") if p.strip()]
            new_partner = [p.strip() for p in partner_text.split(",") if p.strip()]
            
            set_internal_transfer_targets(new_internal)
            set_partner_contribution_patterns(new_partner)
            
            toast_success("Paramètres de détection sauvegardés !")
            st.rerun()
    
    with col_preview:
        if st.button("👁️ Voir le résumé actuel", use_container_width=True):
            st.session_state["show_transfer_summary"] = True
    
    # Affiche le résumé si demandé
    if st.session_state.get("show_transfer_summary", False):
        render_transfer_summary()
    
    # Section d'information
    with st.expander("ℹ️ Comment fonctionne la détection ?"):
        st.markdown("""
        ### Règles de détection
        
        La détection des transferts se fait en analysant le **libellé** de chaque transaction :
        
        1. **Virements Internes** (prioritaire)
           - Détectés si le libellé contient un des mots-clés internes
           - **Ne sont PAS comptés** dans les revenus ni les dépenses
           - Exemple: Transfert entre votre compte perso et votre compte joint
        
        2. **Contributions Partenaire**
           - Détectées si le libellé contient un des mots-clés partenaire
           - **Ne sont PAS comptées** comme revenus (car ce ne sont pas VOS revenus)
           - Exemple: Virement de votre compagne/compagnon vers le compte joint
        
        ### Impact sur les statistiques
        
        | Type | Compté dans Revenus | Compté dans Dépenses |
        |------|---------------------|---------------------|
        | Salaire, Aides | ✅ Oui | ❌ Non |
        | Virement Interne | ❌ Non | ❌ Non |
        | Contribution Partenaire | ❌ Non | ❌ Non |
        | Courses, Factures | ❌ Non | ✅ Oui |
        """)


def render_transfer_summary():
    """
    Affiche un résumé des transferts détectés.
    """
    st.divider()
    st.markdown("#### 📊 Résumé des transferts détectés")
    
    summary = get_transfer_summary()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Virements Internes",
            f"{len(summary['internal_transfers'])} transactions",
        )
    
    with col2:
        st.metric(
            "Contributions Partenaire",
            f"{len(summary['partner_contributions'])} transactions",
        )
    
    with col3:
        total_excluded = abs(summary['total_internal']) + abs(summary['total_contributions'])
        st.metric(
            "Montant total exclu",
            f"{total_excluded:,.2f} €",
        )
    
    # Détails des transferts internes
    if not summary['internal_transfers'].empty:
        with st.expander("🔍 Voir les virements internes"):
            df_display = summary['internal_transfers'][['date', 'label', 'amount', 'account_label']].copy()
            df_display['amount'] = df_display['amount'].apply(lambda x: f"{x:,.2f} €")
            st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Détails des contributions
    if not summary['partner_contributions'].empty:
        with st.expander("🔍 Voir les contributions partenaire"):
            df_display = summary['partner_contributions'][['date', 'label', 'amount', 'account_label']].copy()
            df_display['amount'] = df_display['amount'].apply(lambda x: f"{x:,.2f} €")
            st.dataframe(df_display, use_container_width=True, hide_index=True)


def render_transfer_detection_tool():
    """
    Outil de test de détection sur un libellé.
    """
    with st.expander("🧪 Tester la détection sur un libellé"):
        test_label = st.text_input(
            "Libellé à tester",
            placeholder="Ex: Virement de ELISE vers COMPTE JOINT",
            key="test_transfer_label",
        )
        
        if test_label:
            from modules.transfer_detection import detect_transfer_type
            
            result = detect_transfer_type(test_label)
            
            if result:
                st.success(f"✅ Détecté comme : **{result}**")
            else:
                st.info("ℹ️ Aucun transfert détecté (sera traité comme une transaction normale)")
