import os
import shutil
from datetime import datetime

import streamlit as st

from modules.db.connection import DB_PATH
from modules.ui.feedback import (
    show_error,
    show_success,
    show_warning,
    toast_error,
    toast_info,
    toast_success,
    toast_warning,
)


def create_backup(label="manual"):
    """Create a backup of the database"""
    try:
        backup_dir = "Data/backups"
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"finance_backup_{label}_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        # Vérifier que la base source existe
        if not os.path.exists(DB_PATH):
            show_error("Base de données introuvable", icon="❌")
            return None

        shutil.copy2(DB_PATH, backup_path)

        # Vérifier que la sauvegarde a été créée
        if os.path.exists(backup_path):
            size_mb = os.path.getsize(backup_path) / (1024 * 1024)
            return {"path": backup_path, "filename": backup_filename, "size_mb": size_mb}
        else:
            show_error("La sauvegarde n'a pas pu être créée", icon="❌")
            return None

    except PermissionError as e:
        error_msg = f"Permission refusée : {e}"
        show_error(error_msg, icon="🔒")
        toast_error(f"❌ {error_msg}", icon="🔒")
        return None
    except Exception as e:
        error_msg = f"Erreur lors de la sauvegarde : {e}"
        show_error(error_msg, icon="❌")
        toast_error(f"❌ {error_msg[:80]}", icon="❌")
        return None


def list_backups():
    """List all available backups"""
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
    """Delete a specific backup file"""
    try:
        if os.path.exists(backup_path):
            os.remove(backup_path)
            return True
        return False
    except Exception as e:
        toast_error(f"❌ Erreur suppression : {str(e)[:50]}", icon="❌")
        return False


def render_backup_restore():
    """
    Render the Sauvegardes tab content.
    Create, list, and download database backups.
    """
    st.header("💾 Gestion des Sauvegardes")
    st.markdown("Protégez vos données en créant des sauvegardes régulières.")
    st.info(
        "💡 Les sauvegardes sont automatiques (1 par jour). Vous pouvez aussi en créer manuellement."
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
            "💾 Créer une sauvegarde maintenant",
            type="primary",
            use_container_width=True,
            key="backup_button_119",
        ):
            with st.spinner("🔄 Création de la sauvegarde en cours..."):
                result = create_backup(label="manual")

            if result:
                filename = result["filename"]
                size_mb = result["size_mb"]
                toast_success(f"✅ Sauvegarde créée : {filename} ({size_mb:.1f} MB)", icon="💾")
                show_success(f"✅ Sauvegarde créée : `{filename}` ({size_mb:.1f} MB)")
                st.rerun()
            else:
                toast_error("❌ Échec de la création de la sauvegarde", icon="❌")
                show_error("Impossible de créer la sauvegarde. Vérifiez les permissions.")

    with col_b2:
        if backups:
            # Option to clean old backups
            if len(backups) >= 5:
                if st.button(
                    "🗑️ Nettoyer les vieilles sauvegardes (garder les 5 dernières)",
                    use_container_width=True,
                    key="backup_button_140",
                ):
                    deleted = 0
                    for b in backups[5:]:
                        if delete_backup(b["path"]):
                            deleted += 1
                    if deleted > 0:
                        toast_success(f"🗑️ {deleted} sauvegarde(s) supprimée(s)", icon="🗑️")
                        st.rerun()
                    else:
                        toast_info("ℹ️ Aucune sauvegarde à supprimer", icon="ℹ️")

    st.divider()
    st.subheader("📜 Historique des sauvegardes")

    if not backups:
        show_warning("Aucune sauvegarde trouvée. Créez votre première sauvegarde !", icon="⚠️")
        toast_warning("⚠️ Aucune sauvegarde disponible", icon="⚠️")
    else:
        # Table Header
        c1, c2, c3, c4 = st.columns([3, 1.5, 1, 1])
        c1.markdown("**📄 Fichier**")
        c2.markdown("**📅 Date**")
        c3.markdown("**💾 Taille**")
        c4.markdown("**⬇️ Action**")

        st.divider()

        for b in backups:
            with st.container():
                col_file, col_date, col_size, col_action = st.columns([3, 1.5, 1, 1])

                # Filename with icon based on type
                icon = "🤖" if "auto" in b["filename"] else "💾"
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
                                label="⬇️",
                                data=f,
                                file_name=b["filename"],
                                mime="application/x-sqlite3",
                                key=f"dl_{b['filename']}",
                                help=f"Télécharger {b['filename']}",
                            )
                    except Exception:
                        st.button(
                            "❌",
                            disabled=True,
                            help="Fichier inaccessible",
                            key="backup_button_194",
                        )

        # Footer info
        st.divider()
        if len(backups) >= 10:
            st.caption(
                "📌 Affichage des 10 dernières sauvegardes. Les plus anciennes sont cachées mais toujours disponibles."
            )
        elif len(backups) > 0:
            st.caption(f"📌 {len(backups)} sauvegarde(s) disponible(s).")

        # Storage location
        backup_dir = os.path.abspath("Data/backups")
        st.caption(f"📁 Emplacement : `{backup_dir}`")
