import os
import shutil
import datetime
from modules.logger import logger

DB_PATH = "Data/finance.db"
BACKUP_DIR = "Data/backups"

def ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        logger.info(f"Dossier de sauvegarde créé : {BACKUP_DIR}")

def create_backup(label="auto"):
    """Creates a timestamped backup of the database."""
    ensure_backup_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"finance_{timestamp}_{label}.db")
    
    try:
        shutil.copy2(DB_PATH, backup_path)
        logger.info(f"Sauvegarde créée : {backup_path}")
        cleanup_old_backups()
        return backup_path
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde : {e}")
        return None

def auto_backup_daily():
    """Creates a backup if none exists for today."""
    ensure_backup_dir()
    today_prefix = datetime.datetime.now().strftime("finance_%Y%m%d")
    
    backups = os.listdir(BACKUP_DIR)
    already_done = any(f.startswith(today_prefix) for f in backups)
    
    if not already_done:
        logger.info("Première utilisation du jour, lancement de la sauvegarde automatique...")
        create_backup(label="daily")

def cleanup_old_backups(days=365):
    """Deletes backups older than the specified number of days."""
    ensure_backup_dir()
    now = datetime.datetime.now()
    threshold = now - datetime.timedelta(days=days)
    
    for filename in os.listdir(BACKUP_DIR):
        if not filename.endswith(".db"):
            continue
            
        file_path = os.path.join(BACKUP_DIR, filename)
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        
        if file_time < threshold:
            try:
                os.remove(file_path)
                logger.info(f"Ancienne sauvegarde supprimée : {filename}")
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage : {e}")

def list_backups():
    """Returns a list of available backups sorted by date (newest first)."""
    ensure_backup_dir()
    backups = []
    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith(".db"):
            path = os.path.join(BACKUP_DIR, filename)
            stats = os.stat(path)
            backups.append({
                "filename": filename,
                "path": path,
                "size": stats.st_size,
                "date": datetime.datetime.fromtimestamp(stats.st_mtime)
            })
    
    return sorted(backups, key=lambda x: x['date'], reverse=True)

def restore_backup(backup_filename):
    """Restores a database from a backup file."""
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    if not os.path.exists(backup_path):
        return False, "Fichier de sauvegarde introuvable."
    
    try:
        # Create a safety backup of the current state before restoring
        create_backup(label="pre_restore_safety")
        
        # Restore
        shutil.copy2(backup_path, DB_PATH)
        logger.info(f"Base de données restaurée depuis : {backup_filename}")
        return True, "Restauration réussie. Veuillez redémarrer l'application ou rafraîchir la page."
    except Exception as e:
        logger.error(f"Erreur lors de la restauration : {e}")
        return False, str(e)
