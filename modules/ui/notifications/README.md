# 🔔 Système de Notifications FinancePerso v2

Un système de notifications moderne, cohérent et personnalisable pour FinancePerso.

## ✨ Caractéristiques

- **🎯 Hiérarchie claire** : 6 niveaux de priorité (Critical → Loading)
- **🎨 Design cohérent** : Styles et couleurs unifiés
- **⚙️ Personnalisable** : Préférences utilisateur complètes
- **📱 Responsive** : Adapté mobile et desktop
- **🔔 Notification Center** : Historique et gestion centralisée
- **⚡ Non-intrusif** : Auto-dismiss avec progression visuelle

## 🚀 Démarrage rapide

### 1. Initialisation (app.py)

```python
from modules.ui.notifications import init_notification_system, render_notifications_auto

# Au démarrage
init_notification_system()

# Dans chaque page
render_notifications_auto()
```

### 2. Utilisation basique

```python
from modules.ui.notifications import success, warning, error, info, achievement

# Succès
success("Transaction enregistrée !")

# Avertissement
warning("Budget à 90% atteint", title="Attention")

# Erreur (persistante par défaut)
error("Échec de la sauvegarde", persistent=True)

# Info
info("Nouvelle fonctionnalité disponible")

# Achievement
achievement("Premier import !", description="Vous avez importé vos premières transactions")
```

### 3. Avec actions

```python
from modules.ui.notifications import NotificationAction, info

info(
    "3 transactions en attente de validation",
    actions=[
        NotificationAction(
            label="Valider",
            callback=lambda: st.switch_page("pages/2_Validation.py"),
            primary=True
        ),
        NotificationAction(
            label="Ignorer",
            callback=lambda: None
        )
    ]
)
```

## 📊 Types de notifications

| Niveau | Icône | Durée | Usage |
|--------|-------|-------|-------|
| **Critical** | 🚨 | Persistant | Erreurs bloquantes, perte de données |
| **Warning** | ⚠️ | 10s | Alertes importantes, confirmations |
| **Success** | ✅ | 3s | Confirmations d'actions |
| **Info** | ℹ️ | 5s | Informations contextuelles |
| **Achievement** | 🏆 | 5s | Gamification, milestones |
| **Loading** | 🔄 | Variable | Opérations en cours |

## 🎨 Composants disponibles

### Notification Center

```python
from modules.ui.notifications import (
    render_notification_center_compact,  # Badge sidebar
    render_notification_center_full,      # Page complète
    render_notification_settings          # Configuration
)

# Dans la sidebar
render_notification_center_compact()

# Page dédiée
render_notification_center_full()

# Paramètres
render_notification_settings()
```

### Notifications inline

```python
from modules.ui.notifications import render_inline_notification

render_inline_notification(
    message="Veuillez vérifier vos données",
    level=NotificationLevel.WARNING,
    actions=[
        NotificationAction(label="Vérifier", callback=verify_data)
    ],
    dismissible=True
)
```

### États spéciaux

```python
from modules.ui.notifications import (
    render_achievement_unlock,
    render_loading_state,
    render_empty_state
)

# Achievement avec animation
render_achievement_unlock(
    title="Expert Budget",
    description="Vous avez géré votre budget pendant 3 mois",
    icon="🏆",
    reward="+100 points"
)

# Loading avec progression
render_loading_state(
    message="Import en cours...",
    submessage="Traitement de 150 transactions",
    progress=0.6
)

# État vide engageant
render_empty_state(
    icon="📊",
    title="Aucune donnée",
    description="Importez votre premier relevé pour commencer",
    action_label="Importer",
    action_callback=lambda: st.switch_page("pages/1_Import.py")
)
```

### Confirmation

```python
from modules.ui.notifications import show_confirmation

show_confirmation(
    title="Supprimer cette transaction ?",
    message="Cette action est irréversible.",
    on_confirm=delete_transaction,
    on_cancel=lambda: None,
    confirm_label="Oui, supprimer",
    cancel_label="Annuler",
    danger=True
)
```

## ⚙️ Configuration

### Préférences utilisateur

```python
from modules.ui.notifications import get_notification_manager

manager = get_notification_manager()
manager.update_preferences(
    enabled=True,
    max_visible=3,
    show_success=True,
    show_info=False,  # Désactiver les infos
    custom_durations={
        'success': 5.0,
        'warning': 15.0
    }
)
```

### Types disponibles

```python
class NotificationLevel:
    CRITICAL    # Erreurs bloquantes
    WARNING     # Alertes
    SUCCESS     # Confirmations
    INFO        # Informations
    ACHIEVEMENT # Gamification
    LOADING     # Chargement
```

## 📱 Intégration dans les pages

### Template standard

```python
import streamlit as st
from modules.ui.notifications import render_notifications_auto, success

st.set_page_config(page_title="Ma Page", page_icon="📊")

# 1. Rendre les notifications en attente
render_notifications_auto()

# 2. Contenu de la page
st.title("Ma Page")

# 3. Actions avec feedback
if st.button("Sauvegarder"):
    save_data()
    success("Données sauvegardées !")
    st.rerun()
```

## 🔄 Migration depuis l'ancien système

### Avant (ancien système)

```python
import streamlit as st
from modules.ui.feedback import toast_success, show_error

# Toast
toast_success("Opération réussie")

# Banner persistant
show_error("Une erreur est survenue")
```

### Après (nouveau système)

```python
from modules.ui.notifications import success, error

# Toast auto
success("Opération réussie")

# Persistant
error("Une erreur est survenue", persistent=True)
```

## 🎯 Bonnes pratiques

### 1. Choisir le bon niveau

- **Critical** : Uniquement pour les erreurs bloquantes
- **Warning** : Situations nécessitant attention
- **Success** : Confirmations d'actions réussies
- **Info** : Informations contextuelles discrètes
- **Achievement** : Gamification uniquement

### 2. Messages clairs

```python
# ✅ Bon
success("12 transactions importées avec succès")

# ❌ Éviter
success("OK")
success("Opération terminée")
```

### 3. Timing approprié

```python
# ✅ Actions importantes → Toast + Log
success("Budget créé")

# ✅ Erreurs → Persistant
error("Échec de connexion", persistent=True)

# ✅ Feedbacks fréquents → Court
info("Auto-sauvegarde...", duration=2)
```

### 4. Actions contextuelles

```python
# ✅ Proposer une action
warning(
    "Budget dépassé de 15%",
    actions=[
        NotificationAction(
            label="Voir le budget",
            callback=show_budget_details,
            primary=True
        )
    ]
)
```

## 🧪 Tests

```python
from modules.ui.notifications import (
    success, warning, error, info, achievement,
    render_notification_center_full
)

# Page de test
st.title("Test Notifications")

if st.button("Test Success"):
    success("Ceci est un test de succès !")

if st.button("Test Warning"):
    warning("Ceci est un test d'avertissement")

if st.button("Test Error"):
    error("Ceci est un test d'erreur", persistent=True)

if st.button("Test Achievement"):
    achievement("Test débloqué !")

# Centre de notifications
render_notification_center_full()
```

## 📚 API Complète

### Fonctions principales

| Fonction | Description |
|----------|-------------|
| `notify(message, level, **kwargs)` | Crée une notification générique |
| `success(message, **kwargs)` | Notification de succès |
| `warning(message, **kwargs)` | Notification d'avertissement |
| `error(message, **kwargs)` | Notification d'erreur |
| `info(message, **kwargs)` | Notification informative |
| `achievement(message, **kwargs)` | Notification d'achievement |
| `loading(message, **kwargs)` | Notification de chargement |

### Composants UI

| Composant | Description |
|-----------|-------------|
| `render_notifications_auto()` | Affiche les notifications en attente |
| `render_notification_center_compact()` | Badge pour la sidebar |
| `render_notification_center_full()` | Page historique complète |
| `render_notification_settings()` | Configuration utilisateur |
| `render_inline_notification()` | Notification dans le flux |
| `render_achievement_unlock()` | Célébration achievement |
| `render_loading_state()` | État de chargement |
| `render_empty_state()` | État vide |
| `show_confirmation()` | Boîte de confirmation |

### Classes

| Classe | Description |
|--------|-------------|
| `Notification` | Représentation d'une notification |
| `NotificationLevel` | Enum des niveaux |
| `NotificationAction` | Action associée |
| `NotificationManager` | Gestionnaire singleton |
| `NotificationPreferences` | Préférences utilisateur |

---

**Version** : 2.0.0  
**Auteur** : FinancePerso Team  
**Date** : 2026
