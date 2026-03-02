"""Dashboard principal pour la Couple Edition."""

from __future__ import annotations

from datetime import datetime

import streamlit as st
from dateutil.relativedelta import relativedelta

from modules.couple.couple_settings import (
    get_couple_settings,
    get_setup_progress,
    is_couple_configured,
)
from modules.couple.privacy_filters import (
    can_see_partner_details,
    get_couple_dashboard_data,
)
from modules.couple.transfer_detector import (
    get_pending_transfers,
    validate_transfer,
)
from modules.ui.couple.loans_view import render_loans_tab
from modules.ui.couple.widgets import (
    render_joint_transactions_section,
    render_personal_card,
    render_transfer_section,
)
from modules.utils import format_currency


def render_couple_dashboard():
    """Rend le dashboard couple complet."""

    # Vérifier si configuré
    if not is_couple_configured():
        render_setup_prompt()
        return

    settings = get_couple_settings()

    # Header avec sélecteur de période
    st.header(f"📊 Vue Couple - {settings.get('current_user_name', 'Utilisateur')}", divider=True)

    # Sélecteur de mois
    cols = st.columns([2, 2, 2])

    with cols[0]:
        months = [(datetime.now() - relativedelta(months=i)).strftime("%Y-%m") for i in range(12)]
        current_month = st.session_state.get("couple_month", months[0])
        selected_month = st.selectbox(
            "Mois",
            options=months,
            index=months.index(current_month) if current_month in months else 0,
            format_func=lambda x: datetime.strptime(x, "%Y-%m").strftime("%B %Y"),
            key="couple_month_select",
        )
        st.session_state["couple_month"] = selected_month

    # Calculer les dates
    year, month = selected_month.split("-")
    start_date = f"{year}-{month}-01"
    end_date = (
        datetime.strptime(start_date, "%Y-%m-%d") + relativedelta(months=1, days=-1)
    ).strftime("%Y-%m-%d")

    # Onglets principaux
    tab_overview, tab_loans = st.tabs(
        [
            "📊 **Vue d'ensemble**",
            "🏦 **Emprunts**",
        ]
    )

    with tab_overview:
        render_dashboard_overview(start_date, end_date)

    with tab_loans:
        render_loans_tab()


def render_dashboard_overview(start_date: str, end_date: str):
    """Rend la vue d'ensemble du dashboard."""
    # Récupérer les données
    with st.spinner("Chargement des données..."):
        data = get_couple_dashboard_data(start_date, end_date)

    # Section résumé global
    st.subheader("💰 Résumé global", divider=True)
    render_global_summary(data["summary"])

    # Section comparaison côte à côte
    st.subheader("👥 Comparatif", divider=True)
    render_comparison_section(data)

    # Section communes
    st.subheader("👥 Dépenses communes", divider=True)
    render_joint_transactions_section(data["joint_transactions"])

    # Section virements
    st.subheader("🔄 Virements internes", divider=True)
    render_transfer_section(
        {
            "pending_count": data["pending_transfers"],
            "total_validated_amount": data["validated_transfers_amount"],
        }
    )

    # Détails des virements si demandé
    if st.session_state.get("show_transfer_details"):
        render_transfer_details(start_date, end_date)


def render_setup_prompt():
    """Affiche l'invite de configuration si pas encore fait."""
    progress = get_setup_progress()

    st.info("🔧 **Configuration requise**", icon="⚙️")
    st.write(
        "Le mode Couple nécessite une configuration initiale pour attribuer les cartes et définir la confidentialité."
    )

    st.progress(progress["percentage"] / 100, text=f"Progression: {progress['percentage']}%")

    for step_name, step_info in progress["steps"].items():
        icon = "✅" if step_info["done"] else "⏳"
        st.write(f"{icon} {step_info['label']}")

    st.divider()
    st.page_link("pages/08_Configuration.py", label="🔧 Aller à la Configuration", icon="⚙️")


def render_global_summary(summary: dict):
    """Rend le résumé global avec tous les totaux."""
    me = summary["me"]
    partner = summary["partner"]
    joint = summary["joint"]

    total_income = me["total_income"] + partner["total_income"] + joint["total_income"]
    total_expenses = me["total_expenses"] + partner["total_expenses"] + joint["total_expenses"]
    total_net = me["net"] + partner["net"] + joint["net"]

    cols = st.columns(4)

    with cols[0]:
        st.metric("💰 Revenus totaux", format_currency(total_income))

    with cols[1]:
        st.metric("💸 Dépenses totales", format_currency(total_expenses))

    with cols[2]:
        delta_color = "normal" if total_net >= 0 else "inverse"
        st.metric("📈 Épargne nette", format_currency(total_net), delta_color=delta_color)

    with cols[3]:
        # Reste à vivre = Revenus - Dépenses (hors virements)
        # Les virements sont déjà exclus des stats via exclude_transfers
        reste = total_income + total_expenses
        st.metric("🎯 Reste à vivre", format_currency(reste))


def render_comparison_section(data: dict):
    """Rend la section de comparaison côte à côte."""
    settings = get_couple_settings()
    summary = data["summary"]

    # Déterminer qui est "Moi" et qui est "Partenaire"
    current_role = "A" if settings.get("current_user_id") == settings.get("member_a_id") else "B"

    me_label = settings.get("current_user_name", "Moi")
    partner_label = settings.get(
        "member_b_name" if current_role == "A" else "member_a_name", "Partenaire"
    )

    cols = st.columns(2)

    with cols[0]:
        render_personal_card(
            title=f"{me_label} (mes données)",
            metrics=summary["me"],
            show_details=True,
            categories_df=data["my_categories"],
            emoji="👤",
        )

    with cols[1]:
        # Partenaire : détails uniquement si autorisé
        show_partner_details = can_see_partner_details()

        render_personal_card(
            title=f"{partner_label} (partenaire)",
            metrics=summary["partner"],
            show_details=show_partner_details,
            categories_df=data["partner_categories"],
            emoji="👤",
        )


def render_transfer_details(start_date: str, end_date: str):
    """Rend les détails des virements détectés."""
    st.divider()

    pending = get_pending_transfers()

    if pending:
        st.warning(f"⏳ {len(pending)} virement(s) en attente de validation")

        for transfer in pending:
            with st.container(border=True):
                cols = st.columns([3, 2, 2, 2])

                with cols[0]:
                    st.markdown(f"**{format_currency(transfer['amount'])}**")
                    st.caption(f"{transfer['from_date']} → {transfer['to_date']}")

                with cols[1]:
                    st.text(f"De: ****{transfer.get('from_card', 'N/A')}")
                    st.caption(transfer.get("from_label", "")[:30])

                with cols[2]:
                    st.text(f"Vers: ****{transfer.get('to_card', 'N/A')}")
                    st.caption(transfer.get("to_label", "")[:30])

                with cols[3]:
                    val_cols = st.columns(2)
                    with val_cols[0]:
                        if st.button(
                            "✅", key=f"validate_{transfer['from_id']}_{transfer['to_id']}"
                        ):
                            if validate_transfer(transfer["from_id"], transfer["to_id"], True):
                                st.success("Validé !")
                                st.rerun()
                    with val_cols[1]:
                        if st.button("❌", key=f"reject_{transfer['from_id']}_{transfer['to_id']}"):
                            if validate_transfer(transfer["from_id"], transfer["to_id"], False):
                                st.info("Ignoré")
                                st.rerun()
    else:
        st.success("✅ Tous les virements sont validés")


def render_couple_summary_embedded():
    """Version compacte du résumé couple pour intégration dans d'autres pages."""
    if not is_couple_configured():
        return

    from datetime import datetime

    current_month = datetime.now().strftime("%Y-%m")
    year, month = current_month.split("-")
    start_date = f"{year}-{month}-01"
    end_date = (
        datetime.strptime(start_date, "%Y-%m-%d") + relativedelta(months=1, days=-1)
    ).strftime("%Y-%m-%d")

    data = get_couple_dashboard_data(start_date, end_date)
    summary = data["summary"]

    # Mini métriques
    cols = st.columns(3)

    with cols[0]:
        me_net = summary["me"]["net"]
        st.metric("👤 Mon net", format_currency(me_net))

    with cols[1]:
        partner_net = summary["partner"]["net"]
        st.metric("👤 Partenaire", format_currency(partner_net))

    with cols[2]:
        joint_net = summary["joint"]["net"]
        st.metric("👥 Commun", format_currency(joint_net))

    if st.button(
        "📊 Voir le dashboard complet", key="goto_couple_dashboard", use_container_width=True
    ):
        st.session_state["active_tab"] = "couple"
        st.rerun()
