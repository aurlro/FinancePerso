# 📋 Templates de Prompts - Architecture FinancePerso

> Copier-coller et adapter selon votre besoin

---

## 🎯 Template 1: Nouvelle Feature (Complet)

```markdown
## Contexte
Projet: FinancePerso (app Streamlit V5.5)
Feature: [DÉCRIRE LA FEATURE]

Fichiers concernés:
- [LISTE DES FICHIERS EXISTANTS À MODIFIER]
- [LISTE DES NOUVEAUX FICHIERS À CRÉER]

## Workflow demandé

### Phase 1: Analyse cohérence
consistency-keeper analyze:
- Vérifier si feature/pattern similaire existe déjà
- Identifier réutilisation possible
- Lister composants/fonctions existants pertinents

### Phase 2: Audit technique
python-app-auditor + financeperso-specific:
- Analyser qualité code existant
- Vérifier conventions FinancePerso:
  * Session state, cache, widget keys
  * Messages en français
  * Patterns DB (get_db_connection)
  * Structure modules/ui/v5_5/

### Phase 3: Orchestration
AGENT-000 route:
- Identifier agents spécialisés nécessaires
- Planifier ordre d'exécution
- Gérer dépendances

### Phase 4: Implémentation
[AGENT-XXX] utilise MCP appropriés:
- sqlite: si besoin requêtes DB
- filesystem: si exploration fichiers
- playwright: si test UI nécessaire
- fetch: si appel API externe

### Phase 5: Validation
consistency-keeper validate:
- Vérifier DRY respecté
- Vérifier doc synchronisée (AGENTS.md, CHANGELOG.md)
- Vérifier rangement fichiers
- Vérifier performance (cache, pas de N+1)

### Phase 6: Tests
AGENT-012 (Test Automation):
- Tests unitaires si logique métier
- Tests playwright si UI concerné
- Screenshot comparaison si visuel

## Livrables attendus
- [ ] Code implémenté selon conventions
- [ ] Tests passent
- [ ] Documentation à jour
- [ ] Screenshots validation (si UI)
```

### Exemple rempli:

```markdown
## Contexte
Feature: "Ajouter un filtre par membre sur le dashboard"

Fichiers:
- MODIFIER: modules/ui/v5_5/dashboard/dashboard_v5.py
- MODIFIER: modules/ui/v5_5/dashboard/kpi_grid.py
- CRÉER: modules/ui/v5_5/components/member_filter.py

## Workflow
consistency-keeper → python-app-auditor+financeperso-specific 
→ AGENT-000 → AGENT-009 (UI) + AGENT-006 (Analytics) 
→ AGENT-012 → consistency-keeper validate
```

---

## 🐛 Template 2: Bug Fix (Rapide)

```markdown
## Contexte
Type: Bug Fix
Sévérité: [CRITIQUE/MAJEUR/MINEUR]
Symptôme: [DÉCRIRE LE BUG]
Composant affecté: [MODULE/PAGE]

## Workflow rapide

### Phase 1: Triage
AGENT-000:
- Identifier agent responsable du domaine
- Évaluer impact sur autres composants

### Phase 2: Investigation
[AGENT-XXX]:
- Reproduire le bug
- Identifier root cause
- Utiliser MCP sqlite si données concernées

### Phase 3: Correction
[AGENT-XXX]:
- Implémenter fix minimal
- Vérifier pas d'effets de bord

### Phase 4: Validation rapide
python-app-auditor quick-check:
- Vérifier pas de régression
- Code propre et conventions respectées

### Phase 5: Test
AGENT-012:
- Test de non-régression
- Screenshot si UI (playwright)

## Notes
- Ne PAS passer par consistency-keeper si hotfix urgent
- Privilégier le minimalisme (pas de refacto)
- Documenter dans CHANGELOG.md
```

### Exemple rempli:

```markdown
Bug: "Les transactions importées n'apparaissent pas dans Validation"
Sévérité: CRITIQUE
Agent: AGENT-004 (Transaction Engine)
MCP: sqlite pour vérifier status='pending'
```

---

## 🔄 Template 3: Refactoring

```markdown
## Contexte
Type: Refactoring
Cible: [MODULE/FONCTION À REFACTORER]
Objectif: [POURQUOI: lisibilité/perf/maintenabilité]

## Workflow

### Phase 1: Baseline
consistency-keeper --baseline:
- Capturer état actuel (duplications, complexité)
- Documenter métriques avant

### Phase 2: Plan
python-app-auditor:
- Analyser code cible
- Identifier patterns d'amélioration
- Planifier étapes de migration

### Phase 3: Coordination
AGENT-000:
- Notifier tous les agents concernés
- Planifier ordre de migration
- Identifier risques de régression

### Phase 4: Exécution par étapes
[AGENT-XXX] par composant:
- Migrer étape par étape
- Tests entre chaque étape
- Garder compatibilité temporaire

### Phase 5: Validation
consistency-keeper --compare:
- Comparer avec baseline
- Vérifier amélioration métriques
- S'assurer pas de régression

### Phase 6: Tests complets
AGENT-012 + AGENT-013:
- Tests unitaires complets
- Tests d'intégration
- Tests E2E si changement UX

## Risques à mitiger
- [ ] Régression fonctionnelle
- [ ] Changement de comportement API
- [ ] Impact performance
- [ ] Documentation obsolète
```

---

## 🎨 Template 4: UI/UX - Implémentation Maquette

```markdown
## Contexte
Type: Implémentation maquette V5.5
Référence: [FICHIER MAQUETTE PNG/FIGMA]
Composants: [LISTE DES COMPOSANTS À IMPLÉMENTER]

## Workflow

### Phase 1: Analyse design
consistency-keeper + ux-product-designer:
- Identifier composants existants réutilisables
- Extraire design tokens (couleurs, espacements, typographie)
- Vérifier cohérence avec système V5.5

### Phase 2: Audit technique
streamlit-app-auditor + financeperso-specific:
- Analyser contraintes Streamlit
- Vérifier compatibilité V5.5
- Identifier limitations techniques

### Phase 3: Architecture composants
AGENT-000 → AGENT-009:
- Planifier découpage composants
- Définir props/interfaces
- Organiser structure fichiers

### Phase 4: Implémentation
AGENT-009:
- Utiliser filesystem pour lire existants
- Suivre patterns V5.5 (theme.py, layout.py)
- Props: title, value, on_change, etc.

### Phase 5: Intégration
AGENT-006:
- Intégrer composants dans pages
- Connexion données (sqlite si besoin)
- Gestion état (session_state)

### Phase 6: Validation visuelle
streamlit-app-auditor + playwright:
- Lancer app
- Screenshots comparatifs
- Vérifier responsive/mobile
- Vérifier accessibilité (AGENT-020)

### Phase 7: Finalisation
consistency-keeper:
- Vérifier DRY (pas duplication CSS/composants)
- Synchroniser doc (AGENTS.md)
- Mettre à jour CHANGELOG.md

## Livrables
- [ ] Composants implémentés
- [ ] Screenshots de validation
- [ ] Comparaison côte à côte avec maquette
- [ ] Documentation composants
```

---

## 📊 Template 5: Analytics / Dashboard

```markdown
## Contexte
Type: Nouvelle métrique/analyse
KPI: [NOM DU KPI]
Formule: [COMMENT LE CALCULER]
Visualisation: [TABLEAU/GRAPHIQUE/CARTE]

## Workflow

### Phase 1: Analyse métier
consistency-keeper:
- Vérifier pas de KPI similaire existant
- Identifier source de données
- Vérifier calcul déjà implémenté ailleurs

### Phase 2: Audit données
AGENT-000 → AGENT-001 + AGENT-006:
- Analyser schéma DB (sqlite)
- Valider formule SQL possible
- Tester requête sur données réelles

### Phase 3: Design visualisation
ux-product-designer + AGENT-009:
- Choisir type de visualisation
- Définir interactions (hover, clic, drill-down)
- Maquetter si nouveau composant

### Phase 4: Implémentation calcul
AGENT-006:
- Fonction de calcul avec cache
- Requête SQL optimisée
- Gestion cas limites (données manquantes)

### Phase 5: Implémentation UI
AGENT-009:
- Composant de visualisation
- Intégration dans dashboard
- Responsive design

### Phase 6: Tests
AGENT-012:
- Tests calculs (valeurs attendues)
- Tests affichage (playwright)
- Tests edge cases

## Exemple de requête SQL (via MCP sqlite)
```sql
-- [METTRE REQUÊTE ICI]
```
```

---

## 🔧 Template 6: Configuration/DevOps

```markdown
## Contexte
Type: Configuration / Infrastructure
Cible: [Docker/CI/CD/Environnement/Secrets]

## Workflow

### Phase 1: Analyse existant
AGENT-003 (DevOps Engineer):
- Lire configuration actuelle
- Identifier dépendances
- Évaluer impact changement

### Phase 2: Audit sécurité
AGENT-002 (Security Guardian):
- Vérifier pas d'exposition secrets
- Valider permissions
- Check bonnes pratiques

### Phase 3: Implémentation
AGENT-003:
- Modifier fichiers config
- Utiliser filesystem pour lire/écrire
- Tester localement si possible

### Phase 4: Validation
AGENT-003 + AGENT-013:
- Tests intégration
- Vérifier déploiement fonctionne
- Tests E2E sur environnement

### Phase 5: Documentation
AGENT-021 (Technical Writer):
- Mettre à jour docs déploiement
- Documenter nouvelles variables/env
- Notifier équipe si breaking change
```

---

## ⚡ Template 7: Quick Fix / Hotfix

```markdown
## Contexte
URGENT: [DESCRIPTION RAPIDE]
Fichier: [CHEMIN FICHIER]
Ligne: [NUMÉRO LIGNE APPROX]

## Action immédiate
[AGENT-XXX]:
- Lire fichier concerné
- Appliquer correction minimale
- Vérifier syntaxe ok

## Validation rapide
- Tests essentiels: make test
- Si UI: screenshot rapide
- Pas de consistency-keeper (trop long)

## Post-hotfix (dès que possible)
- Créer issue pour refactor propre
- Documenter dans CHANGELOG.md
- Passer par workflow complet

## ⚠️ Limites
- Ne pas dépasser 20 lignes de modif
- Pas de refacto
- Pas de changement architecture
```

---

## 📋 Cheat Sheet - Choix rapide

| Type de tâche | Workflow | Durée estimée |
|---------------|----------|---------------|
| **Feature complète** | CK → Skills → AGENT-000 → [Agents] → CK → Tests | 30-60 min |
| **Bug fix standard** | AGENT-000 → [Agent] → Audit → Tests | 10-20 min |
| **Bug critique** | [Agent] → Quick fix → Tests | 5-10 min |
| **Refactoring** | CK baseline → Plan → Étapes → CK compare | 45-90 min |
| **UI maquette** | CK+UX → Streamlit audit → AGENT-009 → Playwright | 30-45 min |
| **KPI/Analytics** | CK → AGENT-001(sqlite) → AGENT-006 → AGENT-012 | 20-30 min |
| **Config/DevOps** | AGENT-003 → AGENT-002 → Tests | 15-30 min |

---

## 🎯 Checklist avant d'envoyer un prompt

- [ ] J'ai précisé le type de tâche
- [ ] J'ai listé les fichiers concernés
- [ ] J'ai indiqué le workflow à suivre
- [ ] J'ai mentionné les MCP utiles (si connus)
- [ ] J'ai défini les livrables attendus

---

**Templates créés le:** 2026-03-01
