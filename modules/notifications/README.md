# Module Notifications V3

> Système de notifications unifié avec persistance DB pour FinancePerso

**Version:** 3.0.0  
**Compatibilité:** FinancePerso v5.2.1+

---

## 📋 Description

Le module `notifications` fournit un système de notifications complet et unifié pour FinancePerso, remplaçant l'ancien système V2 basé sur JSON. Il offre une persistance en base de données, une typage fort des notifications, une déduplication avancée et une intégration complète avec le Design System.

### Fonctionnalités clés

- **Persistance SQLite** - Stockage durable des notifications
- **Typage fort** - 20+ types de notifications prédéfinis
- **Déduplication intelligente** - Clé personnalisable avec fenêtre temporelle
- **Préférences granulaires** - Par niveau et par type de notification
- **Actions riches** - Navigation, dismissal, actions personnalisées
- **Expiration & épinglage** - Gestion avancée du cycle de vie
- **Design System** - Interface cohérente avec le reste de l'application

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NotificationService                       │
│                        (Singleton Pattern)                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Service    │  │  Repository  │  │   DetectorRegistry   │  │
│  │   (.notify)  │──│   (SQLite)   │  │    (.run_all)        │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│         │                 │                    │               │
│         ▼                 ▼                    ▼               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Notification                          │  │
│  │  (id, level, type, title, message, actions, metadata)   │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        UI Components                             │
│  ┌────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │  Badge Sidebar │  │ NotificationCenter│  │    Settings    │ │
│  │ (render_badge) │  │  (render_center)  │  │ (render_prefs) │ │
│  └────────────────┘  └──────────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Rôle de chaque fichier

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Point d'entrée du module, exports publics et version |
| `models.py` | Dataclasses et enums (`Notification`, `NotificationType`, `NotificationLevel`) |
| `service.py` | `NotificationService` - API principale et logique métier |
| `repository.py` | `NotificationRepository` - Accès données SQLite |
| `detectors.py` | Détecteurs automatiques de notifications pertinentes |
| `ui.py` | Composants Streamlit pour l'affichage (badge, centre, paramètres) |

---

## 🚀 API Rapide

### Installation / Import

```python
from modules.notifications import (
    NotificationService,
    NotificationType,
    NotificationLevel,
    NotificationAction,
)
```

### Créer une notification

```python
service = NotificationService()

# Notification simple
service.notify(
    type=NotificationType.BUDGET_WARNING,
    title="Budget Alimentation",
    message="Vous avez atteint 85% de votre budget mensuel",
)

# Avec actions
service.notify(
    type=NotificationType.VALIDATION_REMINDER,
    title="Transactions en attente",
    message="12 transactions nécessitent votre validation",
    actions=[
        NotificationAction("Valider", "navigate", "/operations"),
        NotificationAction("Ignorer", "dismiss"),
    ],
)

# Méthodes spécialisées
service.notify_budget(category="Alimentation", spent=850, budget=1000, percentage=85)
service.notify_validation_reminder(count=12, oldest_days=18)
service.notify_duplicate(date="2024-01-15", label="Casino", amount=45.50, count=2)
service.notify_achievement(badge_name="Maître de l'épargne", badge_icon="💰")
```

### Récupérer les non-lues

```python
# Récupérer les notifications non lues (triées par priorité)
unread = service.get_unread(limit=10)

# Filtrer par catégorie
budget_alerts = service.get_unread(category="budget")

# Compter
count = service.count_unread()
```

### Marquer comme lu

```python
# Marquer une notification comme lue
service.mark_read("abc12345")

# Marquer toutes comme lues
service.mark_all_read()

# Ignorer (dismiss)
service.dismiss("abc12345")
```

---

## 📊 Types de notifications

Le système supporte **20+ types de notifications** organisés par catégorie :

### 💰 Budget

| Type | Description | Niveau |
|------|-------------|--------|
| `BUDGET_WARNING` | Approche du seuil défini | `warning` |
| `BUDGET_CRITICAL` | Dépassement imminent | `critical` |
| `BUDGET_OVERRUN` | Dépassement confirmé | `success` |

### 📝 Transactions

| Type | Description | Niveau |
|------|-------------|--------|
| `VALIDATION_REMINDER` | Transactions en attente de validation | `warning` |
| `IMPORT_REMINDER` | Pas d'import depuis X jours | `info` |
| `DUPLICATE_DETECTED` | Doublons détectés | `warning` |
| `LARGE_EXPENSE` | Dépense inhabituellement importante | `warning` |
| `UNUSUAL_PATTERN` | Pattern de dépense anormal | `warning` |

### 🧠 Intelligence

| Type | Description | Niveau |
|------|-------------|--------|
| `ANOMALY_DETECTED` | Anomalie statistique détectée | `warning` |
| `RECURRING_MISSING` | Paiement récurrent absent | `warning` |
| `NEW_MERCHANT` | Nouveau commerçant détecté | `info` |
| `PRICE_INCREASE` | Augmentation de prix détectée | `warning` |

### 🎯 Objectifs

| Type | Description | Niveau |
|------|-------------|--------|
| `GOAL_ACHIEVED` | Objectif financier atteint | `success` |
| `GOAL_PROGRESS` | Progression vers un objectif | `info` |
| `SAVINGS_MILESTONE` | Palier d'épargne atteint | `success` |

### 🏆 Gamification

| Type | Description | Niveau |
|------|-------------|--------|
| `BADGE_EARNED` | Badge débloqué | `achievement` |
| `STREAK_MILESTONE` | Streak de connexion atteint | `achievement` |
| `CHALLENGE_COMPLETED` | Challenge terminé | `achievement` |

### ⚙️ Système

| Type | Description | Niveau |
|------|-------------|--------|
| `SYSTEM_UPDATE` | Nouvelle fonctionnalité disponible | `info` |
| `BACKUP_REMINDER` | Rappel de sauvegarde | `info` |
| `SECURITY_ALERT` | Alerte de sécurité | `critical` |

### 📊 Insights

| Type | Description | Niveau |
|------|-------------|--------|
| `WEEKLY_SUMMARY` | Récapitulatif hebdomadaire | `info` |
| `MONTHLY_INSIGHT` | Insight mensuel | `info` |
| `SPENDING_INSIGHT` | Analyse des dépenses | `info` |

---

## 🔍 Détecteurs

Le système inclut **6 détecteurs automatiques** qui analysent les données et créent des notifications pertinentes :

| Détecteur | Classe | Description |
|-----------|--------|-------------|
| **Budget Alert** | `BudgetAlertDetector` | Surveille les dépassements de budget et crée des alertes warning/critical |
| **Validation Reminder** | `ValidationReminderDetector` | Détecte les transactions en attente depuis trop longtemps |
| **Import Reminder** | `ImportReminderDetector` | Vérifie la date du dernier import et rappelle si > 7 jours |
| **Duplicate Detector** | `DuplicateDetector` | Identifie les transactions en double (même date/label/montant) |
| **Anomaly Detector** | `AnomalyDetector` | Analyse les variations de dépenses vs moyenne historique |
| **Recurring Missing** | `RecurringMissingDetector` | Détecte les paiements récurrents attendus mais absents |

### Utilisation des détecteurs

```python
from modules.notifications import DetectorRegistry, NotificationService

service = NotificationService()
registry = DetectorRegistry(service)

# Exécuter tous les détecteurs
stats = registry.run_all()
print(f"Notifications créées: {stats}")
# Output: {'budget_alerts': 2, 'validation_reminder': 1, ...}

# Exécuter un détecteur spécifique
registry.run("budget_alerts")

# Lister les détecteurs disponibles
print(registry.list_detectors())
```

### Comment ils fonctionnent

1. **BudgetAlertDetector** : Compare les dépenses réelles aux budgets définis, utilise les seuils des préférences utilisateur
2. **ValidationReminderDetector** : Compte les transactions `pending`, calcule l'âge de la plus ancienne
3. **ImportReminderDetector** : Récupère la date du dernier import via `MAX(created_at)`
4. **DuplicateDetector** : Requête SQL avec `GROUP BY date, label, amount HAVING COUNT(*) > 1`
5. **AnomalyDetector** : Compare le mois courant à la moyenne des 3 mois précédents
6. **RecurringMissingDetector** : Analyse les patterns récurrents via window functions SQL

---

## 🗄️ Base de données

### Schéma de la table `notifications`

```sql
CREATE TABLE notifications (
    id TEXT PRIMARY KEY,
    level TEXT NOT NULL CHECK (level IN ('critical', 'warning', 'info', 'success', 'achievement')),
    type TEXT NOT NULL,
    title TEXT,
    message TEXT NOT NULL,
    icon TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    dismissed_at TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Catégorisation
    category TEXT,
    source TEXT,
    
    -- Données JSON
    actions_json TEXT CHECK (json_valid(actions_json)),
    metadata_json TEXT CHECK (json_valid(metadata_json)),
    
    -- Multi-utilisateur (futur)
    user_id INTEGER DEFAULT 1,
    
    -- Déduplication
    dedup_key TEXT,
    
    -- Statut
    is_read BOOLEAN DEFAULT 0,
    is_dismissed BOOLEAN DEFAULT 0,
    is_pinned BOOLEAN DEFAULT 0
);
```

### Indexes

| Index | Colonnes | Description |
|-------|----------|-------------|
| `idx_notifications_user_read` | `(user_id, is_read, created_at DESC)` | Récupération rapide des non-lues |
| `idx_notifications_type` | `(type, created_at DESC)` | Filtrage par type |
| `idx_notifications_category` | `(category, created_at DESC)` | Filtrage par catégorie |
| `idx_notifications_dedup` | `(dedup_key, created_at)` | Déduplication efficace |
| `idx_notifications_expires` | `(expires_at)` WHERE `expires_at IS NOT NULL` | Nettoyage des expirées |

### Tables associées

- **`notification_preferences`** - Préférences utilisateur (seuils, canaux, types activés)
- **`notification_history`** - Historique des envois pour déduplication

### Vues

- **`v_notifications_active`** - Notifications actives (non lues, non expirées) avec priorité
- **`v_notification_stats`** - Statistiques agrégées par utilisateur

---

## 🔄 Migration depuis V2

Ce module remplace l'ancien système de notifications V2 (`modules.ui.notifications`).

### Changements majeurs

| Aspect | V2 | V3 |
|--------|-----|-----|
| Module | `modules.ui.notifications` | `modules.notifications` |
| Manager | `NotificationManager` | `NotificationService` |
| Stockage | Fichier JSON `Data/notifications_v2.json` | SQLite (migration 007) |
| Typage | String libre | `NotificationType` enum |
| Déduplication | Basique | Clé + fenêtre temporelle |
| Préférences | Partielles | Table dédiée complète |

### Guide de migration

Voir la documentation complète : [`docs/MIGRATION_NOTIFICATIONS_V3.md`](../../docs/MIGRATION_NOTIFICATIONS_V3.md)

### Points d'attention

- ⚠️ Les notifications V2 **ne sont pas migrées automatiquement**
- ⚠️ Les préférences utilisateur doivent être **reconfigurées** dans la page Notifications V3
- ✅ Le wrapper V2 peut temporairement rediriger vers V3 pendant la transition

---

## 📝 Changelog

### v3.0.0 (2026-02-28)

- ✨ Création du système de notifications unifié V3
- ✨ Persistance SQLite avec migration 007
- ✨ 20+ types de notifications typés
- ✨ Système de déduplication avancé
- ✨ 6 détecteurs automatiques
- ✨ Préférences utilisateur granulaires
- ✨ Composants UI avec Design System
- ✨ Support expiration et épinglage
- ✨ Actions riches (navigate, dismiss, custom)
- ✨ Vues SQL pour statistiques et notifications actives

---

## 📚 Ressources

- **Migration V2→V3** : `docs/MIGRATION_NOTIFICATIONS_V3.md`
- **Migration SQL** : `migrations/007_notifications.sql`
- **Page de test** : `pages/13_Notifications_V3.py`
- **Design System** : `modules/ui/`

---

## 🤝 Contribution

Pour ajouter un nouveau type de notification :

1. Ajouter l'enum dans `models.py`
2. Ajouter l'icône par défaut dans `service.py`
3. Créer un helper dans `service.py` si pertinent
4. Documenter dans ce README

Pour ajouter un détecteur :

1. Créer une classe héritant de `NotificationDetector` dans `detectors.py`
2. Implémenter `name` (property) et `detect()` (méthode)
3. L'enregistrer dans `DetectorRegistry._register_default_detectors()`
