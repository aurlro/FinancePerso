import streamlit as st
import os
import shutil
import sqlite3
from datetime import datetime
from modules.data_manager import DB_PATH

def create_backup(label="manual"):
    """Create a backup of the database"""
    try:
        backup_dir = "Data/backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"finance_backup_{label}_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        shutil.copy2(DB_PATH, backup_path)
        return backup_path
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")
        return None

def list_backups():
    """List all available backups"""
    backup_dir = "Data/backups"
    if not os.path.exists(backup_dir):
        return []
    
    backups = []
    for filename in sorted(os.listdir(backup_dir), reverse=True):
        if filename.endswith('.db'):
            path = os.path.join(backup_dir, filename)
            stat = os.stat(path)
            backups.append({
                'filename': filename,
                'path': path,
                'date': datetime.fromtimestamp(stat.st_mtime),
                'size': stat.st_size
            })
    
    return backups[:10]  # Last 10 backups

def render_backup_restore():
    """
    Render the Sauvegardes tab content.
    Create, list, and download database backups.
   """
    st.header("Gestion des Sauvegardes")
    st.info("Les sauvegardes sont automatiques (1 par jour). Vous pouvez aussi en créer manuellement.")
    
    col_b1, col_b2 = st.columns([1, 2])
    with col_b1:
        if st.button("💾 Créer une sauvegarde maintenant", type="primary", use_container_width=True):
            path = create_backup(label="manual")
            if path:
                st.success(f"Sauvegarde créée : {os.path.basename(path)}")
                st.rerun()
            else:
                st.error("Erreur lors de la création de la sauvegarde.")
    
    st.divider()
    st.subheader("Historique")
    
    backups = list_backups()
    if not backups:
        st.warning("Aucune sauvegarde trouvée.")
    else:
        # Table Header
        c1, c2, c3 = st.columns([3, 2, 2])
        c1.markdown("**Fichier**")
        c2.markdown("**Date**")
        c3.markdown("**Action**")
        
        for b in backups:
            with st.container():
                col_file, col_date, col_action = st.columns([3, 2, 2])
                col_file.markdown(f"📄 `{b['filename']}`")
                col_date.text(b['date'].strftime('%d/%m/%Y %H:%M'))
                
                with col_action:
                    # Download Button
                    with open(b['path'], "rb") as f:
                        st.download_button(
                            label="⬇️ Télécharger",
                            data=f,
                            file_name=b['filename'],
                            mime="application/x-sqlite3",
                            key=f"dl_{b['filename']}"
                        )
        
        if len(backups) >= 10:
            st.caption("Affichage des 10 dernières sauvegardes.")
