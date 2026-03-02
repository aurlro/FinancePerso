"""
Scenario simulation for financial planning.
What-if analysis for major financial decisions.
"""

from enum import Enum
from dataclasses import dataclass

import pandas as pd

from modules.cashflow.predictor import predict_monthly_cashflow, CashflowPrediction
from modules.logger import logger


class ScenarioType(Enum):
    MAJOR_PURCHASE = "major_purchase"  # e.g., buying a car
    INCOME_CHANGE = "income_change"  # e.g., new job, salary raise
    NEW_RECURRING = "new_recurring"  # e.g., new rent, subscription
    ONE_TIME_EXPENSE = "one_time_expense"  # e.g., vacation, medical
    EMERGENCY_FUND = "emergency_fund"  # Building emergency savings


@dataclass
class Scenario:
    """A financial scenario to simulate."""

    name: str
    type: ScenarioType
    amount: float
    timing_months: int  # When it happens (0 = this month)
    recurring: bool = False
    duration_months: int = 0  # For recurring changes


@dataclass
class ScenarioResult:
    """Result of a scenario simulation."""

    scenario: Scenario
    baseline_predictions: list[CashflowPrediction]
    scenario_predictions: list[CashflowPrediction]
    impact: float  # Difference in final balance
    is_viable: bool  # Does it avoid negative balance?
    warnings: list[str]


def simulate_scenario(scenario: Scenario) -> ScenarioResult | None:
    """
    Simulate a financial scenario and compare to baseline.

    Args:
        scenario: The scenario to simulate

    Returns:
        ScenarioResult with comparison data
    """
    try:
        # Get baseline prediction
        baseline = predict_monthly_cashflow(months_ahead=6)
        if not baseline:
            return None

        # Create scenario prediction (modify baseline)
        scenario_preds = []
        for i, month in enumerate(baseline):
            new_month = CashflowPrediction(
                start_date=month.start_date,
                end_date=month.end_date,
                starting_balance=month.starting_balance,
                predicted_income=month.predicted_income,
                predicted_expenses=month.predicted_expenses,
                predicted_balance=month.predicted_balance,
                confidence=month.confidence,
                warnings=month.warnings.copy(),
            )

            # Apply scenario effects
            if scenario.timing_months <= i:
                if scenario.recurring and (
                    scenario.duration_months == 0
                    or i < scenario.timing_months + scenario.duration_months
                ):
                    # Recurring monthly change
                    if scenario.type in [ScenarioType.INCOME_CHANGE]:
                        new_month.predicted_income += scenario.amount
                    else:
                        new_month.predicted_expenses -= scenario.amount  # Expenses are negative
                elif not scenario.recurring and i == scenario.timing_months:
                    # One-time change
                    if scenario.type == ScenarioType.INCOME_CHANGE:
                        new_month.predicted_income += scenario.amount
                    else:
                        new_month.predicted_expenses -= scenario.amount

                # Recalculate balance
                new_month.predicted_balance = (
                    new_month.starting_balance
                    + new_month.predicted_income
                    + new_month.predicted_expenses
                )

            scenario_preds.append(new_month)

        # Calculate impact
        baseline_final = baseline[-1].predicted_balance
        scenario_final = scenario_preds[-1].predicted_balance
        impact = scenario_final - baseline_final

        # Check viability
        is_viable = all(p.predicted_balance >= 0 for p in scenario_preds)

        # Generate warnings
        warnings = []
        if not is_viable:
            warnings.append("⚠️ Ce scénario entraînerait un découvert!")
        if any(p.predicted_balance < 500 for p in scenario_preds):
            warnings.append("⚠️ Solde faible prévu avec ce scénario")

        return ScenarioResult(
            scenario=scenario,
            baseline_predictions=baseline,
            scenario_predictions=scenario_preds,
            impact=impact,
            is_viable=is_viable,
            warnings=warnings,
        )

    except Exception as e:
        logger.error(f"Error simulating scenario: {e}")
        return None


def render_scenario_simulator():
    """Render scenario simulator in Streamlit."""
    import streamlit as st

    st.subheader("🔮 Simulateur de scénarios")

    scenario_type = st.selectbox(
        "Type de scénario",
        options=[
            ("Achat important", ScenarioType.MAJOR_PURCHASE),
            ("Changement de revenus", ScenarioType.INCOME_CHANGE),
            ("Nouvelle dépense récurrente", ScenarioType.NEW_RECURRING),
            ("Dépense ponctuelle", ScenarioType.ONE_TIME_EXPENSE),
        ],
        format_func=lambda x: x[0],
    )[1]

    amount = st.number_input("Montant (€)", value=1000.0, step=100.0)
    if scenario_type in [ScenarioType.MAJOR_PURCHASE, ScenarioType.ONE_TIME_EXPENSE]:
        amount = -abs(amount)

    timing = st.slider("Quand? (mois)", 0, 6, 0)

    recurring = st.checkbox("Dépense/Revenu récurrent")

    if st.button("Simuler"):
        scenario = Scenario(
            name=f"Simulation {scenario_type.value}",
            type=scenario_type,
            amount=amount,
            timing_months=timing,
            recurring=recurring,
        )

        result = simulate_scenario(scenario)
        if result:
            st.metric(
                "Impact sur le solde (6 mois)",
                f"{result.impact:,.2f}€",
                delta=" viable" if result.is_viable else "⚠️ risqué",
            )

            for warning in result.warnings:
                st.warning(warning)
