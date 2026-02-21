# 🔧 Guide : Maintenance du Dashboard

## Vue d'ensemble

Le système de **Dashboard Cleanup** permet de détecter et réparer automatiquement les problèmes avec les widgets du tableau de bord personnalisable.

---

## 🚀 Lancement Automatique

### Au démarrage de l'application
Le nettoyage s'exécute **automatiquement** à chaque démarrage d'app.py :

```python
# Dans app.py
try:
    from modules.db.dashboard_cleanup import run_startup_cleanup
    cleanup_result = run_startup_cleanup()
    if cleanup_result.widgets_fixed > 0:
        logger.info(f"Dashboard auto-cleanup: {cleanup_result.message}")
except Exception as e:
    logger.warning(f"Dashboard cleanup failed: {e}")
```

**Comportement** :
- Mode silencieux (pas d'interface utilisateur)
- Répare uniquement les problèmes détectés
- Continue même en cas d'erreur (non-critique)

---

## 🎮 Utilisation Manuelle

### 1. Via l'Interface (Configuration)

Aller dans **Configuration → Vue d'ensemble → Maintenance du Dashboard**

Trois boutons disponibles :

| Bouton | Action | Quand l'utiliser |
|--------|--------|------------------|
| 🔍 **Vérifier** | Analyse sans modifier | Suspicion de problème |
| 🔧 **Réparer** | Correction automatique | Erreurs détectées |
| 🔄 **Reset** | Supprime tout et recrée | Dashboard complètement cassé |

### 2. Via le Script en Ligne de Commande

```bash
cd /Users/aurelien/Documents/Projets/FinancePerso

# Vérification uniquement
python scripts/fix_dashboard_layouts.py validate

# Réparation automatique (défaut)
python scripts/fix_dashboard_layouts.py repair

# Nettoyage des widgets corrompus
python scripts/fix_dashboard_layouts.py clean

# Reset complet
python scripts/fix_dashboard_layouts.py reset
```

### 3. Via Python (Programmatique)

```python
from modules.db.dashboard_cleanup import (
    DashboardCleanupManager,
    CleanupScenario,
    run_startup_cleanup,
    reset_dashboard
)

# Méthode 1 : Scénario simple
result = run_startup_cleanup()
print(f"Fixed: {result.widgets_fixed}, Removed: {result.widgets_removed}")

# Méthode 2 : Scénario spécifique
manager = DashboardCleanupManager()
result = manager.run_cleanup(CleanupScenario.AUTO_REPAIR)

# Méthode 3 : Reset complet
result = reset_dashboard()
```

---

## 📋 Scénarios Disponibles

### `AUTO_REPAIR` (Défaut)
- Détecte les widgets corrompus
- Tente de les réparer (conversion Enum → string, etc.)
- Supprime ceux qui ne peuvent pas être réparés
- **Usage** : Cas général

### `VALIDATE_ONLY`
- Analyse sans modifier
- Liste tous les problèmes
- **Usage** : Diagnostic avant réparation

### `CLEAN_CORRUPTED`
- Supprime uniquement les widgets corrompus
- Garde les widgets valides
- **Usage** : Nettoyage sélectif

### `RESET_DEFAULT`
- Supprime **tous** les layouts personnalisés
- Recrée le layout par défaut
- **Usage** : Dernier recours

---

## 🔍 Types de Problèmes Détectés

### 1. WidgetType comme Enum au lieu de String
**Problème** : `{"type": <WidgetType.KPI_DEPENSES: 'kpi_depenses'>}`  
**Solution** : Conversion en `"kpi_depenses"`

### 2. Type de widget inconnu
**Problème** : `{"type": "unknown_widget"}`  
**Solution** : Mapping vers un type valide ou suppression

### 3. Champs manquants
**Problème** : `{"id": "widget_1"}` (manque type, title, etc.)  
**Solution** : Ajout des valeurs par défaut

### 4. JSON corrompu
**Problème** : Données illisibles en base  
**Solution** : Suppression du layout corrompu

---

## 📊 Exemple de Résultat

```python
CleanupResult(
    scenario=CleanupScenario.AUTO_REPAIR,
    success=True,
    widgets_checked=12,
    widgets_fixed=3,
    widgets_removed=1,
    errors=[
        "Widget supprimé (layout 1): type invalide 'unknown'",
    ],
    message="Réparation terminée: 3 widget(s) corrigé(s), 1 supprimé(s)"
)
```

---

## 🛡️ Sécurité

### Avant toute modification
- Les données sont **toujours** lues avant modification
- En cas d'erreur, l'opération est annulée
- Les logs enregistrent toutes les actions

### Rollback manuel
Si un problème survient après nettoyage :
```python
# Restaurer le layout par défaut
from modules.db.dashboard_cleanup import reset_dashboard
reset_dashboard()
```

---

## 📁 Fichiers Concernés

| Fichier | Rôle |
|---------|------|
| `modules/db/dashboard_cleanup.py` | Logique de nettoyage |
| `scripts/fix_dashboard_layouts.py` | Script CLI |
| `modules/ui/config/config_dashboard.py` | Interface Configuration |
| `app.py` | Intégration au démarrage |

---

## 🐛 Dépannage

### "Aucun widget ne s'affiche"
```bash
python scripts/fix_dashboard_layouts.py reset
```

### "Erreur WidgetType persiste"
```python
# Dans Python
from modules.db.connection import get_db_connection
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS dashboard_layouts")
    conn.commit()
```

### "Le cleanup ne résout pas le problème"
1. Vérifier les logs : `logs/app.log`
2. Lancer en mode validate : `python scripts/fix_dashboard_layouts.py validate`
3. Contacter le support avec les erreurs affichées

---

## 🔮 Évolutions Futures

- [ ] Sauvegarde automatique avant nettoyage
- [ ] Restauration d'une version précédente
- [ ] Export/Import des layouts
- [ ] Détection proactive des problèmes

---

## 📞 Support

En cas de problème persistant :
1. Lancer `python scripts/fix_dashboard_layouts.py validate`
2. Copier les erreurs affichées
3. Vérifier les logs dans `logs/`
4. Ouvrir une issue avec les détails
