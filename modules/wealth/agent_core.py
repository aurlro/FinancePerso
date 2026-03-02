"""
Orchestrateur d'IA Agentique - Système de Missions d'Optimisation
=================================================================

Ce module implémente un système agentique capable de :
1. Observer les données (Phase 3 et 5)
2. Raisonner sur les optimisations possibles
3. Proposer des actions concrètes (missions)
4. Générer des documents pré-remplis

Architecture Agentique:
- Triggers: Détecteurs d'anomalies et opportunités
- Reasoning: Logique de recommandation
- Actions: Générateurs de documents et liens
- Validation: Human-in-the-loop obligatoire

Usage:
    from modules.wealth.agent_core import AgentOrchestrator, TriggerType

    orchestrator = AgentOrchestrator()
    missions = orchestrator.analyze_and_generate_missions(
        subscriptions=subs,
        wealth_manager=wealth_mgr,
    )

    for mission in missions:
        print(f"🎯 {mission.title}: {mission.description}")
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

# Imports locaux
from modules.logger import logger
from modules.wealth.subscription_engine import Subscription, SubscriptionStatus
from modules.wealth.wealth_manager import (
    WealthManager,
)


class TriggerType(Enum):
    """Types de déclencheurs pour les missions."""

    PRICE_INCREASE = "price_increase"  # Hausse de prix détectée
    DUPLICATE_SUBSCRIPTION = "duplicate"  # Doublon d'abonnement
    UNUSED_SUBSCRIPTION = "unused"  # Abonnement non utilisé (zombie)
    BETTER_ALTERNATIVE = "better_alternative"  # Alternative moins chère disponible
    UNDERUTILIZED_ASSET = "underutilized"  # Actif sous-utilisé
    HIGH_DEBT_RATIO = "high_debt"  # Endettement élevé
    LOW_SAVINGS_RATE = "low_savings"  # Taux d'épargne faible
    CASH_IDLE = "cash_idle"  # Cash dormant
    CRYPTO_VOLATILITY = "crypto_volatility"  # Crypto trop volatile
    INSURANCE_OVERLAP = "insurance_overlap"  # Doublon d'assurance
    TAX_OPTIMIZATION = "tax_optimization"  # Opportunité fiscale
    DIVERSIFICATION_NEEDED = "diversification"  # Portefeuille non diversifié


class MissionPriority(Enum):
    """Priorité d'une mission."""

    CRITICAL = "critical"  # Action urgente (dette élevée)
    HIGH = "high"  # Fort impact financier
    MEDIUM = "medium"  # Impact modéré
    LOW = "low"  # Nice-to-have
    INFO = "info"  # Information seule


class MissionStatus(Enum):
    """Statut d'une mission."""

    PENDING = "pending"  # En attente de validation
    APPROVED = "approved"  # Approuvée par l'utilisateur
    REJECTED = "rejected"  # Rejetée
    IN_PROGRESS = "in_progress"  # En cours d'exécution
    COMPLETED = "completed"  # Terminée
    EXPIRED = "expired"  # Expirée (date limite dépassée)


class ActionType(Enum):
    """Types d'actions possibles."""

    GENERATE_LETTER = "generate_letter"  # Générer une lettre (résiliation)
    COMPARE_OFFERS = "compare_offers"  # Ouvrir comparateur
    SCHEDULE_CALL = "schedule_call"  # Planifier appel
    SET_REMINDER = "set_reminder"  # Créer rappel
    TRANSFER_MONEY = "transfer_money"  # Virement (HUMAN VALIDATION REQUIRED)
    INVEST_SUGGESTION = "invest_suggestion"  # Suggestion d'investissement
    EXPORT_DATA = "export_data"  # Exporter données


@dataclass
class Action:
    """
    Action spécifique à réaliser.

    Attributes:
        type: Type d'action
        label: Libellé affiché à l'utilisateur
        payload: Données nécessaires à l'action
        requires_human_validation: Nécessite validation humaine
        auto_executable: Peut être exécutée automatiquement
    """

    type: ActionType
    label: str
    payload: dict[str, Any] = field(default_factory=dict)
    requires_human_validation: bool = True
    auto_executable: bool = False

    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "label": self.label,
            "payload": self.payload,
            "requires_human_validation": self.requires_human_validation,
            "auto_executable": self.auto_executable,
        }


@dataclass
class Mission:
    """
    Mission d'optimisation générée par l'IA.

    Une mission représente une opportunité d'amélioration financière
    détectée par le système, avec une action recommandée.

    Attributes:
        id: Identifiant unique
        trigger_type: Type de déclencheur
        title: Titre court
        description: Description détaillée
        priority: Priorité
        status: Statut actuel
        potential_savings: Économie potentielle annuelle (€)
        effort_level: Niveau d'effort requis (1-5)
        time_to_complete: Temps estimé (minutes)
        actions: Liste des actions possibles
        data_sources: Sources de données utilisées
        created_at: Date de création
        expires_at: Date d'expiration
        completed_at: Date de complétion
        user_notes: Notes utilisateur
    """

    id: str
    trigger_type: TriggerType
    title: str
    description: str
    priority: MissionPriority
    status: MissionStatus = MissionStatus.PENDING
    potential_savings: float = 0.0
    effort_level: int = 3  # 1 (facile) à 5 (difficile)
    time_to_complete: int = 15  # minutes
    actions: list[Action] = field(default_factory=list)
    data_sources: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    completed_at: datetime | None = None
    user_notes: str = ""

    def __post_init__(self):
        if self.expires_at is None:
            # Par défaut, expire après 30 jours
            self.expires_at = self.created_at + timedelta(days=30)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "trigger_type": self.trigger_type.value,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "potential_savings": self.potential_savings,
            "effort_level": self.effort_level,
            "time_to_complete": self.time_to_complete,
            "actions": [a.to_dict() for a in self.actions],
            "data_sources": self.data_sources,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "user_notes": self.user_notes,
        }

    def approve(self) -> None:
        """Marque la mission comme approuvée."""
        self.status = MissionStatus.APPROVED
        logger.info(f"Mission approuvée: {self.title}")

    def reject(self, reason: str = "") -> None:
        """Marque la mission comme rejetée."""
        self.status = MissionStatus.REJECTED
        self.user_notes = reason
        logger.info(f"Mission rejetée: {self.title} - {reason}")

    def complete(self) -> None:
        """Marque la mission comme terminée."""
        self.status = MissionStatus.COMPLETED
        self.completed_at = datetime.now()
        logger.info(f"Mission complétée: {self.title}")

    def is_expired(self) -> bool:
        """Vérifie si la mission est expirée."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    @property
    def roi_score(self) -> float:
        """
        Score ROI = Économie / (Effort × Temps)

        Plus le score est élevé, plus la mission est intéressante.
        """
        if self.effort_level <= 0 or self.time_to_complete <= 0:
            return 0.0
        return self.potential_savings / (self.effort_level * self.time_to_complete)


class TriggerDetector:
    """
    Détecteur de déclencheurs (triggers).

    Analyse les données pour détecter des anomalies,
    opportunités ou problèmes nécessitant une action.
    """

    def __init__(self):
        self.logger = logger

    def detect_price_increases(
        self,
        subscriptions: list[Subscription],
        price_history: dict[str, list[tuple[date, float]]] | None = None,
    ) -> list[dict]:
        """
        Détecte les hausses de prix sur les abonnements.

        Args:
            subscriptions: Liste des abonnements actifs
            price_history: Historique des prix par marchand

        Returns:
            Liste des détections avec ancien/nouveau prix
        """
        triggers = []

        for sub in subscriptions:
            # Vérifier si on a un historique de prix
            if price_history and sub.merchant in price_history:
                history = price_history[sub.merchant]
                if len(history) >= 2:
                    # Trier par date
                    history.sort(key=lambda x: x[0])
                    old_price = history[0][1]
                    new_price = history[-1][1]

                    if new_price > old_price:
                        increase_pct = (new_price - old_price) / old_price * 100

                        if increase_pct >= 10:  # Seuil de 10%
                            triggers.append(
                                {
                                    "type": TriggerType.PRICE_INCREASE,
                                    "merchant": sub.merchant,
                                    "old_price": old_price,
                                    "new_price": new_price,
                                    "increase_pct": increase_pct,
                                    "frequency": sub.frequency,
                                    "severity": "high" if increase_pct >= 20 else "medium",
                                }
                            )

        return triggers

    def detect_duplicate_subscriptions(
        self,
        subscriptions: list[Subscription],
    ) -> list[dict]:
        """
        Détecte les doublons d'abonnements (ex: 2 assurances mobiles).

        Args:
            subscriptions: Liste des abonnements

        Returns:
            Liste des doublons détectés
        """
        triggers = []

        # Catégoriser par type de service
        categories = {
            "streaming": ["NETFLIX", "SPOTIFY", "DISNEY", "AMAZON PRIME", "APPLE TV", "CANAL+"],
            "mobile": ["SFR", "ORANGE", "FREE", "BOUYGUES", "RED"],
            "cloud": ["DROPBOX", "GOOGLE ONE", "ICLOUD", "ONEDRIVE"],
            "news": ["LE MONDE", "FIGARO", "MEDIAPART", "NEW YORK TIMES"],
            "fitness": ["GYMPASS", "CLASSPASS", "KEEP", "FREELANCE"],
        }

        # Grouper les abonnements par catégorie
        sub_by_category: dict[str, list[Subscription]] = {cat: [] for cat in categories}

        for sub in subscriptions:
            merchant_upper = sub.merchant.upper()
            for cat, keywords in categories.items():
                if any(kw in merchant_upper for kw in keywords):
                    sub_by_category[cat].append(sub)

        # Détecter les doublons (>1 abonnement dans une catégorie)
        for cat, subs in sub_by_category.items():
            if len(subs) > 1:
                total_cost = sum(s.average_amount for s in subs)
                triggers.append(
                    {
                        "type": TriggerType.DUPLICATE_SUBSCRIPTION,
                        "category": cat,
                        "subscriptions": subs,
                        "count": len(subs),
                        "total_monthly_cost": total_cost,
                    }
                )

        return triggers

    def detect_unused_subscriptions(
        self,
        subscriptions: list[Subscription],
    ) -> list[dict]:
        """
        Détecte les abonnements zombies (non utilisés).

        Args:
            subscriptions: Liste des abonnements

        Returns:
            Liste des abonnements inutilisés
        """
        triggers = []

        for sub in subscriptions:
            if sub.status == SubscriptionStatus.ZOMBIE.value:
                triggers.append(
                    {
                        "type": TriggerType.UNUSED_SUBSCRIPTION,
                        "merchant": sub.merchant,
                        "amount": sub.average_amount,
                        "frequency": sub.frequency,
                        "last_transaction": sub.last_date,
                    }
                )

        return triggers

    def detect_better_alternatives(
        self,
        subscriptions: list[Subscription],
    ) -> list[dict]:
        """
        Détecte les opportunités de meilleures offres.

        Cette méthode compare avec une base de connaissances
        de tarifs concurrents.

        Args:
            subscriptions: Liste des abonnements

        Returns:
            Liste des alternatives moins chères
        """
        # Base de connaissances: tarifs concurrents (€/mois)
        alternatives_db = {
            "MOBILE": [
                {"provider": "Free", "plan": "Forfait 2h", "price": 2.0},
                {"provider": "Red by SFR", "plan": "Forfait 5Go", "price": 10.0},
                {"provider": "B&You", "plan": "Forfait 20Go", "price": 12.0},
            ],
            "STREAMING": [
                {"provider": "Netflix", "plan": "Essentiel", "price": 8.99},
                {"provider": "Disney+", "plan": "Standard", "price": 8.99},
            ],
            "INTERNET": [
                {"provider": "Free", "plan": "Box Delta", "price": 29.99},
                {"provider": "Sosh", "plan": "Fibre", "price": 24.99},
            ],
        }

        triggers = []

        for sub in subscriptions:
            merchant_upper = sub.merchant.upper()

            # Déterminer la catégorie
            category = None
            if any(x in merchant_upper for x in ["SFR", "ORANGE", "FREE", "BOUYGUES"]):
                category = "MOBILE"
            elif any(x in merchant_upper for x in ["NETFLIX", "SPOTIFY", "DISNEY"]):
                category = "STREAMING"
            elif (
                any(x in merchant_upper for x in ["FREE", "ORANGE", "SFR"])
                and "BOX" in merchant_upper
            ):
                category = "INTERNET"

            if category and category in alternatives_db:
                current_monthly = sub.average_amount

                # Trouver une alternative moins chère
                for alt in alternatives_db[category]:
                    if alt["price"] < current_monthly * 0.8:  # 20% moins cher
                        savings = (current_monthly - alt["price"]) * 12  # Annuel
                        triggers.append(
                            {
                                "type": TriggerType.BETTER_ALTERNATIVE,
                                "current": {
                                    "merchant": sub.merchant,
                                    "price": current_monthly,
                                },
                                "alternative": alt,
                                "annual_savings": savings,
                            }
                        )
                        break  # Une seule alternative par abonnement

        return triggers

    def detect_cash_optimization(
        self,
        wealth_manager: WealthManager,
        threshold_ratio: float = 0.2,  # 20% du patrimoine
    ) -> list[dict]:
        """
        Détecte si trop de cash est inactif.

        Args:
            wealth_manager: Gestionnaire de patrimoine
            threshold_ratio: Seuil de cash maximum (% du patrimoine)

        Returns:
            Liste des opportunités d'optimisation
        """
        triggers = []

        net_worth = wealth_manager.get_total_net_worth()
        cash = wealth_manager.cash_balance

        if net_worth > 0:
            cash_ratio = cash / net_worth

            if cash_ratio > threshold_ratio:
                excess_cash = cash - (net_worth * threshold_ratio)
                triggers.append(
                    {
                        "type": TriggerType.CASH_IDLE,
                        "current_cash": cash,
                        "cash_ratio": cash_ratio * 100,
                        "excess_cash": excess_cash,
                        "threshold_ratio": threshold_ratio * 100,
                        "message": f"{cash_ratio*100:.1f}% de votre patrimoine est en cash.",
                    }
                )

        return triggers

    def detect_debt_optimization(
        self,
        wealth_manager: WealthManager,
        monthly_income: float,
    ) -> list[dict]:
        """
        Détecte les problèmes d'endettement.

        Args:
            wealth_manager: Gestionnaire de patrimoine
            monthly_income: Revenu mensuel net

        Returns:
            Liste des alertes dettes
        """
        triggers = []

        # Calculer le taux d'endettement
        total_monthly_payments = sum(l.monthly_payment for l in wealth_manager.liabilities)

        # Ajouter les mensualités immobilières
        for asset in wealth_manager.real_estate:
            if asset.mortgage:
                total_monthly_payments += asset.mortgage.monthly_payment

        if monthly_income > 0:
            debt_ratio = (total_monthly_payments / monthly_income) * 100

            if debt_ratio > 33:
                triggers.append(
                    {
                        "type": TriggerType.HIGH_DEBT_RATIO,
                        "debt_ratio": debt_ratio,
                        "monthly_payments": total_monthly_payments,
                        "monthly_income": monthly_income,
                        "severity": "critical" if debt_ratio > 40 else "warning",
                        "message": f"Taux d'endettement de {debt_ratio:.1f}% (limite: 33%)",
                    }
                )

        return triggers

    def detect_portfolio_diversification(
        self,
        wealth_manager: WealthManager,
    ) -> list[dict]:
        """
        Vérifie la diversification du portefeuille.

        Args:
            wealth_manager: Gestionnaire de patrimoine

        Returns:
            Liste des alertes de diversification
        """
        triggers = []
        allocation = wealth_manager.get_asset_allocation()

        if not allocation:
            return triggers

        # Vérifier la concentration crypto
        crypto_pct = allocation.get("crypto", {}).get("percentage", 0)
        if crypto_pct > 20:
            triggers.append(
                {
                    "type": TriggerType.DIVERSIFICATION_NEEDED,
                    "issue": "crypto_concentration",
                    "current_percentage": crypto_pct,
                    "recommended_max": 10,
                    "message": f"{crypto_pct:.1f}% en crypto (recommandé: <10%)",
                }
            )

        # Vérifier la concentration immobilière
        real_estate_pct = allocation.get("real_estate", {}).get("percentage", 0)
        if real_estate_pct > 70:
            triggers.append(
                {
                    "type": TriggerType.DIVERSIFICATION_NEEDED,
                    "issue": "real_estate_concentration",
                    "current_percentage": real_estate_pct,
                    "recommended_max": 60,
                    "message": f"{real_estate_pct:.1f}% en immobilier (risque de concentration)",
                }
            )

        return triggers


class DocumentGenerator:
    """
    Générateur de documents pour les actions.

    Crée des lettres de résiliation, mises en demeure,
    et autres documents pré-remplis.
    """

    def __init__(self):
        self.logger = logger

    def generate_cancellation_letter(
        self,
        merchant_name: str,
        contract_number: str | None = None,
        subscriber_name: str = "",
        subscriber_address: str = "",
        effective_date: date | None = None,
    ) -> str:
        """
        Génère une lettre de résiliation type.

        Args:
            merchant_name: Nom du prestataire
            contract_number: Numéro de contrat
            subscriber_name: Nom de l'abonné
            subscriber_address: Adresse de l'abonné
            effective_date: Date de prise d'effet

        Returns:
            Texte de la lettre formatée
        """
        if effective_date is None:
            effective_date = date.today() + timedelta(days=30)

        letter = f"""
{subscriber_name}
{subscriber_address}

{merchant_name}
Service Client

À l'attention du service résiliation

{date.today().strftime('%d/%m/%Y')}


Objet : Résiliation de l'abonnement{' n° ' + contract_number if contract_number else ''}

Madame, Monsieur,

Par la présente, je vous informe de ma décision de résilier l'abonnement "
    f"souscrit auprès de vos services"
    f"{' (contrat n° ' + contract_number + ')' if contract_number else ''}, "
    f"avec effet au {effective_date.strftime('%d/%m/%Y')}.

Conformément aux conditions générales de vente et au code de la consommation, "
"je respecte le préavis de résiliation requis.

Je vous prie de bien vouloir :
1. Confirmer la réception de cette demande de résiliation
2. M'indiquer la date effective de résiliation
3. M'adresser un solde de tout compte

Je vous remercie de traiter cette demande dans les meilleurs délais.

Dans l'attente de votre confirmation, je vous prie d'agréer, "
"Madame, Monsieur, l'expression de mes salutations distinguées."


{subscriber_name}


Pièce jointe : Copie de la pièce d'identité (si nécessaire)
"""
        return letter.strip()

    def generate_complaint_letter(
        self,
        merchant_name: str,
        issue_description: str,
        amount_claimed: float | None = None,
        subscriber_name: str = "",
        subscriber_address: str = "",
    ) -> str:
        """
        Génère une lettre de réclamation/mise en demeure.

        Args:
            merchant_name: Nom du prestataire
            issue_description: Description du problème
            amount_claimed: Montant réclamé (optionnel)
            subscriber_name: Nom du réclamant
            subscriber_address: Adresse

        Returns:
            Texte de la lettre formatée
        """
        letter = f"""
{subscriber_name}
{subscriber_address}

{merchant_name}
Service Client / Service Réclamations

À l'attention du service contentieux

{date.today().strftime('%d/%m/%Y')}


Objet : Réclamation / Mise en demeure

Madame, Monsieur,

Je vous adresse la présente lettre en tant que réclamation formelle concernant les faits suivants :

{issue_description}

"""

        if amount_claimed:
            letter += f"À ce titre, je vous demande de me rembourser la somme de {amount_claimed:.2f} €.\n\n"

        letter += """Je vous mets en demeure de :
1. Prendre en compte cette réclamation
2. Procéder aux corrections nécessaires
"""

        if amount_claimed:
            letter += "3. Effectuer le remboursement demandé dans un délai de 30 jours\n"

        letter += f"""
À défaut de réponse satisfactoire dans ce délai, je me verrai dans l'obligation de saisir :
- Le médiateur du contrat
- Le service contentieux
- Les juridictions compétentes

Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.


{subscriber_name}
"""
        return letter.strip()

    def generate_investment_proposal(
        self,
        current_allocation: dict,
        proposal: dict,
        risk_profile: str = "modéré",
    ) -> str:
        """
        Génère une proposition d'investissement.

        Args:
            current_allocation: Allocation actuelle
            proposal: Allocation proposée
            risk_profile: Profil de risque

        Returns:
            Rapport de proposition
        """
        report = f"""
PROPOSITION D'ALLOCATION - PROFIL {risk_profile.upper()}
{'=' * 50}

ALLOCATION ACTUELLE :
"""
        for asset, data in current_allocation.items():
            if isinstance(data, dict):
                pct = data.get("percentage", 0)
                amt = data.get("amount", 0)
                report += f"  • {asset}: {pct:.1f}% (€{amt:,.2f})\n"

        report += """
ALLOCATION RECOMMANDÉE :
"""
        for asset, data in proposal.items():
            if isinstance(data, dict):
                pct = data.get("percentage", 0)
                amt = data.get("amount", 0)
                report += f"  • {asset}: {pct:.1f}% (€{amt:,.2f})\n"

        report += """

JUSTIFICATION :
L'allocation recommandée respecte les principes de diversification
et correspond à votre profil de risque.

ACTIONS SUGGÉRÉES :
"""
        # Calculer les mouvements nécessaires
        for asset in set(current_allocation.keys()) | set(proposal.keys()):
            current = current_allocation.get(asset, {}).get("amount", 0)
            target = proposal.get(asset, {}).get("amount", 0)
            diff = target - current

            if abs(diff) > 100:  # Seulement si significatif
                action = "Investir" if diff > 0 else "Désinvestir"
                report += f"  • {action} €{abs(diff):,.2f} en {asset}\n"

        report += """

⚠️  CETTE PROPOSITION EST DONNÉE À TITRE INFORMATIF.
    ELLE NE CONSTITUTE PAS UN CONSEIL EN INVESTISSEMENT.
    CONSULTEZ UN CONSEILLER FINANCIER AVANT TOUTE DÉCISION.
"""
        return report.strip()

    def save_document(self, content: str, filename: str, output_dir: str = "documents") -> Path:
        """
        Sauvegarde un document sur disque.

        Args:
            content: Contenu du document
            filename: Nom du fichier
            output_dir: Répertoire de sortie

        Returns:
            Chemin du fichier créé
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filepath = output_path / filename
        filepath.write_text(content, encoding="utf-8")

        self.logger.info(f"Document sauvegardé: {filepath}")
        return filepath


class AgentOrchestrator:
    """
    Orchestrateur principal du système agentique.

    Cette classe coordonne les détecteurs de triggers,
    le raisonnement, et la génération de missions.
    """

    def __init__(self):
        self.detector = TriggerDetector()
        self.doc_generator = DocumentGenerator()
        self.logger = logger
        self._mission_counter = 0

    def _generate_mission_id(self) -> str:
        """Génère un ID unique de mission."""
        self._mission_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"MISSION-{timestamp}-{self._mission_counter:04d}"

    def analyze_and_generate_missions(
        self,
        subscriptions: list[Subscription],
        wealth_manager: WealthManager,
        monthly_income: float = 3000.0,
        price_history: dict | None = None,
    ) -> list[Mission]:
        """
        Analyse les données et génère des missions d'optimisation.

        Args:
            subscriptions: Liste des abonnements (Phase 3)
            wealth_manager: Gestionnaire de patrimoine (Phase 5)
            monthly_income: Revenu mensuel net
            price_history: Historique des prix

        Returns:
            Liste des missions générées
        """
        missions = []

        # 1. Détecter les hausses de prix
        price_triggers = self.detector.detect_price_increases(subscriptions, price_history)
        for trigger in price_triggers:
            mission = self._create_price_increase_mission(trigger)
            if mission:
                missions.append(mission)

        # 2. Détecter les doublons
        duplicate_triggers = self.detector.detect_duplicate_subscriptions(subscriptions)
        for trigger in duplicate_triggers:
            mission = self._create_duplicate_mission(trigger)
            if mission:
                missions.append(mission)

        # 3. Détecter les abonnements inutilisés
        unused_triggers = self.detector.detect_unused_subscriptions(subscriptions)
        for trigger in unused_triggers:
            mission = self._create_unused_mission(trigger)
            if mission:
                missions.append(mission)

        # 4. Détecter les meilleures alternatives
        alt_triggers = self.detector.detect_better_alternatives(subscriptions)
        for trigger in alt_triggers:
            mission = self._create_alternative_mission(trigger)
            if mission:
                missions.append(mission)

        # 5. Détecter le cash dormant
        cash_triggers = self.detector.detect_cash_optimization(wealth_manager)
        for trigger in cash_triggers:
            mission = self._create_cash_mission(trigger)
            if mission:
                missions.append(mission)

        # 6. Détecter les problèmes d'endettement
        debt_triggers = self.detector.detect_debt_optimization(wealth_manager, monthly_income)
        for trigger in debt_triggers:
            mission = self._create_debt_mission(trigger)
            if mission:
                missions.append(mission)

        # 7. Détecter les problèmes de diversification
        div_triggers = self.detector.detect_portfolio_diversification(wealth_manager)
        for trigger in div_triggers:
            mission = self._create_diversification_mission(trigger)
            if mission:
                missions.append(mission)

        # Trier par priorité puis par ROI
        priority_order = {
            MissionPriority.CRITICAL: 0,
            MissionPriority.HIGH: 1,
            MissionPriority.MEDIUM: 2,
            MissionPriority.LOW: 3,
            MissionPriority.INFO: 4,
        }
        missions.sort(key=lambda m: (priority_order.get(m.priority, 5), -m.roi_score))

        self.logger.info(f"{len(missions)} missions générées")
        return missions

    def _create_price_increase_mission(self, trigger: dict) -> Mission | None:
        """Crée une mission pour une hausse de prix."""
        merchant = trigger["merchant"]
        increase = trigger["increase_pct"]
        old_price = trigger["old_price"]
        new_price = trigger["new_price"]

        # Calculer l'impact annuel
        freq_multiplier = 12 if trigger["frequency"] == "monthly" else 1
        annual_increase = (new_price - old_price) * freq_multiplier

        action = Action(
            type=ActionType.GENERATE_LETTER,
            label="Générer lettre de réclamation",
            payload={
                "merchant": merchant,
                "issue": f"Hausse de prix de {increase:.1f}% sans préavis",
            },
            requires_human_validation=True,
        )

        return Mission(
            id=self._generate_mission_id(),
            trigger_type=TriggerType.PRICE_INCREASE,
            title=f"📈 Hausse de prix: {merchant}",
            description=f"Votre abonnement {merchant} a augmenté de {increase:.1f}% "
            f"(de {old_price:.2f}€ à {new_price:.2f}€). "
            f"Impact annuel: +{annual_increase:.2f}€.",
            priority=MissionPriority.HIGH if increase >= 20 else MissionPriority.MEDIUM,
            potential_savings=annual_increase,
            effort_level=2,
            time_to_complete=10,
            actions=[action],
            data_sources=["subscriptions", "price_history"],
        )

    def _create_duplicate_mission(self, trigger: dict) -> Mission | None:
        """Crée une mission pour un doublon d'abonnement."""
        category = trigger["category"]
        count = trigger["count"]
        total_cost = trigger["total_monthly_cost"]
        subs = trigger["subscriptions"]

        # Calculer l'économie potentielle (supprimer le plus cher)
        most_expensive = max(subs, key=lambda s: s.average_amount)
        annual_savings = most_expensive.average_amount * 12

        merchants_list = ", ".join([s.merchant for s in subs])

        actions = [
            Action(
                type=ActionType.GENERATE_LETTER,
                label=f"Résilier {most_expensive.merchant}",
                payload={"merchant": most_expensive.merchant},
                requires_human_validation=True,
            ),
            Action(
                type=ActionType.COMPARE_OFFERS,
                label="Comparer les offres",
                payload={"category": category},
                requires_human_validation=False,
            ),
        ]

        return Mission(
            id=self._generate_mission_id(),
            trigger_type=TriggerType.DUPLICATE_SUBSCRIPTION,
            title=f"🔁 Doublon détecté: {category}",
            description=f"Vous avez {count} abonnements {category}: {merchants_list}. "
            f"Coût total: {total_cost:.2f}€/mois. "
            f"Suggestion: Résilier {most_expensive.merchant} "
            f"pour économiser {annual_savings:.2f}€/an.",
            priority=MissionPriority.HIGH,
            potential_savings=annual_savings,
            effort_level=1,
            time_to_complete=5,
            actions=actions,
            data_sources=["subscriptions"],
        )

    def _create_unused_mission(self, trigger: dict) -> Mission | None:
        """Crée une mission pour un abonnement inutilisé."""
        merchant = trigger["merchant"]
        amount = trigger["amount"]
        frequency = trigger["frequency"]
        last_tx = trigger["last_transaction"]

        freq_multiplier = 12 if frequency == "monthly" else 1
        annual_cost = amount * freq_multiplier

        action = Action(
            type=ActionType.GENERATE_LETTER,
            label=f"Résilier {merchant}",
            payload={"merchant": merchant},
            requires_human_validation=True,
        )

        return Mission(
            id=self._generate_mission_id(),
            trigger_type=TriggerType.UNUSED_SUBSCRIPTION,
            title=f"💤 Abonnement dormant: {merchant}",
            description=f"Aucune transaction {merchant} depuis le {last_tx}. "
            f"Vous payez {amount:.2f}€/{frequency} pour un service potentiellement "
            f"inutilisé. Économie potentielle: {annual_cost:.2f}€/an.",
            priority=MissionPriority.MEDIUM,
            potential_savings=annual_cost,
            effort_level=1,
            time_to_complete=5,
            actions=[action],
            data_sources=["subscriptions"],
        )

    def _create_alternative_mission(self, trigger: dict) -> Mission | None:
        """Crée une mission pour une meilleure alternative."""
        current = trigger["current"]
        alt = trigger["alternative"]
        savings = trigger["annual_savings"]

        actions = [
            Action(
                type=ActionType.COMPARE_OFFERS,
                label=f"Voir offre {alt['provider']}",
                payload={
                    "provider": alt["provider"],
                    "plan": alt["plan"],
                    "price": alt["price"],
                },
                requires_human_validation=False,
            ),
        ]

        return Mission(
            id=self._generate_mission_id(),
            trigger_type=TriggerType.BETTER_ALTERNATIVE,
            title=f"💡 Alternative moins chère: {current['merchant']}",
            description=f"Vous payez {current['price']:.2f}€/mois chez {current['merchant']}. "
            f"{alt['provider']} propose {alt['plan']} à {alt['price']:.2f}€/mois. "
            f"Économie potentielle: {savings:.2f}€/an.",
            priority=MissionPriority.MEDIUM,
            potential_savings=savings,
            effort_level=3,
            time_to_complete=30,
            actions=actions,
            data_sources=["subscriptions", "market_data"],
        )

    def _create_cash_mission(self, trigger: dict) -> Mission | None:
        """Crée une mission pour optimiser le cash dormant."""
        excess = trigger["excess_cash"]
        ratio = trigger["cash_ratio"]

        action = Action(
            type=ActionType.INVEST_SUGGESTION,
            label="Voir suggestions d'investissement",
            payload={"excess_cash": excess},
            requires_human_validation=True,
        )

        return Mission(
            id=self._generate_mission_id(),
            trigger_type=TriggerType.CASH_IDLE,
            title="💰 Cash dormant à investir",
            description=f"{ratio:.1f}% de votre patrimoine est en cash ({excess:.0f}€ excès). "
            f"Cette somme pourrait être investie pour générer du rendement. "
            f"À 5% annuel, cela représente {excess * 0.05:.0f}€/an de perte de rendement.",
            priority=MissionPriority.LOW,
            potential_savings=excess * 0.05,  # Rendement perdu
            effort_level=3,
            time_to_complete=60,
            actions=[action],
            data_sources=["wealth_manager"],
        )

    def _create_debt_mission(self, trigger: dict) -> Mission | None:
        """Crée une mission pour un problème d'endettement."""
        ratio = trigger["debt_ratio"]
        severity = trigger["severity"]

        action = Action(
            type=ActionType.EXPORT_DATA,
            label="Exporter bilan complet",
            payload={"type": "debt_analysis"},
            requires_human_validation=False,
        )

        return Mission(
            id=self._generate_mission_id(),
            trigger_type=TriggerType.HIGH_DEBT_RATIO,
            title="⚠️ Taux d'endettement élevé",
            description=f"Votre taux d'endettement est de {ratio:.1f}% (limite recommandée: 33%). "
            f"Cela limite votre capacité d'épargne et présente un risque financier. "
            f"Envisagez de restructurer vos dettes ou d'augmenter vos revenus.",
            priority=MissionPriority.CRITICAL if severity == "critical" else MissionPriority.HIGH,
            potential_savings=0,  # Pas d'économie directe, mais réduction de risque
            effort_level=5,
            time_to_complete=180,
            actions=[action],
            data_sources=["wealth_manager", "liabilities"],
        )

    def _create_diversification_mission(self, trigger: dict) -> Mission | None:
        """Crée une mission pour un problème de diversification."""
        issue = trigger["issue"]
        current_pct = trigger["current_percentage"]
        recommended = trigger["recommended_max"]

        asset_type = "crypto" if issue == "crypto_concentration" else "immobilier"

        action = Action(
            type=ActionType.EXPORT_DATA,
            label="Voir allocation recommandée",
            payload={"type": "diversification_plan"},
            requires_human_validation=True,
        )

        return Mission(
            id=self._generate_mission_id(),
            trigger_type=TriggerType.DIVERSIFICATION_NEEDED,
            title=f"📊 Concentration {asset_type}",
            description=f"{current_pct:.1f}% de votre patrimoine est en {asset_type} "
            f"(recommandé: <{recommended}%). Cette concentration augmente "
            f"le risque de votre portefeuille. Envisagez une diversification.",
            priority=MissionPriority.MEDIUM,
            potential_savings=0,  # Réduction de risque
            effort_level=4,
            time_to_complete=120,
            actions=[action],
            data_sources=["wealth_manager"],
        )

    def execute_action(
        self,
        mission: Mission,
        action_index: int,
        user_data: dict | None = None,
        output_dir: str = "documents",
    ) -> dict[str, Any]:
        """
        Exécute une action d'une mission.

        Args:
            mission: Mission contenant l'action
            action_index: Index de l'action à exécuter
            user_data: Données utilisateur (nom, adresse, etc.)
            output_dir: Répertoire de sortie

        Returns:
            Résultat de l'exécution
        """
        if action_index >= len(mission.actions):
            return {"success": False, "error": "Action index out of range"}

        action = mission.actions[action_index]

        # Vérifier si validation humaine requise
        if action.requires_human_validation:
            self.logger.warning(f"Action requires human validation: {action.label}")
            # Dans une vraie app, on montrerait un dialogue de confirmation

        result = {"success": True, "action": action.type.value, "files": []}

        # Exécuter selon le type
        if action.type == ActionType.GENERATE_LETTER:
            merchant = action.payload.get("merchant", "Prestataire")
            issue = action.payload.get("issue", "")

            user_name = user_data.get("name", "") if user_data else ""
            user_address = user_data.get("address", "") if user_data else ""

            if issue:  # Réclamation
                letter = self.doc_generator.generate_complaint_letter(
                    merchant_name=merchant,
                    issue_description=issue,
                    subscriber_name=user_name,
                    subscriber_address=user_address,
                )
                filename = f"reclamation_{merchant.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
            else:  # Résiliation
                letter = self.doc_generator.generate_cancellation_letter(
                    merchant_name=merchant,
                    subscriber_name=user_name,
                    subscriber_address=user_address,
                )
                filename = f"resiliation_{merchant.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"

            filepath = self.doc_generator.save_document(letter, filename, output_dir)
            result["files"].append(str(filepath))
            result["content"] = letter

        elif action.type == ActionType.COMPARE_OFFERS:
            # Simuler l'ouverture d'un comparateur
            category = action.payload.get("category", "general")
            result["message"] = f"Ouverture du comparateur pour: {category}"
            result["url"] = f"https://comparateur.example.com/{category}"

        elif action.type == ActionType.INVEST_SUGGESTION:
            excess = action.payload.get("excess_cash", 0)
            result["message"] = f"Suggestion d'investissement pour €{excess:,.2f}"
            result["suggestions"] = [
                {"type": "livret_a", "yield": 3.0, "risk": "none"},
                {"type": "fonds_euros", "yield": 4.5, "risk": "low"},
                {"type": "etf_msci", "yield": 7.0, "risk": "medium"},
            ]

        elif action.type == ActionType.EXPORT_DATA:
            export_type = action.payload.get("type", "general")
            filename = f"export_{export_type}_{datetime.now().strftime('%Y%m%d')}.json"
            result["message"] = f"Export des données: {export_type}"
            result["filename"] = filename

        return result

    def get_mission_summary(self, missions: list[Mission]) -> dict[str, Any]:
        """
        Génère un résumé des missions.

        Args:
            missions: Liste des missions

        Returns:
            Statistiques et résumé
        """
        total_savings = sum(m.potential_savings for m in missions)

        by_priority = {}
        by_type = {}

        for mission in missions:
            # Par priorité
            prio = mission.priority.value
            by_priority[prio] = by_priority.get(prio, 0) + 1

            # Par type
            trigger = mission.trigger_type.value
            by_type[trigger] = by_type.get(trigger, 0) + 1

        return {
            "total_missions": len(missions),
            "total_potential_savings": total_savings,
            "by_priority": by_priority,
            "by_type": by_type,
            "high_impact_missions": [
                m
                for m in missions
                if m.priority in (MissionPriority.CRITICAL, MissionPriority.HIGH)
            ],
        }


# ==================== Fonctions utilitaires ====================


def quick_analyze(
    subscriptions: list[Subscription],
    wealth_manager: WealthManager,
    monthly_income: float = 3000.0,
) -> dict[str, Any]:
    """
    Analyse rapide et retourne un résumé des opportunités.

    Args:
        subscriptions: Liste des abonnements
        wealth_manager: Gestionnaire de patrimoine
        monthly_income: Revenu mensuel

    Returns:
        Résumé de l'analyse
    """
    orchestrator = AgentOrchestrator()
    missions = orchestrator.analyze_and_generate_missions(
        subscriptions=subscriptions,
        wealth_manager=wealth_manager,
        monthly_income=monthly_income,
    )

    summary = orchestrator.get_mission_summary(missions)

    return {
        "missions_count": len(missions),
        "potential_annual_savings": summary["total_potential_savings"],
        "top_missions": missions[:3],  # Top 3 missions
        "summary": summary,
    }
