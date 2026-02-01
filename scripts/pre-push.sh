#!/bin/bash
# Script à exécuter avant push (optionnel mais recommandé)
# Usage: ./scripts/pre-push.sh

set -e  # Stop on error

echo "🔍 Pré-push checks..."
echo ""

echo "1️⃣  Running linter (Ruff)..."
ruff check modules/ app.py pages/ --output-format=text

echo ""
echo "2️⃣  Running tests..."
pytest --cov=modules --cov-report=term-missing -q

echo ""
echo "3️⃣  Security check (Bandit)..."
bandit -r modules/ -ll || true

echo ""
echo "✅ All checks passed! Ready to push."
