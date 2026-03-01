"""
Configuration Tab - Paramétrage de l'IA et configuration automatique.
"""


import pandas as pd
import streamlit as st

from modules.ai_manager import get_active_model_name, get_ai_provider
from modules.analytics import detect_financial_profile, detect_recurring_payments
from modules.db.categories import get_categories
from modules.db.rules import add_learning_rule
from modules.db.transactions import get_all_transactions
from modules.ui import card_kpi
from modules.ui.assistant.state import get_assistant_state, set_assistant_state


def render_config_tab():
    """Render the configuration tab."""
    st.header("⚙️ Configuration")
    st.markdown("Paramétrez l'IA et configurez automatiquement vos catégories.")

    # AI Status Card
    render_ai_status_card()

    st.divider()

    # Sub-tabs for different configuration types
    config_auto, config_sub, config_manual = st.tabs(
        ["🤖 Configuration Auto", "📅 Abonnements", "⚙️ Manuel"]
    )

    with config_auto:
        render_auto_config()

    with config_sub:
        render_subscriptions()

    with config_manual:
        render_manual_config()


def render_ai_status_card():
    """Render the AI connection status card."""
    st.subheader("🤖 État de l'IA")

    try:
        provider = get_ai_provider()
        model_name = get_active_model_name()

        col1, col2 = st.columns([2, 1])

        with col1:
            st.success(f"✅ Connecté - {model_name}")
            st.caption("L'IA est active et prête à analyser vos données.")

        with col2:
            if st.button("🔄 Tester", use_container_width=True):
                with st.spinner("Test en cours..."):
                    try:
                        # Simple test prompt
                        provider.generate_text(
                            "Réponds simplement 'OK' pour confirmer la connexion.",
                            model_name=model_name,
                        )
                        st.success("✅ Connexion OK")
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")

    except Exception:
        st.error("❌ IA non disponible")
        st.info(
            """
        Pour activer l'IA :
        1. Obtenez une clé API sur [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Configurez-la dans **⚙️ Configuration → 🔑 API & Services**
        """
        )


def render_auto_config():
    """Render automatic configuration section."""
    st.subheader("🏗️ Détection Automatique")
    st.markdown(
        """
    L'IA analysera vos transactions pour détecter automatiquement :
    - Vos revenus réguliers (salaire, etc.)
    - Vos charges fixes (loyer, électricité, etc.)
    - Vos abonnements récurrents
    """
    )

    if st.button("🚀 Lancer la détection", type="primary"):
        df = get_all_transactions()

        if df.empty:
            st.warning("Importez d'abord des données.")
        else:
            with st.spinner("Analyse de votre profil financier..."):
                candidates = detect_financial_profile(df)
                set_assistant_state("setup_candidates", candidates)
            st.rerun()

    # Display candidates
    candidates = get_assistant_state("setup_candidates")
    if candidates is not None:
        render_candidates_list(candidates)


def render_candidates_list(candidates: list):
    """Render detected configuration candidates."""
    if not candidates:
        st.success("🎉 Tout semble déjà configuré !")
        return

    st.info(f"📋 {len(candidates)} suggestions trouvées")

    with st.form("candidates_form"):
        selection_map = {}

        for i, cand in enumerate(candidates):
            st.divider()

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**{cand['label']}** (~{cand['amount']:.0f} €)")
                st.caption(f"Type : {cand['type']}")

                # Details popover
                with st.popover("👁️ Détails"):
                    details = cand.get("sample_transactions", pd.DataFrame())
                    if not details.empty:
                        sample = details.iloc[0]
                        st.markdown(f"**Libellé** : `{sample.get('label', 'N/A')}`")
                        st.markdown(f"**Date** : {sample.get('date', 'N/A')}")
                        st.markdown(f"**Montant** : {sample.get('amount', 0):.2f} €")
                        st.markdown(
                            f"**Catégorie actuelle** : {sample.get('category_validated', 'Inconnu')}"
                        )
                    else:
                        st.info("Aucun détail disponible")

            with col2:
                choice = st.radio(
                    "Action",
                    ("Confirmer", "Ignorer", "Modifier"),
                    key=f"cand_choice_{i}",
                    horizontal=True,
                    label_visibility="collapsed",
                )

                if choice == "Modifier":
                    new_cat = st.selectbox("Catégorie", get_categories(), key=f"cand_cat_{i}")
                    selection_map[i] = {"action": "save", "cat": new_cat}
                elif choice == "Confirmer":
                    selection_map[i] = {"action": "save", "cat": cand["default_category"]}
                else:
                    selection_map[i] = {"action": "skip"}

        submitted = st.form_submit_button("💾 Sauvegarder", type="primary")

        if submitted:
            count = 0
            for i, cand in enumerate(candidates):
                decision = selection_map.get(i)
                if decision and decision["action"] == "save":
                    if add_learning_rule(cand["label"], decision["cat"]):
                        count += 1

            st.success(f"✅ {count} règles créées !")
            set_assistant_state("setup_candidates", None)


def render_subscriptions():
    """Render subscriptions detection section."""
    st.subheader("📅 Détection des Abonnements")
    st.markdown("Analyse des paiements récurrents sur la base de vos transactions.")

    df = get_all_transactions()

    if df.empty:
        st.info("Importez des données pour détecter vos abonnements.")
        return

    with st.spinner("Analyse des paiements récurrents..."):
        recurring = detect_recurring_payments(df)

    if recurring.empty:
        st.warning("Aucun paiement récurrent détecté (il faut au moins 2 occurrences).")
        st.info("💡 Astuce : Les abonnements seront détectés après 2-3 mois de données.")
        return

    # KPIs
    monthly_total = recurring["avg_amount"].sum()

    col1, col2 = st.columns(2)
    with col1:
        card_kpi(
            "Budget Mensuel", f"{abs(monthly_total):.2f} €", trend="Fixe", trend_color="neutral"
        )
    with col2:
        card_kpi("Abonnements", f"{len(recurring)}", trend="Actifs", trend_color="neutral")

    st.divider()

    # Display table
    st.subheader("Détails")

    display_rec = recurring[
        ["label", "avg_amount", "frequency_label", "variability", "category", "last_date"]
    ].copy()
    display_rec["avg_amount"] = display_rec["avg_amount"].apply(lambda x: f"{x:.2f} €")

    st.dataframe(
        display_rec,
        column_config={
            "label": "Libellé",
            "avg_amount": "Montant Moyen",
            "frequency_label": "Fréquence",
            "variability": "Type",
            "category": "Catégorie",
            "last_date": "Dernière transaction",
        },
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "*Basé sur la régularité des paiements (intervalle ~30 jours) et la constance du montant.*"
    )


def render_manual_config():
    """Render manual configuration section."""
    st.subheader("⚙️ Configuration Manuelle")
    st.markdown("Personnalisez directement vos paramètres financiers.")

    from modules.ui.components.profile_form import render_profile_setup_form

    render_profile_setup_form(key_prefix="assistant_config")
