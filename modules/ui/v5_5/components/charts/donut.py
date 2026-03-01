"""Graphique Donut - Répartition des dépenses.

Usage:
    from modules.ui.v5_5.components.charts import DonutChart
    
    DonutChart.render_expenses(df_month)
"""

from typing import Optional
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


class DonutChart:
    """Graphique donut pour répartition des dépenses."""
    
    # Couleurs par catégorie (cohérent avec le design system)
    CATEGORY_COLORS = {
        "Alimentation": "#10B981",  # Emerald
        "Courses": "#059669",
        "Transport": "#3B82F6",  # Blue
        "Logement": "#6366F1",  # Indigo
        "Santé": "#EF4444",  # Red
        "Loisirs": "#F59E0B",  # Amber
        "Shopping": "#EC4899",  # Pink
        "Vêtements": "#8B5CF6",  # Violet
        "Restaurants": "#F97316",  # Orange
        "Salaire": "#10B981",
        "Revenus": "#22C55E",
        "Investissements": "#14B8A6",
        "Épargne": "#06B6D4",
        "Factures": "#64748B",
        "Abonnements": "#94A3B8",
        "Voyage": "#0EA5E9",
        "Éducation": "#8B5CF6",
        "Cadeaux": "#F43F5E",
        "Virement Interne": "#6B7280",
        "Hors Budget": "#9CA3AF",
        "Inconnu": "#D1D5DB",
        "Autre": "#9CA3AF",
    }
    
    DEFAULT_COLORS = ["#10B981", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6", "#6B7280"]
    
    @staticmethod
    def render_expenses(
        df: pd.DataFrame,
        month_str: Optional[str] = None,
        top_n: int = 5,
        height: int = 350,
    ) -> None:
        """Affiche le graphique de répartition des dépenses.
        
        Args:
            df: DataFrame avec colonnes [amount, category_validated]
            month_str: Mois affiché dans le titre
            top_n: Nombre de catégories à afficher
            height: Hauteur du graphique
        """
        title = f"📊 Répartition des dépenses"
        if month_str:
            title += f" - {month_str}"
        
        st.markdown(f"#### {title}")
        
        try:
            if df.empty:
                st.info("Aucune donnée à afficher")
                return
            
            # Filtrer dépenses uniquement
            expenses = df[df['amount'] < 0].copy()
            if expenses.empty:
                st.info("Aucune dépense ce mois-ci")
                return
            
            # Grouper par catégorie
            by_category = expenses.groupby('category_validated')['amount'].sum().abs().sort_values(ascending=False)
            
            if len(by_category) == 0:
                st.info("Aucune donnée à afficher")
                return
            
            # Top N + autres
            if len(by_category) > top_n:
                top = by_category.head(top_n)
                others = by_category[top_n:].sum()
                by_category = pd.concat([top, pd.Series({'Autres': others})])
            
            # Attribution des couleurs
            colors = []
            for cat in by_category.index:
                color = DonutChart.CATEGORY_COLORS.get(cat, "#6B7280")
                colors.append(color)
            
            # Créer le graphique
            fig = go.Figure(data=[go.Pie(
                labels=by_category.index,
                values=by_category.values,
                hole=0.55,
                marker_colors=colors,
                textinfo='label+percent',
                textposition='outside',
                textfont_size=12,
                textfont_family='Inter, sans-serif',
                pull=[0.02 if i == 0 else 0 for i in range(len(by_category))],  # Séparer légèrement le plus grand
                hovertemplate='<b>%{label}</b><br>%{value:,.2f} €<br>%{percent}<extra></extra>',
            )])
            
            # Total au centre
            total = by_category.sum()
            
            fig.update_layout(
                showlegend=False,
                margin=dict(t=30, b=30, l=30, r=30),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=height,
                annotations=[
                    dict(
                        text=f'<b>{total:,.0f} €</b><br>Total',
                        x=0.5, y=0.5,
                        font_size=14,
                        font_family='Inter, sans-serif',
                        font_color='#374151',
                        showarrow=False
                    )
                ],
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"donut_{month_str or 'default'}")
            
        except Exception as e:
            st.error(f"Erreur lors du chargement du graphique: {str(e)}")
    
    @staticmethod
    def render_income_expenses(
        income: float,
        expenses: float,
        height: int = 300,
    ) -> None:
        """Affiche un donut revenus vs dépenses.
        
        Args:
            income: Montant des revenus
            expenses: Montant des dépenses (valeur positive)
            height: Hauteur du graphique
        """
        labels = ['Revenus', 'Dépenses']
        values = [income, expenses]
        colors = ['#10B981', '#EF4444']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker_colors=colors,
            textinfo='label+value',
            textposition='outside',
            textfont_size=12,
            texttemplate='%{label}<br>%{value:,.0f} €',
            hovertemplate='<b>%{label}</b><br>%{value:,.2f} €<br>%{percent}<extra></extra>',
        )])
        
        # Calcul du reste
        remaining = income - expenses
        remaining_pct = (remaining / income * 100) if income > 0 else 0
        
        fig.update_layout(
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=height,
            annotations=[
                dict(
                    text=f'<b>{remaining:,.0f} €</b><br>Reste<br>({remaining_pct:.0f}%)',
                    x=0.5, y=0.5,
                    font_size=13,
                    font_family='Inter, sans-serif',
                    font_color='#10B981' if remaining >= 0 else '#EF4444',
                    showarrow=False
                )
            ],
        )
        
        st.plotly_chart(fig, use_container_width=True, key="donut_income_expenses")
