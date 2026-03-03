# Guide d'amélioration UX - FinancePerso

> Ce guide explique comment utiliser les nouveaux composants de feedback pour améliorer l'expérience utilisateur.

---

## 🆕 Nouveaux composants disponibles

Le fichier `modules/ui/enhanced_feedback.py` fournit des composants améliorés pour le feedback utilisateur.

### 1. `with_feedback()` - Décorateur pour les actions

Wrapper automatique avec spinner et messages de confirmation :

```python
from modules.ui.enhanced_feedback import with_feedback, show_action_toast

@with_feedback(
    action_name="Import CSV",
    success_msg="✅ Fichier importé avec succès !",
    error_msg="❌ Erreur lors de l'import :"
)
def import_csv_file(file_path):
    """Importe un fichier CSV avec feedback automatique."""
    df = pd.read_csv(file_path)
    save_to_db(df)
    return df

# Utilisation
if st.button("📥 Importer"):
    import_csv_file(uploaded_file)
```

---

### 2. `loading_spinner()` - Context manager

Affiche un spinner avec temps d'exécution :

```python
from modules.ui.enhanced_feedback import loading_spinner

with loading_spinner("Chargement des transactions..."):
    df = load_transactions_from_db()
    # Le spinner s'affiche pendant l'exécution
    # Un message "⏱️ Opération terminée en X.XXs" apparaît après
```

---

### 3. `confirm_button()` - Bouton avec confirmation

Pour les actions destructrices (suppression, etc.) :

```python
from modules.ui.enhanced_feedback import confirm_button

confirm_button(
    label="🗑️ Supprimer toutes les données",
    confirmation_text="⚠️ Cette action est irréversible. Êtes-vous sûr ?",
    on_confirm=lambda: delete_all_data(),
    confirm_label="Oui, tout supprimer",
    cancel_label="Annuler"
)
```

---

### 4. `progress_with_status()` - Barre de progression

Pour les opérations longues avec beaucoup d'éléments :

```python
from modules.ui.enhanced_feedback import progress_with_status

items = get_items_to_process()
pbar, status, update = progress_with_status(len(items), "Traitement des transactions")

for i, item in enumerate(items):
    process_item(item)
    update(i + 1, f"Traitement de : {item['label'][:30]}...")

show_action_toast(f"{len(items)} éléments traités !", "success")
```

---

### 5. `logged_button()` - Bouton avec logging

Pour déboguer les problèmes de boutons qui ne répondent pas :

```python
from modules.ui.enhanced_feedback import logged_button, init_feedback_system

# Au début de votre page
init_feedback_system()

# Utilisation
if logged_button("💾 Sauvegarder", key="btn_save", type_="primary"):
    save_data()
    show_action_toast("Sauvegarde réussie !", "success")
```

Le log d'actions s'affiche dans la sidebar pour déboguer.

---

## 📋 Exemple d'intégration complète

```python
import streamlit as st
from modules.ui.enhanced_feedback import (
    with_feedback, loading_spinner, confirm_button,
    show_action_toast, logged_button, init_feedback_system
)

# Initialisation
init_feedback_system()

st.title("Ma Page avec Feedback Amélioré")

# Section Import
st.subheader("Import de données")

uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")

if uploaded_file is not None:
    if logged_button("📥 Lancer l'import", key="btn_import", type_="primary"):
        try:
            with loading_spinner("Analyse du fichier..."):
                df = pd.read_csv(uploaded_file)
                
            # Traitement avec feedback
            @with_feedback("Import", f"✅ {len(df)} lignes importées !")
            def process_import():
                save_transactions(df)
            
            process_import()
            
        except Exception as e:
            show_action_toast(f"Erreur : {str(e)}", "error")

# Section Danger
st.subheader("Zone de danger")

confirm_button(
    label="🗑️ Supprimer toutes les transactions",
    confirmation_text="⚠️ **ATTENTION** : Cette action supprimera définitivement toutes vos transactions !",
    on_confirm=lambda: (
        delete_all_transactions(),
        show_action_toast("Toutes les transactions ont été supprimées", "warning")
    ),
    confirm_label="Oui, tout supprimer 🗑️",
    cancel_label="❌ Annuler"
)
```

---

## 🎯 Points d'amélioration prioritaires dans votre application

Basé sur l'audit, voici où appliquer ces améliorations :

| Fichier | Problème | Solution recommandée |
|---------|----------|---------------------|
| `pages/1_Import.py` | Pas de feedback sur l'import | `with_feedback()` + `progress_with_status()` |
| `pages/2_Validation.py` | Actions sans confirmation | `confirm_button()` pour les suppressions |
| `pages/4_Recurrence.py` | Calculs longs sans spinner | `loading_spinner()` |
| `modules/db/*` | Opérations batch lentes | `progress_with_status()` |

---

## 🔧 Installation

1. Le fichier `modules/ui/enhanced_feedback.py` est déjà créé
2. Importez les fonctions nécessaires dans vos pages :
   ```python
   from modules.ui.enhanced_feedback import (
       with_feedback, loading_spinner, confirm_button,
       show_action_toast, logged_button, init_feedback_system
   )
   ```
3. Appelez `init_feedback_system()` au début de chaque page pour activer le log

---

*Document créé lors de l'audit UX du 2026-02-01*
