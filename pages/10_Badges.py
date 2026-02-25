"""
Page de collection de badges et récompenses.
"""

import streamlit as st

from modules.gamification.badges import render_badges_collection, BadgeManager

st.set_page_config(
    page_title="Mes Badges - MyFinance",
    page_icon="🏆",
    layout="wide",
)

st.title("🏆 Collection de Badges")

# Vérifier et attribuer les nouveaux badges
new_badges = BadgeManager.check_and_award_badges()

if new_badges:
    st.balloons()
    for badge in new_badges:
        st.success(f"🎉 Nouveau badge débloqué : **{badge.name}**!")
    st.divider()

# Afficher la collection
render_badges_collection()

st.divider()
st.header("🎯 Challenges en cours")

from modules.gamification.challenges import render_challenges_widget

render_challenges_widget()
