"""
Module Patrimoine Holistique - Gestion Multi-Actifs
====================================================

Ce module implémente la gestion complète du patrimoine incluant :
- Actifs liquides (comptes bancaires)
- Actifs immobiliers (avec calcul d'équité)
- Actifs financiers (PEA, Assurance Vie, Bourse)
- Actifs numériques (Crypto, Titres-Restaurant)
- Passifs (crédits immobiliers, crédits conso)

Architecture :
- Repository Pattern pour l'accès aux données
- Unit of Work pour les transactions cohérentes
- Chiffrement AES-256 pour les données sensibles

Usage:
    from modules.wealth.wealth_manager import WealthManager, AssetType

    manager = WealthManager()
    net_worth = manager.get_total_net_worth()
    print(f"Patrimoine net: €{net_worth:,.2f}")
"""

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any

import pandas as pd

from modules.encryption import encrypt_field
from modules.logger import logger


class AssetType(Enum):
    """Types d'actifs supportés."""

    CASH = "cash"  # Liquidités
    REAL_ESTATE = "real_estate"  # Immobilier
    SECURITIES = "securities"  # PEA, CTO
    LIFE_INSURANCE = "life_insurance"  # Assurance vie
    CRYPTO = "crypto"  # Cryptomonnaies
    MEAL_VOUCHERS = "meal_vouchers"  # Titres-restaurant
    RETIREMENT = "retirement"  # PER, Epargne retraite
    OTHER = "other"  # Autres actifs


class LiabilityType(Enum):
    """Types de passifs (dettes)."""

    MORTGAGE = "mortgage"  # Crédit immobilier
    CONSUMER_CREDIT = "consumer_credit"  # Crédit conso
    STUDENT_LOAN = "student_loan"  # Prêt étudiant
    OVERDRAFT = "overdraft"  # Découvert
    OTHER_DEBT = "other_debt"  # Autres dettes


class AssetLiquidity(Enum):
    """Niveau de liquidité d'un actif."""

    IMMEDIATE = "immediate"  # Disponible instantanément
    SHORT_TERM = "short_term"  # < 1 mois
    MEDIUM_TERM = "medium_term"  # 1-12 mois
    LONG_TERM = "long_term"  # > 1 an
    ILLIQUID = "illiquid"  # Non liquide (immobilier)


@dataclass
class MortgageSchedule:
    """
    Tableau d'amortissement d'un crédit immobilier.

    Attributes:
        principal: Capital emprunté initial
        monthly_payment: Mensualité (hors assurance)
        interest_rate: Taux annuel (ex: 0.023 pour 2.3%)
        start_date: Date de début du crédit
        duration_months: Durée totale en mois
        schedule_df: DataFrame avec les colonnes:
            - month: Numéro de mois
            - date: Date de l'échéance
            - payment: Mensualité
            - interest_part: Part intérêts
            - principal_part: Part capital
            - remaining_balance: Capital restant dû
    """

    principal: float
    monthly_payment: float
    interest_rate: float
    start_date: date
    duration_months: int
    schedule_df: pd.DataFrame | None = None

    def __post_init__(self):
        if self.schedule_df is None:
            self.schedule_df = self._generate_schedule()

    def _generate_schedule(self) -> pd.DataFrame:
        """Génère le tableau d'amortissement complet."""
        monthly_rate = self.interest_rate / 12
        schedule = []
        remaining = self.principal

        for month in range(1, self.duration_months + 1):
            interest = remaining * monthly_rate
            principal_part = self.monthly_payment - interest
            remaining -= principal_part

            # Date de l'échéance
            payment_date = self._add_months(self.start_date, month)

            schedule.append(
                {
                    "month": month,
                    "date": payment_date,
                    "payment": round(self.monthly_payment, 2),
                    "interest_part": round(interest, 2),
                    "principal_part": round(principal_part, 2),
                    "remaining_balance": max(0, round(remaining, 2)),
                }
            )

        return pd.DataFrame(schedule)

    @staticmethod
    def _add_months(d: date, months: int) -> date:
        """Ajoute des mois à une date."""
        month = d.month - 1 + months
        year = d.year + month // 12
        month = month % 12 + 1
        day = min(
            d.day,
            [
                31,
                29 if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0 else 28,
                31,
                30,
                31,
                30,
                31,
                31,
                30,
                31,
                30,
                31,
            ][month - 1],
        )
        return date(year, month, day)

    def get_remaining_balance(self, as_of_date: date | None = None) -> float:
        """
        Retourne le capital restant dû à une date donnée.

        Args:
            as_of_date: Date de calcul (défaut: aujourd'hui)

        Returns:
            Capital restant dû
        """
        if as_of_date is None:
            as_of_date = date.today()

        if as_of_date < self.start_date:
            return self.principal

        # Trouver le mois correspondant
        months_elapsed = (as_of_date.year - self.start_date.year) * 12 + (
            as_of_date.month - self.start_date.month
        )

        if months_elapsed >= self.duration_months:
            return 0.0

        return float(self.schedule_df.iloc[months_elapsed]["remaining_balance"])

    def get_equity(self, property_value: float, as_of_date: date | None = None) -> float:
        """
        Calcule l'équité nette immobilière.

        Formule: Valeur du bien - Capital restant dû

        Args:
            property_value: Valeur actuelle estimée du bien
            as_of_date: Date de calcul

        Returns:
            Équité nette (peut être négative si sous-eau)
        """
        remaining = self.get_remaining_balance(as_of_date)
        return property_value - remaining

    def get_paid_principal(self, as_of_date: date | None = None) -> float:
        """Retourne le capital déjà remboursé."""
        remaining = self.get_remaining_balance(as_of_date)
        return self.principal - remaining

    def get_progress_percentage(self, as_of_date: date | None = None) -> float:
        """Pourcentage de remboursement effectué."""
        paid = self.get_paid_principal(as_of_date)
        return (paid / self.principal * 100) if self.principal > 0 else 0.0

    def get_interest_paid(self, as_of_date: date | None = None) -> float:
        """Total des intérêts payés à ce jour."""
        if as_of_date is None:
            as_of_date = date.today()

        months_elapsed = min(
            (as_of_date.year - self.start_date.year) * 12
            + (as_of_date.month - self.start_date.month),
            self.duration_months,
        )

        if months_elapsed <= 0:
            return 0.0

        return float(self.schedule_df.iloc[:months_elapsed]["interest_part"].sum())

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            "principal": self.principal,
            "monthly_payment": self.monthly_payment,
            "interest_rate": self.interest_rate,
            "start_date": self.start_date.isoformat(),
            "duration_months": self.duration_months,
        }


@dataclass
class RealEstateAsset:
    """
    Actif immobilier avec crédit associé.

    Attributes:
        id: Identifiant unique
        name: Nom du bien (ex: "Appartement Paris 14")
        address: Adresse (chiffrée)
        purchase_price: Prix d'achat
        current_value: Valeur estimée actuelle
        purchase_date: Date d'achat
        mortgage: Crédit immobilier associé (optionnel)
        metadata: Informations complémentaires
    """

    id: str
    name: str
    address: str
    purchase_price: float
    current_value: float
    purchase_date: date
    mortgage: MortgageSchedule | None = None
    metadata: dict = field(default_factory=dict)

    def get_equity(self, as_of_date: date | None = None) -> float:
        """Calcule l'équité nette immobilière."""
        if self.mortgage:
            return self.mortgage.get_equity(self.current_value, as_of_date)
        return self.current_value

    def get_loan_to_value(self, as_of_date: date | None = None) -> float:
        """Ratio LTV (Loan-to-Value)."""
        if not self.mortgage:
            return 0.0
        remaining = self.mortgage.get_remaining_balance(as_of_date)
        return (remaining / self.current_value * 100) if self.current_value > 0 else 0.0

    def get_value_change(self) -> tuple[float, float]:
        """
        Retourne l'évolution de valeur absolue et en pourcentage.

        Returns:
            (variation_absolue, variation_pourcentage)
        """
        change = self.current_value - self.purchase_price
        pct = (change / self.purchase_price * 100) if self.purchase_price > 0 else 0.0
        return change, pct

    def is_underwater(self, as_of_date: date | None = None) -> bool:
        """Vérifie si le bien est 'sous l'eau' (valeur < crédit restant)."""
        if not self.mortgage:
            return False
        return self.current_value < self.mortgage.get_remaining_balance(as_of_date)

    def to_dict(self, encrypt_sensitive: bool = True) -> dict:
        """Convertit en dictionnaire."""
        address = encrypt_field(self.address) if encrypt_sensitive else self.address
        return {
            "id": self.id,
            "name": self.name,
            "address": address,
            "purchase_price": self.purchase_price,
            "current_value": self.current_value,
            "purchase_date": self.purchase_date.isoformat(),
            "mortgage": self.mortgage.to_dict() if self.mortgage else None,
            "metadata": self.metadata,
        }


@dataclass
class FinancialAsset:
    """
    Actif financier (PEA, CTO, Assurance Vie).

    Attributes:
        id: Identifiant unique
        name: Nom du compte
        asset_type: Type d'actif
        institution: Établissement financier
        current_value: Valeur actuelle
        invested_amount: Montant investi (pour calculer la plus-value)
        liquidity: Niveau de liquidité
        metadata: Informations complémentaires
    """

    id: str
    name: str
    asset_type: AssetType
    institution: str
    current_value: float
    invested_amount: float = 0.0
    liquidity: AssetLiquidity = AssetLiquidity.MEDIUM_TERM
    metadata: dict = field(default_factory=dict)

    def get_unrealized_gain(self) -> tuple[float, float]:
        """
        Retourne la plus-value latente absolue et en pourcentage.

        Returns:
            (plus_value_absolue, plus_value_pourcentage)
        """
        gain = self.current_value - self.invested_amount
        pct = (gain / self.invested_amount * 100) if self.invested_amount > 0 else 0.0
        return gain, pct

    def get_performance_annualized(self, years: float) -> float:
        """
        Calcule la performance annualisée (CAGR).

        Formule: (Valeur finale / Valeur initiale)^(1/n) - 1
        """
        if self.invested_amount <= 0 or years <= 0:
            return 0.0
        return (self.current_value / self.invested_amount) ** (1 / years) - 1

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name,
            "asset_type": self.asset_type.value,
            "institution": self.institution,
            "current_value": self.current_value,
            "invested_amount": self.invested_amount,
            "liquidity": self.liquidity.value,
            "metadata": self.metadata,
        }


@dataclass
class CryptoAsset:
    """
    Actif cryptomonnaie.

    Attributes:
        id: Identifiant unique
        symbol: Symbole (BTC, ETH, etc.)
        name: Nom complet
        quantity: Quantité détenue
        current_price: Prix unitaire actuel
        avg_buy_price: Prix moyen d'achat
        platform: Plateforme d'échange
    """

    id: str
    symbol: str
    name: str
    quantity: float
    current_price: float
    avg_buy_price: float = 0.0
    platform: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def current_value(self) -> float:
        """Valeur actuelle totale."""
        return self.quantity * self.current_price

    @property
    def invested_amount(self) -> float:
        """Montant investi."""
        return self.quantity * self.avg_buy_price

    def get_unrealized_gain(self) -> tuple[float, float]:
        """Plus-value latente."""
        gain = self.current_value - self.invested_amount
        pct = (gain / self.invested_amount * 100) if self.invested_amount > 0 else 0.0
        return gain, pct

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "name": self.name,
            "quantity": self.quantity,
            "current_price": self.current_price,
            "avg_buy_price": self.avg_buy_price,
            "platform": self.platform,
            "current_value": self.current_value,
        }


@dataclass
class Liability:
    """
    Passif (dette).

    Attributes:
        id: Identifiant unique
        name: Nom de la dette
        liability_type: Type de dette
        total_amount: Montant total initial
        remaining_amount: Montant restant à rembourser
        monthly_payment: Mensualité
        interest_rate: Taux d'intérêt
        maturity_date: Date de fin
    """

    id: str
    name: str
    liability_type: LiabilityType
    total_amount: float
    remaining_amount: float
    monthly_payment: float
    interest_rate: float = 0.0
    maturity_date: date | None = None
    metadata: dict = field(default_factory=dict)

    @property
    def progress_percentage(self) -> float:
        """Pourcentage remboursé."""
        if self.total_amount <= 0:
            return 0.0
        paid = self.total_amount - self.remaining_amount
        return paid / self.total_amount * 100

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name,
            "liability_type": self.liability_type.value,
            "total_amount": self.total_amount,
            "remaining_amount": self.remaining_amount,
            "monthly_payment": self.monthly_payment,
            "interest_rate": self.interest_rate,
            "maturity_date": self.maturity_date.isoformat() if self.maturity_date else None,
        }


class WealthManager:
    """
    Gestionnaire de patrimoine holistique.

    Cette classe agrège tous les actifs et passifs pour calculer
    le patrimoine net total et fournir des analyses complètes.

    Attributes:
        real_estate: Liste des biens immobiliers
        financial_assets: Liste des actifs financiers
        crypto_assets: Liste des cryptomonnaies
        liabilities: Liste des dettes
        cash_balance: Solde cash (comptes courants)

    Example:
        >>> manager = WealthManager()
        >>> manager.add_real_estate(apartment)
        >>> manager.add_financial_asset(pea_account)
        >>> net_worth = manager.get_total_net_worth()
        >>> print(f"Patrimoine net: €{net_worth:,.2f}")
    """

    def __init__(self):
        self.real_estate: list[RealEstateAsset] = []
        self.financial_assets: list[FinancialAsset] = []
        self.crypto_assets: list[CryptoAsset] = []
        self.liabilities: list[Liability] = []
        self.cash_balance: float = 0.0
        self._last_updated: datetime = datetime.now()

        logger.info("WealthManager initialisé")

    # ==================== Ajout d'actifs ====================

    def add_real_estate(self, asset: RealEstateAsset) -> None:
        """Ajoute un bien immobilier."""
        self.real_estate.append(asset)
        logger.info(f"Bien immobilier ajouté: {asset.name} ({asset.current_value:,.2f}€)")

    def add_financial_asset(self, asset: FinancialAsset) -> None:
        """Ajoute un actif financier."""
        self.financial_assets.append(asset)
        logger.info(f"Actif financier ajouté: {asset.name} ({asset.current_value:,.2f}€)")

    def add_crypto_asset(self, asset: CryptoAsset) -> None:
        """Ajoute un actif crypto."""
        self.crypto_assets.append(asset)
        logger.info(f"Crypto ajoutée: {asset.symbol} ({asset.current_value:,.2f}€)")

    def add_liability(self, liability: Liability) -> None:
        """Ajoute un passif."""
        self.liabilities.append(liability)
        logger.info(f"Passif ajouté: {liability.name} ({liability.remaining_amount:,.2f}€ restant)")

    def set_cash_balance(self, amount: float) -> None:
        """Définit le solde cash."""
        self.cash_balance = amount
        logger.info(f"Cash mis à jour: {amount:,.2f}€")

    # ==================== Calculs de patrimoine ====================

    def get_total_assets(self) -> dict[str, float]:
        """
        Calcule le total des actifs par catégorie.

        Returns:
            Dict avec les totaux par type d'actif
        """
        real_estate_total = sum(a.current_value for a in self.real_estate)
        financial_total = sum(a.current_value for a in self.financial_assets)
        crypto_total = sum(c.current_value for c in self.crypto_assets)

        return {
            "cash": self.cash_balance,
            "real_estate": real_estate_total,
            "financial": financial_total,
            "crypto": crypto_total,
            "total": self.cash_balance + real_estate_total + financial_total + crypto_total,
        }

    def get_total_liabilities(self) -> dict[str, float]:
        """
        Calcule le total des passifs par catégorie.

        Returns:
            Dict avec les totaux par type de dette
        """
        by_type: dict[str, float] = {}
        total = 0.0

        for liability in self.liabilities:
            type_key = liability.liability_type.value
            by_type[type_key] = by_type.get(type_key, 0.0) + liability.remaining_amount
            total += liability.remaining_amount

        by_type["total"] = total
        return by_type

    def get_net_real_estate_value(self) -> float:
        """
        Calcule la valeur nette immobilière totale.

        Returns:
            Somme des équités nettes de tous les biens
        """
        return sum(asset.get_equity() for asset in self.real_estate)

    def get_total_net_worth(self) -> float:
        """
        Calcule le patrimoine net total.

        Formule: Total Actifs - Total Passifs

        Returns:
            Patrimoine net (peut être négatif)
        """
        assets = self.get_total_assets()
        liabilities = self.get_total_liabilities()

        # Pour l'immobilier, on prend l'équité nette (valeur - crédit)
        real_estate_equity = self.get_net_real_estate_value()

        # On compte l'immobilier en equity, pas en valeur brute
        total_assets = (
            self.cash_balance
            + real_estate_equity
            + sum(a.current_value for a in self.financial_assets)
            + sum(c.current_value for c in self.crypto_assets)
        )

        # On ne double-compte pas les crédits immobiliers déjà déduits
        non_mortgage_debt = sum(
            l.remaining_amount
            for l in self.liabilities
            if l.liability_type != LiabilityType.MORTGAGE
        )

        return total_assets - non_mortgage_debt

    def get_asset_allocation(self) -> dict[str, dict[str, Any]]:
        """
        Calcule la répartition du patrimoine.

        Returns:
            Dict avec pourcentages et montants par catégorie
        """
        total = self.get_total_net_worth()
        if total <= 0:
            return {}

        cash = self.cash_balance
        real_estate = self.get_net_real_estate_value()
        financial = sum(a.current_value for a in self.financial_assets)
        crypto = sum(c.current_value for c in self.crypto_assets)

        # Dettes non immobilières
        other_debt = sum(
            l.remaining_amount
            for l in self.liabilities
            if l.liability_type != LiabilityType.MORTGAGE
        )

        return {
            "cash": {
                "amount": cash,
                "percentage": cash / total * 100,
                "liquidity": "immediate",
            },
            "real_estate": {
                "amount": real_estate,
                "percentage": real_estate / total * 100,
                "liquidity": "illiquid",
            },
            "financial": {
                "amount": financial,
                "percentage": financial / total * 100,
                "liquidity": "medium_term",
            },
            "crypto": {
                "amount": crypto,
                "percentage": crypto / total * 100,
                "liquidity": "short_term",
            },
            "other_debt": {
                "amount": -other_debt,  # Négatif pour visualisation
                "percentage": -other_debt / total * 100 if total > 0 else 0,
                "liquidity": "liability",
            },
        }

    def get_liquidity_analysis(self) -> dict[str, float]:
        """
        Analyse la liquidité du patrimoine.

        Returns:
            Dict avec liquidité immédiate, court, moyen, long terme
        """
        immediate = self.cash_balance
        short_term = sum(c.current_value for c in self.crypto_assets)

        medium_term = sum(
            a.current_value
            for a in self.financial_assets
            if a.liquidity
            in (AssetLiquidity.IMMEDIATE, AssetLiquidity.SHORT_TERM, AssetLiquidity.MEDIUM_TERM)
        )

        long_term = sum(
            a.current_value
            for a in self.financial_assets
            if a.liquidity == AssetLiquidity.LONG_TERM
        )

        illiquid = self.get_net_real_estate_value()

        return {
            "immediate": immediate,
            "short_term": short_term,
            "medium_term": medium_term,
            "long_term": long_term,
            "illiquid": illiquid,
            "total_liquid": immediate + short_term + medium_term,
        }

    def get_performance_summary(self) -> dict[str, Any]:
        """
        Résumé des performances par classe d'actif.

        Returns:
            Dict avec performances réalisées et latentes
        """
        # Immobilier
        real_estate_gains = []
        for asset in self.real_estate:
            change_abs, change_pct = asset.get_value_change()
            real_estate_gains.append(
                {
                    "name": asset.name,
                    "absolute": change_abs,
                    "percentage": change_pct,
                }
            )

        # Actifs financiers
        financial_gains = []
        for asset in self.financial_assets:
            gain, pct = asset.get_unrealized_gain()
            financial_gains.append(
                {
                    "name": asset.name,
                    "unrealized_gain": gain,
                    "percentage": pct,
                }
            )

        # Crypto
        crypto_gains = []
        for crypto in self.crypto_assets:
            gain, pct = crypto.get_unrealized_gain()
            crypto_gains.append(
                {
                    "symbol": crypto.symbol,
                    "unrealized_gain": gain,
                    "percentage": pct,
                }
            )

        return {
            "real_estate": {
                "gains": real_estate_gains,
                "total_unrealized": sum(g["absolute"] for g in real_estate_gains),
            },
            "financial": {
                "gains": financial_gains,
                "total_unrealized": sum(g["unrealized_gain"] for g in financial_gains),
            },
            "crypto": {
                "gains": crypto_gains,
                "total_unrealized": sum(g["unrealized_gain"] for g in crypto_gains),
            },
        }

    # ==================== Export / Import ====================

    def to_dict(self, encrypt_sensitive: bool = True) -> dict:
        """Exporte tout le patrimoine en dictionnaire."""
        return {
            "real_estate": [a.to_dict(encrypt_sensitive) for a in self.real_estate],
            "financial_assets": [a.to_dict() for a in self.financial_assets],
            "crypto_assets": [c.to_dict() for c in self.crypto_assets],
            "liabilities": [l.to_dict() for l in self.liabilities],
            "cash_balance": self.cash_balance,
            "total_net_worth": self.get_total_net_worth(),
            "last_updated": self._last_updated.isoformat(),
        }

    def to_json(self, encrypt_sensitive: bool = True) -> str:
        """Exporte en JSON."""
        return json.dumps(self.to_dict(encrypt_sensitive), indent=2, ensure_ascii=False)

    def get_summary(self) -> str:
        """Retourne un résumé textuel du patrimoine."""
        assets = self.get_total_assets()
        liabilities = self.get_total_liabilities()
        net_worth = self.get_total_net_worth()
        allocation = self.get_asset_allocation()

        lines = [
            "=" * 50,
            "RÉSUMÉ DU PATRIMOINE",
            "=" * 50,
            "",
            f"💰 Cash: {self.cash_balance:>15,.2f} €",
            f"🏠 Immobilier (net): {self.get_net_real_estate_value():>15,.2f} €",
            f"📈 Financier: {assets['financial']:>15,.2f} €",
            f"₿ Crypto: {assets['crypto']:>15,.2f} €",
            "-" * 35,
            f"TOTAL ACTIFS: {assets['total']:>15,.2f} €",
            "",
            f"💳 Dettes (hors immo): {liabilities.get('total', 0) - sum(l.remaining_amount for l in self.liabilities if l.liability_type == LiabilityType.MORTGAGE):>15,.2f} €",
            "",
            "=" * 35,
            f"PATRIMOINE NET: {net_worth:>15,.2f} €",
            "=" * 35,
            "",
            "RÉPARTITION:",
        ]

        for category, data in allocation.items():
            if category != "other_debt" and data["amount"] > 0:
                emoji = {"cash": "💰", "real_estate": "🏠", "financial": "📈", "crypto": "₿"}.get(
                    category, "📊"
                )
                lines.append(f"  {emoji} {category}: {data['percentage']:.1f}%")

        lines.append("")
        return "\n".join(lines)


# ==================== Fonctions utilitaires ====================


def calculate_monthly_debt_service(manager: WealthManager) -> float:
    """
    Calcule le service mensuel total de la dette.

    Returns:
        Somme de toutes les mensualités
    """
    total = 0.0

    # Mensualités de crédits
    for liability in manager.liabilities:
        total += liability.monthly_payment

    # Mensualités immobilières
    for asset in manager.real_estate:
        if asset.mortgage:
            total += asset.mortgage.monthly_payment

    return total


def calculate_debt_to_income_ratio(manager: WealthManager, monthly_income: float) -> float:
    """
    Calcule le ratio dette/revenu (endettement).

    Args:
        manager: Instance WealthManager
        monthly_income: Revenu mensuel net

    Returns:
        Ratio en pourcentage (33% recommandé max)
    """
    if monthly_income <= 0:
        return 0.0

    debt_service = calculate_monthly_debt_service(manager)
    return debt_service / monthly_income * 100


def calculate_savings_rate(
    manager: WealthManager,
    monthly_income: float,
    monthly_expenses: float,
) -> float:
    """
    Calcule le taux d'épargne.

    Returns:
        Pourcentage d'épargne sur revenus
    """
    if monthly_income <= 0:
        return 0.0

    savings = monthly_income - monthly_expenses
    return savings / monthly_income * 100
