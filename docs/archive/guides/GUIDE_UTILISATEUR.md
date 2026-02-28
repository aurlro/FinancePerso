# 🚀 Guide Utilisateur - FinancePerso

> Comment utiliser l'app au quotidien en 5 minutes

---

## 📱 Démarrage rapide

### Lancer l'application
```bash
# Terminal
cd FinancePerso && streamlit run app.py

# Ou double-clique sur : Lancer_App.command
```

L'app s'ouvre dans ton navigateur à `http://localhost:8501`

### 🎯 Guide de démarrage

La première fois, une **pop-up de configuration** s'affiche automatiquement. Elle te guide en 4 étapes :

1. **👋 Bienvenue** - Présentation de l'app
2. **👥 Membres** - Ajoute les utilisateurs (toi, ta famille...)
3. **🏷️ Catégories** - Choisis tes catégories de dépenses
4. **⚡ Paramètres optionnels** - IA et notifications

💡 **Tu peux réouvrir ce guide à tout moment** via le bouton "🎯 Revoir le guide" sur la page d'accueil.

---

## 🔄 Flux quotidien (3 étapes)

### 1️⃣ Import (Page "📥 Import")

**Quand ?** Une fois par semaine/mois quand tu as ton relevé bancaire

**Comment :**
1. Sélectionne ton format :
   - **BoursoBank** → laisse "BoursoBank (Auto)"
   - **Autre banque** → choisis "Autre" et configure le séparateur (; ou ,)
2. Glisse-dépose ton fichier CSV
3. Choisis l'**année** et le **mois** (par défaut : année en cours)
4. Sélectionne ou crée le **compte** (Perso / Joint / etc.)
5. Clique sur **"🚀 Valider et Importer"**

💡 **Astuce :** L'app détecte automatiquement les doublons. Si tout est déjà importé, elle te le dira.

---

### 2️⃣ Validation (Page "✅ Validation")

**Quand ?** Juste après l'import, ou quand tu veux catégoriser

**Comment :**

Pour chaque groupe de transactions :
1. **Catégorie** : sélectionne dans la liste (avec emoji 🏷️)
2. **Qui a payé ?** : choisis le membre (Aurélien, Élise, Duo...)
3. **Pour qui ?** : 
   - "Famille" (par défaut)
   - "Maison" (charges du foyer)
   - ou un membre spécifique
4. **Tags** (optionnel) : clique sur les boutons rapides ou crées-en un
5. Clique **"Valider"** (bouton vert ✅)

**Raccourcis rapides :**
- **Validation externe** : clique sur ✅ à droite du groupe (sans ouvrir)
- **Validation en masse** : coche plusieurs groupes → "Appliquer" en haut
- **Annuler** : bouton "🔙" en haut à droite → "Confirmer l'annulation"

💡 **Astuce pour les chèques :** Quand tu valides un chèque, un champ "Nature" apparaît automatiquement. Décris l'usage → un tag `chèque-{nature}` sera créé.

---

### 3️⃣ Synthèse (Page "📊 Tableau de bord")

**Quand ?** Quand tu veux voir où va ton argent

**Filtres disponibles (sidebar à gauche) :**
- **Période** : années et mois
- **Comptes** : perso, joint, etc.
- **Membres** : qui a payé
- **Bénéficiaires** : pour qui
- **Tags** : filtre spécifique

**Ce que tu vois :**
- 📊 **KPIs** : Total dépensé, revenus, épargne
- 📈 **Évolution** : courbe sur la période
- 🥧 **Répartition** : camembert par catégorie
- 🏆 **Top dépenses** : les 10 plus gros postes
- 💰 **Budgets** : suivi vs objectifs

💡 **Astuce :** Décoche "Afficher virements internes 🔄" pour ne pas compter les transferts entre tes comptes.

---

## 🎯 Cas particuliers

### Les virements internes
Quand tu transfères entre tes comptes :
1. Catégorie = **"Virement Interne"**
2. Le montant n'apparaîtra pas dans tes dépenses (exclu automatiquement)

### Les remboursements
Si tu vois un "AVOIR" positif :
- Le tag "Remboursement" est ajouté automatiquement
- C'est considéré comme un revenu (positif)

### Les opérations récurrentes
Va sur la page **"🔁 Analyse des Récurrences"** pour voir :
- Tes abonnements détectés (Netflix, Spotify, etc.)
- Tes revenus réguliers (salaire, etc.)
- La balance mensuelle (charges vs revenus)

### Les alertes budget 🔔
Les notifications se déclenchent automatiquement quand :
- Un budget atteint 75% (info)
- Un budget atteint 90% (attention)
- Un budget est dépassé à 100% (alerte critique)

Tu recevras :
- Une **notification desktop** (si activée)
- Un **email** (si configuré)

Configure tes alertes dans **⚙️ Configuration → 🔔 Notifications**

---

## ⚙️ Configuration essentielle (Page "⚙️ Configuration")

### À faire une fois :

**1. Notifications** (tab "🔔 Notifications")
- Active les alertes desktop (notifications natives macOS/Windows/Linux)
- Configure les alertes email (SMTP Gmail ou autre)
- Définis tes seuils d'alerte :
  - 🚨 Dépassement (par défaut: 100%)
  - ⚠️ Attention (par défaut: 90%)
  - ℹ️ Information (par défaut: 75%)

**Test** : Clique sur "Envoyer une notification de test" pour vérifier que tout fonctionne.

**3. Membres du foyer** (tab "🏠 Foyer & Membres")
- Ajoute Aurélien, Élise, etc.
- Définis qui est "household" (membre du foyer) ou "external" (extérieur)
- Configure les cartes (associe un suffixe de CB à un membre)

**4. Catégories** (tab "🏷️ Catégories")
- Crée tes catégories perso
- Ajoute des emojis pour les repérer vite
- Marque les catégories "fixes" (loyer, abonnements...)

**5. Clé API IA** (tab "🔑 API & Services")
- Recommandé : **Gemini** (gratuit) → `GEMINI_API_KEY`
- Alternative : **Ollama** (100% offline)
- Sans clé : l'app fonctionne avec les règles manuelles uniquement

---

## 💡 Tips pour aller plus vite

### Raccourcis clavier
| Action | Raccourci |
|--------|-----------|
| Valider une ligne | Tab → Enter |
| Fermer une notification | Échap |
| Rafraîchir la page | R |

### Automatisation
- **Règles d'apprentissage** : quand tu coches "Mém." lors de la validation, une règle est créée. La prochaine fois, la catégorie sera appliquée auto.
- **Mapping cartes** : configure une fois, les membres sont détectés auto lors de l'import

### Sauvegardes
- Les backups sont automatiques (dans `Data/backups/`)
- Tu peux exporter manuellement via la page Configuration → "💾 Sauvegardes"

---

## 🆘 Problèmes fréquents

| Problème | Solution |
|----------|----------|
| "Aucune transaction trouvée" en import | Vérifie l'année/mois sélectionné |
| Mauvais caractères dans le CSV | Sélectionne le bon séparateur (; ou ,) |
| Transactions en double | Normal, elles sont ignorées auto. Vérifie quand même la période |
| Membre pas détecté | Ajoute un mapping carte dans Configuration |
| Lenteur | Rafraîchis la page (R), ou valide par petits lots |

---

## 📊 Bonnes pratiques

1. **Importe régulièrement** (hebdo ou mensuel) → moins de travail d'un coup
2. **Valide rapidement** → ne laisse pas trainer 200 transactions à valider
3. **Utilise les tags** pour suivre des sujets spécifiques (vacances, travaux...)
4. **Configure les budgets** → tu verras les alertes en temps réel
5. **Vérifie les récurrences** → détecte les abonnements oubliés

---

## 📱 Navigation

La barre latérale gauche te permet d'accéder à toutes les pages :
- 📥 **Import** - Importer des relevés
- ✅ **Validation** - Catégoriser les transactions
- 📊 **Synthèse** - Dashboard et analyses
- 🔁 **Récurrences** - Abonnements et revenus réguliers
- 🧠 **Règles** - Gérer les règles d'apprentissage
- 🧠 **Assistant** - Audit IA et suggestions
- ⚙️ **Configuration** - Paramètres et maintenance

---

**🎉 Tu es prêt ! Lance l'app et importe ton premier relevé.**

Besoin d'aide ? Vérifie la page "📑 Logs" dans Configuration pour voir les erreurs.
