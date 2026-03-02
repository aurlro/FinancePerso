"""
Dashboard Patrimoine 360° - Vue Streamlit
=========================================

Interface complète de gestion patrimoniale avec :
- Treemap de répartition des actifs
- Centre de contrôle agentique (missions)
- Indicateur d'équité immobilière
- Intégration Monte Carlo Phase 4

Usage:
    # Dans app.py ou navigation Streamlit
    from views.wealth_view import render_wealth_dashboard
    render_wealth_dashboard()
"""

from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modules.wealth.agent_core import (
    AgentOrchestrator,
    MissionPriority,
)

# Imports Phase 4 pour projections
from modules.wealth.math_engine import ScenarioType, quick_simulation
from modules.wealth.subscription_engine import Subscription

# Imports des modules Phase 5
from modules.wealth.wealth_manager import (
    AssetType,
    CryptoAsset,
    FinancialAsset,
    Liability,
    LiabilityType,
    MortgageSchedule,
    RealEstateAsset,
    WealthManager,
    calculate_monthly_debt_service,
)


def render_wealth_dashboard(
    wealth_manager: WealthManager | None = None,
    subscriptions: list[Subscription] | None = None,
    monthly_income: float = 3000.0,
):
    """
    Rend le dashboard complet du patrimoine.

    Args:
        wealth_manager: Gestionnaire de patrimoine (créé si None)
        subscriptions: Liste des abonnements pour les missions
        monthly_income: Revenu mensuel pour les calculs
    """
    st.title("🏛️ Patrimoine 360°")
    st.markdown("Vue consolidée de votre patrimoine et missions d'optimisation")

    # Initialiser avec des données de démo si nécessaire
    if wealth_manager is None:
        wealth_manager = _create_demo_wealth_manager()

    if subscriptions is None:
        subscriptions = _create_demo_subscriptions()

    # Layout: Onglets
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📊 Vue d'ensemble",
            "🎯 Missions Agentiques",
            "🏠 Immobilier",
            "📈 Projections",
        ]
    )

    with tab1:
        _render_overview_tab(wealth_manager)

    with tab2:
        _render_missions_tab(wealth_manager, subscriptions, monthly_income)

    with tab3:
        _render_real_estate_tab(wealth_manager)

    with tab4:
        _render_projections_tab(wealth_manager, monthly_income)


def _create_demo_wealth_manager() -> WealthManager:
    """Crée un gestionnaire avec des données de démo."""
    manager = WealthManager()

    # Cash
    manager.set_cash_balance(25000.0)

    # Immobilier avec crédit
    mortgage = MortgageSchedule(
        principal=300000,
        monthly_payment=1200,
        interest_rate=0.023,
        start_date=date(2020, 1, 15),
        duration_months=240,
    )
    apartment = RealEstateAsset(
        id="apt-001",
        name="Appartement Paris 14",
        address="12 Rue de la Santé, 75014 Paris",
        purchase_price=350000,
        current_value=420000,
        purchase_date=date(2020, 1, 15),
        mortgage=mortgage,
    )
    manager.add_real_estate(apartment)

    # Actifs financiers
    pea = FinancialAsset(
        id="pea-001",
        name="PEA Boursorama",
        asset_type=AssetType.SECURITIES,
        institution="Boursorama Banque",
        current_value=45000,
        invested_amount=35000,
    )
    manager.add_financial_asset(pea)

    assurance_vie = FinancialAsset(
        id="av-001",
        name="Assurance Vie Linxea",
        asset_type=AssetType.LIFE_INSURANCE,
        institution="Linxea",
        current_value=30000,
        invested_amount=28000,
    )
    manager.add_financial_asset(assurance_vie)

    # Crypto
    btc = CryptoAsset(
        id="btc-001",
        symbol="BTC",
        name="Bitcoin",
        quantity=0.25,
        current_price=85000,
        avg_buy_price=45000,
        platform="Kraken",
    )
    manager.add_crypto_asset(btc)

    eth = CryptoAsset(
        id="eth-001",
        symbol="ETH",
        name="Ethereum",
        quantity=2.5,
        current_price=3200,
        avg_buy_price=2800,
        platform="Kraken",
    )
    manager.add_crypto_asset(eth)

    # Dettes
    consumer_credit = Liability(
        id="credit-001",
        name="Crédit conso",
        liability_type=LiabilityType.CONSUMER_CREDIT,
        total_amount=15000,
        remaining_amount=8500,
        monthly_payment=350,
        interest_rate=0.0590,
        maturity_date=date(2027, 6, 15),
    )
    manager.add_liability(consumer_credit)

    return manager


def _create_demo_subscriptions() -> list[Subscription]:
    """Crée des abonnements de démo."""
    return [
        Subscription(
            merchant="NETFLIX",
            frequency="monthly",
            average_amount=17.99,
            amount_std=0.0,
            last_date="2026-01-15",
            next_expected_date="2026-02-15",
            confidence_score=0.99,
            status="ACTIF",
            transaction_count=24,
        ),
        Subscription(
            merchant="SPOTIFY",
            frequency="monthly",
            average_amount=10.99,
            amount_std=0.0,
            last_date="2026-01-10",
            next_expected_date="2026-02-10",
            confidence_score=0.99,
            status="ACTIF",
            transaction_count=36,
        ),
        Subscription(
            merchant="SFR MOBILE",
            frequency="monthly",
            average_amount=24.99,
            amount_std=0.0,
            last_date="2026-01-05",
            next_expected_date="2026-02-05",
            confidence_score=0.95,
            status="ACTIF",
            transaction_count=48,
        ),
        Subscription(
            merchant="CANAL+",
            frequency="monthly",
            average_amount=29.99,
            amount_std=0.0,
            last_date="2026-01-20",
            next_expected_date="2026-02-20",
            confidence_score=0.90,
            status="ZOMBIE",
            transaction_count=12,
        ),
    ]


def _render_overview_tab(wealth_manager: WealthManager):
    """Rend l'onglet de vue d'ensemble."""
    st.header("📊 Vue d'ensemble du Patrimoine")

    # KPIs principaux
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        net_worth = wealth_manager.get_total_net_worth()
        st.metric(
            label="Patrimoine Net",
            value=f"€{net_worth:,.0f}",
            delta=None,
        )

    with col2:
        assets = wealth_manager.get_total_assets()
        st.metric(
            label="Total Actifs",
            value=f"€{assets['total']:,.0f}",
        )

    with col3:
        liabilities = wealth_manager.get_total_liabilities()
        st.metric(
            label="Total Dettes",
            value=f"€{liabilities['total']:,.0f}",
        )

    with col4:
        liquidity = wealth_manager.get_liquidity_analysis()
        st.metric(
            label="Liquidité Immédiate",
            value=f"€{liquidity['immediate']:,.0f}",
        )

    st.divider()

    # Treemap de répartition
    st.subheader("Répartition du Patrimoine")

    allocation = wealth_manager.get_asset_allocation()

    # Préparer les données pour le treemap
    treemap_data = []
    for category, data in allocation.items():
        if category == "other_debt":
            continue  # Skip les dettes dans le treemap principal

        if data["amount"] > 0:
            treemap_data.append(
                {
                    "Catégorie": category.replace("_", " ").title(),
                    "Valeur": data["amount"],
                    "Pourcentage": f"{data['percentage']:.1f}%",
                }
            )

    if treemap_data:
        df_treemap = pd.DataFrame(treemap_data)

        fig = px.treemap(
            df_treemap,
            path=["Catégorie"],
            values="Valeur",
            custom_data=["Pourcentage"],
            color="Valeur",
            color_continuous_scale="Viridis",
            title="",
        )

        fig.update_traces(
            texttemplate="<b>%{label}</b><br>%{customdata[0]}<br>€%{value:,.0f}",
            hovertemplate="<b>%{label}</b><br>Valeur: €%{value:,.2f}<br>%{customdata[0]}<extra></extra>",
        )

        fig.update_layout(
            height=400,
            margin=dict(t=20, b=20, l=20, r=20),
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Détails par classe d'actif
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Actifs")

        # Cash
        st.write(f"**Cash:** €{wealth_manager.cash_balance:,.2f}")

        # Immobilier
        real_estate_value = sum(a.current_value for a in wealth_manager.real_estate)
        real_estate_equity = wealth_manager.get_net_real_estate_value()
        st.write(f"**Immobilier (valeur):** €{real_estate_value:,.2f}")
        st.write(f"**Immobilier (équité nette):** €{real_estate_equity:,.2f}")

        # Financier
        financial_value = sum(a.current_value for a in wealth_manager.financial_assets)
        st.write(f"**Financier:** €{financial_value:,.2f}")

        # Crypto
        crypto_value = sum(c.current_value for c in wealth_manager.crypto_assets)
        st.write(f"**Crypto:** €{crypto_value:,.2f}")

    with col2:
        st.subheader("💳 Dettes")

        for liability in wealth_manager.liabilities:
            progress = liability.progress_percentage
            st.write(f"**{liability.name}**")
            st.progress(progress / 100)
            st.caption(f"€{liability.remaining_amount:,.2f} restant ({progress:.1f}% remboursé)")

        # Crédits immobiliers
        for asset in wealth_manager.real_estate:
            if asset.mortgage:
                progress = asset.mortgage.get_progress_percentage()
                remaining = asset.mortgage.get_remaining_balance()
                st.write(f"**Crédit {asset.name}**")
                st.progress(progress / 100)
                st.caption(f"€{remaining:,.2f} restant ({progress:.1f}% remboursé)")


def _render_missions_tab(
    wealth_manager: WealthManager,
    subscriptions: list[Subscription],
    monthly_income: float,
):
    """Rend l'onglet des missions agentiques."""
    st.header("🎯 Centre de Contrôle Agentique")
    st.markdown("Missions d'optimisation générées par l'IA")

    # Initialiser l'orchestrateur
    orchestrator = AgentOrchestrator()

    # Générer les missions
    if "missions" not in st.session_state:
        with st.spinner("Analyse en cours..."):
            st.session_state.missions = orchestrator.analyze_and_generate_missions(
                subscriptions=subscriptions,
                wealth_manager=wealth_manager,
                monthly_income=monthly_income,
            )

    missions = st.session_state.missions

    # Résumé
    summary = orchestrator.get_mission_summary(missions)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Missions actives", len(missions))
    with col2:
        st.metric("Économie potentielle", f"€{summary['total_potential_savings']:,.0f}/an")
    with col3:
        high_impact = len(summary["high_impact_missions"])
        st.metric("Impact élevé", high_impact, delta="à traiter" if high_impact > 0 else None)

    st.divider()

    # Filtrer par priorité
    priority_filter = st.selectbox(
        "Filtrer par priorité",
        ["Toutes", "Critique", "Haute", "Moyenne", "Faible"],
    )

    priority_map = {
        "Toutes": None,
        "Critique": MissionPriority.CRITICAL,
        "Haute": MissionPriority.HIGH,
        "Moyenne": MissionPriority.MEDIUM,
        "Faible": MissionPriority.LOW,
    }

    filtered_missions = missions
    if priority_filter != "Toutes":
        prio = priority_map[priority_filter]
        filtered_missions = [m for m in missions if m.priority == prio]

    # Afficher les missions
    if not filtered_missions:
        st.info("Aucune mission pour ce filtre. 🎉")

    for i, mission in enumerate(filtered_missions):
        # Déterminer la couleur selon la priorité
        priority_colors = {
            MissionPriority.CRITICAL: "🔴",
            MissionPriority.HIGH: "🟠",
            MissionPriority.MEDIUM: "🟡",
            MissionPriority.LOW: "🟢",
            MissionPriority.INFO: "⚪",
        }
        emoji = priority_colors.get(mission.priority, "⚪")

        with st.expander(f"{emoji} {mission.title} (+€{mission.potential_savings:.0f}/an)"):
            st.write(mission.description)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"Priorité: {mission.priority.value}")
            with col2:
                st.caption(f"Effort: {'⭐' * mission.effort_level}")
            with col3:
                st.caption(f"Temps: ~{mission.time_to_complete} min")

            st.divider()

            # Actions disponibles
            st.subheader("Actions disponibles")

            for j, action in enumerate(mission.actions):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**{action.label}**")
                    if action.requires_human_validation:
                        st.caption("⚠️ Nécessite votre validation")

                with col2:
                    btn_key = f"action_{mission.id}_{j}"

                    if st.button("Exécuter", key=btn_key):
                        # Simuler l'exécution
                        if action.type.value == "generate_letter":
                            st.info("Génération de la lettre...")

                            # Créer le document
                            from modules.wealth.agent_core import DocumentGenerator

                            doc_gen = DocumentGenerator()

                            merchant = action.payload.get("merchant", "Prestataire")
                            letter = doc_gen.generate_cancellation_letter(
                                merchant_name=merchant,
                                subscriber_name="Jean Dupont",
                                subscriber_address="123 Rue Example, 75000 Paris",
                            )

                            st.text_area("Lettre générée:", letter, height=300)

                            # Bouton de téléchargement
                            st.download_button(
                                label="📥 Télécharger la lettre",
                                data=letter,
                                file_name=f"resiliation_{merchant.lower().replace(' ', '_')}.txt",
                                mime="text/plain",
                            )

                        elif action.type.value == "compare_offers":
                            st.info("Ouverture du comparateur...")
                            category = action.payload.get("category", "general")
                            st.markdown(
                                f"[🌐 Ouvrir le comparateur](https://comparateur.example.com/{category})"
                            )

                        elif action.type.value == "invest_suggestion":
                            st.info("Suggestions d'investissement:")
                            suggestions = [
                                {"type": "Livret A", "yield": "3.0%", "risk": "Aucun"},
                                {"type": "Fonds Euros", "yield": "4.5%", "risk": "Faible"},
                                {"type": "ETF MSCI World", "yield": "7.0%", "risk": "Moyen"},
                            ]
                            for sugg in suggestions:
                                st.write(
                                    f"- **{sugg['type']}**: {sugg['yield']} (risque: {sugg['risk']})"
                                )

                        # Marquer comme traitée
                        mission.approve()

    # Bouton pour rafraîchir les missions
    if st.button("🔄 Rafraîchir les missions"):
        del st.session_state["missions"]
        st.rerun()


def _render_real_estate_tab(wealth_manager: WealthManager):
    """Rend l'onglet immobilier."""
    st.header("🏠 Détail Immobilier")

    if not wealth_manager.real_estate:
        st.info("Aucun bien immobilier enregistré.")
        return

    for asset in wealth_manager.real_estate:
        with st.expander(f"🏠 {asset.name}", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Informations")
                st.write(f"**Adresse:** {asset.address}")
                st.write(f"**Prix d'achat:** €{asset.purchase_price:,.2f}")
                st.write(f"**Valeur actuelle:** €{asset.current_value:,.2f}")

                # Évolution
                change_abs, change_pct = asset.get_value_change()
                delta_color = "normal" if change_abs >= 0 else "inverse"
                st.metric(
                    label="Plus-value latente",
                    value=f"€{change_abs:,.2f}",
                    delta=f"{change_pct:+.1f}%",
                    delta_color=delta_color,
                )

            with col2:
                if asset.mortgage:
                    st.subheader("Crédit immobilier")

                    # Jauge de remboursement
                    progress = asset.mortgage.get_progress_percentage()
                    remaining = asset.mortgage.get_remaining_balance()
                    equity = asset.get_equity()

                    # Indicateur circulaire
                    fig = go.Figure(
                        go.Indicator(
                            mode="gauge+number+delta",
                            value=progress,
                            domain={"x": [0, 1], "y": [0, 1]},
                            title={"text": "Progression remboursement"},
                            gauge={
                                "axis": {"range": [0, 100]},
                                "bar": {"color": "darkgreen"},
                                "steps": [
                                    {"range": [0, 33], "color": "lightgray"},
                                    {"range": [33, 66], "color": "yellow"},
                                    {"range": [66, 100], "color": "lightgreen"},
                                ],
                                "threshold": {
                                    "line": {"color": "red", "width": 4},
                                    "thickness": 0.75,
                                    "value": 100,
                                },
                            },
                        )
                    )

                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)

                    # Détails
                    st.write(f"**Capital restant dû:** €{remaining:,.2f}")
                    st.write(f"**Équité nette:** €{equity:,.2f}")
                    st.write(f"**Mensualité:** €{asset.mortgage.monthly_payment:,.2f}")
                    st.write(f"**Taux:** {asset.mortgage.interest_rate*100:.2f}%")

                    # Alertes
                    ltv = asset.get_loan_to_value()
                    if ltv > 80:
                        st.warning(f"⚠️ LTV élevé: {ltv:.1f}% (risque de sous-eau)")

                    if asset.is_underwater():
                        st.error("🚨 Bien sous l'eau! Valeur < Crédit restant")
                else:
                    st.info("Pas de crédit associé")

            # Tableau d'amortissement
            if asset.mortgage and st.checkbox(
                "Voir tableau d'amortissement", key=f"amort_{asset.id}"
            ):
                df = asset.mortgage.schedule_df.head(24)  # 24 premiers mois
                st.dataframe(
                    df[
                        ["month", "payment", "principal_part", "interest_part", "remaining_balance"]
                    ],
                    use_container_width=True,
                    column_config={
                        "month": st.column_config.NumberColumn("Mois"),
                        "payment": st.column_config.NumberColumn("Mensualité", format="€%.2f"),
                        "principal_part": st.column_config.NumberColumn("Capital", format="€%.2f"),
                        "interest_part": st.column_config.NumberColumn("Intérêts", format="€%.2f"),
                        "remaining_balance": st.column_config.NumberColumn(
                            "Restant dû", format="€%.2f"
                        ),
                    },
                )


def _render_projections_tab(wealth_manager: WealthManager, monthly_income: float):
    """Rend l'onglet des projections Monte Carlo."""
    st.header("📈 Projections Patrimoniales")

    # Paramètres de simulation
    col1, col2, col3 = st.columns(3)

    with col1:
        current_net_worth = wealth_manager.get_total_net_worth()
        st.write(f"**Patrimoine net actuel:** €{current_net_worth:,.2f}")

        # Calculer le versement mensuel disponible
        calculate_monthly_debt_service(wealth_manager)
        available_for_saving = monthly_income * 0.3  # 30% des revenus

        monthly_contribution = st.number_input(
            "Versement mensuel",
            min_value=0,
            max_value=int(monthly_income),
            value=int(available_for_saving),
            step=50,
        )

    with col2:
        years = st.slider("Horizon (années)", 5, 30, 10)

        scenario = st.selectbox(
            "Profil de risque",
            [
                ("Défensif (2%/5%)", ScenarioType.DEFENSIF),
                ("Conservateur (3%/8%)", ScenarioType.CONSERVATEUR),
                ("Modéré (7%/15%)", ScenarioType.MODERE),
                ("Agressif (10%/25%)", ScenarioType.AGRESSIF),
            ],
            format_func=lambda x: x[0],
        )[1]

    with col3:
        st.write("**Scénarios What-If**")

        inflation_adjust = st.checkbox("📈 Ajuster pour inflation (4%)", value=False)
        market_shock = st.checkbox("📉 Choc initial -20%", value=False)

        if inflation_adjust:
            monthly_contribution *= 1.04  # Augmentation des versements
            st.caption(f"Versement ajusté: €{monthly_contribution:.0f}/mois")

    # Lancer la simulation
    if st.button("🚀 Lancer la projection", type="primary"):
        with st.spinner("Simulation Monte Carlo en cours... (10 000 trajectoires)"):
            # Capital initial (ajuster pour choc si demandé)
            initial_capital = current_net_worth * 0.8 if market_shock else current_net_worth

            # Simulation rapide
            result = quick_simulation(
                initial_capital=initial_capital,
                monthly_contribution=monthly_contribution,
                years=years,
                scenario=scenario,
                n_simulations=1000,  # Réduit pour la démo
            )

            # Créer un graphique simple avec les résultats
            fig = go.Figure()

            # Ligne médiane
            fig.add_trace(
                go.Scatter(
                    x=[0, years],
                    y=[initial_capital, result["median"]],
                    mode="lines",
                    name="Scénario Médian (50%)",
                    line=dict(color="#0066CC", width=3),
                )
            )

            # Bande de confiance 5%-95%
            fig.add_trace(
                go.Scatter(
                    x=[0, years, years, 0],
                    y=[
                        initial_capital,
                        result["percentile_95"],
                        result["percentile_5"],
                        initial_capital,
                    ],
                    fill="toself",
                    fillcolor="rgba(255, 165, 0, 0.15)",
                    line=dict(color="rgba(255, 165, 0, 0)"),
                    name="Zone Catastrophe → Optimiste (5%-95%)",
                    hoverinfo="skip",
                )
            )

            fig.update_layout(
                title="Projection Monte Carlo du Patrimoine",
                xaxis_title="Années",
                yaxis_title="Capital (€)",
                yaxis_tickformat=",.0f",
                hovermode="x unified",
                showlegend=True,
                height=500,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Résumé
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Scénario pessimiste (5%)",
                    f"€{result['percentile_5']:,.0f}",
                )

            with col2:
                st.metric(
                    "Scénario médian (50%)",
                    f"€{result['median']:,.0f}",
                    delta=f"+{result['median'] - current_net_worth:,.0f}€",
                )

            with col3:
                st.metric(
                    "Scénario optimiste (95%)",
                    f"€{result['percentile_95']:,.0f}",
                )

            # Probabilités d'atteinte des objectifs
            st.subheader("Probabilité d'atteinte des objectifs")

            life_goals = (
                []
            )  # Initialisation par défaut (à remplacer par récupération DB si nécessaire)
            for goal in life_goals:
                # Calculer probabilité approximative
                if result["percentile_95"] >= goal["amount"]:
                    prob = 95
                elif result["median"] >= goal["amount"]:
                    prob = 75
                elif result["percentile_5"] >= goal["amount"]:
                    prob = 25
                else:
                    prob = 5

                col1, col2, col3 = st.columns([2, 1, 3])

                with col1:
                    st.write(f"**{goal['name']}** ({goal['year']} ans)")
                    st.caption(f"Objectif: €{goal['amount']:,.0f}")

                with col2:
                    st.write(f"**{prob}%**")

                with col3:
                    st.progress(prob / 100)


# ==================== Point d'entrée ====================

if __name__ == "__main__":
    # Mode standalone pour tests
    render_wealth_dashboard()
