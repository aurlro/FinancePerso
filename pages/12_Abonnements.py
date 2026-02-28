"""
📅 Abonnements - Redirection vers Automatisation

Cette page a été fusionnée avec la page 🧠 Automatisation.
Les fonctionnalités sont maintenant accessibles dans :
- 📥 Inbox : Validation des nouveaux abonnements
- ⚙️ Règles > 🔁 Abonnements : Gestion des abonnements confirmés
- 📊 Historique > 💳 Calculateur : Calculateur "Reste à vivre"

Ce fichier est conservé pour la compatibilité des favoris/liens.
"""

import time

import streamlit as st

from modules.ui import load_css, render_scroll_to_top
from modules.ui.tokens import Colors, Spacing, Typography

# Configuration de la page
st.set_page_config(
    page_title="Abonnements - Redirection",
    page_icon="📅",
    layout="wide",
)

# Chargement du Design System
load_css()

# Titre de la page
st.title("📅 Abonnements")

# ═══════════════════════════════════════════════════════════════════════════════
# CARTE INFO PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════

main_info_card = (
    f'<div style="'
    f'background: linear-gradient(135deg, {Colors.INFO_BG.value} 0%, {Colors.SLATE_100.value} 100%); '
    f'border-left: 4px solid {Colors.INFO.value}; '
    f'border-radius: 12px; '
    f'padding: {Spacing.LG.value}; '
    f'margin-bottom: {Spacing.LG.value}; '
    f'">'
    f'<h3 style="'
    f'color: {Colors.INFO_DARK.value}; '
    f'font-size: {Typography.SIZE_XL.value}; '
    f'font-weight: {Typography.WEIGHT_SEMIBOLD.value}; '
    f'margin: 0 0 {Spacing.SM.value} 0; '
    f'">🔄 Les fonctionnalités ont été déplacées</h3>'
    f'<p style="'
    f'color: {Colors.SLATE_700.value}; '
    f'font-size: {Typography.SIZE_BASE.value}; '
    f'line-height: {Typography.LEADING_RELAXED.value}; '
    f'margin: 0; '
    f'">'
    f'Les fonctionnalités de gestion des abonnements ont été fusionnées avec la page '
    f'<strong>🧠 Automatisation</strong> pour une expérience plus cohérente et centralisée.'
    f'</p></div>'
)
st.markdown(main_info_card, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION : OÙ TROUVER VOS FONCTIONNALITÉS
# ═══════════════════════════════════════════════════════════════════════════════

section_title = (
    f'<h2 style="'
    f'color: {Colors.SLATE_800.value}; '
    f'font-size: {Typography.SIZE_2XL.value}; '
    f'font-weight: {Typography.WEIGHT_SEMIBOLD.value}; '
    f'margin: {Spacing.XL.value} 0 {Spacing.MD.value} 0; '
    f'">📍 Où trouver vos fonctionnalités</h2>'
)
st.markdown(section_title, unsafe_allow_html=True)

# Données des cartes de redirection
feature_cards = [
    {
        "icon": "📥",
        "title": "Inbox Validation",
        "description": "Validez les nouvelles détections d'abonnements et gérez les suggestions",
        "path": "pages/4_Intelligence.py",
        "color": Colors.SUCCESS.value,
        "bg_color": Colors.SUCCESS_BG.value,
    },
    {
        "icon": "⚙️",
        "title": "Règles Abonnements",
        "description": "Gérez vos abonnements confirmés et configurez les règles de détection",
        "path": "pages/4_Intelligence.py",
        "color": Colors.PRIMARY.value,
        "bg_color": Colors.SLATE_100.value,
    },
    {
        "icon": "⚠️",
        "title": "Alertes Zombies",
        "description": "Surveillez les abonnements inutilisés et recevez des alertes",
        "path": "pages/4_Intelligence.py",
        "color": Colors.WARNING.value,
        "bg_color": Colors.WARNING_BG.value,
    },
    {
        "icon": "💳",
        "title": "Calculateur",
        "description": "Calculez votre 'reste à vivre' après tous vos abonnements",
        "path": "pages/4_Intelligence.py",
        "color": Colors.ACCENT.value,
        "bg_color": Colors.ACCENT_BG.value,
    },
]

# Affichage des cartes en grille 2x2
for i in range(0, len(feature_cards), 2):
    cols = st.columns(2)
    
    for j, card in enumerate(feature_cards[i:i+2]):
        with cols[j]:
            card_html = (
                f'<div style="'
                f'background: {Colors.WHITE.value}; '
                f'border: 1px solid {Colors.SLATE_200.value}; '
                f'border-radius: 12px; '
                f'padding: {Spacing.LG.value}; '
                f'margin-bottom: {Spacing.MD.value}; '
                f'transition: all 0.2s ease; '
                f'">'
                f'<div style="'
                f'display: flex; '
                f'align-items: center; '
                f'gap: {Spacing.SM.value}; '
                f'margin-bottom: {Spacing.SM.value}; '
                f'">'
                f'<span style="'
                f'font-size: {Typography.SIZE_2XL.value}; '
                f'background: {card["bg_color"]}; '
                f'padding: {Spacing.SM.value}; '
                f'border-radius: 8px; '
                f'">{card["icon"]}</span>'
                f'<h4 style="'
                f'color: {Colors.SLATE_800.value}; '
                f'font-size: {Typography.SIZE_LG.value}; '
                f'font-weight: {Typography.WEIGHT_SEMIBOLD.value}; '
                f'margin: 0; '
                f'">{card["title"]}</h4></div>'
                f'<p style="'
                f'color: {Colors.SLATE_600.value}; '
                f'font-size: {Typography.SIZE_SM.value}; '
                f'line-height: {Typography.LEADING_RELAXED.value}; '
                f'margin: 0 0 {Spacing.MD.value} 0; '
                f'">{card["description"]}</p></div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Bouton de redirection pour cette carte
            if st.button(
                "🚀 Y aller →",
                key=f"btn_{card['title']}",
                use_container_width=True,
                type="secondary",
            ):
                st.switch_page(card["path"])

# ═══════════════════════════════════════════════════════════════════════════════
# BOUTON PRINCIPAL DE REDIRECTION
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(
    f'<div style="margin: {Spacing.XL.value} 0;"></div>',
    unsafe_allow_html=True
)

# Container pour le bouton principal avec style
button_container = (
    f'<div style="'
    f'background: linear-gradient(135deg, {Colors.SLATE_50.value} 0%, {Colors.WHITE.value} 100%); '
    f'border: 2px dashed {Colors.SLATE_300.value}; '
    f'border-radius: 16px; '
    f'padding: {Spacing.XL.value}; '
    f'text-align: center; '
    f'">'
    f'<p style="'
    f'color: {Colors.SLATE_600.value}; '
    f'font-size: {Typography.SIZE_SM.value}; '
    f'margin: 0 0 {Spacing.MD.value} 0; '
    f'">Cliquez ci-dessous pour accéder à la page Automatisation</p></div>'
)
st.markdown(button_container, unsafe_allow_html=True)

if st.button(
    "🚀 Aller vers Automatisation",
    type="primary",
    use_container_width=True,
):
    st.switch_page("pages/4_Intelligence.py")

# ═══════════════════════════════════════════════════════════════════════════════
# BARRE DE PROGRESSION DE REDIRECTION
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(
    f'<div style="margin: {Spacing.LG.value} 0;"></div>',
    unsafe_allow_html=True
)

# Container stylisé pour la progression
progress_container_html = (
    f'<div style="'
    f'background: {Colors.SLATE_50.value}; '
    f'border-radius: 8px; '
    f'padding: {Spacing.MD.value}; '
    f'">'
    f'<p style="'
    f'color: {Colors.SLATE_600.value}; '
    f'font-size: {Typography.SIZE_SM.value}; '
    f'text-align: center; '
    f'margin: 0 0 {Spacing.SM.value} 0; '
    f'">⏱️ Redirection automatique dans <strong>5 secondes</strong>...</p></div>'
)
st.markdown(progress_container_html, unsafe_allow_html=True)

# Barre de progression avec couleur du Design System
progress_text = "Redirection en cours..."
my_bar = st.progress(0, text=progress_text)

# Animation de la barre avec les couleurs du Design System
for percent_complete in range(100):
    time.sleep(0.05)
    my_bar.progress(
        percent_complete + 1,
        text=f"{progress_text} ({percent_complete + 1}%)",
    )

# ═══════════════════════════════════════════════════════════════════════════════
# REDIRECTION JAVASCRIPT
# ═══════════════════════════════════════════════════════════════════════════════

# Redirection JavaScript pour une expérience fluide
st.markdown(
    """
    <script>
        setTimeout(function() {
            window.location.href = '/Intelligence';
        }, 5000);
    </script>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════════════
# LIEN MANUEL DE SECOURS
# ═══════════════════════════════════════════════════════════════════════════════

st.divider()

footer_html = (
    f'<div style="'
    f'text-align: center; '
    f'padding: {Spacing.MD.value}; '
    f'">'
    f'<p style="'
    f'color: {Colors.SLATE_500.value}; '
    f'font-size: {Typography.SIZE_SM.value}; '
    f'margin: 0; '
    f'">Si la redirection ne fonctionne pas : '
    f'<a href="/Intelligence" style="'
    f'color: {Colors.INFO.value}; '
    f'text-decoration: none; '
    f'font-weight: {Typography.WEIGHT_MEDIUM.value}; '
    f'">Cliquez ici pour aller vers Automatisation →</a></p></div>'
)
st.markdown(footer_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SCROLL TO TOP
# ═══════════════════════════════════════════════════════════════════════════════

render_scroll_to_top()
