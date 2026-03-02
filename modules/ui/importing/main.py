import datetime

import pandas as pd
import streamlit as st

from modules.categorization import categorize_transaction_batch
from modules.db.stats import get_all_account_labels, get_recent_imports
from modules.db.transactions import get_all_hashes, get_all_transactions, save_transactions
from modules.ingestion import load_transaction_file
from modules.logger import logger
from modules.onboarding import render_onboarding_widget
from modules.ui.importing.preview import (
    render_import_preview,
    show_import_progress,
    show_import_summary,
)
from modules.utils import validate_csv_file


def render_import_tab():
    """Renders the Importation tab content."""

    # Onboarding for new users
    df_check = get_all_transactions()
    render_onboarding_widget("default", has_data=not df_check.empty)

    st.header("📥 Importation des relevés")

    # WIZARD PROGRESS INDICATOR
    steps = ["📁 Fichier", "⚙️ Paramètres", "👁️ Preview", "✅ Import"]

    # Déterminer l'étape actuelle basée sur l'état
    if "import_step" not in st.session_state:
        st.session_state.import_step = 0

    current_step = st.session_state.import_step

    # Progress bar
    st.progress((current_step + 1) / len(steps))

    # Indicateur visuel des étapes
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i < current_step:
                st.success(f"✓ {step}")  # Terminé
            elif i == current_step:
                st.info(f"→ **{step}**")  # Actif
            else:
                st.caption(f"○ {step}")  # À venir

    st.divider()

    # Quick guide
    with st.expander("📖 Guide rapide d'import", expanded=False):
        st.markdown("""
        ### Comment importer vos relevés bancaires
        
        1. **Connectez-vous** à votre banque en ligne
        2. **Téléchargez** votre relevé au format CSV
        3. **Sélectionnez** le format de votre banque ci-dessous
        4. **Glissez-deposez** le fichier ou cliquez pour sélectionner
        5. **Vérifiez** le preview avant de confirmer
        
        **Formats supportés :** Boursorama, Revolut, N26, Fortuneo, et banques standards CSV
        """)
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
                f"ℹ️ **Dernier import :** {last_imp['count']} transactions sur "
                f"**{last_imp['account_label']}** (le {date_str})"
            )
            if c2.button("✖️", key="hide_imp_btn", help="Masquer"):
                st.session_state.hide_import_summary = True
                st.rerun()

    # --- STEP 1: FILE UPLOAD ---
    st.subheader("1️⃣ Sélection du fichier")

    # Import bank templates
    from modules.ingestion.bank_templates import BANK_TEMPLATES

    st.markdown("**🏦 Sélectionnez votre banque**")

    # Afficher les banques supportées dans une grille
    bank_cols = st.columns(3)
    selected_bank_key = None

    bank_icons = {
        "boursorama": "🏦",
        "ing_direct": "🟠",
        "credit_mutuel": "🔵",
        "societe_generale": "🔴",
        "caisse_epargne": "🟢",
        "banque_populaire": "🟣",
    }

    for i, (bank_key, template) in enumerate(BANK_TEMPLATES.items()):
        with bank_cols[i % 3]:
            icon = bank_icons.get(bank_key, "🏦")
            if st.button(
                f"{icon} {template.name}",
                key=f"bank_btn_{bank_key}",
                use_container_width=True,
                type=(
                    "primary" if st.session_state.get("selected_bank") == bank_key else "secondary"
                ),
            ):
                selected_bank_key = bank_key
                st.session_state["selected_bank"] = bank_key
                st.rerun()

    # Option configuration manuelle
    with st.expander("⚙️ Configuration manuelle (autre banque)", expanded=False):
        col1, col2, col3 = st.columns(3)
        sep = col1.selectbox("Séparateur", [";", ",", "\t"], index=0)
        decimal = col2.selectbox("Décimale", [",", "."], index=0)
        skiprows = col3.number_input("Lignes à ignorer (en-tête)", min_value=0, value=0)

        if st.button("Utiliser configuration manuelle", key="manual_config_btn"):
            st.session_state["selected_bank"] = "custom"
            st.rerun()

    # Afficher la banque sélectionnée
    selected_bank_key = st.session_state.get("selected_bank")
    config = None

    if selected_bank_key and selected_bank_key != "custom":
        template = BANK_TEMPLATES[selected_bank_key]
        st.success(
            f"✅ Banque sélectionnée : **{template.name}** | "
            f"Délimiteur: '{template.delimiter}' | Encodage: {template.encoding}"
        )
        import_mode = "bank_template"
    elif selected_bank_key == "custom":
        st.info("📝 Mode configuration manuelle activé")
        config = {"sep": sep, "decimal": decimal, "skiprows": skiprows, "mapping": {}}
        import_mode = "custom"
    else:
        st.warning("👆 Veuillez sélectionner votre banque ci-dessus")
        import_mode = None

    uploaded_file = st.file_uploader(
        "Choisir un fichier CSV", type=["csv"], key="file_uploader_ops"
    )

    if uploaded_file is not None:
        # Passer à l'étape 1 (Fichier sélectionné)
        st.session_state.import_step = 1

        # Validate file
        is_valid, error_msg = validate_csv_file(uploaded_file)
        if not is_valid:
            st.error(f"⚠️ Fichier invalide : {error_msg}")
            return

        # Handle Column Mapping for Custom Mode
        if import_mode == "custom":
            st.info("Veuillez mapper les colonnes de votre fichier.")
            try:
                uploaded_file.seek(0)
                preview_df = pd.read_csv(uploaded_file, sep=sep, skiprows=skiprows, nrows=2)
                cols = preview_df.columns.tolist()

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    col_date = st.selectbox("Colonne Date", cols, key="import_custom_col_date")
                with c2:
                    col_amt = st.selectbox("Colonne Montant", cols, key="import_custom_col_amount")
                with c3:
                    col_label = st.selectbox("Colonne Libellé", cols, key="import_custom_col_label")
                with c4:
                    col_member = st.selectbox(
                        "Colonne Carte (optionnel)",
                        ["-- Ignorer --"] + cols,
                        key="import_custom_col_member",
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
            # Passer à l'étape 2 (Paramètres)
            st.session_state.import_step = 2

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

            # Passer à l'étape 3 (Preview)
            st.session_state.import_step = 3

            # Parse file
            st.divider()
            st.subheader("3️⃣ Prévisualisation & Doublons")

            try:
                mode_arg = "bourso_preset" if selected_bank_key == "boursorama" else "custom"
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

                    # Initialiser duplicates_mask par défaut
                    duplicates_mask = pd.Series(False, index=df.index)
                    num_duplicates = 0
                    num_new = len(df)

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

                    # --- STEP 3: PROFESSIONAL PREVIEW ---
                    st.session_state.import_step = 3

                    # Préparer les données pour le composant de preview
                    detected_bank = (
                        "BoursoBank"
                        if selected_bank_key == "boursorama"
                        else "Banque personnalisée"
                    )
                    duplicates_df = (
                        df[duplicates_mask].copy()
                        if existing_hashes and num_duplicates > 0
                        else None
                    )

                    # Callbacks pour les actions
                    def on_import_confirmed(df_to_import, options):
                        """Callback quand l'utilisateur confirme l'import."""
                        st.session_state["import_confirmed"] = True
                        st.session_state["df_to_import"] = df_to_import
                        st.session_state["import_options"] = options
                        st.session_state["account_name"] = account_name

                    def on_import_cancelled():
                        """Callback quand l'utilisateur annule."""
                        st.session_state["import_cancelled"] = True

                    # Afficher le preview professionnel
                    render_import_preview(
                        df=df,
                        detected_bank=detected_bank,
                        duplicates=duplicates_df,
                        on_confirm=on_import_confirmed,
                        on_cancel=on_import_cancelled,
                        key="import_preview_main",
                    )

                    # Gérer les actions du preview
                    if st.session_state.get("import_cancelled"):
                        st.session_state["import_cancelled"] = False
                        st.session_state.import_step = 0
                        st.rerun()

                    if st.session_state.get("import_confirmed"):
                        df_import = st.session_state["df_to_import"]
                        options = st.session_state["import_options"]
                        auto_cat = options.get("auto_categorize", True)
                        options.get("skip_validation", False)

                        # Réinitialiser les flags
                        st.session_state["import_confirmed"] = False

                        # Passer à l'étape 4 (Import)
                        st.session_state.import_step = 4

                        # --- STEP 4: IMPORT AVEC PROGRESSION ---
                        st.divider()
                        st.subheader("4️⃣ Import des données")

                        # Étapes d'import pour la barre de progression
                        import_steps = [
                            "Préparation des données",
                            "Catégorisation automatique",
                            "Enregistrement en base",
                            "Finalisation",
                        ]

                        errors = []
                        categorized_count = 0

                        with st.container():
                            # Étape 1: Préparation
                            show_import_progress(1, len(import_steps), import_steps[0])

                            # Étape 2: Catégorisation (si activée)
                            if auto_cat:
                                show_import_progress(2, len(import_steps), import_steps[1])

                                # Préparer les données pour le batch
                                tx_data = [
                                    (row["label"], row["amount"], row["date"])
                                    for _, row in df_import.iterrows()
                                ]

                                # Catégorisation en batch (beaucoup plus rapide)
                                progress_bar = st.progress(0)
                                update_interval = max(1, len(tx_data) // 20)  # Tous les 5%

                                try:
                                    all_results = categorize_transaction_batch(tx_data)
                                    categorized_count = len(
                                        [r for r in all_results if r[0] != "Inconnu"]
                                    )

                                    # Simuler une progression pour l'UX
                                    for i in range(0, len(tx_data), update_interval):
                                        progress_bar.progress(
                                            min((i + update_interval) / len(tx_data), 1.0)
                                        )

                                except Exception as e:
                                    logger.error(f"Batch categorization failed: {e}")
                                    # Fallback: marquer tout comme Inconnu
                                    all_results = [("Inconnu", "error", 0.0)] * len(tx_data)

                                df_import["category_validated"] = [
                                    r[0] if r[0] else "Inconnu" for r in all_results
                                ]
                                df_import["ai_confidence"] = [r[2] for r in all_results]
                                df_import["status"] = [
                                    "validated" if r[1] == "rule" else "pending"
                                    for r in all_results
                                ]
                            else:
                                # Sans catégorisation auto
                                df_import["category_validated"] = "Inconnu"
                                df_import["ai_confidence"] = 0.0
                                df_import["status"] = "pending"

                            # Étape 3: Enregistrement
                            show_import_progress(3, len(import_steps), import_steps[2])
                            df_import["account_label"] = account_name
                            count, skipped = save_transactions(df_import)

                            # Étape 4: Finalisation
                            show_import_progress(4, len(import_steps), import_steps[3])

                            # Afficher le résumé professionnel
                            show_import_summary(
                                imported=count,
                                categorized=categorized_count,
                                duplicates_skipped=skipped,
                                errors=errors,
                            )

                            # Redirection vers validation si succès
                            if count > 0:
                                st.session_state["just_imported"] = True
                                st.rerun()

            except pd.errors.ParserError as e:
                logger.error(f"CSV parse error: {e}")
                st.error(f"❌ Format CSV invalide : {e}")
            except ValueError as e:
                logger.error(f"Validation error: {e}")
                st.error(f"❌ Données invalides : {e}")
            except KeyError as e:
                logger.error(f"Missing column error: {e}")
                st.error(f"❌ Colonne manquante dans le fichier : {e}")
            except Exception as e:
                logger.exception(f"Unexpected error during import: {e}")
                st.error(
                    "❌ Une erreur inattendue s'est produite. Veuillez réessayer ou contacter le support."
                )
