"""
Dynamic Budget System
Ajuste automatiquement les budgets selon les saisonnalités et tendances.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from modules.db.budgets import get_budgets, set_budget
from modules.transaction_types import filter_expense_transactions


@dataclass
class SeasonalPattern:
    """Pattern saisonnier pour une catégorie."""

    category: str
    month_factors: dict[int, float]  # Mois -> Facteur (1.0 = moyenne)
    confidence: float  # 0-1
    sample_size: int


@dataclass
class BudgetAdjustment:
    """Suggestion d'ajustement de budget."""

    category: str
    current_budget: float
    suggested_budget: float
    reason: str
    confidence: float
    expected_savings: float
    risk_level: str  # 'low', 'medium', 'high'


class DynamicBudgetEngine:
    """
    Engine de budgets dynamiques avec ajustement auto.
    """

    def __init__(self, df_history: pd.DataFrame):
        """
        Initialise l'engine avec l'historique des transactions.

        Args:
            df_history: DataFrame avec toutes les transactions historiques
        """
        self.df = df_history.copy()
        if not self.df.empty and "date_dt" in self.df.columns:
            self.df["date_dt"] = pd.to_datetime(self.df["date_dt"])
            self.df["month"] = self.df["date_dt"].dt.month
            self.df["year"] = self.df["date_dt"].dt.year

    def analyze_seasonality(self, category: str, min_months: int = 6) -> SeasonalPattern | None:
        """
        Analyse la saisonnalité d'une catégorie.

        Args:
            category: Nom de la catégorie
            min_months: Nombre minimum de mois d'historique

        Returns:
            Pattern saisonnier ou None si pas assez de données
        """
        if self.df.empty:
            return None

        cat_data = filter_expense_transactions(self.df)
        cat_data = cat_data[cat_data["category_validated"] == category].copy()

        if len(cat_data) < 10:
            return None

        cat_data["amount"] = cat_data["amount"].abs()

        # Grouper par mois
        monthly_avg = cat_data.groupby("month")["amount"].mean()

        if len(monthly_avg) < min_months:
            return None

        # Calculer le facteur saisonnier
        overall_avg = cat_data["amount"].mean()

        month_factors = {}
        for month in range(1, 13):
            if month in monthly_avg.index:
                factor = monthly_avg[month] / overall_avg if overall_avg > 0 else 1.0
                month_factors[month] = round(factor, 2)
            else:
                month_factors[month] = 1.0

        # Calculer la confiance basée sur la variance
        variance = np.var(list(month_factors.values()))
        confidence = min(
            1.0, variance * 2
        )  # Plus la variance est élevée, plus le pattern est marqué

        return SeasonalPattern(
            category=category,
            month_factors=month_factors,
            confidence=confidence,
            sample_size=len(cat_data),
        )

    def get_current_month_adjustment(self, category: str, base_budget: float) -> tuple[float, str]:
        """
        Calcule l'ajustement recommandé pour le mois courant.

        Args:
            category: Nom de la catégorie
            base_budget: Budget de base mensuel

        Returns:
            Tuple (budget ajusté, raison)
        """
        current_month = datetime.now().month
        pattern = self.analyze_seasonality(category)

        if not pattern or pattern.confidence < 0.3:
            return base_budget, "Pas assez d'historique pour un ajustement"

        factor = pattern.month_factors.get(current_month, 1.0)
        adjusted = base_budget * factor

        if factor > 1.2:
            reason = f"📈 Mois typiquement élevé (+{(factor-1)*100:.0f}%)"
        elif factor < 0.8:
            reason = f"📉 Mois typiquement bas (-{(1-factor)*100:.0f}%)"
        else:
            reason = "📊 Dans la moyenne saisonnière"

        return adjusted, reason

    def suggest_budget_adjustments(self) -> list[BudgetAdjustment]:
        """
        Suggère des ajustements pour tous les budgets.

        Returns:
            Liste des suggestions d'ajustement
        """
        suggestions = []

        budgets = get_budgets()
        if budgets.empty or self.df.empty:
            return suggestions

        for _, budget_row in budgets.iterrows():
            category = budget_row["category"]
            current = budget_row["amount"]

            # Calculer la moyenne réelle des 6 derniers mois
            six_months_ago = datetime.now() - timedelta(days=180)
            recent = filter_expense_transactions(self.df)
            recent = recent[
                (recent["category_validated"] == category) & (recent["date_dt"] >= six_months_ago)
            ]

            if len(recent) < 3:
                continue

            actual_avg = abs(recent["amount"].mean())

            # Écart significatif ?
            diff_pct = abs(current - actual_avg) / current if current > 0 else 0

            if diff_pct > 0.2:  # > 20% d'écart
                # Déterminer le niveau de risque
                if diff_pct > 0.5:
                    risk = "high"
                elif diff_pct > 0.3:
                    risk = "medium"
                else:
                    risk = "low"

                # Calculer l'économie potentielle
                if current > actual_avg:
                    expected_savings = current - actual_avg
                    reason = f"Vous dépensez en moyenne {actual_avg:.0f}€ (budget: {current:.0f}€)"
                else:
                    expected_savings = 0
                    reason = f"Vous dépassez régulièrement votre budget ({actual_avg:.0f}€ vs {current:.0f}€)"

                suggestions.append(
                    BudgetAdjustment(
                        category=category,
                        current_budget=current,
                        suggested_budget=actual_avg,
                        reason=reason,
                        confidence=min(1.0, len(recent) / 12),
                        expected_savings=expected_savings,
                        risk_level=risk,
                    )
                )

        # Trier par économie potentielle
        suggestions.sort(key=lambda x: x.expected_savings, reverse=True)
        return suggestions

    def detect_underspent_categories(self, current_month_df: pd.DataFrame) -> list[dict]:
        """
        Détecte les catégories sous-utilisées ce mois-ci.

        Args:
            current_month_df: Données du mois en cours

        Returns:
            Liste des catégories avec budget disponible
        """
        results = []

        budgets = get_budgets()
        if budgets.empty:
            return results

        today = datetime.now()
        day_of_month = today.day
        days_in_month = 30  # Approximation

        for _, budget in budgets.iterrows():
            category = budget["category"]
            budget_amount = budget["amount"]

            # Dépenses actuelles
            spent = filter_expense_transactions(current_month_df)
            spent = spent[spent["category_validated"] == category]["amount"].abs().sum()

            remaining = budget_amount - spent

            if remaining > 0:
                # Progression temporelle
                expected_progress = day_of_month / days_in_month
                actual_progress = spent / budget_amount if budget_amount > 0 else 1

                # Si on est en avance sur le budget
                if actual_progress < expected_progress * 0.8:
                    results.append(
                        {
                            "category": category,
                            "budget": budget_amount,
                            "spent": spent,
                            "remaining": remaining,
                            "days_left": days_in_month - day_of_month,
                            "daily_allowance": (
                                remaining / (days_in_month - day_of_month)
                                if day_of_month < days_in_month
                                else 0
                            ),
                            "status": "ahead",  # En avance
                        }
                    )

        return results

    def generate_smart_budgets(self, target_monthly_savings: float) -> dict[str, float]:
        """
        Génère des budgets optimisés pour atteindre un objectif d'épargne.

        Args:
            target_monthly_savings: Objectif d'épargne mensuelle

        Returns:
            Dict des budgets suggérés par catégorie
        """
        if self.df.empty:
            return {}

        # Calculer les dépenses moyennes actuelles
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_expenses = filter_expense_transactions(self.df)
        recent_expenses = recent_expenses[recent_expenses["date_dt"] >= six_months_ago].copy()

        if recent_expenses.empty:
            return {}

        recent_expenses["amount"] = recent_expenses["amount"].abs()

        # Dépenses moyennes par catégorie
        avg_by_category = recent_expenses.groupby("category_validated")["amount"].mean().to_dict()
        sum(avg_by_category.values())

        # Calculer la réduction nécessaire
        current_savings = 0  # Simplifié
        savings_gap = target_monthly_savings - current_savings

        if savings_gap <= 0:
            return {cat: avg for cat, avg in avg_by_category.items()}

        # Réduction proportionnelle (plus facile sur les catégories variables)
        variable_categories = ["Loisirs", "Shopping", "Restaurants", "Courses"]

        suggested = {}
        reduction_needed = savings_gap

        for category, avg in avg_by_category.items():
            if category in variable_categories and reduction_needed > 0:
                # Réduction plus agressive sur les variables
                reduction = min(avg * 0.3, reduction_needed)  # Max -30%
                suggested[category] = avg - reduction
                reduction_needed -= reduction
            else:
                suggested[category] = avg

        return suggested


class BudgetChallenge:
    """
    Système de challenges d'économies (gamification).
    """

    CHALLENGES = [
        {
            "id": "no_impulse_week",
            "name": "Semaine sans impulsions",
            "description": "Aucune dépense > 50€ pendant 7 jours",
            "difficulty": "easy",
            "reward": "🏅 Maître de soi",
            "savings_potential": 200,
        },
        {
            "id": "category_reduction_20",
            "name": "Réduction ciblée",
            "description": "Réduire une catégorie de 20% ce mois-ci",
            "difficulty": "medium",
            "reward": "🎯 Snipeur",
            "savings_potential": 100,
        },
        {
            "id": "no_eating_out_week",
            "name": "Cuisine maison",
            "description": "0 restaurant pendant 1 semaine",
            "difficulty": "medium",
            "reward": "👨‍🍳 Chef à domicile",
            "savings_potential": 80,
        },
        {
            "id": "savings_streak_3",
            "name": "Série d'épargne",
            "description": "3 mois consécutifs avec épargne positive",
            "difficulty": "hard",
            "reward": "💎 Discipliné",
            "savings_potential": 500,
        },
        {
            "id": "under_budget_all",
            "name": "Budget master",
            "description": "Respecter tous les budgets ce mois-ci",
            "difficulty": "hard",
            "reward": "🏆 Champion",
            "savings_potential": 300,
        },
    ]

    @classmethod
    def get_available_challenges(
        cls, df_history: pd.DataFrame, current_month_df: pd.DataFrame
    ) -> list[dict]:
        """
        Retourne les challenges disponibles selon le contexte.

        Args:
            df_history: Historique complet
            current_month_df: Mois en cours

        Returns:
            Liste des challenges avec statut
        """
        challenges = []

        for challenge in cls.CHALLENGES:
            challenge_with_status = challenge.copy()
            challenge_with_status["status"] = "available"
            challenge_with_status["progress"] = 0

            # Vérifier si déjà en cours ou complété (depuis session)
            challenge_key = f"challenge_{challenge['id']}"
            if challenge_key in st.session_state:
                challenge_with_status["status"] = st.session_state[challenge_key]

            # Calculer la progression si applicable
            if challenge["id"] == "category_reduction_20" and not current_month_df.empty:
                # Vérifier si une catégorie est en réduction
                # Simplifié
                pass

            challenges.append(challenge_with_status)

        return challenges

    @classmethod
    def start_challenge(cls, challenge_id: str):
        """Démarre un challenge."""
        st.session_state[f"challenge_{challenge_id}"] = "active"
        st.session_state[f"challenge_{challenge_id}_start"] = datetime.now()

    @classmethod
    def complete_challenge(cls, challenge_id: str):
        """Marque un challenge comme complété."""
        st.session_state[f"challenge_{challenge_id}"] = "completed"
        st.balloons()
        st.success(f"🎉 Challenge '{challenge_id}' réussi !")


def render_dynamic_budget_suggestions(engine: DynamicBudgetEngine):
    """
    Affiche les suggestions d'ajustement de budgets.
    """
    st.subheader("🎯 Ajustements de Budgets Recommandés")
    st.caption("Basé sur vos habitudes des 6 derniers mois")

    suggestions = engine.suggest_budget_adjustments()

    if not suggestions:
        st.success("✅ Vos budgets sont bien calibrés !")
        return

    for sugg in suggestions:
        with st.container(border=True):
            cols = st.columns([2, 2, 1])

            with cols[0]:
                st.markdown(f"**{sugg.category}**")
                st.caption(sugg.reason)

            with cols[1]:
                st.write(f"{sugg.current_budget:.0f}€ → **{sugg.suggested_budget:.0f}€**")
                if sugg.expected_savings > 0:
                    st.success(f"💰 +{sugg.expected_savings:.0f}€/mois")

            with cols[2]:
                risk_color = {"low": "🟢", "medium": "🟠", "high": "🔴"}
                st.markdown(f"### {risk_color.get(sugg.risk_level, '⚪')}")

                if st.button("Appliquer", key=f"apply_{sugg.category}", use_container_width=True):
                    try:
                        set_budget(sugg.category, sugg.suggested_budget)
                        st.success(f"Budget {sugg.category} mis à jour !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {e}")


def render_seasonal_adjustments(engine: DynamicBudgetEngine):
    """
    Affiche les ajustements saisonniers.
    """
    st.subheader("📅 Ajustements Saisonniers")

    budgets = get_budgets()
    if budgets.empty:
        return

    current_month = datetime.now().month
    month_names = [
        "",
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    ]

    st.caption(f"Prévisions pour **{month_names[current_month]}**")

    for _, budget in budgets.iterrows():
        category = budget["category"]
        base = budget["amount"]

        adjusted, reason = engine.get_current_month_adjustment(category, base)

        if adjusted != base:
            with st.container():
                cols = st.columns([2, 1, 1])
                with cols[0]:
                    st.write(f"**{category}**")
                with cols[1]:
                    diff = adjusted - base
                    color = "green" if diff < 0 else "orange"
                    st.markdown(f":{color}[{base:.0f}€ → {adjusted:.0f}€]")
                with cols[2]:
                    st.caption(reason)


def render_challenges_section(df_history: pd.DataFrame, current_month_df: pd.DataFrame):
    """
    Affiche la section des challenges d'économies.
    """
    st.subheader("🏆 Challenges d'Économies")
    st.caption("Relevez des défis pour améliorer vos finances")

    challenges = BudgetChallenge.get_available_challenges(df_history, current_month_df)

    # Grouper par difficulté
    easy = [c for c in challenges if c["difficulty"] == "easy"]
    medium = [c for c in challenges if c["difficulty"] == "medium"]
    hard = [c for c in challenges if c["difficulty"] == "hard"]

    tab_easy, tab_medium, tab_hard = st.tabs(["Facile", "Moyen", "Difficile"])

    for tab, challenge_list in [(tab_easy, easy), (tab_medium, medium), (tab_hard, hard)]:
        with tab:
            for challenge in challenge_list:
                _render_challenge_card(challenge)


def _render_challenge_card(challenge: dict):
    """Rendu d'une carte de challenge."""
    status_icons = {"available": "⚪", "active": "🔵", "completed": "✅"}

    with st.container(border=True):
        cols = st.columns([3, 1, 1])

        with cols[0]:
            st.markdown(f"**{challenge['name']}** {status_icons.get(challenge['status'], '⚪')}")
            st.caption(challenge["description"])
            st.caption(f"🏅 Récompense: {challenge['reward']}")

        with cols[1]:
            st.caption("💰 Potentiel")
            st.write(f"**{challenge['savings_potential']}€**")

        with cols[2]:
            if challenge["status"] == "available":
                if st.button("Relever", key=f"start_{challenge['id']}", type="primary"):
                    BudgetChallenge.start_challenge(challenge["id"])
                    st.rerun()
            elif challenge["status"] == "active":
                st.progress(challenge.get("progress", 0) / 100, text="En cours...")
                if st.button("Abandonner", key=f"cancel_{challenge['id']}"):
                    del st.session_state[f"challenge_{challenge['id']}"]
                    st.rerun()
            elif challenge["status"] == "completed":
                st.success("✅ Complété !")


# Import pour les fonctions de rendu
import streamlit as st

__all__ = [
    "DynamicBudgetEngine",
    "BudgetChallenge",
    "render_dynamic_budget_suggestions",
    "render_seasonal_adjustments",
    "render_challenges_section",
]
