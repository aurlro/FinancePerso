"""
Visualisations - Cônes de Probabilité & Projections Patrimoniales
================================================================

Ce module gère les visualisations interactives des simulations Monte Carlo
avec Plotly, incluant les cônes de probabilité et les scénarios What-If.

Usage:
    from modules.wealth.visualizations import plot_wealth_projection
    from modules.wealth.math_engine import MonteCarloSimulator
    
    simulator = MonteCarloSimulator(...)
    result = simulator.run_simulation()
    
    fig = plot_wealth_projection(result)
    fig.show()
"""

import numpy as np
import plotly.graph_objects as go
from typing import Optional, List, Dict

from modules.wealth.math_engine import SimulationResult


def plot_wealth_projection(
    result: SimulationResult,
    life_goals: Optional[List[Dict]] = None,
    title: str = "Projection Patrimoniale (Simulation Monte Carlo)",
    height: int = 600,
    show_confidence_bands: bool = True,
) -> go.Figure:
    """
    Crée un graphique de cône de probabilité avec Plotly.
    
    Args:
        result: Résultat de la simulation Monte Carlo
        life_goals: Liste des objectifs de vie [{"name": "Achat", "amount": 150000, "year": 5}]
        title: Titre du graphique
        height: Hauteur du graphique (pixels)
        show_confidence_bands: Afficher les bandes de confiance
        
    Returns:
        Figure Plotly interactive
    """
    fig = go.Figure()
    
    time_points = result.time_points
    
    # Calcul des percentiles
    p5 = result.get_percentile(5)
    p25 = result.get_percentile(25)
    p50 = result.get_percentile(50)
    p75 = result.get_percentile(75)
    p95 = result.get_percentile(95)
    
    # Zone de confiance 90% (5% - 95%)
    if show_confidence_bands:
        fig.add_trace(go.Scatter(
            x=np.concatenate([time_points, time_points[::-1]]),
            y=np.concatenate([p5, p95[::-1]]),
            fill='toself',
            fillcolor='rgba(255, 165, 0, 0.15)',
            line=dict(color='rgba(255, 165, 0, 0)'),
            name='Zone Catastrophe → Optimiste (5%-95%)',
            hoverinfo='skip',
            showlegend=True,
        ))
    
    # Zone interquartile (25% - 75%)
    fig.add_trace(go.Scatter(
        x=np.concatenate([time_points, time_points[::-1]]),
        y=np.concatenate([p25, p75[::-1]]),
        fill='toself',
        fillcolor='rgba(0, 128, 255, 0.2)',
        line=dict(color='rgba(0, 128, 255, 0)'),
        name='Zone probable (25%-75%)',
        hoverinfo='skip',
        showlegend=True,
    ))
    
    # Trajectoire médiane (50%)
    fig.add_trace(go.Scatter(
        x=time_points,
        y=p50,
        mode='lines',
        name='Scénario Médian (50%)',
        line=dict(color='#0066CC', width=3),
        hovertemplate=(
            "<b>Année %{x:.1f}</b><br>"
            "Capital projeté: <b>%{y:,.0f} €</b><br>"
            "<i>Le scénario le plus probable</i>"
            "<extra></extra>"
        ),
    ))
    
    # Percentile 95% (scénario optimiste)
    fig.add_trace(go.Scatter(
        x=time_points,
        y=p95,
        mode='lines',
        name='Scénario Optimiste (95%)',
        line=dict(color='rgba(0, 200, 0, 0.6)', width=2, dash='dash'),
        hovertemplate=(
            "<b>Année %{x:.1f}</b><br>"
            "Scénario optimiste: <b>%{y:,.0f} €</b><br>"
            "<i>5% des cas dépassent cette valeur</i>"
            "<extra></extra>"
        ),
    ))
    
    # Percentile 5% (scénario catastrophe)
    fig.add_trace(go.Scatter(
        x=time_points,
        y=p5,
        mode='lines',
        name='Scénario Catastrophe (5%)',
        line=dict(color='rgba(255, 80, 80, 0.6)', width=2, dash='dash'),
        hovertemplate=(
            "<b>Année %{x:.1f}</b><br>"
            "Scénario défavorable: <b>%{y:,.0f} €</b><br>"
            "<i>95% des cas sont meilleurs que ceci</i>"
            "<extra></extra>"
        ),
    ))
    
    # Quelques trajectoires individuelles
    n_sample = min(50, result.simulations.shape[0])
    sample_indices = np.random.choice(result.simulations.shape[0], n_sample, replace=False)
    
    for i, idx in enumerate(sample_indices[:5]):
        trajectory = result.get_trajectory(idx)
        fig.add_trace(go.Scatter(
            x=time_points,
            y=trajectory,
            mode='lines',
            line=dict(color='rgba(128, 128, 128, 0.15)', width=1),
            name='Trajectoires simulées' if i == 0 else None,
            showlegend=(i == 0),
            hoverinfo='skip',
        ))
    
    # Objectifs de vie
    if life_goals:
        for goal in life_goals:
            goal_year = goal.get('year', 0)
            goal_amount = goal.get('amount', 0)
            goal_name = goal.get('name', 'Objectif')
            
            if goal_year <= result.time_points[-1]:
                # Ligne verticale pour l'objectif
                fig.add_vline(
                    x=goal_year,
                    line=dict(color='purple', width=2, dash='dot'),
                    annotation_text=goal_name,
                    annotation_position='top',
                )
                
                # Point d'intersection
                idx = int(goal_year * 12)
                if idx < len(p50):
                    prob_success = np.mean(result.simulations[:, idx] >= goal_amount)
                    
                    fig.add_trace(go.Scatter(
                        x=[goal_year],
                        y=[goal_amount],
                        mode='markers',
                        marker=dict(size=12, color='purple', symbol='star'),
                        name=f"{goal_name} ({prob_success:.0%} de chances)",
                        hovertemplate=(
                            f"<b>{goal_name}</b><br>"
                            f"Montant: {goal_amount:,.0f} €<br>"
                            f"Année: {goal_year}<br>"
                            f"Probabilité de réussite: <b>{prob_success:.1%}</b><br>"
                            f"<i>En se basant sur le scénario médian</i>"
                            "<extra></extra>"
                        ),
                    ))
    
    # Mise en page
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=20),
            x=0.5,
            xanchor='center',
        ),
        xaxis_title='Années',
        yaxis_title='Capital (€)',
        height=height,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.25,
            xanchor='center',
            x=0.5,
            font=dict(size=11),
        ),
        margin=dict(l=60, r=40, t=80, b=100),
    )
    
    # Format de l'axe Y en euros
    fig.update_yaxes(
        tickformat=',.0f',
        tickprefix='€',
        gridcolor='rgba(0,0,0,0.1)',
    )
    
    fig.update_xaxes(
        gridcolor='rgba(0,0,0,0.1)',
        dtick=1,
    )
    
    # Annotation résumé
    final_median = p50[-1]
    final_p5 = p5[-1]
    final_p95 = p95[-1]
    
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref='paper',
        yref='paper',
        text=(
            f"<b>Projection à {int(result.time_points[-1])} ans</b><br>"
            f"Capital médian: <b>€{final_median:,.0f}</b><br>"
            f"Intervalle 90%: [€{final_p5:,.0f} - €{final_p95:,.0f}]<br>"
            f"<i>Sur {result.params['n_simulations']:,} simulations</i>"
        ),
        showarrow=False,
        font=dict(size=11),
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor='rgba(0,0,0,0.2)',
        borderwidth=1,
        borderpad=8,
        align='left',
    )
    
    return fig


def plot_scenario_comparison(
    results: List[SimulationResult],
    scenario_names: List[str],
    title: str = "Comparaison des Scénarios",
    height: int = 500,
) -> go.Figure:
    """Compare plusieurs scénarios sur un même graphique."""
    fig = go.Figure()
    
    colors = ['#0066CC', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    for i, (result, name) in enumerate(zip(results, scenario_names)):
        color = colors[i % len(colors)]
        time_points = result.time_points
        p50 = result.get_percentile(50)
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=p50,
            mode='lines',
            name=f"{name} (Médian)",
            line=dict(color=color, width=3),
            hovertemplate=(
                f"<b>{name}</b><br>"
                "Année: %{x:.1f}<br>"
                "Capital: <b>%{y:,.0f} €</b><br>"
                "<extra></extra>"
            ),
        ))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18),
            x=0.5,
            xanchor='center',
        ),
        xaxis_title='Années',
        yaxis_title='Capital (€)',
        height=height,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5,
        ),
    )
    
    fig.update_yaxes(tickformat=',.0f', tickprefix='€')
    
    return fig


def plot_probability_distribution(
    result: SimulationResult,
    target: Optional[float] = None,
    title: str = "Distribution des Capitaux Finals",
) -> go.Figure:
    """Affiche la distribution des valeurs finales (histogramme)."""
    final_values = result.get_final_values()
    
    prob_success = None
    if target:
        prob_success = np.mean(final_values >= target)
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=final_values,
        nbinsx=50,
        name='Distribution',
        marker_color='rgba(0, 102, 204, 0.6)',
        hovertemplate='Capital: %{x:,.0f} €<br>Fréquence: %{y}<extra></extra>',
    ))
    
    median = np.median(final_values)
    fig.add_vline(
        x=median,
        line=dict(color='red', width=2, dash='dash'),
        annotation_text=f'Médiane: €{median:,.0f}',
    )
    
    if target and prob_success is not None:
        fig.add_vline(
            x=target,
            line=dict(color='green', width=2),
            annotation_text=f'Objectif: €{target:,.0f} ({prob_success:.1%})',
        )
    
    fig.update_layout(
        title=title,
        xaxis_title='Capital final (€)',
        yaxis_title='Nombre de simulations',
        template='plotly_white',
        showlegend=False,
    )
    
    fig.update_xaxes(tickformat=',.0f')
    
    return fig
