import streamlit as st
from modules.ingestion import load_transaction_file
from modules.db.transactions import save_transactions, get_all_transactions, get_all_hashes
from modules.db.migrations import init_db
from modules.db.stats import get_recent_imports, get_all_account_labels
from modules.categorization import categorize_transaction
from modules.ui import load_css
from modules.ui.feedback import (
    toast_success, toast_error, toast_warning, toast_info,
    show_success, show_error, show_warning, import_feedback,
    celebrate_completion
)
from modules.utils import validate_csv_file
from modules.ai_manager import is_ai_available
import pandas as pd
import datetime

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

            # Validate column mapping
            validation_errors = []

            # Check for duplicate mappings
            mapped_cols = [col_date, col_amt, col_label]
            if col_member != "-- Ignorer --":
                mapped_cols.append(col_member)

            if len(mapped_cols) != len(set(mapped_cols)):
                validation_errors.append("❌ Plusieurs champs pointent vers la même colonne")

            # Validate sample data from each column
            try:
                if col_date in preview_df.columns:
                    # Try parsing a date from the first non-null value
                    date_sample = preview_df[col_date].dropna().iloc[0] if not preview_df[col_date].empty else None
                    if date_sample is None:
                        validation_errors.append(f"⚠️ Colonne '{col_date}' (Date) est vide")

                if col_amt in preview_df.columns:
                    # Check if amount column contains numeric-like values
                    amt_sample = preview_df[col_amt].dropna().iloc[0] if not preview_df[col_amt].empty else None
                    if amt_sample is None:
                        validation_errors.append(f"⚠️ Colonne '{col_amt}' (Montant) est vide")
                    else:
                        # Try converting to float
                        try:
                            str_amt = str(amt_sample).replace(',', '.').replace(' ', '')
                            float(str_amt)
                        except ValueError:
                            validation_errors.append(f"⚠️ Colonne '{col_amt}' ne semble pas contenir de montants (échantillon: '{amt_sample}')")

                if col_label in preview_df.columns:
                    label_sample = preview_df[col_label].dropna().iloc[0] if not preview_df[col_label].empty else None
                    if label_sample is None:
                        validation_errors.append(f"⚠️ Colonne '{col_label}' (Libellé) est vide")

            except Exception as e:
                validation_errors.append(f"Erreur lors de la validation: {e}")

            if validation_errors:
                st.warning("⚠️ Problèmes détectés avec le mapping :")
                for err in validation_errors:
                    st.markdown(f"- {err}")
                st.info("💡 Vous pouvez continuer mais vérifiez que les colonnes sont correctement mappées.")

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
            existing_accounts = get_all_account_labels()
            if not existing_accounts:
                existing_accounts = ["Compte Principal"]
            
            account_choice = st.radio("Compte", ["Compte existant", "Créer un nouveau compte"])
            
            if account_choice == "Compte existant":
                account_name = st.selectbox("Sélectionner le compte", existing_accounts)
            else:
                default_acc = st.session_state.get('default_account_name', "")
                account_name = st.text_input("Nom du nouveau compte", value=default_acc, placeholder="Ex: Compte Joint, Livret A...")
                if not account_name:
                    account_name = "Nouveau Compte"
        
        with col_q2:
            st.subheader("📅 Période")
            # Dynamic years: from 2024 to current year + 1 (future-proof)
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
                existing_hashes = get_all_hashes()
                force_import = False
                
                if existing_hashes:
                    duplicates_mask = df['tx_hash'].isin(existing_hashes)
                    num_duplicates = duplicates_mask.sum()
                    num_new = len(df) - num_duplicates
                    
                    if num_duplicates > 0:
                        st.warning(f"⚠️ **{num_duplicates} doublon(s) détecté(s)** - même date, libellé et montant.")
                        
                        with st.expander(f"Voir les {num_duplicates} doublons"):
                            df_dup_preview = df[duplicates_mask][['date', 'label', 'amount']].copy()
                            df_dup_preview.columns = ['Date', 'Libellé', 'Montant'] # Clean display
                            st.dataframe(df_dup_preview.head(20))
                            st.caption("💡 Ces transactions ont la même date, le même libellé et le même montant que des transactions déjà importées.")
                            toast_warning(f"{num_duplicates} doublon(s) détecté(s)", icon="⚠️")
                        
                        # Option to force import
                        col_dup1, col_dup2 = st.columns([2, 1])
                        with col_dup1:
                            force_import = st.checkbox(
                                "Forcer l'import (ignorer les doublons)", 
                                value=False,
                                help="Cochez cette case si vous savez que ce ne sont pas de vrais doublons (ex: deux achats identiques le même jour)"
                            )
                        with col_dup2:
                            if force_import:
                                st.info("⚠️ Les 'doublons' seront importés quand même")
                    
                    if num_new == 0 and not force_import:
                        st.error("❌ Toutes les transactions sont déjà importées !")
                        st.stop()
                    
                    if force_import:
                        st.success(f"✅ **{len(df)} transactions** prêtes à l'import (doublons ignorés).")
                    else:
                        st.success(f"✅ **{num_new} nouvelles transactions** prêtes à l'import.")
                else:
                    num_new = len(df)
                    st.success(f"✅ {num_new} nouvelles transactions prêtes à l'import.")
                
                # Apply duplicate filtering unless force_import is True
                if existing_hashes and not force_import:
                    df_import = df[~duplicates_mask].copy()
                else:
                    df_import = df.copy()
                
                # Preview new transactions
                st.subheader("Aperçu des transactions à importer")
                df_new_preview = df_import.head(10).copy()
                # Rename for display
                df_new_display = df_new_preview[['date', 'label', 'amount']].copy()
                df_new_display.columns = ['Date', 'Libellé', 'Montant']
                st.dataframe(df_new_display)
                
                # --- STEP 4: CATEGORIZATION & IMPORT ---
                st.divider()
                st.header("4️⃣ Import")
                
                # Check AI availability
                ai_available = is_ai_available()
                
                if not ai_available:
                    st.info("""
                    🌐 **Mode hors ligne activé**
                    
                    Aucune clé API IA détectée. L'import utilisera uniquement les règles de catégorisation manuelles.
                    Les transactions seront marquées comme "à valider" pour que vous puissiez les catégoriser manuellement.
                    
                    Pour activer l'IA : Configurez votre clé API dans la page **⚙️ Configuration** → **🔑 API & Services**.
                    """)
                
                auto_cat = st.checkbox(
                    "Lancer la catégorisation automatique (Règles + IA)" if ai_available else "Lancer la catégorisation par règles uniquement", 
                    value=True
                )
                
                if st.button("🚀 Valider et Importer", type="primary"):
                    status_container = st.empty()
                    progress_bar = st.progress(0)
                    
                    with st.status("Traitement des transactions...", expanded=True) as status:
                        # Categorize if requested
                        if auto_cat:
                            st.write("Analyse et catégorisation des transactions...")
                            all_results = []
                            total = len(df_import)
                            rules_count = 0
                            ai_count = 0
                            
                            for i, (idx, row) in enumerate(df_import.iterrows()):
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
                            
                            df_import['category_validated'] = [r[0] if r[0] else 'Inconnu' for r in all_results]
                            df_import['ai_confidence'] = [r[2] for r in all_results]
                            df_import['status'] = ['validated' if r[1] == 'rule' else 'pending' for r in all_results]
                            
                            if ai_available:
                                st.write(f"✅ Analyse terminée : {rules_count} par règles, {ai_count} par IA.")
                            else:
                                st.write(f"✅ Analyse terminée : {rules_count} par règles (mode hors ligne).")
                        
                        # Assign account
                        df_import['account_label'] = account_name
                        
                        # Save
                        st.write("Sauvegarde dans la base de données...")
                        count, skipped = save_transactions(df_import)
                        status.update(label="Importation terminée !", state="complete", expanded=False)
                    
                    # Clean up feedback widgets
                    progress_bar.empty()
                        
                    # Feedback visuel amélioré
                    import_feedback(count, skipped, account_name)
                    
                    if count > 0:
                        show_success(f"🎉 {count} transactions importées sur **{account_name}**")
                        st.session_state.hide_import_summary = False
                        celebrate_completion(min_items=10, actual_items=count)
                    elif skipped > 0 and count == 0:
                        show_warning(f"Toutes les transactions existent déjà ({skipped} doublons)")
                    else:
                        show_info("Aucune nouvelle transaction à importer")
                        
                    # Afficher un résumé détaillé
                    if count > 0:
                        with st.expander("📊 Résumé détaillé de l'import", expanded=False):
                            col_r1, col_r2, col_r3 = st.columns(3)
                            with col_r1:
                                st.metric("Importées", count)
                            with col_r2:
                                st.metric("Ignorées", skipped)
                            with col_r3:
                                st.metric("Total fichier", count + skipped)
                            
                            if auto_cat:
                                st.info(f"📌 {rules_count} catégorisées par règles | {ai_count} par IA")
                        
        except Exception as e:
            error_msg = str(e)
            toast_error(f"Erreur lors de l'import : {error_msg[:50]}...")
            show_error(f"Une erreur est survenue : {error_msg}")
            
            # Suggestions d'aide selon l'erreur
            if "encoding" in error_msg.lower():
                st.info("💡 **Conseil** : Essayez de convertir votre fichier en UTF-8 avant l'import.")
            elif "delimiter" in error_msg.lower() or "separateur" in error_msg.lower():
                st.info("💡 **Conseil** : Vérifiez le séparateur choisi (point-virgule vs virgule).")

st.divider()
if is_ai_available():
    st.caption("💡 Les transactions seront analysées par notre IA pour proposer des catégories.")
else:
    st.caption("💡 Mode hors ligne : seules les règles manuelles seront appliquées. Configurez une clé API pour activer l'IA.")

from modules.ui.layout import render_app_info
render_app_info()
