import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def render_evolution_chart(df_current: pd.DataFrame):
    """
    Render monthly income/expenses evolution line chart with filled areas.
    Shows surplus (green) and deficit (red) zones.
    
    Args:
        df_current: Current period transactions with date_dt column
    """
    st.subheader("📉 Évolution des Flux")
    
    if df_current.empty:
        st.info("Aucune donnée disponible.")
        return
    
    # Group by month
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
    
    df_plot = pd.DataFrame(monthly_data)
    
    if df_plot.empty:
        st.info("Sélectionnez une période avec des données pour voir l'évolution.")
        return
    
    # Create figure
    fig_evol = go.Figure()
    
    # Calculate min for the fill trick
    min_line = np.minimum(df_plot['Revenus'], df_plot['Dépenses'])
    
    # 1. Base trace for Surplus (Green area between min and Revenus)
    fig_evol.add_trace(go.Scatter(
        x=df_plot['Mois'], y=min_line,
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    fig_evol.add_trace(go.Scatter(
        x=df_plot['Mois'], y=df_plot['Revenus'],
        fill='tonexty',
        fillcolor='rgba(34, 197, 94, 0.3)',
        line=dict(width=0),
        name="Zone de Surplus (Épargne)",
        hoverinfo='skip'
    ))
    
    # 2. Base trace for Deficit (Red area between min and Dépenses)
    fig_evol.add_trace(go.Scatter(
        x=df_plot['Mois'], y=min_line,
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    fig_evol.add_trace(go.Scatter(
        x=df_plot['Mois'], y=df_plot['Dépenses'],
        fill='tonexty',
        fillcolor='rgba(239, 68, 68, 0.3)',
        line=dict(width=0),
        name="Zone de Déficit",
        hoverinfo='skip'
    ))
    
    # 3. Solid lines on top
    fig_evol.add_trace(go.Scatter(
        x=df_plot['Mois'], y=df_plot['Revenus'],
        name="Revenus",
        line=dict(color="#22c55e", width=4, shape='spline'),
        mode='lines+markers'
    ))
    fig_evol.add_trace(go.Scatter(
        x=df_plot['Mois'], y=df_plot['Dépenses'],
        name="Dépenses",
        line=dict(color="#ef4444", width=4, shape='spline'),
        mode='lines+markers'
    ))
    
    # 4. Solde Net (Line)
    df_net = df_plot.copy()
    df_net['Solde'] = df_net['Revenus'] - df_net['Dépenses']
    fig_evol.add_trace(go.Scatter(
        x=df_net['Mois'], y=df_net['Solde'],
        name="Caisse (Net)",
        line=dict(color="white" if not st.get_option("theme.base") == "light" else "black", width=2, dash='dot'),
        mode='lines'
    ))
    
    fig_evol.update_layout(
        xaxis_title="", 
        yaxis_title="Montant (€)", 
        height=450,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    st.plotly_chart(fig_evol, use_container_width=True)

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
