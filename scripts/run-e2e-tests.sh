#!/bin/bash
# Script pour lancer les tests E2E Playwright
# Usage: ./run-e2e-tests.sh [headed|ui|report]

set -e

echo "🧪 FinancePerso E2E Tests"
echo "=========================="

# Check if we're in the right directory
if [ ! -d "web/frontend" ]; then
    echo "❌ Erreur: Exécutez ce script depuis la racine du projet"
    exit 1
fi

cd web/frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    npm ci
fi

# Install Playwright browsers if needed
if ! npx playwright install --help > /dev/null 2>&1; then
    echo "🎭 Installation de Playwright..."
    npm install -D @playwright/test
    npx playwright install
fi

# Run tests based on argument
case "${1:-}" in
    headed)
        echo "🖥️  Lancement des tests en mode headed (visible)..."
        npx playwright test --headed
        ;;
    ui)
        echo "🎨 Lancement du mode UI interactif..."
        npx playwright test --ui
        ;;
    report)
        echo "📊 Génération du rapport..."
        npx playwright show-report
        ;;
    *)
        echo "🚀 Lancement des tests E2E (headless)..."
        npx playwright test
        ;;
esac

echo "✅ Tests terminés!"
