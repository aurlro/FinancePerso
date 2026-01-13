import streamlit as st
from modules.ingestion import load_transaction_file
from modules.data_manager import save_transactions, init_db
from modules.categorization import categorize_transaction
from modules.ui import load_css
import pandas as pd

st.set_page_config(page_title="Import", page_icon="📥")
load_css()

# Ensure DB is ready
init_db()

st.title("📥 Import des relevés")

# 1. Configuration Zone
st.sidebar.header("Configuration")
import_mode = st.sidebar.radio("Format de la banque", ["BoursoBank (Auto)", "Autre (Toutes banques)"])

config = None

if import_mode == "Autre (Toutes banques)":
    st.sidebar.subheader("Options CSV")
    sep = st.sidebar.selectbox("Séparateur", [";", ",", "\t"], index=0)
    decimal = st.sidebar.selectbox("Décimale", [",", "."], index=0)
    skiprows = st.sidebar.number_input("Lignes à ignorer (en-tête)", min_value=0, value=0)
    
    config = {
        'sep': sep,
        'decimal': decimal,
        'skiprows': skiprows,
        'mapping': {}
    }

st.markdown("Chargez vos fichiers CSV pour alimenter votre assistant.")

uploaded_file = st.file_uploader("Choisir un fichier CSV", type=['csv'])

if uploaded_file is not None:
    # Handle Column Mapping for Custom Mode
    if import_mode == "Autre (Toutes banques)":
        st.info("Veuillez mapper les colonnes de votre fichier.")
        try:
            # Read just the header to get columns
            uploaded_file.seek(0)
            preview_df = pd.read_csv(uploaded_file, sep=sep, skiprows=skiprows, nrows=2)
            cols = preview_df.columns.tolist()
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                col_date = st.selectbox("Colonne Date", cols)
            with c2:
                col_amt = st.selectbox("Colonne Montant", cols)
            with c3:
                col_label = st.selectbox("Colonne Libellé", cols)
            with c4:
                col_member = st.selectbox("Colonne Carte (optionnel)", ["-- Ignorer --"] + cols)
                
            config['mapping'] = {
                'date': col_date,
                'amount': col_amt,
                'label': col_label,
                'member': col_member if col_member != "-- Ignorer --" else None
            }
            
            # Allow user to proceed
            ready_to_import = True
        except Exception as e:
            st.error(f"Impossible de lire l'en-tête du fichier : {e}")
            ready_to_import = False
    else:
        ready_to_import = True

    if ready_to_import:
        # Account Selection
        account_name = st.text_input("Nom du compte (ex: Compte Courant, Joint, Livret A)", value="Compte Principal")
        
        # Preview
        st.subheader("Prévisualisation")
        
        # Run ingestion
        try:
            mode_arg = "bourso_preset" if "Bourso" in import_mode else "custom"
            df = load_transaction_file(uploaded_file, mode=mode_arg, config=config)
            
            if isinstance(df, tuple): # Error case
                 st.error(f"Erreur lors de la lecture : {df[1]}")
            elif df is not None:
                st.dataframe(df.head())
                st.info(f"{len(df)} transactions détectées.")
                
                # Auto-categorization
                if st.checkbox("Lancer la catégorisation automatique (Règles + IA)", value=True):
                    with st.spinner("Analyse en cours..."):
                        results = df.apply(lambda row: categorize_transaction(row['label'], row['amount'], row['date']), axis=1)
                        
                        df['category_validated'] = results.apply(lambda x: x[0] if x[0] else 'Inconnu')
                        df['ai_confidence'] = results.apply(lambda x: x[2])
                        df['status'] = results.apply(lambda x: 'validated' if x[1] == 'rule' else 'pending') 
                
                # Assign selected account
                df['account_label'] = account_name
                
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
