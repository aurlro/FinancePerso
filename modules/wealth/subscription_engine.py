"""
Moteur de Détection de Récurrence - Subscription Detector
=========================================================

Ce module implémente un algorithme de détection des abonnements et charges fixes
basé sur l'analyse temporelle et la stabilité des montants.

Usage:
    from modules.wealth.subscription_engine import SubscriptionDetector

    detector = SubscriptionDetector()
    subscriptions = detector.detect_subscriptions(df_transactions)

    for sub in subscriptions:
        print(f"{sub.merchant}: {sub.frequency} - {sub.average_amount}€")

Contraintes:
- Approche probabiliste/mathématique (pas d'IA lourde)
- Gestion des doubles prélèvements (30 du mois + 1er du mois suivant)
- Exclusion des virements internes
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Tuple
import statistics

import pandas as pd
import numpy as np

from modules.wealth.data_cleaning import clean_transaction_label
from modules.logger import logger


class SubscriptionStatus(Enum):
    """Statut d'un abonnement détecté."""

    ACTIF = "ACTIF"
    A_RISQUE = "A_RISQUE"  # Variation anormale détectée
    ZOMBIE = "ZOMBIE"  # Pas de transaction depuis > 45j (mensuel)
    INACTIF = "INACTIF"  # Résilié ou suspendu


class FrequencyType(Enum):
    """Types de fréquences supportées."""

    HEBDOMADAIRE = "weekly"  # 6-8 jours
    MENSUEL = "monthly"  # 28-32 jours
    BIMENSUEL = "bimonthly"  # 13-16 jours
    TRIMESTRIEL = "quarterly"  # 85-95 jours
    SEMESTRIEL = "semiannual"  # 175-185 jours
    ANNUEL = "annual"  # 360-370 jours
    IRREGULIER = "irregular"  # Non détecté


# Fenêtres de détection pour chaque fréquence (en jours)
FREQUENCY_WINDOWS = {
    FrequencyType.HEBDOMADAIRE: (6, 8),
    FrequencyType.BIMENSUEL: (13, 16),
    FrequencyType.MENSUEL: (28, 32),
    FrequencyType.TRIMESTRIEL: (85, 95),
    FrequencyType.SEMESTRIEL: (175, 185),
    FrequencyType.ANNUEL: (360, 370),
}

# Seuils pour statut ZOMBIE (en jours, selon fréquence)
ZOMBIE_THRESHOLDS = {
    FrequencyType.HEBDOMADAIRE: 14,
    FrequencyType.BIMENSUEL: 30,
    FrequencyType.MENSUEL: 45,
    FrequencyType.TRIMESTRIEL: 120,
    FrequencyType.SEMESTRIEL: 200,
    FrequencyType.ANNUEL: 400,
}


@dataclass
class Subscription:
    """
    Représentation d'un abonnement/charge fixe détecté.

    Attributes:
        merchant: Nom du commerçant (clean_merchant)
        frequency: Type de fréquence (monthly, weekly, etc.)
        average_amount: Montant moyen
        amount_std: Écart-type des montants
        last_date: Dernière date de prélèvement
        next_expected_date: Date prévue du prochain prélèvement
        confidence_score: Score de confiance (0-1)
        status: Statut (ACTIF, A_RISQUE, ZOMBIE, INACTIF)
        transaction_count: Nombre de transactions analysées
        category: Catégorie PFCv2
        metadata: Métadonnées additionnelles
    """

    merchant: str
    frequency: str
    average_amount: float
    amount_std: float
    last_date: str
    next_expected_date: str
    confidence_score: float
    status: str
    transaction_count: int
    category: Optional[str] = None
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convertit l'abonnement en dictionnaire."""
        return {
            "merchant": self.merchant,
            "frequency": self.frequency,
            "average_amount": round(self.average_amount, 2),
            "amount_std": round(self.amount_std, 2),
            "last_date": self.last_date,
            "next_expected_date": self.next_expected_date,
            "confidence_score": round(self.confidence_score, 2),
            "status": self.status,
            "transaction_count": self.transaction_count,
            "category": self.category,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convertit l'abonnement en JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class RemainingBudgetResult:
    """
    Résultat du calcul du Reste à Vivre.

    Attributes:
        current_balance: Solde actuel du compte
        days_ahead: Période de projection en jours
        upcoming_charges: Liste des charges à venir avec dates
        total_upcoming: Montant total des charges à venir
        remaining_budget: "Reste à vivre" après charges
        percentage_remaining: Pourcentage du budget restant
        status: Statut du budget (ok, warning, critical)
        daily_budget: Budget quotidien disponible
    """

    current_balance: float
    days_ahead: int
    upcoming_charges: List[Dict]
    total_upcoming: float
    remaining_budget: float
    percentage_remaining: float
    status: str
    daily_budget: float

    def to_dict(self) -> Dict:
        """Convertit le résultat en dictionnaire."""
        return {
            "current_balance": round(self.current_balance, 2),
            "days_ahead": self.days_ahead,
            "upcoming_charges": self.upcoming_charges,
            "total_upcoming": round(self.total_upcoming, 2),
            "remaining_budget": round(self.remaining_budget, 2),
            "percentage_remaining": round(self.percentage_remaining, 1),
            "status": self.status,
            "daily_budget": round(self.daily_budget, 2),
        }


class SubscriptionDetector:
    """
    Détecteur d'abonnements basé sur l'analyse temporelle et statistique.

    Algorithme:
    1. Groupement par clean_merchant
    2. Analyse des intervalles entre transactions
    3. Identification de la fréquence (médiane des intervalles)
    4. Validation stabilité montant (écart-type < 20%)
    5. Détection des doubles prélèvements
    6. Assignation statut (ACTIF, ZOMBIE, etc.)

    Usage:
        detector = SubscriptionDetector(
            amount_tolerance=0.15,  # 15% variance montant
            date_tolerance=3,       # 3 jours variance date
            min_occurrences=3       # Minimum 3 transactions
        )
        subscriptions = detector.detect_subscriptions(df)
    """

    def __init__(
        self,
        amount_tolerance: float = 0.15,  # 15% variance montant
        date_tolerance: int = 3,  # 3 jours variance date
        min_occurrences: int = 3,  # Minimum 3 occurrences
        ignore_internal_transfers: bool = True,
    ):
        """
        Initialise le détecteur.

        Args:
            amount_tolerance: Variance acceptée sur le montant (0.15 = 15%)
            date_tolerance: Variance acceptée sur les dates (en jours)
            min_occurrences: Nombre minimum de transactions pour valider
            ignore_internal_transfers: Exclure les virements internes
        """
        self.amount_tolerance = amount_tolerance
        self.date_tolerance = date_tolerance
        self.min_occurrences = min_occurrences
        self.ignore_internal_transfers = ignore_internal_transfers

    def detect_subscriptions(
        self,
        df: pd.DataFrame,
        reference_date: Optional[datetime] = None,
    ) -> List[Subscription]:
        """
        Détecte tous les abonnements dans un DataFrame de transactions.

        Args:
            df: DataFrame avec colonnes [date, label, amount, category_validated]
            reference_date: Date de référence pour calculer next_expected_date

        Returns:
            Liste des abonnements détectés
        """
        if df.empty:
            return []

        if reference_date is None:
            reference_date = datetime.now()

        # Nettoyer et préparer les données
        data = self._prepare_data(df)
        if data.empty:
            return []

        subscriptions = []

        # Grouper par commerçant nettoyé
        for merchant, group in data.groupby("clean_merchant"):
            if len(group) < self.min_occurrences:
                continue

            # Analyser ce groupe
            subscription = self._analyze_merchant_group(merchant, group, reference_date)

            if subscription:
                subscriptions.append(subscription)

        # Trier par confiance décroissante
        subscriptions.sort(key=lambda x: x.confidence_score, reverse=True)

        logger.info(f"Détection terminée: {len(subscriptions)} abonnements trouvés")
        return subscriptions

    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prépare les données pour l'analyse."""
        data = df.copy()

        # Convertir les dates
        data["date"] = pd.to_datetime(data["date"])

        # Filtrer uniquement les dépenses (montants négatifs)
        data = data[data["amount"] < 0].copy()

        # Exclure les virements internes si demandé
        if self.ignore_internal_transfers:
            excluded_categories = ["Virement Interne", "Hors Budget", "Transfer"]
            data = data[~data["category_validated"].isin(excluded_categories)]

        # Nettoyer les libellés pour obtenir le commerçant
        data["clean_merchant"] = data["label"].apply(clean_transaction_label)

        # Supprimer les montants très faibles (arrondis, etc.)
        data = data[data["amount"].abs() > 1.0]

        return data

    def _analyze_merchant_group(
        self,
        merchant: str,
        group: pd.DataFrame,
        reference_date: datetime,
    ) -> Optional[Subscription]:
        """
        Analyse un groupe de transactions pour un commerçant.

        Args:
            merchant: Nom du commerçant
            group: DataFrame des transactions de ce commerçant
            reference_date: Date de référence

        Returns:
            Subscription si détecté, None sinon
        """
        # Trier par date
        group = group.sort_values("date")

        # Calculer les intervalles entre transactions
        dates = group["date"].tolist()
        amounts = group["amount"].abs().tolist()  # Valeurs absolues

        if len(dates) < self.min_occurrences:
            return None

        # Calculer les intervalles en jours
        intervals = []
        for i in range(1, len(dates)):
            delta = (dates[i] - dates[i - 1]).days
            if delta > 0:  # Ignorer les doublons même jour
                intervals.append(delta)

        if not intervals:
            return None

        # Détecter la fréquence
        frequency, confidence = self._detect_frequency(intervals)

        if frequency == FrequencyType.IRREGULIER:
            return None

        # Vérifier stabilité du montant
        amount_stability = self._check_amount_stability(amounts)

        # Combiner les scores de confiance
        final_confidence = confidence * amount_stability

        if final_confidence < 0.5:  # Seuil minimum
            return None

        # Calculer les statistiques
        avg_amount = statistics.mean(amounts)
        amount_std = statistics.stdev(amounts) if len(amounts) > 1 else 0

        # Déterminer le statut
        last_date = dates[-1]
        status = self._determine_status(
            frequency, last_date, reference_date, amount_std, avg_amount
        )

        # Prédire la prochaine date
        next_date = self._predict_next_date(frequency, last_date, reference_date)

        # Récupérer la catégorie la plus fréquente
        category = group["category_validated"].mode().iloc[0] if not group.empty else None

        # Métadonnées
        metadata = {
            "intervals": intervals,
            "median_interval": statistics.median(intervals),
            "amount_cv": (amount_std / avg_amount) if avg_amount > 0 else 0,
            "date_range": f"{dates[0].strftime('%Y-%m-%d')} to {last_date.strftime('%Y-%m-%d')}",
        }

        return Subscription(
            merchant=merchant,
            frequency=frequency.value,
            average_amount=avg_amount,
            amount_std=amount_std,
            last_date=last_date.strftime("%Y-%m-%d"),
            next_expected_date=next_date.strftime("%Y-%m-%d"),
            confidence_score=final_confidence,
            status=status.value,
            transaction_count=len(group),
            category=category,
            metadata=metadata,
        )

    def _detect_frequency(self, intervals: List[int]) -> Tuple[FrequencyType, float]:
        """
        Détecte la fréquence basée sur les intervalles.

        Returns:
            Tuple (frequency_type, confidence_score)
        """
        if not intervals:
            return FrequencyType.IRREGULIER, 0.0

        # Utiliser la médiane pour robustesse
        median_interval = statistics.median(intervals)

        # Calculer l'écart-type relatif
        if len(intervals) > 1:
            std = statistics.stdev(intervals)
            cv = std / median_interval if median_interval > 0 else float("inf")
        else:
            cv = 0

        # Tester chaque fréquence
        best_match = FrequencyType.IRREGULIER
        best_confidence = 0.0

        for freq, (min_days, max_days) in FREQUENCY_WINDOWS.items():
            # Vérifier si la médiane est dans la fenêtre
            if min_days <= median_interval <= max_days:
                # Calculer confiance basée sur la cohérence des intervalles
                # et la proximité avec le centre de la fenêtre
                center = (min_days + max_days) / 2
                distance_from_center = abs(median_interval - center) / (max_days - min_days)

                # Plus l'écart-type est faible, plus la confiance est haute
                consistency_score = max(0, 1 - cv)

                # Proximité au centre
                center_score = 1 - distance_from_center

                confidence = consistency_score * 0.7 + center_score * 0.3

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = freq

        return best_match, best_confidence

    def _check_amount_stability(self, amounts: List[float]) -> float:
        """
        Vérifie la stabilité des montants.

        Returns:
            Score de stabilité (0-1)
        """
        if len(amounts) < 2:
            return 0.5

        avg = statistics.mean(amounts)
        std = statistics.stdev(amounts)

        if avg == 0:
            return 0.0

        # Coefficient de variation
        cv = std / avg

        # Tolérance : 20% max
        if cv > 0.20:
            return max(0, 1 - (cv - 0.20) * 5)  # Pénalité progressive

        return 1.0

    def _determine_status(
        self,
        frequency: FrequencyType,
        last_date: datetime,
        reference_date: datetime,
        amount_std: float,
        avg_amount: float,
    ) -> SubscriptionStatus:
        """Détermine le statut de l'abonnement."""
        days_since_last = (reference_date - last_date).days

        # Vérifier si ZOMBIE (pas de transaction depuis longtemps)
        zombie_threshold = ZOMBIE_THRESHOLDS.get(frequency, 45)
        if days_since_last > zombie_threshold:
            return SubscriptionStatus.ZOMBIE

        # Vérifier variation anormale du montant
        if avg_amount > 0:
            cv = amount_std / avg_amount
            if cv > self.amount_tolerance:
                return SubscriptionStatus.A_RISQUE

        return SubscriptionStatus.ACTIF

    def _predict_next_date(
        self,
        frequency: FrequencyType,
        last_date: datetime,
        reference_date: datetime,
    ) -> datetime:
        """Prédit la prochaine date de prélèvement."""
        # Jours à ajouter selon la fréquence
        days_map = {
            FrequencyType.HEBDOMADAIRE: 7,
            FrequencyType.BIMENSUEL: 14,
            FrequencyType.MENSUEL: 30,
            FrequencyType.TRIMESTRIEL: 90,
            FrequencyType.SEMESTRIEL: 180,
            FrequencyType.ANNUEL: 365,
        }

        days = days_map.get(frequency, 30)
        next_date = last_date + timedelta(days=days)

        # Si la date prédite est déjà passée, ajuster
        while next_date < reference_date:
            next_date += timedelta(days=days)

        return next_date

    def detect_zombie_subscriptions(
        self,
        subscriptions: List[Subscription],
    ) -> List[Subscription]:
        """Filtre les abonnements ZOMBIE."""
        return [s for s in subscriptions if s.status == SubscriptionStatus.ZOMBIE.value]

    def detect_amount_increases(
        self,
        df: pd.DataFrame,
        threshold_percent: float = 15.0,
    ) -> List[Dict]:
        """
        Détecte les augmentations de montant suspects.

        Args:
            df: DataFrame des transactions
            threshold_percent: Seuil d'augmentation (en %)

        Returns:
            Liste des augmentations détectées
        """
        increases = []
        data = self._prepare_data(df)

        for merchant, group in data.groupby("clean_merchant"):
            group = group.sort_values("date")
            amounts = group["amount"].abs().tolist()

            if len(amounts) < 2:
                continue

            # Comparer montant moyen historique vs récent
            split = len(amounts) // 2
            old_avg = statistics.mean(amounts[:split]) if split > 0 else amounts[0]
            recent_avg = statistics.mean(amounts[split:])

            if old_avg > 0:
                increase_pct = ((recent_avg - old_avg) / old_avg) * 100

                if increase_pct > threshold_percent:
                    increases.append(
                        {
                            "merchant": merchant,
                            "old_average": round(old_avg, 2),
                            "recent_average": round(recent_avg, 2),
                            "increase_percent": round(increase_pct, 1),
                            "category": group["category_validated"].iloc[-1],
                        }
                    )

        return increases

    def calculate_monthly_fixed_charges(
        self,
        subscriptions: List[Subscription],
    ) -> float:
        """
        Calcule le total mensualisé des charges fixes.

        Convertit toutes les fréquences en équivalent mensuel.
        """
        monthly_total = 0.0

        frequency_multipliers = {
            "weekly": 4.33,  # 52 semaines / 12 mois
            "bimonthly": 2.0,  # 2x par mois
            "monthly": 1.0,  # 1x par mois
            "quarterly": 1 / 3,  # 1x tous les 3 mois
            "semiannual": 1 / 6,  # 1x tous les 6 mois
            "annual": 1 / 12,  # 1x par an
        }

        for sub in subscriptions:
            if sub.status != SubscriptionStatus.INACTIF.value:
                multiplier = frequency_multipliers.get(sub.frequency, 1.0)
                monthly_total += sub.average_amount * multiplier

        return round(monthly_total, 2)


def detect_subscriptions_simple(
    df: pd.DataFrame,
    min_occurrences: int = 3,
) -> List[Dict]:
    """
    Fonction utilitaire simple pour détecter les abonnements.

    Usage:
        subscriptions = detect_subscriptions_simple(df)
        for sub in subscriptions:
            print(f"{sub['merchant']}: {sub['frequency']}")
    """
    detector = SubscriptionDetector(min_occurrences=min_occurrences)
    subscriptions = detector.detect_subscriptions(df)
    return [sub.to_dict() for sub in subscriptions]


def calculate_remaining_budget(
    current_balance: float,
    subscriptions: List[Subscription],
    days_ahead: int = 30,
) -> RemainingBudgetResult:
    """
    Calcule le "Reste à Vivre" en soustrayant les abonnements à venir.

    Args:
        current_balance: Solde actuel
        subscriptions: Liste des abonnements
        days_ahead: Nombre de jours à projeter

    Returns:
        RemainingBudgetResult avec détails du calcul
    """
    today = datetime.now()
    end_date = today + timedelta(days=days_ahead)

    upcoming_total = 0.0
    upcoming_charges = []

    for sub in subscriptions:
        sub_obj = Subscription(**sub) if isinstance(sub, dict) else sub

        if sub_obj.status == SubscriptionStatus.INACTIF.value:
            continue

        next_date = datetime.strptime(sub_obj.next_expected_date, "%Y-%m-%d")

        # Vérifier si le prélèvement est dans la période
        if today <= next_date <= end_date:
            upcoming_total += sub_obj.average_amount
            upcoming_charges.append(
                {
                    "merchant": sub_obj.merchant,
                    "amount": round(sub_obj.average_amount, 2),
                    "date": sub_obj.next_expected_date,
                }
            )

    remaining = current_balance - upcoming_total
    percentage = (remaining / current_balance * 100) if current_balance > 0 else 0
    daily = remaining / days_ahead if days_ahead > 0 else 0

    # Déterminer le statut
    if remaining < 0:
        status = "critical"
    elif percentage < 20:
        status = "warning"
    else:
        status = "ok"

    return RemainingBudgetResult(
        current_balance=current_balance,
        days_ahead=days_ahead,
        upcoming_charges=upcoming_charges,
        total_upcoming=upcoming_total,
        remaining_budget=remaining,
        percentage_remaining=percentage,
        status=status,
        daily_budget=daily,
    )
