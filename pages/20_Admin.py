"""
Page Administration - Analytics & Accessibilité
Accessible uniquement via le menu Système ou directement
"""

import streamlit as st

from modules.analytics.events import get_analytics_summary
from modules.analytics.metrics import MetricsCollector
from modules.ui.accessibility import get_accessibility_report
from modules.ui.theme import get_theme

st.set_page_config(page_title="Admin - Analytics & Accessibilité", page_icon="🔧", layout="wide")

st.title("🔧 Administration FinancePerso")

# Onglets pour organiser les sections
tab_analytics, tab_accessibility, tab_theme = st.tabs(
    ["📊 Analytics", "♿ Accessibilité", "🎨 Thème"]
)

# ==================== ANALYTICS ====================
with tab_analytics:
    st.header("📊 Métriques Utilisateurs")

    # Métriques clés en haut
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        import_j1 = MetricsCollector.get_import_conversion_rate(days=1)
        st.metric(
            "Import J+1",
            f"{import_j1['conversion_rate']:.1f}%",
            f"{import_j1['imported_users']}/{import_j1['total_new_users']}",
        )

    with col2:
        import_j7 = MetricsCollector.get_import_conversion_rate(days=7)
        st.metric(
            "Import J+7",
            f"{import_j7['conversion_rate']:.1f}%",
            f"{import_j7['imported_users']}/{import_j7['total_new_users']}",
        )

    with col3:
        retention_j7 = MetricsCollector.get_retention_rate(days=7)
        st.metric(
            "Rétention J+7",
            f"{retention_j7['retention_rate']:.1f}%",
            f"{retention_j7['retained_users']}/{retention_j7['cohort_size']}",
        )

    with col4:
        events = get_analytics_summary(days=7)
        st.metric("Événements (7j)", f"{events.get('total_events', 0)}")

    st.divider()

    # Adoption des fonctionnalités
    st.subheader("🚀 Adoption des fonctionnalités")
    adoption = MetricsCollector.get_feature_adoption(days=30)

    if adoption:
        # Convertir en format pour st.bar_chart
        chart_data = {k: v["users"] for k, v in adoption.items()}
        st.bar_chart(chart_data)
    else:
        st.info("Pas encore de données d'adoption")

# ==================== ACCESSIBILITÉ ====================
with tab_accessibility:
    st.header("♿ Vérification Accessibilité WCAG")

    theme = get_theme()
    theme_config = {
        "text_primary": theme.text_primary,
        "text_secondary": theme.text_secondary,
        "bg_card": theme.bg_card,
        "primary": theme.primary,
        "positive": theme.positive,
        "negative": theme.negative,
    }

    report = get_accessibility_report(theme_config)

    # Badge de conformité
    if report["passes_all_aa"]:
        st.success("✅ Thème conforme WCAG AA")
    else:
        st.error(f"❌ {len(report['failures'])} problèmes de contraste détectés")

    # Détail des vérifications
    st.subheader("Détail des contrastes")

    for check in report["all_checks"]:
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            fg = check["foreground"]
            bg = check["background"]
            st.markdown(
                f"<span style='color:{fg}; background:{bg}; padding: 4px 8px; border-radius: 4px;'>"
                f"Texte</span> {fg} sur {bg}",
                unsafe_allow_html=True,
            )

        with col2:
            ratio = check["ratio"]
            if check["passes_aaa"]:
                st.markdown(f"✅ **{ratio}:1** (AAA)")
            elif check["passes_aa"]:
                st.markdown(f"✅ **{ratio}:1** (AA)")
            else:
                st.markdown(f"❌ **{ratio}:1**")

        with col3:
            if check["passes_aa"]:
                st.caption("Conforme")
            else:
                st.caption("Non conforme")

    # Recommandations
    if report["failures"]:
        st.warning("### Recommandations")
        for f in report["failures"]:
            st.markdown(
                f"- **{f['foreground']}** sur **{f['background']}** : "
                f"{f['ratio']}:1 (minimum requis: {f['required']}:1)"
            )

# ==================== THÈME ====================
with tab_theme:
    st.header("🎨 Configuration du Thème")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Thème actuel")
        st.json(
            {
                "name": theme.name,
                "is_dark": theme.is_dark,
                "primary": theme.primary,
                "primary_light": theme.primary_light,
                "text_primary": theme.text_primary,
                "bg_card": theme.bg_card,
            }
        )

    with col2:
        st.subheader("Aperçu")
        st.markdown(
            f"""
        <div style="
            background: {theme.bg_card};
            color: {theme.text_primary};
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid {theme.border};
        ">
            <h4 style="color: {theme.primary}; margin-top: 0;">Titre primaire</h4>
            <p>Texte normal sur fond de carte</p>
            <p style="color: {theme.text_secondary};">Texte secondaire</p>
            <div style="
                background: {theme.primary};
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 4px;
                display: inline-block;
                margin-top: 0.5rem;
            ">Bouton primaire</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

st.divider()
st.caption("FinancePerso v5.5 - Administration interne")
