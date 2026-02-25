"""
Vue "Abonnements" - Interface de gestion des charges fixes.
==========================================================

Cette vue affiche :
- KPIs : Total charges fixes mensuelles vs Revenus
- Tableau des abonnements avec barre de progression
- Alertes "Zombie" et augmentations suspectes

Usage:
    import streamlit as st
    from views.subscriptions import render_subscriptions_page
    
    render_subscriptions_page()
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from src.subscription_engine import (
    SubscriptionDetector,
    SubscriptionStatus,
    calculate_remaining_budget,
)
from modules.db.transactions import get_all_transactions
from modules.logger import logger


def render_subscriptions_page():
    """Affiche la page complète des abonnements."""
    st.title("📅 Abonnements & Charges Fixes")
    st.markdown("---")
    
    # Chargement des données
    df = get_all_transactions()
    
    if df.empty:
        st.info("Aucune transaction trouvée. Importez des données pour commencer.")
        return
    
    # Détecter les abonnements
    detector = SubscriptionDetector()
    subscriptions = detector.detect_subscriptions(df)
    
    if not subscriptions:
        st.info("Aucun abonnement détecté. L'algorithme nécessite au moins 3 occurrences.")
        return
    
    # Section 1: KPIs
    render_kpis_section(subscriptions, df)
    
    st.markdown("---")
    
    # Section 2: Tableau des abonnements
    render_subscriptions_table(subscriptions)
    
    st.markdown("---")
    
    # Section 3: Alertes Zombie
    render_zombie_alerts(detector, subscriptions)
    
    st.markdown("---")
    
    # Section 4: Détections d'augmentations
    render_increase_alerts(detector, df)
    
    st.markdown("---")
    
    # Section 5: Calculateur "Reste à Vivre"
    render_remaining_budget_calculator(subscriptions)


def render_kpis_section(subscriptions, df):
    """Affiche les KPIs principaux."""
    st.header("📊 Vue d'ensemble")
    
    # Calculer les KPIs
    detector = SubscriptionDetector()
    monthly_total = detector.calculate_monthly_fixed_charges(subscriptions)
    
    # Nombre par statut
    active_count = sum(1 for s in subscriptions if s.status == SubscriptionStatus.ACTIF.value)
    zombie_count = sum(1 for s in subscriptions if s.status == SubscriptionStatus.ZOMBIE.value)
    risk_count = sum(1 for s in subscriptions if s.status == SubscriptionStatus.A_RISQUE.value)
    
    # Calculer le ratio charges/revenus si possible
    income_df = df[df["amount"] > 0]
    monthly_income = income_df["amount"].sum() / 12 if not income_df.empty else 0
    
    # Afficher les métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Charges fixes mensuelles",
            value=f"{monthly_total:,.2f} €",
        )
    
    with col2:
        st.metric(
            label="✅ Abonnements actifs",
            value=active_count,
        )
    
    with col3:
        if zombie_count > 0:
            st.metric(
                label="🧟 Abonnements zombies",
                value=zombie_count,
                delta="À vérifier",
                delta_color="off",
            )
        else:
            st.metric(label="🧟 Abonnements zombies", value=0)
    
    with col4:
        if risk_count > 0:
            st.metric(
                label="⚠️ À risque",
                value=risk_count,
                delta="Variation détectée",
                delta_color="inverse",
            )
        else:
            st.metric(label="⚠️ À risque", value=0)
    
    # Barre de progression charges/revenus
    if monthly_income > 0:
        ratio = min(monthly_total / monthly_income, 1.0)
        st.markdown(f"**Ratio charges fixes / revenus :** {ratio*100:.1f}%")
        
        # Couleur selon le ratio
        if ratio < 0.3:
            color = "green"
            status = "Sain"
        elif ratio < 0.5:
            color = "orange"
            status = "Modéré"
        else:
            color = "red"
            status = "Élevé"
        
        st.progress(ratio, text=f"{status} ({ratio*100:.1f}%)")


def render_subscriptions_table(subscriptions):
    """Affiche le tableau des abonnements avec barres de progression."""
    st.header("📋 Vos Abonnements")
    
    # Préparer les données
    today = datetime.now()
    
    table_data = []
    for sub in subscriptions:
        next_date = datetime.strptime(sub.next_expected_date, "%Y-%m-%d")
        days_until = (next_date - today).days
        
        # Progression vers prochain prélèvement
        # Pour mensuel: 0-30 jours
        if sub.frequency == "monthly":
            progress = max(0, min(1, 1 - (days_until / 30)))
        elif sub.frequency == "weekly":
            progress = max(0, min(1, 1 - (days_until / 7)))
        else:
            progress = 0.5  # Default
        
        # Icône selon statut
        status_icon = {
            SubscriptionStatus.ACTIF.value: "🟢",
            SubscriptionStatus.A_RISQUE.value: "🟠",
            SubscriptionStatus.ZOMBIE.value: "🧟",
            SubscriptionStatus.INACTIF.value: "⚫",
        }.get(sub.status, "⚪")
        
        table_data.append({
            "Statut": status_icon,
            "Commerçant": sub.merchant,
            "Catégorie": sub.category or "-",
            "Montant": f"{sub.average_amount:,.2f} €",
            "Fréquence": _translate_frequency(sub.frequency),
            "Prochain": sub.next_expected_date,
            "Jours restants": max(0, days_until),
            "Progression": progress,
            "Confiance": f"{sub.confidence_score*100:.0f}%",
        })
    
    df_table = pd.DataFrame(table_data)
    
    # Afficher avec coloration
    st.dataframe(
        df_table,
        column_config={
            "Progression": st.column_config.ProgressColumn(
                "Progression",
                help="Temps écoulé depuis le dernier prélèvement",
                format="%d%%",
                min_value=0,
                max_value=1,
            ),
            "Statut": st.column_config.Column("Statut", width="small"),
            "Commerçant": st.column_config.Column("Commerçant", width="medium"),
            "Montant": st.column_config.Column("Montant", width="small"),
        },
        hide_index=True,
        use_container_width=True,
    )
    
    # Légende
    st.caption("""
    **Légende:** 🟢 Actif | 🟠 Variation détectée | 🧟 Zombie (inactif) | ⚫ Résilié
    """)


def render_zombie_alerts(detector, subscriptions):
    """Affiche les alertes pour les abonnements zombies."""
    zombies = detector.detect_zombie_subscriptions(subscriptions)
    
    if zombies:
        st.header("🧟 Abonnements suspects")
        st.warning(f"{len(zombies)} abonnement(s) n'ont pas eu de prélèvement récent.")
        
        for zombie in zombies:
            with st.expander(f"🧟 {zombie.merchant} - {zombie.average_amount:,.2f} €"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Dernier prélèvement:** {zombie.last_date}")
                    st.write(f"**Fréquence:** {_translate_frequency(zombie.frequency)}")
                    st.write(f"**Catégorie:** {zombie.category or 'Non catégorisé'}")
                
                with col2:
                    st.write(f"**Transactions historiques:** {zombie.transaction_count}")
                    st.write(f"**Confiance de détection:** {zombie.confidence_score*100:.0f}%")
                    
                    if zombie.metadata:
                        cv = zombie.metadata.get("amount_cv", 0)
                        st.write(f"**Variabilité montant:** {cv*100:.1f}%")
                
                st.info("💡 **Action suggérée:** Vérifiez si cet abonnement est toujours actif ou s'il peut être résilié.")


def render_increase_alerts(detector, df):
    """Affiche les alertes d'augmentation de montant."""
    increases = detector.detect_amount_increases(df)
    
    if increases:
        st.header("📈 Augmentations détectées")
        st.warning(f"{len(increases)} augmentation(s) de montant suspects.")
        
        for inc in increases:
            with st.expander(f"📈 {inc['merchant']} (+{inc['increase_percent']}%)"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Ancien montant moyen",
                        value=f"{inc['old_average']:,.2f} €",
                    )
                
                with col2:
                    st.metric(
                        label="Nouveau montant moyen",
                        value=f"{inc['recent_average']:,.2f} €",
                        delta=f"+{inc['increase_percent']}%",
                        delta_color="inverse",
                    )
                
                with col3:
                    st.write(f"**Catégorie:** {inc['category'] or 'Non catégorisé'}")
                
                st.info("💡 **Action suggérée:** Vérifiez si cette augmentation est justifiée ou si vous pouvez négocier/résilier.")


def render_remaining_budget_calculator(subscriptions):
    """Affiche le calculateur de 'Reste à Vivre'."""
    st.header("💳 Calculateur 'Reste à Vivre'")
    
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
    
    if st.button("🚀 Calculer mon reste à vivre", use_container_width=True):
        result = calculate_remaining_budget(
            current_balance=current_balance,
            subscriptions=[sub.to_dict() for sub in subscriptions],
            days_ahead=days_ahead,
        )
        
        # Afficher le résultat
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Solde actuel",
                value=f"{result.current_balance:,.2f} €",
            )
        
        with col2:
            st.metric(
                label=f"Charges à venir ({days_ahead}j)",
                value=f"-{result.total_upcoming:,.2f} €",
                delta_color="inverse",
            )
        
        with col3:
            color = "normal" if result.status == "ok" else "inverse"
            st.metric(
                label="🎯 Vrai Reste à Vivre",
                value=f"{result.remaining_budget:,.2f} €",
                delta="Sain" if result.status == "ok" else "Critique",
                delta_color=color,
            )
        
        # Détails des prélèvements à venir
        if result.upcoming_charges:
            st.markdown("#### 📅 Prélèvements à venir")
            
            upcoming_df = pd.DataFrame(result.upcoming_charges)
            upcoming_df = upcoming_df.sort_values('date')
            
            st.dataframe(
                upcoming_df,
                column_config={
                    "merchant": "Commerçant",
                    "amount": st.column_config.NumberColumn("Montant", format="%.2f €"),
                    "date": "Date prévue",
                },
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.success("✅ Aucun prélèvement prévu dans cette période !")


def _translate_frequency(freq: str) -> str:
    """Traduit les fréquences en français."""
    translations = {
        "weekly": "Hebdomadaire",
        "bimonthly": "Bimensuel",
        "monthly": "Mensuel",
        "quarterly": "Trimestriel",
        "semiannual": "Semestriel",
        "annual": "Annuel",
        "irregular": "Irrégulier",
    }
    return translations.get(freq, freq)


# Point d'entrée pour Streamlit
if __name__ == "__main__":
    render_subscriptions_page()
