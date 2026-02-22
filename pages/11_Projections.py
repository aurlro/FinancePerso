"""
Vue "Projections & Scénarios" - Interface What-If Streamlit
==========================================================

Cette vue permet à l'utilisateur de simuler différents scénarios:
- "Et si l'inflation monte à 4% ?"
- "Et si je place 200€ de plus par mois ?"
- "Et si le marché chute de 20% ?"

Usage:
    import streamlit as st
    from views.projections import render_projections_page
    
    render_projections_page()
"""

import streamlit as st
import numpy as np
from datetime import datetime
from typing import Dict

from src.math_engine import MonteCarloSimulator, ScenarioType, quick_simulation
from src.visualizations import plot_wealth_projection, plot_scenario_comparison
from src.subscription_engine import calculate_remaining_budget, SubscriptionDetector
from modules.db.transactions import get_all_transactions
from modules.logger import logger


def render_projections_page():
    """Affiche la page complète des projections et scénarios."""
    st.title("🔮 Projections Patrimoniales & Scénarios")
    st.markdown("---")
    
    # Section 1: Configuration de base
    st.header("⚙️ Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Situation actuelle")
        
        # Capital initial
        initial_capital = st.number_input(
            "Capital actuel (€)",
            min_value=0,
            max_value=10_000_000,
            value=10_000,
            step=1_000,
            help="Capital déjà épargné et investi",
        )
        
        # Versement mensuel - Intégration avec Reste à Vivre Phase 3
        default_contribution = get_default_monthly_contribution()
        
        monthly_contribution = st.number_input(
            "Versement mensuel (€)",
            min_value=0,
            max_value=50_000,
            value=default_contribution,
            step=50,
            help="Montant que vous pouvez épargner chaque mois (basé sur votre 'Reste à Vivre')",
        )
        
        if default_contribution > 0:
            st.info(f"💡 Basé sur votre analyse 'Reste à Vivre' (Phase 3), vous pouvez épargner environ **{default_contribution}€/mois**.")
    
    with col2:
        st.subheader("Horizon")
        
        # Durée
        years = st.slider(
            "Durée de projection (années)",
            min_value=1,
            max_value=40,
            value=10,
            help="Sur combien d'années projeter votre patrimoine",
        )
        
        # Objectif
        target_amount = st.number_input(
            "Objectif patrimonial (€) (optionnel)",
            min_value=0,
            max_value=10_000_000,
            value=100_000,
            step=10_000,
            help="Capital que vous souhaitez atteindre (pour calcul de probabilité)",
        )
    
    st.markdown("---")
    
    # Section 2: Scénario de base
    st.header("📊 Scénario de base")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        scenario_type = st.selectbox(
            "Profil de risque",
            options=[
                ScenarioType.DEFENSIF,
                ScenarioType.CONSERVATEUR,
                ScenarioType.MODERE,
                ScenarioType.AGRESSIF,
                ScenarioType.CRYPTO,
            ],
            format_func=lambda x: {
                ScenarioType.DEFENSIF: "🛡️ Défensif (Livret, 2%)",
                ScenarioType.CONSERVATEUR: "📋 Conservateur (Obligations, 4%)",
                ScenarioType.MODERE: "📈 Modéré (Mixte, 7%)",
                ScenarioType.AGRESSIF: "🚀 Agressif (Actions, 10%)",
                ScenarioType.CRYPTO: "⚡ Crypto (Très risqué, 20%)",
            }.get(x, x.value),
            help="Choisissez un profil correspondant à votre tolérance au risque",
        )
    
    with col2:
        annual_return = st.slider(
            "Rendement annuel attendu (%)",
            min_value=-5.0,
            max_value=30.0,
            value=int(SCENARIO_PARAMS[scenario_type]["mu"] * 100),
            step=0.5,
            help="μ (mu) - Rendement moyen historique attendu",
        ) / 100
    
    with col3:
        volatility = st.slider(
            "Volatilité / Risque (%)",
            min_value=0.0,
            max_value=100.0,
            value=int(SCENARIO_PARAMS[scenario_type]["sigma"] * 100),
            step=1.0,
            help="σ (sigma) - Incertitude/volatilité du rendement",
        ) / 100
    
    # Scénarios What-If
    st.markdown("---")
    st.header("🎮 Scénarios What-If")
    st.markdown("Testez différentes hypothèses pour voir leur impact sur votre patrimoine.")
    
    what_if_scenarios = create_what_if_scenarios(
        initial_capital, monthly_contribution, annual_return, volatility, years
    )
    
    # Simulation
    run_simulation = st.button("🚀 Lancer la simulation", use_container_width=True)
    
    if run_simulation:
        with st.spinner(f"Simulation de 10 000 trajectoires sur {years} ans..."):
            try:
                # Simulation de base
                simulator = MonteCarloSimulator(
                    initial_capital=initial_capital,
                    monthly_contribution=monthly_contribution,
                    annual_return=annual_return,
                    volatility=volatility,
                    years=years,
                )
                
                result = simulator.run_simulation(n_simulations=10000)
                stats = result.statistics
                
                # Affichage des résultats
                display_simulation_results(result, stats, target_amount)
                
                # Affichage du graphique principal
                st.subheader("📈 Cône de Probabilité")
                
                life_goals = []
                if target_amount > 0:
                    life_goals.append({
                        "name": "Objectif",
                        "amount": target_amount,
                        "year": years,
                    })
                
                fig = plot_wealth_projection(result, life_goals=life_goals)
                st.plotly_chart(fig, use_container_width=True)
                
                # Scénarios What-If
                if what_if_scenarios:
                    display_what_if_comparison(what_if_scenarios, years)
                
                # Distribution des résultats
                display_distribution(result, target_amount)
                
                # Tableau récapitulatif
                display_summary_table(result)
                
            except Exception as e:
                logger.error(f"Erreur simulation: {e}")
                st.error(f"Une erreur est survenue: {e}")


def get_default_monthly_contribution() -> int:
    """
    Récupère le versement mensuel par défaut basé sur le Reste à Vivre (Phase 3).
    
    Returns:
        Montant mensuel suggéré (arrondi)
    """
    try:
        df = get_all_transactions()
        if df.empty:
            return 500  # Valeur par défaut
        
        # Détecter les abonnements
        detector = SubscriptionDetector()
        subscriptions = detector.detect_subscriptions(df)
        
        if not subscriptions:
            return 500
        
        # Calculer les charges fixes mensuelles
        monthly_charges = detector.calculate_monthly_fixed_charges(subscriptions)
        
        # Estimer les revenus moyens mensuels
        income_df = df[df["amount"] > 0]
        if not income_df.empty:
            avg_monthly_income = income_df["amount"].sum() / 12
            # Reste à vivre = 60% des revenus - charges fixes
            suggested_savings = max(0, avg_monthly_income * 0.6 - monthly_charges)
            return int(suggested_savings / 100) * 100  # Arrondir à la centaine
        
        return 500
        
    except Exception as e:
        logger.warning(f"Impossible de calculer le Reste à Vivre: {e}")
        return 500


def create_what_if_scenarios(
    base_capital: float,
    base_contribution: float,
    base_return: float,
    base_volatility: float,
    years: int,
) -> Dict:
    """Crée les variations de scénarios What-If."""
    scenarios = {}
    
    st.markdown("#### Sélectionnez les scénarios à comparer:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.checkbox("📈 Inflation à 4%", help="Impact d'une inflation élevée sur vos versements"):
            scenarios["inflation_4pct"] = {
                "capital": base_capital,
                "contribution": base_contribution,
                "return": base_return,
                "volatility": base_volatility,
                "years": years,
                "inflation": 0.04,
            }
        
        if st.checkbox("💰 +200€/mois", help="Impact d'une épargne accrue"):
            scenarios["plus_200"] = {
                "capital": base_capital,
                "contribution": base_contribution + 200,
                "return": base_return,
                "volatility": base_volatility,
                "years": years,
            }
    
    with col2:
        if st.checkbox("📉 Choc -20%", help="Impact d'une baisse de 20% la première année"):
            scenarios["choc_20pct"] = {
                "capital": base_capital * 0.8,
                "contribution": base_contribution,
                "return": base_return,
                "volatility": base_volatility,
                "years": years,
            }
        
        if st.checkbox("📊 Rendement +2%", help="Impact d'un meilleur rendement"):
            scenarios["return_plus_2"] = {
                "capital": base_capital,
                "contribution": base_contribution,
                "return": min(base_return + 0.02, 0.30),
                "volatility": base_volatility,
                "years": years,
            }
    
    with col3:
        if st.checkbox("🎯 Double épargne", help="Doubler le versement mensuel"):
            scenarios["double_savings"] = {
                "capital": base_capital,
                "contribution": base_contribution * 2,
                "return": base_return,
                "volatility": base_volatility,
                "years": years,
            }
        
        if st.checkbox("⏱️ Durée +5 ans", help="Impact d'une durée plus longue"):
            scenarios["plus_5ans"] = {
                "capital": base_capital,
                "contribution": base_contribution,
                "return": base_return,
                "volatility": base_volatility,
                "years": years + 5,
            }
    
    return scenarios


def display_simulation_results(result, stats, target_amount):
    """Affiche les résultats principaux de la simulation."""
    st.markdown("---")
    st.header("📊 Résultats de la simulation")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Capital médian",
            value=f"€{stats['median']:,.0f}",
            help="Le résultat le plus probable (50% des cas)",
        )
    
    with col2:
        st.metric(
            label="Scénario optimiste (95%)",
            value=f"€{stats['percentile_95']:,.0f}",
            help="5% des cas dépassent cette valeur",
        )
    
    with col3:
        st.metric(
            label="Scénario pessimiste (5%)",
            value=f"€{stats['percentile_5']:,.0f}",
            help="95% des cas sont meilleurs que ceci",
        )
    
    with col4:
        if target_amount > 0:
            final_values = result.get_final_values()
            prob_success = np.mean(final_values >= target_amount)
            
            st.metric(
                label=f"Probabilité d'atteindre l'objectif",
                value=f"{prob_success:.1%}",
                help=f"Chances d'atteindre €{target_amount:,.0f}",
            )


def display_what_if_comparison(scenarios, years):
    """Affiche la comparaison des scénarios What-If."""
    st.markdown("---")
    st.header("🎮 Comparaison des scénarios What-If")
    
    if not scenarios:
        return
    
    # Lancer les simulations pour chaque scénario
    results = []
    names = []
    
    scenario_labels = {
        "inflation_4pct": "Inflation 4%",
        "plus_200": "+200€/mois",
        "choc_20pct": "Choc -20%",
        "return_plus_2": "Rendement +2%",
        "double_savings": "Double épargne",
        "plus_5ans": "+5 ans",
    }
    
    for key, params in scenarios.items():
        sim = MonteCarloSimulator(
            initial_capital=params["capital"],
            monthly_contribution=params["contribution"],
            annual_return=params["return"],
            volatility=params["volatility"],
            years=params["years"],
            annual_inflation=params.get("inflation", 0),
        )
        
        result = sim.run_simulation(n_simulations=5000)
        results.append(result)
        names.append(scenario_labels.get(key, key))
    
    # Graphique comparatif
    fig = plot_scenario_comparison(results, names)
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau récapitulatif
    st.subheader("📋 Tableau comparatif")
    
    comparison_data = []
    for name, res in zip(names, results):
        stats = res.statistics
        comparison_data.append({
            "Scénario": name,
            "Capital médian": f"€{stats['median']:,.0f}",
            "Optimiste (95%)": f"€{stats['percentile_95']:,.0f}",
            "Pessimiste (5%)": f"€{stats['percentile_5']:,.0f}",
        })
    
    st.table(comparison_data)


def display_distribution(result, target_amount):
    """Affiche la distribution des résultats."""
    st.markdown("---")
    st.header("📊 Distribution des résultats")
    
    fig = plot_probability_distribution(result, target_amount if target_amount > 0 else None)
    st.plotly_chart(fig, use_container_width=True)


def display_summary_table(result):
    """Affiche un tableau récapitulatif détaillé."""
    st.markdown("---")
    st.subheader("📋 Résumé détaillé")
    
    stats = result.statistics
    params = result.params
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Paramètres de la simulation**")
        st.markdown(f"""
        - Capital initial: **€{params['initial_capital']:,.0f}**
        - Versement mensuel: **€{params['monthly_contribution']:,.0f}**
        - Rendement annuel: **{params['annual_return']:.1%}**
        - Volatilité: **{params['volatility']:.1%}**
        - Durée: **{params['years']} ans**
        - Nombre de simulations: **{params['n_simulations']:,}**
        """)
    
    with col2:
        st.markdown("**Résultats clés**")
        st.markdown(f"""
        - Capital médian: **€{stats['median']:,.0f}**
        - Capital moyen: **€{stats['mean']:,.0f}**
        - Écart-type: **€{stats['std']:,.0f}**
        - Intervalle 90%: **[€{stats['percentile_5']:,.0f} - €{stats['percentile_95']:,.0f}]**
        - Meilleur cas: **€{stats['max']:,.0f}**
        - Pire cas: **€{stats['min']:,.0f}**
        """)


# Point d'entrée
if __name__ == "__main__":
    render_projections_page()
