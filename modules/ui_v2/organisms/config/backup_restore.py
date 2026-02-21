"""Backup and restore UI component.

Provides UI for creating, listing, and downloading database backups.
"""

import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional

import streamlit as st

from modules.db.connection import DB_PATH
from modules.ui_v2.atoms.icons import IconSet
from modules.ui_v2.molecules.banners import show_error, show_success, show_warning
from modules.ui_v2.molecules.toasts import toast_error, toast_info, toast_success, toast_warning


def create_backup(label: str = "manual") -> Optional[Dict]:
    """Create a backup of the database.

    Args:
        label: Label for the backup (e.g., 'manual', 'auto')

    Returns:
        Dict with backup info or None if failed
    """
    try:
        backup_dir = "Data/backups"
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"finance_backup_{label}_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        # Vérifier que la base source existe
        if not os.path.exists(DB_PATH):
            show_error("Base de données introuvable", icon=IconSet.ERROR.value)
            return None

        shutil.copy2(DB_PATH, backup_path)

        # Vérifier que la sauvegarde a été créée
        if os.path.exists(backup_path):
            size_mb = os.path.getsize(backup_path) / (1024 * 1024)
            return {"path": backup_path, "filename": backup_filename, "size_mb": size_mb}
        else:
            show_error("La sauvegarde n'a pas pu être créée", icon=IconSet.ERROR.value)
            return None

    except PermissionError as e:
        error_msg = f"Permission refusée : {e}"
        show_error(error_msg, icon=IconSet.LOCKED.value)
        toast_error(f"{IconSet.ERROR.value} {error_msg}", icon=IconSet.LOCKED.value)
        return None
    except Exception as e:
        error_msg = f"Erreur lors de la sauvegarde : {e}"
        show_error(error_msg, icon=IconSet.ERROR.value)
        toast_error(f"{IconSet.ERROR.value} {error_msg[:80]}", icon=IconSet.ERROR.value)
        return None


def list_backups() -> List[Dict]:
    """List all available backups.

    Returns:
        List of backup dicts with filename, path, date, and size
    """
    backup_dir = "Data/backups"
    if not os.path.exists(backup_dir):
        return []

    backups = []
    for filename in sorted(os.listdir(backup_dir), reverse=True):
        if filename.endswith(".db"):
            path = os.path.join(backup_dir, filename)
            try:
                stat = os.stat(path)
                size_mb = stat.st_size / (1024 * 1024)
                backups.append(
                    {
                        "filename": filename,
                        "path": path,
                        "date": datetime.fromtimestamp(stat.st_mtime),
                        "size_mb": size_mb,
                    }
                )
            except Exception:
                # Ignorer les fichiers inaccessibles
                continue

    return backups[:10]  # Last 10 backups


def delete_backup(backup_path: str) -> bool:
    """Delete a specific backup file.

    Args:
        backup_path: Path to the backup file

    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        if os.path.exists(backup_path):
            os.remove(backup_path)
            return True
        return False
    except Exception as e:
        toast_error(f"{IconSet.ERROR.value} Erreur suppression : {str(e)[:50]}", icon=IconSet.ERROR.value)
        return False


def render_backup_restore() -> None:
    """
    Render the Sauvegardes tab content.
    Create, list, and download database backups.
    """
    st.header(f"{IconSet.SAVE.value} Gestion des Sauvegardes")
    st.markdown("Protégez vos données en créant des sauvegardes régulières.")
    st.info(
        f"{IconSet.LIGHTBULB.value} Les sauvegardes sont automatiques (1 par jour). Vous pouvez aussi en créer manuellement."
    )

    # Stats
    backups = list_backups()
    if backups:
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Sauvegardes disponibles", len(backups))
        with col_stats2:
            latest = backups[0]["date"] if backups else None
            latest_str = latest.strftime("%d/%m/%Y %H:%M") if latest else "Aucune"
            st.metric("Dernière sauvegarde", latest_str)
        with col_stats3:
            total_size = sum(b["size_mb"] for b in backups)
            st.metric("Espace utilisé", f"{total_size:.1f} MB")

    st.divider()

    col_b1, col_b2 = st.columns([1, 2])
    with col_b1:
        if st.button(
            f"{IconSet.SAVE.value} Créer une sauvegarde maintenant",
            type="primary",
            use_container_width=True,
            key="backup_button_119",
        ):
            with st.spinner(f"{IconSet.REFRESH.value} Création de la sauvegarde en cours..."):
                result = create_backup(label="manual")

            if result:
                filename = result["filename"]
                size_mb = result["size_mb"]
                toast_success(f"{IconSet.SUCCESS.value} Sauvegarde créée : {filename} ({size_mb:.1f} MB)", icon=IconSet.SAVE.value)
                show_success(f"{IconSet.SUCCESS.value} Sauvegarde créée : `{filename}` ({size_mb:.1f} MB)")
                st.rerun()
            else:
                toast_error(f"{IconSet.ERROR.value} Échec de la création de la sauvegarde", icon=IconSet.ERROR.value)
                show_error("Impossible de créer la sauvegarde. Vérifiez les permissions.")

    with col_b2:
        if backups:
            # Option to clean old backups
            if len(backups) >= 5:
                if st.button(
                    f"{IconSet.DELETE.value} Nettoyer les vieilles sauvegardes (garder les 5 dernières)",
                    use_container_width=True,
                    key="backup_button_140",
                ):
                    deleted = 0
                    for b in backups[5:]:
                        if delete_backup(b["path"]):
                            deleted += 1
                    if deleted > 0:
                        toast_success(f"{IconSet.DELETE.value} {deleted} sauvegarde(s) supprimée(s)", icon=IconSet.DELETE.value)
                        st.rerun()
                    else:
                        toast_info(f"{IconSet.INFO.value} Aucune sauvegarde à supprimer", icon=IconSet.INFO.value)

    st.divider()
    st.subheader(f"{IconSet.HISTORY.value} Historique des sauvegardes")

    if not backups:
        show_warning("Aucune sauvegarde trouvée. Créez votre première sauvegarde !", icon=IconSet.WARNING.value)
        toast_warning(f"{IconSet.WARNING.value} Aucune sauvegarde disponible", icon=IconSet.WARNING.value)
    else:
        # Table Header
        c1, c2, c3, c4 = st.columns([3, 1.5, 1, 1])
        c1.markdown(f"**{IconSet.FILE.value} Fichier**")
        c2.markdown(f"**{IconSet.CALENDAR.value} Date**")
        c3.markdown(f"**{IconSet.SAVE.value} Taille**")
        c4.markdown(f"**{IconSet.DOWNLOAD.value} Action**")

        st.divider()

        for b in backups:
            with st.container():
                col_file, col_date, col_size, col_action = st.columns([3, 1.5, 1, 1])

                # Filename with icon based on type
                icon = IconSet.SETTINGS.value if "auto" in b["filename"] else IconSet.SAVE.value
                col_file.markdown(f"{icon} `{b['filename']}`")

                # Date
                col_date.text(b["date"].strftime("%d/%m/%Y %H:%M"))

                # Size
                col_size.text(f"{b['size_mb']:.1f} MB")

                # Download Button
                with col_action:
                    try:
                        with open(b["path"], "rb") as f:
                            st.download_button(
                                label=f"{IconSet.DOWNLOAD.value}",
                                data=f,
                                file_name=b["filename"],
                                mime="application/x-sqlite3",
                                key=f"dl_{b['filename']}",
                                help=f"Télécharger {b['filename']}",
                            )
                    except Exception:
                        st.button(
                            IconSet.ERROR.value,
                            disabled=True,
                            help="Fichier inaccessible",
                            key="backup_button_194",
                        )

        # Footer info
        st.divider()
        if len(backups) >= 10:
            st.caption(
                f"{IconSet.PIN.value} Affichage des 10 dernières sauvegardes. Les plus anciennes sont cachées mais toujours disponibles."
            )
        elif len(backups) > 0:
            st.caption(f"{IconSet.PIN.value} {len(backups)} sauvegarde(s) disponible(s).")

        # Storage location
        backup_dir = os.path.abspath("Data/backups")
        st.caption(f"{IconSet.FOLDER.value} Emplacement : `{backup_dir}`")
