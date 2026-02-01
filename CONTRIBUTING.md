# Guide de Contribution

Merci de votre intérêt pour contribuer à MyFinance Companion !

## 🚀 Workflow de développement

### 1. Configuration locale

```bash
# Cloner le repo
git clone <repository-url>
cd FinancePerso

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Installer les dépendances
pip install -r requirements.txt
pip install -r requirements-dev.txt  # outils de dev
```

### 2. Avant de commit

Les tests tournent automatiquement sur GitHub Actions, mais vous pouvez les lancer localement :

```bash
# Linter
ruff check modules/ app.py pages/

# Tests
pytest --cov=modules -v

# Ou tout en un (avant push)
./scripts/pre-push.sh  # si vous créez ce script
```

### 3. Créer une Pull Request

1. Créez une branche : `git checkout -b feature/ma-feature`
2. Committez vos changements : `git commit -am "Ajout de: ma feature"`
3. Push : `git push origin feature/ma-feature`
4. Créez une PR sur GitHub

La CI va automatiquement :
- ✅ Lancer les tests sur Python 3.11 et 3.12
- ✅ Vérifier le linting avec Ruff
- ✅ Générer le rapport de couverture

## 📝 Conventions de code

- **Black** : Formatage automatique (line-length: 100)
- **Ruff** : Linting et imports triés
- **Type hints** : Recommandé pour les fonctions publiques
- **Docstrings** : Google style

### Exemple

```python
def categorize_transaction(
    transaction: Transaction,
    rules: list[Rule] | None = None,
) -> Category:
    """Catégorise une transaction selon les règles existantes.
    
    Args:
        transaction: La transaction à catégoriser
        rules: Liste optionnelle de règles à appliquer
        
    Returns:
        La catégorie assignée
        
    Raises:
        ValueError: Si la transaction est invalide
    """
    ...
```

## 🧪 Écrire des tests

Les tests sont dans le dossier `tests/` avec la même structure que `modules/`.

```python
# tests/test_example.py
import pytest
from modules.example import ma_fonction

def test_ma_fonction():
    # Arrange
    input_data = "test"
    
    # Act
    result = ma_fonction(input_data)
    
    # Assert
    assert result == "expected"
```

Run : `pytest tests/test_example.py -v`

## 🔒 Sécurité

- **Jamais** de credentials dans le code
- Utilisez `.env` pour les variables sensibles
- Chiffrez les données sensibles avec `modules/encryption.py`

## 🐛 Signaler un bug

Ouvrez une issue avec :
- Description du problème
- Étapes pour reproduire
- Comportement attendu vs réel
- Screenshots si pertinent
- Logs d'erreur (sans données sensibles)

## 💡 Proposer une feature

Ouvrez une issue avec le label `enhancement` et décrivez :
- Le problème que ça résout
- La solution proposée
- Alternatives considérées

---

Merci ! 🎉
