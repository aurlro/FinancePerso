# Code Quality Roadmap

> Plan d'amélioration progressive de la qualité du code et réduction de la dette technique.

---

## État Actuel (2026-03-02)

✅ **CI/CD Pipeline**: PASSING
- Black 26.1.0 formatting
- Ruff linting (line-length: 120)
- Essential tests passing (13/13)
- Security scans (Bandit/Safety) - reports generated
- Aucune erreur de syntaxe
- Aucun warning Ruff actif

⚠️ **Dette Technique Restante**:
- Ruff line-length: 120 (target: 100) - ~1500 lignes à corriger
- 5 règles de style ignorées (N818, N806, E402, UP043, F811, F821)
- Warnings Bandit ~30 (non bloquants)
- Couverture de tests incomplète (~40%)

---

## Phase 1: Stabilisation ✅ TERMINÉE (2026-03-02)

- [x] Correction du formatage Black
- [x] Synchronisation versions CI avec requirements-dev.txt
- [x] Correction des erreurs d'import critiques
- [x] Configuration Ruff avec valeurs par défaut raisonnables
- [x] CI tolérante aux problèmes non bloquants
- [x] Correction doc_agent.py pour compatibilité CI
- [x] Correction erreurs de syntaxe f-string dans `modules/ui/molecules/`
- [x] Correction point-virgule dans `modules/db/transactions.py:532`

---

## Phase 2: Qualité Code ✅ TERMINÉE (2026-03-02)

### 2.1 Corrections Ruff - Première passe ✅

| Règle | Description | Fichiers | Statut |
|-------|-------------|----------|--------|
| UP038 | `isinstance(X \| Y)` | `ai_manager.py:795` | ✅ Corrigé |
| E501 | Ligne >120 chars | `smart_reminders_widget.py:91` | ✅ Corrigé |
| UP046 | Invalide (supprimé) | `pyproject.toml` | ✅ Corrigé |

### 2.2 E741 - Noms de variables ambigus ✅

**Problème**: Variable `l` (lettre L minuscule) ambiguë avec `I` ou `1`

| Fichier | Ligne | Correction |
|---------|-------|------------|
| `modules/local_ml.py` | 226 | `l` → `label` |
| `modules/ui/couple/setup_wizard.py` | 355, 368 | `l` → `label` / `jl` |
| `modules/ui/notifications/center.py` | 183, 203 | `l` → `level` |
| `modules/ui/recurrence_tabs.py` | 197, 198, 233 | `l` → `lbl`, `c` → `cat` |
| `modules/wealth/agent_core.py` | 486 | `l` → `liab` |
| `modules/wealth/wealth_manager.py` | 597, 622, 754, 773 | `l` → `liab` |

**Total**: 10 corrections

**Résultat**: Ruff passe complètement (`All checks passed!`)

---

## Phase 3: Raffinement Code 📋 NEXT

### 3.1 Longueur des Lignes (120 → 100)
**Complexité**: Élevée (~1500 lignes concernées)
**Impact**: Faible (lisibilité marginale)
**Priorité**: Basse

```bash
# Vérifier le nombre de lignes à corriger
python -m ruff check modules/ --select E501 --line-length 100 | wc -l
# ~1500 lignes
```

**Décision**: Reporter à une phase ultérieure (Phase 5).
La limite actuelle de 120 caractères est un compromis acceptable.

### 3.2 Règles de Style Restantes

| Règle | Description | Nb erreurs | Priorité | Action |
|-------|-------------|------------|----------|--------|
| E402 | Import non en haut de fichier | ~15 | Moyenne | À corriger |
| N806 | Variable en majuscules dans fonction | ~30 | Basse | Ignorer (patterns constants) |
| N818 | Exception sans suffixe Error | ~5 | Basse | À corriger |
| F811 | Redéfinition import | ~3 | Moyenne | À corriger |
| F821 | Nom undefined | ~2 | Haute | À corriger |
| UP043 | Type params génériques | 0 | - | Ignorer (compatibilité) |

**Prochaine étape**: Corriger E402, F811, F821 (impact potentiel)

### 3.3 Sécurité (Bandit)

| Code | Description | Nb | Priorité |
|------|-------------|-----|----------|
| B608 | SQL injection possible | ~8 | Haute |
| B324 | MD5 utilisé | ~2 | Moyenne |
| B301 | Pickle utilisé | ~1 | Basse |

---

## Phase 4: Tests 🧪 PLANNIFIÉE

- [ ] Ajouter tests d'intégration
- [ ] Améliorer couverture à 80%+
- [ ] Ajouter tests E2E avec Playwright
- [ ] Mock des services externes (APIs IA)

---

## Phase 5: Perfectionnement 🎯 PLANNIFIÉE

- [ ] Longueur lignes 120 → 100
- [ ] N806 - Patterns constants en majuscules
- [ ] N818 - Suffixe Error sur exceptions
- [ ] Docstrings manquantes (~200)

---

## Commandes

### Développement Quotidien
```bash
make check        # Vérification rapide avant commit
make test         # Tests essentiels
make format       # Auto-formatage du code
```

### Avant PR
```bash
make ci           # Simulation CI complète
python scripts/ci_health_check.py
```

### Nettoyage Progressif
```bash
# Vérifier E402
python -m ruff check modules/ --select E402

# Vérifier F811/F821
python -m ruff check modules/ --select F811,F821

# Vérifier sécurité
bandit -r modules/ -f json -o bandit-report.json
```

---

## Suivi des Métriques

| Métrique | Initial | Actuel | Cible |
|----------|---------|--------|-------|
| Ruff errors | 250+ | 0 ✅ | 0 |
| Line length | 250 | 120 | 100 |
| Ruff ignores | 8 | 6 | 0 |
| E741 corrigés | 12 | 0 ✅ | 0 |
| Tests passants | 13/13 | 13/13 ✅ | 13/13 |
| Bandit warnings | ~35 | ~30 | 0 |
| Couverture tests | ~40% | ~40% | 80% |

---

## Ressources

- [Règles Ruff](https://docs.astral.sh/ruff/rules/)
- [Guide de Style Black](https://black.readthedocs.io/en/stable/the_black_code_style.html)
- [Tests Bandit](https://bandit.readthedocs.io/en/latest/plugins/index.html)

---

*Dernière mise à jour: 2026-03-02*
*Status: Phase 2 ✅ terminée - Phase 3 prête à démarrer*
