# Test Onboarding - Guide Complet

## 🚀 Lancement pour Test

### 1. Démarrer l'API (Terminal 1)

```bash
cd /Users/aurelien/Documents/Projets/FinancePerso
source .venv/bin/activate
python web/api/start_api.py
```

### 2. Démarrer le Frontend (Terminal 2)

```bash
cd /Users/aurelien/Documents/Projets/FinancePerso/web/frontend
npm run dev
```

### 3. Ouvrir le navigateur

http://localhost:8081 (ou le port indiqué)

## 📝 Scénario de Test

### Test 1: Onboarding Complet

**Étape 1: Page d'accueil**
- [ ] Vérifier que l'écran "Bienvenue sur FinancePerso" s'affiche
- [ ] Cliquer sur "Commencer"

**Étape 2: Création du foyer**
- [ ] Saisir un nom de foyer (ex: "Notre Foyer")
- [ ] Cliquer sur "Continuer"

**Étape 3: Ajout de membres**
- [ ] Ajouter un premier membre (ex: "Jean")
- [ ] Ajouter un deuxième membre (ex: "Marie")
- [ ] Cliquer sur "Continuer"

**Étape 4: Ajout d'un compte bancaire**
- [ ] Nom du compte: "Compte Courant"
- [ ] Type: "Compte joint"
- [ ] Solde initial: "2500"
- [ ] Cliquer sur "Ajouter le compte"
- [ ] Cliquer sur "Continuer"

**Étape 5: Import de transactions**
- [ ] Option A: Cliquer sur "Passer cette étape" pour l'instant
- [ ] OU Option B: Sélectionner un fichier CSV et tester l'import

**Résultat attendu:**
- [ ] Redirection vers le Dashboard
- [ ] Les stats s'affichent avec les données du compte créé

### Test 2: Revenir au Dashboard après onboarding

1. Rafraîchir la page
2. **Résultat:** Onboarding ne doit PAS réapparaître (localStorage marqué comme complété)

### Test 3: Reset et recommencer

Dans la console du navigateur:
```javascript
localStorage.removeItem('onboarding-completed')
localStorage.removeItem('fp_token')
```

Rafraîchir → L'onboarding doit réapparaître

## 🔧 Dépannage

### Problème: Page blanche

**Vérifier:**
1. L'API tourne sur http://localhost:8000
2. Le frontend tourne sans erreur dans le terminal
3. Console navigateur (F12) sans erreurs rouges

### Problème: Onboarding bloque à une étape

**Console → taper:**
```javascript
// Forcer la complétion
localStorage.setItem('onboarding-completed', 'true')
location.reload()
```

### Problème: Données non sauvegardées

Les données sont stockées en mémoire (mock). Pour persister:
- À l'étape 4, vérifier que le compte apparaît dans la liste
- Sinon, vérifier la console pour les erreurs

## ✅ Validation

| Étape | Status |
|-------|--------|
| Écran Bienvenue | ⬜ |
| Création foyer | ⬜ |
| Ajout membres | ⬜ |
| Ajout compte | ⬜ |
| Skip import | ⬜ |
| Dashboard affiché | ⬜ |

**Date de test:** _____
**Testeur:** _____
**Résultat:** ⬜ PASS / ⬜ FAIL
