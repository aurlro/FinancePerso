# Guide Utilisateur FinancePerso

## 📱 Interface

### Navigation

L'application comporte 7 sections principales :

1. **📊 Dashboard** - Vue d'ensemble de vos finances
2. **💳 Transactions** - Liste et recherche des transactions
3. **📁 Catégories** - Gestion des catégories de dépenses
4. **📥 Import** - Import de relevés bancaires
5. **✅ Validation** - Catégorisation rapide
6. **🎯 Budgets** - Suivi budgétaire
7. **👥 Membres** - Gestion multi-utilisateurs
8. **⚙️ Paramètres** - Configuration

### Recherche rapide (Cmd+K)

Appuyez sur `Cmd+K` (Mac) ou `Ctrl+K` (Windows/Linux) pour ouvrir la recherche globale :
- Recherchez des transactions
- Accédez rapidement aux pages
- Exécutez des actions

## 📊 Dashboard

Le dashboard affiche :
- **3 KPIs** : Revenus, Dépenses, Solde du mois
- **Graphique des tendances** : Évolution sur 6 mois
- **Graphique de répartition** : Dépenses par catégorie
- **Détail par catégorie** : Liste des dépenses

## 📥 Import CSV

### Préparer son fichier

Votre fichier CSV doit contenir :
- **Date** : JJ/MM/AAAA ou AAAA-MM-JJ
- **Description** : Libellé de la transaction
- **Montant** : Nombre (négatif pour dépenses, positif pour revenus)
- **Catégorie** (optionnel)

### Exemple

```csv
Date;Description;Montant
13/03/2025;CARREFOUR;-45.67
12/03/2025;SALAIRE;2500.00
10/03/2025;TOTAL STATION;-65.00
```

### Importer

1. Allez dans **Import**
2. Sélectionnez votre fichier
3. Choisissez le séparateur (; par défaut)
4. Vérifiez le preview
5. Cliquez sur **Importer**

Les doublons (même date + description + montant) sont automatiquement ignorés.

## ✅ Validation

Après l'import, validez vos transactions :

1. Allez dans **Validation**
2. Les transactions sont groupées par description similaire
3. Sélectionnez une catégorie pour chaque groupe
4. Cliquez sur **Valider tout**

**Astuce** : Utilisez l'IA pour catégoriser automatiquement !

## 🎯 Budgets

### Créer un budget

1. Allez dans **Budgets**
2. Cliquez sur **Ajouter un budget**
3. Sélectionnez une catégorie
4. Définissez le montant mensuel
5. Sauvegardez

### Suivi

La barre de progression indique :
- 🟢 **Vert** : < 80% du budget
- 🟠 **Orange** : 80% - 100% du budget
- 🔴 **Rouge** : > 100% du budget

## 👥 Multi-membres

### Ajouter un membre

1. Allez dans **Membres**
2. Cliquez sur **Ajouter**
3. Nom, emoji, couleur
4. Sauvegardez

### Assigner une transaction

Dans la liste des transactions :
1. Cliquez sur la colonne "Membre"
2. Sélectionnez qui a fait cette dépense

Le dashboard montre la répartition par membre.

## 🤖 Intelligence Artificielle

### Configuration

1. Allez dans **Paramètres** > **Intelligence Artificielle**
2. Choisissez votre provider :
   - **Gemini** (gratuit, recommandé)
   - **OpenAI** (payant, plus précis)
   - **Local** (sans API, règles simples)
3. Entrez votre clé API (si Gemini/OpenAI)
4. Testez la connexion
5. Activez "Catégorisation automatique"

### Clé API Gemini (Gratuit)

1. Allez sur [makersuite.google.com](https://makersuite.google.com)
2. Connectez-vous avec votre compte Google
3. Créez une clé API
4. Copiez-la dans les paramètres FinancePerso

Votre clé reste stockée localement sur votre ordinateur.

## 🔄 Mises à jour

L'application vérifie automatiquement les mises à jour.

Pour vérifier manuellement :
1. Allez dans **Paramètres**
2. Section **Mises à jour**
3. Cliquez sur **Vérifier**

## ❓ FAQ

**Q : Mes données sont-elles sécurisées ?**  
R : Oui, tout reste sur votre ordinateur dans une base SQLite locale. Vos clés API ne sont jamais envoyées ailleurs que vers les services choisis.

**Q : Puis-je utiliser l'application hors ligne ?**  
R : Oui, l'application fonctionne 100% offline. Seules les fonctionnalités IA nécessitent internet.

**Q : Comment sauvegarder mes données ?**  
R : La base de données est dans `~/Library/Application Support/Electron/finance.db` (macOS) ou équivalent. Copiez ce fichier pour sauvegarder.

**Q : Puis-je importer depuis mon bank ?**  
R : Oui, exportez un CSV depuis votre banque et importez-le. Les formats courants sont détectés automatiquement.

**Q : L'application est-elle gratuite ?**  
R : Oui, et open source ! Vous pouvez même héberger vous-même.

## 🆘 Support

- **GitHub Issues** : Signaler un bug ou proposer une fonctionnalité
- **Email** : support@financeperso.app

---

*Dernière mise à jour : Mars 2025*
