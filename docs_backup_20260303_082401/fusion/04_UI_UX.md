# 04 - UI/UX & Design System

## 🎨 Design Tokens

### Couleurs

```typescript
// tokens.ts
export const tokens = {
  colors: {
    // Primary - Emerald
    primary: {
      50: '#ecfdf5',
      100: '#d1fae5',
      200: '#a7f3d0',
      300: '#6ee7b7',
      400: '#34d399',
      500: '#10b981', // Main
      600: '#059669',
      700: '#047857',
    },
    
    // Semantic
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    
    // Couple-specific
    personA: '#8b5cf6', // Violet
    personB: '#06b6d4', // Cyan
    joint: '#10b981',   // Emerald
  },
  
  spacing: {
    xs: '0.25rem',   // 4px
    sm: '0.5rem',    // 8px
    md: '1rem',      // 16px
    lg: '1.5rem',    // 24px
    xl: '2rem',      // 32px
  },
  
  borderRadius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
    full: '9999px',
  },
  
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
    glow: '0 0 20px rgba(16, 185, 129, 0.3)',
  },
};
```

### Typographie

```css
/* Font stack */
--font-sans: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Scale */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
```

---

## 📱 Layouts

### Mobile-First Breakpoints

```css
/* Mobile first */
default: 0-639px       /* Mobile */
sm: 640px+             /* Large mobile */
md: 768px+             /* Tablet */
lg: 1024px+            /* Desktop */
xl: 1280px+            /* Large desktop */
```

### Page Structure

```
┌─────────────────────────────────────┐
│  Header (Logo + Menu + Profil)     │
├─────────────────────────────────────┤
│                                     │
│  Main Content                       │
│  ├── KPI Cards (grid)              │
│  ├── Charts                        │
│  └── Transaction List              │
│                                     │
├─────────────────────────────────────┤
│  Bottom Navigation (mobile)        │
└─────────────────────────────────────┘
```

---

## 🧩 Composants clés

### KPI Card

```typescript
interface KPICardProps {
  title: string;
  value: string;
  icon: string;
  trend?: {
    value: string;
    direction: 'up' | 'down' | 'neutral';
  };
  color?: 'emerald' | 'violet' | 'cyan';
}
```

### Transaction Item

```typescript
interface TransactionItemProps {
  id: string;
  label: string;
  amount: number;
  date: string;
  category: {
    name: string;
    emoji: string;
    color: string;
  };
  status: 'pending' | 'validated';
  onValidate?: () => void;
  onEdit?: () => void;
}
```

### Import Wizard

```typescript
interface ImportWizardProps {
  steps: [
    'upload',      // Upload fichier
    'mapping',     // Mapping colonnes
    'preview',     // Preview données
    'validation',  // Validation batch
    'import'       // Import final
  ];
  onComplete: (result: ImportResult) => void;
}
```

---

## 🎯 Parcours utilisateur

### 1. Onboarding

```
┌─────────────────────────────────────┐
│  1. Bienvenue                        │
│     └── Tagline + CTA               │
│                                     │
│  2. Création ménage                  │
│     └── Nom + Membres               │
│                                     │
│  3. Configuration comptes            │
│     └── Perso / Joint               │
│                                     │
│  4. Import initial                   │
│     └── CSV + Catégorisation        │
│                                     │
│  5. Dashboard                        │
│     └── Première vue                │
└─────────────────────────────────────┘
```

### 2. Usage quotidien

```
Dashboard (default view)
    │
    ├── Reste à vivre (card principale)
    ├── Dépenses du jour
    ├── À valider (badge si > 0)
    └── Quick actions

Navigation
    ├── 📊 Dashboard
    ├── 💳 Transactions
    ├── 📈 Budgets
    ├── 👥 Couple
    └── ⚙️ Paramètres
```

---

## 🎭 États & Feedback

### Loading States

```typescript
// Skeleton pour liste
<Skeleton className="h-12 w-full" />

// Spinner pour actions
<Loader2 className="h-4 w-4 animate-spin" />

// Progress pour import
<Progress value={importProgress} />
```

### Empty States

```typescript
// Pas de transactions
<EmptyState
  icon="📊"
  title="Aucune transaction"
  description="Importez votre premier relevé pour commencer"
  action={{ label: "Importer", onClick: openImport }}
/>

// Pas de budget
<EmptyState
  icon="🎯"
  title="Aucun budget défini"
  description="Créez votre premier budget pour suivre vos dépenses"
/>
```

---

## 📱 Responsive

### Mobile (< 768px)
- Navigation bottom bar
- Cards full width
- Transactions : swipe actions
- Import : stepper vertical

### Desktop (>= 1024px)
- Navigation sidebar
- Dashboard grid 3 colonnes
- Transactions : tableau
- Import : stepper horizontal

---

[→ Guide démarrage : 05_START.md](./05_START.md)
