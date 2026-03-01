"""
Module de Sécurité & Surveillance AML
======================================

Système de détection d'anomalies et surveillance anti-blanchiment (AML):
- Détection de patterns suspects
- Risk scoring automatique
- Alertes de sécurité
- Audit trail
- Conformité réglementaire

Usage:
    from modules.wealth.security_monitor import SecurityMonitor, RiskLevel
    
    monitor = SecurityMonitor()
    risk_score = monitor.analyze_transaction(transaction)
    
    if risk_score.level == RiskLevel.HIGH:
        monitor.flag_transaction(transaction_id, reason)
"""

import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict
import logging

import pandas as pd

from modules.logger import logger


class RiskLevel(Enum):
    """Niveaux de risque pour les transactions."""
    NONE = "none"           # Pas de risque
    LOW = "low"             # Risque faible
    MEDIUM = "medium"       # Risque modéré
    HIGH = "high"           # Risque élevé
    CRITICAL = "critical"   # Risque critique - action immédiate requise


class RiskFlag(Enum):
    """Types de flags de risque détectables."""
    # Flags AML
    LARGE_AMOUNT = "large_amount"                    # Montant inhabituellement élevé
    RAPID_SUCCESSION = "rapid_succession"            # Plusieurs transactions rapides
    ROUND_AMOUNT = "round_amount"                    # Montants ronds suspects
    OFFSHORE_TRANSFER = "offshore_transfer"          # Transfert vers zone à risque
    SHELL_COMPANY = "shell_company"                  # Entreprise écran suspecte
    PEP_INVOLVED = "pep_involved"                    # Personne politiquement exposée
    
    # Flags comportementaux
    UNUSUAL_HOUR = "unusual_hour"                    # Transaction à heure inhabituelle
    WEEKEND_ACTIVITY = "weekend_activity"            # Activité week-end anormale
    VELOCITY_SPIKE = "velocity_spike"                # Pic de vélocité
    PATTERN_BREAK = "pattern_break"                  # Rupture de pattern habituel
    
    # Flags techniques
    NEW_DEVICE = "new_device"                        # Nouvel appareil
    VPN_TOR = "vpn_tor"                              # Connexion via VPN/TOR
    GEO_IMPOSSIBLE = "geo_impossible"                # Géographie impossible
    MULTIPLE_FAILED = "multiple_failed"              # Multiples échecs


@dataclass
class RiskScore:
    """
    Score de risque d'une transaction.
    
    Attributes:
        transaction_id: ID de la transaction
        score: Score numérique (0-100)
        level: Niveau de risque
        flags: Liste des flags déclenchés
        details: Détails de l'analyse
        timestamp: Date de l'analyse
        requires_review: Nécessite une revue manuelle
    """
    transaction_id: str
    score: float
    level: RiskLevel
    flags: List[RiskFlag]
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    requires_review: bool = False
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire."""
        return {
            'transaction_id': self.transaction_id,
            'score': self.score,
            'level': self.level.value,
            'flags': [f.value for f in self.flags],
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'requires_review': self.requires_review,
        }


@dataclass
class SecurityAlert:
    """
    Alerte de sécurité générée.
    
    Attributes:
        id: Identifiant unique
        alert_type: Type d'alerte
        severity: Sévérité
        description: Description
        affected_transactions: IDs des transactions concernées
        created_at: Date de création
        status: Statut (new, investigating, resolved, false_positive)
        assigned_to: Assignée à
        resolution_notes: Notes de résolution
    """
    id: str
    alert_type: str
    severity: RiskLevel
    description: str
    affected_transactions: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "new"
    assigned_to: Optional[str] = None
    resolution_notes: str = ""
    
    def resolve(self, notes: str, by: str):
        """Marque l'alerte comme résolue."""
        self.status = "resolved"
        self.resolution_notes = notes
        self.assigned_to = by
        logger.info(f"Alerte {self.id} résolue par {by}")


@dataclass
class AuditLogEntry:
    """
    Entrée d'audit pour traçabilité.
    
    Attributes:
        timestamp: Date/heure
        user_id: ID utilisateur
        action: Action effectuée
        resource_type: Type de ressource
        resource_id: ID de la ressource
        ip_address: Adresse IP
        user_agent: User agent
        success: Succès ou échec
        details: Détails additionnels
    """
    timestamp: datetime
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    details: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'ip_address': self.ip_address,
            'success': self.success,
            'details': self.details,
        }


class SecurityMonitor:
    """
    Moniteur de sécurité pour détection AML et anomalies.
    
    Cette classe implémente:
    - Scoring de risque automatique
    - Détection de patterns suspects
    - Gestion des alertes
    - Audit trail
    
    Seuils de risque configurables selon le profil utilisateur.
    """
    
    # Seuils par défaut
    DEFAULT_THRESHOLDS = {
        'large_amount': 10000,           # €10k
        'rapid_succession_seconds': 60,   # 1 minute
        'velocity_daily_limit': 50000,    # €50k/jour
        'unusual_hour_start': 23,         # 23h
        'unusual_hour_end': 6,            # 6h
    }
    
    # Pays à haut risque (exemple simplifié)
    HIGH_RISK_COUNTRIES = {
        'AF', 'BY', 'CF', 'CU', 'IR', 'KP', 'LY', 'MM', 'RU', 'SO', 'SD', 'SY', 'VE', 'YE'
    }
    
    def __init__(self, thresholds: Optional[Dict] = None):
        """
        Initialise le moniteur de sécurité.
        
        Args:
            thresholds: Seuils personnalisés (optionnel)
        """
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS.copy()
        self.alerts: List[SecurityAlert] = []
        self.audit_logs: List[AuditLogEntry] = []
        self.flagged_transactions: Set[str] = set()
        
        # Historique pour analyse de patterns
        self._transaction_history: Dict[str, List[Dict]] = defaultdict(list)
        
        logger.info("SecurityMonitor initialisé")
    
    def analyze_transaction(
        self,
        transaction: Dict[str, Any],
        user_profile: Optional[Dict] = None,
    ) -> RiskScore:
        """
        Analyse une transaction et calcule son score de risque.
        
        Args:
            transaction: Données de la transaction
            user_profile: Profil utilisateur pour contexte
            
        Returns:
            RiskScore avec flags et niveau
        """
        flags = []
        details = {}
        score = 0.0
        
        tx_id = transaction.get('id', 'unknown')
        amount = abs(transaction.get('amount', 0))
        tx_date = transaction.get('date')
        label = transaction.get('label', '')
        
        # 1. Détection montant élevé
        if amount > self.thresholds['large_amount']:
            flags.append(RiskFlag.LARGE_AMOUNT)
            score += 15
            details['large_amount'] = f"{amount}€ > {self.thresholds['large_amount']}€"
        
        # 2. Montants ronds (suspects pour blanchiment)
        if self._is_round_amount(amount):
            flags.append(RiskFlag.ROUND_AMOUNT)
            score += 10
            details['round_amount'] = f"Montant rond: {amount}€"
        
        # 3. Heure inhabituelle
        if tx_date and self._is_unusual_hour(tx_date):
            flags.append(RiskFlag.UNUSUAL_HOUR)
            score += 10
            details['unusual_hour'] = "Transaction entre 23h et 6h"
        
        # 4. Weekend
        if tx_date and self._is_weekend(tx_date):
            flags.append(RiskFlag.WEEKEND_ACTIVITY)
            score += 5
            details['weekend'] = "Activité week-end"
        
        # 5. Vélocité (si historique disponible)
        user_id = transaction.get('user_id', 'default')
        velocity_score = self._check_velocity(user_id, transaction)
        if velocity_score > 0:
            flags.append(RiskFlag.VELOCITY_SPIKE)
            score += velocity_score
            details['velocity'] = f"Pic de vélocité détecté"
        
        # 6. Patterns de label suspects
        label_flags = self._analyze_label(label)
        flags.extend(label_flags)
        score += len(label_flags) * 10
        
        # 7. Transfert offshore (si pays disponible)
        country = transaction.get('country_code')
        if country and country in self.HIGH_RISK_COUNTRIES:
            flags.append(RiskFlag.OFFSHORE_TRANSFER)
            score += 25
            details['offshore'] = f"Pays à risque: {country}"
        
        # Calculer le niveau de risque
        level = self._calculate_risk_level(score)
        requires_review = score >= 30
        
        # Stocker dans l'historique
        self._transaction_history[user_id].append(transaction)
        
        # Logger si risque élevé
        if level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            logger.warning(f"Risque {level.value} détecté pour transaction {tx_id}: score={score}")
        
        return RiskScore(
            transaction_id=tx_id,
            score=score,
            level=level,
            flags=flags,
            details=details,
            requires_review=requires_review,
        )
    
    def analyze_batch(
        self,
        transactions: List[Dict[str, Any]],
        user_profile: Optional[Dict] = None,
    ) -> List[RiskScore]:
        """
        Analyse un lot de transactions.
        
        Args:
            transactions: Liste de transactions
            user_profile: Profil utilisateur
            
        Returns:
            Liste des scores de risque
        """
        scores = []
        
        for tx in transactions:
            score = self.analyze_transaction(tx, user_profile)
            scores.append(score)
            
            # Détecter les patterns de succession rapide
            if len(scores) >= 2:
                self._detect_rapid_succession(scores[-2:], transactions)
        
        return scores
    
    def flag_transaction(self, transaction_id: str, reason: str):
        """
        Flag une transaction pour investigation.
        
        Args:
            transaction_id: ID de la transaction
            reason: Raison du flag
        """
        self.flagged_transactions.add(transaction_id)
        
        # Créer une alerte
        alert = SecurityAlert(
            id=self._generate_alert_id(),
            alert_type="manual_flag",
            severity=RiskLevel.HIGH,
            description=f"Transaction flaguée manuellement: {reason}",
            affected_transactions=[transaction_id],
        )
        self.alerts.append(alert)
        
        logger.warning(f"Transaction {transaction_id} flaguée: {reason}")
    
    def unflag_transaction(self, transaction_id: str, by: str, reason: str):
        """
        Retire le flag d'une transaction.
        
        Args:
            transaction_id: ID de la transaction
            by: Qui retire le flag
            reason: Raison
        """
        if transaction_id in self.flagged_transactions:
            self.flagged_transactions.discard(transaction_id)
            logger.info(f"Flag retiré pour {transaction_id} par {by}: {reason}")
    
    def create_alert(
        self,
        alert_type: str,
        severity: RiskLevel,
        description: str,
        affected_transactions: List[str],
    ) -> SecurityAlert:
        """
        Crée une alerte de sécurité.
        
        Args:
            alert_type: Type d'alerte
            severity: Sévérité
            description: Description
            affected_transactions: IDs concernés
            
        Returns:
            Alerte créée
        """
        alert = SecurityAlert(
            id=self._generate_alert_id(),
            alert_type=alert_type,
            severity=severity,
            description=description,
            affected_transactions=affected_transactions,
        )
        self.alerts.append(alert)
        
        logger.warning(f"Alerte créée: {alert.id} - {alert_type} - {severity.value}")
        
        return alert
    
    def get_pending_alerts(
        self,
        min_severity: Optional[RiskLevel] = None,
    ) -> List[SecurityAlert]:
        """
        Récupère les alertes en attente.
        
        Args:
            min_severity: Sévérité minimum
            
        Returns:
            Liste des alertes
        """
        alerts = [a for a in self.alerts if a.status == "new"]
        
        if min_severity:
            severity_order = {
                RiskLevel.CRITICAL: 4,
                RiskLevel.HIGH: 3,
                RiskLevel.MEDIUM: 2,
                RiskLevel.LOW: 1,
                RiskLevel.NONE: 0,
            }
            min_val = severity_order.get(min_severity, 0)
            alerts = [a for a in alerts if severity_order.get(a.severity, 0) >= min_val]
        
        return sorted(alerts, key=lambda a: a.created_at, reverse=True)
    
    def log_audit(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict] = None,
    ):
        """
        Enregistre une entrée d'audit.
        
        Args:
            user_id: ID utilisateur
            action: Action effectuée
            resource_type: Type de ressource
            resource_id: ID ressource
            ip_address: IP
            user_agent: User agent
            success: Succès
            details: Détails
        """
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details or {},
        )
        self.audit_logs.append(entry)
        
        # Logger critique
        if not success:
            logger.warning(f"Échec audit: {user_id} - {action} - {resource_type}")
    
    def get_audit_trail(
        self,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[AuditLogEntry]:
        """
        Récupère le trail d'audit filtré.
        
        Args:
            user_id: Filtrer par utilisateur
            resource_type: Filtrer par type
            resource_id: Filtrer par ID
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Entrées d'audit
        """
        entries = self.audit_logs
        
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        if resource_type:
            entries = [e for e in entries if e.resource_type == resource_type]
        if resource_id:
            entries = [e for e in entries if e.resource_id == resource_id]
        if start_date:
            entries = [e for e in entries if e.timestamp >= start_date]
        if end_date:
            entries = [e for e in entries if e.timestamp <= end_date]
        
        return sorted(entries, key=lambda e: e.timestamp, reverse=True)
    
    def export_audit_log(self, filepath: str):
        """
        Exporte le log d'audit vers un fichier.
        
        Args:
            filepath: Chemin du fichier
        """
        import json
        
        data = [entry.to_dict() for entry in self.audit_logs]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Audit log exporté: {filepath}")
    
    def get_risk_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Génère un résumé des risques.
        
        Args:
            days: Nombre de jours à analyser
            
        Returns:
            Résumé des risques
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        # Compter les flags
        flag_counts = defaultdict(int)
        level_counts = defaultdict(int)
        
        for user_id, transactions in self._transaction_history.items():
            for tx in transactions:
                tx_date = tx.get('date')
                if isinstance(tx_date, str):
                    tx_date = datetime.fromisoformat(tx_date)
                
                if tx_date and tx_date >= cutoff:
                    # Re-analyser pour stats
                    score = self.analyze_transaction(tx)
                    level_counts[score.level.value] += 1
                    for flag in score.flags:
                        flag_counts[flag.value] += 1
        
        return {
            'period_days': days,
            'flagged_transactions': len(self.flagged_transactions),
            'pending_alerts': len(self.get_pending_alerts()),
            'flag_counts': dict(flag_counts),
            'level_counts': dict(level_counts),
            'high_risk_transactions': level_counts.get('high', 0) + level_counts.get('critical', 0),
        }
    
    # ==================== Méthodes privées ====================
    
    def _is_round_amount(self, amount: float) -> bool:
        """Détecte si un montant est rond (suspect)."""
        # Montants comme 1000, 5000, 10000, etc.
        round_amounts = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000]
        return any(abs(amount - ra) < 1 for ra in round_amounts)
    
    def _is_unusual_hour(self, tx_date) -> bool:
        """Vérifie si la transaction est à une heure inhabituelle."""
        if isinstance(tx_date, str):
            tx_date = datetime.fromisoformat(tx_date)
        
        hour = tx_date.hour
        return hour >= self.thresholds['unusual_hour_start'] or hour < self.thresholds['unusual_hour_end']
    
    def _is_weekend(self, tx_date) -> bool:
        """Vérifie si la transaction est en week-end."""
        if isinstance(tx_date, str):
            tx_date = datetime.fromisoformat(tx_date)
        
        return tx_date.weekday() >= 5  # 5 = Samedi, 6 = Dimanche
    
    def _check_velocity(self, user_id: str, transaction: Dict) -> float:
        """Vérifie la vélocité des transactions."""
        history = self._transaction_history.get(user_id, [])
        
        if len(history) < 3:
            return 0.0
        
        # Calculer le total des 24 dernières heures
        tx_date = transaction.get('date')
        if isinstance(tx_date, str):
            tx_date = datetime.fromisoformat(tx_date)
        
        day_ago = tx_date - timedelta(hours=24)
        daily_total = sum(
            abs(tx.get('amount', 0))
            for tx in history
            if isinstance(tx.get('date'), datetime) and tx['date'] >= day_ago
        )
        
        if daily_total > self.thresholds['velocity_daily_limit']:
            return 20.0  # Score de risque
        
        return 0.0
    
    def _analyze_label(self, label: str) -> List[RiskFlag]:
        """Analyse le libellé pour détecter des patterns suspects."""
        flags = []
        label_upper = label.upper()
        
        # Mots-clés suspects
        suspicious_keywords = [
            'CRYPTO', 'BITCOIN', 'BTC', 'BLOCKCHAIN',
            'CASINO', 'POKER', 'BET', 'GAMBLING',
            'MONEY TRANSFER', 'WESTERN UNION',
        ]
        
        for keyword in suspicious_keywords:
            if keyword in label_upper:
                flags.append(RiskFlag.SHELL_COMPANY)
                break
        
        return flags
    
    def _detect_rapid_succession(self, scores: List[RiskScore], transactions: List[Dict]):
        """Détecte les transactions en succession rapide."""
        if len(scores) < 2:
            return
        
        tx1 = transactions[-2]
        tx2 = transactions[-1]
        
        date1 = tx1.get('date')
        date2 = tx2.get('date')
        
        if isinstance(date1, str):
            date1 = datetime.fromisoformat(date1)
        if isinstance(date2, str):
            date2 = datetime.fromisoformat(date2)
        
        if date1 and date2:
            delta = (date2 - date1).total_seconds()
            if delta < self.thresholds['rapid_succession_seconds']:
                for score in scores:
                    if RiskFlag.RAPID_SUCCESSION not in score.flags:
                        score.flags.append(RiskFlag.RAPID_SUCCESSION)
                        score.score += 15
                        score.details['rapid_succession'] = f"{delta:.0f}s entre transactions"
    
    def _calculate_risk_level(self, score: float) -> RiskLevel:
        """Calcule le niveau de risque à partir du score."""
        if score >= 50:
            return RiskLevel.CRITICAL
        elif score >= 30:
            return RiskLevel.HIGH
        elif score >= 15:
            return RiskLevel.MEDIUM
        elif score > 0:
            return RiskLevel.LOW
        return RiskLevel.NONE
    
    def _generate_alert_id(self) -> str:
        """Génère un ID d'alerte unique."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:6]
        return f"SEC-{timestamp}-{random_suffix.upper()}"


# ==================== Fonctions utilitaires ====================

def quick_risk_check(transaction: Dict[str, Any]) -> RiskScore:
    """
    Vérification rapide de risque pour une transaction.
    
    Args:
        transaction: Transaction à analyser
        
    Returns:
        Score de risque
    """
    monitor = SecurityMonitor()
    return monitor.analyze_transaction(transaction)


def check_suspicious_pattern(transactions: List[Dict]) -> List[Dict]:
    """
    Vérifie un lot de transactions pour patterns suspects.
    
    Args:
        transactions: Liste de transactions
        
    Returns:
        Transactions suspectes avec scores
    """
    monitor = SecurityMonitor()
    results = []
    
    for tx in transactions:
        score = monitor.analyze_transaction(tx)
        if score.level in (RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL):
            results.append({
                'transaction': tx,
                'risk_score': score,
            })
    
    return results


def generate_security_report(days: int = 30) -> Dict[str, Any]:
    """
    Génère un rapport de sécurité.
    
    Args:
        days: Période d'analyse
        
    Returns:
        Rapport de sécurité
    """
    monitor = SecurityMonitor()
    
    return {
        'generated_at': datetime.now().isoformat(),
        'period_days': days,
        'summary': monitor.get_risk_summary(days),
        'pending_alerts': len(monitor.get_pending_alerts()),
        'recommendations': [
            "Surveiller les transactions avec score > 30",
            "Investiguer les flags 'offshore_transfer'",
            "Vérifier les activités week-end répétées",
        ],
    }
