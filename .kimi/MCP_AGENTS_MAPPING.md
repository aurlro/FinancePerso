# 🔗 Mapping MCP Servers ↔ Agents FinancePerso

> Quel MCP utiliser pour quel agent ? Référence rapide.

---

## 📊 Tableau de correspondance

| Agent | Domaine | MCP Principal | MCP Secondaire | Cas d'usage typique |
|-------|---------|---------------|----------------|---------------------|
| **AGENT-000** | Orchestration | - | github | Créer issues de coordination |
| **AGENT-001** | Database | **sqlite** | filesystem | Migrations, requêtes complexes |
| **AGENT-002** | Security | github | filesystem | Scan secrets, audit fichiers |
| **AGENT-003** | DevOps | filesystem | shell | Docker, CI/CD, scripts |
| **AGENT-004** | Transactions | **sqlite** | context7 | Debug transactions, import |
| **AGENT-005** | Categorization | **sqlite** | context7 | Stats IA, apprentissage |
| **AGENT-006** | Analytics | **sqlite** | playwright | KPIs, dashboards, screenshots |
| **AGENT-007** | AI Providers | fetch | context7 | Test APIs, doc providers |
| **AGENT-008** | AI Features | sqlite | fetch | Anomalies, prédictions |
| **AGENT-009** | UI Components | filesystem | playwright | Création composants, screenshots |
| **AGENT-010** | Navigation | **playwright** | - | UX flows, clics, navigation |
| **AGENT-011** | Validation | **sqlite** | filesystem | Data integrity, schéma |
| **AGENT-012** | Tests | **playwright** | shell | E2E tests, screenshots |
| **AGENT-013** | QA | **playwright** | github | Validation, issues PRs |
| **AGENT-014** | Budgets | **sqlite** | - | Calculs budget vs réel |
| **AGENT-015** | Members | **sqlite** | - | Stats membres, attribution |
| **AGENT-016** | Notifications | **sqlite** | - | Queue notifs, historique |
| **AGENT-017** | Data Pipeline | **sqlite** | filesystem | ETL, migrations data |
| **AGENT-018** | Open Banking | **fetch** | sqlite | APIs bancaires, sync |
| **AGENT-019** | Performance | **playwright** | sqlite | Benchmarks, lenteurs |
| **AGENT-020** | Accessibility | **playwright** | - | A11y checks, contrastes |
| **AGENT-021** | Documentation | filesystem | github | Docs, README, wiki |

---

## 🎯 Utilisation par MCP

### MCP SQLite → Agents DB/Analytics

**Agents concernés:** AGENT-001, 004, 005, 006, 011, 014, 015, 016, 017, 019

```sql
-- AGENT-001 (Database Architect)
-- Vérifier structure tables
SELECT name FROM sqlite_master WHERE type='table';

-- AGENT-004 (Transaction Engine)
-- Debug transaction spécifique
SELECT * FROM transactions WHERE tx_hash = 'abc123';

-- AGENT-006 (Analytics Dashboard)
-- Calcul KPIs pour dashboard
SELECT 
    SUM(CASE WHEN amount < 0 THEN ABS(amount) END) as depenses,
    SUM(CASE WHEN amount > 0 THEN amount END) as revenus
FROM transactions 
WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now');

-- AGENT-014 (Budget Manager)
-- Budget vs Réel
SELECT b.category, b.amount as budget,
       COALESCE(SUM(t.amount), 0) as depense
FROM budgets b
LEFT JOIN transactions t ON b.category = t.category_validated
GROUP BY b.category;
```

### MCP Filesystem → Agents UI/Dev

**Agents concernés:** AGENT-003, 009, 021

```python
# AGENT-009 (UI Component Architect)
# Lister composants existants V5.5
filesystem/list_directory: {"path": "/modules/ui/v5_5/components"}

# AGENT-021 (Technical Writer)
# Explorer structure docs
filesystem/list_directory: {"path": "/docs"}

# AGENT-003 (DevOps Engineer)
# Vérifier scripts de déploiement
filesystem/list_directory: {"path": "/scripts"}
```

### MCP Playwright → Agents Test/UX

**Agents concernés:** AGENT-006, 010, 012, 013, 019, 020

```python
# AGENT-010 (Navigation Experience)
# Test flow utilisateur
playwright/navigate: {"url": "http://localhost:8501"}
playwright/click: {"element": "Menu Opérations"}
playwright/fill_form: {"fields": [...]}

# AGENT-012 (Test Automation)
# Screenshot pour comparaison
playwright/take_screenshot: {"filename": "test_kpi_cards.png"}

# AGENT-019 (Performance Engineer)
# Mesurer temps chargement
playwright/navigate: {"url": "http://localhost:8501"}
# + analyse console network
```

### MCP GitHub → Agents Dev/QA

**Agents concernés:** AGENT-002, 003, 013, 021

```python
# AGENT-013 (QA Integration)
# Créer issue pour bug trouvé
github/create_issue: {
    "title": "[V5.5] KPI Card monte incorrectement",
    "body": "...",
    "labels": ["bug", "v5.5", "ui"]
}

# AGENT-003 (DevOps)
# Créer PR après feature
github/create_pull_request: {
    "title": "Feat: Nouveau système de KPIs",
    "head": "feature/kpi-v5.5",
    "base": "main"
}
```

### MCP Fetch → Agents API/Integrations

**Agents concernés:** AGENT-007, 018

```python
# AGENT-018 (Open Banking)
# Tester API bancaire
fetch/fetch: {
    "url": "https://api.bank.com/v1/accounts",
    "headers": {"Authorization": "Bearer ..."}
}

# AGENT-007 (AI Provider Manager)
# Vérifier statut API OpenAI
timeout=30
```

---

## 🔧 Configuration MCP optimale par agent

### AGENT-001: Database Architect

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "/Users/aurelien/Documents/Projets/FinancePerso/Data/finance.db"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/aurelien/Documents/Projets/FinancePerso/migrations"]
    }
  }
}
```

### AGENT-009: UI Component Architect

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/aurelien/Documents/Projets/FinancePerso/modules/ui"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-playwright"]
    }
  }
}
```

### AGENT-006: Analytics Dashboard Engineer

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "/Users/aurelien/Documents/Projets/FinancePerso/Data/finance.db"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-playwright"]
    }
  }
}
```

---

## 📋 Scénarios d'utilisation MCP

### Scénario 1: Debug transaction manquante

```
Agent: AGENT-004 (Transaction Engine)
MCP: sqlite

Requêtes:
1. "SELECT COUNT(*) FROM transactions WHERE date = '2026-02-01'"
2. "SELECT * FROM transactions WHERE label LIKE '%AMAZON%' AND date >= '2026-01-01'"
3. "SELECT status, COUNT(*) FROM transactions GROUP BY status"
```

### Scénario 2: Créer composant UI V5.5

```
Agents: AGENT-009 → AGENT-006 → AGENT-012
MCP: filesystem, playwright

Actions:
1. AGENT-009: filesystem/list_directory → voir composants existants
2. AGENT-009: Crée nouveau composant
3. AGENT-006: Intègre dans dashboard
4. AGENT-012: playwright/navigate + screenshot pour validation
```

### Scénario 3: Audit performance

```
Agent: AGENT-019 (Performance Engineer)
MCP: playwright, sqlite

Actions:
1. playwright/navigate: "http://localhost:8501"
2. playwright/take_screenshot: {fullPage: true}
3. sqlite/read_query: "SELECT COUNT(*) FROM transactions" → corrèle avec temps chargement
4. Analyse: Identifier goulots d'étranglement
```

### Scénario 4: Migration de données

```
Agents: AGENT-001 → AGENT-017 → AGENT-012
MCP: sqlite, filesystem

Actions:
1. AGENT-001: sqlite/read_query → backup données
2. AGENT-017: filesystem/read_file → script migration
3. AGENT-001: sqlite/write_query → applique migration
4. AGENT-012: sqlite/read_query → vérifie intégrité
```

---

## ⚡ Quick Reference

| Tu veux... | Utilise MCP... | Via Agent... |
|------------|----------------|--------------|
| Requête SQL | **sqlite** | AGENT-001, 004, 006 |
| Explorer fichiers | **filesystem** | AGENT-009, 021 |
| Screenshot UI | **playwright** | AGENT-006, 012 |
| Tester navigation | **playwright** | AGENT-010 |
| Appel API externe | **fetch** | AGENT-007, 018 |
| Gestion GitHub | **github** | AGENT-003, 013 |
| Doc library | **context7** | AGENT-005, 007 |

---

**Dernière mise à jour:** 2026-03-01
