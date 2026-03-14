---
name: financeperso-specific
description: Conventions spécifiques au projet FinancePerso. COUVRE DEUX APPLICATIONS : (1) Application Streamlit legacy (racine) et (2) Application Electron moderne (financeperso-electron/). Ce skill fournit les patterns, architecture et bonnes pratiques propres à FinancePerso. À utiliser TOUJOURS COMBINÉ avec python-app-auditor (pour Streamlit), electron-vite-expert (pour Electron), ou streamlit-app-auditor.
---

# FinancePerso - Conventions Projet

## 🏗️ Architecture Dual-Stack

Ce projet contient **DEUX applications** :

```
FinancePerso/
├── [RACINE]                    # Application Streamlit (Legacy)
│   ├── app.py                  # Point d'entrée Streamlit
│   ├── pages/                  # Pages Streamlit (01_*.py, 02_*.py...)
│   ├── modules/                # Modules Python métier
│   │   ├── ai/                 # Suite IA
│   │   ├── db/                 # Couche accès données SQLite
│   │   ├── ui/                 # Composants UI Streamlit
│   │   └── *.py                # Modules métier
│   ├── Data/
│   │   └── finance.db          # Base SQLite (partagée)
│   └── tests/                  # Tests Python
│
└── financeperso-electron/      # Application Electron (Nouveau)
    ├── src/
    │   ├── main.js             # Electron Main Process (Node.js)
    │   ├── preload.js          # Pont IPC sécurisé
    │   ├── App.tsx             # Root React
    │   ├── pages/              # 11 pages React
    │   ├── components/         # Composants React
    │   ├── hooks/              # Hooks personnalisés
    │   ├── services/           # Services (DB, AI, File)
    │   └── types/              # Types TypeScript
    ├── src/services/
    │   ├── database.js         # SQLite service (sqlite3)
    │   ├── file-import.cjs     # Import CSV natif
    │   └── ai-service.cjs      # Service IA (API Gemini/OpenAI)
    ├── tests/e2e/              # Tests Playwright
    └── package.json
```

---

## 📱 Application 1: Streamlit (Legacy)

### Patterns spécifiques Streamlit

#### Connexion base de données
```python
from modules.db.connection import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (id,))
```

#### Session State
```python
# Initialisation toujours avec check
if 'key' not in st.session_state:
    st.session_state.key = default_value

# Modification + rerun
st.session_state.key = new_value
st.rerun()
```

#### Widget keys
Format obligatoire: `f"{type}_{unique_id}"`
```python
st.button("Save", key=f"btn_save_{tx_id}")
st.text_input("Label", key=f"input_label_{i}")
```

#### Messages utilisateur
Toujours en français:
```python
st.success("✅ Transaction enregistrée")
st.error("❌ Une erreur est survenue")
```

### Modules IA Streamlit

Pattern d'utilisation:
```python
from modules.ai import detect_amount_anomalies
from modules.ai_manager import get_ai_provider

provider = get_ai_provider()
anomalies = detect_amount_anomalies(df)
```

### UI Components Streamlit

Import convention:
```python
from modules.ui import load_css, card_kpi, display_flash_messages
from modules.ui.components import render_transaction_drill_down
```

### Tests Streamlit

```bash
pytest
pytest tests/db/ -v
pytest tests/ai/ -v
```

---

## 💻 Application 2: Electron (Nouveau)

### Patterns spécifiques Electron

#### Communication IPC (Renderer → Main)

**Dans le renderer (React)**:
```typescript
// Utiliser window.electronAPI exposé par preload.js
const transactions = await window.electronAPI.db.getAllTransactions(100);
const filePath = await window.electronAPI.file.selectCSV();
```

**Dans le main (Node.js)**:
```javascript
const { ipcMain } = require('electron');

ipcMain.handle('db:get-all-transactions', async (_, limit) => {
  return await dbService.getAllTransactions(limit);
});
```

#### Base de données SQLite (sqlite3)

```javascript
// src/services/database.js - Pattern async/await
class DatabaseService {
  async getAllTransactions(limit = 100, offset = 0) {
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT * FROM transactions ORDER BY date DESC LIMIT ? OFFSET ?`,
        [limit, offset],
        (err, rows) => err ? reject(err) : resolve(rows)
      );
    });
  }
}
```

#### Hooks React personnalisés

```typescript
// src/hooks/useTransactions.ts
import { useState, useEffect } from 'react';

export function useTransactions(limit = 100) {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTransactions();
  }, [limit]);

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const data = await window.electronAPI.db.getAllTransactions(limit);
      setTransactions(data);
    } finally {
      setLoading(false);
    }
  };

  return { transactions, loading, refresh: loadTransactions };
}
```

#### Composants UI shadcn/ui

```typescript
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

// Usage
<Card>
  <CardHeader>
    <CardTitle>Titre</CardTitle>
  </CardHeader>
  <CardContent>
    <Button onClick={handleClick}>Action</Button>
  </CardContent>
</Card>
```

#### Graphiques Recharts

```typescript
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

// Pattern avec ResponsiveContainer
<ResponsiveContainer width="100%" height={300}>
  <PieChart>
    <Pie data={data} dataKey="value" nameKey="name">
      {data.map((entry, index) => (
        <Cell key={`cell-${index}`} fill={entry.color} />
      ))}
    </Pie>
    <Tooltip />
  </PieChart>
</ResponsiveContainer>
```

### Tests Electron

```bash
cd financeperso-electron
npm run test              # Tests E2E Playwright
npm run test:ui           # Mode UI Playwright
npx playwright test tests/e2e/dashboard.spec.ts  # Test spécifique
```

### Build Electron

```bash
cd financeperso-electron
npm run dev               # Développement
npm run build             # Build production
npm run package           # Package local
npm run make              # Créer les installateurs
```

---

## 🔄 Points Communs / Partagés

### Schéma Base de Données (Identique)

```sql
-- Utilisé par les DEUX applications (même fichier SQLite)
transactions:
  - id, date, label, amount, type (debit/credit)
  - category, category_validated
  - member, tags (JSON)
  - tx_hash (déduplication)

categories:
  - id, name, emoji, color, is_fixed, budget_amount

members:
  - id, name, member_type, color

learning_rules:
  - id, pattern, category, priority
```

### Localisation des données

- **Streamlit**: `Data/finance.db` (configurable via DB_PATH)
- **Electron**: `~/Library/Application Support/Electron/finance.db` (macOS)
- **Electron**: `%APPDATA%/Electron/finance.db` (Windows)

### Feature Parité

| Feature | Streamlit | Electron | Statut |
|---------|-----------|----------|--------|
| Dashboard | ✅ | ✅ | Parité |
| Import CSV | ✅ | ✅ | Parité |
| Validation | ✅ | ✅ | Parité |
| Budgets | ✅ | ✅ | Parité |
| Multi-membres | ✅ | ✅ | Parité |
| Patrimoine | ✅ | ✅ | Parité |
| Abonnements | ✅ | ✅ | Parité |
| Assistant IA | ✅ | ✅ | Parité |
| Recherche | ⚠️ | ✅ | Electron > |
| Auto-updater | ❌ | ✅ | Bonus Electron |
| Packaging natif | ❌ | ✅ | Bonus Electron |

---

## 🤖 Combinaison avec les Skills & Agents

### Pour travailler sur l'application Streamlit
```
consistency-keeper → python-app-auditor + financeperso-specific → AGENT-001/004/005
```

### Pour travailler sur l'application Electron
```
consistency-keeper → electron-vite-expert + financeperso-specific → AGENT-025/009/012
```

### Pour synchroniser les deux applications
```
electron-python-sync (pour data sync) + AGENT-017/018
```

### Agents spécialisés par app

**Streamlit:**
- AGENT-001: Database Architect
- AGENT-004: Transaction Engine
- AGENT-005: Categorization AI
- AGENT-006: Analytics Dashboard

**Electron:**
- AGENT-025: Electron Desktop Architect
- AGENT-009: UI Component Architect
- AGENT-010: Navigation Experience
- AGENT-012: Test Automation

**Communs:**
- AGENT-014: Budget Wealth Manager
- AGENT-015: Member Management
- AGENT-007/008: AI Providers

---

## ⚠️ Anti-patterns à Éviter

### Streamlit
| Problème | Solution |
|----------|----------|
| `from modules.ui import card_kpi` dans boucle | Importer une seule fois en haut |
| Modification DB sans invalider cache | `st.cache_data.clear()` |
| Requête DB sans context manager | `with get_db_connection() as conn:` |
| Clés widgets en dur | `key=f"btn_{unique_id}"` |

### Electron
| Problème | Solution |
|----------|----------|
| `import { app } from 'electron'` | Utiliser `require('electron')` |
| Appel DB depuis renderer sans IPC | Toujours passer par `window.electronAPI` |
| SQL injection | Toujours utiliser des paramètres bind `?` |
| Fenêtre sans preload | Configurer `contextIsolation: true` |

---

## 📚 Références

- [references/architecture.md](references/architecture.md) - Détails architecture Streamlit
- [financeperso-electron/PROJECT_COMPLETION_REPORT.md](../financeperso-electron/PROJECT_COMPLETION_REPORT.md) - Rapport Electron
- AGENTS.md à la racine - Guide complet agents
