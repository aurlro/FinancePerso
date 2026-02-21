# Migration v5.2.0 - Archivage des modules legacy

## Résumé des changements

Cette migration archive tous les modules legacy et met à jour les imports vers les nouvelles versions.

## Fichiers archivés

Les fichiers suivants ont été déplacés vers `archive/legacy_v5/modules/`:

- `modules/data_manager.py` → Utiliser `modules.db.*` directement
- `modules/ai_manager.py` → Utiliser `modules.ai_manager_v2`
- `modules/update_manager.py` → Utiliser `modules.update`
- `modules/db/legacy_wrapper.py` → Utiliser `modules.db_v2.repositories.*`
- `modules/ui/config/` → Utiliser `modules.ui_v2.organisms.config`
- `modules/ui/dashboard/customizable_dashboard.py` → Utiliser `modules.ui_v2.templates.dashboard`
- `modules/ui/notifications/components.py` → Utiliser `modules.ui_v2.organisms.notifications`

## Mises à jour d'imports

### Avant → Après

```python
# AI Manager
from modules.ai_manager import get_ai_provider  # ❌
from modules.ai_manager_v2 import get_ai_provider  # ✅

# Data Manager
from modules.data_manager import get_all_transactions  # ❌
from modules.db.transactions import get_all_transactions  # ✅

from modules.data_manager import add_category  # ❌
from modules.db.categories import add_category  # ✅

from modules.data_manager import add_member  # ❌
from modules.db.members import add_member  # ✅

from modules.data_manager import add_learning_rule  # ❌
from modules.db.rules import add_learning_rule  # ✅

# Update Manager
from modules.update_manager import get_update_manager  # ❌
from modules.update import get_update_manager  # ✅

from modules.update_manager import UpdateManager  # ❌
from modules.update import UpdateManager  # ✅
```

## Modules mis à jour

Les fichiers suivants ont été mis à jour pour utiliser les nouveaux imports:

1. `modules/categorization.py`
2. `modules/ai/audit_engine.py`
3. `modules/ai/conversational_assistant.py`
4. `modules/ai/smart_tagger.py`
5. `modules/ui/importing/main.py`
6. `modules/ui_v2/molecules/components/quick_actions.py`
7. `modules/ui/components/quick_actions.py`
8. `modules/ui/assistant/config_tab.py`
9. `modules/ui/config/config_dashboard.py`
10. `modules/ui/validation/main.py`
11. `pages/3_Synthèse.py`
12. `pages/10_Nouveautés.py`
13. `scripts/audit_redux.py`
14. `modules/update/__init__.py` (ajout de `get_update_manager`)

## Tests

Les tests ont été mis à jour et passent tous:
```bash
pytest tests/db/test_members.py - PASSED
pytest tests/db/test_rules.py - PASSED
pytest tests/ai/test_anomaly_detector.py - PASSED
pytest tests/ai/test_rules_auditor.py - PASSED
```

## CI/CD

Les workflows GitHub Actions ont été ajoutés:
- `.github/workflows/ci.yml` - Tests, lint, sécurité
- `.github/workflows/release.yml` - Release automatique
- `Dockerfile` - Conteneurisation
- `docker-compose.yml` - Déploiement local
