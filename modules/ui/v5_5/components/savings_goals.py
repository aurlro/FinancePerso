"""Objectifs d'épargne - Widget de suivi des objectifs.

Usage:
    from modules.ui.v5_5.components.savings_goals import SavingsGoalsWidget
    
    SavingsGoalsWidget.render()
"""

from typing import List, Optional
import streamlit as st


class SavingsGoal:
    """Représente un objectif d'épargne."""
    
    def __init__(
        self,
        name: str,
        target: float,
        current: float,
        icon: str = "🎯",
        color: str = "#10B981",
    ):
        self.name = name
        self.target = target
        self.current = current
        self.icon = icon
        self.color = color
    
    @property
    def progress(self) -> float:
        """Pourcentage de progression."""
        if self.target == 0:
            return 0
        return min(100, (self.current / self.target) * 100)
    
    @property
    def remaining(self) -> float:
        """Montant restant."""
        return max(0, self.target - self.current)


class SavingsGoalsWidget:
    """Widget de suivi des objectifs d'épargne."""
    
    @staticmethod
    def render(
        goals: Optional[List[SavingsGoal]] = None,
        max_display: int = 3,
    ) -> None:
        """Affiche les objectifs d'épargne.
        
        Args:
            goals: Liste des objectifs (None = récupère depuis DB)
            max_display: Nombre maximum d'objectifs à afficher
        """
        st.markdown("#### 🎯 Objectifs d'épargne")
        
        # Récupérer depuis DB si pas fourni
        if goals is None:
            goals = SavingsGoalsWidget._get_goals_from_db()
        
        if not goals:
            st.info("Aucun objectif défini. Créez votre premier objectif d'épargne!")
            if st.button("➕ Créer un objectif", use_container_width=True):
                st.switch_page("pages/10_Projections.py")
            return
        
        # Afficher les objectifs
        for goal in goals[:max_display]:
            SavingsGoalsWidget._render_goal(goal)
        
        # Lien vers tous les objectifs
        if len(goals) > max_display:
            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.button(f"Voir les {len(goals)} objectifs →", use_container_width=True):
                st.switch_page("pages/10_Projections.py")
    
    @staticmethod
    def _render_goal(goal: SavingsGoal) -> None:
        """Affiche un objectif."""
        progress_color = goal.color if goal.progress < 100 else "#10B981"
        
        with st.container(border=False):
            cols = st.columns([1, 4])
            
            with cols[0]:
                st.markdown(f"<div style='font-size: 1.75rem; text-align: center;'>{goal.icon}</div>", unsafe_allow_html=True)
            
            with cols[1]:
                # Nom et montants
                header_cols = st.columns([2, 1])
                with header_cols[0]:
                    st.write(f"**{goal.name}**")
                with header_cols[1]:
                    st.markdown(
                        f"<div style='text-align: right; font-size: 0.875rem;'>"
                        f"<b>{goal.current:,.0f} €</b> / {goal.target:,.0f} €"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                
                # Barre de progression
                st.progress(goal.progress / 100)
                
                # Info complémentaire
                if goal.progress >= 100:
                    st.caption("🎉 Objectif atteint!")
                else:
                    st.caption(f"Reste {goal.remaining:,.0f} € ({goal.progress:.0f}%)")
        
        st.divider()
    
    @staticmethod
    def _get_goals_from_db() -> List[SavingsGoal]:
        """Récupère les objectifs depuis la base de données."""
        try:
            # TODO: Implémenter la récupération depuis DB
            # Pour l'instant, retourner des données de démonstration
            return [
                SavingsGoal("Vacances Japon", 5000, 3250, "🗾", "#F59E0B"),
                SavingsGoal("Nouvelle voiture", 15000, 8000, "🚗", "#3B82F6"),
                SavingsGoal("Fonds d'urgence", 10000, 10000, "🛡️", "#10B981"),
            ]
        except Exception:
            return []


def render_mini_savings_summary() -> None:
    """Affiche un résumé compact des objectifs."""
    try:
        goals = SavingsGoalsWidget._get_goals_from_db()
        
        if not goals:
            return
        
        total_target = sum(g.target for g in goals)
        total_current = sum(g.current for g in goals)
        progress = (total_current / total_target * 100) if total_target > 0 else 0
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("<div style='font-size: 2rem;'>🎯</div>", unsafe_allow_html=True)
        with col2:
            st.write(f"**Objectifs d'épargne**")
            st.progress(progress / 100)
            st.caption(f"{total_current:,.0f} € / {total_target:,.0f} € ({progress:.0f}%)")
    
    except Exception:
        pass
