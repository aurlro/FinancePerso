#!/bin/bash
# Script de déploiement pour FinancePerso
# Usage: ./scripts/deploy.sh [production|staging]

set -e

ENV=${1:-staging}
echo "🚀 Déploiement FinancePerso - Environnement: $ENV"
echo ""

# Vérifier les prérequis
echo "📋 Vérification des prérequis..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git n'est pas installé"
    exit 1
fi

echo "✅ Prérequis OK"
echo ""

# Vérifier le statut git
echo "📊 Statut Git..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Attention: Des fichiers non commités détectés"
    git status --short
    read -p "Continuer quand même? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🧪 Tests..."
# Lancer les tests essentiels
python -m pytest tests/test_essential.py -v -x
if [ $? -ne 0 ]; then
    echo "❌ Tests échoués"
    exit 1
fi
echo "✅ Tests passés"
echo ""

# Build Docker
echo "🔨 Build Docker..."
VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo "dev")
IMAGE_TAG="financeperso:$VERSION"

docker build \
    --build-arg ENABLE_CORS=true \
    --build-arg ENABLE_XSRF=true \
    -t "$IMAGE_TAG" \
    -t "financeperso:latest" \
    .

if [ $? -ne 0 ]; then
    echo "❌ Build Docker échoué"
    exit 1
fi

echo "✅ Build réussi: $IMAGE_TAG"
echo ""

# Test du conteneur
echo "🧪 Test du conteneur..."
docker run -d --name financeperso-test -p 8501:8501 "$IMAGE_TAG"
sleep 5

# Vérifier la santé
if curl -s http://localhost:8501/_stcore/health > /dev/null; then
    echo "✅ Conteneur healthy"
else
    echo "❌ Conteneur unhealthy"
    docker logs financeperso-test
    docker stop financeperso-test
    docker rm financeperso-test
    exit 1
fi

# Nettoyer le conteneur de test
docker stop financeperso-test > /dev/null
docker rm financeperso-test > /dev/null

echo ""

# Déploiement
echo "📦 Déploiement..."
if [ "$ENV" = "production" ]; then
    echo "🚀 Déploiement en PRODUCTION"
    
    # Tag pour production
    docker tag "$IMAGE_TAG" "financeperso:production"
    
    # Sauvegarder l'ancienne version
    docker tag financeperso:production financeperso:production-backup 2>/dev/null || true
    
    # Redémarrer le service
    docker-compose down || true
    docker-compose up -d
    
    echo "✅ Production déployée"
    
else
    echo "🧪 Déploiement en STAGING"
    
    # Tag pour staging
    docker tag "$IMAGE_TAG" "financeperso:staging"
    
    # Démarrer en staging
    docker run -d \
        --name financeperso-staging \
        -p 8502:8501 \
        -e ENVIRONMENT=staging \
        "$IMAGE_TAG"
    
    echo "✅ Staging déployé sur http://localhost:8502"
fi

echo ""
echo "📊 Résumé du déploiement:"
echo "  • Version: $VERSION"
echo "  • Environnement: $ENV"
echo "  • Image: $IMAGE_TAG"
echo "  • Date: $(date)"
echo ""
echo "✅ Déploiement terminé avec succès!"
