"""
🚨 Alerts Section - Alertes intelligentes

Fonctionnalités issues de l'ancienne page Abonnements :
- Détection d'abonnements "zombies" (inactifs)
- Alertes d'augmentation de prix
- Calculatrice "Reste à vivre"
"""

from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from modules.db.transactions import get_all_transactions

# =============================================================================
# DATA MODELS
# =============================================================================


class SubscriptionAlert:
    """Represents a subscription alert."""

    def __init__(
        self, type: str, merchant: str, message: str, severity: str = "info", data: dict = None
    ):
        self.type = type  # "zombie", "increase", "new"
        self.merchant = merchant
        self.message = message
        self.severity = severity  # "info", "warning", "danger"
        self.data = data or {}
        self.created_at = datetime.now()


# =============================================================================
# ALERT DETECTORS
# =============================================================================


def detect_zombie_subscriptions(
    df: pd.DataFrame, confirmed_patterns: list[dict]
) -> list[SubscriptionAlert]:
    """
    Detect subscriptions that haven't had a payment recently.

    A subscription is considered "zombie" if:
    - It was confirmed as recurring
    - No transaction in the last 45 days (for monthly)
    - No transaction in the last 120 days (for yearly)
    """
    alerts = []

    if df.empty or not confirmed_patterns:
        return alerts

    today = datetime.now()

    for pattern in confirmed_patterns:
        label = pattern.get("label_pattern", "")
        category = pattern.get("category", "")

        # Find transactions matching this pattern
        mask = df["label"].str.contains(label, case=False, na=False)
        if category and "category" in df.columns:
            mask = mask & (df["category"] == category)

        matches = df[mask]

        if matches.empty:
            # No transactions at all - suspicious
            alerts.append(
                SubscriptionAlert(
                    type="zombie",
                    merchant=label,
                    message=f"Aucune transaction trouvée pour '{label}' - Vérifiez si l'abonnement est toujours actif",
                    severity="warning",
                    data={"last_date": None, "pattern": label},
                )
            )
            continue

        # Check last transaction date
        matches["date"] = pd.to_datetime(matches["date"])
        last_date = matches["date"].max()
        days_since = (today - last_date).days

        # Determine expected frequency from notes or default to monthly
        notes = pattern.get("notes", "").lower()
        if "annuel" in notes or "year" in notes:
            threshold = 400  # Annual
        elif "trimestriel" in notes or "quarter" in notes:
            threshold = 120  # Quarterly
        else:
            threshold = 45  # Monthly default

        if days_since > threshold:
            alerts.append(
                SubscriptionAlert(
                    type="zombie",
                    merchant=label,
                    message=f"Pas de prélèvement depuis {days_since} jours (seuil: {threshold})",
                    severity="warning" if days_since < threshold * 2 else "danger",
                    data={
                        "last_date": last_date.strftime("%Y-%m-%d"),
                        "days_since": days_since,
                        "threshold": threshold,
                        "pattern": label,
                    },
                )
            )

    return alerts


def detect_price_increases(
    df: pd.DataFrame, confirmed_patterns: list[dict]
) -> list[SubscriptionAlert]:
    """
    Detect significant price increases in subscriptions.

    Flags increases > 10% compared to historical average.
    """
    alerts = []

    if df.empty or not confirmed_patterns:
        return alerts

    for pattern in confirmed_patterns:
        label = pattern.get("label_pattern", "")
        category = pattern.get("category", "")

        mask = df["label"].str.contains(label, case=False, na=False)
        if category and "category" in df.columns:
            mask = mask & (df["category"] == category)

        matches = df[mask].copy()

        if len(matches) < 3:
            continue  # Not enough history

        matches["date"] = pd.to_datetime(matches["date"])
        matches = matches.sort_values("date")

        # Split into recent (last 2 months) and historical
        two_months_ago = datetime.now() - timedelta(days=60)
        recent = matches[matches["date"] > two_months_ago]
        historical = matches[matches["date"] <= two_months_ago]

        if len(recent) == 0 or len(historical) == 0:
            continue

        # Compare averages
        recent_avg = recent["amount"].abs().mean()
        historical_avg = historical["amount"].abs().mean()

        if historical_avg > 0:
            increase_pct = ((recent_avg - historical_avg) / historical_avg) * 100

            if increase_pct > 10:  # More than 10% increase
                alerts.append(
                    SubscriptionAlert(
                        type="increase",
                        merchant=label,
                        message=(
                            f"Augmentation de {increase_pct:.1f}% détectée "
                            f"({historical_avg:.2f}€ → {recent_avg:.2f}€)"
                        ),
                        severity="warning" if increase_pct < 25 else "danger",
                        data={
                            "old_average": historical_avg,
                            "new_average": recent_avg,
                            "increase_percent": increase_pct,
                            "pattern": label,
                        },
                    )
                )

    return alerts


# =============================================================================
# RENDERERS
# =============================================================================


def render_alerts_section():
    """Render the alerts section for the inbox."""
    from modules.db.recurrence_feedback import get_all_feedback

    df = get_all_transactions()
    confirmed = get_all_feedback(status="confirmed")

    if not confirmed:
        return

    # Detect alerts
    zombie_alerts = detect_zombie_subscriptions(df, confirmed)
    increase_alerts = detect_price_increases(df, confirmed)

    all_alerts = zombie_alerts + increase_alerts

    if not all_alerts:
        return

    st.subheader(f"🚨 {len(all_alerts)} alerte(s) à vérifier")

    for alert in all_alerts:
        _render_alert_card(alert)


def _render_alert_card(alert: SubscriptionAlert):
    """Render a single alert card."""

    colors = {
        "info": ("blue", "ℹ️"),
        "warning": ("orange", "⚠️"),
        "danger": ("red", "🚨"),
    }
    color, icon = colors.get(alert.severity, ("gray", "📌"))

    with st.container(border=True):
        cols = st.columns([0.5, 3, 1])

        with cols[0]:
            st.markdown(f"<div style='font-size: 24px;'>{icon}</div>", unsafe_allow_html=True)

        with cols[1]:
            alert_type_labels = {
                "zombie": "🧟 Abonnement zombie",
                "increase": "📈 Augmentation de prix",
                "new": "✨ Nouvelle détection",
            }
            st.markdown(f"**{alert.merchant}**")
            st.caption(f"{alert_type_labels.get(alert.type, alert.type)}: {alert.message}")

        with cols[2]:
            if st.button(
                "👀 Voir détails", key=f"alert_{alert.merchant[:20]}", use_container_width=True
            ):
                st.session_state["selected_alert"] = alert
                st.info(f"Détails: {alert.data}")


def render_remaining_budget_calculator():
    """Render the 'reste à vivre' calculator."""
    from modules.db.recurrence_feedback import get_all_feedback

    st.subheader("💳 Calculateur 'Reste à vivre'")
    st.caption("Calculez votre budget disponible après les charges fixes")

    confirmed = get_all_feedback(status="confirmed")

    if not confirmed:
        st.info("Validez d'abord vos abonnements pour utiliser le calculateur.")
        return

    # Estimer les charges mensuelles
    monthly_charges = 0.0
    for sub in confirmed:
        notes = sub.get("notes", "").lower()
        # Essayer d'extraire le montant des notes
        import re

        amount_match = re.search(r"(\d+[.,]?\d*)\s*€", notes)
        if amount_match:
            try:
                amount = float(amount_match.group(1).replace(",", "."))
                # Ajuster selon la fréquence
                if "annuel" in notes:
                    amount = amount / 12
                elif "trimestriel" in notes:
                    amount = amount / 3
                monthly_charges += abs(amount)
            except ValueError:
                pass

    # Interface du calculateur
    col1, col2 = st.columns(2)

    with col1:
        current_balance = st.number_input(
            "Solde actuel (€)",
            min_value=0.0,
            value=1500.0,
            step=100.0,
        )

    with col2:
        days_ahead = st.selectbox(
            "Projection",
            options=[7, 15, 30, 60, 90],
            format_func=lambda x: f"{x} jours",
            index=2,  # 30 jours par défaut
        )

    # Estimer les charges à venir
    upcoming = monthly_charges * (days_ahead / 30)
    remaining = current_balance - upcoming

    if st.button("🚀 Calculer", use_container_width=True, type="primary"):
        cols = st.columns(3)

        with cols[0]:
            st.metric("Solde actuel", f"{current_balance:,.2f} €")

        with cols[1]:
            st.metric(
                f"Charges prévues ({days_ahead}j)",
                f"-{upcoming:,.2f} €",
                delta_color="inverse",
            )

        with cols[2]:
            status = "Sain" if remaining > 0 else "Critique"
            color = "normal" if remaining > 0 else "inverse"
            st.metric(
                "🎯 Reste à vivre",
                f"{remaining:,.2f} €",
                delta=status,
                delta_color=color,
            )

        if remaining < 0:
            st.error("⚠️ Attention : vos charges fixes dépassent votre solde actuel !")
        elif remaining < upcoming * 0.5:
            st.warning("💡 Votre marge de manoeuvre est limitée.")
        else:
            st.success("✅ Votre budget est sain.")
