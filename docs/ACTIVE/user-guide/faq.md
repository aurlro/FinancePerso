# ❓ FAQ - Questions Fréquentes

## Général

### Qu'est-ce que FinancePerso ?

FinancePerso est une application de gestion financière personnelle qui vous aide à :
- 📥 Importer automatiquement vos transactions
- 🏷️ Catégoriser vos dépenses
- 💰 Suivre vos budgets
- 📊 Analyser vos finances

### Mes données sont-elles sécurisées ?

**Oui !** Toutes vos données :
- ✅ Sont stockées **localement** (SQLite sur votre machine)
- ✅ Peuvent être **chiffrées** (AES-256)
- ✅ Ne quittent **jamais** votre machine (sauf si vous activez l'IA cloud)
- ✅ Vous en êtes le **propriétaire unique**

### Puis-je utiliser FinancePerso hors ligne ?

**Oui, entièrement !** 

L'application fonctionne 100% offline. Seules les fonctionnalités IA cloud nécessitent internet (et elles sont optionnelles).

---

## Import

### Quelles banques sont supportées ?

Toutes les banques exportant en **CSV**, **QIF** ou **OFX** :

| Banque | Format | Méthode |
|--------|--------|---------|
| BNP Paribas | CSV | Export web |
| Crédit Mutuel | CSV | Export web |
| Société Générale | CSV | Export web |
| Banque Postale | CSV | Export web |
| Crédit Agricole | CSV | Export web |
| Hello bank! | CSV | Export web |
| N26 | CSV | Export app |
| Revolut | CSV | Export app |

### Puis-je importer plusieurs années d'historique ?

**Oui !** Utilisez la fonction **Import Massif** :
- Jusqu'à 50 000 transactions
- ~30 secondes pour 10 000 transactions
- Détection automatique des doublons

### Qu'est-ce que le mode Open Banking ?

C'est une connexion **directe** à votre banque via API :
- 🔄 Synchronisation automatique
- 🏦 Plus besoin d'importer manuellement
- 🔒 Sécurisé (PSD2)

> Disponible pour certaines banques uniquement

---

## Fonctionnalités

### Comment fonctionne la catégorisation automatique ?

Le système utilise une **cascade intelligente** :

```
1. Vos règles personnalisées
2. Pattern matching (libellés)
3. Intelligence artificielle (optionnel)
4. Machine Learning local
5. Catégorie par défaut
```

**Précision** : Augmente avec le temps à mesure que vous corrigez !

### Puis-je créer mes propres catégories ?

**Oui, illimité !**

1. Allez dans **Configuration > Catégories**
2. Cliquez sur **Nouvelle catégorie**
3. Choisissez un emoji et une couleur

### Qu'est-ce que le mode couple ?

Le mode couple permet de :
- 👥 Gérer un budget partagé
- 📊 Attribuer les dépenses par membre
- 💶 Suivre les dettes entre vous
- 🎯 Définir des objectifs communs

### Comment fonctionnent les budgets ?

1. **Créez** un budget par catégorie (ex: 300€ pour Alimentation)
2. **Suivez** vos dépenses en temps réel
3. **Recevez** des alertes à 80% et 100%
4. **Ajustez** mensuellement

---

## Problèmes Techniques

### L'application ne démarre pas

**Diagnostic** :
```bash
# 1. Vérifier Python
python --version  # Doit être 3.11+

# 2. Vérifier les dépendances
pip install -r requirements.txt

# 3. Lancer le doctor
python scripts/doctor.py
```

### Erreur "Module not found"

**Solution** :
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall

# Vérifier l'environnement
which python
pip list | grep streamlit
```

### Problèmes de performance (lent)

**Solutions** :

1. **Vider le cache**
   - Configuration > Maintenance > Vider le cache

2. **Optimiser la base**
   - Configuration > Outils avancés > Optimiser

3. **Réduire l'historique**
   - Ne charger que les 12 derniers mois

4. **Augmenter la mémoire**
   - Fermer les autres applications

### Erreur "Database is locked"

**Cause** : Plusieurs instances ouvertes

**Solution** :
```bash
# Trouver et tuer les processus
pkill -f "streamlit"

# Ou redémarrer l'ordinateur
```

### Les graphiques ne s'affichent pas

**Cause** : Problème avec Plotly

**Solution** :
```bash
pip install --upgrade plotly
```

---

## Intelligence Artificielle

### L'IA est-elle obligatoire ?

**Non !** L'IA est **optionnelle** :

| Fonctionnalité | Sans IA | Avec IA |
|----------------|---------|---------|
| Import CSV | ✅ | ✅ |
| Catégorisation | ✅ Basique | ✅ Améliorée |
| Prédictions | ❌ | ✅ |
| Anomalies | ❌ | ✅ |

### Quelles sont les options d'IA ?

| Provider | Coût | Offline | Qualité |
|----------|------|---------|---------|
| **Gemini** | Gratuit | ❌ | ⭐⭐⭐ |
| **Ollama** | Gratuit | ✅ | ⭐⭐ |
| **OpenAI** | Payant | ❌ | ⭐⭐⭐⭐ |
| **DeepSeek** | Bon marché | ❌ | ⭐⭐⭐ |

### Comment configurer l'IA ?

1. Obtenez une clé API (Gemini est gratuit)
2. Ajoutez-la dans `.env` :
   ```
   GEMINI_API_KEY=votre_cle
   AI_PROVIDER=gemini
   ```
3. Redémarrez l'application

---

## Compte & Données

### Comment sauvegarder mes données ?

**Automatique** :
- Sauvegardes quotidiennes dans `Data/backups/`

**Manuel** :
1. Allez dans **Configuration > Sauvegardes**
2. Cliquez sur **Créer une sauvegarde**
3. Téléchargez le fichier `.db`

### Comment exporter mes données ?

**Format CSV** :
- Transactions > Export > CSV

**Format JSON** (complet) :
- Configuration > Export complet

**Format Excel** :
- Dashboard > Exporter vers Excel

### Puis-je utiliser FinancePerso sur plusieurs ordinateurs ?

**Oui**, avec synchronisation :

1. **Cloud** : Mettez la base SQLite sur Dropbox/Google Drive
2. **Git** : Versionnez avec git (données chiffrées)
3. **NAS** : Stockez sur un serveur local

### Comment supprimer toutes mes données ?

```bash
# Supprimer la base de données
rm Data/finance.db

# Ou via l'interface
# Configuration > Outils avancés > Réinitialiser
```

---

## Contribution

### Puis-je contribuer au projet ?

**Oui !** Voir [CONTRIBUTING.md](../../../CONTRIBUTING.md)

### Comment signaler un bug ?

Créez une issue GitHub avec :
- 🏷️ Version de FinancePerso
- 💻 Système d'exploitation
- 📝 Description détaillée
- 🔄 Étapes de reproduction
- 📸 Capture d'écran si possible

### Comment suggérer une fonctionnalité ?

1. Vérifiez si elle n'existe pas déjà
2. Créez une issue avec le label "enhancement"
3. Décrivez le use case

---

## Questions diverses

### FinancePerso est-il gratuit ?

**Oui, 100% gratuit et open-source !**

- Pas de frais cachés
- Pas d'abonnement
- Pas de publicités

### Puis-je utiliser FinancePerso pour mon entreprise ?

**Oui**, sous licence MIT. 

> Note : FinancePerso est optimisé pour la gestion personnelle, pas professionnelle.

### Existe-t-il une application mobile ?

**Pas encore native**, mais :
- ✅ Site web responsive (fonctionne sur mobile)
- ✅ PWA (Progressive Web App) installable
- 🔄 App native en développement (v7.0)

### Comment puis-je soutenir le projet ?

- ⭐ Star le repo GitHub
- 🐛 Signaler les bugs
- 💡 Proposer des améliorations
- 📝 Améliorer la documentation
- 💰 Faire un don (si option disponible)

---

**Vous ne trouvez pas votre réponse ?**

- 📖 Consultez la [documentation complète](../README.md)
- 💬 Rejoignez la communauté Discord (si disponible)
- 📧 Contactez l'équipe
