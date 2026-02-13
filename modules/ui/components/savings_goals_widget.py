"""
Savings Goals Widget - Composant UI pour afficher les objectifs d'épargne.

Intégré dans le dashboard pour créer de la motivation émotionnelle.
"""

import streamlit as st
from typing import Optional

from modules.savings_goals import (
    get_active_savings_goals,
    get_closest_savings_goal,
    contribute_to_savings_goal,
    SavingsGoal
)
from modules.ui.feedback import toast_success, toast_info


def render_savings_goal_card(goal: SavingsGoal, compact: bool = False):
    """Afficher une carte d'objectif d'épargne."""
    
    if compact:
        # Version compacte pour le dashboard
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.markdown(f"<h1 style='text-align: center; margin: 0;'>{goal.emoji}</h1>", unsafe_allow_html=True)
            
            with col2:
                st.write(f"**{goal.name}**")
                
                # Barre de progression
                progress = goal.progress_pct / 100
                st.progress(progress, text=f"{goal.progress_pct:.0f}%")
                
                # Détails
                if goal.days_remaining:
                    if goal.days_remaining > 0:
                        st.caption(f"⏰ {goal.days_remaining} jours restants")
                    else:
                        st.caption("⚠️ Date dépassée")
                
                if goal.monthly_needed and goal.monthly_needed > 0:
                    st.caption(f"💡 {goal.monthly_needed:.0f}€/mois recommandé")
            
            with col3:
                st.write(f"**{goal.current_amount:.0f}€**")
                st.caption(f"/ {goal.target_amount:.0f}€")
    
    else:
        # Version complète avec actions
        with st.container(border=True):
            # Header
            col_header, col_actions = st.columns([3, 1])
            
            with col_header:
                st.markdown(f"## {goal.emoji} {goal.name}")
                if goal.description:
                    st.caption(goal.description)
            
            with col_actions:
                if goal.is_achieved():
                    st.success("🎉 Atteint !")
                else:
                    st.caption(f"⏰ {goal.days_remaining}j" if goal.days_remaining else "")
            
            # Progress bar
            progress = goal.progress_pct / 100
            st.progress(progress, text=f"{goal.progress_pct:.1f}% complété")
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Actuel", f"{goal.current_amount:.0f}€")
            with col2:
                st.metric("Objectif", f"{goal.target_amount:.0f}€")
            with col3:
                st.metric("Reste", f"{goal.remaining_amount:.0f}€")
            
            # Contribution rapide
            if not goal.is_achieved():
                with st.form(f"contribute_{goal.id}"):
                    st.write("**Ajouter un montant**")
                    
                    cols = st.columns(4)
                    preset_amounts = [10, 50, 100, 500]
                    selected_amount = None
                    
                    for i, preset in enumerate(preset_amounts):
                        with cols[i]:
                            if st.form_submit_button(f"+{preset}€", use_container_width=True):
                                selected_amount = preset
                    
                    custom_amount = st.number_input(
                        "Ou montant personnalisé",
                        min_value=0.0,
                        max_value=float(goal.remaining_amount),
                        value=0.0,
                        step=10.0
                    )
                    
                    submit = st.form_submit_button("💰 Contribuer", type="primary", use_container_width=True)
                    
                    if submit:
                        amount = selected_amount if selected_amount else custom_amount
                        if amount > 0:
                            if contribute_to_savings_goal(goal.id, amount):
                                toast_success(f"✅ {amount:.0f}€ ajoutés à '{goal.name}' !", icon="💰")
                                
                                # Check if goal achieved
                                if goal.current_amount + amount >= goal.target_amount:
                                    st.balloons()
                                    st.success(f"🎉 Félicitations ! Objectif '{goal.name}' atteint !")
                                
                                st.rerun()


def render_savings_goals_summary():
    """Afficher un résumé des objectifs d'épargne pour le dashboard."""
    
    goals = get_active_savings_goals()
    
    if not goals:
        # Empty state engageant
        with st.container(border=True):
            st.markdown("### 🎯 Objectifs d'épargne")
            st.info("💡 Définissez votre premier objectif d'épargne pour rester motivé !")
            
            col1, col2, col3 = st.columns(3)
            examples = [
                ("🏖️", "Vacances", 2000),
                ("🚗", "Voiture", 8000),
                ("🏠", "Apport", 50000),
            ]
            
            for emoji, name, target in examples:
                with col1 if name == "Vacances" else col2 if name == "Voiture" else col3:
                    st.caption(f"{emoji} {name}")
                    st.write(f"{target:,}€")
            
            if st.button("➕ Créer mon objectif", type="primary", use_container_width=True, key="create_goal_empty"):
                st.session_state['show_goal_form'] = True
                st.rerun()
        
        return
    
    # Afficher l'objectif le plus proche
    closest = get_closest_savings_goal()
    
    with st.container(border=True):
        st.markdown("### 🎯 Objectif prioritaire")
        
        if closest:
            render_savings_goal_card(closest, compact=True)
            
            # Action rapide
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💰 Contribuer", use_container_width=True, key="contribute_main"):
                    st.session_state['contribute_to'] = closest.id
                    st.rerun()
            with col2:
                if st.button("📋 Voir tous", use_container_width=True, key="see_all_goals"):
                    st.session_state['view_all_goals'] = True
                    st.rerun()
        
        # Résumé si plusieurs objectifs
        if len(goals) > 1:
            st.divider()
            st.caption(f"Et {len(goals) - 1} autre(s) objectif(s) actif(s)")


def render_goal_creation_form():
    """Formulaire de création d'objectif."""
    
    st.subheader("🎯 Nouvel objectif d'épargne")
    
    with st.form("create_goal_form"):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            emoji = st.selectbox(
                "Icône",
                options=["🏖️", "🚗", "🏠", "📱", "💻", "✈️", "🎁", "🎓", "💍", "🎯"],
                index=0
            )
        
        with col2:
            name = st.text_input("Nom de l'objectif", placeholder="Ex: Vacances au Japon")
        
        description = st.text_area("Description (optionnel)", placeholder="Pourquoi cet objectif est important pour vous ?")
        
        col3, col4 = st.columns(2)
        
        with col3:
            target = st.number_input("Montant objectif (€)", min_value=100.0, value=1000.0, step=100.0)
        
        with col4:
            initial = st.number_input("Montant déjà épargné (€)", min_value=0.0, value=0.0, step=50.0)
        
        deadline = st.date_input(
            "Date cible (optionnel)",
            value=None,
            min_value=st.date_input
        )
        
        submitted = st.form_submit_button("✨ Créer l'objectif", type="primary", use_container_width=True)
        
        if submitted:
            if not name:
                st.error("❌ Le nom est obligatoire")
            elif target <= 0:
                st.error("❌ Le montant objectif doit être positif")
            else:
                from modules.savings_goals import create_savings_goal
                
                deadline_str = deadline.isoformat() if deadline else None
                
                goal = create_savings_goal(
                    name=name,
                    target=target,
                    emoji=emoji,
                    description=description,
                    initial_amount=initial,
                    deadline=deadline_str
                )
                
                toast_success(f"🎯 Objectif '{name}' créé !", icon="✨")
                
                # Clear form state
                if 'show_goal_form' in st.session_state:
                    del st.session_state['show_goal_form']
                
                st.rerun()
    
    if st.button("❌ Annuler", key="cancel_goal_creation"):
        if 'show_goal_form' in st.session_state:
            del st.session_state['show_goal_form']
        st.rerun()


def render_savings_goals_page():
    """Page complète de gestion des objectifs."""
    
    st.header("🎯 Mes Objectifs d'Épargne")
    st.caption("Visualisez et atteignez vos objectifs financiers")
    
    # Check for form display
    if st.session_state.get('show_goal_form'):
        render_goal_creation_form()
        return
    
    # Bouton création
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Nouvel objectif", type="primary", use_container_width=True):
            st.session_state['show_goal_form'] = True
            st.rerun()
    
    # Liste des objectifs
    goals = get_active_savings_goals()
    achieved = get_goals_manager().get_achieved_goals()
    
    if not goals and not achieved:
        st.info("📭 Aucun objectif défini. Créez votre premier objectif pour commencer !")
        return
    
    # Objectifs actifs
    if goals:
        st.subheader(f"🎯 Objectifs en cours ({len(goals)})")
        
        for goal in sorted(goals, key=lambda g: g.progress_pct, reverse=True):
            render_savings_goal_card(goal, compact=False)
    
    # Objectifs atteints
    if achieved:
        st.divider()
        st.subheader(f"🏆 Objectifs atteints ({len(achieved)})")
        
        with st.expander("Voir les objectifs complétés"):
            for goal in achieved:
                st.success(f"{goal.emoji} **{goal.name}** - {goal.target_amount:.0f}€ atteints ! 🎉")


# Helper pour l'intégration dans le daily widget
def get_goal_insight_for_daily_widget() -> Optional[dict]:
    """Génère un insight pour le daily widget basé sur les objectifs."""
    
    closest = get_closest_savings_goal()
    if not closest:
        return None
    
    # Ne pas montrer si déjà atteint
    if closest.is_achieved():
        return None
    
    progress = closest.progress_pct
    
    # Messages motivants selon la progression
    if progress >= 90:
        message = f"🎉 Presque là ! Plus que {closest.remaining_amount:.0f}€"
        priority = "high"
    elif progress >= 50:
        message = f"💪 À mi-parcours ! Continuez comme ça"
        priority = "medium"
    else:
        message = f"🌱 Début du voyage, objectif: {closest.target_amount:.0f}€"
        priority = "low"
    
    return {
        "type": "savings_goal",
        "title": f"{closest.emoji} {closest.name}",
        "message": message,
        "metric": f"{progress:.0f}%",
        "metric_label": "atteint",
        "progress": progress / 100,
        "priority": priority,
        "action": "savings_goals",
        "action_label": "Voir l'objectif",
    }


def get_goals_manager():
    """Import tardif pour éviter les circular imports."""
    from modules.savings_goals import get_goals_manager
    return get_goals_manager()
