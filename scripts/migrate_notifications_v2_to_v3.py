#!/usr/bin/env python3
"""
Migration des préférences notifications V2 → V3
===============================================

Usage:
    python scripts/migrate_notifications_v2_to_v3.py [--dry-run] [--skip-history]

Ce script migre:
1. Les préférences V2 (table settings ou app_settings) vers notification_preferences
2. L'historique des notifications depuis notifications_v2.json (optionnel)

Mappings V2 → V3:
- notif_enabled → critical_enabled, warning_enabled, info_enabled, success_enabled, achievement_enabled
- notif_threshold_warning → budget_warning_threshold
- notif_threshold_critical → budget_critical_threshold
- notif_desktop → desktop_enabled
- notif_email_enabled → email_enabled
- notif_email_to → email_address
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.db.connection import get_db_connection
from modules.logger import logger


# Mapping des clés V2 vers les champs V3
V2_TO_V3_MAPPING = {
    # Seuils
    "notif_threshold_warning": ("budget_warning_threshold", int, 80),
    "notif_threshold_critical": ("budget_critical_threshold", int, 100),
    "notif_threshold_notice": ("budget_warning_threshold", int, 80),  # Fallback
    
    # Canaux
    "notif_desktop": ("desktop_enabled", bool, True),
    "notif_email_enabled": ("email_enabled", bool, False),
    "notif_email_to": ("email_address", str, None),
    
    # Activation globale (décomposée par niveau)
    "notif_enabled": ("all_levels", bool, False),
}

# Valeurs par défaut pour V3
V3_DEFAULTS = {
    "critical_enabled": True,
    "warning_enabled": True,
    "info_enabled": True,
    "success_enabled": True,
    "achievement_enabled": True,
    "desktop_enabled": True,
    "email_enabled": False,
    "sms_enabled": False,
    "email_address": None,
    "budget_warning_threshold": 80,
    "budget_critical_threshold": 100,
    "daily_digest_enabled": True,
    "weekly_summary_enabled": True,
    "type_preferences_json": "{}",
}


def parse_bool(value):
    """Parse une valeur booléenne depuis différents formats."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("true", "1", "yes", "on", "enabled")


def get_v2_settings_from_db(conn: sqlite3.Connection) -> Dict[str, str]:
    """Récupère les paramètres V2 depuis la base de données."""
    cursor = conn.cursor()
    settings = {}
    
    # Essayer d'abord la table settings
    try:
        cursor.execute("SELECT key, value FROM settings WHERE key LIKE 'notif_%'")
        rows = cursor.fetchall()
        settings = {row[0]: row[1] for row in rows}
        if settings:
            logger.info(f"✅ Trouvé {len(settings)} paramètres V2 dans 'settings'")
    except sqlite3.OperationalError:
        logger.debug("Table 'settings' non trouvée ou inaccessible")
    
    # Essayer ensuite app_settings
    try:
        cursor.execute("SELECT key, value FROM app_settings WHERE key LIKE 'notif_%'")
        rows = cursor.fetchall()
        app_settings = {row[0]: row[1] for row in rows}
        if app_settings:
            logger.info(f"✅ Trouvé {len(app_settings)} paramètres V2 dans 'app_settings'")
            settings.update(app_settings)
    except sqlite3.OperationalError:
        logger.debug("Table 'app_settings' non trouvée ou inaccessible")
    
    return settings


def get_v2_settings_from_json() -> Dict[str, str]:
    """Récupère les paramètres V2 depuis un fichier JSON éventuel."""
    json_paths = [
        Path("Data/notifications_v2.json"),
        Path("Data/settings.json"),
        Path("Data/notification_settings.json"),
    ]
    
    for path in json_paths:
        if path.exists():
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                
                # Extraire les paramètres notif_ si présents
                if isinstance(data, dict):
                    settings = {
                        k: str(v) for k, v in data.items()
                        if k.startswith("notif_")
                    }
                    if settings:
                        logger.info(f"✅ Trouvé {len(settings)} paramètres V2 dans '{path}'")
                        return settings
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Impossible de lire {path}: {e}")
    
    return {}


def ensure_notification_preferences_table(conn: sqlite3.Connection) -> bool:
    """S'assure que la table notification_preferences existe."""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_preferences (
                user_id INTEGER DEFAULT 1 PRIMARY KEY,
                critical_enabled BOOLEAN DEFAULT 1,
                warning_enabled BOOLEAN DEFAULT 1,
                info_enabled BOOLEAN DEFAULT 1,
                success_enabled BOOLEAN DEFAULT 1,
                achievement_enabled BOOLEAN DEFAULT 1,
                type_preferences_json TEXT DEFAULT '{}' CHECK (json_valid(type_preferences_json)),
                desktop_enabled BOOLEAN DEFAULT 1,
                email_enabled BOOLEAN DEFAULT 0,
                sms_enabled BOOLEAN DEFAULT 0,
                email_address TEXT,
                budget_warning_threshold INTEGER DEFAULT 80,
                budget_critical_threshold INTEGER DEFAULT 100,
                daily_digest_enabled BOOLEAN DEFAULT 1,
                weekly_summary_enabled BOOLEAN DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index pour performances
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notif_prefs_user 
            ON notification_preferences(user_id)
        """)
        
        # Insertion des préférences par défaut si non existantes
        cursor.execute("""
            INSERT OR IGNORE INTO notification_preferences (user_id) VALUES (1)
        """)
        
        conn.commit()
        logger.info("✅ Table notification_preferences vérifiée/créée")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"❌ Erreur création table notification_preferences: {e}")
        return False


def migrate_v2_to_v3(
    conn: sqlite3.Connection,
    v2_settings: Dict[str, str],
    dry_run: bool = False
) -> Dict[str, Any]:
    """Migre les paramètres V2 vers V3."""
    
    # Initialiser avec les valeurs par défaut V3
    v3_values = V3_DEFAULTS.copy()
    migrated_keys = []
    
    # Traiter chaque paramètre V2
    for v2_key, v2_value in v2_settings.items():
        if v2_key in V2_TO_V3_MAPPING:
            v3_field, converter, default = V2_TO_V3_MAPPING[v2_key]
            
            try:
                if converter == bool:
                    converted_value = parse_bool(v2_value)
                elif converter == int:
                    converted_value = int(v2_value) if v2_value else default
                else:
                    converted_value = v2_value if v2_value else default
                
                # Cas spécial: notif_enabled active/désactive tous les niveaux
                if v3_field == "all_levels":
                    v3_values["critical_enabled"] = converted_value
                    v3_values["warning_enabled"] = converted_value
                    v3_values["info_enabled"] = converted_value
                    v3_values["success_enabled"] = converted_value
                    v3_values["achievement_enabled"] = converted_value
                else:
                    v3_values[v3_field] = converted_value
                
                migrated_keys.append({
                    "v2_key": v2_key,
                    "v2_value": v2_value,
                    "v3_field": v3_field,
                    "v3_value": converted_value
                })
                
            except (ValueError, TypeError) as e:
                logger.warning(f"⚠️ Impossible de convertir {v2_key}={v2_value}: {e}")
    
    # Sauvegarder dans la base de données
    if not dry_run:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO notification_preferences (
                    user_id,
                    critical_enabled,
                    warning_enabled,
                    info_enabled,
                    success_enabled,
                    achievement_enabled,
                    type_preferences_json,
                    desktop_enabled,
                    email_enabled,
                    sms_enabled,
                    email_address,
                    budget_warning_threshold,
                    budget_critical_threshold,
                    daily_digest_enabled,
                    weekly_summary_enabled,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                1,  # user_id
                v3_values["critical_enabled"],
                v3_values["warning_enabled"],
                v3_values["info_enabled"],
                v3_values["success_enabled"],
                v3_values["achievement_enabled"],
                v3_values["type_preferences_json"],
                v3_values["desktop_enabled"],
                v3_values["email_enabled"],
                v3_values["sms_enabled"],
                v3_values["email_address"],
                v3_values["budget_warning_threshold"],
                v3_values["budget_critical_threshold"],
                v3_values["daily_digest_enabled"],
                v3_values["weekly_summary_enabled"],
                datetime.now().isoformat(),
            ))
            conn.commit()
            logger.info(f"✅ Préférences V3 sauvegardées ({len(migrated_keys)} paramètres)")
        except sqlite3.Error as e:
            logger.error(f"❌ Erreur sauvegarde préférences V3: {e}")
            raise
    
    return {
        "migrated_count": len(migrated_keys),
        "migrated_keys": migrated_keys,
        "v3_values": v3_values,
    }


def migrate_notification_history(
    conn: sqlite3.Connection,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Migre l'historique des notifications depuis notifications_v2.json."""
    
    json_path = Path("Data/notifications_v2.json")
    
    if not json_path.exists():
        logger.info("ℹ️ Aucun fichier notifications_v2.json trouvé")
        return {"migrated_count": 0, "skipped": True}
    
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"❌ Impossible de lire notifications_v2.json: {e}")
        return {"migrated_count": 0, "error": str(e)}
    
    # S'assurer que la table notifications existe
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                level TEXT NOT NULL CHECK (level IN ('critical', 'warning', 'info', 'success', 'achievement')),
                type TEXT NOT NULL,
                title TEXT,
                message TEXT NOT NULL,
                icon TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                dismissed_at TIMESTAMP,
                expires_at TIMESTAMP,
                category TEXT,
                source TEXT,
                actions_json TEXT CHECK (json_valid(actions_json)),
                metadata_json TEXT CHECK (json_valid(metadata_json)),
                user_id INTEGER DEFAULT 1,
                dedup_key TEXT,
                is_read BOOLEAN DEFAULT 0,
                is_dismissed BOOLEAN DEFAULT 0,
                is_pinned BOOLEAN DEFAULT 0
            )
        """)
        
        # Index pour performances
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_user_read 
            ON notifications(user_id, is_read, created_at DESC)
        """)
        
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"❌ Erreur création table notifications: {e}")
        return {"migrated_count": 0, "error": str(e)}
    
    # Extraire l'historique
    history = []
    if isinstance(data, dict):
        history = data.get("history", [])
    elif isinstance(data, list):
        history = data
    
    if not history:
        logger.info("ℹ️ Aucune notification dans l'historique V2")
        return {"migrated_count": 0, "skipped": True}
    
    # Mapper les niveaux V2 vers V3
    level_mapping = {
        "high": "critical",
        "medium": "warning",
        "low": "info",
        "success": "success",
        "achievement": "achievement",
        "info": "info",
        "warning": "warning",
        "critical": "critical",
    }
    
    migrated_count = 0
    error_count = 0
    
    if not dry_run:
        for notif in history:
            try:
                # Mapper les champs V2 vers V3
                notif_id = notif.get("id") or f"migrated_{datetime.now().timestamp()}_{migrated_count}"
                level = level_mapping.get(notif.get("level", "info"), "info")
                notif_type = notif.get("type", "general")
                title = notif.get("title", "")
                message = notif.get("message", "")
                icon = notif.get("icon", "")
                created_at = notif.get("created_at", datetime.now().isoformat())
                read = notif.get("read", False)
                dismissed = notif.get("dismissed", False)
                
                cursor.execute("""
                    INSERT OR IGNORE INTO notifications (
                        id, level, type, title, message, icon,
                        created_at, is_read, is_dismissed, user_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    notif_id, level, notif_type, title, message, icon,
                    created_at, read, dismissed, 1
                ))
                migrated_count += 1
                
            except (sqlite3.Error, KeyError, TypeError) as e:
                logger.warning(f"⚠️ Erreur migration notification: {e}")
                error_count += 1
        
        conn.commit()
    
    logger.info(f"✅ Historique migré: {migrated_count} notifications ({error_count} erreurs)")
    
    return {
        "migrated_count": migrated_count,
        "error_count": error_count,
        "total_in_file": len(history),
    }


def generate_migration_report(
    conn: sqlite3.Connection,
    migration_result: dict,
    history_result: dict,
) -> Dict[str, Any]:
    """Génère un rapport de migration."""
    cursor = conn.cursor()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "preferences_migrated": migration_result.get("migrated_count", 0),
        "history_migrated": history_result.get("migrated_count", 0),
        "v3_values": migration_result.get("v3_values", {}),
    }
    
    # Vérifier l'état final
    try:
        cursor.execute("SELECT COUNT(*) FROM notification_preferences")
        report["total_v3_preferences"] = cursor.fetchone()[0]
    except sqlite3.Error:
        report["total_v3_preferences"] = 0
    
    try:
        cursor.execute("SELECT COUNT(*) FROM notifications")
        report["total_v3_notifications"] = cursor.fetchone()[0]
    except sqlite3.Error:
        report["total_v3_notifications"] = 0
    
    return report


def print_report(report: Dict[str, Any]) -> None:
    """Affiche le rapport de migration."""
    print("\n" + "=" * 70)
    print("RAPPORT DE MIGRATION NOTIFICATIONS V2 → V3")
    print("=" * 70)
    print(f"Timestamp: {report['timestamp']}")
    print(f"\n📊 Préférences:")
    print(f"   - Paramètres V2 migrés: {report['preferences_migrated']}")
    print(f"   - Entrées V3 finales: {report['total_v3_preferences']}")
    
    print(f"\n📨 Historique:")
    print(f"   - Notifications migrées: {report['history_migrated']}")
    print(f"   - Notifications V3 finales: {report['total_v3_notifications']}")
    
    print(f"\n⚙️ Configuration V3:")
    v3_values = report.get("v3_values", {})
    print(f"   - Critical enabled: {v3_values.get('critical_enabled', True)}")
    print(f"   - Warning enabled: {v3_values.get('warning_enabled', True)}")
    print(f"   - Info enabled: {v3_values.get('info_enabled', True)}")
    print(f"   - Desktop enabled: {v3_values.get('desktop_enabled', True)}")
    print(f"   - Email enabled: {v3_values.get('email_enabled', False)}")
    print(f"   - Budget warning threshold: {v3_values.get('budget_warning_threshold', 80)}%")
    print(f"   - Budget critical threshold: {v3_values.get('budget_critical_threshold', 100)}%")
    
    print("\n" + "=" * 70)


def main():
    """Point d'entrée principal du script de migration."""
    parser = argparse.ArgumentParser(
        description="Migration des préférences notifications V2 → V3"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Simulation sans modification de la base de données"
    )
    parser.add_argument(
        "--skip-history",
        action="store_true",
        help="Ne pas migrer l'historique des notifications"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Utiliser uniquement les fichiers JSON (pas la DB V2)"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("⚠️  MODE DRY-RUN - Aucune modification ne sera effectuée\n")
    
    logger.info("🚀 Démarrage de la migration notifications V2 → V3")
    
    try:
        with get_db_connection() as conn:
            # Étape 1: S'assurer que la table V3 existe
            logger.info("📦 Vérification de la structure V3...")
            if not ensure_notification_preferences_table(conn):
                logger.error("❌ Impossible de créer la table notification_preferences")
                return 1
            
            # Étape 2: Récupérer les paramètres V2
            logger.info("🔍 Recherche des paramètres V2...")
            
            if args.json_only:
                v2_settings = get_v2_settings_from_json()
            else:
                v2_settings = get_v2_settings_from_db(conn)
                if not v2_settings:
                    logger.info("ℹ️ Aucun paramètre V2 dans la DB, recherche dans JSON...")
                    v2_settings = get_v2_settings_from_json()
            
            if not v2_settings:
                logger.warning("⚠️ Aucun paramètre V2 trouvé, utilisation des valeurs par défaut V3")
            else:
                logger.info(f"✅ Trouvé {len(v2_settings)} paramètres V2")
            
            # Étape 3: Migrer les préférences
            logger.info("🔄 Migration des préférences...")
            migration_result = migrate_v2_to_v3(conn, v2_settings, args.dry_run)
            
            if migration_result["migrated_count"] > 0:
                logger.info(f"✅ {migration_result['migrated_count']} paramètres migrés")
            
            # Étape 4: Migrer l'historique (si demandé)
            history_result = {"migrated_count": 0, "skipped": True}
            if not args.skip_history:
                logger.info("🔄 Migration de l'historique...")
                history_result = migrate_notification_history(conn, args.dry_run)
            else:
                logger.info("⏭️ Migration de l'historique ignorée")
            
            # Étape 5: Générer et afficher le rapport
            if not args.dry_run:
                report = generate_migration_report(conn, migration_result, history_result)
                print_report(report)
            else:
                print("\n" + "=" * 70)
                print("SIMULATION (DRY-RUN)")
                print("=" * 70)
                print(f"\nParamètres V2 trouvés: {len(v2_settings)}")
                print(f"Paramètres à migrer: {migration_result['migrated_count']}")
                print("\nMappings:")
                for mapping in migration_result.get("migrated_keys", []):
                    print(f"  {mapping['v2_key']} = {mapping['v2_value']} → {mapping['v3_field']} = {mapping['v3_value']}")
                print("\nValeurs V3 finales:")
                for key, value in migration_result.get("v3_values", {}).items():
                    print(f"  {key} = {value}")
                print("=" * 70)
            
            if args.dry_run:
                logger.info("✅ Simulation terminée")
            else:
                logger.info("✅ Migration terminée avec succès!")
            
            return 0
            
    except Exception as e:
        logger.error(f"❌ Erreur fatale lors de la migration: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
