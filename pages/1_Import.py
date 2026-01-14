import streamlit as st
from modules.ingestion import load_transaction_file
from modules.data_manager import save_transactions, init_db, get_all_transactions, get_recent_imports
from modules.categorization import categorize_transaction
from modules.ui import load_css
from modules.utils import validate_csv_file
import pandas as pd

st.set_page_config(page_title="Import", page_icon="📥")
load_css()
init_db()

st.title("📥 Import des relevés")

# --- RECENT IMPORTS SUMMARY ---
if 'hide_import_summary' not in st.session_state:
    st.session_state.hide_import_summary = False

recent_imports = get_recent_imports(limit=1)
if not recent_imports.empty and not st.session_state.hide_import_summary:
    last_imp = recent_imports.iloc[0]
    date_str = pd.to_datetime(last_imp['import_date']).strftime('%d/%m à %H:%M')
    with st.container(border=True):
        c1, c2 = st.columns([0.92, 0.08])
        c1.markdown(f"ℹ️ **Dernier import :** {last_imp['count']} transactions sur **{last_imp['account_label']}** (le {date_str})")
        if c2.button("✖️", key="hide_imp_btn", help="Masquer"):
            st.session_state.hide_import_summary = True
            st.rerun()

# --- STEP 1: FILE UPLOAD ---
st.header("1️⃣ Sélection du fichier")

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

uploaded_file = st.file_uploader("Choisir un fichier CSV", type=['csv'])

if uploaded_file is not None:
    # Validate file
    is_valid, error_msg = validate_csv_file(uploaded_file)
    if not is_valid:
        st.error(f"⚠️ Fichier invalide : {error_msg}")
        st.stop()
    
    # Handle Column Mapping for Custom Mode
    if import_mode == "Autre (Toutes banques)":
        st.info("Veuillez mapper les colonnes de votre fichier.")
        try:
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
            ready_to_import = True
        except Exception as e:
            st.error(f"Impossible de lire l'en-tête du fichier : {e}")
            ready_to_import = False
    else:
        ready_to_import = True

    if ready_to_import:
        # --- STEP 2: QUESTIONNAIRE ---
        st.divider()
        st.header("2️⃣ Paramètres d'import")
        
        col_q1, col_q2 = st.columns(2)
        
        with col_q1:
            st.subheader("📁 Compte associé")
            # Get existing accounts
            existing_accounts = get_all_transactions()['account_label'].dropna().unique().tolist()
            if not existing_accounts:
                existing_accounts = ["Compte Principal"]
            
            account_choice = st.radio("Compte", ["Compte existant", "Créer un nouveau compte"])
            
            if account_choice == "Compte existant":
                account_name = st.selectbox("Sélectionner le compte", existing_accounts)
            else:
                account_name = st.text_input("Nom du nouveau compte", placeholder="Ex: Compte Joint, Livret A...")
                if not account_name:
                    account_name = "Nouveau Compte"
        
        with col_q2:
            st.subheader("📅 Période")
            # Dynamic years: from 2024 to current year + 1 (future-proof)
            import datetime
            current_year = datetime.date.today().year
            years = list(range(2024, current_year + 2))  # 2024 to next year
            selected_year = st.selectbox("Année", years, index=len(years)-2)  # Default to current year
            
            months = ["Tous", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                     "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
            selected_month = st.selectbox("Mois (optionnel)", months)
        
        # Parse file
        st.divider()
        st.header("3️⃣ Prévisualisation & Doublons")
        
        try:
            mode_arg = "bourso_preset" if "Bourso" in import_mode else "custom"
            df = load_transaction_file(uploaded_file, mode=mode_arg, config=config)
            
            if isinstance(df, tuple):
                st.error(f"Erreur lors de la lecture : {df[1]}")
                st.stop()
            elif df is not None:
                # Apply period filter
                df['date'] = pd.to_datetime(df['date'])
                df = df[df['date'].dt.year == selected_year]
                
                if selected_month != "Tous":
                    month_num = months.index(selected_month)  # 1-indexed since "Tous" is 0
                    df = df[df['date'].dt.month == month_num]
                
                df['date'] = df['date'].dt.date  # Convert back to date
                
                if df.empty:
                    st.warning(f"Aucune transaction trouvée pour {selected_month} {selected_year}.")
                    st.stop()
                
                period_label = selected_month if selected_month != 'Tous' else "toute l'année"
                st.info(f"📊 {len(df)} transactions trouvées pour {period_label} {selected_year}.")
                
                # --- DUPLICATE DETECTION ---
                existing_df = get_all_transactions()
                
                if not existing_df.empty:
                    # Create comparison keys
                    df['_dup_key'] = df.apply(lambda r: f"{r['date']}_{r['label']}_{r['amount']}", axis=1)
                    existing_df['_dup_key'] = existing_df.apply(lambda r: f"{r['date']}_{r['label']}_{r['amount']}", axis=1)
                    
                    duplicates_mask = df['_dup_key'].isin(existing_df['_dup_key'])
                    num_duplicates = duplicates_mask.sum()
                    num_new = len(df) - num_duplicates
                    
                    df = df.drop(columns=['_dup_key'])
                    
                    if num_duplicates > 0:
                        st.warning(f"⚠️ **{num_duplicates} doublons détectés** (déjà importés). Ils seront ignorés.")
                        with st.expander(f"Voir les {num_duplicates} doublons"):
                            df_dup_preview = df[duplicates_mask][['date', 'label', 'amount']].copy()
                            df_dup_preview.columns = ['Date', 'Libellé', 'Montant'] # Clean display
                            st.dataframe(df_dup_preview.head(20))
                    
                    if num_new == 0:
                        st.error("❌ Toutes les transactions sont déjà importées !")
                        st.stop()
                    
                    st.success(f"✅ **{num_new} nouvelles transactions** prêtes à l'import.")
                else:
                    num_new = len(df)
                    st.success(f"✅ {num_new} nouvelles transactions prêtes à l'import.")
                
                # Preview new transactions
                st.subheader("Aperçu des nouvelles transactions")
                df_new_preview = df[~duplicates_mask].head(10).copy() if not existing_df.empty else df.head(10).copy()
                # Rename for display
                df_new_display = df_new_preview[['date', 'label', 'amount']].copy()
                df_new_display.columns = ['Date', 'Libellé', 'Montant']
                st.dataframe(df_new_display)
                
                # --- STEP 4: CATEGORIZATION & IMPORT ---
                st.divider()
                st.header("4️⃣ Import")
                
                auto_cat = st.checkbox("Lancer la catégorisation automatique (Règles + IA)", value=True)
                
                if st.button("🚀 Valider et Importer", type="primary"):
                    status_container = st.empty()
                    progress_bar = st.progress(0)
                    
                    with st.status("Traitement des transactions...", expanded=True) as status:
                        # Categorize if requested
                        if auto_cat:
                            st.write("Analyse et catégorisation des transactions...")
                            all_results = []
                            total = len(df)
                            rules_count = 0
                            ai_count = 0
                            
                            for i, (idx, row) in enumerate(df.iterrows()):
                                # Update feedback every few records to avoid flickering
                                progress_bar.progress((i + 1) / total)
                                if (i + 1) % 5 == 0 or (i + 1) == total:
                                    status.update(label=f"Traitement : {i+1}/{total} transactions...")
                                
                                # Call categorization
                                cat, source, conf = categorize_transaction(row['label'], row['amount'], row['date'])
                                all_results.append((cat, source, conf))
                                
                                if source == 'rule':
                                    rules_count += 1
                                else:
                                    ai_count += 1
                            
                            df['category_validated'] = [r[0] if r[0] else 'Inconnu' for r in all_results]
                            df['ai_confidence'] = [r[2] for r in all_results]
                            df['status'] = ['validated' if r[1] == 'rule' else 'pending' for r in all_results]
                            
                            st.write(f"✅ Analyse terminée : {rules_count} par règles, {ai_count} par IA.")
                        
                        # Assign account
                        df['account_label'] = account_name
                        
                        # Save
                        st.write("Sauvegarde dans la base de données...")
                        count, skipped = save_transactions(df)
                        status.update(label="Importation terminée !", state="complete", expanded=False)
                    
                    # Clean up feedback widgets
                    progress_bar.empty()
                        
                    if count > 0:
                        st.success(f"🎉 Nous venons d'importer {count} lignes sur le compte **{account_name}**.")
                        st.session_state.hide_import_summary = False
                        st.balloons()
                    if skipped > 0:
                        st.info(f"{skipped} doublons ignorés.")
                    if count == 0:
                        st.info("Aucune nouvelle transaction à importer.")
                        
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")

st.divider()
st.caption("💡 Les transactions seront analysées par notre IA pour proposer des catégories.")
