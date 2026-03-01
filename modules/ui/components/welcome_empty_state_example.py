"""
Exemple d'utilisation du composant WelcomeEmptyState.

Ce fichier montre différentes façons d'utiliser le composant d'accueil.
À intégrer dans une page Streamlit (par exemple app.py ou pages/3_Synthèse.py).
"""

import streamlit as st

# Import du composant
from modules.ui.components.welcome_empty_state import (
    WelcomeEmptyState,
    render_welcome_empty_state,
)


def example_1_basic_usage():
    """Exemple 1: Utilisation basique avec les valeurs par défaut."""
    st.subheader("Exemple 1: Utilisation basique")
    
    WelcomeEmptyState.render()


def example_2_customized():
    """Exemple 2: Personnalisation complète."""
    st.subheader("Exemple 2: Personnalisation")
    
    WelcomeEmptyState.render(
        title="🎉 Bienvenue !",
        subtitle="Votre nouveau tableau de bord financier",
        message="Importez vos premières transactions pour découvrir toutes les fonctionnalités.",
        primary_action_text="🚀 Commencer maintenant",
        primary_action_link="pages/1_Opérations.py",
        secondary_action_text="❓ Besoin d'aide",
        secondary_action_link="https://docs.example.com/guide",
        show_steps=True,
        accent_color="#6366F1",  # Indigo
    )


def example_3_with_callbacks():
    """Exemple 3: Utilisation avec des callbacks Python."""
    st.subheader("Exemple 3: Avec callbacks Python")
    
    def on_primary_click():
        st.session_state["show_import_modal"] = True
        st.toast("Ouverture du modal d'import...")
    
    def on_secondary_click():
        st.session_state["show_help"] = True
    
    WelcomeEmptyState.render(
        title="👋 Hello !",
        subtitle="Prêt à gérer vos finances ?",
        primary_action_text="📥 Importer",
        primary_callback=on_primary_click,
        secondary_action_text="ℹ️ Aide",
        secondary_callback=on_secondary_click,
    )


def example_4_custom_steps():
    """Exemple 4: Étapes personnalisées."""
    st.subheader("Exemple 4: Étapes personnalisées")
    
    custom_steps = [
        ("📱", "Connectez votre banque"),
        ("🔐", "Sécurisez vos données"),
        ("📊", "Analysez vos dépenses"),
        ("🎯", "Définissez vos objectifs"),
    ]
    
    WelcomeEmptyState.render(
        title="🏦 Bienvenue !",
        subtitle="Configuration initiale requise",
        message="Suivez ces étapes pour configurer votre espace financier personnel.",
        steps=custom_steps,
        accent_color="#F59E0B",  # Amber
    )


def example_5_no_steps():
    """Exemple 5: Sans la section étapes."""
    st.subheader("Exemple 5: Sans étapes")
    
    WelcomeEmptyState.render(
        title="🌟 C'est parti !",
        subtitle="Votre espace est prêt",
        show_steps=False,
    )


def example_6_quick_function():
    """Exemple 6: Fonction utilitaire rapide."""
    st.subheader("Exemple 6: Fonction utilitaire")
    
    # Utilisation de la fonction rapide
    render_welcome_empty_state(
        title="💰 Gérez votre argent",
        subtitle="Suivi intelligent de vos finances",
    )


# Page d'exemple Streamlit
if __name__ == "__main__":
    st.set_page_config(
        page_title="WelcomeEmptyState - Exemples",
        page_icon="👋",
        layout="centered",
    )
    
    st.title("👋 WelcomeEmptyState - Exemples d'utilisation")
    st.markdown("""
    Ce fichier démontre différentes façons d'utiliser le composant `WelcomeEmptyState`.
    
    ### Installation
    ```python
    from modules.ui.components.welcome_empty_state import WelcomeEmptyState
    ```
    """)
    
    st.divider()
    
    # Sélecteur d'exemple
    example = st.selectbox(
        "Choisir un exemple",
        [
            "1. Utilisation basique (défaut)",
            "2. Personnalisation complète",
            "3. Avec callbacks Python",
            "4. Étapes personnalisées",
            "5. Sans étapes",
            "6. Fonction utilitaire",
        ],
    )
    
    st.divider()
    
    # Afficher l'exemple sélectionné
    if example.startswith("1"):
        example_1_basic_usage()
    elif example.startswith("2"):
        example_2_customized()
    elif example.startswith("3"):
        example_3_with_callbacks()
    elif example.startswith("4"):
        example_4_custom_steps()
    elif example.startswith("5"):
        example_5_no_steps()
    elif example.startswith("6"):
        example_6_quick_function()
