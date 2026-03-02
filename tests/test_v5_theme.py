"""
Page de test pour le thème V5.5

Usage:
    streamlit run tests/test_v5_theme.py
"""

import streamlit as st

from modules.ui.v5_5 import LightColors, apply_light_theme

# Configuration
st.set_page_config(
    page_title="Test Thème V5.5",
    page_icon="🎨",
    layout="wide",
)

# Appliquer le thème
apply_light_theme()

st.title("🎨 Test du Thème V5.5 - Light Mode")

st.markdown("Cette page teste le nouveau thème light mode inspiré des maquettes FinCouple.")

# Section couleurs
st.header("🎨 Palette de couleurs")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("**Primary (Emerald)**")
    st.markdown(
        f"<div style='background:{LightColors.PRIMARY};padding:20px;border-radius:8px;color:white;text-align:center;'>#10B981</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='background:{LightColors.PRIMARY_BG};padding:10px;border-radius:8px;text-align:center;margin-top:5px;'>#D1FAE5</div>",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown("**Success**")
    st.markdown(
        f"<div style='background:{LightColors.SUCCESS};padding:20px;border-radius:8px;color:white;text-align:center;'>#10B981</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='background:{LightColors.SUCCESS_BG};padding:10px;border-radius:8px;text-align:center;margin-top:5px;'>#DCFCE7</div>",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown("**Danger**")
    st.markdown(
        f"<div style='background:{LightColors.DANGER};padding:20px;border-radius:8px;color:white;text-align:center;'>#EF4444</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='background:{LightColors.DANGER_BG};padding:10px;border-radius:8px;text-align:center;margin-top:5px;'>#FEE2E2</div>",
        unsafe_allow_html=True,
    )

with col4:
    st.markdown("**Warning**")
    st.markdown(
        f"<div style='background:{LightColors.WARNING};padding:20px;border-radius:8px;color:white;text-align:center;'>#F59E0B</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='background:{LightColors.WARNING_BG};padding:10px;border-radius:8px;text-align:center;margin-top:5px;'>#FEF3C7</div>",
        unsafe_allow_html=True,
    )

# Backgrounds
st.subheader("🖼️ Couleurs de fond")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**BG Page**")
    st.markdown(
        f"<div style='background:{LightColors.BG_PAGE};padding:30px;border-radius:8px;border:1px solid #E5E7EB;text-align:center;'>#F9FAFB</div>",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown("**BG Card**")
    st.markdown(
        f"<div style='background:{LightColors.BG_CARD};padding:30px;border-radius:8px;border:1px solid #E5E7EB;text-align:center;'>#FFFFFF</div>",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown("**BG Secondary**")
    st.markdown(
        f"<div style='background:{LightColors.BG_SECONDARY};padding:30px;border-radius:8px;border:1px solid #E5E7EB;text-align:center;'>#F3F4F6</div>",
        unsafe_allow_html=True,
    )

# Texte
st.subheader("📝 Couleurs de texte")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"<p style='color:{LightColors.TEXT_PRIMARY};font-size:1.2rem;font-weight:600;'>Text Primary</p>",
        unsafe_allow_html=True,
    )
    st.code(LightColors.TEXT_PRIMARY)

with col2:
    st.markdown(
        f"<p style='color:{LightColors.TEXT_SECONDARY};font-size:1.2rem;font-weight:600;'>Text Secondary</p>",
        unsafe_allow_html=True,
    )
    st.code(LightColors.TEXT_SECONDARY)

with col3:
    st.markdown(
        f"<p style='color:{LightColors.TEXT_MUTED};font-size:1.2rem;font-weight:600;'>Text Muted</p>",
        unsafe_allow_html=True,
    )
    st.code(LightColors.TEXT_MUTED)

# Composants
st.header("🔘 Composants")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Boutons")
    st.button("▶️ Bouton Primaire", type="primary", use_container_width=True)
    st.button("📖 Bouton Secondaire", type="secondary", use_container_width=True)

with col2:
    st.subheader("Input")
    st.text_input("Label", placeholder="Placeholder...")
    st.selectbox("Select", options=["Option 1", "Option 2", "Option 3"])

# Alertes
st.header("⚠️ Alertes")
st.success("✅ Message de succès")
st.error("❌ Message d'erreur")
st.warning("⚠️ Message d'avertissement")
st.info("ℹ️ Message d'information")

# Métrique
st.header("📊 Métrique (KPI)")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Reste à vivre", "1 847.52 €", "+13.8%")
col2.metric("Dépenses", "-2 152.48 €", "-9.4%")
col3.metric("Revenus", "4 200.00 €", "+5.0%")
col4.metric("Épargne", "200.00 €")

st.divider()
st.caption("FinancePerso V5.5 - Thème Light Mode")
