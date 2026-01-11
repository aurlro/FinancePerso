import streamlit as st
from modules.ingestion import load_transaction_file
from modules.data_manager import save_transactions, init_db
from modules.categorization import categorize_transaction
import pandas as pd

st.set_page_config(page_title="Import", page_icon="📥")

# Ensure DB is ready
init_db()

st.title("📥 Import des relevés")
st.markdown("Chargez vos fichiers CSV pour alimenter votre assistant.")

uploaded_file = st.file_uploader("Choisir un fichier CSV", type=['csv'])

if uploaded_file is not None:
    # Preview
    st.subheader("Prévisualisation")
    
    # Run ingestion
    try:
        df = load_transaction_file(uploaded_file)
        
        if isinstance(df, tuple): # Error case based on my implementation returning (None, error_msg)
             st.error(f"Erreur lors de la lecture : {df[1]}")
        elif df is not None:
            st.dataframe(df.head())
            st.info(f"{len(df)} transactions détectées.")
            
            # Auto-categorization
            if st.checkbox("Lancer la catégorisation automatique (Règles + IA)", value=True):
                with st.spinner("Analyse en cours..."):
                    # Apply categorization
                    # We use apply but we need to pass multiple columns.
                    # lambda row: categorize_transaction(row['label'], row['amount'], row['date'])
                    results = df.apply(lambda row: categorize_transaction(row['label'], row['amount'], row['date']), axis=1)
                    # results is a series of tuples (category, source, confidence)
                    
                    # Unpack
                    df['category_validated'] = results.apply(lambda x: x[0] if x[0] else 'Inconnu')
                    df['ai_confidence'] = results.apply(lambda x: x[2])
                    df['status'] = results.apply(lambda x: 'validated' if x[1] == 'rule' else 'pending') 
                    # If rule matched -> validated? Or still pending user review? 
                    # Plan says "Validation humaine". So maybe keep 'pending' but pre-fill category.
                    # Let's say: if high confidence rule -> validated? No, let's keep all as pending for review but pre-filled.
                    # Except maybe strict rules.
            
            st.dataframe(df.head())

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Valider et Importer", type="primary"):
                    count, skipped = save_transactions(df)
                    if count > 0:
                        st.success(f"{count} transactions importées !")
                        st.balloons()
                    if skipped > 0:
                        st.warning(f"{skipped} doublons ignorés.")
                    if count == 0 and skipped > 0:
                         st.info("Aucune nouvelle transaction.")
            
    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")

st.divider()
st.markdown("Format supporté : *BoursoBank CSV* (séparateur point-virgule).")
