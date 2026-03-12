# 📥 Import de Transactions

Ce guide explique comment importer vos transactions bancaires dans FinancePerso.

---

## 📄 Formats Supportés

| Format | Extension | Description | Documentation |
|--------|-----------|-------------|---------------|
| **CSV** | `.csv` | Format universel | ⭐ Recommandé |
| **QIF** | `.qif` | Quicken Interchange Format | ✅ Supporté |
| **OFX** | `.ofx` | Open Financial Exchange | ✅ Supporté |
| **JSON** | `.json` | Export FinancePerso | ✅ Supporté |

---

## 📊 Import CSV

### Format attendu

Votre CSV doit contenir au minimum ces colonnes :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `date` | Date de la transaction | `2024-01-15` |
| `label` | Libellé / description | `SUPER U PARIS` |
| `amount` | Montant (négatif pour dépenses) | `-45.67` ou `2500.00` |

### Exemple de fichier CSV

```csv
date,label,amount,category
2024-01-15,SUPER U PARIS,-45.67,Alimentation
2024-01-14,SALAIRE JANVIER,2500.00,Revenus
2024-01-13,PHARMACIE CENTRALE,-23.50,Santé
2024-01-12,TOTAL STATION,-60.00,Transport
```

### Import pas à pas

1. **Accéder à la page Import**
   - Cliquez sur **Import** dans le menu latéral

2. **Télécharger le fichier**
   - Glissez-déposez votre fichier CSV
   - Ou cliquez pour sélectionner

3. **Mapper les colonnes**
   - Associez chaque colonne CSV au champ correspondant
   - Date → `date`
   - Libellé → `label`
   - Montant → `amount`

4. **Lancer l'import**
   - Cliquez sur **Importer**
   - Attendez la confirmation

---

## 🚀 Import Massif (10 000+ transactions)

Pour importer un grand volume de transactions :

### Prérequis

- Fichier CSV avec un en-tête
- Encodage UTF-8 recommandé

### Procédure

1. Allez dans **Configuration > Import Massif**
   
2. **Configuration avancée**
   - Taille des batchs : 1000 transactions (par défaut)
   - Workers parallèles : 4 (par défaut)
   - Mode simulation : testez d'abord

3. **Lancer l'import**
   ```
   Temps estimé : ~30 secondes pour 10 000 transactions
   ```

4. **Suivi en temps réel**
   - Barre de progression
   - Nombre de transactions importées
   - Doublons détectés
   - Erreurs éventuelles

---

## 🏦 Import depuis Open Banking

Si vous avez connecté vos comptes bancaires :

### Synchronisation automatique

1. Allez dans **Comptes Bancaires** 🏦
2. Cliquez sur **Synchroniser**
3. Les transactions sont importées automatiquement

> 📚 Voir le guide [Open Banking](../banking.md)

---

## 🔄 Import depuis d'autres outils

### Migration depuis Bankin' / Linxo

1. Exportez vos données au format CSV depuis Bankin'
2. Dans FinancePerso, allez dans **Configuration > Migration**
3. Sélectionnez **Bankin'**
4. Téléchargez votre export
5. Suivez les instructions

### Migration depuis YNAB

1. Export depuis YNAB (CSV)
2. Dans FinancePerso : **Configuration > Migration > YNAB**
3. Mappez les catégories YNAB vers FinancePerso
4. Importez

---

## 🛠️ Dépannage

### Problème : "Format de date non reconnu"

**Cause** : La date n'est pas au format attendu

**Solutions** :
- Convertissez en `YYYY-MM-DD` avant import
- Ou utilisez le mapping avancé pour spécifier le format

### Problème : "Montant invalide"

**Cause** : Format numérique incorrect

**Solutions** :
- Utilisez le point comme séparateur décimal : `45.67`
- Pas de symboles monétaires (€, $)
- Pas d'espaces dans les nombres

### Problème : "Doublons détectés"

**Cause** : Transactions déjà importées

**Comportement** :
- Le système détecte automatiquement les doublons
- Les doublons sont ignorés
- Vérifiez dans **Validation** si nécessaire

### Problème : Caractères spéciaux illisibles

**Cause** : Mauvais encodage

**Solution** :
```bash
# Convertir en UTF-8 avec iconv
iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv
```

---

## 📈 Performances

| Nombre de transactions | Temps estimé |
|------------------------|--------------|
| 100 | < 1 seconde |
| 1 000 | ~3 secondes |
| 10 000 | ~30 secondes |
| 50 000 | ~2 minutes |

---

**Prochaine étape** : ✅ [Guide de validation](validation.md)
