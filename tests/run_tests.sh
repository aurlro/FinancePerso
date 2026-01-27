#!/bin/bash
# Script pour lancer les tests en contournant le problème .DS_Store

echo "🧪 FinancePerso Test Runner"
echo "================================"

# Solution 1: Supprimer temporairement .DS_Store
if [ -f "../.DS_Store" ]; then
    echo "⚠️  Suppression temporaire de .DS_Store..."
    mv ../.DS_Store ../.DS_Store.bak 2>/dev/null || true
fi

# Solution 2: Lancer pytest avec --ignore
echo ""
echo "Lancement des tests..."
python3 -m pytest \
    --ignore=../.DS_Store \
    --ignore=.DS_Store \
    -v \
    "$@"

TEST_EXIT_CODE=$?

# Restaurer .DS_Store si déplacé
if [ -f "../.DS_Store.bak" ]; then
    mv ../.DS_Store.bak ../.DS_Store 2>/dev/null || true
fi

exit $TEST_EXIT_CODE
