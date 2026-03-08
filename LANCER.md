# 🚀 Guide de Lancement - MyFinance Companion

## Démarrage Rapide (Recommandé)

### macOS / Linux

```bash
# 1. Cloner ou naviguer vers le projet
cd /Users/aurelien/Documents/Projets/FinancePerso

# 2. Lancer l'application (double-clic sur MyFinance.command)
./MyFinance.command
```

### Windows

```powershell
# 1. Ouvrir PowerShell dans le dossier du projet
cd C:\chemin\vers\FinancePerso

# 2. Créer l'environnement virtuel
python -m venv .venv

# 3. Activer l'environnement
.venv\Scripts\activate

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer
streamlit run app.py
```

---

## 🛠️ Installation Complète

Si c'est votre première installation, exécutez :

```bash
# Rendre le script exécutable et lancer
chmod +x setup.sh
./setup.sh
```

Ce script va :
1. ✅ Vérifier Python 3.11+
2. ✅ Créer l'environnement virtuel (`.venv`)
3. ✅ Installer toutes les dépendances
4. ✅ Créer le fichier `.env`
5. ✅ Initialiser la base de données
6. ✅ Vérifier l'installation

---

## 📋 Prérequis

| Composant | Version | Lien |
|-----------|---------|------|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| (macOS) Homebrew | Dernière | [brew.sh](https://brew.sh) |

### Installation des prérequis

**macOS avec Homebrew :**
```bash
brew install python@3.12
```

**Ubuntu/Debian :**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

---

## 🎯 Options de Lancement

### Lancement Standard
```bash
./MyFinance.command
```

### Avec Réinstallation
```bash
./MyFinance.command --reset
```

### Exécuter les Tests
```bash
./MyFinance.command --test
```

### Aide
```bash
./MyFinance.command --help
```

---

## 🔧 Configuration

### 1. Clés API (Recommandé)

Éditez le fichier `.env` :

```bash
# Google Gemini (Gratuit)
GEMINI_API_KEY=votre_cle_ici

# OU DeepSeek (Bon marché)
DEEPSEEK_API_KEY=votre_cle_ici

# OU Ollama (100% Offline)
# Installez Ollama : https://ollama.com
OLLAMA_URL=http://localhost:11434
```

### 2. Chiffrement (Optionnel mais recommandé)

Générez une clé de chiffrement :

```bash
source .venv/bin/activate
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copiez la sortie dans `.env` :
```bash
ENCRYPTION_KEY=votre_cle_generee
```

---

## 🐛 Résolution des Problèmes

### "Permission denied" sur macOS

Si vous obtenez une erreur de permission au premier lancement :

```bash
# Solution 1 : Terminal
xattr -d com.apple.quarantine MyFinance.command

# Solution 2 : Clic droit
# Faites clic droit → Ouvrir → Accepter
```

### "ModuleNotFoundError"

```bash
# Réinstallez les dépendances
source .venv/bin/activate
pip install -r requirements.txt
```

### "Address already in use" (Port occupé)

Le script détecte automatiquement le port occupé et utilise le suivant.
Vous pouvez aussi spécifier manuellement :

```bash
streamlit run app.py --server.port=8502
```

### Base de données corrompue

```bash
# Backup et recréation
cp Data/finance.db Data/finance.db.backup.$(date +%Y%m%d)
rm Data/finance.db
source .venv/bin/activate
python -c "from modules.db.migrations import init_db; init_db()"
```

---

## 📁 Structure du Projet

```
FinancePerso/
├── MyFinance.command    ← 🚀 Script de lancement (MAC/LINUX)
├── setup.sh             ← 🛠️ Installation complète
├── app.py               ← Point d'entrée Streamlit
├── modules/             ← Code métier
│   ├── db/              ← Base de données
│   ├── ui/              ← Interface utilisateur
│   └── ...
├── pages/               ← Pages Streamlit
├── Data/                ← Données (SQLite)
│   └── finance.db
├── .venv/               ← Environnement virtuel
└── requirements.txt     ← Dépendances
```

---

## 🔄 Mise à Jour

Pour mettre à jour l'application après un `git pull` :

```bash
# Option 1 : Relancer le setup
./setup.sh

# Option 2 : Mise à jour rapide
git pull
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📝 Commandes Utiles

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer les tests
make test

# Lancer avec rechargement automatique (développement)
streamlit run app.py

# Lancer en mode production (plus rapide)
streamlit run app.py --server.fileWatcherType=none

# Voir les logs
tail -f logs/app.log
```

---

## 🆘 Support

En cas de problème :

1. Consultez les logs : `logs/app.log`
2. Exécutez les tests : `./MyFinance.command --test`
3. Vérifiez la configuration : `cat .env`
4. Réinstallez : `./setup.sh`

---

**Prêt à gérer vos finances !** 💰
