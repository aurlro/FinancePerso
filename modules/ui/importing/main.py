import streamlit as st
import pandas as pd
import datetime
from modules.ingestion import load_transaction_file
from modules.db.transactions import save_transactions, get_all_transactions, get_all_hashes
from modules.db.stats import get_recent_imports, get_all_account_labels
from modules.categorization import categorize_transaction
from modules.ui import load_css, render_scroll_to_top
from modules.ui.feedback import (
    toast_success,
    toast_error,
    toast_warning,
    toast_info,
    show_success,
    show_error,
    show_warning,
    show_info,
    import_feedback,
    celebrate_completion,
)
from modules.utils import validate_csv_file
from modules.validators import validate_transaction, sanitize_string_input
from modules.ai_manager import is_ai_available
from modules.onboarding import render_onboarding_widget


def render_import_tab():
    """Renders the Importation tab content."""

    # Onboarding for new users
    df_check = get_all_transactions()
    render_onboarding_widget("default", has_data=not df_check.empty)

    st.header("📥 Importation des relevés")

    # Quick guide
    with st.expander("📖 Guide rapide d'import", expanded=False):
        st.markdown(
            """
        ### Comment importer vos relevés bancaires
        
        1. **Connectez-vous** à votre banque en ligne
        2. **Téléchargez** votre relevé au format CSV
        3. **Sélectionnez** le format de votre banque ci-dessous
        4. **Glissez-deposez** le fichier ou cliquez pour sélectionner
        5. **Vérifiez** le preview avant de confirmer
        
        **Formats supportés :** Boursorama, Revolut, N26, Fortuneo, et banques standards CSV
        """
        )
        st.info("🎥 Tutoriel vidéo à venir - En attendant, suivez les étapes ci-dessus")

    # --- RECENT IMPORTS SUMMARY ---
    if "hide_import_summary" not in st.session_state:
        st.session_state.hide_import_summary = False

    recent_imports = get_recent_imports(limit=1)
    if not recent_imports.empty and not st.session_state.hide_import_summary:
        last_imp = recent_imports.iloc[0]
        date_str = pd.to_datetime(last_imp["import_date"]).strftime("%d/%m à %H:%M")
        with st.container(border=True):
            c1, c2 = st.columns([0.92, 0.08])
            c1.markdown(
                f"ℹ️ **Dernier import :** {last_imp['count']} transactions sur **{last_imp['account_label']}** (le {date_str})"
            )
            if c2.button("✖️", key="hide_imp_btn", help="Masquer"):
                st.session_state.hide_import_summary = True
                st.rerun()

    # --- STEP 1: FILE UPLOAD ---
    st.subheader("1️⃣ Sélection du fichier")

    import_mode = st.radio(
        "Format de la banque", ["BoursoBank (Auto)", "Autre (Toutes banques)"], horizontal=True
    )

    config = None
    if import_mode == "Autre (Toutes banques)":
        with st.expander("Configuration CSV avancée", expanded=True):
            col1, col2, col3 = st.columns(3)
            sep = col1.selectbox("Séparateur", [";", ",", "\t"], index=0)
            decimal = col2.selectbox("Décimale", [",", "."], index=0)
            skiprows = col3.number_input("Lignes à ignorer (en-tête)", min_value=0, value=0)

            config = {"sep": sep, "decimal": decimal, "skiprows": skiprows, "mapping": {}}

    uploaded_file = st.file_uploader(
        "Choisir un fichier CSV", type=["csv"], key="file_uploader_ops"
    )

    if uploaded_file is not None:
        # Validate file
        is_valid, error_msg = validate_csv_file(uploaded_file)
        if not is_valid:
            st.error(f"⚠️ Fichier invalide : {error_msg}")
            return

        # Handle Column Mapping for Custom Mode
        if import_mode == "Autre (Toutes banques)":
            st.info("Veuillez mapper les colonnes de votre fichier.")
            try:
                uploaded_file.seek(0)
                preview_df = pd.read_csv(uploaded_file, sep=sep, skiprows=skiprows, nrows=2)
                cols = preview_df.columns.tolist()

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    col_date = st.selectbox("Colonne Date", cols, key="selectbox_81")
                with c2:
                    col_amt = st.selectbox("Colonne Montant", cols, key="selectbox_83")
                with c3:
                    col_label = st.selectbox("Colonne Libellé", cols, key="selectbox_85")
                with c4:
                    col_member = st.selectbox(
                        "Colonne Carte (optionnel)", ["-- Ignorer --"] + cols, key="selectbox_87"
                    )

                config["mapping"] = {
                    "date": col_date,
                    "amount": col_amt,
                    "label": col_label,
                    "member": col_member if col_member != "-- Ignorer --" else None,
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
            st.subheader("2️⃣ Paramètres d'import")

            col_q1, col_q2 = st.columns(2)

            with col_q1:
                st.markdown("**📂 Compte associé**")
                # Get existing accounts
                existing_accounts = get_all_account_labels()
                if not existing_accounts:
                    existing_accounts = ["Compte Principal"]

                account_choice = st.radio(
                    "Compte",
                    ["Compte existant", "Créer un nouveau compte"],
                    key="radio_op_acc",
                    horizontal=True,
                )

                if account_choice == "Compte existant":
                    account_name = st.selectbox(
                        "Sélectionner le compte", existing_accounts, key="selectbox_op_acc"
                    )
                else:
                    account_name = st.text_input(
                        "Nom du nouveau compte",
                        placeholder="Ex: Compte Joint, Livret A...",
                        key="text_input_op_acc",
                    )
                    if not account_name:
                        account_name = "Nouveau Compte"

            with col_q2:
                st.markdown("**📅 Période**")
                current_year = datetime.date.today().year
                years = list(range(2024, current_year + 2))
                selected_year = st.selectbox(
                    "Année", years, index=len(years) - 2, key="selectbox_op_year"
                )

                months = [
                    "Tous",
                    "Janvier",
                    "Février",
                    "Mars",
                    "Avril",
                    "Mai",
                    "Juin",
                    "Juillet",
                    "Août",
                    "Septembre",
                    "Octobre",
                    "Novembre",
                    "Décembre",
                ]
                selected_month = st.selectbox("Mois (optionnel)", months, key="selectbox_op_month")

            # Parse file
            st.divider()
            st.subheader("3️⃣ Prévisualisation & Doublons")

            try:
                mode_arg = "bourso_preset" if "Bourso" in import_mode else "custom"
                df = load_transaction_file(uploaded_file, mode=mode_arg, config=config)

                if isinstance(df, tuple):
                    st.error(f"Erreur lors de la lecture : {df[1]}")
                    return
                elif df is not None:
                    # Apply period filter
                    df["date"] = pd.to_datetime(df["date"])
                    df = df[df["date"].dt.year == selected_year]

                    if selected_month != "Tous":
                        month_num = months.index(selected_month)
                        df = df[df["date"].dt.month == month_num]

                    df["date"] = df["date"].dt.date

                    if df.empty:
                        st.warning(
                            f"Aucune transaction trouvée pour {selected_month} {selected_year}."
                        )
                        return

                    period_label = selected_month if selected_month != "Tous" else "toute l'année"
                    st.info(
                        f"📊 {len(df)} transactions trouvées pour {period_label} {selected_year}."
                    )

                    # --- DUPLICATE DETECTION ---
                    existing_hashes = get_all_hashes()
                    force_import = False

                    if existing_hashes:
                        duplicates_mask = df["tx_hash"].isin(existing_hashes)
                        num_duplicates = duplicates_mask.sum()
                        num_new = len(df) - num_duplicates

                        if num_duplicates > 0:
                            st.warning(f"⚠️ **{num_duplicates} doublon(s) détecté(s)**")
                            force_import = st.checkbox(
                                "Forcer l'import (ignorer les doublons)", value=False
                            )

                        if num_new == 0 and not force_import:
                            st.error("❌ Toutes les transactions sont déjà importées !")
                            return

                    # Preview
                    st.dataframe(df.head(5)[["date", "label", "amount"]])

                    # --- STEP 4: IMPORT ---
                    st.divider()
                    st.subheader("4️⃣ Import des données")

                    ai_available = is_ai_available()
                    auto_cat = st.checkbox("Lancer la catégorisation automatique", value=True)

                    if st.button(
                        "🚀 Valider et Importer",
                        type="primary",
                        key="btn_ops_run_import",
                        use_container_width=True,
                    ):
                        df_import = (
                            df[~duplicates_mask].copy()
                            if existing_hashes and not force_import
                            else df.copy()
                        )

                        with st.status("Importation en cours...", expanded=True) as status:
                            if auto_cat:
                                all_results = []
                                total = len(df_import)
                                for i, (_, row) in enumerate(df_import.iterrows()):
                                    cat, source, conf = categorize_transaction(
                                        row["label"], row["amount"], row["date"]
                                    )
                                    all_results.append((cat, source, conf))

                                df_import["category_validated"] = [
                                    r[0] if r[0] else "Inconnu" for r in all_results
                                ]
                                df_import["ai_confidence"] = [r[2] for r in all_results]
                                df_import["status"] = [
                                    "validated" if r[1] == "rule" else "pending"
                                    for r in all_results
                                ]

                            df_import["account_label"] = account_name
                            count, skipped = save_transactions(df_import)
                            status.update(label="Importation terminée !", state="complete")

                        import_feedback(count, skipped, account_name)
                        if count > 0:
                            st.session_state["just_imported"] = True
                            st.rerun()

            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")
