# 🎨 Roadmap UI/UX - Fusion FinCouple Pro

> Design system, composants et parcours utilisateur

---

## 1. Design System

### 1.1 Tokens de design

```typescript
// tokens.ts
export const tokens = {
  colors: {
    // Primary - Emerald (comme FinCouple)
    primary: {
      50: '#ecfdf5',
      100: '#d1fae5',
      200: '#a7f3d0',
      300: '#6ee7b7',
      400: '#34d399',
      500: '#10b981', // Main
      600: '#059669',
      700: '#047857',
      800: '#065f46',
      900: '#064e3b',
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
    '2xl': '3rem',   // 48px
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

### 1.2 Typographie

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

## 2. Composants Clés

### 2.1 KPI Cards

```tsx
// Composant fusionné (FinCouple design + FinancePerso data)
interface KpiCardProps {
  title: string;
  value: string;
  trend?: {
    value: number;
    label: string;
    direction: 'up' | 'down' | 'neutral';
  };
  icon: LucideIcon;
  variant?: 'default' | 'income' | 'expense' | 'savings';
}

// Variantes de couleur
const variants = {
  default: 'bg-white border-slate-200',
  income: 'bg-emerald-50 border-emerald-200',
  expense: 'bg-rose-50 border-rose-200',
  savings: 'bg-blue-50 border-blue-200',
};
```

**Design:**
- Card avec border-radius lg (12px)
- Shadow md au hover
- Icon dans un badge rond coloré
- Value en text-2xl bold
- Trend avec flèche et couleur

### 2.2 Transaction List

```tsx
interface TransactionListProps {
  transactions: Transaction[];
  onSelect?: (t: Transaction) => void;
  onValidate?: (ids: string[]) => void;
  groupBy?: 'date' | 'category' | 'none';
  enableBulkActions?: boolean;
}
```

**Features:**
- Grouping par date (aujourd'hui, hier, cette semaine...)
- Swipe actions sur mobile
- Checkbox pour sélection multiple
- Drag & drop pour catégoriser
- Virtualization pour grandes listes

### 2.3 Import Wizard

**Steps:**
1. **Upload**: Dropzone avec preview
2. **Mapping**: Select colonnes avec détection auto
3. **Preview**: Tableau avec catégories suggérées
4. **Validation**: Résumé avant import
5. **Success**: Animation + CTA

### 2.4 Charts

```tsx
// Recharts configuration
const chartConfig = {
  expenses: {
    label: 'Dépenses',
    color: 'hsl(var(--destructive))',
  },
  income: {
    label: 'Revenus',
    color: 'hsl(var(--success))',
  },
};
```

**Types:**
- Donut: Répartition catégories
- Line: Évolution temporelle
- Bar: Comparaison périodes
- Area: Cumul (patrimoine)

---

## 3. Parcours Utilisateur

### 3.1 Onboarding

```
Étape 1: Bienvenue
┌─────────────────────────────────────────┐
│  👋 Bienvenue sur FinCouple Pro         │
│                                         │
│  La gestion financière simplifiée       │
│  pour les couples.                      │
│                                         │
│  [Commencer]                            │
└─────────────────────────────────────────┘

Étape 2: Configuration foyer
┌─────────────────────────────────────────┐
│  👥 Votre foyer                         │
│                                         │
│  Comment s'appelle votre foyer?         │
│  [________________]                     │
│                                         │
│  Qui êtes-vous?                         │
│  [Alice] [Bob] [Autre]                  │
│                                         │
│  [Continuer]                            │
└─────────────────────────────────────────┘

Étape 3: Premier compte
┌─────────────────────────────────────────┐
│  💳 Votre premier compte                │
│                                         │
│  Type: [Perso ▼] [Joint ▼]             │
│  Nom: [Compte joint ______]             │
│  Banque: [Société Générale ▼]          │
│                                         │
│  [Ajouter]         [Passer pour l'instant]
└─────────────────────────────────────────┘

Étape 4: Import ou Démo
┌─────────────────────────────────────────┐
│  📥 Importez vos relevés                │
│                                         │
│  [Importer un CSV]    [Voir la démo]    │
│                                         │
│  💡 Conseil: Exportez vos relevés       │
│  depuis votre appli bancaire            │
└─────────────────────────────────────────┘
```

### 3.2 Dashboard Quotidien

```
┌─────────────────────────────────────────────────────┐
│  ☰  FinCouple Pro              🔔 👤               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Mars 2026                    [<] [Aujourd'hui] [>]│
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ Reste à  │ │ Dépenses │ │ Revenus  │ │Épargne │ │
│  │ vivre    │ │          │ │          │ │        │ │
│  │ €2,450   │ │ -€3,200  │ │ +€5,800  │ │ €600   │ │
│  │ ↑ 12%    │ │ ↑ 5%     │ │ → 0%     │ │ ↑ 20%  │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│                                                     │
│  ┌───────────────────┐ ┌─────────────────────────┐ │
│  │  Répartition      │ │  Évolution              │ │
│  │                   │ │                         │ │
│  │    [DONUT]        │ │    [LINE CHART]         │ │
│  │                   │ │                         │ │
│  │  🟡 Alim: €800    │ │                         │ │
│  │  🔵 Loyer: €1,200 │ │                         │ │
│  └───────────────────┘ └─────────────────────────┘ │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │  Transactions récentes              [Voir tout]│ │
│  │  ────────────────────────────────────────────  │ │
│  │  🍽️  Super U              -€85.40   ✅        │ │
│  │  🏠  Loyer mars          -€1,200    ✅        │ │
│  │  💰  Salaire             +€2,900    ✅        │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │  💡 Suggestion IA                             │ │
│  │  8 transactions à catégoriser                 │ │
│  │  [Valider rapidement]                         │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 3.3 Validation Rapide

```
┌─────────────────────────────────────────────────────┐
│  8 transactions à valider                           │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │  🍽️  Super U, Carrefour... (5)    [Valider ▼]│ │
│  │  Suggéré: Alimentation                        │ │
│  │  ───────────────────────────────────────────  │ │
│  │  ☑️ Super U Marseille    -€45.20   12/03     │ │
│  │  ☑️ Carrefour City       -€23.50   11/03     │ │
│  │  ☑️ Monoprix             -€16.70   10/03     │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │  🚗  Total, Shell... (3)          [Valider ▼]│ │
│  │  Suggéré: Transport                           │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 4. Responsive Breakpoints

```typescript
// breakpoints.ts
export const breakpoints = {
  sm: '640px',   // Mobile landscape
  md: '768px',   // Tablet
  lg: '1024px',  // Desktop
  xl: '1280px',  // Large desktop
  '2xl': '1536px', // Extra large
};

// Usage
const Dashboard = () => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <KpiCard />
      <KpiCard />
      <KpiCard />
      <KpiCard />
    </div>
  );
};
```

### Mobile-First Adaptations

| Élément | Desktop | Mobile |
|---------|---------|--------|
| KPI Cards | 4 colonnes | 2 colonnes → scroll horizontal |
| Charts | Côte à côte | Empilés |
| Navigation | Sidebar fixe | Bottom nav + hamburger |
| Transactions | Tableau | Cards empilées |
| Import | Wizard étapes | Stepper vertical |

---

## 5. Micro-interactions

### 5.1 Animations

```typescript
// Framer Motion variants
const fadeIn = {
  hidden: { opacity: 0, y: 10 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.3 }
  },
};

const stagger = {
  visible: {
    transition: { staggerChildren: 0.05 }
  },
};

// Usage
<motion.div
  initial="hidden"
  animate="visible"
  variants={stagger}
>
  {kpis.map(kpi => (
    <motion.div key={kpi.id} variants={fadeIn}>
      <KpiCard {...kpi} />
    </motion.div>
  ))}
</motion.div>
```

### 5.2 Feedback utilisateur

| Action | Feedback |
|--------|----------|
| Import réussi | Toast + confetti (si >100 tx) |
| Validation batch | Toast avec nombre + undo (5s) |
| Nouveau badge | Modal célébration |
| Streak perdu | Gentle notification |
| Budget dépassé | Alert banner + suggestion |

---

## 6. Dark Mode

```typescript
// tailwind.config.ts
darkMode: 'class',

theme: {
  extend: {
    colors: {
      background: 'hsl(var(--background))',
      foreground: 'hsl(var(--foreground))',
      // ... shadcn colors
    },
  },
}

// Usage
<div className="bg-white dark:bg-slate-950">
  <h1 className="text-slate-900 dark:text-slate-100">
```

---

## 7. Accessibilité (a11y)

### Checklist

- [ ] Contraste WCAG AA minimum
- [ ] Focus visible sur tous les éléments interactifs
- [ ] Labels pour tous les inputs
- [ ] Alt text pour images
- [ ] ARIA labels où nécessaire
- [ ] Navigation clavier complète
- [ ] Reduced motion support

### Exemple

```tsx
<button
  aria-label="Valider la transaction"
  className="focus:ring-2 focus:ring-primary focus:outline-none"
>
  <CheckIcon aria-hidden="true" />
</button>
```

---

## 8. Assets

### 8.1 Icons

```typescript
// Lucide React (consistent avec FinCouple)
import { 
  Wallet, 
  TrendingUp, 
  TrendingDown, 
  PiggyBank,
  CreditCard,
  Settings,
  // ... 
} from 'lucide-react';
```

### 8.2 Illustrations

- Empty states: [undraw.co](https://undraw.co) ou similaire
- Onboarding: Custom illustrations
- Badges: SVG animés

---

*Dernière mise à jour: 2026-03-02*
