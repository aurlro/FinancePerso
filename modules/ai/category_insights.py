"""
Category Insights Engine
Génère des recommandations intelligentes par catégorie de budget.
Détecte les anomalies et propose des actions contextuelles.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from modules.logger import logger


@dataclass
class CategoryInsight:
    """Insight généré pour une catégorie."""

    category: str
    insight_type: str  # 'anomaly', 'trend', 'suggestion', 'alert'
    severity: str  # 'high', 'medium', 'low'
    title: str
    description: str
    action: Optional[str] = None
    action_link: Optional[str] = None
    amount: Optional[float] = None
    savings_potential: Optional[float] = None


@dataclass
class TransactionAnomaly:
    """Anomalie détectée dans une transaction."""

    transaction_id: int
    label: str
    amount: float
    date: str
    anomaly_type: str  # 'unusual_amount', 'unusual_frequency', 'new_merchant'
    expected_amount: Optional[float] = None
    deviation_percent: Optional[float] = None


class CategoryInsightsEngine:
    """
    Engine d'analyse par catégorie pour générer des insights actionnables.
    """

    def __init__(self, df_full: pd.DataFrame):
        """
        Initialize avec l'historique complet des transactions.

        Args:
            df_full: DataFrame avec toutes les transactions (doit avoir date_dt, category_validated, amount, label)
        """
        self.df = df_full.copy()
        if not self.df.empty and "date_dt" in self.df.columns:
            self.df["date_dt"] = pd.to_datetime(self.df["date_dt"])

    def get_category_insights(
        self, category: str, current_month_df: pd.DataFrame
    ) -> List[CategoryInsight]:
        """
        Génère tous les insights pour une catégorie donnée.

        Args:
            category: Nom de la catégorie
            current_month_df: DataFrame du mois en cours

        Returns:
            Liste d'insights triés par sévérité
        """
        insights = []

        if self.df.empty:
            return insights

        # Filtrer les données de cette catégorie (toutes les transactions, pas seulement amount < 0)
        # Un remboursement (amount > 0) dans une catégorie de dépense doit être inclus
        cat_history = self.df[self.df["category_validated"] == category].copy()

        cat_current = current_month_df[current_month_df["category_validated"] == category].copy()

        if cat_history.empty or cat_current.empty:
            return insights

        cat_history["amount"] = cat_history["amount"].abs()
        cat_current["amount"] = cat_current["amount"].abs()

        # 1. Détecter les anomalies de montant
        insights.extend(self._detect_amount_anomalies(category, cat_history, cat_current))

        # 2. Analyser la tendance
        insights.extend(self._analyze_trend(category, cat_history, cat_current))

        # 3. Détecter nouveaux commerçants
        insights.extend(self._detect_new_merchants(category, cat_history, cat_current))

        # 4. Générer des suggestions d'économies
        insights.extend(self._generate_savings_suggestions(category, cat_history, cat_current))

        # Trier par sévérité
        severity_order = {"high": 0, "medium": 1, "low": 2}
        insights.sort(key=lambda x: severity_order.get(x.severity, 3))

        return insights

    def _detect_amount_anomalies(
        self, category: str, history: pd.DataFrame, current: pd.DataFrame
    ) -> List[CategoryInsight]:
        """Détecte les transactions avec des montants inhabituels."""
        insights = []

        # Calculer les stats historiques (3 derniers mois exclu mois courant)
        three_months_ago = datetime.now() - timedelta(days=90)
        recent_history = history[history["date_dt"] < three_months_ago]

        if len(recent_history) < 3:
            return insights

        mean_amount = recent_history["amount"].mean()
        std_amount = recent_history["amount"].std()

        if std_amount == 0:
            return insights

        # Détecter les transactions anormales
        for _, tx in current.iterrows():
            amount = tx["amount"]
            z_score = (amount - mean_amount) / std_amount

            if z_score > 2.5:  # > 2.5 écarts-types
                deviation = ((amount - mean_amount) / mean_amount) * 100
                insights.append(
                    CategoryInsight(
                        category=category,
                        insight_type="anomaly",
                        severity="high" if z_score > 3 else "medium",
                        title=f"🚨 Dépense inhabituelle",
                        description=f"'{tx['label']}' à {amount:.0f}€ est {deviation:.0f}% plus élevé que d'habitude (moyenne: {mean_amount:.0f}€)",
                        action="Vérifier cette transaction",
                        amount=amount,
                        savings_potential=amount - mean_amount,
                    )
                )

        return insights

    def _analyze_trend(
        self, category: str, history: pd.DataFrame, current: pd.DataFrame
    ) -> List[CategoryInsight]:
        """Analyse la tendance par rapport aux mois précédents."""
        insights = []

        # Grouper par mois
        history["month"] = history["date_dt"].dt.to_period("M")
        monthly_spend = history.groupby("month")["amount"].sum()

        if len(monthly_spend) < 2:
            return insights

        # Moyenne des 3 derniers mois complets
        avg_last_3 = monthly_spend.tail(3).mean()
        current_total = current["amount"].sum()

        if avg_last_3 > 0:
            change_pct = ((current_total - avg_last_3) / avg_last_3) * 100

            if change_pct > 30:
                insights.append(
                    CategoryInsight(
                        category=category,
                        insight_type="trend",
                        severity="high" if change_pct > 50 else "medium",
                        title=f"📈 Forte augmentation",
                        description=f"Vos dépenses '{category}' ont augmenté de {change_pct:.0f}% par rapport à la moyenne ({avg_last_3:.0f}€ → {current_total:.0f}€)",
                        action="Analyser les causes",
                        amount=current_total,
                        savings_potential=current_total - avg_last_3,
                    )
                )
            elif change_pct < -20:
                insights.append(
                    CategoryInsight(
                        category=category,
                        insight_type="trend",
                        severity="low",
                        title=f"📉 Réussite !",
                        description=f"Vous avez réduit vos dépenses '{category}' de {abs(change_pct):.0f}% par rapport à la moyenne. Continuez ainsi !",
                        action="Voir le détail",
                    )
                )

        return insights

    def _detect_new_merchants(
        self, category: str, history: pd.DataFrame, current: pd.DataFrame
    ) -> List[CategoryInsight]:
        """Détecte les nouveaux commerçants ou libellés."""
        insights = []

        # Extraire les noms uniques (simplifié)
        known_labels = set(history["label"].str.lower().unique())

        new_transactions = []
        for _, tx in current.iterrows():
            label_lower = tx["label"].lower()
            # Vérifier si similaire à un existant
            is_new = True
            for known in known_labels:
                if label_lower in known or known in label_lower:
                    is_new = False
                    break

            if is_new:
                new_transactions.append(tx)

        if new_transactions:
            total_new = sum(tx["amount"] for tx in new_transactions)
            insights.append(
                CategoryInsight(
                    category=category,
                    insight_type="suggestion",
                    severity="low",
                    title=f"🆕 Nouvelles dépenses détectées",
                    description=f"{len(new_transactions)} nouvelle(s) dépense(s) dans '{category}' pour un total de {total_new:.0f}€",
                    action="Vérifier et catégoriser",
                )
            )

        return insights

    def _generate_savings_suggestions(
        self, category: str, history: pd.DataFrame, current: pd.DataFrame
    ) -> List[CategoryInsight]:
        """Génère des suggestions d'économies."""
        insights = []

        # Analyser la fréquence
        current_month = datetime.now().month
        current_year = datetime.now().year

        # Nombre de transactions ce mois
        tx_count_current = len(current)

        # Moyenne mensuelle historique
        history["month"] = history["date_dt"].dt.to_period("M")
        monthly_counts = history.groupby("month").size()
        avg_tx_per_month = monthly_counts.mean()

        if tx_count_current > avg_tx_per_month * 1.5:
            # Trop de petites transactions
            avg_amount = current["amount"].mean()
            potential_savings = (tx_count_current - avg_tx_per_month) * avg_amount * 0.5

            insights.append(
                CategoryInsight(
                    category=category,
                    insight_type="suggestion",
                    severity="medium",
                    title=f"💡 Opportunité d'économie",
                    description=f"Vous faites {tx_count_current} transactions ce mois contre {avg_tx_per_month:.0f} en moyenne. En regroupant vos achats, vous pourriez économiser ~{potential_savings:.0f}€/mois",
                    action="Voir les fréquences",
                    savings_potential=potential_savings,
                )
            )

        return insights

    def get_top_insights(
        self, current_month_df: pd.DataFrame, max_insights: int = 5
    ) -> List[CategoryInsight]:
        """
        Récupère les insights les plus importants sur toutes les catégories.

        Args:
            current_month_df: DataFrame du mois en cours
            max_insights: Nombre maximum d'insights à retourner

        Returns:
            Liste des insights prioritaires
        """
        all_insights = []

        # Obtenir les catégories uniques du mois courant
        if current_month_df.empty or "category_validated" not in current_month_df.columns:
            return all_insights

        # Obtenir les catégories uniques (sans filtrer par amount, car une catégorie de dépense
        # peut avoir des remboursements avec amount > 0)
        from modules.transaction_types import is_expense_category

        categories = current_month_df[
            current_month_df["category_validated"].apply(is_expense_category)
        ]["category_validated"].unique()

        for category in categories:
            insights = self.get_category_insights(category, current_month_df)
            all_insights.extend(insights)

        # Trier par sévérité et potentiel d'économie
        severity_order = {"high": 0, "medium": 1, "low": 2}
        all_insights.sort(
            key=lambda x: (severity_order.get(x.severity, 3), -(x.savings_potential or 0))
        )

        return all_insights[:max_insights]

    def get_anomalous_transactions(
        self, category: str, current_month_df: pd.DataFrame
    ) -> List[TransactionAnomaly]:
        """
        Récupère les transactions anormales pour une catégorie.

        Args:
            category: Catégorie à analyser
            current_month_df: DataFrame du mois en cours

        Returns:
            Liste des anomalies détectées
        """
        anomalies = []

        # Inclure toutes les transactions de la catégorie (pas seulement amount < 0)
        cat_history = self.df[self.df["category_validated"] == category].copy()

        cat_current = current_month_df[current_month_df["category_validated"] == category].copy()

        if cat_history.empty or cat_current.empty:
            return anomalies

        cat_history["amount"] = cat_history["amount"].abs()
        cat_current["amount"] = cat_current["amount"].abs()

        # Calculer stats
        mean_amount = cat_history["amount"].mean()
        std_amount = cat_history["amount"].std()

        if std_amount == 0:
            return anomalies

        for _, tx in cat_current.iterrows():
            amount = tx["amount"]
            z_score = (amount - mean_amount) / std_amount

            if z_score > 2.0:
                anomalies.append(
                    TransactionAnomaly(
                        transaction_id=int(tx.get("id", 0)),
                        label=tx.get("label", "Inconnu"),
                        amount=amount,
                        date=str(tx.get("date", "")),
                        anomaly_type="unusual_amount",
                        expected_amount=mean_amount,
                        deviation_percent=((amount - mean_amount) / mean_amount) * 100,
                    )
                )

        return anomalies


def render_category_insights_card(insight: CategoryInsight):
    """
    Rendu Streamlit d'une carte d'insight.

    Args:
        insight: L'insight à afficher
    """
    color_map = {"high": "🔴", "medium": "🟠", "low": "🟢"}

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{insight.title}** — *{insight.category}*")
            st.write(insight.description)

            if insight.savings_potential and insight.savings_potential > 0:
                st.caption(f"💰 Potentiel d'économie: **{insight.savings_potential:.0f}€/mois**")

        with col2:
            st.markdown(f"### {color_map.get(insight.severity, '⚪')}")
            if insight.action:
                if st.button(
                    insight.action,
                    key=f"insight_{insight.category}_{insight.insight_type}",
                    use_container_width=True,
                ):
                    st.toast(f"Action: {insight.action}", icon="💡")


# Fonction utilitaire pour intégration rapide
def get_smart_recommendations(df_full: pd.DataFrame, df_current: pd.DataFrame) -> Dict:
    """
    Fonction simple pour obtenir des recommandations intelligentes.

    Args:
        df_full: Historique complet
        df_current: Mois en cours

    Returns:
        Dict avec insights et anomalies
    """
    engine = CategoryInsightsEngine(df_full)

    insights = engine.get_top_insights(df_current, max_insights=5)

    # Calculer le potentiel total d'économies
    total_savings = sum(i.savings_potential for i in insights if i.savings_potential)

    return {
        "insights": insights,
        "total_savings_potential": total_savings,
        "count_by_severity": {
            "high": sum(1 for i in insights if i.severity == "high"),
            "medium": sum(1 for i in insights if i.severity == "medium"),
            "low": sum(1 for i in insights if i.severity == "low"),
        },
    }
