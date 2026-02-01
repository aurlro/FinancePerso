#!/usr/bin/env python3
"""
Script de test pour diagnostiquer les problèmes d'email.
Usage: python test_email.py
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# ⚠️ REMPLACE CES VALEURS avec tes vraies informations
# Ou laisse-les vides pour utiliser les variables d'environnement
SMTP_USER = os.getenv('SMTP_USER', "ton.email@gmail.com")
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', "ton-app-password-16-caracteres")
SMTP_SERVER = os.getenv('SMTP_SERVER', "smtp.gmail.com")
SMTP_PORT = int(os.getenv('SMTP_PORT', "587"))


def test_email():
    """Teste la connexion SMTP et l'envoi d'email."""
    
    print("="*60)
    print("🔧 Test de configuration email MyFinance")
    print("="*60)
    
    # Vérifier la configuration
    if SMTP_USER == "ton.email@gmail.com" or not SMTP_USER:
        print("\n❌ ERREUR: Tu dois configurer SMTP_USER dans ce script!")
        print("   Édite le fichier test_email.py et change:")
        print(f'   SMTP_USER = "ton.email@gmail.com"')
        print(f'   SMTP_PASSWORD = "ton-app-password"')
        return
    
    if SMTP_PASSWORD == "ton-app-password-16-caracteres" or not SMTP_PASSWORD:
        print("\n❌ ERREUR: Tu dois configurer SMTP_PASSWORD dans ce script!")
        print("   Va sur https://myaccount.google.com/apppasswords pour générer un App Password")
        return
    
    print(f"\n📧 Configuration:")
    print(f"   Serveur: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"   Utilisateur: {SMTP_USER}")
    print(f"   Mot de passe: {'*' * len(SMTP_PASSWORD)} ({len(SMTP_PASSWORD)} caractères)")
    
    print(f"\n🔌 Connexion à {SMTP_SERVER}:{SMTP_PORT}...")
    
    server = None
    try:
        # Création de la connexion
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        
        # Activer le debug pour voir les échanges
        print("\n📡 Activation du mode debug...")
        server.set_debuglevel(1)
        
        # EHLO
        print("\n📡 Envoi EHLO...")
        server.ehlo()
        
        # STARTTLS (pour le port 587)
        if SMTP_PORT == 587:
            print("\n🔒 Démarrage STARTTLS...")
            server.starttls()
            server.ehlo()
        
        # Login
        print(f"\n🔑 Tentative de login avec {SMTP_USER}...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("✅ Login réussi!")
        
        # Créer le message
        print("\n📝 Préparation du message...")
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = SMTP_USER
        msg['Subject'] = '✅ Test MyFinance Companion'
        
        body = """Bonjour!

Si tu reçois cet email, c'est que la configuration SMTP fonctionne parfaitement! 🎉

Tu peux maintenant:
1. Retourner dans l'application MyFinance
2. Aller dans Configuration > Notifications
3. Remplir les mêmes informations
4. Cliquer sur "Test notification"

---
MyFinance Companion
"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Envoi
        print("\n📤 Envoi de l'email...")
        server.send_message(msg)
        
        print("\n" + "="*60)
        print("✅ SUCCÈS! L'email a été envoyé!")
        print("="*60)
        print(f"\n📧 Vérifie ta boîte mail: {SMTP_USER}")
        print("(N'oublie pas de vérifier les spams aussi)")
        
    except smtplib.SMTPAuthenticationError as e:
        print("\n" + "="*60)
        print("❌ ERREUR D'AUTHENTIFICATION")
        print("="*60)
        print(f"\nDétails: {e}")
        print("\n💡 SOLUTIONS:")
        print("   1. Vérifie que tu utilises un App Password (pas ton mot de passe Gmail)")
        print("   2. Vérifie que la 2FA est activée: https://myaccount.google.com/signinoptions/two-step-verification")
        print("   3. Régénère un App Password: https://myaccount.google.com/apppasswords")
        print("   4. Assure-toi de copier l'App Password sans les espaces")
        
    except smtplib.SMTPConnectError as e:
        print("\n" + "="*60)
        print("❌ ERREUR DE CONNEXION")
        print("="*60)
        print(f"\nDétails: {e}")
        print("\n💡 SOLUTIONS:")
        print("   1. Vérifie que tu es connecté à Internet")
        print("   2. Essaie le port 465 au lieu de 587")
        print("   3. Vérifie que le pare-feu ne bloque pas le port SMTP")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERREUR")
        print("="*60)
        print(f"\nDétails: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if server:
            try:
                server.quit()
                print("\n🔌 Connexion fermée.")
            except:
                pass


if __name__ == "__main__":
    test_email()
