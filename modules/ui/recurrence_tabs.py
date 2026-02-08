"""
Module containing tab implementations for the Recurrence page.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Any
from datetime import datetime
from modules.ui.recurrence_manager import (
    render_recurrence_card,
    render_manual_add_section,
    render_feedback_summary,
    delete_feedback,
    get_recurrence_feedback,
    set_recurrence_feedback,
)
from modules.db.recurrence_feedback import get_all_feedback
from modules.transaction_types import (
    get_color_for_transaction,
    is_income_category,
    is_expense_category,
)


def render_timeline_chart(recurring_df: pd.DataFrame):
    """Render a monthly timeline of recurring payments."""
    if recurring_df.empty:
        return

    # Prepare data for timeline (Day 1-31)
    timeline_data = []

    current_day = datetime.now().day

    for _, row in recurring_df.iterrows():
        day = row.get("frequency_days", 1) % 30
        if day == 0:
            day = 1  # Fallback

        timeline_data.append(
            {
                "Day": day,
                "Label": row["label"],
                "Amount": row["avg_amount"],
                "Type": "Revenu" if is_income_category(row.get("category")) else "Dépense",
            }
        )

    df_timeline = pd.DataFrame(timeline_data).sort_values("Day")

    fig = go.Figure()

    # Expenses (Red)
    expenses = df_timeline[df_timeline["Type"] == "Dépense"]
    fig.add_trace(
        go.Scatter(
            x=expenses["Day"],
            y=expenses["Amount"].abs(),
            mode="markers",
            name="Dépenses",
            text=expenses["Label"],
            marker=dict(size=12, color="#ef4444", symbol="circle"),
            hovertemplate="<b>%{text}</b><br>Jour %{x}<br>%{y:.2f} €<extra></extra>",
        )
    )

    # Income (Green)
    incomes = df_timeline[df_timeline["Type"] == "Revenu"]
    fig.add_trace(
        go.Scatter(
            x=incomes["Day"],
            y=incomes["Amount"],
            mode="markers",
            name="Revenus",
            text=incomes["Label"],
            marker=dict(size=15, color="#22c55e", symbol="diamond"),
            hovertemplate="<b>%{text}</b><br>Jour %{x}<br>%{y:.2f} €<extra></extra>",
        )
    )

    # Current day line
    fig.add_vline(
        x=current_day,
        line_width=2,
        line_dash="dash",
        line_color="gray",
        annotation_text="Aujourd'hui",
    )

    fig.update_layout(
        title="📅 Calendrier des prélèvements (Jour du mois)",
        xaxis=dict(range=[0, 32], title="Jour du mois", tickmode="linear", tick0=1, dtick=2),
        yaxis=dict(title="Montant (€)"),
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="closest",
    )

    st.plotly_chart(fig, use_container_width=True)


def render_dashboard_tab(recurring_df: pd.DataFrame, validated_df: pd.DataFrame):
    """Tab 1: Dashboard Overview."""
    st.markdown("### 📊 Vue d'ensemble")

    # 1. KPIs
    confirmed_df = recurring_df[recurring_df["user_feedback"] == "confirmed"]

    if confirmed_df.empty:
        st.info(
            "Aucun abonnement confirmé. Allez dans l'onglet 'Validation' pour confirmer vos récurrences."
        )
        return

    # Déterminer les revenus et dépenses en utilisant les catégories
    monthly_expenses = sum(
        row["avg_amount"]
        for _, row in confirmed_df.iterrows()
        if is_expense_category(row.get("category"))
    )
    monthly_income = sum(
        row["avg_amount"]
        for _, row in confirmed_df.iterrows()
        if is_income_category(row.get("category"))
    )
    balance = monthly_income + monthly_expenses  # Expenses are negative

    col1, col2, col3 = st.columns(3)
    col1.metric("💳 Charges Fixes (Mensuel)", f"{abs(monthly_expenses):,.2f} €")
    col2.metric("💰 Revenus Fixes (Mensuel)", f"{monthly_income:,.2f} €")
    col3.metric("⚖️ Reste à vivre (après fixes)", f"{balance:,.2f} €", delta_color="normal")

    st.divider()

    # 2. Timeline
    render_timeline_chart(confirmed_df)

    # 3. Next payments (Mockup logic based on day of month)
    st.subheader("🗓️ Prochaines échéances estimées")

    today = datetime.now().day
    # Filter for future days in month, or wrap around
    # Simple logic: sort by day, find next after today
    confirmed_df["day"] = confirmed_df["frequency_days"].apply(lambda x: int(x % 30) if x else 1)

    # Sort by day
    sorted_recs = confirmed_df.sort_values("day")

    # Find next 4
    future = sorted_recs[sorted_recs["day"] >= today].head(4)
    if len(future) < 4:
        # Wrap around to next month
        wrap = sorted_recs[sorted_recs["day"] < today].head(4 - len(future))
        next_payments = pd.concat([future, wrap])
    else:
        next_payments = future

    cols = st.columns(4)
    for i, (_, row) in enumerate(next_payments.iterrows()):
        with cols[i]:
            with st.container(border=True):
                st.markdown(f"**{row['label']}**")
                date_str = f"Le {row['day']} du mois"
                st.caption(f"🗓️ {date_str}")
                amount = row["avg_amount"]
                category = row.get("category", "")
                color = get_color_for_transaction(category)
                st.markdown(f":{color}[{abs(amount):,.0f} €]")


def render_validation_tab(recurring_df: pd.DataFrame, cat_emoji_map: Dict):
    """Tab 2: Validation Inbox (Pending items only)."""
    st.markdown("### ✅ Validation (Inbox)")
    st.caption("Validez les nouvelles récurrences détectées pour les ajouter à votre budget.")

    # Filter for pending only
    # Note: recurring_df should already have user_feedback column merged or we check manually

    pending_df = recurring_df[recurring_df["user_feedback"].isna()]

    if pending_df.empty:
        st.canvas(
            """
            <div style="text-align: center; padding: 50px;">
                <h1>🎉</h1>
                <h3>Tout est à jour !</h3>
                <p>Aucune nouvelle récurrence détectée à valider.</p>
            </div>
            """
        )
        st.balloons()
        return

    st.success(f"**{len(pending_df)}** nouvelles détections à vérifier.")

    for _, row in pending_df.iterrows():
        categories = cat_emoji_map  # Pass map
        render_recurrence_card(
            row,
            on_confirm=lambda l, c: _handle_feedback(l, c, True, "Confirmé depuis Inbox"),
            on_reject=lambda l, c: _handle_feedback(l, c, False, "Rejeté depuis Inbox"),
            cat_emoji_map=cat_emoji_map,
        )


def _handle_feedback(label, category, is_recurring, notes):
    set_recurrence_feedback(label, is_recurring, category, notes)
    st.rerun()


def render_subscriptions_tab(recurring_df: pd.DataFrame, cat_emoji_map: Dict):
    """Tab 3: Active Subscriptions (Confirmed items)."""
    st.markdown("### 💳 Abonnements & Revenus Actifs")

    confirmed_df = recurring_df[recurring_df["user_feedback"] == "confirmed"]

    if confirmed_df.empty:
        st.info("Aucun abonnement actif.")
    else:
        # Group by type using categories
        incomes = confirmed_df[confirmed_df["category"].apply(is_income_category)]
        expenses = confirmed_df[confirmed_df["category"].apply(is_expense_category)]

        if not incomes.empty:
            st.subheader(f"💰 Revenus ({len(incomes)})")
            for _, row in incomes.iterrows():
                render_recurrence_card(row, None, None, cat_emoji_map)  # Read-only-ish view

        if not expenses.empty:
            st.subheader(f"💳 Dépenses ({len(expenses)})")
            for _, row in expenses.iterrows():
                render_recurrence_card(row, None, None, cat_emoji_map)

    # Manual Add Section at bottom
    st.divider()
    render_manual_add_section(on_add=lambda l, c: st.rerun())


def render_trash_tab():
    """Tab 4: Rejected Items history."""
    st.markdown("### 🗑️ Corbeille (Faux positifs)")
    st.caption("Historique des détections que vous avez rejetées.")

    rejected = get_all_feedback(status="rejected")

    if not rejected:
        st.info("Corbeille vide.")
        return

    for item in rejected:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"**{item['label_pattern']}**")
        with col2:
            st.caption(item.get("notes", ""))
        with col3:
            if st.button("Restaurer", key=f"restore_{item['id']}"):
                delete_feedback(item["label_pattern"], item["category"])
                st.toast("Restauré !")
                st.rerun()
