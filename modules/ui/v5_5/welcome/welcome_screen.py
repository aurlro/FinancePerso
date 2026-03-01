"""Welcome Screen - Écran d'accueil V5.5.

Affiche le WelcomeCard si aucune transaction n'existe,
ou redirige vers le dashboard si des données sont présentes.

Usage:
    from modules.ui.v5_5.welcome import render_welcome_screen
    
    render_welcome_screen()
"""

from typing import Optional
import streamlit as st

from modules.ui.v5_5.components.welcome_card import WelcomeCard
from modules.db.transactions import get_transactions_count


def render_welcome_screen(
    user_name: Optional[str] = None,
    redirect_to_dashboard: bool = True,
) -> None:
    """Affiche l'écran d'accueil ou redirige vers le dashboard.
    
    Cette fonction vérifie si l'utilisateur a des transactions:
    - Si NON: Affiche le WelcomeCard avec CTA import/guide
    - Si OUI: Redirige vers le dashboard (optionnel)
    
    Args:
        user_name: Nom de l'utilisateur (affiché dans le titre)
        redirect_to_dashboard: Si True, redirige automatiquement vers 
                              le dashboard quand des données existent
    
    Usage:
        # Dans app.py ou page d'accueil
        from modules.ui.v5_5.welcome import render_welcome_screen
        
        render_welcome_screen(user_name="Alex")
    """
    
    # Vérifier si l'utilisateur a des transactions
    try:
        transaction_count = get_transactions_count()
    except Exception as e:
        # En cas d'erreur DB, on affiche le welcome quand même
        transaction_count = 0
        st.warning("⚠️ Impossible de vérifier vos transactions. Veuillez réessayer.")
    
    # Si des données existent et redirection activée
    if transaction_count > 0 and redirect_to_dashboard:
        # Rediriger vers le dashboard
        st.switch_page("pages/3_Synthèse.py")
        return
    
    # Si des données existent mais pas de redirection
    if transaction_count > 0:
        st.info("📊 Vous avez déjà des transactions. [Allez au dashboard](pages/3_Synthèse.py)")
        return
    
    # Afficher le WelcomeCard
    WelcomeCard.render_with_guide_modal(
        on_primary=lambda: _navigate_to_import(),
        user_name=user_name,
    )


def _navigate_to_import() -> None:
    """Navigue vers la page d'import."""
    st.switch_page("pages/1_Opérations.py")


def _navigate_to_dashboard() -> None:
    """Navigue vers le dashboard."""
    st.switch_page("pages/3_Synthèse.py")


def has_transactions() -> bool:
    """Vérifie si l'utilisateur a des transactions.
    
    Returns:
        True si au moins une transaction existe
    
    Usage:
        if has_transactions():
            show_dashboard()
        else:
            show_welcome()
    """
    try:
        return get_transactions_count() > 0
    except Exception:
        return False


def get_user_name() -> Optional[str]:
    """Récupère le nom de l'utilisateur courant.
    
    Returns:
        Nom de l'utilisateur ou None si non défini
    """
    # Essayer de récupérer depuis la session
    if "user_name" in st.session_state:
        return st.session_state.user_name
    
    # Essayer depuis les paramètres couple
    try:
        from modules.couple import get_current_user
        user = get_current_user()
        if user:
            return user.get("name")
    except Exception:
        pass
    
    return None


def render_welcome_or_dashboard(user_name: Optional[str] = None) -> None:
    """Affiche welcome ou dashboard selon les données.
    
    Fonction utilitaire qui combine la logique de détection
    et d'affichage en une seule fonction.
    
    Args:
        user_name: Nom de l'utilisateur
    """
    # Si pas de nom fourni, essayer de le récupérer
    if user_name is None:
        user_name = get_user_name()
    
    # Vérifier les transactions
    if has_transactions():
        # Rediriger vers dashboard
        _navigate_to_dashboard()
    else:
        # Afficher welcome
        render_welcome_screen(user_name=user_name, redirect_to_dashboard=False)
