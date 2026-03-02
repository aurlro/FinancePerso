"""
Module d'onboarding pour guider les nouveaux utilisateurs.
Fournit une expérience de premier lancement fluide.
"""

import streamlit as st

from modules.db.categories import get_categories
from modules.db.transactions import get_all_transactions
from modules.logger import logger


class OnboardingManager:
    """Gère l'onboarding des nouveaux utilisateurs."""

    STEPS = {
        1: "🎯 Configuration initiale",
        2: "📥 Premier import",
        3: "🎉 Prêt à utiliser l'app !",
    }

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self._init_session_state()

    def _init_session_state(self):
        """Initialise les variables de session."""
        if "onboarding_step" not in st.session_state:
            st.session_state["onboarding_step"] = 1
        if "onboarding_completed" not in st.session_state:
            st.session_state["onboarding_completed"] = False

    def is_first_time(self) -> bool:
        """Vérifie si c'est la première utilisation."""
        try:
            transactions = get_all_transactions()
            categories = get_categories()

            # Considéré comme first-time si:
            # - Aucune transaction (DataFrame vide)
            # - ET aucune catégorie personnalisée (liste vide)
            # - ET l'onboarding n'est pas marqué comme complété
            has_no_transactions = (
                transactions.empty if hasattr(transactions, "empty") else len(transactions) == 0
            )
            has_no_categories = (
                len(categories) == 0 if isinstance(categories, list) else categories.empty
            )

            return (has_no_transactions and has_no_categories) and not st.session_state.get(
                "onboarding_completed", False
            )
        except Exception as e:
            logger.error(f"Erreur verification first-time: {e}")
            return False

    def render_welcome(self):
        """Affiche l'écran de bienvenue."""
        st.markdown(
            """
        <style>
        .onboarding-welcome {
            text-align: center;
            padding: 3rem 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 1rem;
            margin-bottom: 2rem;
        }
        .onboarding-welcome h1 {
            color: white !important;
            margin-bottom: 1rem;
        }
        .onboarding-welcome p {
            color: rgba(255,255,255,0.9) !important;
            font-size: 1.2rem;
        }
        </style>
        <div class="onboarding-welcome">
            <h1>🎉 Bienvenue sur FinancePerso !</h1>
            <p>Votre compagnon pour une gestion financière simplifiée et intelligente.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    def render_step_indicator(self):
        """Affiche l'indicateur de progression."""
        current = st.session_state.onboarding_step
        total = len(self.STEPS)

        cols = st.columns(total)
        for i, (step_num, step_name) in enumerate(self.STEPS.items(), 1):
            with cols[i - 1]:
                if step_num < current:
                    st.success(f"✅ Étape {step_num}")
                elif step_num == current:
                    st.info(f"🔄 Étape {step_num}")
                else:
                    st.caption(f"○ Étape {step_num}")

        st.progress(current / total)

    def render_step_1_config(self):
        """Étape 1: Configuration initiale."""
        st.subheader("⚙️ Configuration initiale")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 🏠 Configuration du foyer
            
            Commencez par configurer les membres de votre foyer :
            - Ajoutez votre conjoint/partenaire
            - Ajoutez les membres de votre famille
            - Définissez les associations de cartes
            """)

            if st.button("➕ Ajouter des membres", key="onboarding_add_members"):
                st.switch_page("pages/08_Configuration.py")

        with col2:
            st.markdown("""
            ### 📂 Catégories de dépenses
            
            Personnalisez vos catégories selon vos besoins :
            - Catégories fixes (loyer, assurances)
            - Catégories variables (courses, loisirs)
            - Sous-catégories personnalisées
            """)

            if st.button("⚙️ Configurer les catégories", key="onboarding_config_cats"):
                st.switch_page("pages/08_Configuration.py")

        st.divider()

        col_skip, col_next = st.columns([1, 1])
        with col_skip:
            if st.button("⏭️ Passer cette étape", type="secondary", key="onboarding_skip_step1"):
                st.session_state.onboarding_step = 2
                st.rerun()
        with col_next:
            if st.button("Continuer →", type="primary", key="onboarding_next_step1"):
                st.session_state.onboarding_step = 2
                st.rerun()

    def render_step_2_import(self):
        """Étape 2: Premier import."""
        st.subheader("📥 Importez vos premières transactions")

        st.markdown("""
        ### 🎯 Pourquoi importer vos relevés ?
        
        L'import de vos relevés bancaires permet de :
        - 📊 Visualiser vos dépenses par catégorie
        - 💰 Suivre votre budget en temps réel
        - 🔍 Détecter les anomalies et paiements récurrents
        - 📈 Obtenir des prédictions personnalisées
        """)

        st.info(
            "💡 **Conseil** : Commencez par importer vos relevés des 3 derniers mois "
            "pour avoir une vision complète de vos finances."
        )

        # Zone de drop stylisée
        st.markdown(
            """
        <style>
        .upload-zone {
            border: 3px dashed #4CAF50;
            border-radius: 1rem;
            padding: 3rem;
            text-align: center;
            background: rgba(76, 175, 80, 0.05);
            margin: 2rem 0;
        }
        .upload-zone:hover {
            background: rgba(76, 175, 80, 0.1);
            cursor: pointer;
        }
        </style>
        <div class="upload-zone">
            <h3>📂 Glissez-déposez votre fichier CSV ici</h3>
            <p>Ou cliquez ci-dessous pour sélectionner un fichier</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Le vrai uploader sera ajouté par la page parent
        st.session_state.show_uploader = True

        col_skip, col_next = st.columns([1, 1])
        with col_skip:
            if st.button("⏭️ Passer cette étape", type="secondary", key="skip_import"):
                st.session_state.onboarding_step = 3
                st.rerun()

    def render_step_3_complete(self):
        """Étape 3: Félicitations !"""
        st.balloons()

        st.markdown(
            """
        <style>
        .onboarding-complete {
            text-align: center;
            padding: 3rem;
        }
        </style>
        <div class="onboarding-complete">
            <h1>🎉 Félicitations !</h1>
            <p style="font-size: 1.3rem; margin: 2rem 0;">
                Vous êtes prêt à prendre le contrôle de vos finances.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.subheader("🚀 Prochaines étapes recommandées")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📊 Dashboard", "Disponible")
            st.caption("Visualisez vos finances en un coup d'œil")
            if st.button("Voir le Dashboard", key="goto_dashboard"):
                st.switch_page("pages/02_Dashboard.py")

        with col2:
            st.metric("🤖 Assistant IA", "Actif")
            st.caption("Posez des questions sur vos finances")
            if st.button("Essayer l'Assistant", key="goto_assistant"):
                st.switch_page("pages/06_Assistant.py")

        with col3:
            st.metric("⚙️ Configuration", "Disponible")
            st.caption("Personnalisez vos catégories et membres")
            if st.button("Configurer", key="goto_config"):
                st.switch_page("pages/08_Configuration.py")

        st.divider()

        if st.button("✅ Terminer l'onboarding", type="primary", key="onboarding_finish"):
            st.session_state.onboarding_completed = True
            st.rerun()

    def render(self):
        """Rend l'interface d'onboarding complète."""
        if not self.is_first_time() or st.session_state.get("onboarding_completed"):
            return False

        self.render_welcome()
        self.render_step_indicator()

        step = st.session_state.onboarding_step

        with st.container():
            if step == 1:
                self.render_step_1_config()
            elif step == 2:
                self.render_step_2_import()
            elif step == 3:
                self.render_step_3_complete()

        return True


def render_onboarding_widget(user_id: str = "default", has_data: bool = False):
    """
    Widget d'onboarding à afficher sur les pages principales.

    Args:
        user_id: Identifiant utilisateur
        has_data: True si l'utilisateur a déjà des données
    """
    # Si l'utilisateur a des données, ne pas afficher
    if has_data or st.session_state.get("onboarding_completed", False):
        return

    # Afficher un bandeau de bienvenue discret
    with st.container(border=True):
        col1, col2, col3 = st.columns([0.15, 0.7, 0.15])

        with col1:
            st.markdown("### 🎯")

        with col2:
            st.markdown("**Bienvenue !** Vous n'avez pas encore importé de transactions.")
            st.caption("Commencez par importer vos relevés bancaires pour visualiser vos finances.")

        with col3:
            if st.button(
                "Démarrer →",
                type="primary",
                use_container_width=True,
                key="onboarding_widget_start",
            ):
                st.session_state["active_op_tab"] = "📥 Importation"
                st.switch_page("pages/01_Import.py")

        # Bouton pour fermer le widget
        if st.button("✕ Ignorer", key="dismiss_onboarding"):
            st.session_state.onboarding_completed = True
            st.rerun()


def show_tour_button():
    """Affiche un bouton pour relancer le tour guidé."""
    if st.button("🎯 Relancer le tour guidé", type="secondary", key="onboarding_restart_tour"):
        st.session_state.onboarding_completed = False
        st.session_state.onboarding_step = 1
        st.session_state["active_op_tab"] = "📥 Importation"
        st.switch_page("pages/01_Import.py")


# Export pour compatibilité
__all__ = ["OnboardingManager", "render_onboarding_widget", "show_tour_button"]
