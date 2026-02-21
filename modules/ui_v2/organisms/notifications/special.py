"""
Composants de notification spéciaux pour le système UI v2.

Inclut les achievements, états de chargement et états vides avec
animations et effets visuels spéciaux.
"""

from collections.abc import Callable

import streamlit as st


def render_achievement_unlock(
    title: str, description: str, icon: str = "🏆", reward: str | None = None
):
    """
    Affiche une célébration pour un achievement débloqué.

    Args:
        title: Nom de l'achievement
        description: Description de ce qui a été accompli
        icon: Icône de l'achievement
        reward: Récompense éventuelle (badge, points, etc.)
    """
    # Animation de célébration
    st.balloons()

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 50%, #fbbf24 100%);
            border-radius: 16px;
            padding: 32px;
            text-align: center;
            margin: 20px 0;
            box-shadow: 0 10px 40px rgba(251, 191, 36, 0.3);
            animation: achievement-pulse 2s ease-in-out infinite;
        ">
            <div style="font-size: 64px; margin-bottom: 16px;">{icon}</div>
            <div style="
                font-size: 14px;
                font-weight: 600;
                color: #92400e;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 8px;
            ">Achievement Débloqué !</div>
            <div style="
                font-size: 24px;
                font-weight: 700;
                color: #78350f;
                margin-bottom: 8px;
            ">{title}</div>
            <div style="color: #92400e; font-size: 16px;">{description}</div>
            {f'<div style="margin-top: 16px; padding: 8px 16px; background: rgba(255,255,255,0.5); border-radius: 20px; display: inline-block; color: #92400e; font-weight: 600;">🎁 {reward}</div>' if reward else ''}
        </div>
        
        <style>
        @keyframes achievement-pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
        }}
        </style>
    """,
        unsafe_allow_html=True,
    )


def render_loading_state(
    message: str = "Chargement en cours...",
    submessage: str | None = None,
    progress: float | None = None,
):
    """
    Affiche un état de chargement amélioré.

    Args:
        message: Message principal
        submessage: Message secondaire détaillé
        progress: Progression entre 0 et 1 (None = indéterminé)
    """
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            f"""
            <div style="
                text-align: center;
                padding: 40px 20px;
                background: #f9fafb;
                border-radius: 12px;
                margin: 20px 0;
            ">
                <div style="
                    font-size: 48px;
                    margin-bottom: 16px;
                    animation: loading-bounce 1.5s ease-in-out infinite;
                ">🔄</div>
                <div style="
                    font-size: 18px;
                    font-weight: 600;
                    color: #374151;
                    margin-bottom: 8px;
                ">{message}</div>
                {f'<div style="color: #6b7280; font-size: 14px;">{submessage}</div>' if submessage else ''}
            </div>
            
            <style>
            @keyframes loading-bounce {{
                0%, 100% {{ transform: translateY(0) rotate(0deg); }}
                50% {{ transform: translateY(-10px) rotate(180deg); }}
            }}
            </style>
        """,
            unsafe_allow_html=True,
        )

        if progress is not None:
            st.progress(progress, text=f"{progress*100:.0f}%")
        else:
            st.progress(0, text="Patientez...")


def render_empty_state(
    icon: str,
    title: str,
    description: str,
    action_label: str | None = None,
    action_callback: Callable | None = None,
):
    """
    Affiche un état vide engageant.

    Args:
        icon: Emoji représentatif
        title: Titre de l'état vide
        description: Explication
        action_label: Label du bouton d'action
        action_callback: Fonction appelée au clic
    """
    st.markdown(
        f"""
        <div style="
            text-align: center;
            padding: 60px 20px;
            background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
            border-radius: 16px;
            border: 2px dashed #d1d5db;
            margin: 20px 0;
        ">
            <div style="font-size: 64px; margin-bottom: 20px; opacity: 0.7;">{icon}</div>
            <div style="
                font-size: 20px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 8px;
            ">{title}</div>
            <div style="color: #6b7280; max-width: 400px; margin: 0 auto;">
                {description}
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(f"✨ {action_label}", use_container_width=True, type="primary"):
                action_callback()
