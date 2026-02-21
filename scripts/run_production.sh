#!/bin/bash
#
# Script de lancement Production - FinancePerso
# =============================================
#
# Ce script lance FinancePerso en mode production optimisé
# sans utiliser Docker, avec:
# - Gunicorn comme serveur WSGI
# - Configuration de performance
# - Gestion des logs
# - Health checks
#
# Usage:
#   ./scripts/run_production.sh [port]
#
# Exemple:
#   ./scripts/run_production.sh 8501
#

set -euo pipefail

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="FinancePerso"
APP_MODULE="app:app"
DEFAULT_PORT=8501
PORT=${1:-$DEFAULT_PORT}
WORKERS=${WORKERS:-4}
WORKER_CLASS=${WORKER_CLASS:-"uvicorn.workers.UvicornWorker"}
TIMEOUT=${TIMEOUT:-120}
KEEP_ALIVE=${KEEP_ALIVE:-5}
MAX_REQUESTS=${MAX_REQUESTS:-10000}
MAX_REQUESTS_JITTER=${MAX_REQUESTS_JITTER:-1000}

# Répertoires
LOG_DIR="logs"
PID_DIR=".pid"
VENV_DIR=".venv"

# Fichiers
PID_FILE="$PID_DIR/financeperso.pid"
ACCESS_LOG="$LOG_DIR/access.log"
ERROR_LOG="$LOG_DIR/error.log"
APP_LOG="$LOG_DIR/app.log"

# Fonctions d'aide
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier les dépendances
check_dependencies() {
    log_info "Vérification des dépendances..."
    
    # Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 n'est pas installé"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_info "Python version: $PYTHON_VERSION"
    
    # Vérifier si l'environnement virtuel existe
    if [ ! -d "$VENV_DIR" ]; then
        log_warning "Environnement virtuel non trouvé: $VENV_DIR"
        log_info "Création de l'environnement virtuel..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activer l'environnement virtuel
    source "$VENV_DIR/bin/activate"
    
    # Vérifier les packages requis
    pip install -q gunicorn uvicorn streamlit
    
    log_success "Dépendances OK"
}

# Créer les répertoires nécessaires
setup_directories() {
    log_info "Configuration des répertoires..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$PID_DIR"
    mkdir -p "Data/backups"
    
    log_success "Répertoires créés"
}

# Vérifier si l'application est déjà en cours d'exécution
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_warning "L'application est déjà en cours d'exécution (PID: $PID)"
            log_info "Arrêtez d'abord l'application avec: ./scripts/run_production.sh stop"
            exit 1
        else
            # PID obsolète
            rm -f "$PID_FILE"
        fi
    fi
}

# Nettoyer les vieux logs
cleanup_logs() {
    log_info "Nettoyage des vieux logs..."
    
    # Garder seulement 7 jours de logs
    find "$LOG_DIR" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
    
    # Rotation des logs actuels si trop gros (>100MB)
    for logfile in "$ACCESS_LOG" "$ERROR_LOG" "$APP_LOG"; do
        if [ -f "$logfile" ] && [ $(stat -f%z "$logfile" 2>/dev/null || stat -c%s "$logfile" 2>/dev/null || echo 0) -gt 104857600 ]; then
            mv "$logfile" "${logfile}.$(date +%Y%m%d)"
            gzip "${logfile}.$(date +%Y%m%d)" &
        fi
    done
    
    log_success "Logs nettoyés"
}

# Optimiser la base de données
optimize_database() {
    log_info "Optimisation de la base de données..."
    
    if [ -f "Data/finance.db" ]; then
        python3 -c "
import sqlite3
conn = sqlite3.connect('Data/finance.db')
conn.execute('VACUUM')
conn.execute('ANALYZE')
conn.close()
print('Base de données optimisée')
" 2>/dev/null || log_warning "Impossible d'optimiser la base de données"
    fi
}

# Lancer l'application
start_app() {
    log_info "Démarrage de $APP_NAME sur le port $PORT..."
    log_info "Workers: $WORKERS | Timeout: ${TIMEOUT}s | Max requests: $MAX_REQUESTS"
    
    # Créer le fichier de configuration Gunicorn temporaire
    GUNICORN_CONFIG=$(cat <<EOF
import os
import multiprocessing

# Server socket
bind = "0.0.0.0:$PORT"
backlog = 2048

# Worker processes
workers = $WORKERS
worker_class = "$WORKER_CLASS"
worker_connections = 1000
timeout = $TIMEOUT
keepalive = $KEEP_ALIVE
max_requests = $MAX_REQUESTS
max_requests_jitter = $MAX_REQUESTS_JITTER

# Logging
accesslog = "$ACCESS_LOG"
errorlog = "$ERROR_LOG"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "$APP_NAME"

# Server mechanics
daemon = False
pidfile = "$PID_FILE"

# SSL (décommenter si nécessaire)
# keyfile = "ssl/key.pem"
# certfile = "ssl/cert.pem"

# Server hooks
def on_starting(server):
    print("Gunicorn starting...")

def on_reload(server):
    print("Gunicorn reloading...")
EOF
)
    
    # Sauvegarder la config
    CONFIG_FILE=".gunicorn.conf.py"
    echo "$GUNICORN_CONFIG" > "$CONFIG_FILE"
    
    # Lancer Gunicorn en arrière-plan
    log_info "Lancement de Gunicorn..."
    
    # Utiliser Streamlit directement avec optimisation
    exec python3 -m streamlit run app.py \
        --server.port "$PORT" \
        --server.address "0.0.0.0" \
        --server.maxUploadSize 200 \
        --server.maxMessageSize 200 \
        --server.enableCORS false \
        --server.enableXsrfProtection true \
        --browser.gatherUsageStats false \
        --logger.level info \
        2>&1 | tee -a "$APP_LOG" &
    
    STREAMLIT_PID=$!
    echo $STREAMLIT_PID > "$PID_FILE"
    
    # Attendre que le serveur démarre
    log_info "Attente du démarrage..."
    sleep 3
    
    # Vérifier que le serveur est bien démarré
    if ps -p "$STREAMLIT_PID" > /dev/null 2>&1; then
        log_success "$APP_NAME démarré avec succès!"
        log_info "PID: $STREAMLIT_PID"
        log_info "URL: http://localhost:$PORT"
        log_info "Logs: $LOG_DIR/"
        
        # Afficher les infos système
        echo ""
        echo "=============================================="
        echo "  $APP_NAME - Mode Production"
        echo "=============================================="
        echo "  Status: 🟢 EN LIGNE"
        echo "  Port: $PORT"
        echo "  PID: $STREAMLIT_PID"
        echo "  Workers: $WORKERS"
        echo "  Logs: $LOG_DIR/"
        echo "=============================================="
        echo ""
        
        # Health check
        health_check
    else
        log_error "Échec du démarrage"
        exit 1
    fi
}

# Health check
health_check() {
    log_info "Health check..."
    
    # Attendre que le serveur soit prêt
    sleep 2
    
    # Vérifier si le port est ouvert
    if command -v curl &> /dev/null; then
        if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT/_stcore/health" | grep -q "200\|307"; then
            log_success "Health check OK"
        else
            log_warning "Health check avertissement (peut être normal au démarrage)"
        fi
    elif command -v nc &> /dev/null; then
        if nc -z localhost "$PORT" 2>/dev/null; then
            log_success "Port $PORT accessible"
        else
            log_warning "Port $PORT non accessible (encore en démarrage?)"
        fi
    fi
}

# Arrêter l'application
stop_app() {
    log_info "Arrêt de $APP_NAME..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        
        if ps -p "$PID" > /dev/null 2>&1; then
            # Arrêt gracieux
            kill -TERM "$PID" 2>/dev/null || true
            
            # Attendre 10 secondes
            sleep 10
            
            # Forcer si nécessaire
            if ps -p "$PID" > /dev/null 2>&1; then
                log_warning "Forçage de l'arrêt..."
                kill -KILL "$PID" 2>/dev/null || true
            fi
            
            log_success "$APP_NAME arrêté"
        else
            log_warning "Processus $PID non trouvé"
        fi
        
        rm -f "$PID_FILE"
    else
        log_warning "Aucun fichier PID trouvé"
        
        # Essayer de trouver et tuer les processus Streamlit
        pkill -f "streamlit run app.py" 2>/dev/null || true
    fi
}

# Redémarrer l'application
restart_app() {
    log_info "Redémarrage de $APP_NAME..."
    stop_app
    sleep 2
    start_app
}

# Afficher le statut
status_app() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "=============================================="
            echo "  $APP_NAME - Statut"
            echo "=============================================="
            echo "  Status: 🟢 EN LIGNE"
            echo "  PID: $PID"
            echo "  Port: $PORT"
            echo "  URL: http://localhost:$PORT"
            echo "  Logs: $LOG_DIR/"
            echo "=============================================="
            
            # Afficher les ressources utilisées
            if command -v ps &> /dev/null; then
                echo ""
                echo "Ressources:"
                ps -p "$PID" -o pid,ppid,%cpu,%mem,etime,command 2>/dev/null || true
            fi
        else
            echo "=============================================="
            echo "  $APP_NAME - Statut"
            echo "=============================================="
            echo "  Status: 🔴 ARRÊTÉ (PID obsolète)"
            echo "=============================================="
            rm -f "$PID_FILE"
        fi
    else
        echo "=============================================="
        echo "  $APP_NAME - Statut"
        echo "=============================================="
        echo "  Status: 🔴 ARRÊTÉ"
        echo "=============================================="
    fi
}

# Afficher les logs
tail_logs() {
    log_info "Affichage des logs (Ctrl+C pour quitter)..."
    
    if [ -f "$APP_LOG" ]; then
        tail -f "$APP_LOG"
    else
        log_error "Fichier de log non trouvé: $APP_LOG"
    fi
}

# Sauvegarder la base de données
backup_db() {
    log_info "Sauvegarde de la base de données..."
    
    BACKUP_DIR="Data/backups"
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/finance_backup_$TIMESTAMP.db"
    
    if [ -f "Data/finance.db" ]; then
        cp "Data/finance.db" "$BACKUP_FILE"
        gzip "$BACKUP_FILE"
        log_success "Sauvegarde créée: ${BACKUP_FILE}.gz"
    else
        log_warning "Base de données non trouvée"
    fi
}

# Menu d'aide
show_help() {
    cat <<EOF
FinancePerso - Script de Production
====================================

Usage: ./scripts/run_production.sh [commande] [options]

Commandes:
  start [port]     Démarrer l'application (port par défaut: 8501)
  stop             Arrêter l'application
  restart          Redémarrer l'application
  status           Afficher le statut
  logs             Afficher les logs en temps réel
  backup           Sauvegarder la base de données
  help             Afficher cette aide

Variables d'environnement:
  WORKERS          Nombre de workers (défaut: 4)
  TIMEOUT          Timeout en secondes (défaut: 120)
  MAX_REQUESTS     Max requêtes par worker (défaut: 10000)

Exemples:
  ./scripts/run_production.sh start
  ./scripts/run_production.sh start 8080
  WORKERS=8 ./scripts/run_production.sh start
  ./scripts/run_production.sh stop
  ./scripts/run_production.sh logs

EOF
}

# Point d'entrée principal
case "${1:-start}" in
    start)
        check_dependencies
        setup_directories
        check_running
        cleanup_logs
        optimize_database
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        status_app
        ;;
    logs)
        tail_logs
        ;;
    backup)
        backup_db
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Commande inconnue: $1"
        show_help
        exit 1
        ;;
esac
