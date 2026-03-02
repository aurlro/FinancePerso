"""
Page de collection de badges et récompenses.
"""

import streamlit as st

from modules.gamification.badges import BadgeManager, render_badges_collection
from modules.ui import load_css, render_scroll_to_top
from modules.ui.design_system import Colors, Spacing, Typography, apply_vibe_theme
from modules.ui.layout import render_app_info

# Page Setup
st.set_page_config(
    page_title="Mes Badges - MyFinance",
    page_icon="🏆",
    layout="wide",
)

# Apply Design System
apply_vibe_theme()
load_css()

# Header avec Design System
st.markdown(
    f"""
<h1 style="
    font-size: {Typography.SIZE_3XL};
    font-weight: {Typography.WEIGHT_BOLD};
    margin-bottom: {Spacing.LG};
    background: linear-gradient(135deg, {Colors.TEXT_PRIMARY.value} 0%, {Colors.PRIMARY_LIGHT.value} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
">
    🏆 Collection de Badges
</h1>
""",
    unsafe_allow_html=True,
)

# Vérifier et attribuer les nouveaux badges
new_badges = BadgeManager.check_and_award_badges()

if new_badges:
    st.balloons()
    for badge in new_badges:
        st.success(f"🎉 Nouveau badge débloqué : **{badge.name}**!")
    st.divider()

# Afficher la collection
render_badges_collection()

# Section Challenges
st.divider()
st.markdown(
    f"""
<h2 style="
    font-size: {Typography.SIZE_2XL};
    font-weight: {Typography.WEIGHT_SEMIBOLD};
    color: {Colors.TEXT_PRIMARY.value};
    margin-top: {Spacing.XL};
    margin-bottom: {Spacing.LG};
    border-bottom: 2px solid {Colors.BORDER.value};
    padding-bottom: {Spacing.SM};
">
    🎯 Challenges en cours
</h2>
""",
    unsafe_allow_html=True,
)

from modules.gamification.challenges import render_challenges_widget

render_challenges_widget()

render_scroll_to_top()
render_app_info()
