# Guide de Contribution

Merci de votre intérêt pour FinancePerso ! Ce document vous guide pour contribuer au projet.

## 🎯 Types de contributions

- 🐛 **Bug reports** - Signaler des problèmes
- 💡 **Feature requests** - Proposer des fonctionnalités
- 📝 **Documentation** - Améliorer la documentation
- 🔧 **Code** - Implémenter des fonctionnalités ou corriger des bugs

## 🚀 Workflow de développement

### 1. Setup environnement

```bash
# Cloner le repo
git clone https://github.com/votre-username/financeperso-electron.git
cd financeperso-electron

# Installer les dépendances
npm install

# Lancer en mode dev
npm run dev
```

### 2. Structure des branches

- `main` - Production stable
- `develop` - Branche de développement
- `feature/*` - Nouvelles fonctionnalités
- `bugfix/*` - Corrections de bugs
- `hotfix/*` - Corrections urgentes

### 3. Créer une feature

```bash
# Depuis develop
git checkout develop
git pull origin develop

# Créer une branche
git checkout -b feature/ma-nouvelle-feature

# Développer...

# Committer
npm run lint        # Vérifier le linting
npm run test:e2e    # Lancer les tests
git add .
git commit -m "feat: ajoute ma nouvelle feature"

# Pousser
git push origin feature/ma-nouvelle-feature
```

### 4. Standards de code

#### TypeScript / React

```typescript
// ✅ Bon
interface Transaction {
  id: number;
  description: string;
  amount: number;
}

export function TransactionItem({ transaction }: { transaction: Transaction }) {
  const [isEditing, setIsEditing] = useState(false);
  
  const handleEdit = useCallback(() => {
    setIsEditing(true);
  }, []);
  
  return (
    <div className="flex items-center">
      <span>{transaction.description}</span>
    </div>
  );
}

// ❌ Mauvais
function TransactionItem(props) {
  var editing = false;
  return <div>{props.transaction.description}</div>;
}
```

#### Nommage

- **Composants** : PascalCase (`TransactionItem.tsx`)
- **Hooks** : camelCase avec prefix `use` (`useTransactions.ts`)
- **Utilitaires** : camelCase (`formatCurrency.ts`)
- **Types/Interfaces** : PascalCase (`Transaction`, `MemberData`)

#### Styles

Utiliser Tailwind CSS avec les conventions du projet :

```tsx
// ✅ Bon
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm">
  <span className="text-sm font-medium text-gray-900">Label</span>
</div>

// Utiliser les composants shadcn/ui quand disponibles
import { Button } from '@/components/ui/button';
<Button variant="outline" size="sm">Cliquer</Button>
```

### 5. Tests

Toute nouvelle fonctionnalité doit avoir des tests E2E :

```typescript
// tests/e2e/m Feature.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Ma Feature', () => {
  test('devrait fonctionner correctement', async ({ page }) => {
    await page.goto('/ma-feature');
    await expect(page.getByText('Titre')).toBeVisible();
    
    // Actions...
    await page.click('button');
    
    // Assertions
    await expect(page.getByText('Résultat')).toBeVisible();
  });
});
```

### 6. Messages de commit

Format : `type(scope): description`

Types :
- `feat` - Nouvelle fonctionnalité
- `fix` - Correction de bug
- `docs` - Documentation
- `style` - Formatage (pas de changement de code)
- `refactor` - Refactoring
- `test` - Tests
- `chore` - Maintenance

Exemples :
```
feat(budgets): ajoute les alertes de dépassement
fix(import): corrige la détection du séparateur CSV
docs(readme): met à jour les instructions d'installation
test(members): ajoute les tests E2E multi-membres
```

## 🎨 Design System

### Couleurs

```css
/* Primaire */
--primary-50: #ecfdf5;
--primary-500: #10b981;  /* Emerald */
--primary-600: #059669;

/* Semantic */
--success: #22c55e;
--warning: #f59e0b;
--error: #ef4444;

/* Membres */
--member-primary: #8b5cf6;   /* Violet */
--member-secondary: #06b6d4; /* Cyan */
```

### Composants UI

Utiliser les composants existants dans `src/components/ui/` :

- `Button` - Boutons avec variants
- `Card` - Conteneurs
- `Dialog` - Modals
- `Input` - Champs texte
- `Select` - Dropdowns
- `Badge` - Badges de statut
- `Progress` - Barres de progression

## 🐛 Signaler un bug

Utilisez les GitHub Issues avec ce format :

```markdown
**Description**
Description claire du bug

**Reproduction**
1. Aller à '...'
2. Cliquer sur '...'
3. Voir l'erreur

**Comportement attendu**
Ce qui devrait se passer

**Screenshots**
Si applicable

**Environnement**
- OS: [ex: macOS 14]
- Version: [ex: 1.0.0]
- Node: [ex: 20.11.0]
```

## 💡 Proposer une fonctionnalité

GitHub Issues avec label `enhancement` :

```markdown
**Description**
Description de la fonctionnalité

**Use case**
Pourquoi cette fonctionnalité est utile

**Proposition**
Comment l'implémenter (optionnel)

**Alternatives**
Autres solutions envisagées (optionnel)
```

## 🔒 Sécurité

Ne commitez jamais :
- Clés API en dur
- Fichiers `.env` avec secrets
- Données personnelles de test

Utilisez plutôt :
```typescript
// ✅ Bon
const apiKey = process.env.API_KEY;

// ❌ Mauvais
const apiKey = 'sk-1234567890abcdef';
```

## 📞 Contact

- Issues GitHub : [github.com/votre-username/financeperso-electron/issues](https://github.com/votre-username/financeperso-electron/issues)
- Email : votre-email@example.com

Merci pour votre contribution ! 🎉
