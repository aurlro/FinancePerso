"""Member-related analyzers."""

from modules.ai.suggestions.base import BaseAnalyzer
from modules.ai.suggestions.models import AnalysisContext, Priority, Suggestion, SuggestionType


class UnknownMemberAnalyzer(BaseAnalyzer):
    """Suggest member mappings for transactions with unknown members."""

    def __init__(self):
        super().__init__("UnknownMemberAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_transactions():
            return suggestions

        unknown_df = context.transactions[context.transactions["member"] == "Inconnu"]

        if unknown_df.empty:
            return suggestions

        # Group by card suffix
        card_groups = unknown_df[unknown_df["card_suffix"].notna()].groupby("card_suffix").size()

        for card_suffix, count in card_groups.head(3).items():
            if count >= 3:
                suggestions.append(
                    Suggestion(
                        id=self._generate_id("member_card", card_suffix),
                        type=SuggestionType.MEMBER.value,
                        priority=Priority.MEDIUM.value,
                        title=f"💳 Carte non identifiée : ...{card_suffix}",
                        description=(
                            f"{count} transactions avec cette carte n'ont pas de "
                            f"membre attribué. Mappez cette carte pour une "
                            f"attribution automatique."
                        ),
                        action_label="Mapper la carte",
                        action_data={"card_suffix": card_suffix, "type": "map_card"},
                        impact_score=min(count * 8, 90),
                        auto_fixable=False,
                    )
                )

        # Group by account
        account_groups = (
            unknown_df[unknown_df["account_label"].notna()].groupby("account_label").size()
        )

        for account, count in account_groups.head(2).items():
            if count >= 5:
                suggestions.append(
                    Suggestion(
                        id=self._generate_id("member_acc", hash(account) % 10000),
                        type=SuggestionType.MEMBER.value,
                        priority=Priority.HIGH.value,
                        title=f"🏦 Compte sans membre par défaut : {account}",
                        description=(
                            f"{count} transactions 'Inconnu' sur ce compte. "
                            f"Définissez un membre par défaut pour ce compte."
                        ),
                        action_label="Définir membre",
                        action_data={"account_label": account, "type": "map_account"},
                        impact_score=min(count * 5, 85),
                        auto_fixable=False,
                    )
                )

        return suggestions


class BeneficiaryAnalyzer(BaseAnalyzer):
    """Suggest mapping frequent beneficiaries."""

    def __init__(self):
        super().__init__("BeneficiaryAnalyzer")

    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        suggestions = []

        if not context.has_transactions():
            return suggestions

        # Check beneficiary field
        if "beneficiary" not in context.transactions.columns:
            return suggestions

        beneficiaries = context.transactions[
            (context.transactions["beneficiary"].notna())
            & (context.transactions["beneficiary"] != "")
            & (context.transactions["beneficiary"] != "Inconnu")
            & (context.transactions["beneficiary"] != "Famille")
        ]

        if beneficiaries.empty:
            return suggestions

        # Count by beneficiary
        ben_counts = beneficiaries["beneficiary"].value_counts().head(5)

        # Get existing member names
        existing_members = set()
        if context.has_members():
            existing_members = set(context.members["name"].str.lower().tolist())

        for beneficiary, count in ben_counts.items():
            if count >= 5 and beneficiary.lower() not in existing_members:
                suggestions.append(
                    Suggestion(
                        id=self._generate_id("benef", hash(beneficiary) % 10000),
                        type=SuggestionType.MEMBER.value,
                        priority=Priority.LOW.value,
                        title=f"👤 Bénéficiaire fréquent : {beneficiary}",
                        description=(
                            f"{count} transactions vers '{beneficiary}'. Ajoutez "
                            f"comme membre pour de meilleures statistiques."
                        ),
                        action_label="Ajouter membre",
                        action_data={"name": beneficiary, "type": "add_member"},
                        impact_score=min(count * 5, 60),
                        auto_fixable=False,
                    )
                )

        return suggestions
