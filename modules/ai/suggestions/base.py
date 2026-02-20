"""Base class for all analyzers."""

from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from modules.ai.suggestions.models import AnalysisContext, Suggestion
from modules.logger import logger


class BaseAnalyzer(ABC):
    """Base class for all suggestion analyzers.

    All analyzers must inherit from this class and implement the analyze method.

    Example:
        class MyAnalyzer(BaseAnalyzer):
            def analyze(self, context: AnalysisContext) -> list[Suggestion]:
                suggestions = []
                # Analysis logic here
                return suggestions
    """

    def __init__(self, name: str = None):
        """Initialize analyzer.

        Args:
            name: Analyzer name (for logging)
        """
        self.name = name or self.__class__.__name__

    @abstractmethod
    def analyze(self, context: AnalysisContext) -> list[Suggestion]:
        """Analyze data and return suggestions.

        Args:
            context: Analysis context containing all necessary data

        Returns:
            List of suggestions
        """
        pass

    def run(self, context: AnalysisContext) -> list[Suggestion]:
        """Run analyzer with error handling.

        Args:
            context: Analysis context

        Returns:
            List of suggestions (empty if analysis failed)
        """
        try:
            return self.analyze(context)
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            return []

    def _generate_id(self, prefix: str, *parts) -> str:
        """Generate a unique ID for a suggestion.

        Args:
            prefix: ID prefix
            *parts: Additional parts to include in ID

        Returns:
            Generated ID string
        """
        parts_str = "_".join(str(p) for p in parts if p)
        return f"{prefix}_{parts_str}".lower().replace(" ", "_")

    def _get_pending_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get pending (unvalidated) transactions.

        Args:
            df: Transactions DataFrame

        Returns:
            Filtered DataFrame with only pending transactions
        """
        if df.empty or "status" not in df.columns:
            return pd.DataFrame()
        return df[df["status"] == "pending"]

    def _get_validated_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get validated transactions.

        Args:
            df: Transactions DataFrame

        Returns:
            Filtered DataFrame with only validated transactions
        """
        if df.empty or "status" not in df.columns:
            return df
        return df[df["status"] == "validated"]

    def _get_expenses(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get expense transactions (negative amounts).

        Args:
            df: Transactions DataFrame

        Returns:
            Filtered DataFrame with only expenses
        """
        if df.empty or "amount" not in df.columns:
            return pd.DataFrame()
        return df[df["amount"] < 0]

    def _get_income(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get income transactions (positive amounts).

        Args:
            df: Transactions DataFrame

        Returns:
            Filtered DataFrame with only income
        """
        if df.empty or "amount" not in df.columns:
            return pd.DataFrame()
        return df[df["amount"] > 0]
