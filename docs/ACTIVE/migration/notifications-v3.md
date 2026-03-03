# Guide de Migration - Système de Notifications V3

> Documentation complète pour la migration du système de notifications V2 vers V3.

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Changements pour les utilisateurs](#2-changements-pour-les-utilisateurs)
3. [Changements pour les développeurs](#3-changements-pour-les-développeurs)
4. [Migration des données](#4-migration-des-données)
5. [Timeline de transition](#5-timeline-de-transition)
6. [Checklist de migration](#6-checklist-de-migration)
7. [Référence API](#7-référence-api)

---

## 1. Vue d'ensemble

### Pourquoi une nouvelle version ?

Le système de notifications V2, bien que fonctionnel, présentait plusieurs limitations :

- **Pas de persistance en base de données** - Les notifications étaient stockées dans un fichier JSON (`Data/notifications_v2.json`)
- **Pas de déduplication avancée** - Risque de spam de notifications similaires
- **API limitée** - Pas de typage fort des notifications
- **Pas de gestion fine des préférences** - Impossible de désactiver certains types spécifiques
- **Pas d'intégration avec le Design System** - Interface incohérente

### Principales améliorations

| Fonctionnalité | V2 | V3 |
|---------------|-----|-----|
| Persistance | Fichier JSON | SQLite avec migration 007 |
| Typage | String libre | `NotificationType` enum |
| Déduplication | Basique (groupe) | Clé personnalisable + fenêtre temps |
| Préférences | Globales | Par niveau + par type |
| Actions | URL simple | Actions riches (navigate, dismiss, custom) |
| UI | Composants legacy | Design System intégré |
| Expiration | Non | Support natif |
| Épinglage | Non | Support natif |

### Tableau comparatif V2 vs V3

```
┌─────────────────────┬──────────────────────────┬──────────────────────────┐
│ Aspect              │ V2                       │ V3                       │
├─────────────────────┼──────────────────────────┼──────────────────────────┤
│ Module principal    │ modules.ui.notifications │ modules.notifications    │
│ Manager             │ NotificationManager      │ NotificationService      │
│ Stockage            │ JSON file                │ DB SQLite (migration 007)│
│ Singleton           │ Oui (thread-safe)        │ Oui                      │
│ Types de notifs     │ 5 niveaux                │ 5 niveaux + 20+ types    │
│ Historique          │ 100 items max            │ Configurable (défaut 50) │
│ Actions             │ Callback/URL             │ Rich actions avec data   │
│ Préférences DB      │ Partiel                  │ Table dédiée complète    │
└─────────────────────┴──────────────────────────┴──────────────────────────┘
```

---

## 2. Changements pour les utilisateurs

### Nouvelle page : `pages/13_Notifications_V3.py`

Une nouvelle page dédiée au centre de notifications V3 est disponible :

- **Centre de notifications** - Historique complet avec filtres
- **Paramètres** - Configuration fine des préférences
- **Test** - Création de notifications de test

Accès : `Sidebar > 🔔 Notifications V3` ou directement via l'URL.

### Nouveau badge sidebar

Le V3 propose un nouveau composant de badge pour la sidebar :

```python
from modules.notifications.ui import render_notification_badge

# Dans la sidebar
render_notification_badge()
```

Caractéristiques :
- Design moderne avec le Design System
- Affiche les 3 dernières notifications non lues
- Compteur visuel avec niveau de criticité (couleur)
- Navigation rapide vers le centre complet

### Nouveau centre de notifications

Le centre de notifications V3 (`render_notification_center`) offre :

- **Stats en temps réel** - Non lues, total, critiques
- **Filtres avancés** - Par type, statut, catégorie
- **Tri flexible** - Date, priorité
- **Actions rapides** - Tout marquer comme lu, vider l'historique
- **Cartes riches** - Avec icônes, timestamps relatifs, actions

### Migration des préférences utilisateur

⚠️ **Important** : Les préférences V2 ne sont **pas migrées automatiquement** vers V3.

**À faire pour chaque utilisateur :**

1. Se rendre sur la page `13_Notifications_V3.py`
2. Onglet "⚙️ Paramètres"
3. Reconfigurer les préférences souhaitées
4. Sauvegarder

Les préférences V3 sont stockées dans la table `notification_preferences` (migration 007).

---

## 3. Changements pour les développeurs

### API avant (V2)

```python
from modules.ui.notifications import NotificationManager

manager = NotificationManager()

# Créer une notification
manager.add_notification(
    level="warning",
    title="Alerte Budget",
    message="Vous avez atteint 90% du budget Alimentation"
)

# Ou utiliser les helpers
manager.success("Opération réussie!")
manager.warning("Attention", "Message...")
manager.error("Erreur", persistent=True)

# Marquer comme lu
manager.mark_as_read(notification_id)

# Récupérer les non-lues
unread = manager.get_unread()
```

### API après (V3)

```python
from modules.notifications import NotificationService, NotificationType

service = NotificationService()

# Créer une notification typée
service.notify(
    type=NotificationType.BUDGET_WARNING,
    title="Alerte Budget",
    message="Vous avez atteint 90% du budget Alimentation",
    actions=[
        NotificationAction("Voir", "navigate", "/budgets"),
        NotificationAction("Ignorer", "dismiss")
    ]
)

# Utiliser les méthodes spécialisées
service.notify_budget(category="Alimentation", spent=900, budget=1000, percentage=90)
service.notify_validation_reminder(count=12, oldest_days=18)
service.notify_duplicate(date="2024-01-15", label="Casino", amount=45.50, count=2)
service.notify_achievement(badge_name="Maître de l'épargne", badge_icon="💰")

# Marquer comme lu
service.mark_read(notification_id)

# Récupérer les non-lues
unread = service.get_unread(limit=10)
```

### Différences clés

| Aspect | V2 | V3 |
|--------|-----|-----|
| Import | `from modules.ui.notifications import NotificationManager` | `from modules.notifications import NotificationService, NotificationType` |
| Instanciation | `manager = NotificationManager()` | `service = NotificationService()` |
| Méthode principale | `manager.notify(...)` | `service.notify(...)` |
| Niveau | `level=NotificationLevel.WARNING` | Déduit du `NotificationType` |
| Actions | `actions=[NotificationAction(...)]` | Identique |
| Déduplication | `group="budget_alert"` | `dedup_key="budget_alim_20240115", dedup_hours=24` |

### Exemple de migration complète

**Avant (V2) :**

```python
from modules.ui.notifications import NotificationManager, NotificationLevel, NotificationAction

manager = NotificationManager()

# Alertes budget
alerts = check_budget_alerts()
for alert in alerts:
    if alert["level"] == "critical":
        level = NotificationLevel.CRITICAL
    else:
        level = NotificationLevel.WARNING
    
    manager.notify(
        title=f"Alerte {alert['category']}",
        message=f"Budget dépassé: {alert['percentage']:.0f}%",
        level=level,
        actions=[NotificationAction("Voir", url="/budgets")]
    )
```

**Après (V3) :**

```python
from modules.notifications import NotificationService

service = NotificationService()

# Alertes budget
alerts = check_budget_alerts()
for alert in alerts:
    service.notify_budget(
        category=alert["category"],
        spent=alert["spent"],
        budget=alert["budget"],
        percentage=alert["percentage"]
    )
```

### Types de notifications disponibles (V3)

```python
from modules.notifications.models import NotificationType

# Budget
NotificationType.BUDGET_WARNING      # Approche du seuil
NotificationType.BUDGET_CRITICAL     # Dépassement
NotificationType.BUDGET_OVERRUN      # Dépassement confirmé

# Transactions
NotificationType.VALIDATION_REMINDER  # Transactions en attente
NotificationType.IMPORT_REMINDER      # Pas importé depuis X jours
NotificationType.DUPLICATE_DETECTED   # Doublons trouvés
NotificationType.LARGE_EXPENSE        # Dépense importante
NotificationType.UNUSUAL_PATTERN      # Pattern anormal

# Intelligence
NotificationType.ANOMALY_DETECTED     # Anomalie statistique
NotificationType.RECURRING_MISSING    # Paiement récurrent absent
NotificationType.NEW_MERCHANT         # Nouveau commerçant
NotificationType.PRICE_INCREASE       # Augmentation prix

# Objectifs
NotificationType.GOAL_ACHIEVED        # Objectif atteint
NotificationType.GOAL_PROGRESS        # Progression objectif
NotificationType.SAVINGS_MILESTONE    # Palier épargne

# Gamification
NotificationType.BADGE_EARNED         # Badge débloqué
NotificationType.STREAK_MILESTONE     # Streak atteint
NotificationType.CHALLENGE_COMPLETED  # Challenge terminé

# Système
NotificationType.SYSTEM_UPDATE        # Nouvelle fonctionnalité
NotificationType.BACKUP_REMINDER      # Rappel sauvegarde
NotificationType.SECURITY_ALERT       # Alerte sécurité

# Insights
NotificationType.WEEKLY_SUMMARY       # Récap hebdomadaire
NotificationType.MONTHLY_INSIGHT      # Insight mensuel
NotificationType.SPENDING_INSIGHT     # Insight dépenses
```

---

## 4. Migration des données

### Table DB créée par migration 007

Le fichier `migrations/007_notifications.sql` crée :

1. **Table `notifications`** - Stockage principal des notifications
2. **Table `notification_preferences`** - Préférences utilisateur
3. **Table `notification_history`** - Historique des envois (dédup)
4. **Vue `v_notifications_active`** - Notifications actives (non lues, non expirées)
5. **Vue `v_notification_stats`** - Statistiques par utilisateur

### Pas de migration automatique des notifications V2

⚠️ Les notifications existantes en V2 (fichier `Data/notifications_v2.json`) **ne sont pas migrées**.

**Raisons :**
- Structure différente (pas de `type` en V2)
- Risque de conflits avec la déduplication V3
- Opportunité de repartir sur un historique propre

**Action recommandée :**
```python
# Au premier lancement V3, notifier l'utilisateur
service.notify(
    type=NotificationType.SYSTEM_UPDATE,
    title="🆕 Système de notifications mis à jour",
    message="Les anciennes notifications n'ont pas été migrées. "
            "Configurez vos préférences dans la page Notifications V3.",
    actions=[NotificationAction("Configurer", "navigate", "13_Notifications_V3")]
)
```

### Les préférences utilisateur doivent être reconfigurées

Les préférences V2 étaient stockées dans `app_settings` avec le préfixe `notif_`.
Les préférences V3 utilisent la table dédiée `notification_preferences`.

**Mapping des préférences :**

| V2 (app_settings) | V3 (notification_preferences) |
|-------------------|-------------------------------|
| `notif_enabled` | `critical_enabled`, `warning_enabled`, etc. |
| `notif_desktop` | `desktop_enabled` |
| `notif_email_enabled` | `email_enabled` |
| `notif_threshold_warning` | `budget_warning_threshold` |
| `notif_threshold_critical` | `budget_critical_threshold` |

---

## 5. Timeline de transition

### Phase 1 : Parallèle (maintenant)

**Durée** : Immédiat et pendant 1 mois

- V2 et V3 coexistent
- V2 reste le système par défaut dans le code existant
- V3 disponible via `pages/13_Notifications_V3.py`
- Les développeurs peuvent migrer progressivement

**Action :**
```python
# Le wrapper V2 continue de fonctionner
from modules.ui.notifications import NotificationManager
manager = NotificationManager()  # Redirige vers V2
```

### Phase 2 : Transition (dans 1 mois)

**Durée** : 2 mois

- V3 devient le système par défaut
- Le wrapper V2 redirige vers V3
- Documentation et exemples mis à jour
- Nouveau code doit utiliser V3

**Action :**
```python
# Le wrapper V2 redirige vers V3
from modules.ui.notifications import NotificationManager
manager = NotificationManager()  # Redirige maintenant vers V3
```

### Phase 3 : Fin (dans 3 mois)

**Durée** : Permanent

- V2 supprimé du codebase
- Fichier `Data/notifications_v2.json` peut être supprimé
- Documentation V2 archivée

---

## 6. Checklist de migration

Pour chaque fichier utilisant l'ancien système :

### Étapes de migration

- [ ] **Remplacer les imports**
  ```python
  # Avant
  from modules.ui.notifications import NotificationManager, NotificationLevel
  
  # Après
  from modules.notifications import NotificationService, NotificationType
  ```

- [ ] **Adapter les appels API**
  ```python
  # Avant
  manager = NotificationManager()
  manager.notify(title="...", message="...", level=NotificationLevel.WARNING)
  
  # Après
  service = NotificationService()
  service.notify(type=NotificationType.BUDGET_WARNING, title="...", message="...")
  ```

- [ ] **Mettre à jour la gestion des actions**
  ```python
  # Avant
  NotificationAction(label="Voir", url="/budgets")
  
  # Après
  NotificationAction("Voir", "navigate", "/budgets")
  ```

- [ ] **Tester les notifications**
  - Créer des notifications de test
  - Vérifier l'affichage dans le centre V3
  - Tester les actions (clic sur boutons)
  - Vérifier la déduplication

- [ ] **Mettre à jour la documentation**
  - Commentaires de code
  - README du module
  - Documentation utilisateur si applicable

### Fichiers à migrer (exemples)

```bash
# Rechercher les usages de l'ancien système
grep -r "NotificationManager" modules/ pages/ --include="*.py"
grep -r "from modules.ui.notifications" modules/ pages/ --include="*.py"
grep -r "add_notification" modules/ pages/ --include="*.py"
```

---

## 7. Référence API

### NotificationService (V3)

```python
class NotificationService:
    """Service singleton pour la gestion des notifications."""
    
    # Création
    def notify(self, type, message, title=None, **kwargs) -> Notification
    def notify_budget(self, category, spent, budget, percentage) -> Notification
    def notify_validation_reminder(self, count, oldest_days) -> Notification
    def notify_duplicate(self, date, label, amount, count) -> Notification
    def notify_import_reminder(self, days_since_import) -> Notification
    def notify_achievement(self, badge_name, badge_icon) -> Notification
    
    # Récupération
    def get_unread(self, limit=50, category=None) -> list[Notification]
    def get_all(self, limit=50, include_dismissed=False) -> list[Notification]
    def count_unread(self) -> int
    def get_by_id(self, notification_id) -> Notification | None
    
    # Gestion
    def mark_read(self, notification_id) -> bool
    def mark_all_read(self) -> int
    def dismiss(self, notification_id) -> bool
    def delete(self, notification_id) -> bool
    def cleanup(self, days=30) -> int
    
    # Préférences
    def get_preferences(self) -> NotificationPreferences
    def save_preferences(self, prefs) -> None
    def is_enabled(self, type) -> bool
```

### Composants UI (V3)

```python
from modules.notifications.ui import (
    render_notification_badge,      # Badge sidebar
    render_notification_center,      # Centre complet
    render_notification_settings,    # Paramètres
)

# Utilisation
render_notification_badge(service)
render_notification_center(service)
render_notification_settings(service)
```

### Paramètres de notify()

```python
service.notify(
    type=NotificationType.BUDGET_WARNING,  # Obligatoire: type de notification
    message="Vous avez atteint 85%",        # Obligatoire: message
    title="Budget Alimentation",           # Optionnel: titre
    level=None,                            # Optionnel: auto-déduit du type
    icon=None,                             # Optionnel: emoji personnalisé
    category=None,                         # Optionnel: pour regroupement
    source=None,                           # Optionnel: module source
    actions=None,                          # Optionnel: liste d'actions
    metadata=None,                         # Optionnel: données additionnelles
    dedup_key=None,                        # Optionnel: clé de déduplication
    dedup_hours=24,                        # Optionnel: fenêtre de déduplication
    expires_in_hours=None,                 # Optionnel: expiration
    pin=False,                             # Optionnel: épingler
)
```

---

## Support et questions

Pour toute question sur la migration :

1. Consulter ce guide
2. Vérifier les exemples dans `pages/13_Notifications_V3.py`
3. Se référer au code source dans `modules/notifications/`
4. Ouvrir une issue avec le label `migration-v3`

---

*Dernière mise à jour : 2026-02-28*
*Version du guide : 1.0.0*
*Compatible avec FinancePerso v5.2.1+*
