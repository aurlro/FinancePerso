"""
Local ML Manager UI Component

Interface pour gérer et utiliser le modèle ML local scikit-learn.
"""

from datetime import datetime

import streamlit as st

from modules.local_ml import (
    MODEL_PATH,
    get_classifier,
    get_local_ml_stats,
    is_local_ml_available,
    train_local_model,
)
from modules.ui.feedback import toast_error, toast_success


def render_local_ml_section():
    """
    Render the local ML management section in configuration.
    Allows training, monitoring, and using the local ML model.
    """
    st.header("🤖 Modèle ML Local (scikit-learn)")
    st.markdown("""
    Entraînez un modèle de catégorisation **100% offline** sur vos propres données.
    Alternative à l'IA cloud pour plus de confidentialité.
    """)

    # Check if scikit-learn is available
    if not is_local_ml_available():
        st.error("❌ scikit-learn n'est pas installé")
        st.info("""
        **Installation:**
        ```bash
        pip install scikit-learn
        ```
        """)
        return

    # Get model stats
    stats = get_local_ml_stats()

    # Status indicator
    col1, col2, col3 = st.columns(3)

    with col1:
        if stats["is_trained"]:
            st.success("✅ Modèle entraîné")
        else:
            st.warning("⚠️ Modèle non entraîné")

    with col2:
        st.metric("Catégories", stats["categories_count"])

    with col3:
        if stats["training_date"]:
            training_date = datetime.fromisoformat(stats["training_date"])
            days_ago = (datetime.now() - training_date).days
            st.metric("Âge du modèle", f"{days_ago} jours")
        else:
            st.metric("Âge du modèle", "N/A")

    st.divider()

    # Training section
    st.subheader("🎓 Entraînement")

    if stats["is_trained"]:
        st.info(f"""
        **Modèle actuel:**
        - Catégories: {', '.join(stats['categories'][:5])}{'...' if len(stats['categories']) > 5 else ''}
        - Fichier: `{MODEL_PATH}`
        """)

    col_train, col_retrain = st.columns(2)

    with col_train:
        if not stats["is_trained"]:
            if st.button(
                "🚀 Entraîner le modèle", type="primary", use_container_width=True, key="button_78"
            ):
                with st.spinner("Entraînement en cours... Cela peut prendre quelques secondes."):
                    success, message = train_local_model()

                if success:
                    toast_success(message, icon="🎉")
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    toast_error(message, icon="❌")
                    st.error(f"❌ {message}")
        else:
            if st.button(
                "🔄 Réentraîner", type="secondary", use_container_width=True, key="button_90"
            ):
                with st.spinner("Réentraînement..."):
                    success, message = train_local_model()

                if success:
                    toast_success(message, icon="🔄")
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    toast_error(message, icon="❌")
                    st.error(f"❌ {message}")

    with col_retrain:
        if stats["is_trained"]:
            if st.button(
                "🗑️ Supprimer le modèle",
                type="secondary",
                use_container_width=True,
                key="button_104",
            ):
                import os

                try:
                    if os.path.exists(MODEL_PATH):
                        os.remove(MODEL_PATH)
                        toast_success("Modèle supprimé", icon="🗑️")
                        st.rerun()
                except Exception as e:
                    toast_error(f"Erreur: {e}", icon="❌")

    # Test section
    if stats["is_trained"]:
        st.divider()
        st.subheader("🧪 Test du modèle")

        test_label = st.text_input(
            "Libellé de test", placeholder="Ex: UBER TRIP, AMAZON FR, CARREFOUR..."
        )

        if test_label:
            classifier = get_classifier()
            prediction, confidence = classifier.predict(test_label)

            if prediction:
                # Color based on confidence
                if confidence >= 0.8:
                    color = "green"
                    emoji = "✅"
                elif confidence >= 0.6:
                    color = "orange"
                    emoji = "⚠️"
                else:
                    color = "red"
                    emoji = "❓"

                st.markdown(
                    f"""
                <div style="
                    padding: 15px;
                    border-radius: 8px;
                    background: {'#dcfce7' if confidence >= 0.8 else '#fef3c7' if confidence >= 0.6 else '#fee2e2'};
                    border-left: 4px solid {color};
                ">
                    <strong>{emoji} Prédiction:</strong> {prediction}<br>
                    <strong>Confiance:</strong> {confidence:.1%}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.warning("Impossible de faire une prédiction")

    # Comparison with AI
    st.divider()
    st.subheader("📊 Comparaison IA Local vs Cloud")

    comparison_data = {
        "Critère": ["Confidentialité", "Latence", "Précision", "Coût", "Connexion requise"],
        "ML Local": ["🔒 100% offline", "⚡ Instantané", "📈 ~75-85%*", "💰 Gratuit", "📡 Non"],
        "IA Cloud": [
            "☁️ Envoie données",
            "⏱️ 1-3 secondes",
            "📈 ~85-95%",
            "💰 API payante",
            "📡 Oui",
        ],
    }

    st.dataframe(comparison_data, use_container_width=True, hide_index=True)

    st.caption("*La précision dépend de la quantité et qualité de vos données d'entraînement")

    # Usage recommendations
    st.info("""
    💡 **Recommandations:**
    - Utilisez le **ML Local** si vous privilégiez la confidentialité
    - Utilisez l'**IA Cloud** si vous voulez la meilleure précision
    - Le modèle local s'améliore avec le temps (plus de données = meilleures prédictions)
    """)


def render_ml_mode_selector():
    """
    Render a selector for ML mode preference in settings.
    Returns the selected mode.
    """
    st.subheader("🎛️ Mode de catégorisation")

    # Get current preference
    if "ml_mode_preference" not in st.session_state:
        st.session_state["ml_mode_preference"] = "auto"

    mode = st.radio(
        "Préférence de catégorisation",
        options=["auto", "local", "cloud", "rules_only"],
        format_func=lambda x: {
            "auto": "🤖 Auto (Local si disponible, sinon Cloud)",
            "local": "🏠 ML Local uniquement (100% offline)",
            "cloud": "☁️ IA Cloud uniquement",
            "rules_only": "📋 Règles uniquement (pas de ML)",
        }[x],
        key="ml_mode_preference",
    )

    stats = get_local_ml_stats()

    if mode == "local" and not stats["is_trained"]:
        st.warning(
            "⚠️ Le modèle local n'est pas entraîné. Allez dans la section 'Modèle ML Local' pour l'entraîner."
        )

    return mode
