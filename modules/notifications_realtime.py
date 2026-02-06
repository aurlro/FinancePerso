"""
Real-time Notifications System
Détecte et notifie les événements importants en temps réel.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from modules.logger import logger
from modules.ai.category_insights import CategoryInsightsEngine


class AlertType(Enum):
    """Types d'alertes temps réel."""
    ANOMALY = "anomaly"
    BUDGET_OVERRUN = "budget_overrun"
    DUPLICATE = "duplicate"
    NEW_MERCHANT = "new_merchant"
    LARGE_EXPENSE = "large_expense"
    SAVINGS_MILESTONE = "savings_milestone"


@dataclass
class RealTimeAlert:
    """Alerte temps réel."""
    id: str
    type: AlertType
    severity: str  # 'critical', 'warning', 'info', 'success'
    title: str
    message: str
    category: Optional[str] = None
    amount: Optional[float] = None
    timestamp: datetime = None
    actions: List[Dict] = None
    dismissed: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.actions is None:
            self.actions = []


class RealTimeNotificationManager:
    """
    Gestionnaire de notifications temps réel.
    Détecte les événements lors de l'import et de la navigation.
    """
    
    # Seuils de configuration
    LARGE_EXPENSE_THRESHOLD = 100  # €
    ANOMALY_ZSCORE_THRESHOLD = 2.5
    DUPLICATE_TIME_WINDOW_HOURS = 24
    
    def __init__(self):
        self.alerts: List[RealTimeAlert] = []
        self._load_pending_alerts()
    
    def _load_pending_alerts(self):
        """Charge les alertes en attente depuis la session."""
        if 'pending_alerts' not in st.session_state:
            st.session_state['pending_alerts'] = []
        self.alerts = st.session_state['pending_alerts']
    
    def _save_alerts(self):
        """Sauvegarde les alertes dans la session."""
        st.session_state['pending_alerts'] = self.alerts
    
    def check_new_transaction(self, tx: Dict, df_history: pd.DataFrame) -> List[RealTimeAlert]:
        """
        Vérifie une nouvelle transaction et génère des alertes si nécessaire.
        À appeler lors de l'import de chaque transaction.
        
        Args:
            tx: Transaction nouvellement importée
            df_history: Historique des transactions
            
        Returns:
            Liste des alertes générées
        """
        new_alerts = []
        
        # 1. Détecter les grosses dépenses
        if tx.get('amount', 0) < -self.LARGE_EXPENSE_THRESHOLD:
            alert = self._create_large_expense_alert(tx)
            if alert:
                new_alerts.append(alert)
        
        # 2. Détecter les anomalies dans la catégorie
        if not df_history.empty and tx.get('category_validated'):
            category = tx['category_validated']
            # Include all transactions in this category (not just amount < 0)
            # A refund (positive amount) should be included in history for context
            cat_history = df_history[df_history['category_validated'] == category]
            
            if len(cat_history) >= 3:
                amounts = cat_history['amount'].abs()
                mean_amount = amounts.mean()
                std_amount = amounts.std()
                
                if std_amount > 0:
                    tx_amount = abs(tx.get('amount', 0))
                    z_score = (tx_amount - mean_amount) / std_amount
                    
                    if z_score > self.ANOMALY_ZSCORE_THRESHOLD:
                        alert = self._create_anomaly_alert(tx, mean_amount, z_score)
                        new_alerts.append(alert)
        
        # 3. Détecter les doublons potentiels
        duplicate = self._check_duplicate(tx, df_history)
        if duplicate:
            alert = self._create_duplicate_alert(tx, duplicate)
            new_alerts.append(alert)
        
        # 4. Nouveau commerçant
        if not df_history.empty and tx.get('label'):
            known_labels = set(df_history['label'].str.lower().unique())
            if tx['label'].lower() not in known_labels:
                alert = self._create_new_merchant_alert(tx)
                new_alerts.append(alert)
        
        # Sauvegarder les nouvelles alertes
        self.alerts.extend(new_alerts)
        self._save_alerts()
        
        return new_alerts
    
    def check_budget_overrun(self, category: str, spent: float, budget: float) -> Optional[RealTimeAlert]:
        """
        Vérifie si un budget vient d'être dépassé.
        
        Args:
            category: Nom de la catégorie
            spent: Montant dépensé
            budget: Budget défini
            
        Returns:
            Alerte si dépassement, None sinon
        """
        if spent > budget:
            overrun = spent - budget
            percent_over = (overrun / budget) * 100
            
            alert = RealTimeAlert(
                id=f"budget_{category}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                type=AlertType.BUDGET_OVERRUN,
                severity='critical' if percent_over > 20 else 'warning',
                title=f"🚨 Budget {category} dépassé !",
                message=f"Vous avez dépensé {spent:.0f}€ sur {budget:.0f}€ budgeté (+{percent_over:.0f}%)",
                category=category,
                amount=overrun,
                actions=[
                    {'label': 'Voir les dépenses', 'action': 'view_category'},
                    {'label': 'Ajuster le budget', 'action': 'adjust_budget'}
                ]
            )
            
            self.alerts.append(alert)
            self._save_alerts()
            return alert
        
        return None
    
    def check_savings_milestone(self, current_savings: float, previous_savings: float) -> Optional[RealTimeAlert]:
        """
        Détecte les jalons d'épargne positifs.
        
        Args:
            current_savings: Épargne actuelle
            previous_savings: Épargne période précédente
            
        Returns:
            Alerte de célébration si amélioration significative
        """
        if previous_savings <= 0 and current_savings > 0:
            # Passage en positif
            alert = RealTimeAlert(
                id=f"savings_positive_{datetime.now().strftime('%Y%m%d')}",
                type=AlertType.SAVINGS_MILESTONE,
                severity='success',
                title="🎉 Félicitations !",
                message=f"Vous êtes revenu à l'équilibre avec {current_savings:.0f}€ d'épargne ce mois-ci !",
                amount=current_savings,
                actions=[
                    {'label': 'Voir le détail', 'action': 'view_savings'}
                ]
            )
            self.alerts.append(alert)
            self._save_alerts()
            return alert
        
        # Amélioration de 50%+
        if previous_savings > 0:
            improvement = ((current_savings - previous_savings) / previous_savings) * 100
            if improvement >= 50:
                alert = RealTimeAlert(
                    id=f"savings_improvement_{datetime.now().strftime('%Y%m%d')}",
                    type=AlertType.SAVINGS_MILESTONE,
                    severity='success',
                    title="📈 Super progression !",
                    message=f"Votre épargne a augmenté de {improvement:.0f}% par rapport au mois dernier !",
                    amount=current_savings,
                    actions=[
                        {'label': 'Continuer ainsi !', 'action': 'view_trends'}
                    ]
                )
                self.alerts.append(alert)
                self._save_alerts()
                return alert
        
        return None
    
    def _create_large_expense_alert(self, tx: Dict) -> Optional[RealTimeAlert]:
        """Crée une alerte pour une grosse dépense."""
        amount = abs(tx.get('amount', 0))
        return RealTimeAlert(
            id=f"large_{tx.get('id', 'unknown')}",
            type=AlertType.LARGE_EXPENSE,
            severity='warning',
            title="💰 Grosse dépense détectée",
            message=f"'{tx.get('label', 'Inconnu')}' de {amount:.0f}€ vient d'être importée.",
            category=tx.get('category_validated'),
            amount=amount,
            actions=[
                {'label': 'Vérifier', 'action': 'view_transaction'},
                {'label': 'Catégoriser', 'action': 'categorize'}
            ]
        )
    
    def _create_anomaly_alert(self, tx: Dict, mean_amount: float, z_score: float) -> RealTimeAlert:
        """Crée une alerte pour une anomalie."""
        amount = abs(tx.get('amount', 0))
        deviation = ((amount - mean_amount) / mean_amount) * 100
        
        return RealTimeAlert(
            id=f"anomaly_{tx.get('id', 'unknown')}",
            type=AlertType.ANOMALY,
            severity='critical' if z_score > 3 else 'warning',
            title="🚨 Dépense inhabituelle",
            message=f"'{tx.get('label', 'Inconnu')}' à {amount:.0f}€ est {deviation:.0f}% plus élevé que votre moyenne ({mean_amount:.0f}€)",
            category=tx.get('category_validated'),
            amount=amount,
            actions=[
                {'label': 'Vérifier', 'action': 'view_transaction'},
                {'label': 'Marquer OK', 'action': 'dismiss'}
            ]
        )
    
    def _check_duplicate(self, tx: Dict, df_history: pd.DataFrame) -> Optional[pd.Series]:
        """Vérifie si une transaction similaire existe déjà."""
        if df_history.empty:
            return None
        
        # Recherche dans les dernières 24h
        cutoff = datetime.now() - timedelta(hours=self.DUPLICATE_TIME_WINDOW_HOURS)
        recent = df_history[df_history['date_dt'] >= cutoff]
        
        if recent.empty:
            return None
        
        # Match sur montant et libellé similaire
        amount = tx.get('amount', 0)
        label = tx.get('label', '').lower()
        
        for _, row in recent.iterrows():
            amount_match = abs(row['amount'] - amount) < 0.01
            label_similar = label in row['label'].lower() or row['label'].lower() in label
            
            if amount_match and label_similar:
                return row
        
        return None
    
    def _create_duplicate_alert(self, tx: Dict, duplicate: pd.Series) -> RealTimeAlert:
        """Crée une alerte pour un doublon potentiel."""
        return RealTimeAlert(
            id=f"dup_{tx.get('id', 'unknown')}",
            type=AlertType.DUPLICATE,
            severity='warning',
            title="⚠️ Doublon potentiel",
            message=f"Une transaction similaire à '{tx.get('label')}' existe déjà (importée le {duplicate.get('date', '?')})",
            category=tx.get('category_validated'),
            amount=abs(tx.get('amount', 0)),
            actions=[
                {'label': 'Voir l\'original', 'action': 'view_original'},
                {'label': 'Conserver quand même', 'action': 'keep'}
            ]
        )
    
    def _create_new_merchant_alert(self, tx: Dict) -> RealTimeAlert:
        """Crée une alerte pour un nouveau commerçant."""
        return RealTimeAlert(
            id=f"new_{tx.get('id', 'unknown')}",
            type=AlertType.NEW_MERCHANT,
            severity='info',
            title="🆕 Nouveau commerçant",
            message=f"'{tx.get('label')}' n'a jamais été vu auparavant. Vérifiez la catégorisation.",
            category=tx.get('category_validated'),
            amount=abs(tx.get('amount', 0)),
            actions=[
                {'label': 'Catégoriser', 'action': 'categorize'}
            ]
        )
    
    def get_pending_alerts(self, severity_filter: Optional[List[str]] = None) -> List[RealTimeAlert]:
        """
        Récupère les alertes en attente.
        
        Args:
            severity_filter: Filtrer par sévérité ['critical', 'warning', 'info', 'success']
            
        Returns:
            Liste des alertes non dismissées
        """
        pending = [a for a in self.alerts if not a.dismissed]
        
        if severity_filter:
            pending = [a for a in pending if a.severity in severity_filter]
        
        # Trier par sévérité puis date
        severity_order = {'critical': 0, 'warning': 1, 'info': 2, 'success': 3}
        pending.sort(key=lambda x: (severity_order.get(x.severity, 4), x.timestamp), reverse=True)
        
        return pending
    
    def dismiss_alert(self, alert_id: str):
        """Marque une alerte comme traitée."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.dismissed = True
                break
        self._save_alerts()
    
    def dismiss_all(self):
        """Marque toutes les alertes comme traitées."""
        for alert in self.alerts:
            alert.dismissed = True
        self._save_alerts()
    
    def clear_old_alerts(self, days: int = 7):
        """Supprime les alertes de plus de X jours."""
        cutoff = datetime.now() - timedelta(days=days)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff or not a.dismissed]
        self._save_alerts()


# Instance globale
_notification_manager = None

def get_notification_manager() -> RealTimeNotificationManager:
    """Singleton du gestionnaire de notifications."""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = RealTimeNotificationManager()
    return _notification_manager


# Fonctions utilitaires pour l'UI

def render_notification_banner():
    """
    Affiche une bannière avec les alertes en attente.
    À placer en haut de l'application.
    """
    manager = get_notification_manager()
    alerts = manager.get_pending_alerts()
    
    if not alerts:
        return
    
    # Afficher seulement les alertes critiques/warning
    critical_alerts = [a for a in alerts if a.severity in ['critical', 'warning']]
    
    if critical_alerts:
        with st.container(border=True):
            st.markdown(f"### 🔔 {len(critical_alerts)} alerte{'s' if len(critical_alerts) > 1 else ''} en attente")
            
            for alert in critical_alerts[:3]:  # Limiter à 3
                color = "🔴" if alert.severity == 'critical' else "🟠"
                with st.container():
                    cols = st.columns([4, 1])
                    with cols[0]:
                        st.write(f"{color} **{alert.title}**")
                        st.caption(alert.message)
                    with cols[1]:
                        if st.button("✓", key=f"dismiss_{alert.id}"):
                            manager.dismiss_alert(alert.id)
                            st.rerun()
            
            if len(critical_alerts) > 3:
                st.caption(f"... et {len(critical_alerts) - 3} autres alertes")


def render_notification_center():
    """
    Centre de notifications complet.
    À intégrer dans une page dédiée ou la configuration.
    """
    manager = get_notification_manager()
    
    st.header("🔔 Centre de Notifications")
    
    # Onglets par type
    tab_all, tab_critical, tab_success = st.tabs(["Toutes", "Alertes", "Succès"])
    
    with tab_all:
        alerts = manager.get_pending_alerts()
        _render_alerts_list(alerts, manager)
    
    with tab_critical:
        alerts = manager.get_pending_alerts(['critical', 'warning'])
        _render_alerts_list(alerts, manager)
    
    with tab_success:
        alerts = manager.get_pending_alerts(['success'])
        _render_alerts_list(alerts, manager)


def _render_alerts_list(alerts: List[RealTimeAlert], manager: RealTimeNotificationManager):
    """Rendu d'une liste d'alertes."""
    if not alerts:
        st.info("Aucune notification")
        return
    
    for alert in alerts:
        icon_map = {
            'critical': '🔴',
            'warning': '🟠',
            'info': '🔵',
            'success': '🟢'
        }
        
        with st.container(border=True):
            cols = st.columns([4, 1])
            
            with cols[0]:
                st.write(f"{icon_map.get(alert.severity, '⚪')} **{alert.title}**")
                st.caption(alert.message)
                st.caption(f"_{alert.timestamp.strftime('%d/%m %H:%M')}_")
                
                # Actions
                if alert.actions:
                    action_cols = st.columns(len(alert.actions))
                    for i, action in enumerate(alert.actions):
                        with action_cols[i]:
                            st.button(action['label'], key=f"{alert.id}_{action['action']}")
            
            with cols[1]:
                if st.button("✓ Lu", key=f"read_{alert.id}"):
                    manager.dismiss_alert(alert.id)
                    st.rerun()
    
    if st.button("🗑️ Tout marquer comme lu"):
        manager.dismiss_all()
        st.rerun()