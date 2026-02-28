# 🔧 Corrections Immédiates - Fichiers à Modifier

Ce document liste les corrections exactes à apporter page par page.

---

## 1. 6_Explorer.py

### Problèmes
- ❌ Pas de st.title()
- ❌ Pas de init_db()
- ❌ Pas de render_scroll_to_top()
- ❌ Pas de render_app_info()

### Corrections

```python
# AJOUTER après la ligne 13 (après les imports) :
from modules.db.migrations import init_db
from modules.ui.layout import render_app_info
from modules.ui import render_scroll_to_top

# MODIFIER la ligne 24 (après load_css()) :
load_css()
init_db()  # AJOUTER CETTE LIGNE

# AJOUTER à la fin du fichier (après render_explorer_page) :
render_scroll_to_top()
render_app_info()
```

### Fichier corrigé complet :
```python
"""
🔍 Explorateur - Exploration de catégories et tags avec filtres avancés.
"""
import streamlit as st
from modules.db.migrations import init_db
from modules.ui import load_css, render_scroll_to_top
from modules.ui.layout import render_app_info
from modules.ui.explorer import render_explorer_page

st.set_page_config(
    page_title="Explorateur",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()
init_db()

# ... reste du code inchangé ...

render_explorer_page(...)

render_scroll_to_top()
render_app_info()
```

---

## 2. 98_Tests.py

### Problèmes
- ❌ Pas de load_css()
- ❌ Pas de init_db()
- ❌ Pas de render_app_info()

### Corrections

```python
# AJOUTER aux imports :
from modules.db.migrations import init_db
from modules.ui import load_css
from modules.ui.layout import render_app_info

# AJOUTER après st.set_page_config() :
load_css()
init_db()

# AJOUTER avant render_scroll_to_top() :
render_app_info()
```

---

## 3. 1_Import.py

### Problème
- ⚠️ Layout default au lieu de wide

### Correction

```python
# MODIFIER la ligne 10 :
st.set_page_config(page_title="Import", page_icon="📥", layout="wide")
```

---

## 4. 3_Synthese.py

### Problème
- ⚠️ st.title() dans def main() au lieu du niveau module

### Correction (optionnelle - moins critique)

Déplacer le titre au début du fichier pour qu'il soit visible immédiatement :

```python
# AJOUTER après init_db() :
st.title("📊 Tableau de bord")

# DANS main(), REMPLACER st.title() par un sous-titre optionnel :
def main():
    st.markdown("### Vue d'ensemble de vos finances")
```

---

## 5. 10_Nouveautés.py

### Problème
- ❌ Pas d'init_db() (pour cohérence, même si pas utilisé)

### Correction

```python
# AJOUTER aux imports :
from modules.db.migrations import init_db

# AJOUTER après load_css() :
init_db()
```

---

## 6. 4_Regles.py

### Problème
- ⚠️ Titre incohérent avec page_title

### Correction

```python
# MODIFIER la ligne 52 :
st.title("🧠 Règles & Mémoire de l'assistant")
```

---

## 📋 Résumé des modifications

| Fichier | Lignes à ajouter | Lignes à modifier | Priorité |
|---------|-----------------|-------------------|----------|
| 6_Explorer.py | 4 | 0 | 🔴 Critique |
| 98_Tests.py | 3 | 0 | 🔴 Critique |
| 1_Import.py | 0 | 1 | 🟡 Moyenne |
| 3_Synthese.py | 0 | 1 | 🟢 Faible |
| 10_Nouveautés.py | 1 | 0 | 🟢 Faible |
| 4_Regles.py | 0 | 1 | 🟢 Faible |

---

## ✅ Checklist de vérification post-correction

Après chaque correction, vérifier :
- [ ] La page se charge sans erreur
- [ ] Le titre s'affiche correctement
- [ ] Le style est cohérent avec les autres pages
- [ ] Le bouton "scroll to top" apparaît après scroll
- [ ] L'info app version est visible en bas

---

## 🚀 Commande de validation

```bash
cd /Users/aurelien/Documents/Projets/FinancePerso
python -m py_compile pages/6_Explorer.py
python -m py_compile pages/98_Tests.py
python -m py_compile pages/1_Import.py
echo "✅ Syntaxe OK"
```
