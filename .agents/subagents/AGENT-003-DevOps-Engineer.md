# AGENT-003: DevOps Engineer

## 🎯 Mission

Architecte DevOps de FinancePerso. Responsable de l'infrastructure, du pipeline CI/CD, de la containerisation et de la fiabilité des déploiements. Garant de la qualité automatisée et de la livraison continue.

---

## 📚 Contexte: Infrastructure FinancePerso

### Philosophie
> "Automatiser ce qui peut l'être, documenter ce qui doit l'être, monitorer tout le reste."

### Stack DevOps

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVOPS STACK                             │
├─────────────────────────────────────────────────────────────┤
│  CI/CD: GitHub Actions                                       │
│  ├─ Test matrix: Python 3.11, 3.12                          │
│  ├─ Security: Bandit + Safety                               │
│  └─ Coverage: Codecov                                       │
├─────────────────────────────────────────────────────────────┤
│  CONTAINERIZATION: Docker                                    │
│  ├─ Base: python:3.12-slim                                  │
│  ├─ User: non-root (appuser)                                │
│  └─ Health: HTTP check sur port 8501                        │
├─────────────────────────────────────────────────────────────┤
│  ORCHESTRATION: Docker Compose                               │
│  └─ Volume: Data persistante + .env                         │
├─────────────────────────────────────────────────────────────┤
│  TOOLING:                                                    │
│  ├─ Lint: Ruff (remplace flake8/isort)                      │
│  ├─ Format: Black                                           │
│  └─ Test: pytest + coverage                                 │
├─────────────────────────────────────────────────────────────┤
│  SCRIPTS:                                                    │
│  └─ doctor, benchmark, cleanup, audit, migrate              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Pipeline CI/CD

### Architecture GitHub Actions

```yaml
# .github/workflows/ci.yml
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    TEST     │───→│  SECURITY   │───→│    BUILD    │───→│   NOTIFY    │
│             │    │             │    │             │    │             │
│ Matrix:     │    │ Bandit scan │    │ Docker      │    │ Success/    │
│ 3.11, 3.12  │    │ Safety check│    │ startup     │    │ Failure     │
│             │    │             │    │             │    │             │
│ Steps:      │    │             │    │             │    │             │
│ - Install   │    │             │    │             │    │             │
│ - Ruff      │    │             │    │             │    │             │
│ - Black     │    │             │    │             │    │             │
│ - pytest    │    │             │    │             │    │             │
│ - Codecov   │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Configuration

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - uses: actions/cache@v3  # Cache pip
      # ... install, lint, test

  security:
    runs-on: ubuntu-latest
    steps:
      - name: Run Bandit security scan
        run: bandit -r modules/ -f json -o bandit-report.json || true
      - name: Check vulnerabilities
        run: safety check -r requirements.txt || true

  build:
    needs: [test, security]
    steps:
      - name: Verify application starts
        run: |
          timeout 10s streamlit run app.py &
          sleep 5
```

---

## 🐳 Containerization

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies (cache layer)
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Security: non-root user
RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; \
         urllib.request.urlopen('http://localhost:8501/_stcore/health')" \
    || exit 1

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  financeperso:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./Data:/app/Data        # Persist database
      - ./.env:/app/.env:ro     # Secrets (read-only)
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c",
        "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Commandes Docker

```bash
# Build
docker build -t financeperso .

# Run
docker run -p 8501:8501 -v $(pwd)/Data:/app/Data financeperso

# Compose (développement)
docker-compose up -d
docker-compose logs -f
docker-compose down

# Health check
docker ps
docker inspect --format='{{.State.Health.Status}}' financeperso
```

---

## 🛠️ Tooling Configuration

### Black (Formatage)

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py312']
exclude = '''
/(
    \.git
  | \.pytest_cache
  | __pycache__
  | Data
  | docs
)/
'''
```

### Ruff (Linting)

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
]
ignore = []
```

### Pytest (Tests)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=modules --cov-report=html --cov-report=term-missing -v"
```

---

## 📜 Scripts de Maintenance

### Makefile

```makefile
.PHONY: help setup test lint format check ci run clean

help:
	@echo "FinancePerso commands:"
	@echo "  make setup    - Setup dev environment"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linter"
	@echo "  make format   - Format code"
	@echo "  make check    - Run all checks"
	@echo "  make ci       - Run CI locally"
	@echo "  make run      - Start app"
	@echo "  make clean    - Clean cache"

setup:
	@./scripts/setup_dev_env.sh

test:
	@pytest tests/test_essential.py -v

lint:
	@ruff check modules/ app.py pages/

format:
	@black modules/ app.py pages/ tests/

check: lint test

ci:
	@ruff check modules/ || true
	@pytest tests/ --cov=modules

run:
	@streamlit run app.py

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .coverage coverage.xml htmlcov/
```

### Scripts Utilitaires

| Script | Usage | Description |
|--------|-------|-------------|
| `doctor.py` | `python scripts/doctor.py` | Diagnostic environnement |
| `benchmark.py` | `python scripts/benchmark.py` | Performance DB |
| `cleanup_backups.py` | `python scripts/cleanup_backups.py` | Nettoyage backups |
| `audit_codebase.py` | `python scripts/audit_codebase.py` | Audit qualité |
| `migrate_module.py` | `python scripts/migrate_module.py` | Migration code |

### Exemple: Doctor Script

```python
#!/usr/bin/env python3
"""FinancePerso - Environment Doctor"""

import sys
import subprocess

def check(name, command, success_msg, error_msg):
    """Run a check command."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"✓ {name}: {success_msg}")
            return True
        else:
            print(f"✗ {name}: {error_msg}")
            return False
    except Exception as e:
        print(f"✗ {name}: {e}")
        return False

def main():
    print("FinancePerso - Environment Doctor")
    print("=" * 50)
    
    checks = [
        check("Python 3.12", "python3 --version", "OK", "Not found"),
        check("Streamlit", "python3 -c 'import streamlit'", "Installed", "Missing"),
        check("Database", "test -f Data/finance.db", "Exists", "Not found"),
        check("Env file", "test -f .env", "Exists", "Not found"),
    ]
    
    passed = sum(checks)
    print(f"\nResults: {passed}/{len(checks)} checks passed")
    
    if passed == len(checks):
        print("✅ Environment is ready!")
        return 0
    else:
        print("⚠️  Some issues detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## 🔧 Responsabilités

### Quand consulter cet agent

✅ **OBLIGATOIRE**:
- Modification pipeline CI/CD
- Mise à jour Dockerfile/docker-compose
- Ajout de dépendances (requirements.txt)
- Problème de build ou déploiement
- Optimisation performance infrastructure
- Mise en place monitoring

❌ **PAS NÉCESSAIRE**:
- Bug fonctionnel applicatif (aller vers QA Agent)
- Problème base de données (aller vers Database Agent)
- Modification UI (aller vers UI Agent)

### Workflow DevOps

```
1. DÉVELOPPEMENT
   └── make run  # Local development
   └── make test  # Quick test
   └── make lint  # Check style

2. PRÉ-COMMIT
   └── make check  # Lint + test
   └── git commit

3. CI/CD
   └── Push → GitHub Actions
   └── Test matrix (3.11, 3.12)
   └── Security scan
   └── Build verification

4. DÉPLOIEMENT
   └── docker-compose pull
   └── docker-compose up -d
   └── Health check
   └── Monitoring
```

---

## 📋 Templates de Code

### Template: Nouveau Workflow GitHub Actions

```yaml
# .github/workflows/feature.yml
name: Feature CI

on:
  push:
    branches: [feature/*]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      
      - name: Install
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Test feature
        run: pytest tests/test_feature.py -v
```

### Template: Nouveau Script de Maintenance

```python
#!/usr/bin/env python3
"""
Script: feature_maintenance.py
Description: [Description du script]
Usage: python scripts/feature_maintenance.py [--dry-run]
"""

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(dry_run: bool = False):
    """Main function."""
    logger.info(f"Starting maintenance (dry_run={dry_run})")
    
    # Implementation
    
    logger.info("Maintenance completed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Maintenance script")
    parser.add_argument("--dry-run", action="store_true", help="Simulate only")
    args = parser.parse_args()
    
    main(dry_run=args.dry_run)
```

### Template: Dockerfile Multi-stage

```dockerfile
# Build stage (if compilation needed)
FROM python:3.12-slim as builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim

WORKDIR /app

# Copy only installed packages
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application
COPY . .

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "app.py"]
```

---

## 🚨 Procédures d'Urgence

### Rollback Déploiement

```bash
#!/bin/bash
# rollback.sh

# 1. Arrêter le service
docker-compose down

# 2. Restaurer version précédente
docker pull financeperso:previous
docker tag financeperso:previous financeperso:latest

# 3. Restaurer base de données si nécessaire
./scripts/restore_backup.sh

# 4. Redémarrer
docker-compose up -d

# 5. Vérifier santé
sleep 5
curl -f http://localhost:8501/_stcore/health || exit 1
echo "Rollback completed"
```

### Incident Response

```python
# Emergency procedures
EMERGENCY_RESPONSE = {
    "container_wont_start": [
        "docker-compose logs",
        "Check .env file exists",
        "Check Data/ permissions",
        "docker system prune (cleanup)"
    ],
    "high_memory_usage": [
        "docker stats",
        "Check for memory leaks in logs",
        "Restart container",
        "Scale up if needed"
    ],
    "ci_failure": [
        "Check GitHub Actions logs",
        "Run make check locally",
        "Fix issues",
        "Re-push"
    ]
}
```

---

## 📚 Références

### Fichiers Clés
- `.github/workflows/ci.yml` - Pipeline CI/CD
- `Dockerfile` - Image container
- `docker-compose.yml` - Orchestration
- `Makefile` - Commandes standards
- `pyproject.toml` - Configuration tooling
- `scripts/` - Scripts de maintenance

### Commandes Essentielles

```bash
# CI Local
make ci

# Docker
docker-compose up -d
docker-compose logs -f
docker-compose down

# Maintenance
python scripts/doctor.py
python scripts/benchmark.py
python scripts/cleanup_backups.py

# Git
make check && git commit -m "..."
```

---

**Version**: 1.0  
**Créé par**: Orchestrateur d'Analyse 360°  
**Date**: 2026-02-25  
**Statut**: PRÊT À L'EMPLOI

---

## 🌍 Module Additionnel: Multi-Environnements

### Architecture Environnements

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENVIRONNEMENTS                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DEV                    STAGING                   PROD          │
│  ┌──────────┐           ┌──────────┐            ┌──────────┐   │
│  │ Local    │──────────→│  Preprod │───────────→│  Live    │   │
│  │ SQLite   │  promote  │  SQLite  │  deploy    │  SQLite  │   │
│  │ Hot reload│          │  Test data│           │  Backup  │   │
│  └──────────┘           └──────────┘            └──────────┘   │
│       ↑                                               ↑         │
│   Developer                                    End Users        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Configuration par Environnement

```python
"""
Gestion centralisée des configurations d'environnement.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class AppConfig:
    """Configuration applicative."""
    env: Environment
    debug: bool
    log_level: str
    db_path: str
    backup_enabled: bool
    encryption_required: bool
    sentry_dsn: Optional[str]
    ai_provider: str
    cache_ttl: int
    max_upload_size_mb: int

class ConfigManager:
    """Manager de configuration."""
    
    CONFIGS = {
        Environment.DEVELOPMENT: AppConfig(
            env=Environment.DEVELOPMENT,
            debug=True,
            log_level="DEBUG",
            db_path="Data/finance_dev.db",
            backup_enabled=False,
            encryption_required=False,  # Facilite le debug
            sentry_dsn=None,
            ai_provider="ollama",  # Local, gratuit
            cache_ttl=60,
            max_upload_size_mb=50
        ),
        Environment.STAGING: AppConfig(
            env=Environment.STAGING,
            debug=False,
            log_level="INFO",
            db_path="Data/finance_staging.db",
            backup_enabled=True,
            encryption_required=True,
            sentry_dsn="https://xxx@staging.sentry.io/xxx",
            ai_provider="gemini",
            cache_ttl=300,
            max_upload_size_mb=100
        ),
        Environment.PRODUCTION: AppConfig(
            env=Environment.PRODUCTION,
            debug=False,
            log_level="WARNING",
            db_path="Data/finance.db",
            backup_enabled=True,
            encryption_required=True,
            sentry_dsn="https://xxx@production.sentry.io/xxx",
            ai_provider="gemini",
            cache_ttl=600,
            max_upload_size_mb=100
        )
    }
    
    @classmethod
    def get_current(cls) -> AppConfig:
        """Retourne la configuration de l'environnement actuel."""
        import os
        env_str = os.getenv("ENVIRONMENT", "development").lower()
        env = Environment(env_str)
        return cls.CONFIGS[env]
    
    @classmethod
    def is_prod(cls) -> bool:
        """Vérifie si on est en production."""
        return cls.get_current().env == Environment.PRODUCTION

# Usage
config = ConfigManager.get_current()
if config.encryption_required:
    enable_encryption()
```

### Docker Compose Multi-Environnements

```yaml
# docker-compose.yml (Base)
version: '3.8'

services:
  financeperso:
    build: .
    volumes:
      - ./Data:/app/Data
      - ./.env:/app/.env:ro
    environment:
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "-c",
        "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

---
# docker-compose.override.yml (Dev - auto-loaded)
version: '3.8'

services:
  financeperso:
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=development
    volumes:
      - ./modules:/app/modules:ro  # Hot reload
      - ./pages:/app/pages:ro
    command: ["streamlit", "run", "app.py", "--server.runOnSave", "true"]

---
# docker-compose.staging.yml
version: '3.8'

services:
  financeperso:
    ports:
      - "8502:8501"
    environment:
      - ENVIRONMENT=staging
    restart: unless-stopped

---
# docker-compose.prod.yml
version: '3.8'

services:
  financeperso:
    ports:
      - "80:8501"
    environment:
      - ENVIRONMENT=production
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Scripts de Déploiement

```bash
#!/bin/bash
# deploy.sh - Script de déploiement universel

set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

echo "🚀 Déploiement sur $ENVIRONMENT (version: $VERSION)"

# Vérifications
if [ "$ENVIRONMENT" == "production" ]; then
    echo "⚠️  PRODUCTION DETECTÉ"
    read -p "Êtes-vous sûr? (yes/no) " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Annulé"
        exit 1
    fi
fi

# Backup avant déploiement (prod uniquement)
if [ "$ENVIRONMENT" == "production" ]; then
    echo "💾 Backup de la base..."
    docker exec financeperso python -c "from modules.backup_manager; create_backup()"
fi

# Pull et déploiement
echo "📥 Pull de l'image..."
docker pull financeperso:$VERSION

echo "🔄 Redémarrage..."
docker-compose -f docker-compose.yml -f docker-compose.${ENVIRONMENT}.yml down
docker-compose -f docker-compose.yml -f docker-compose.${ENVIRONMENT}.yml up -d

# Health check
echo "🏥 Health check..."
sleep 5
for i in {1..10}; do
    if curl -f http://localhost:$([ "$ENVIRONMENT" == "production" ] && echo "80" || echo "8502")/_stcore/health > /dev/null 2>&1; then
        echo "✅ Déploiement réussi!"
        exit 0
    fi
    echo "⏳ Attente... ($i/10)"
    sleep 3
done

echo "❌ Health check failed!"
# Rollback
if [ "$ENVIRONMENT" == "production" ]; then
    echo "🔄 Rollback en cours..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
    docker pull financeperso:previous
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
fi
exit 1
```

---

## 🔐 Module Additionnel: Secrets Management

### GitHub Secrets

```yaml
# .github/workflows/ci.yml avec secrets
name: CI/CD Pipeline

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Create .env from secrets
        run: |
          echo "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" >> .env
          echo "ENCRYPTION_KEY=${{ secrets.ENCRYPTION_KEY }}" >> .env
          echo "SENTRY_DSN=${{ secrets.SENTRY_DSN }}" >> .env
      
      - name: Test with secrets
        run: pytest tests/
        env:
          ENVIRONMENT: ci

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production  # Protection rules
    steps:
      - name: Deploy to production
        run: |
          echo "${{ secrets.SSH_KEY }}" > deploy_key.pem
          chmod 600 deploy_key.pem
          ssh -i deploy_key.pem user@server "./deploy.sh production ${{ github.sha }}"
```

### Vault Integration (Optionnel)

```python
"""
Integration HashiCorp Vault pour secrets enterprise.
"""

import hvac
from functools import lru_cache

class VaultClient:
    """Client Vault pour secrets dynamiques."""
    
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv("VAULT_ADDR"),
            token=os.getenv("VAULT_TOKEN")
        )
    
    def get_secret(self, path: str) -> dict:
        """Récupère un secret."""
        response = self.client.secrets.kv.v2.read_secret_version(
            path=path
        )
        return response["data"]["data"]
    
    def get_database_credentials(self) -> tuple[str, str]:
        """Génère des credentials DB dynamiques."""
        response = self.client.secrets.database.generate_credentials(
            name="financeperso-db-role"
        )
        return response["data"]["username"], response["data"]["password"]

# Usage
vault = VaultClient()
api_key = vault.get_secret("financeperso/api")["gemini_key"]
```

---

## 📊 Module Additionnel: Monitoring & Observability

### Métriques Application

```python
"""
Métriques métier et techniques.
"""

from dataclasses import dataclass
from typing import Dict, Any
import time

@dataclass
class AppMetrics:
    """Métriques applicatives."""
    
    # Business
    transactions_imported_today: int
    categorization_accuracy: float
    active_users: int
    
    # Performance
    avg_query_time_ms: float
    cache_hit_rate: float
    db_size_mb: float
    
    # Health
    last_backup_timestamp: float
    errors_last_hour: int
    ai_api_latency_ms: float

class MetricsCollector:
    """Collecteur de métriques."""
    
    def collect(self) -> AppMetrics:
        """Collecte toutes les métriques."""
        return AppMetrics(
            transactions_imported_today=self._count_today_transactions(),
            categorization_accuracy=self._calculate_accuracy(),
            active_users=self._count_active_users(),
            avg_query_time_ms=QueryProfiler.get_avg_time(),
            cache_hit_rate=CacheManager.get_hit_rate(),
            db_size_mb=os.path.getsize(DB_PATH) / 1024 / 1024,
            last_backup_timestamp=self._last_backup_time(),
            errors_last_hour=ErrorTracker.count_recent_errors(hours=1),
            ai_api_latency_ms=AIManager.get_avg_latency()
        )
    
    def to_prometheus(self) -> str:
        """Exporte au format Prometheus."""
        metrics = self.collect()
        return f"""
# HELP finance_transactions_total Nombre total de transactions
finance_transactions_total {metrics.transactions_imported_today}

# HELP finance_db_size_mb Taille base de données
finance_db_size_mb {metrics.db_size_mb}

# HELP finance_cache_hit_rate Taux cache hit
finance_cache_hit_rate {metrics.cache_hit_rate}
"""
```

### Health Checks Avancés

```python
"""
Health checks complets pour monitoring.
"""

from dataclasses import dataclass
from typing import List, Optional
import sqlite3
import requests

@dataclass
class HealthStatus:
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    response_time_ms: float
    message: Optional[str] = None

class HealthChecker:
    """Vérificateur de santé complet."""
    
    CHECKS = [
        "database",
        "ai_provider",
        "disk_space",
        "memory",
        "backup_freshness"
    ]
    
    @classmethod
    def full_check(cls) -> List[HealthStatus]:
        """Exécute tous les health checks."""
        results = []
        
        for check_name in cls.CHECKS:
            start = time.time()
            try:
                status = getattr(cls, f"_check_{check_name}")()
            except Exception as e:
                status = HealthStatus(
                    name=check_name,
                    status="unhealthy",
                    response_time_ms=(time.time() - start) * 1000,
                    message=str(e)
                )
            results.append(status)
        
        return results
    
    @classmethod
    def _check_database(cls) -> HealthStatus:
        """Vérifie la base de données."""
        start = time.time()
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.execute("PRAGMA integrity_check")
        conn.close()
        
        return HealthStatus(
            name="database",
            status="healthy",
            response_time_ms=(time.time() - start) * 1000
        )
    
    @classmethod
    def _check_ai_provider(cls) -> HealthStatus:
        """Vérifie l'IA provider."""
        start = time.time()
        provider = get_ai_provider()
        response = provider.generate_text("test", timeout=5)
        
        return HealthStatus(
            name="ai_provider",
            status="healthy" if response else "degraded",
            response_time_ms=(time.time() - start) * 1000
        )
    
    @classmethod
    def _check_disk_space(cls) -> HealthStatus:
        """Vérifie l'espace disque."""
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (2**30)
        
        status = "healthy" if free_gb > 10 else "degraded" if free_gb > 5 else "unhealthy"
        
        return HealthStatus(
            name="disk_space",
            status=status,
            response_time_ms=0,
            message=f"{free_gb} GB free"
        )
    
    @classmethod
    def _check_backup_freshness(cls) -> HealthStatus:
        """Vérifie l'âge du dernier backup."""
        last_backup = BackupManager().get_last_backup_time()
        hours_since = (time.time() - last_backup) / 3600
        
        status = "healthy" if hours_since < 25 else "degraded" if hours_since < 48 else "unhealthy"
        
        return HealthStatus(
            name="backup_freshness",
            status=status,
            response_time_ms=0,
            message=f"Last backup: {hours_since:.1f}h ago"
        )
    
    @classmethod
    def get_overall_status(cls) -> str:
        """Retourne le statut global."""
        checks = cls.full_check()
        
        if any(c.status == "unhealthy" for c in checks):
            return "unhealthy"
        if any(c.status == "degraded" for c in checks):
            return "degraded"
        return "healthy"
```

### Alerting

```python
"""
Système d'alerting.
"""

class AlertManager:
    """Gestionnaire d'alertes."""
    
    ALERT_RULES = {
        "db_down": {
            "condition": "health.database == 'unhealthy'",
            "severity": "critical",
            "channels": ["email", "slack"]
        },
        "disk_full": {
            "condition": "metrics.disk_free_gb < 5",
            "severity": "critical",
            "channels": ["email"]
        },
        "backup_stale": {
            "condition": "metrics.hours_since_backup > 48",
            "severity": "warning",
            "channels": ["email"]
        },
        "high_error_rate": {
            "condition": "metrics.errors_last_hour > 10",
            "severity": "warning",
            "channels": ["slack"]
        }
    }
    
    def evaluate_rules(self):
        """Évalue toutes les règles d'alerte."""
        metrics = MetricsCollector().collect()
        health = HealthChecker.full_check()
        
        for rule_name, rule in self.ALERT_RULES.items():
            if self._evaluate_condition(rule["condition"], metrics, health):
                self._send_alert(rule_name, rule)
    
    def _send_alert(self, rule_name: str, rule: dict):
        """Envoie une alerte."""
        if "slack" in rule["channels"]:
            self._send_slack_alert(rule_name, rule)
        if "email" in rule["channels"]:
            self._send_email_alert(rule_name, rule)
```

---

## 🚨 Module Additionnel: Disaster Recovery Plan (DRP)

### Plan de Reprise d'Activité

```python
"""
Plan de reprise d'activité (DRP).
"""

class DisasterRecovery:
    """Procédures de reprise d'activité."""
    
    RTO_MINUTES = 60   # Recovery Time Objective
    RPO_MINUTES = 1440  # Recovery Point Objective (24h de données max perdues)
    
    @classmethod
    def scenario_corrupted_database(cls):
        """
        Scénario: Base corrompue.
        
        Steps:
        1. Arrêter l'application
        2. Identifier la dernière backup saine
        3. Restaurer la backup
        4. Vérifier intégrité
        5. Redémarrer
        6. Notifier utilisateurs des données potentiellement perdues
        """
        pass
    
    @classmethod
    def scenario_server_failure(cls):
        """
        Scénario: Serveur hors service.
        
        Steps:
        1. Provisionner nouveau serveur
        2. Restaurer Docker containers
        3. Restaurer base depuis backup cloud
        4. Mettre à jour DNS
        5. Vérifier santé
        """
        pass
    
    @classmethod
    def scenario_ransomware(cls):
        """
        Scénario: Attaque ransomware.
        
        Steps:
        1. Isoler le système (air gap)
        2. Ne PAS payer la rançon
        3. Analyser la portée
        4. Reconstruire depuis backups offline
        5. Changer TOUTES les clés/secrets
        6. Forensic investigation
        """
        pass

# Document de procédures
DRP_DOCUMENT = """
# DISASTER RECOVERY PLAN - FinancePerso

## Contacts d'Urgence
- Lead Tech: +33 X XX XX XX XX
- Responsable Produit: +33 X XX XX XX XX
- Hébergeur: support@hosting.com

## Inventaire des Ressources
- Serveur: XXX.XXX.XXX.XXX
- Base de données: Data/finance.db
- Backups: Data/backups/, S3 (s3://financeperso-backups/)

## Procédures

### Perte de Données Mineure (< 1h)
1. Restaurer depuis backup local automatique
2. Vérifier intégrité
3. Redémarrer

### Corruption Base de Données
1. docker-compose down
2. mv Data/finance.db Data/finance.db.corrupted
3. gunzip -c Data/backups/finance_auto_YYYYMMDD_HHMMSS.db.gz > Data/finance.db
4. sqlite3 Data/finance.db "PRAGMA integrity_check"
5. docker-compose up -d

### Incident Majeur (Serveur Inaccessible)
1. Provisionner nouveau VPS
2. Installer Docker
3. Cloner repo
4. Restaurer .env depuis password manager
5. Télécharger dernière backup: aws s3 cp s3://bucket/backup.db.gz Data/
6. docker-compose up -d
7. Mettre à jour DNS

### Tests DRP
- Test de backup: Mensuel
- Test de restauration: Trimestriel
- Test complet DRP: Annuel
"""
```

---

**Version**: 1.1 - **COMPLÉTÉ**  
**Ajouts**: Multi-environnements, Secrets Management, Monitoring, Health Checks, DRP complet
