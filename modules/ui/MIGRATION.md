# Plan de Migration - Design System V2

> Guide de migration depuis l'ancien code UI vers le nouveau Design System

---

## 🎯 Objectif

Migrer progressivement tout le code UI vers le nouveau Design System Atomic :
- **Tokens** : Couleurs, typographie, espacements unifiés
- **Atomes** : Composants de base réutilisables
- **Molécules** : Compositions type `Card`, `EmptyState`
- **Feedback V2** : Système de feedback modernisé

---

## 📊 État actuel

| Domaine | Fichiers | Statut | Priorité |
|---------|----------|--------|----------|
| Tokens | ✅ Créés | ✅ Prêt | P0 |
| Atomes | ✅ Créés | ✅ Prêt | P0 |
| Molécules | ✅ Créés | ✅ Prêt | P0 |
| Feedback | ✅ V2 créé | 🔄 Migration | P1 |
| Dashboard | ⏳ À migrer | ⏳ En attente | P2 |
| Validation | ⏳ À migrer | ⏳ En attente | P2 |
| Assistant | ⏳ À migrer | ⏳ En attente | P3 |
| Config | ⏳ À migrer | ⏳ En attente | P3 |

---

## 🔄 Étapes de migration

### Phase 1 : Fondation (Cette semaine)

#### 1.1 Créer les fichiers de base ✅

```bash
# Créer la structure
mkdir -p modules/ui/{tokens,atoms,molecules,organisms,templates}

# Les fichiers suivants ont été créés:
# - modules/ui/tokens/__init__.py
# - modules/ui/tokens/colors.py
# - modules/ui/tokens/typography.py
# - modules/ui/tokens/spacing.py
# - modules/ui/tokens/radius.py
# - modules/ui/atoms/__init__.py
# - modules/ui/atoms/button.py
# - modules/ui/atoms/badge.py
# - modules/ui/atoms/icon.py
# - modules/ui/molecules/__init__.py
# - modules/ui/molecules/card.py
# - modules/ui/molecules/empty_state.py
# - modules/ui/molecules/metric.py
# - modules/ui/organisms/__init__.py
# - modules/ui/templates/__init__.py
# - modules/ui/templates/page_layout.py
# - modules/ui/feedback_v2.py
```

#### 1.2 Mettre à jour `modules/ui/__init__.py` ✅

Le fichier `__init__.py` principal a été mis à jour pour exposer :
- Les nouveaux composants
- La compatibilité avec l'ancien feedback

---

### Phase 2 : Migration Feedback (Semaine prochaine)

#### 2.1 Remplacer les imports

**Avant:**
```python
from modules.ui.feedback import toast_success, show_warning
```

**Après:**
```python
from modules.ui import Feedback
# ou
from modules.ui.feedback_v2 import Feedback, Toast, Banner
```

#### 2.2 Remplacer les appels

**Avant:**
```python
toast_success("Sauvegardé !")
show_warning("Attention", "Message...")
```

**Après:**
```python
Feedback.toast.success("Sauvegardé !")
Feedback.banner.warning("Attention", "Message...")
```

#### 2.3 Fichiers à modifier

| Fichier | Lignes concernées | Action |
|---------|-------------------|--------|
| `modules/ui/feedback.py` | Tout | Garder pour compatibilité, marquer @deprecated |
| `pages/*.py` | Import feedback | Migrer vers Feedback V2 |
| `modules/ui/components/*.py` | Toast/Banner | Migrer vers Feedback V2 |

---

### Phase 3 : Migration Cartes (2-3 semaines)

#### 3.1 Identifier les fonctions de cartes

```bash
# Chercher toutes les fonctions de cartes
grep -rn "def.*card\|def render.*card" modules/ pages/ --include="*.py"
```

#### 3.2 Remplacer par `Card`

**Avant:**
```python
def render_kpi_card(title, value, trend):
    st.markdown(f"""
    <div style="border: 1px solid #e2e8f0; padding: 16px;">
        <h4>{title}</h4>
        <p style="font-size: 24px;">{value}</p>
    </div>
    """, unsafe_allow_html=True)

render_kpi_card("Total", "1000 €", "+5%")
```

**Après:**
```python
from modules.ui.molecules import Card

Card.metric(
    title="Total",
    value="1000 €",
    trend="+5%",
    trend_up=True
)
```

#### 3.3 Fichiers prioritaires

1. `modules/ui/dashboard/kpi_cards.py` → Utiliser `Card.metric()`
2. `modules/ui/components/empty_states.py` → Utiliser `EmptyState`
3. `modules/ui/assistant/components.py` → Utiliser `Card` pour les cartes IA
4. `modules/ui/notifications/center.py` → Utiliser `Card.alert()`

---

### Phase 4 : Migration Couleurs (3-4 semaines)

#### 4.1 Audit des couleurs hardcodées

```bash
# Lister toutes les couleurs hex
grep -rn "#[0-9A-Fa-f]\{6\}" modules/ pages/ --include="*.py" | grep -v "tokens/colors.py"
```

#### 4.2 Remplacement systématique

**Avant:**
```python
st.markdown("<div style='color: #22c55e;'>...</div>", unsafe_allow_html=True)
```

**Après:**
```python
from modules.ui.tokens import Colors
st.markdown(f"<div style='color: {Colors.SUCCESS};'>...</div>", unsafe_allow_html=True)
```

#### 4.3 Mapping des couleurs courantes

| Ancien | Nouveau |
|--------|---------|
| `#22c55e` | `Colors.SUCCESS` |
| `#ef4444` | `Colors.DANGER` |
| `#f59e0b` | `Colors.WARNING` |
| `#3b82f6` | `Colors.INFO` |
| `#0f172a` | `Colors.PRIMARY` |
| `#64748b` | `Colors.SLATE_500` |
| `#f8fafc` | `Colors.SLATE_50` |
| `#e2e8f0` | `Colors.SLATE_200` |

---

### Phase 5 : Migration Typographie (4-5 semaines)

#### 5.1 Remplacer les tailles hardcodées

**Avant:**
```python
st.markdown("<span style='font-size: 14px;'>...</span>", unsafe_allow_html=True)
```

**Après:**
```python
from modules.ui.tokens import Typography
st.markdown(f"<span style='font-size: {Typography.SIZE_SM};'>...</span>", unsafe_allow_html=True)
```

#### 5.2 Mapping des tailles

| Pixels | Rem | Token |
|--------|-----|-------|
| 12px | 0.75rem | `Typography.SIZE_XS` |
| 14px | 0.875rem | `Typography.SIZE_SM` |
| 16px | 1rem | `Typography.SIZE_BASE` |
| 18px | 1.125rem | `Typography.SIZE_LG` |
| 20px | 1.25rem | `Typography.SIZE_XL` |
| 24px | 1.5rem | `Typography.SIZE_2XL` |

---

### Phase 6 : Structure Atomic Design (5-6 semaines)

#### 6.1 Organiser les composants existants

Déplacer les composants existants vers la structure atomic :

```
modules/ui/
├── atoms/
│   ├── button.py ✅
│   ├── badge.py ✅
│   ├── icon.py ✅
│   ├── input.py (À créer)
│   └── select.py (À créer)
├── molecules/
│   ├── card.py ✅
│   ├── empty_state.py ✅
│   ├── metric.py ✅
│   ├── chip_selector.py (À déplacer depuis components/)
│   └── avatar_selector.py (À déplacer depuis components/)
├── organisms/
│   ├── header.py (À créer)
│   ├── sidebar.py (À créer)
│   ├── transaction_list.py (À créer)
│   └── dashboard_section.py (À créer)
```

---

## 📋 Checklist de migration par fichier

Pour chaque fichier migré, vérifier :

- [ ] Imports : Utilise les nouveaux tokens et composants
- [ ] Couleurs : Aucune couleur hardcodée
- [ ] Typographie : Aucune taille hardcodée
- [ ] Espacements : Aucun padding/margin hardcodé
- [ ] Boutons : Utilise `Button` (pas `st.button`)
- [ ] Cartes : Utilise `Card` (pas HTML custom)
- [ ] Badges : Utilise `Badge` (pas HTML custom)
- [ ] États vides : Utilise `EmptyState`
- [ ] Feedback : Utilise `Feedback` V2
- [ ] Tests : Les tests passent toujours

---

## 🚀 Commandes utiles

### Audit

```bash
# Compter les couleurs hardcodées
grep -rn "#[0-9A-Fa-f]\{6\}" modules/ pages/ --include="*.py" | wc -l

# Lister les fichiers avec couleurs hardcodées
grep -rln "#[0-9A-Fa-f]\{6\}" modules/ pages/ --include="*.py"

# Chercher les st.button directs
grep -rn "st\.button" modules/ui --include="*.py" | grep -v "Button\."

# Chercher les st.markdown avec style
grep -rn "st\.markdown.*style" modules/ --include="*.py"
```

### Vérification

```bash
# Tests essentiels
make test

# Linting
make lint

# Vérification complète
make check
```

---

## 📊 Suivi de progression

| Phase | Progression | Fichiers migrés | Fichiers restants |
|-------|-------------|-----------------|-------------------|
| 1 - Fondation | 100% | 15 | 0 |
| 2 - Feedback | 0% | 1 | ~15 |
| 3 - Cartes | 0% | 1 | ~20 |
| 4 - Couleurs | 0% | 1 | ~70 |
| 5 - Typographie | 0% | 1 | ~50 |
| 6 - Structure | 0% | 0 | ~30 |

**Total estimé : ~150 fichiers à migrer**

---

## 💡 Conseils

1. **Migrer par domaine** : Commencer par un module complet (ex: dashboard)
2. **Tests fréquents** : Lancer `make test` après chaque fichier
3. **Pas de rush** : La migration peut se faire progressivement sur plusieurs semaines
4. **Documentation** : Mettre à jour ce fichier avec les progrès
5. **Revue de code** : Faire relire les migrations importantes

---

## 📞 Support

En cas de questions :
1. Consulter `DESIGN_SYSTEM_GUIDE.md`
2. Regarder les exemples dans `modules/ui/atoms/`, `molecules/`
3. Vérifier la documentation des tokens

---

*Document créé le 2026-02-27*
*Dernière mise à jour : 2026-02-27*
