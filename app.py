import os
import sys
from datetime import date
from pathlib import Path

import streamlit as st

from modules.encryption import get_encryption

# --- ERROR TRACKING & SECURITY INITIALIZATION ---
from modules.error_tracking import init_error_tracking
from modules.logger import logger

# Initialize Sentry if DSN configured
if os.getenv("SENTRY_DSN"):
    init_error_tracking(
        dsn=os.getenv("SENTRY_DSN"), environment=os.getenv("ENVIRONMENT", "production")
    )

# Initialize encryption
encryption = get_encryption()
if encryption.is_enabled():
    logger.info("🔐 Encryption enabled for sensitive fields")
else:
    logger.warning("⚠️  Encryption disabled - add ENCRYPTION_KEY to .env for production")

from modules.db.migrations import init_db
from modules.db.stats import get_global_stats, is_app_initialized
from modules.gamification.streaks import record_daily_login, render_streak_badge

# ============================================================
# SYSTÈME DE NOTIFICATIONS V3
# ============================================================
from modules.notifications import DetectorRegistry, NotificationService
from modules.notifications.ui import render_notification_badge as render_notification_badge_v3
from modules.ui import card_kpi, display_flash_messages, load_css
from modules.ui.components.daily_widget import render_daily_widget, render_quick_stats_row
from modules.ui.components.onboarding_modal import render_onboarding_modal, should_show_onboarding
from modules.ui.components.quick_actions import render_quick_actions_grid
from modules.ui.components.smart_actions import render_smart_actions
from modules.ui.feedback import toast_success
from modules.ui.theme import ThemeManager, init_theme, render_theme_toggle

# Ajouter le répertoire parent au path (utiliser append pour éviter le shadowing)
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.append(project_root)


# Imports Design System
try:
    from modules.ui import apply_vibe_theme  # noqa: F401

    DESIGN_SYSTEM_AVAILABLE = True
except ImportError:
    DESIGN_SYSTEM_AVAILABLE = False

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MyFinance Companion",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# PWA Support - Add meta tags for mobile
st.markdown(
    """
    <meta name="theme-color" content="#1E88E5">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="MyFinance">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="manifest" href="/assets/manifest.json">
""",
    unsafe_allow_html=True,
)

# Register Service Worker for PWA
st.markdown(
    """
    <script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('assets/service-worker.js')
            .then((registration) => {
                console.log('[PWA] Service Worker registered:', registration.scope);
            })
            .catch((error) => {
                console.log('[PWA] Service Worker registration failed:', error);
            });
    }
    </script>
""",
    unsafe_allow_html=True,
)

load_css()

# Initialiser et appliquer le thème v5.5
init_theme()
ThemeManager.apply_theme_css()

# Afficher le toggle de thème dans la sidebar
render_theme_toggle()
try:
    # Test d'accès critique (vérifie si l'OS bloque l'accès au dossier Data et logs)
    if os.path.exists("Data"):
        os.listdir("Data")

    init_db()

    # Initialiser les analytics
    from modules.analytics import init_analytics

    init_analytics()

except PermissionError:
    st.error("### 🛑 Sécurité macOS : Accès refusé")
    st.error(
        "L'application ne peut pas accéder aux données. Vérifiez les permissions "
        "dans **Réglages Système macOS > Confidentialité et sécurité > "
        "Fichiers et dossiers**."
    )
    logger.error("PermissionError: Accès refusé au dossier Data")
    st.stop()
except Exception:
    st.error("### 🛑 Erreur fatale au démarrage")
    st.error("Impossible d'initialiser l'application. Veuillez réessayer ou contacter le support.")
    logger.exception("Fatal startup error")
    st.stop()

# --- SESSION STATE INITIALIZATION (AVANT toute utilisation) ---
if "default_account_name" not in st.session_state:
    st.session_state["default_account_name"] = None
if "onboarding_complete" not in st.session_state:
    st.session_state["onboarding_complete"] = None
if "onboarding_dismissed" not in st.session_state:
    st.session_state["onboarding_dismissed"] = None
if "onboarding_step" not in st.session_state:
    st.session_state["onboarding_step"] = None

# --- DASHBOARD CLEANUP (Auto-repair on startup) ---
# Exécuté une seule fois par session pour éviter les ralentissements
if "startup_cleanup_done" not in st.session_state:
    try:
        from modules.db.dashboard_cleanup import run_startup_cleanup

        cleanup_result = run_startup_cleanup()
        if cleanup_result.widgets_fixed > 0 or cleanup_result.widgets_removed > 0:
            logger.info(f"Dashboard auto-cleanup: {cleanup_result.message}")
        st.session_state["startup_cleanup_done"] = True
    except Exception as e:
        logger.warning(f"Dashboard cleanup failed (non-critical): {e}")

# --- AUTOMATED MAINTENANCE (Weekly Cleanup) ---
# Exécuté une seule fois par session pour éviter les ralentissements
if "maintenance_checked" not in st.session_state:
    try:
        from modules.db.maintenance import check_and_perform_maintenance

        check_and_perform_maintenance()
        st.session_state["maintenance_checked"] = True
    except Exception as e:
        logger.warning(f"Automated maintenance failed (non-critical): {e}")

# Système de notifications V3 - exécuté une fois par jour maximum
# Utiliser une clé session_state pour tracker la dernière exécution

# Initialiser la clé si nécessaire
if "notifications_v3_last_run" not in st.session_state:
    st.session_state["notifications_v3_last_run"] = None

# Vérifier si on doit exécuter les détecteurs (une fois par jour)
today_str = date.today().isoformat()
should_run_detectors = st.session_state["notifications_v3_last_run"] != today_str

# Initialiser le service V3
notification_service_v3 = NotificationService()

if should_run_detectors:
    try:
        registry = DetectorRegistry(notification_service_v3)
        detector_stats = registry.run_all()
        st.session_state["notifications_v3_last_run"] = today_str
        logger.info(f"Notifications V3 - Détecteurs exécutés: {detector_stats}")
    except Exception as e:
        logger.warning(f"Notifications V3 - Erreur lors de l'exécution des détecteurs: {e}")

# Track daily login for streak (une fois par session)
if "daily_login_recorded" not in st.session_state:
    record_daily_login()
    st.session_state["daily_login_recorded"] = True

# Afficher le badge de notification et le streak dans la sidebar
# Utiliser le nouveau système V3 avec le service
render_notification_badge_v3(notification_service_v3)
render_streak_badge()

# Afficher les messages flash en attente
display_flash_messages()

# --- ONBOARDING MODAL ---
if should_show_onboarding():
    render_onboarding_modal()

# --- MAIN LOGIC ---

if not is_app_initialized():
    # === ONBOARDING MODE - Invitation à compléter la configuration ===
    st.title("👋 Bienvenue sur MyFinance Companion")
    st.markdown("### Votre assistant personnel pour une gestion financière sereine.")

    st.info("""
    **Pourquoi cette application ?**
    - 🔒 **Données locales** : Vos comptes ne quittent jamais votre ordinateur.
    - 🧠 **Intelligence Artificielle** : Catégorisation automatique et conseils personnalisés.
    - 📊 **Tableaux de bord** : Visualisez où part votre argent.
    """)

    st.divider()

    # Invitation à compléter la configuration
    st.warning("⚠️ Configuration requise pour commencer")
    st.markdown("Pour utiliser l'application, veuillez compléter la configuration initiale.")

    if st.button(
        "🚀 Compléter la configuration",
        type="primary",
        use_container_width=True,
        key="btn_complete_onboarding",
    ):
        st.session_state["onboarding_dismissed"] = False
        st.session_state["onboarding_step"] = 1
        st.rerun()

else:
    # === DASHBOARD MODE ===
    stats = get_global_stats()

    st.title("🏠 Accueil")

    # Check if user has data
    if stats.get("total_transactions", 0) == 0:
        # Empty state for new users - WelcomeEmptyState
        from modules.ui.components.welcome_empty_state import WelcomeEmptyState

        WelcomeEmptyState.render(
            title="👋 Bonjour !",
            subtitle="Bienvenue dans votre espace financier",
            message="Commencez par importer vos relevés bancaires pour visualiser vos "
            "finances, suivre vos budgets et atteindre vos objectifs d'épargne.",
            primary_action_text="📥 Importer mes relevés",
            primary_action_link="pages/01_Import.py",
            secondary_action_text="📖 Voir le guide",
            secondary_action_link=None,
            show_steps=True,
        )
    else:
        # 🆕 DAILY WIDGET - Crée l'habitude quotidienne
        render_daily_widget()

        # 🆕 QUICK STATS ROW
        render_quick_stats_row()

        st.divider()

        # 1. Global KPIs
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            card_kpi(
                "Transactions Totales",
                f"{stats.get('total_transactions', 0)}",
                trend="Données",
                trend_color="positive",
            )
        with c2:
            last_date = stats.get("last_import")
            last_str = last_date if last_date else "Jamais"
            card_kpi("Dernier Import", last_str, trend="Date", trend_color="positive")
        with c3:
            sav = stats.get("current_month_savings", 0)
            color = "positive" if sav >= 0 else "negative"
            card_kpi(
                "Épargne du Mois",
                f"{sav:+,.0f} €",
                trend=f"{stats.get('current_month_rate', 0):.1f}%",
                trend_color=color,
            )
        with c4:
            st.write("")  # Placeholder or shortcut
            if st.button(
                "📥 Nouvelles Opérations",
                use_container_width=True,
                type="primary",
                key="btn_new_operations",
            ):
                toast_success("Ouverture de la page Opérations...", icon="📥")
                st.switch_page("pages/01_Import.py")
            if st.button("📊 Voir la Synthèse", use_container_width=True, key="btn_view_synthesis"):
                toast_success("Ouverture du tableau de bord...", icon="📊")
                st.switch_page("pages/02_Dashboard.py")

        st.divider()

        # 2. Key Actions & Status
        c_left, c_right = st.columns([2, 1])

        with c_left:
            # Nouvelles actions rapides avec popups
            render_quick_actions_grid()

        with c_right:
            # 🆕 SMART ACTIONS - remplace le bouton "Revoir le guide" inutile
            render_smart_actions()

    # Navigation vers Test_Dashboard V5.5 (Beta)
    from modules.constants import TEST_DASHBOARD_ENABLED

    if TEST_DASHBOARD_ENABLED:
        st.sidebar.divider()
        st.sidebar.markdown("### 🆕 Nouveau")
        if st.sidebar.button(
            "✨ Tester le nouveau dashboard",
            use_container_width=True,
            type="secondary",
            help="Découvrez la nouvelle interface V5.5 avec design FinCouple",
        ):
            st.switch_page("pages/02_Dashboard.py")

    st.sidebar.success("✅ Application Initialisée")

    # Show App Info in Sidebar
    from modules.ui.layout import render_app_info

    render_app_info()
