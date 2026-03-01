"""Dashboard Empty State - État vide avec onboarding.

Usage:
    from modules.ui.v5_5.dashboard import render_dashboard_empty
    
    render_dashboard_empty(user_name="Alex")
"""

from typing import Optional
import streamlit as st

from modules.ui.v5_5.theme import apply_light_theme, LightColors
from modules.ui.v5_5.components.dashboard_header import DashboardHeader


def render_dashboard_empty(user_name: Optional[str] = None) -> None:
    """Affiche le dashboard quand aucune transaction n'existe.
    
    Affiche:
    - Header avec "Bonjour [Nom]"
    - Section "Vue d'ensemble" (vide)
    - Card onboarding avec 3 étapes
    - Bouton "Voir le guide"
    
    Args:
        user_name: Nom de l'utilisateur
    """
    # Appliquer thème
    apply_light_theme()
    
    # 1. Header (simplifié, sans sélecteur)
    DashboardHeader.render_simple(
        user_name=user_name,
        subtitle="Commencez votre parcours financier"
    )
    
    # 2. Section Vue d'ensemble
    st.markdown("""
    <h2 style="
        font-size: 1.25rem;
        font-weight: 600;
        color: #1F2937;
        margin-top: 2rem;
        margin-bottom: 1rem;
    ">
        📊 Vue d'ensemble
    </h2>
    """, unsafe_allow_html=True)
    
    # 3. Card onboarding
    _render_onboarding_card()
    
    # 4. Bouton guide
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📖 Voir le guide", use_container_width=True, key="empty_guide_btn"):
            _show_guide_modal()
    
    # Footer
    st.divider()
    st.caption("FinancePerso V5.5 - En attente de données")


def _render_onboarding_card() -> None:
    """Rend la card avec les 3 étapes d'onboarding."""
    
    st.markdown("""
    <style>
    .v5-onboarding-container {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
    
    .v5-onboarding-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 2rem;
        max-width: 500px;
        width: 100%;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .v5-onboarding-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .v5-step {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1.25rem;
    }
    
    .v5-step:last-child {
        margin-bottom: 0;
    }
    
    .v5-step-number {
        background: #10B981;
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.875rem;
        margin-right: 1rem;
        flex-shrink: 0;
    }
    
    .v5-step-text {
        color: #374151;
        font-size: 1rem;
        line-height: 1.5;
        padding-top: 0.25rem;
    }
    
    .v5-step-highlight {
        font-weight: 600;
        color: #10B981;
    }
    </style>
    
    <div class="v5-onboarding-container">
        <div class="v5-onboarding-card">
            <div class="v5-onboarding-title">💡 POUR BIEN DÉMARRER</div>
            
            <div class="v5-step">
                <span class="v5-step-number">1</span>
                <div class="v5-step-text">
                    Importez vos relevés bancaires au <span class="v5-step-highlight">format CSV</span>
                </div>
            </div>
            
            <div class="v5-step">
                <span class="v5-step-number">2</span>
                <div class="v5-step-text">
                    Laissez l'<span class="v5-step-highlight">IA catégoriser</span> automatiquement vos transactions
                </div>
            </div>
            
            <div class="v5-step">
                <span class="v5-step-number">3</span>
                <div class="v5-step-text">
                    Validez et <span class="v5-step-highlight">visualisez vos insights</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _show_guide_modal() -> None:
    """Affiche le guide d'onboarding dans un dialog."""
    
    @st.dialog("📖 Guide de démarrage", width="large")
    def guide_dialog():
        st.markdown("""
        ### Comment utiliser FinancePerso
        
        #### 1. 📥 Importez vos relevés
        
        Connectez-vous à votre espace client bancaire et téléchargez votre relevé 
        au format CSV. La plupart des banques proposent cette exportation.
        
        **Banques supportées:**
        - BNP Paribas
        - Société Générale
        - Crédit Agricole
        - Banque Postale
        - Et +50 autres...
        
        ---
        
        #### 2. 🤖 Laissez l'IA catégoriser
        
        Notre intelligence artificielle analyse automatiquement chaque transaction :
        - Reconnaissance des commerces
        - Catégorisation par type de dépense
        - Détection des revenus réguliers
        
        **Précision:** Plus vous validez, plus l'IA devient précise !
        
        ---
        
        #### 3. ✏️ Validez les suggestions
        
        Parcourez les transactions proposées et validez ou corrigez les catégories.
        Cette étape est cruciale pour des statistiques fiables.
        
        ---
        
        #### 4. 📊 Visualisez vos finances
        
        Une fois vos données importées, accédez à :
        - Dashboard avec KPIs en temps réel
        - Suivi budgétaire par catégorie
        - Prédictions et conseils d'épargne
        - Analyses tendances
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Commencer l'import", use_container_width=True, type="primary"):
                st.switch_page("pages/1_Opérations.py")
        
        with col2:
            if st.button("✅ Fermer", use_container_width=True):
                st.rerun()
    
    guide_dialog()


def render_onboarding_mini() -> None:
    """Version compacte de l'onboarding (pour sidebar ou footer)."""
    
    st.markdown("""
    <div style="
        background: #F0FDF4;
        border: 1px solid #10B981;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    ">
        <div style="font-weight: 600; color: #065F46; margin-bottom: 0.5rem;">
            💡 Premiers pas
        </div>
        <div style="font-size: 0.875rem; color: #047857;">
            Importez vos relevés CSV pour visualiser vos finances
        </div>
    </div>
    """, unsafe_allow_html=True)
