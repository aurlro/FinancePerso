# ✅ Validation et Catégorisation

Ce guide explique comment valider et catégoriser vos transactions importées.

---

## 🤔 Pourquoi valider ?

La validation permet de :

- ✅ **Vérifier** la catégorisation automatique
- ✅ **Corriger** les erreurs
- ✅ **Apprendre** au système vos préférences
- ✅ **Améliorer** la précision future

> 💡 Plus vous validez, plus la catégorisation devient précise !

---

## 📋 Processus de Validation

### 1. Accéder aux transactions

1. Cliquez sur **Validation** dans le menu latéral
2. Les transactions non validées s'affichent

### 2. Vue par groupe (recommandé)

Les transactions sont groupées automatiquement :
- **Même libellé** (ex: "SUPER U")
- **Même montant**
- **Même période**

> 💡 Cette vue permet de valider 10 transactions en 1 clic !

### 3. Actions disponibles

Pour chaque groupe ou transaction :

| Action | Icône | Description |
|--------|-------|-------------|
| **Valider** | ✅ | Confirme la catégorie proposée |
| **Modifier** | ✏️ | Change la catégorie |
| **Membre** | 👤 | Attribue à un autre membre (mode couple) |
| **Tags** | 🏷️ | Ajoute des labels personnalisés |
| **Éditer** | 📝 | Modifie les détails (date, montant) |
| **Ignorer** | 🗑️ | Supprime la transaction |

---

## 🧠 Comment fonctionne la catégorisation ?

Le système utilise une **cascade intelligente** :

### Priorité 1 : Vos règles exactes
```
Si libellé contient "SUPER U" → Catégorie "Alimentation"
```
> Basé sur vos corrections précédentes

### Priorité 2 : Règles partielles
```
Si libellé contient "PHARMACIE" → Catégorie "Santé"
```
> Pattern matching sur les mots-clés

### Priorité 3 : Intelligence Artificielle
```
Libellé : "STARBUCKS PARIS 15"
IA détecte : Café/Restaurant
```
> Utilise Gemini/OpenAI (si configuré)

### Priorité 4 : Machine Learning Local
```
Modèle entraîné sur vos transactions passées
```
> Fonctionne 100% offline

### Priorité 5 : Catégorie par défaut
```
"Inconnu" ou "Divers"
```
> Quand aucune autre méthode ne fonctionne

---

## 🏷️ Utiliser les Tags

Les tags permettent de grouper transversalement :

### Exemples de tags utiles

| Tag | Utilisation |
|-----|-------------|
| `#vacances-2024` | Dépenses de vacances |
| `#remboursable` | Dépenses à rembourser |
| `#pro` | Dépenses professionnelles |
| `#famille` | Dépenses familiales |
| `#urgent` | À traiter en priorité |

### Comment ajouter des tags

1. En validation, cliquez sur 🏷️ **Tags**
2. Sélectionnez un tag existant ou créez-en un
3. Les tags apparaissent dans les filtres

---

## ⚡ Validation rapide (Mode expert)

### Raccourcis clavier

| Touche | Action |
|--------|--------|
| `↑` `↓` | Naviguer entre transactions |
| `←` `→` | Changer de groupe |
| `Enter` | Valider |
| `Space` | Sélectionner |
| `c` | Changer catégorie |
| `m` | Changer membre |
| `t` | Ajouter tag |
| `s` | Ignorer transaction |

### Validation par lot

1. **Sélectionnez** plusieurs transactions (Ctrl+Click)
2. **Choisissez** l'action en haut de page
3. **Appliquez** à toutes les sélectionnées

---

## 📊 Mode Avancé

Activez le mode avancé dans **Configuration > Préférences** :

### Fonctionnalités supplémentaires

- **Scores de confiance** : Voir le % de certitude de l'IA
- **Règles actives** : Voir quelle règle a été appliquée
- **Conflits** : Détecter les règles contradictoires
- **Historique** : Voir les modifications passées

---

## 🎯 Workflow recommandé

### Quotidien (5 minutes)

1. Importez vos nouvelles transactions
2. Validez les transactions du jour
3. Corrigez si nécessaire

### Hebdomadaire (15 minutes)

1. Passez en revue toutes les transactions de la semaine
2. Vérifiez les catégories "Inconnu"
3. Créez de nouvelles règles pour les patterns récurrents

### Mensuel (30 minutes)

1. Revue complète du mois
2. Analyse des budgets
3. Ajustement des catégories si besoin

---

## 🛠️ Gestion des Règles

### Créer une règle manuelle

1. Allez dans **Configuration > Règles**
2. Cliquez sur **Nouvelle règle**
3. Définissez :
   - **Pattern** : mot-clé à détecter (ex: "NETFLIX")
   - **Catégorie** : destination (ex: "Abonnements")
   - **Priorité** : 1 (haute) à 10 (basse)

### Exemples de règles efficaces

| Pattern | Catégorie | Priorité |
|---------|-----------|----------|
| `NETFLIX` | Abonnements | 1 |
| `SPOTIFY` | Abonnements | 1 |
| `PHARMACIE` | Santé | 2 |
| `SALAIRE` | Revenus | 1 |
| `VIREMENT` | Transferts | 5 |

---

**Prochaine étape** : 📊 [Guide du dashboard](dashboard.md)
