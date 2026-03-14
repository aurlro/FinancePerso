# 📊 RAPPORT D'AUDIT DE COHÉRENCE - FinancePerso Electron

## Score de Cohérence Global : **62/100** ⚠️

---

## 🔴 PROBLÈMES CRITIQUES (P0)

### 1. Duplication massive de `formatCurrency` - **7 occurrences**

| Fichier | Ligne |
|---------|-------|
| `pages/Wealth.tsx` | 54 |
| `pages/Budgets.tsx` | 54 |
| `pages/Subscriptions.tsx` | 65 |
| `components/wealth/WealthDistribution.tsx` | 14 |
| `components/wealth/SavingsGoalCard.tsx` | 28 |
| `components/wealth/WealthOverview.tsx` | 34 |
| `components/wealth/ProjectionSimulator.tsx` | 21 |

**Code dupliqué:**
```typescript
const formatCurrency = (amount: number) => 
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(amount);
```

**Solution:**
```typescript
// lib/formatters.ts
export const formatCurrency = (amount: number, currency = 'EUR') => 
  new Intl.NumberFormat('fr-FR', { style: 'currency', currency }).format(amount);
```

---

### 2. Double définition de `DashboardStats`

- `types/index.ts:33` - Interface principale
- `hooks/useElectron.ts:33` - Interface locale dupliquée

**Solution:** Supprimer la définition de `useElectron.ts` et importer depuis `@/types`.

---

### 3. Deux hooks IPC identiques - `useElectron` vs `useIPC`

Les deux hooks exposent **quasiment la même API** avec des déclarations de types `Window` différentes :
- `useElectron.ts` - Plus ancien, moins complet
- `useIPC.ts` - Plus récent, plus complet

**Impact:** Confusion sur quel hook utiliser. Certains composants utilisent `useElectron` (Dashboard), d'autres `useIPC` (Budgets, Subscriptions).

**Solution:** 
- Supprimer `useElectron.ts` 
- Renommer `useIPC.ts` → `useElectron.ts` 
- Mettre à jour tous les imports

---

### 4. Trois composants `KPICard` différents

| Composant | Emplacement | Props |
|-----------|-------------|-------|
| KPICard (générique) | `components/KPICard.tsx` | `title, value, icon, trend, color` |
| KPICard (charts) | `components/charts/KPICard.tsx` | `title, value, variant, trend, trendLabel` |
| KPICard (interne) | `components/wealth/WealthOverview.tsx` | `title, amount, icon, color, trend` |

**Solution:** 
- Garder celui de `components/KPICard.tsx` (le plus flexible)
- Supprimer ou refactorer les autres pour utiliser le composant commun

---

### 5. Déclarations `Window` dupliquées

Interface `Window` redéfinie dans :
- `hooks/useIPC.ts` (5-62)
- `hooks/useElectron.ts` (5-30) 
- `pages/Transactions.tsx` (11-19)

**Solution:** Créer un fichier `src/types/electron.d.ts` avec une seule déclaration globale.

---

## 🟠 PROBLÈMES IMPORTANTS (P1)

### 6. Duplication de constantes membres

- `hooks/useMembers.ts:5-6` : `DEFAULT_MEMBER_COLORS`, `DEFAULT_MEMBER_EMOJIS`
- `pages/Members.tsx:13-22` : `MEMBER_COLORS`, `MEMBER_EMOJIS` (avec labels)

**Solution:** Unifier dans `useMembers.ts` et exporter pour réutilisation.

---

### 7. Duplication de `formatDate`

- `pages/Subscriptions.tsx:72-81`
- `components/wealth/SavingsGoalCard.tsx:35-43`

**Solution:** Déplacer dans `lib/formatters.ts`.

---

### 8. Duplication de `getMonthsRemaining` / calcul de mois

- `hooks/useWealth.ts:194-197` (dans `addGoal`)
- `components/wealth/SavingsGoalCard.tsx:45-53` (fonction `getMonthsRemaining`)

**Solution:** Créer un utilitaire `lib/dateUtils.ts`.

---

### 9. Icônes inline dupliquées

Plusieurs icônes identiques définies dans plusieurs pages :
- `PlusIcon` : Budgets.tsx, Subscriptions.tsx, Wealth.tsx, SavingsGoalCard.tsx
- `EditIcon`, `TrashIcon`, `AlertTriangleIcon` : Budgets.tsx, Subscriptions.tsx

**Solution:** Utiliser la librairie `lucide-react` déjà installée ou créer un fichier `components/icons/index.ts`.

---

### 10. Pattern de gestion d'état incohérent

Certains hooks utilisent :
- `loading` (useMembers, useTransactions)
- `isLoading` (useBudgets, useWealthAccounts, useSubscriptions)

**Solution:** Standardiser sur `isLoading` (plus explicite).

---

## 🟡 PROBLÈMES MINEURS (P2)

### 11. Imports incohérents
- Certains utilisent `@/types`
- D'autres utilisent `../types`

### 12. Style de guillemets incohérent
- Mélange de simples `'` et doubles `"` quotes

### 13. Composants UI locaux dans les pages
Plusieurs pages définissent leurs propres composants (ex: `BudgetCard` dans Budgets.tsx) qui pourraient être réutilisables.

---

## ✅ POINTS POSITIFS NOTABLES

### 1. Architecture modulaire bien structurée
- Séparation claire entre hooks, composants, pages et types
- Pattern de hooks cohérent avec `useState`, `useCallback`, `useEffect`

### 2. Bonne utilisation de TypeScript
- Types bien définis dans `types/index.ts` et `types/wealth.ts`
- Re-exports bien organisés via les fichiers `index.ts`

### 3. Gestion des états de chargement/erreur
- Pattern cohérent : `loading`, `error`, `refresh` dans les hooks

### 4. Utilisation de shadcn/ui
- Composants UI réutilisables bien intégrés
- Cohérence visuelle grâce à Tailwind CSS

---

## 📋 PLAN D'ACTION RECOMMANDÉ

### Phase 1 - Refactor Critique (P0)
1. [ ] Créer `lib/formatters.ts` avec `formatCurrency`, `formatDate`
2. [ ] Créer `types/electron.d.ts` avec déclaration Window unique
3. [ ] Unifier les hooks useElectron/useIPC
4. [ ] Supprimer les doublons de KPICard

### Phase 2 - Nettoyage (P1)
5. [ ] Créer `lib/dateUtils.ts` pour les calculs de dates
6. [ ] Unifier les constantes membres
7. [ ] Utiliser lucide-react pour les icônes
8. [ ] Standardiser sur `isLoading`

### Phase 3 - Polish (P2)
9. [ ] Uniformiser les imports
10. [ ] Normaliser les quotes
11. [ ] Extraire les composants réutilisables des pages

---

## 📊 MÉTRIQUES

| Métrique | Valeur | État |
|----------|--------|------|
| Duplication de code | ~15% | ⚠️ Élevé |
| Fonctions format* dupliquées | 7 | 🔴 Critique |
| Hooks IPC similaires | 2 | 🔴 Critique |
| Composants KPICard | 3 | 🔴 Critique |
| Fichiers index.ts bien structurés | 4/4 | ✅ Bon |
| Utilisation TypeScript | 100% | ✅ Excellent |

---

*Rapport généré par Consistency Keeper - 14 mars 2026*
