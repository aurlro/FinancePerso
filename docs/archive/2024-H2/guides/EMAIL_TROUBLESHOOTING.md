# 🔧 Guide de Diagnostic - Problèmes d'Email Gmail

Ce guide t'aide à diagnostiquer et résoudre les problèmes d'envoi d'emails avec Gmail.

---

## ✅ Vérifications Préalables

### 1. Configuration dans l'app

Dans **Configuration > Notifications > Email**, vérifie :

| Champ | Valeur attendue |
|-------|----------------|
| Serveur SMTP | `smtp.gmail.com` |
| Port | `587` (STARTTLS) ou `465` (SSL) |
| Email / Utilisateur | Ton adresse Gmail complète |
| Mot de passe | **App Password** de 16 caractères (pas ton mot de passe Gmail!) |
| Destinataire | Optionnel, laisse vide pour recevoir sur le même email |

---

## 🔐 Configuration Gmail Requise

### Étape 1: Activer l'Authentification à 2 Facteurs (OBLIGATOIRE)

1. Va sur https://myaccount.google.com/security
2. Dans "Connexion à Google", clique sur **Vérification en 2 étapes**
3. Active-la (nécessite un téléphone)

> ⚠️ **SANS 2FA, tu ne peux PAS créer d'App Password!**

### Étape 2: Générer un App Password

1. Va sur https://myaccount.google.com/apppasswords
2. Sélectionne **"Mail"** dans le premier dropdown
3. Sélectionne **"Autre (nom personnalisé)"** dans le second
4. Tape : `MyFinance Companion`
5. Clique **Générer**
6. Copie les **16 caractères** (ex: `abcd efgh ijkl mnop`) → colle sans espaces

> 💡 **L'App Password ressemble à**: `xxxx xxxx xxxx xxxx` (4 groupes de 4)

---

## 🧪 Test de Diagnostic

### Test 1: Vérifier la configuration

Dans l'app, clique sur **"📤 Test notification"**.

#### Résultats possibles :

| Message | Signification | Solution |
|---------|--------------|----------|
| ✅ Email OK ! | Tout fonctionne | Aucune action |
| ❌ Authentification échouée | Mauvais App Password | Régénère un App Password |
| ❌ Impossible de se connecter | Port/Serveur incorrect | Vérifie smtp.gmail.com:587 |
| ❌ Configuration incomplète | Champs manquants | Remplis tous les champs |

### Test 2: Script de diagnostic Python

Crée un fichier `test_email.py` à la racine du projet :

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Remplace ces valeurs
SMTP_USER = "ton.email@gmail.com"
SMTP_PASSWORD = "xxxx xxxx xxxx xxxx"  # Ton App Password (sans espaces)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def test_email():
    print(f"🔌 Connexion à {SMTP_SERVER}:{SMTP_PORT}...")
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.set_debuglevel(1)  # Active le debug détaillé
        
        print("📡 EHLO...")
        server.ehlo()
        
        print("🔒 STARTTLS...")
        server.starttls()
        server.ehlo()
        
        print(f"🔑 Login avec {SMTP_USER}...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = SMTP_USER
        msg['Subject'] = 'Test MyFinance'
        msg.attach(MIMEText('Ceci est un test!', 'plain'))
        
        print("📤 Envoi...")
        server.send_message(msg)
        
        print("✅ Email envoyé avec succès!")
        server.quit()
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Erreur d'authentification: {e}")
        print("💡 Vérifie que tu utilises un App Password (pas ton mot de passe Gmail)")
        print("💡 Vérifie que la 2FA est activée sur ton compte")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_email()
```

**Exécute :**
```bash
cd /Users/aurelien/Documents/Projets/FinancePerso
python test_email.py
```

---

## 🚨 Erreurs Courantes

### Erreur 1: "Username and Password not accepted"

**Cause**: Tu utilises ton mot de passe Gmail au lieu de l'App Password

**Solution**:
1. Va sur https://myaccount.google.com/apppasswords
2. Génère un nouveau App Password
3. Copie-le exactement (16 caractères sans espaces)

---

### Erreur 2: "Application-specific password required"

**Cause**: L'authentification à 2 facteurs n'est pas activée

**Solution**:
1. Active la 2FA: https://myaccount.google.com/signinoptions/two-step-verification
2. Puis génère un App Password

---

### Erreur 3: "Connection refused" ou timeout

**Cause**: Port SMTP bloqué ou mauvais serveur

**Solution**:
- Vérifie que tu es sur `smtp.gmail.com` (pas gmail.com)
- Essaie le port `587` avec STARTTLS (recommandé)
- OU essaie le port `465` avec SSL

---

### Erreur 4: "5.7.8 Username and Password not accepted" avec App Password valide

**Cause**: L'accès aux applications moins sécurisées ou une sécurité renforcée

**Solution**:
1. Va sur https://myaccount.google.com/lesssecureapps
2. Vérifie que c'est désactivé (ce qui est normal avec 2FA)
3. Essaie de te connecter depuis l'app puis vérifie tes emails Gmail pour une alerte de sécurité
4. Clique sur "C'était bien moi" dans l'email de Google

---

## 🔍 Debug dans l'application

### Activer les logs détaillés

Dans `modules/notifications.py`, modifie la fonction `test_notification_settings` :

```python
server.set_debuglevel(1)  # Change de 0 à 1
```

Puis relance le test dans l'app.

### Vérifier les logs

Les logs sont dans `logs/app.log` :

```bash
tail -f logs/app.log | grep -i "smtp\|email\|notification"
```

---

## ✅ Checklist Finale

Avant de demander de l'aide, vérifie :

- [ ] J'ai activé la 2FA sur mon compte Google
- [ ] J'ai généré un App Password (16 caractères)
- [ ] J'ai copié l'App Password SANS les espaces
- [ ] Le serveur est bien `smtp.gmail.com`
- [ ] Le port est bien `587`
- [ ] Mon email est complet (avec @gmail.com)
- [ ] J'ai cliqué sur "Sauvegarder" avant "Test notification"
- [ ] J'ai vérifié mes spams dans Gmail

---

## 🆘 Si rien ne marche

### Option 1: Utiliser un autre provider

| Provider | Serveur | Port |
|----------|---------|------|
| Outlook/Hotmail | smtp-mail.outlook.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |
| iCloud | smtp.mail.me.com | 587 |

### Option 2: Désactiver temporairement

Si tu n'arrives vraiment pas à faire fonctionner les emails, tu peux :
1. Utiliser uniquement les **notifications desktop** (qui fonctionnent sans configuration)
2. Vérifier l'app manuellement régulièrement

### Option 3: Me contacter

Si après tout ça ça ne marche toujours pas :
1. Exécute le script `test_email.py` ci-dessus
2. Copie les messages d'erreur complets
3. Vérifie que tu as bien suivi toutes les étapes

---

**Note**: Gmail est parfois restrictif. L'App Password est la SEULE méthode fiable avec un compte Gmail moderne (avec 2FA).
