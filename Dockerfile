# =============================================================================
# Dockerfile pour FinancePerso
# =============================================================================
# Build: docker build -t financeperso .
# Run:   docker run -p 8501:8501 financeperso
# =============================================================================

FROM python:3.12-slim

# Arguments de build
ARG ENVIRONMENT=production
ARG UID=1000
ARG GID=1000

# Labels
LABEL maintainer="FinancePerso Team"
LABEL description="Application de gestion financière personnelle"
LABEL version="5.6.0"

WORKDIR /app

# =============================================================================
# Installation des dépendances système
# =============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# =============================================================================
# Installation des dépendances Python
# =============================================================================
# Copier d'abord les fichiers de requirements pour le caching
COPY requirements.txt requirements-ml.txt ./

# Installer les dépendances principales
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Installer les dépendances ML (optionnel mais recommandé)
RUN pip install --no-cache-dir -r requirements-ml.txt || echo "ML dependencies skipped"

# =============================================================================
# Copie du code application
# =============================================================================
# Copier les fichiers essentiels d'abord (meilleur caching)
COPY app.py ./
COPY pyproject.toml ./
COPY README.md ./

# Copier les dossiers
COPY modules/ ./modules/
COPY pages/ ./pages/
COPY assets/ ./assets/
COPY views/ ./views/
COPY scripts/ ./scripts/

# Créer les répertoires nécessaires
RUN mkdir -p Data backups logs

# =============================================================================
# Configuration de l'utilisateur non-root
# =============================================================================
RUN groupadd -g ${GID} appuser && \
    useradd -m -u ${UID} -g ${GID} appuser && \
    chown -R appuser:appuser /app

USER appuser

# =============================================================================
# Configuration de l'environnement
# =============================================================================
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXsSRFProtection=false

# =============================================================================
# Health check
# =============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# =============================================================================
# Exposition du port et commande de démarrage
# =============================================================================
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
