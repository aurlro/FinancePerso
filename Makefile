# FinancePerso - Makefile
# Standard commands for development

.PHONY: help setup test test-cov lint format clean run check ci doc-check doc-update doc-generate

# Default target
help:
	@echo "FinancePerso - Available commands:"
	@echo ""
	@echo "  make setup      - Setup development environment"
	@echo "  make test       - Run essential tests quickly"
	@echo "  make test-all   - Run all tests with coverage"
	@echo "  make lint       - Run linter (Ruff)"
	@echo "  make format     - Format code (Black)"
	@echo "  make check      - Run all checks (lint + test)"
	@echo "  make ci         - Run CI pipeline locally"
	@echo "  make run        - Start Streamlit app"
	@echo "  make clean      - Clean cache and temp files"
	@echo "  make doc-check  - Check documentation consistency"
	@echo "  make doc-update - Update documentation"
	@echo "  make doc-generate MODULE=x - Generate module documentation"
	@echo ""

# Setup environment
setup:
	@./scripts/setup_dev_env.sh

# Quick test (essential only)
test:
	@echo "🧪 Running essential tests..."
	@python3 -m pytest tests/test_essential.py -v --tb=short

# Full test suite
test-all:
	@echo "🧪 Running all tests with coverage..."
	@python3 -m pytest tests/ --cov=modules --cov-report=term-missing -v --tb=short

# Lint code
lint:
	@echo "🔍 Running linter..."
	@python3 -m ruff check modules/ app.py pages/ --output-format=full

# Format code
format:
	@echo "✨ Formatting code..."
	@python3 -m black modules/ app.py pages/ tests/

# Run all checks
check: lint test
	@echo "✅ All checks passed!"

# CI simulation
ci:
	@echo "🔄 Running CI pipeline locally..."
	@python3 -m ruff check modules/ app.py pages/ --output-format=text || true
	@python3 -m pytest tests/ --cov=modules --cov-report=xml -v --tb=short

# Start application
run:
	@echo "🚀 Starting Streamlit..."
	@streamlit run app.py

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .coverage coverage.xml htmlcov/
	@echo "✨ Clean complete"

# Documentation checks
doc-check:
	@echo "🔍 Checking documentation consistency..."
	@python3 .agents/doc_agent.py --check

doc-update:
	@echo "📝 Updating documentation..."
	@python3 .agents/doc_agent.py --update

doc-generate:
	@if [ -z "$(MODULE)" ]; then \
		echo "❌ Usage: make doc-generate MODULE=<module_name>"; \
		exit 1; \
	fi
	@echo "📚 Generating documentation for $(MODULE)..."
	@python3 .agents/doc_agent.py --generate $(MODULE)"
