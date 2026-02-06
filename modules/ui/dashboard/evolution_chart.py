"""
Module de graphiques d'évolution avec caching.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np


@st.cache_data(ttl=300)
def _compute_monthly_evolution(df_current: pd.DataFrame) -> pd.DataFrame:
    """Cache les calculs mensuels pour l'évolution."""
    if df_current.empty:
        return pd.DataFrame()
    
    df_evol = df_current.copy()
    df_evol['Mois'] = df_evol['date_dt'].dt.strftime('%Y-%m')
    
    # Complete the date range to avoid gaps
    all_months = pd.date_range(
        start=df_evol['date_dt'].min(),
        end=df_evol['date_dt'].max(),
        freq='MS'
    ).strftime('%Y-%m').tolist()
    
    monthly_data = []
    for m in all_months:
        g = df_evol[df_evol['Mois'] == m]
        inc = g[g['amount'] > 0]['amount'].sum()
        exp = abs(g[g['amount'] < 0]['amount'].sum())
        monthly_data.append({"Mois": m, "Revenus": inc, "Dépenses": exp})
    
    return pd.DataFrame(monthly_data)


def render_evolution_chart(df_current: pd.DataFrame):
    """
    Render monthly income/expenses evolution as grouped bar chart.
    Simplified version: bars for income/expenses + line for net balance.
    
    Args:
        df_current: Current period transactions with date_dt column
    """
    st.subheader("📉 Évolution des Flux")
    
    df_plot = _compute_monthly_evolution(df_current)
    
    if df_plot.empty:
        st.info("Aucune donnée disponible.")
        return
    
    # Calculate net balance
    df_plot['Solde'] = df_plot['Revenus'] - df_plot['Dépenses']
    
    # Create figure with grouped bars
    fig = go.Figure()
    
    # Income bars (green)
    fig.add_trace(go.Bar(
        x=df_plot['Mois'],
        y=df_plot['Revenus'],
        name="Revenus",
        marker_color='#22c55e',
        text=df_plot['Revenus'].apply(lambda x: f"{x:,.0f}€"),
        textposition='outside'
    ))
    
    # Expense bars (red)
    fig.add_trace(go.Bar(
        x=df_plot['Mois'],
        y=df_plot['Dépenses'],
        name="Dépenses",
        marker_color='#ef4444',
        text=df_plot['Dépenses'].apply(lambda x: f"{x:,.0f}€"),
        textposition='outside'
    ))
    
    # Net balance line
    fig.add_trace(go.Scatter(
        x=df_plot['Mois'],
        y=df_plot['Solde'],
        name="Solde Net",
        line=dict(color='#3b82f6', width=3),
        mode='lines+markers',
        marker=dict(size=8)
    ))
    
    # Layout
    fig.update_layout(
        barmode='group',
        xaxis_title="",
        yaxis_title="Montant (€)",
        height=400,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_savings_trend_chart():
    """
    Render 12-month savings trend chart with cashflow bars and rate line.
    """
    st.subheader("📈 Tendance d'Épargne (12 derniers mois)")
    
    from modules.analytics import get_monthly_savings_trend
    df_trend = get_monthly_savings_trend(months=12)
    
    if df_trend.empty:
        st.info("Pas assez de données historiques pour la tendance d'épargne.")
        return
    
    # Create combo chart: Bars for Cashflow, Line for Savings Rate
    fig_trend = go.Figure()
    
    # Bars for Savings Amount (Absolute)
    fig_trend.add_trace(go.Bar(
        x=df_trend['month'], 
        y=df_trend['Epargne'],
        name="Epargne (€)",
        marker_color=df_trend['Epargne'].apply(lambda x: '#22c55e' if x >= 0 else '#ef4444')
    ))
    
    # Line for Rate (%)
    fig_trend.add_trace(go.Scatter(
        x=df_trend['month'], 
        y=df_trend['Taux'],
        name="Taux (%)",
        yaxis="y2",
        line=dict(color="#3b82f6", width=3),
        mode='lines+markers'
    ))
    
    fig_trend.update_layout(
        xaxis_title="",
        yaxis=dict(title="Montant (€)", showgrid=False),
        yaxis2=dict(title="Taux (%)", overlaying="y", side="right", range=[-20, 80], showgrid=True),
        height=400,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
