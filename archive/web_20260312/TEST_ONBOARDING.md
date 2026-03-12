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

**Étape 1: Page d'accueille**
- [ ] Vérifier que l'écran "Bienvenue sur FinancePerso" s'affiche
- [ ] Cliquer sur "Commencer"

**Étape 2: Création du foyer**
- [ ] Saisir un nom de foyer (ex: "Notre Foyer")
- [ ] Cliquer sur "Continuer"

**Étape 3: Ajout de membres**
- [ ] Vérifier que "Moi" est présent (connecté par défaut)
- [ ] Vérifier l'explication : "Actif = se connecte à l'app"
- [ ] Ajouter un partenaire actif (ex: "Marie") - pourra se connecter
- [ ] Ajouter un membre non-actif (ex: "Bébé") - participe aux dépenses mais ne se connecte pas
- [ ] Tester le toggle pour passer un membre en "Hors-ligne"
- [ ] Cliquer sur "Continuer"

**Étape 4: Ajout d'un compte bancaire**
- [ ] Vérifier le toggle "Compte commun (joint)" - activé par défaut
- [ ] Nom du compte: "Compte Courant"
- [ ] Banque: "Boursorama"
- [ ] Type: "Compte commun"
- [ ] Cliquer sur "Ajouter le compte"
- [ ] Cliquer sur "Continuer"

**Étape 5: Import de transactions**
- [ ] Option A: Cliquer sur "Passer cette étape"

**Résultat attendu:**
- [ ] Redirection vers le Dashboard

## 📖 Explication Actif vs Non-Actif (CORRECTE)

### 👤 Actif (bouton vert "Connecté")
- **Se connecte** à l'application avec un email/mot de passe
- **Exemples** : vous, votre partenaire, un colocataire
- **Peut** : voir toutes les transactions, ajouter des dépenses, configurer

### 🚫 Non-Actif (bouton gris "Hors-ligne")  
- **Participe** aux dépenses mais **ne se connecte pas**
- **Exemples** : bébé/enfant (dépenses puériculture), animal de compagnie (vétérinaire), voiture (essence/entretien)
- **Usage** : permet de catégoriser les dépenses sans créer de compte utilisateur

**Cas d'usage typique :**
- 👤 Vous (Actif)
- 👤 Partenaire (Actif) 
- 🚫 Bébé (Non-actif) - pour les dépenses bébé sans que bébé ait un compte 😉
- 🚫 Chien (Non-actif) - pour les frais vétérinaire

## ✅ Validation

| Étape | Status |
|-------|--------|
| "Moi" présent par défaut | ⬜ |
| Explication correcte Actif/Non-actif | ⬜ |
| Ajout membre actif (connecté) | ⬜ |
| Ajout membre non-actif (hors-ligne) | ⬜ |
| Toggle fonctionne | ⬜ |
| Dashboard affiché | ⬜ |

**Date de test:** _____
**Testeur:** _____
**Résultat:** ⬜ PASS / ⬜ FAIL
