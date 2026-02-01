import streamlit as st
import os
from modules.logger import LOG_FILE, LOG_DIR

def render_log_viewer():
    """
    Render the Logs tab content.
    Displays application logs with filtering and clearing capabilities.
    """
    st.header("📑 Journaux Système (Logs)")
    st.markdown("Consultez l'activité de l'application et diagnostiquez les éventuels problèmes.")
    
    # Show log file path
    st.caption(f"Fichier: `{LOG_FILE}`")
    
    if not os.path.exists(LOG_FILE):
        st.info("📭 Aucun fichier de log trouvé.")
        st.info("💡 Les logs apparaîtront ici après le prochain démarrage de l'application ou la prochaine action.")
        
        # Show log directory status
        if os.path.exists(LOG_DIR):
            st.success(f"✅ Le répertoire `{LOG_DIR}/` existe.")
        else:
            st.warning(f"⚠️ Le répertoire `{LOG_DIR}/` sera créé automatiquement.")
        return
    
    # File exists - show stats
    file_size = os.path.getsize(LOG_FILE)
    file_size_kb = file_size / 1024
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taille", f"{file_size_kb:.1f} KB")
    with col2:
        # Count lines
        with open(LOG_FILE, "r", encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        st.metric("Lignes", line_count)
    with col3:
        # Last modified
        mtime = os.path.getmtime(LOG_FILE)
        from datetime import datetime
        last_mod = datetime.fromtimestamp(mtime).strftime('%d/%m %H:%M')
        st.metric("Modifié", last_mod)
    
    # Filters
    st.divider()
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        level_filter = st.multiselect(
            "Niveau de log",
            options=["INFO", "WARNING", "ERROR", "DEBUG"],
            default=["INFO", "WARNING", "ERROR"],
            help="Filtrer par niveau de sévérité"
        )
    
    with col_filter2:
        search = st.text_input("🔍 Recherche texte", placeholder="Error, DB, Ingestion...")
    
    # Load and filter logs
    with open(LOG_FILE, "r", encoding='utf-8') as f:
        logs = f.readlines()
    
    # Apply filters
    filtered_logs = logs
    
    # Level filter
    if level_filter:
        filtered_logs = [l for l in filtered_logs if any(level in l for level in level_filter)]
    
    # Text search filter
    if search:
        filtered_logs = [l for l in filtered_logs if search.lower() in l.lower()]
    
    # Show results
    st.divider()
    
    if not filtered_logs:
        st.info("Aucun log ne correspond aux filtres.")
        return
    
    # Slider for number of lines (only if no search filter - otherwise show all matches)
    if not search:
        num_lines = st.slider("Nombre de lignes à afficher", 10, min(500, len(filtered_logs)), min(100, len(filtered_logs)))
        display_logs = filtered_logs[-num_lines:]
    else:
        display_logs = filtered_logs
        st.caption(f"{len(display_logs)} ligne(s) trouvée(s)")
    
    # Colorize log levels
    colored_logs = []
    for line in display_logs:
        if "ERROR" in line:
            line = f"🔴 {line}"
        elif "WARNING" in line:
            line = f"🟡 {line}"
        elif "INFO" in line:
            line = f"🔵 {line}"
        colored_logs.append(line)
    
    st.text_area(
        "Logs",
        value="".join(colored_logs),
        height=400,
        key="log_display",
        help="Derniers événements de l'application"
    )
    
    # Actions
    st.divider()
    col_actions1, col_actions2 = st.columns(2)
    
    with col_actions1:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.rerun()
    
    with col_actions2:
        if st.button("🗑️ Effacer les logs", use_container_width=True, type="secondary"):
            with open(LOG_FILE, "w", encoding='utf-8') as f:
                f.write("")
            st.toast("Logs effacés !", icon="🗑️")
            st.rerun()
