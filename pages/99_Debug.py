"""
🐞 Debug & Santé des Données
Outils pour auditer les données, détecter les doublons et vérifier les règles.
"""
import streamlit as st
import pandas as pd
from modules.db.connection import get_db_connection
from modules.ui import load_css

st.set_page_config(page_title="Debug & Santé", page_icon="🐞", layout="wide")
load_css()

st.title("🐞 Debug & Santé des Données")

tabs = st.tabs(["🔍 Détecteur de Doublons", "📏 Audit des Règles", "🔧 Outils Système"])

with tabs[0]:
    st.header("🔍 Détecteur de Doublons (Cross-Account)")
    st.info("Recherche de transactions identiques (Date + Montant + Libellé) présentes sur plusieurs comptes différents.")
    
    if st.button("Lancer l'analyse"):
        with get_db_connection() as conn:
            query = """
                SELECT date, label, amount, COUNT(DISTINCT account_label) as accounts_count, 
                       GROUP_CONCAT(account_label, ', ') as accounts,
                       COUNT(*) as total_occurrences
                FROM transactions
                GROUP BY date, label, amount
                HAVING accounts_count > 1
            """
            duplicates = pd.read_sql(query, conn)
            
            if duplicates.empty:
                st.success("✅ Aucune collision inter-comptes détectée. Votre base est saine !")
            else:
                st.warning(f"⚠️ {len(duplicates)} transactions potentielles en doublon sur plusieurs comptes")
                st.dataframe(duplicates, use_container_width=True)
                
                with st.expander("Voir les détails des doublons"):
                    for _, row in duplicates.iterrows():
                        st.markdown(f"**{row['label']}** ({row['amount']} €) le {row['date']}")
                        st.caption(f"Présent sur : {row['accounts']}")
                        if st.button(f"Nettoyer {row['label'][:20]}...", key=f"clean_{row['label']}"):
                            # Logic to keep only one logic would go here
                            st.write("Fonction de nettoyage à implémenter si besoin.")

with tabs[1]:
    st.header("📏 Audit des Règles")
    from modules.db.rules import get_learning_rules
    rules = get_learning_rules()
    
    st.metric("Nombre de règles", len(rules))
    
    # Check for duplicate patterns
    duplicates_rules = rules[rules.duplicated(subset=['pattern'], keep=False)]
    if not duplicates_rules.empty:
        st.error("⚠️ Des règles ont des patterns identiques !")
        st.dataframe(duplicates_rules)
    else:
        st.success("✅ Pas de conflits de patterns directs.")
        
    st.subheader("Toutes les règles")
    st.dataframe(rules, use_container_width=True)

with tabs[2]:
    st.header("🔧 Outils Système")
    
    from modules.db.stats import get_global_stats
    stats = get_global_stats()
    st.json(stats)
    
    if st.button("Forcer le recalcul du cache", type="primary"):
        from modules.cache_manager import invalidate_transaction_caches
        invalidate_transaction_caches()
        st.success("Cache invalidé !")
