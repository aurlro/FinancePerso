# 🔧 Correction : Erreur WidgetType

## Problème
```
ValueError: <WidgetType.KPI_DEPENSES: 'kpi_depenses'> is not a valid WidgetType
```

## Cause
Les données du dashboard personnalisable stockées en base contiennent des types de widgets qui ne sont pas reconnus par l'enum `WidgetType`.

## Solution Appliquée

### Modification dans `customizable_dashboard.py`

La méthode `from_dict` gère maintenant les valeurs inconnues :

```python
@classmethod
def from_dict(cls, data: Dict) -> 'DashboardWidget':
    """Crée un widget depuis un dictionnaire."""
    type_val = data.get('type', 'kpi_depenses')
    
    if isinstance(type_val, WidgetType):
        widget_type = type_val
    else:
        try:
            widget_type = WidgetType(type_val)
        except ValueError:
            # Type inconnu → utiliser valeur par défaut
            logger.warning(f"Unknown widget type '{type_val}', using default")
            widget_type = WidgetType.KPI_DEPENSES
    
    return cls(...)
```

## Si le problème persiste

### Option 1 : Réinitialiser le dashboard
Aller dans **Configuration → Dashboard** et cliquer sur "Réinitialiser la mise en page".

### Option 2 : Supprimer les layouts en base
Exécuter dans la console Python :
```python
from modules.db.dashboard_layouts import delete_layout
# Supprimer tous les layouts personnalisés
delete_layout('custom')
```

### Option 3 : Vider le cache Streamlit
```bash
# Arrêter Streamlit
rm -rf .streamlit/cache/*
# Relancer
streamlit run app.py
```

## Vérification
Après correction, le dashboard devrait charger avec les widgets par défaut.
