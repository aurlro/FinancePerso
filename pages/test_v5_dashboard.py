"""
Page de test pour le Dashboard V5.5

Usage:
    streamlit run pages/test_v5_dashboard.py
"""

import streamlit as st
from modules.ui.v5_5 import render_dashboard_v5, render_welcome_screen, has_transactions

# Configuration
st.set_page_config(
    page_title="Test Dashboard V5.5",
    page_icon="📊",
    layout="wide",
)

st.sidebar.title("🔧 Configuration")

# Options de test
test_mode = st.sidebar.radio(
    "Mode de test",
    options=["Dashboard (avec données)", "Welcome (sans données)", "Auto (détection)"],
    index=2
)

user_name = st.sidebar.text_input("Nom utilisateur", value="Alex")
force_view = st.sidebar.checkbox("Forcer la vue (ignore détection)", value=False)

st.sidebar.divider()
st.sidebar.caption("FinancePerso V5.5")

# Main content
st.title("📊 Test Dashboard V5.5")

# Mode auto
if test_mode == "Auto (détection)" and not force_view:
    has_data = has_transactions()
    st.info(f"🔍 Détection: {'Données trouvées' if has_data else 'Aucune donnée'}")
    
    if has_data:
        render_dashboard_v5(user_name=user_name)
    else:
        render_welcome_screen(user_name=user_name)

# Mode Dashboard forcé
elif test_mode == "Dashboard (avec données)" or (force_view and test_mode == "Auto (détection)"):
    st.warning("⚠️ Mode forcé: Dashboard (même sans données)")
    
    # Mock des données si nécessaire
    if not has_transactions():
        st.info("💡 Mode démo avec données fictives")
        # Afficher dashboard avec données mock
        from modules.ui.v5_5.components import KPICard, KPIData
        from modules.ui.v5_5.components.dashboard_header import DashboardHeader, get_current_month_name
        from modules.ui.v5_5.theme import apply_light_theme
        
        apply_light_theme()
        
        # Header
        DashboardHeader.render(
            user_name=user_name,
            current_month=get_current_month_name(),
        )
        
        # KPIs mock
        st.markdown("### 📊 Vue d'ensemble")
        
        kpis = [
            KPIData("Reste à vivre", "1 847.52 €", "positive", "💚", "#DCFCE7", "+13.8%", "vs Janvier"),
            KPIData("Dépenses", "-2 152.48 €", "negative", "💳", "#FEE2E2", "-9.4%", "vs Janvier"),
            KPIData("Revenus", "4 200.00 €", "positive", "📈", "#DBEAFE", "+5.0%", "vs Janvier"),
            KPIData("Épargne", "200.00 €", "positive", "🎯", "#F3E8FF", None, "🎉 Premier versement !"),
        ]
        
        cols = st.columns(4)
        for idx, kpi in enumerate(kpis):
            with cols[idx]:
                KPICard.render(kpi)
        
        # Message
        st.success("✅ Dashboard affiché avec données de démonstration")
    else:
        render_dashboard_v5(user_name=user_name)

# Mode Welcome forcé
else:
    st.warning("⚠️ Mode forcé: Welcome (même avec données)")
    render_welcome_screen(user_name=user_name)

st.divider()
st.caption("FinancePerso V5.5 - Test Dashboard")
