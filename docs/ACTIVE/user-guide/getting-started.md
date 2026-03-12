# 🚀 Démarrage Rapide

Bienvenue dans **FinancePerso** ! Ce guide vous aidera à configurer votre application en quelques minutes.

---

## 📋 Prérequis

- **Python** 3.11 ou supérieur
- Un fichier de transactions bancaires (CSV)
- Environ 5 minutes de temps libre

---

## 🛠️ Installation

### 1. Cloner le repository

```bash
git clone https://github.com/votre-repo/FinancePerso.git
cd FinancePerso
```

### 2. Créer l'environnement virtuel

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Éditez `.env` avec vos clés API (optionnel pour démarrer) :

```bash
# Optionnel - pour la catégorisation IA
GEMINI_API_KEY=votre_cle_gemini
```

### 5. Lancer l'application

```bash
make run
# ou
streamlit run app.py
```

🎉 L'application est accessible sur **http://localhost:8501**

---

## 🎯 Première Utilisation

### Étape 1 : Créer vos catégories

1. Allez dans **Configuration** ⚙️
2. Cliquez sur **Catégories**
3. Créez vos catégories personnalisées :
   - 🍽️ Alimentation
   - 🚗 Transport
   - 🏠 Logement
   - 💊 Santé
   - 🎮 Loisirs
   - etc.

> 💡 **Astuce** : Commencez avec 10-15 catégories maximum, vous pourrez en ajouter plus tard.

### Étape 2 : Importer vos transactions

1. Rendez-vous dans **Import** 📥
2. Téléchargez votre fichier CSV bancaire
3. Mappez les colonnes (date, libellé, montant)
4. Cliquez sur **Importer**

> 📚 Voir le [guide d'import complet](import.md)

### Étape 3 : Valider et catégoriser

1. Allez dans **Validation** ✅
2. Vérifiez les catégories proposées
3. Corrigez si nécessaire
4. Validez les transactions

> 📚 Voir le [guide de validation](validation.md)

### Étape 4 : Explorer le dashboard

1. Ouvrez **Dashboard** 📊
2. Découvrez vos statistiques
3. Analysez vos dépenses par catégorie
4. Suivez vos budgets

> 📚 Voir le [guide du dashboard](dashboard.md)

---

## ⌨️ Raccourcis Clavier

FinancePerso supporte la navigation au clavier :

| Raccourci | Action |
|-----------|--------|
| `?` | Afficher l'aide des raccourcis |
| `g` + `i` | Aller à la page Import |
| `g` + `d` | Aller au Dashboard |
| `g` + `v` | Aller à Validation |
| `g` + `b` | Aller aux Budgets |
| `g` + `s` | Aller aux Settings |
| `n` + `t` | Nouvelle transaction |
| `Escape` | Fermer / Annuler |

---

## 🆘 Besoin d'aide ?

- ❓ Consultez la [FAQ](faq.md)
- 📖 Lisez la [documentation complète](../README.md)
- 🐛 Signalez un bug sur GitHub

---

**Prochaine étape recommandée** : 📥 [Guide d'import](import.md)
