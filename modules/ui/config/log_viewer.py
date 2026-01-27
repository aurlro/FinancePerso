import streamlit as st
import os

def render_log_viewer():
    """
    Render the Logs tab content.
    Displays application logs with filtering and clearing capabilities.
    """
    st.header("📑 Journaux Système (Logs)")
    st.markdown("Consultez l'activité de l'application et diagnostiquez les éventuels problèmes.")
    
    LOG_FILE = "app.log"
    
    if not os.path.exists(LOG_FILE):
        st.info("Aucun fichier de log trouvé.")
    else:
        with open(LOG_FILE, "r") as f:
            logs = f.readlines()
        
        # Show last 100 lines by default
        num_lines = st.slider("Nombre de lignes à afficher", 10, 500, 100)
        
        # Search filter
        search = st.text_input("Filtrer par mot-clé", placeholder="Error, DB, Ingestion...")
        
        filtered_logs = [l for l in logs if not search or search.lower() in l.lower()]
        
        st.text_area("Rendu brut", value="".join(filtered_logs[-num_lines:]), height=500)
        
        if st.button("Effacer les logs 🗑️", help="Vider le fichier log actuel"):
            with open(LOG_FILE, "w") as f:
                f.write("")
            st.success("Logs effacés !")
            st.rerun()
