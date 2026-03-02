# Module `modules/notifications`

> Système de notifications V3 pour FinancePerso.

## Vue d'ensemble

Système de notifications unifié avec persistance en base, détecteurs automatiques et UI intégrée.

## Architecture

```
modules/notifications/
├── __init__.py          # Exports et version
├── models.py            # Dataclasses (Notification, NotificationLevel)
├── service.py           # NotificationService (singleton)
├── repository.py        # Accès base de données
├── detectors.py         # Détecteurs de notifications
├── ui.py                # Composants UI
├── center.py            # Centre de notifications
├── manager.py           # Manager (compatibilité)
├── components.py        # Composants UI atomiques
├── proactive.py         # Alertes proactives
├── realtime.py          # Alertes temps réel
└── types.py             # Types et enums
```

## Utilisation

### Créer une notification

```python
from modules.notifications import NotificationService, NotificationType

service = NotificationService()
service.notify(
    type=NotificationType.BUDGET_WARNING,
    title="Budget dépassé",
    message="Vous avez dépassé votre budget Courses",
    level="warning"
)
```

### Afficher dans l'UI

```python
from modules.notifications.ui import render_notification_center

render_notification_center()
```

### Détecteurs automatiques

Les détecteurs s'exécutent automatiquement au démarrage:

- `BudgetDetector` - Alertes budget
- `ValidationReminderDetector` - Rappels validation
- `SpendingInsightDetector` - Insights dépenses
- `RecurringPaymentDetector` - Paiements récurrents

## Types de notifications

| Type | Usage |
|------|-------|
| `budget_warning` | Dépassement budget |
| `validation_reminder` | Transactions en attente |
| `spending_insight` | Analyses dépenses |
| `recurring_payment` | Paiements récurrents |
| `system` | Messages système |

## Migration depuis V2

```python
# Ancien
from modules.ui.feedback import show_notification

# Nouveau
from modules.notifications import NotificationService
```

Voir `docs/MIGRATION_NOTIFICATIONS_V3.md` pour le guide complet.
