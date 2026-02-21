"""Data operations UI component.

Provides UI for data export, deletion by period, and transaction search/delete.
"""

from io import BytesIO
from typing import Optional

import streamlit as st

from modules.db.stats import get_available_months
from modules.db.transactions import (
    delete_transaction_by_id,
    delete_transactions_by_period,
    get_all_transactions,
    get_transactions_by_criteria,
)
from modules.transaction_types import get_color_for_transaction
from modules.ui_v2.atoms.icons import IconSet
from modules.ui_v2.molecules.banners import show_error, show_info, show_success, show_warning
from modules.ui_v2.molecules.toasts import toast_error, toast_info, toast_success, toast_warning


def render_export_section() -> None:
    """
    Render only the export section.
    Can be used standalone or within render_data_operations.
    """
    df_all = get_all_transactions()
    if df_all.empty:
        st.info(f"{IconSet.INFO.value} Aucune transaction à exporter.")
        return

    total_tx = len(df_all)
    st.caption(f"{IconSet.CHART.value} {total_tx} transaction(s) disponible(s)")

    col_ex1, col_ex2, col_ex3 = st.columns([2, 1, 1])

    with col_ex1:
        # Period filter for export
        available_months = get_available_months()
        export_period = st.selectbox(
            "Période à exporter",
            options=["Toutes"] + available_months,
            index=0,
            key="export_period",
            help="Sélectionnez une période spécifique ou toutes les transactions",
        )

    # Filter data if needed
    if export_period != "Toutes":
        df_export = df_all[df_all["date"].str.startswith(export_period)].copy()
    else:
        df_export = df_all.copy()

    with col_ex2:
        st.markdown(
            f"<p style='margin-top:28px; font-size:0.9em; color:#666;'>📋 {len(df_export)} transaction(s)</p>",
            unsafe_allow_html=True,
        )

    with col_ex3:
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        # CSV Export
        csv = df_export.to_csv(index=False, sep=";", encoding="utf-8-sig")
        st.download_button(
            label=f"{IconSet.FILE.value} CSV",
            data=csv,
            file_name=f"financeperso_export_{export_period.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Exporter au format CSV (compatible Excel)",
        )

    # Excel Export (if openpyxl is available)
    try:
        import openpyxl  # noqa: F401

        excel_buffer = BytesIO()
        df_export.to_excel(excel_buffer, index=False, sheet_name="Transactions")
        excel_buffer.seek(0)

        col_ex4, col_ex5 = st.columns([3, 1])
        with col_ex5:
            st.download_button(
                label=f"{IconSet.CHART.value} Excel",
                data=excel_buffer,
                file_name=f"financeperso_export_{export_period.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Exporter au format Excel",
            )
    except ImportError:
        st.caption(f"{IconSet.LIGHTBULB.value} Installez `openpyxl` pour l'export Excel : `pip install openpyxl`")


def render_data_operations() -> None:
    """
    Render the Données & Danger tab content.
    Dangerous operations: delete by period, search and delete specific transactions.
    """
    st.header(f"{IconSet.SAVE.value} Gestion des Données")

    # --- EXPORT SECTION ---
    st.subheader(f"{IconSet.EXPORT.value} Exporter les données")
    st.markdown(
        "Téléchargez vos transactions pour une sauvegarde externe ou une analyse dans un tableur."
    )

    render_export_section()

    st.divider()

    # Warning zone
    st.error(f"{IconSet.WARNING.value} **Zone de Danger**")
    st.warning(
        "Les opérations ci-dessous sont **irréversibles**. Assurez-vous d'avoir une sauvegarde avant de supprimer des données."
    )

    # --- DELETE BY PERIOD ---
    st.subheader(f"{IconSet.DELETE.value} Supprimer par Période")
    st.markdown(
        "Supprimez toutes les transactions d'un mois donné (utile pour nettoyer un import incorrect)."
    )

    available_months = get_available_months()
    if not available_months:
        st.info(f"{IconSet.INFO.value} Aucune transaction dans la base.")
    else:
        col_d1, col_d2 = st.columns([2, 1])
        with col_d1:
            selected_month = st.selectbox(
                "Mois à supprimer",
                available_months,
                format_func=lambda x: f"{x} ({len(get_transactions_by_criteria(period=x))} tx)",
                key="month_to_delete",
                help="Sélectionnez le mois à supprimer",
            )

        with col_d2:
            st.markdown("<div style='height: 1.6rem;'></div>", unsafe_allow_html=True)
            if st.button(
                f"{IconSet.DELETE.value} Supprimer", type="primary", use_container_width=True, key="btn_delete_month"
            ):
                if selected_month:
                    # Confirmation via checkbox
                    if "confirm_delete_month" not in st.session_state:
                        st.session_state["confirm_delete_month"] = False

                    if not st.session_state["confirm_delete_month"]:
                        st.session_state["confirm_delete_month"] = True
                        show_warning(
                            f"{IconSet.WARNING.value} Confirmer la suppression de **{selected_month}** ? Cliquez à nouveau pour confirmer.",
                            icon=IconSet.WARNING.value,
                        )
                        toast_warning(
                            f"{IconSet.WARNING.value} Cliquez encore sur Supprimer pour confirmer la suppression de {selected_month}",
                            icon=IconSet.WARNING.value,
                        )
                        st.rerun()
                    else:
                        with st.spinner(f"{IconSet.REFRESH.value} Suppression des transactions de {selected_month}..."):
                            count = delete_transactions_by_period(selected_month)

                        if count > 0:
                            toast_success(
                                f"{IconSet.DELETE.value} {count} transaction(s) supprimée(s) pour {selected_month}",
                                icon=IconSet.DELETE.value,
                            )
                            show_success(
                                f"{IconSet.SUCCESS.value} {count} transaction(s) de {selected_month} ont été supprimées"
                            )
                        else:
                            show_info(f"{IconSet.INFO.value} Aucune transaction à supprimer pour cette période")
                            toast_info(
                                f"{IconSet.INFO.value} Aucune transaction trouvée pour {selected_month}", icon=IconSet.INFO.value
                            )

                        st.session_state["confirm_delete_month"] = False
                        st.rerun()

    # Reset confirmation if month changed
    if "confirm_delete_month" in st.session_state and st.session_state.get(
        "month_to_delete"
    ) != st.session_state.get("last_selected_month"):
        st.session_state["confirm_delete_month"] = False
        st.session_state["last_selected_month"] = st.session_state.get("month_to_delete")

    # --- TRANSACTION SEARCH & DELETE ---
    st.divider()
    st.subheader(f"{IconSet.SEARCH.value} Rechercher et Supprimer")
    st.markdown("Trouvez et supprimez des transactions spécifiques.")

    search_label = st.text_input(
        "Rechercher par libellé",
        placeholder="Ex: AMAZON, SNCF, LIDL...",
        help="Entrez un mot-clé pour chercher dans les libellés",
    )

    if search_label:
        if len(search_label.strip()) < 2:
            toast_warning(f"{IconSet.WARNING.value} Entrez au moins 2 caractères pour la recherche", icon=IconSet.SEARCH.value)

        results = get_transactions_by_criteria(label_contains=search_label.strip())
        if results.empty:
            show_info(f"{IconSet.SEARCH.value} Aucune transaction trouvée pour '{search_label}'", icon=IconSet.SEARCH.value)
            toast_info(f"{IconSet.INFO.value} Aucun résultat pour '{search_label}'", icon=IconSet.SEARCH.value)
        else:
            show_success(f"{IconSet.SEARCH.value} **{len(results)}** transaction(s) trouvée(s)", icon=IconSet.SEARCH.value)
            toast_success(f"{IconSet.SUCCESS.value} {len(results)} transaction(s) trouvée(s)", icon=IconSet.SEARCH.value)

            for _, row in results.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    get_color_for_transaction(
                        row.get("category_validated", "Inconnu")
                    )
                    c1.markdown(
                        f"{IconSet.CALENDAR.value} **{row['date']}**  \n"
                        f"{IconSet.FILE.value} {row['label']}  \n"
                        f"{IconSet.MONEY.value} **{row['amount']:.2f}€** • {IconSet.TAG.value} {row['category']}"
                    )
                    if c2.button(
                        IconSet.DELETE.value, key=f"del_tx_{row['id']}", help="Supprimer cette transaction"
                    ):
                        try:
                            delete_transaction_by_id(row["id"])
                            toast_success(
                                f"{IconSet.DELETE.value} Transaction supprimée : {row['label'][:30]} ({row['amount']:.2f}€)",
                                icon=IconSet.DELETE.value,
                            )
                            st.rerun()
                        except Exception as e:
                            error_msg = str(e)
                            if "not found" in error_msg.lower():
                                toast_warning(f"{IconSet.WARNING.value} Cette transaction n'existe plus", icon=IconSet.WARNING.value)
                            else:
                                toast_error(f"{IconSet.ERROR.value} Erreur suppression : {error_msg[:50]}", icon=IconSet.ERROR.value)

    # --- VERSIONING ---
    st.divider()
    st.subheader(f"{IconSet.ROCKET.value} Mise à jour de Version")
    st.markdown(
        "Analyse les derniers commits Git pour mettre à jour la version et générer le Changelog."
    )

    if st.button(
        f"{IconSet.REFRESH.value} Lancer la mise à jour (Git commits)",
        use_container_width=True,
        key="config_run_versioning",
    ):
        import subprocess

        with st.spinner(f"{IconSet.REFRESH.value} Analyse des commits Git en cours..."):
            try:
                # Run the versioning script
                result = subprocess.run(
                    ["python3", "scripts/versioning.py"], capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    toast_success(f"{IconSet.SUCCESS.value} Version mise à jour avec succès", icon=IconSet.ROCKET.value)
                    show_success(f"{IconSet.ROCKET.value} **Mise à jour réussie**")
                    with st.expander(f"{IconSet.INFO.value} Détails des changements", expanded=False):
                        st.code(result.stdout)
                else:
                    error_output = result.stderr if result.stderr else "Erreur inconnue"
                    toast_error(f"{IconSet.ERROR.value} Échec de la mise à jour", icon=IconSet.ERROR.value)
                    show_error(f"**Erreur :**\n\n{error_output}")
            except subprocess.TimeoutExpired:
                toast_error(f"{IconSet.ERROR.value} Timeout : le script a pris trop de temps", icon=IconSet.CLOCK.value)
                show_error("Le script de versioning a dépassé le temps imparti")
            except FileNotFoundError:
                toast_error(f"{IconSet.ERROR.value} Script introuvable : scripts/versioning.py", icon=IconSet.ERROR.value)
                show_error("Le script de versioning n'a pas été trouvé")
            except Exception as e:
                toast_error(f"{IconSet.ERROR.value} Impossible de lancer le script : {str(e)[:50]}", icon=IconSet.ERROR.value)
                show_error(f"Impossible de lancer le script de versioning : {str(e)}")
