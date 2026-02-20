"""Income analysis analyzer."""

from modules.ai.suggestions.base import BaseAnalyzer
from modules.ai.suggestions.models import AnalysisContext, Priority, Suggestion, SuggestionType


class IncomeVariationAnalyzer(BaseAnalyzer):
    """Detect income variations (drops or increases)."""

    def __init__(self):
        super().__init__("IncomeVariationAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_transactions():
            return suggestions

        income = self._get_income(context.transactions)

        if income.empty:
            return suggestions

        income = income.copy()
        income["month"] = income["date"].str[:7]
        monthly_income = income.groupby("month")["amount"].sum()

        if len(monthly_income) < 3:
            return suggestions

        # Calculate average excluding last month
        historical_avg = monthly_income.iloc[:-1].mean()
        last_month = monthly_income.iloc[-1]

        variation_pct = abs((last_month - historical_avg) / historical_avg * 100)

        if variation_pct > 20:  # Significant variation
            if last_month < historical_avg:
                suggestions.append(
                    Suggestion(
                        id="income_drop",
                        type=SuggestionType.PATTERN.value,
                        priority=Priority.HIGH.value,
                        title=f"📉 Baisse des revenus ({variation_pct:.0f}%)",
                        description=f"Revenus du mois : {last_month:.0f}€ vs moyenne : {historical_avg:.0f}€. Vérifiez vos sources de revenus.",
                        action_label="Analyser",
                        action_data={"type": "view_income_analysis"},
                        impact_score=min(int(variation_pct), 100),
                        auto_fixable=False,
                    )
                )
            else:
                suggestions.append(
                    Suggestion(
                        id="income_increase",
                        type=SuggestionType.PATTERN.value,
                        priority=Priority.LOW.value,
                        title=f"📈 Hausse des revenus (+{variation_pct:.0f}%)",
                        description=f"Excellent ! Revenus du mois : {last_month:.0f}€ vs moyenne : {historical_avg:.0f}€.",
                        action_label="Voir détails",
                        action_data={"type": "view_income_analysis"},
                        impact_score=min(int(variation_pct / 2), 100),
                        auto_fixable=False,
                    )
                )

        return suggestions
