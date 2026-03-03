# Guide de Déploiement FinancePerso

Ce guide explique comment déployer l'application FinancePerso avec Docker.

## Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum (4GB recommandé)

## Méthode 1: Déploiement Automatique (Recommandé)

Utilisez le script de déploiement fourni :

```bash
# Rendre le script exécutable (une seule fois)
chmod +x scripts/deploy.sh

# Déployer en développement (défaut)
./scripts/deploy.sh

# Déployer en production
./scripts/deploy.sh production
```

Le script effectue automatiquement :
1. Vérification des prérequis
2. Nettoyage des ressources Docker inutilisées
3. Construction de l'image
4. Démarrage des containers
5. Vérification de santé de l'application

## Méthode 2: Déploiement Manuel

### 1. Configuration

Créez le fichier `.env` à partir du template :

```bash
cp .env.example .env
# Éditez .env avec vos vraies valeurs
nano .env
```

### 2. Build

```bash
docker-compose build
```

### 3. Démarrage

```bash
docker-compose up -d
```

### 4. Vérification

```bash
# Vérifier que l'application répond
curl http://localhost:8501/_stcore/health

# Voir les logs
docker-compose logs -f
```

### 5. Accès

Ouvrez votre navigateur : http://localhost:8501

## Commandes Utiles

```bash
# Arrêter l'application
docker-compose down

# Redémarrer
docker-compose restart

# Rebuild complet (sans cache)
docker-compose build --no-cache

# Voir les logs en temps réel
docker-compose logs -f app

# Shell dans le container
docker-compose exec app bash

# Mettre à jour l'image
docker-compose pull
docker-compose up -d
```

## Variables d'Environnement Importantes

| Variable | Description | Défaut |
|----------|-------------|--------|
| `STREAMLIT_PORT` | Port d'accès à l'application | 8501 |
| `ENVIRONMENT` | Environnement (development/production) | production |
| `DB_PATH` | Chemin de la base SQLite | /app/Data/finance.db |
| `GEMINI_API_KEY` | Clé API Google Gemini | - |
| `ENCRYPTION_KEY` | Clé de chiffrement AES-256 | - |

## Persistance des Données

Les données sont persistées via des volumes Docker :

- `./Data` : Base de données SQLite
- `./logs` : Fichiers de logs

Pour sauvegarder la base de données :

```bash
# Backup
cp Data/finance.db backups/finance_$(date +%Y%m%d).db

# Restore
cp backups/finance_YYYYMMDD.db Data/finance.db
```

## Mise à Jour

Pour mettre à jour l'application :

```bash
# 1. Pull des derniers changements
git pull

# 2. Rebuild et redémarrage
./scripts/deploy.sh production
```

## Dépannage

### L'application ne démarre pas

```bash
# Vérifier les logs
docker-compose logs app

# Vérifier le healthcheck
docker-compose ps
```

### Problème de permissions

```bash
# Corriger les permissions sur Data
sudo chown -R $USER:$USER Data/
sudo chown -R $USER:$USER logs/
```

### Port déjà utilisé

```bash
# Changer le port dans .env
STREAMLIT_PORT=8502
```

## Production Avancée

Pour un déploiement production robuste, considérez :

1. **Reverse Proxy** (nginx/traefik) avec HTTPS
2. **Monitoring** avec Sentry configuré
3. **Backups automatiques** de la base de données
4. **Limites de ressources** dans docker-compose.yml

Exemple avec nginx :

```nginx
server {
    listen 443 ssl;
    server_name finance.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Support

En cas de problème :
1. Consultez les logs : `docker-compose logs`
2. Vérifiez la santé : `curl http://localhost:8501/_stcore/health`
3. Ouvrez une issue sur GitHub
