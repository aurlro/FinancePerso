---
name: financeperso-electron-specific
description: Conventions et patterns spécifiques au projet financeperso-electron (application Electron de gestion financière). Couvre l'architecture réelle avec 11 pages, IPC, SQLite, et intégration IA. À utiliser pour toute modification sur financeperso-electron/.
---

# FinancePerso Electron - Conventions Projet

## 📁 Structure du Projet

```
financeperso-electron/
├── src/
│   ├── main.js                    # Entry point Electron Main
│   ├── preload.js                 # Preload script (contextBridge)
│   ├── App.tsx                    # Root React avec Router
│   │
│   ├── pages/                     # 11 Pages fonctionnelles
│   │   ├── Dashboard.tsx          # Tableau de bord + graphiques
│   │   ├── Transactions.tsx       # Liste transactions + CRUD
│   │   ├── Import.tsx             # Import CSV
│   │   ├── Validation.tsx         # Validation batch
│   │   ├── Budgets.tsx            # Gestion budgets
│   │   ├── Categories.tsx         # Gestion catégories
│   │   ├── Members.tsx            # Multi-membres
│   │   ├── Wealth.tsx             # Patrimoine + simulateur
│   │   ├── Subscriptions.tsx      # Abonnements
│   │   ├── Assistant.tsx          # Chat IA
│   │   └── Settings.tsx           # Paramètres
│   │
│   ├── components/                # Composants React
│   │   ├── ui/                    # shadcn/ui (Button, Card, Dialog...)
│   │   ├── charts/                # Composants Recharts
│   │   ├── CommandPalette.tsx     # Recherche globale Cmd+K
│   │   ├── Layout.tsx             # Layout avec Sidebar/BottomNav
│   │   └── ...
│   │
│   ├── hooks/                     # Hooks personnalisés
│   │   ├── useTransactions.ts
│   │   ├── useCategories.ts
│   │   ├── useMembers.ts
│   │   └── ...
│   │
│   ├── services/                  # Services métier
│   │   ├── database.js            # SQLite service (main process)
│   │   ├── file-import.cjs        # Import CSV
│   │   └── ai-service.cjs         # Service IA
│   │
│   ├── lib/                       # Utilitaires
│   │   └── utils.ts               # cn() et helpers
│   │
│   └── types/                     # Types TypeScript
│       ├── electron.d.ts          # Types IPC
│       └── index.ts               # Types métier
│
├── tests/e2e/                     # Tests Playwright
├── assets/                        # Icônes et images
└── forge.config.js                # Config Electron Forge
```

---

## 🔌 Pattern IPC (Inter-Process Communication)

### Exposition API (preload.js)

```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Database
  db: {
    getAllTransactions: (limit, offset) => 
      ipcRenderer.invoke('db:get-all-transactions', limit, offset),
    addTransaction: (tx) => 
      ipcRenderer.invoke('db:add-transaction', tx),
    updateTransaction: (id, data) => 
      ipcRenderer.invoke('db:update-transaction', id, data),
    deleteTransaction: (id) => 
      ipcRenderer.invoke('db:delete-transaction', id),
    searchTransactions: (query) => 
      ipcRenderer.invoke('db:search-transactions', query),
  },
  
  // Categories
  categories: {
    getAll: () => ipcRenderer.invoke('categories:get-all'),
    add: (category) => ipcRenderer.invoke('categories:add', category),
    update: (id, data) => ipcRenderer.invoke('categories:update', id, data),
    delete: (id) => ipcRenderer.invoke('categories:delete', id),
  },
  
  // Members
  members: {
    getAll: () => ipcRenderer.invoke('members:get-all'),
    add: (member) => ipcRenderer.invoke('members:add', member),
    update: (id, data) => ipcRenderer.invoke('members:update', id, data),
    delete: (id) => ipcRenderer.invoke('members:delete', id),
  },
  
  // Budgets
  budgets: {
    getAll: () => ipcRenderer.invoke('budgets:get-all'),
    getStatus: () => ipcRenderer.invoke('budgets:get-status'),
    set: (category, amount) => ipcRenderer.invoke('budgets:set', category, amount),
    delete: (category) => ipcRenderer.invoke('budgets:delete', category),
  },
  
  // File operations
  file: {
    selectCSV: () => ipcRenderer.invoke('file:select-csv'),
    importCSV: (filePath, options) => 
      ipcRenderer.invoke('file:import-csv', filePath, options),
  },
  
  // AI
  ai: {
    categorize: (label, amount) => 
      ipcRenderer.invoke('ai:categorize', label, amount),
    getSettings: () => ipcRenderer.invoke('ai:get-settings'),
    saveSettings: (settings) => ipcRenderer.invoke('ai:save-settings', settings),
    createRule: (pattern, category) => 
      ipcRenderer.invoke('ai:create-rule', pattern, category),
    analyze: (type) => ipcRenderer.invoke('ai:analyze', type),
  },
  
  // App
  app: {
    getVersion: () => ipcRenderer.invoke('app:get-version'),
    getPath: (name) => ipcRenderer.invoke('app:get-path', name),
  },
});
```

### Utilisation dans React

```typescript
// Pattern: Toujours utiliser useCallback pour les appels IPC
import { useState, useEffect, useCallback } from 'react';

export function useTransactions(limit = 100) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await window.electronAPI.db.getAllTransactions(limit);
      setTransactions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    load();
  }, [load]);

  const add = useCallback(async (tx: Partial<Transaction>) => {
    await window.electronAPI.db.addTransaction(tx);
    await load();
  }, [load]);

  const update = useCallback(async (id: number, data: Partial<Transaction>) => {
    await window.electronAPI.db.updateTransaction(id, data);
    await load();
  }, [load]);

  const remove = useCallback(async (id: number) => {
    await window.electronAPI.db.deleteTransaction(id);
    await load();
  }, [load]);

  return { transactions, loading, error, refresh: load, add, update, remove };
}
```

---

## 🗄️ SQLite Patterns

### DatabaseService (src/services/database.js)

```javascript
class DatabaseService {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.db = null;
  }

  async initialize() {
    return new Promise((resolve, reject) => {
      this.db = new sqlite3.Database(this.dbPath, (err) => {
        if (err) reject(err);
        else this.createTables().then(resolve).catch(reject);
      });
    });
  }

  // Pattern query: Toujours promisify
  async query(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }

  async run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve({ id: this.lastID, changes: this.changes });
      });
    });
  }

  async get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.get(sql, params, (err, row) => {
        if (err) reject(err);
        else resolve(row);
      });
    });
  }
}
```

### Schéma Tables

```javascript
async createTables() {
  const tables = [
    // Transactions
    `CREATE TABLE IF NOT EXISTS transactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT NOT NULL,
      label TEXT NOT NULL,
      amount REAL NOT NULL,
      type TEXT CHECK(type IN ('debit', 'credit')) NOT NULL,
      category TEXT,
      category_validated INTEGER DEFAULT 0,
      member TEXT,
      tags TEXT,
      tx_hash TEXT UNIQUE,
      status TEXT DEFAULT 'pending',
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )`,
    
    // Categories
    `CREATE TABLE IF NOT EXISTS categories (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      emoji TEXT DEFAULT '📦',
      color TEXT DEFAULT '#10b981',
      is_fixed INTEGER DEFAULT 0,
      budget_amount REAL
    )`,
    
    // Members
    `CREATE TABLE IF NOT EXISTS members (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      member_type TEXT DEFAULT 'adult',
      color TEXT DEFAULT '#10b981'
    )`,
    
    // Budgets
    `CREATE TABLE IF NOT EXISTS budgets (
      category TEXT PRIMARY KEY,
      amount REAL NOT NULL,
      period TEXT DEFAULT 'monthly'
    )`,
    
    // Wealth Accounts
    `CREATE TABLE IF NOT EXISTS wealth_accounts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      type TEXT CHECK(type IN ('checking', 'savings', 'investment', 'crypto', 'real_estate')) NOT NULL,
      balance REAL NOT NULL,
      currency TEXT DEFAULT 'EUR'
    )`,
    
    // Savings Goals
    `CREATE TABLE IF NOT EXISTS savings_goals (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      target_amount REAL NOT NULL,
      current_amount REAL DEFAULT 0,
      deadline TEXT
    )`,
    
    // Subscriptions
    `CREATE TABLE IF NOT EXISTS subscriptions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      amount REAL NOT NULL,
      frequency TEXT DEFAULT 'monthly',
      next_payment TEXT,
      category TEXT
    )`,
    
    // Learning Rules
    `CREATE TABLE IF NOT EXISTS learning_rules (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      pattern TEXT UNIQUE NOT NULL,
      category TEXT NOT NULL,
      priority INTEGER DEFAULT 0
    )`,
    
    // AI Settings
    `CREATE TABLE IF NOT EXISTS ai_settings (
      id INTEGER PRIMARY KEY CHECK (id = 1),
      provider TEXT DEFAULT 'gemini',
      model TEXT DEFAULT 'gemini-2.0-flash',
      api_key TEXT,
      enabled INTEGER DEFAULT 0
    )`,
  ];

  for (const sql of tables) {
    await this.run(sql);
  }
}
```

---

## 🎨 Composants UI (shadcn/ui)

### Pattern Card avec KPI

```typescript
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";

interface KPICardProps {
  title: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
}

export function KPICard({ title, value, change, trend, icon }: KPICardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {change !== undefined && (
          <p className={`text-xs flex items-center ${
            trend === 'up' ? 'text-green-600' : 
            trend === 'down' ? 'text-red-600' : 'text-gray-600'
          }`}>
            {trend === 'up' ? <TrendingUp className="w-3 h-3 mr-1" /> : 
             trend === 'down' ? <TrendingDown className="w-3 h-3 mr-1" /> : null}
            {change > 0 ? '+' : ''}{change}%
          </p>
        )}
      </CardContent>
    </Card>
  );
}
```

### Pattern Dialog CRUD

```typescript
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function AddCategoryDialog({ onAdd }: { onAdd: (name: string) => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onAdd(name.trim());
      setName('');
      setOpen(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>Nouvelle catégorie</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Ajouter une catégorie</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="name">Nom</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Transport"
            />
          </div>
          <Button type="submit">Ajouter</Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
```

---

## 📊 Graphiques Recharts

### Pattern Chart Dépenses

```typescript
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

interface ExpenseChartProps {
  data: Array<{ name: string; value: number }>;
}

export function ExpenseChart({ data }: ExpenseChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
```

---

## 🤖 Intégration IA

### Pattern AI Service

```javascript
// src/services/ai-service.cjs
const { GoogleGenAI } = require('@google/genai');

class AIService {
  constructor(dbService) {
    this.db = dbService;
    this.genAI = null;
    this.model = null;
  }

  async initialize() {
    const settings = await this.db.getAISettings();
    if (settings?.enabled && settings?.api_key) {
      this.genAI = new GoogleGenAI({ apiKey: settings.api_key });
      this.model = settings.model || 'gemini-2.0-flash';
    }
  }

  async categorize(label, amount) {
    if (!this.genAI) {
      // Fallback: règles locales
      return this.categorizeWithRules(label, amount);
    }

    const prompt = `Catégorise cette transaction:
Label: "${label}"
Montant: ${amount}€

Réponds UNIQUEMENT avec le nom de la catégorie parmi: ${categories.join(', ')}`;

    try {
      const response = await this.genAI.models.generateContent({
        model: this.model,
        contents: prompt,
      });
      
      const category = response.text.trim();
      return { category, confidence: 0.9, source: 'ai' };
    } catch (error) {
      return this.categorizeWithRules(label, amount);
    }
  }

  categorizeWithRules(label, amount) {
    // Pattern matching simple
    const rules = [
      { pattern: /supermarche|carrefour|auchan|lidl/i, category: 'Alimentation' },
      { pattern: /total|shell|bp|essence/i, category: 'Transport' },
      { pattern: /edf|engie|direct energie/i, category: 'Logement' },
    ];

    for (const rule of rules) {
      if (rule.pattern.test(label)) {
        return { category: rule.category, confidence: 0.7, source: 'rules' };
      }
    }

    return { category: 'Inconnu', confidence: 0, source: 'default' };
  }
}

module.exports = { AIService };
```

---

## 🧪 Tests E2E

### Pattern Test Page

```typescript
// tests/e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
  });

  test('affiche les KPIs principaux', async ({ page }) => {
    await expect(page.getByText('Revenus du mois')).toBeVisible();
    await expect(page.getByText('Dépenses du mois')).toBeVisible();
    await expect(page.getByText('Solde')).toBeVisible();
  });

  test('navigation vers transactions', async ({ page }) => {
    await page.getByRole('link', { name: /transactions/i }).click();
    await expect(page).toHaveURL(/.*transactions/);
    await expect(page.getByText('Transactions')).toBeVisible();
  });

  test('command palette s\'ouvre avec Cmd+K', async ({ page }) => {
    await page.keyboard.press('Meta+k');
    await expect(page.getByPlaceholder('Rechercher...')).toBeVisible();
  });
});
```

---

## ✅ Checklist Nouvelle Feature

### Backend (Main Process)
- [ ] Ajouter méthode dans DatabaseService
- [ ] Ajouter handler IPC dans main.js
- [ ] Exposer dans preload.js
- [ ] Ajouter types dans electron.d.ts

### Frontend (Renderer)
- [ ] Créer hook React dans hooks/
- [ ] Créer/modifier page dans pages/
- [ ] Ajouter route dans App.tsx
- [ ] Ajouter lien dans Layout.tsx

### Tests
- [ ] Ajouter test E2E dans tests/e2e/
- [ ] Vérifier build: `npm run build`
- [ ] Vérifier tests: `npm run test`

### UI
- [ ] Messages en français
- [ ] Loading states
- [ ] Error boundaries
- [ ] Empty states

---

## 📚 Ressources Internes

- [PROJECT_COMPLETION_REPORT.md](../../PROJECT_COMPLETION_REPORT.md) - Rapport complet
- [ROADMAP.md](../../ROADMAP.md) - Roadmap et features
- [USER_GUIDE.md](../../USER_GUIDE.md) - Guide utilisateur

---

**Version**: 1.0  
**Dernière mise à jour**: 2026-03-13  
**Compatible avec**: financeperso-electron v1.0.0
