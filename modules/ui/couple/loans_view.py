"""Vue des emprunts pour la Couple Edition."""

from __future__ import annotations

import streamlit as st

from modules.couple.loans import (
    create_loan,
    delete_loan,
    detect_loan_payments,
    get_all_loans,
    get_loan_transactions,
    get_loans_summary,
    link_transaction_to_loan,
    update_loan,
)
from modules.db.members import get_members
from modules.utils import format_currency


def render_loans_section():
    """Rend la section complète des emprunts."""
    st.subheader("🏦 Mes Emprunts", divider=True)

    # Vue d'ensemble
    render_loans_summary()

    st.divider()

    # Liste des emprunts
    render_loans_list()

    st.divider()

    # Bouton d'ajout
    if st.button("➕ Ajouter un emprunt", use_container_width=True):
        st.session_state["show_add_loan"] = True
        st.rerun()

    if st.session_state.get("show_add_loan"):
        render_add_loan_form()


def render_loans_summary():
    """Affiche le résumé des emprunts."""
    summary = get_loans_summary()

    if summary["total_loans"] == 0:
        st.info("📭 Aucun emprunt en cours. Ajoutez votre premier emprunt !")
        return

    # KPIs
    cols = st.columns(4)

    with cols[0]:
        st.metric("Emprunts actifs", summary["total_loans"])

    with cols[1]:
        st.metric("Capital restant", format_currency(summary["total_remaining"]))

    with cols[2]:
        st.metric("Mensualités totales", format_currency(summary["total_monthly"])) + "/mois"

    with cols[3]:
        st.metric("Progression moyenne", f"{summary['average_progress']:.1f}%")

    # Barre de progression globale
    st.progress(
        summary["average_progress"] / 100,
        text=f"Remboursement global: {summary['average_progress']:.1f}%",
    )


def render_loans_list():
    """Affiche la liste des emprunts."""
    loans = get_all_loans(active_only=True)

    if not loans:
        return

    for loan in loans:
        with st.container(border=True):
            render_loan_card(loan)


def render_loan_card(loan: dict):
    """Affiche une carte d'emprunt."""
    progress = loan.get("repayment_progress_pct", 0) or 0
    remaining = loan.get("remaining_capital", 0) or 0
    monthly = loan.get("monthly_payment", 0) or 0

    # Header avec nom et organisme
    cols = st.columns([3, 2, 2, 1])

    with cols[0]:
        st.markdown(f"**{loan['name']}**")
        if loan.get("lender"):
            st.caption(f"{loan['lender']}")

    with cols[1]:
        rate = loan.get("interest_rate")
        rate_text = f"{rate}%" if rate else "N/A"
        st.metric("Mensualité", f"{format_currency(monthly)}", rate_text)

    with cols[2]:
        st.metric("Capital restant", format_currency(remaining))

    with cols[3]:
        # Type d'attribution
        type_labels = {"PERSONAL_A": "👤 A", "PERSONAL_B": "👤 B", "JOINT": "👥 Commun"}
        account_type = loan.get("account_type", "JOINT")
        st.caption(type_labels.get(account_type, account_type))

        if st.button("✏️", key=f"edit_loan_{loan['id']}"):
            st.session_state[f'editing_loan_{loan["id"]}'] = True
            st.rerun()

    # Barre de progression
    st.progress(progress / 100, text=f"{progress:.1f}% remboursé")

    # Détails si édition
    if st.session_state.get(f'editing_loan_{loan["id"]}'):
        render_loan_editor(loan)


def render_loan_editor(loan: dict):
    """Affiche l'éditeur d'emprunt."""
    st.divider()

    with st.form(key=f"loan_form_{loan['id']}"):
        cols = st.columns(2)

        with cols[0]:
            name = st.text_input("Nom", value=loan.get("name", ""), key=f"loan_name_{loan['id']}")
            lender = st.text_input(
                "Organisme", value=loan.get("lender", "") or "", key=f"loan_lender_{loan['id']}"
            )
            principal = st.number_input(
                "Capital emprunté",
                value=float(loan.get("principal_amount", 0) or 0),
                step=1000.0,
                key=f"loan_principal_{loan['id']}",
            )

        with cols[1]:
            monthly = st.number_input(
                "Mensualité",
                value=float(loan.get("monthly_payment", 0) or 0),
                step=50.0,
                key=f"loan_monthly_{loan['id']}",
            )
            rate = st.number_input(
                "Taux (%)",
                value=float(loan.get("interest_rate", 0) or 0),
                step=0.1,
                format="%.2f",
                key=f"loan_rate_{loan['id']}",
            )
            duration = st.number_input(
                "Durée (mois)",
                value=int(loan.get("total_duration_months", 0) or 0),
                step=12,
                key=f"loan_duration_{loan['id']}",
            )

        # Attribution
        members = get_members()
        member_options = [None] + [m["id"] for m in members]
        member_labels = {None: "— Commun —"}
        for m in members:
            member_labels[m["id"]] = m.get("name", m["id"])

        current_member = loan.get("member_id")
        member_col, type_col = st.columns(2)

        with member_col:
            member_id = st.selectbox(
                "Attribué à",
                options=member_options,
                format_func=lambda x: member_labels.get(x, str(x)),
                index=(
                    member_options.index(current_member) if current_member in member_options else 0
                ),
                key=f"loan_member_{loan['id']}",
            )

        with type_col:
            account_type = st.selectbox(
                "Type",
                options=["JOINT", "PERSONAL_A", "PERSONAL_B"],
                index=["JOINT", "PERSONAL_A", "PERSONAL_B"].index(
                    loan.get("account_type", "JOINT")
                ),
                key=f"loan_type_{loan['id']}",
            )

        notes = st.text_area(
            "Notes", value=loan.get("notes", "") or "", key=f"loan_notes_{loan['id']}"
        )

        # Boutons
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True):
                if update_loan(
                    loan["id"],
                    name=name,
                    lender=lender,
                    principal_amount=principal,
                    monthly_payment=monthly,
                    interest_rate=rate,
                    total_duration_months=duration,
                    member_id=member_id,
                    account_type=account_type,
                    notes=notes,
                ):
                    st.success("✅ Emprunt mis à jour")
                    del st.session_state[f'editing_loan_{loan["id"]}']
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la mise à jour")

        with col2:
            if st.form_submit_button("🗑️ Supprimer", use_container_width=True):
                if delete_loan(loan["id"], soft=True):
                    st.success("✅ Emprunt supprimé")
                    st.rerun()
                else:
                    st.error("❌ Erreur")

        with col3:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                del st.session_state[f'editing_loan_{loan["id"]}']
                st.rerun()

    # Section paiements
    st.divider()
    render_loan_payments_section(loan)


def render_loan_payments_section(loan: dict):
    """Affiche la section des paiements d'un emprunt."""
    st.markdown("**💳 Paiements liés**")

    # Paiements existants
    payments = get_loan_transactions(loan["id"])

    if payments:
        st.caption(f"{len(payments)} paiement(s) enregistré(s)")
        for p in payments[:5]:  # Limiter à 5
            cols = st.columns([2, 2, 2, 1])
            with cols[0]:
                st.text(p.get("date", "N/A"))
            with cols[1]:
                st.text(p.get("label", "N/A")[:30])
            with cols[2]:
                st.text(format_currency(p.get("amount", 0)))
            with cols[3]:
                # TODO: bouton supprimer lien
                pass
    else:
        st.caption("Aucun paiement lié")

    # Détection automatique
    st.caption("🔍 Détection automatique")
    potential = detect_loan_payments(loan["id"])

    if potential:
        st.write(f"{len(potential)} paiement(s) potentiel(s) détecté(s):")
        for p in potential[:3]:  # Limiter à 3
            cols = st.columns([3, 2, 1])
            with cols[0]:
                st.text(f"{p.get('date', 'N/A')} - {p.get('label', 'N/A')[:25]}")
            with cols[1]:
                st.text(format_currency(p.get("amount", 0)))
            with cols[2]:
                if st.button("🔗 Lier", key=f"link_{loan['id']}_{p['id']}"):
                    if link_transaction_to_loan(loan["id"], p["id"]):
                        st.success("Lié !")
                        st.rerun()


def render_add_loan_form():
    """Affiche le formulaire d'ajout d'emprunt."""
    st.divider()
    st.markdown("**➕ Nouvel emprunt**")

    with st.form(key="add_loan_form"):
        cols = st.columns(2)

        with cols[0]:
            name = st.text_input("Nom *", placeholder="ex: Prêt Immobilier")
            lender = st.text_input("Organisme", placeholder="ex: Banque Populaire")
            principal = st.number_input("Capital emprunté *", min_value=0.0, step=1000.0)

        with cols[1]:
            monthly = st.number_input("Mensualité *", min_value=0.0, step=50.0)
            rate = st.number_input("Taux annuel (%)", min_value=0.0, step=0.1, format="%.2f")
            duration = st.number_input("Durée (mois)", min_value=0, step=12)

        # Attribution
        members = get_members()
        member_col, type_col = st.columns(2)

        with member_col:
            member_options = [None] + [m["id"] for m in members]
            member_labels = {None: "— Commun —"}
            for m in members:
                member_labels[m["id"]] = m.get("name", m["id"])

            member_id = st.selectbox(
                "Attribué à",
                options=member_options,
                format_func=lambda x: member_labels.get(x, str(x)),
            )

        with type_col:
            account_type = st.selectbox("Type", options=["JOINT", "PERSONAL_A", "PERSONAL_B"])

        notes = st.text_area("Notes")

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Créer", type="primary", use_container_width=True):
                if not name or monthly <= 0:
                    st.error("❌ Nom et mensualité sont obligatoires")
                else:
                    loan_id = create_loan(
                        name=name,
                        monthly_payment=monthly,
                        principal_amount=principal,
                        lender=lender,
                        interest_rate=rate if rate > 0 else None,
                        total_duration_months=duration if duration > 0 else None,
                        member_id=member_id,
                        account_type=account_type,
                        notes=notes,
                    )
                    if loan_id:
                        st.success(f"✅ Emprunt créé (ID: {loan_id})")
                        del st.session_state["show_add_loan"]
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la création")

        with col2:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                del st.session_state["show_add_loan"]
                st.rerun()


def render_loans_tab():
    """Onglet complet pour les emprunts (à intégrer dans le dashboard couple)."""
    st.header("🏦 Gestion des Emprunts")

    render_loans_section()
