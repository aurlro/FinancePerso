# AGENT-006: Analytics & Dashboard Engineer

## 🎯 Mission

Architecte des analytics et dashboards de FinancePerso. Responsable des visualisations, indicateurs financiers, analyses de tendances et reporting. Garant de la clarté et de l'actionnabilité des données présentées.

---

## 📚 Contexte: Architecture Analytics

### Philosophie
> "Un bon dashboard ne montre pas des données, il raconte une histoire et suggère des actions."

### Types d'Analytics

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ANALYTICS LAYERS                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  DESCRIPTIVE          DIAGNOSTIC          PREDICTIVE               │
│  (What happened)      (Why happened)      (What will happen)       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │ KPI Cards    │    │ Drill-down   │    │ Budget       │         │
│  │ Monthly      │    │ Comparisons  │    │ alerts       │         │
│  │ summaries    │    │ Anomalies    │    │ Trends       │         │
│  └──────────────┘    └──────────────┘    └──────────────┘         │
│                                                                      │
│  PRESCRIPTIVE                                                       │
│  (What to do)                                                      │
│  ┌──────────────┐                                                  │
│  │ Smart        │                                                  │
│  │ suggestions  │                                                  │
│  │ Actions      │                                                  │
│  └──────────────┘                                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Module 1: KPIs & Metriques Financieres

### KPI Cards

```python
class FinancialKPIs:
    """Indicateurs financiers cles."""
    
    @staticmethod
    def get_monthly_summary(month: str = None) -> dict:
        """
        Resume mensuel complet.
        
        Returns:
            {
                'period': '2026-02',
                'total_income': 5000.00,
                'total_expenses': -3200.00,
                'balance': 1800.00,
                'savings_rate': 0.36,
                'transaction_count': 45,
                'top_category': 'Alimentation',
                'vs_last_month': {
                    'income_change': +200.00,
                    'expense_change': -150.00,
                    'savings_change': +0.05
                }
            }
        """
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        
        df = get_transactions_by_month(month)
        
        income = df[df['amount'] > 0]['amount'].sum()
        expenses = df[df['amount'] < 0]['amount'].sum()
        balance = income + expenses
        
        savings_rate = balance / income if income > 0 else 0
        
        # Top categorie
        by_category = df[df['amount'] < 0].groupby('category_validated')['amount'].sum()
        top_category = by_category.idxmin() if not by_category.empty else None
        
        # Comparaison mois precedent
        prev_month = get_previous_month(month)
        prev_df = get_transactions_by_month(prev_month)
        prev_income = prev_df[prev_df['amount'] > 0]['amount'].sum()
        prev_expenses = prev_df[prev_df['amount'] < 0]['amount'].sum()
        
        return {
            'period': month,
            'total_income': round(income, 2),
            'total_expenses': round(expenses, 2),
            'balance': round(balance, 2),
            'savings_rate': round(savings_rate, 2),
            'transaction_count': len(df),
            'top_category': top_category,
            'vs_last_month': {
                'income_change': round(income - prev_income, 2),
                'expense_change': round(expenses - prev_expenses, 2),
                'savings_change': round(savings_rate - (prev_income + prev_expenses) / prev_income if prev_income > 0 else 0, 2)
            }
        }
    
    @staticmethod
    def get_ytd_summary(year: int = None) -> dict:
        """Resume year-to-date."""
        if year is None:
            year = datetime.now().year
        
        df = get_transactions_by_year(year)
        
        return {
            'year': year,
            'total_income': df[df['amount'] > 0]['amount'].sum(),
            'total_expenses': df[df['amount'] < 0]['amount'].sum(),
            'avg_monthly_income': df[df['amount'] > 0].groupby(df['date'].dt.month)['amount'].sum().mean(),
            'avg_monthly_expenses': df[df['amount'] < 0].groupby(df['date'].dt.month)['amount'].sum().mean()
        }
```

---

## 📈 Module 2: Visualisations

### Chart Types

```python
class ChartBuilder:
    """Constructeur de graphiques Plotly."""
    
    @staticmethod
    def evolution_chart(df: pd.DataFrame, freq: str = 'M') -> go.Figure:
        """
        Graphique d'evolution temporelle.
        
        Args:
            df: DataFrame avec date et amount
            freq: 'D' daily, 'W' weekly, 'M' monthly
        """
        df['date'] = pd.to_datetime(df['date'])
        
        # Resampler
        if freq == 'M':
            grouped = df.groupby([df['date'].dt.to_period('M')])['amount'].sum()
        elif freq == 'W':
            grouped = df.groupby([df['date'].dt.isocalendar().week])['amount'].sum()
        else:
            grouped = df.groupby('date')['amount'].sum()
        
        fig = go.Figure()
        
        # Revenus
        fig.add_trace(go.Scatter(
            x=grouped.index,
            y=grouped[grouped > 0],
            name='Revenus',
            line=dict(color='#2ecc71'),
            fill='tozeroy'
        ))
        
        # Depenses
        fig.add_trace(go.Scatter(
            x=grouped.index,
            y=grouped[grouped < 0],
            name='Depenses',
            line=dict(color='#e74c3c'),
            fill='tozeroy'
        ))
        
        fig.update_layout(
            title='Evolution des finances',
            xaxis_title='Periode',
            yaxis_title='Montant (EUR)',
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def category_pie_chart(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
        """Camembert des depenses par categorie."""
        expenses = df[df['amount'] < 0].groupby('category_validated')['amount'].sum().abs()
        expenses = expenses.nlargest(top_n)
        
        fig = go.Figure(data=[go.Pie(
            labels=expenses.index,
            values=expenses.values,
            hole=0.4,
            textinfo='label+percent',
            hovertemplate='%{label}<br>%{value:.2f} EUR<br>%{percent}'
        )])
        
        fig.update_layout(title=f'Top {top_n} Categories de depenses')
        return fig
    
    @staticmethod
    def heatmap_calendar(df: pd.DataFrame, year: int, month: int) -> go.Figure:
        """Calendrier de depenses."""
        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date'].dt.year == year) & (df['date'].dt.month == month)]
        
        daily = df.groupby('date')['amount'].sum()
        
        # Creer matrice 7xN (semaines)
        # Implementation...
        
        fig = go.Figure(data=go.Heatmap(
            z=[[daily.get(datetime(year, month, d), 0) for d in range(1, 32)]],
            colorscale='RdYlGn',
            hoverongaps=False
        ))
        
        return fig
```

---

## 🎯 Module 3: Smart Insights

### Detection de Patterns

```python
class SmartInsights:
    """Insights automatiques sur les donnees."""
    
    @staticmethod
    def detect_anomalies(df: pd.DataFrame) -> list[dict]:
        """
        Detecte les transactions anormales.
        
        Criteres:
        - Montant > 3x ecart-type categorie
        - Premiere occurrence fournisseur avec montant eleve
        - Transaction hors heures habituelles
        """
        anomalies = []
        
        for category in df['category_validated'].unique():
            cat_df = df[df['category_validated'] == category]
            
            mean = cat_df['amount'].mean()
            std = cat_df['amount'].std()
            
            # Transactions > 3 sigma
            outliers = cat_df[abs(cat_df['amount'] - mean) > 3 * std]
            
            for _, row in outliers.iterrows():
                anomalies.append({
                    'type': 'amount_outlier',
                    'transaction_id': row['id'],
                    'category': category,
                    'amount': row['amount'],
                    'expected_range': (mean - 2*std, mean + 2*std),
                    'severity': 'high' if abs(row['amount']) > 1000 else 'medium'
                })
        
        return anomalies
    
    @staticmethod
    def spending_trends(df: pd.DataFrame) -> list[dict]:
        """Analyse les tendances de depenses."""
        trends = []
        
        # Comparer ce mois vs moyenne 3 derniers mois
        current_month = df[df['date'] >= (datetime.now() - timedelta(days=30))]
        prev_3months = df[
            (df['date'] >= (datetime.now() - timedelta(days=120))) &
            (df['date'] < (datetime.now() - timedelta(days=30)))
        ]
        
        for category in df['category_validated'].unique():
            current = current_month[current_month['category_validated'] == category]['amount'].sum()
            previous = prev_3months[prev_3months['category_validated'] == category]['amount'].sum() / 3
            
            if previous != 0:
                change_pct = (current - previous) / abs(previous)
                
                if abs(change_pct) > 0.3:  # 30% changement
                    trends.append({
                        'category': category,
                        'change_pct': change_pct,
                        'direction': 'increase' if change_pct > 0 else 'decrease',
                        'current_amount': current,
                        'avg_previous': previous,
                        'message': f"{'Augmentation' if change_pct > 0 else 'Reduction'} de {abs(change_pct):.0%} sur {category}"
                    })
        
        return trends
    
    @staticmethod
    def budget_alerts(budgets: dict, actuals: dict) -> list[dict]:
        """Alertes budget."""
        alerts = []
        
        for category, budget in budgets.items():
            actual = actuals.get(category, 0)
            usage = abs(actual) / budget if budget > 0 else 0
            
            if usage >= 1.0:
                alerts.append({
                    'category': category,
                    'type': 'over_budget',
                    'severity': 'critical',
                    'message': f"Budget {category} depasse: {usage:.0%} utilise"
                })
            elif usage >= 0.8:
                alerts.append({
                    'category': category,
                    'type': 'approaching_limit',
                    'severity': 'warning',
                    'message': f"Budget {category} a {usage:.0%}: attention"
                })
        
        return alerts
```

---

## 🎛️ Module 4: Dashboard System

### Dashboard Personnalisable

```python
"""
Systeme de dashboard avec widgets configurables.
"""

# Table: dashboard_layouts
# layout_json format:
{
    "widgets": [
        {
            "id": "kpi_1",
            "type": "kpi_balance",
            "position": {"x": 0, "y": 0, "w": 3, "h": 2},
            "config": {"period": "current_month"}
        },
        {
            "id": "chart_1", 
            "type": "evolution_line",
            "position": {"x": 3, "y": 0, "w": 9, "h": 4},
            "config": {"months": 6}
        }
    ]
}

WIDGET_REGISTRY = {
    'kpi_balance': KpiBalanceWidget,
    'kpi_savings': KpiSavingsWidget,
    'evolution_line': EvolutionChartWidget,
    'category_pie': CategoryPieWidget,
    'recent_transactions': RecentTransactionsWidget,
    'budget_status': BudgetStatusWidget,
    'alerts': AlertsWidget
}

class DashboardRenderer:
    """Rendu du dashboard."""
    
    def render(self, layout_id: str = 'default'):
        """Rend le dashboard complet."""
        layout = get_layout(layout_id)
        
        # Grille CSS Grid
        st.markdown("""
        <style>
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        for widget_config in layout:
            widget_class = WIDGET_REGISTRY[widget_config['type']]
            widget = widget_class(widget_config)
            
            col = st.columns([widget_config['position']['w']])[0]
            with col:
                widget.render()
```

---

## 🔧 Responsabilites

### Quand consulter cet agent

- Nouveau KPI ou metrique
- Nouveau type de graphique
- Modification du dashboard
- Analyses de tendances
- Alertes budget/finance
- Export de rapports

---

**Version**: 1.0
**Date**: 2026-02-25
**Statut**: PRET A L'EMPLOI

---

## 🔧 Module Additionnel: Caching & Exports

### Caching des Resultats

```python
"""
Caching intelligent des calculs analytics.
"""

import hashlib
from functools import wraps

class AnalyticsCache:
    """Cache pour resultats analytics."""
    
    @staticmethod
    def cache_key(prefix: str, **kwargs) -> str:
        """Genere une cle de cache."""
        data = json.dumps(kwargs, sort_keys=True, default=str)
        return f"{prefix}:{hashlib.md5(data.encode()).hexdigest()[:12]}"
    
    @classmethod
    def get_or_compute(
        cls,
        key: str,
        compute_func: Callable,
        ttl: int = 3600
    ):
        """
        Recupere du cache ou calcule.
        
        Args:
            key: Cle de cache
            compute_func: Fonction de calcul
            ttl: Time-to-live en secondes
        """
        # Essayer cache
        cached = st.cache_data.get(key)
        if cached is not None:
            return cached
        
        # Calculer
        result = compute_func()
        
        # Stocker
        st.cache_data.set(key, result, ttl=ttl)
        
        return result

# Decorateur
def cached_analytics(ttl: int = 3600):
    """Decorateur de cache pour fonctions analytics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generer cle
            key = AnalyticsCache.cache_key(
                func.__name__,
                args=args,
                kwargs=kwargs
            )
            
            return AnalyticsCache.get_or_compute(
                key,
                lambda: func(*args, **kwargs),
                ttl
            )
        return wrapper
    return decorator

# Usage
@cached_analytics(ttl=1800)  # 30 minutes
def get_monthly_summary_cached(month: str) -> dict:
    """Version cachee du resume mensuel."""
    return FinancialKPIs.get_monthly_summary(month)
```

### Export de Rapports

```python
"""
Export des rapports dans differents formats.
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from fpdf import FPDF
import base64

class ReportExporter:
    """Exporteur de rapports."""
    
    @staticmethod
    def to_excel(df: pd.DataFrame, title: str = "Rapport") -> bytes:
        """
        Exporte vers Excel avec mise en forme.
        
        Returns:
            Contenu fichier Excel (bytes)
        """
        wb = Workbook()
        ws = wb.active
        ws.title = title
        
        # Header
        headers = list(df.columns)
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # Data
        for row_idx, row in enumerate(df.itertuples(index=False), 2):
            for col_idx, value in enumerate(row, 1):
                ws.cell(row=row_idx, column=col_idx, value=value)
        
        # Auto-width
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Sauvegarder en bytes
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output.getvalue()
    
    @staticmethod
    def to_pdf(summary: dict, charts: list, title: str = "Rapport Financier") -> bytes:
        """
        Exporte vers PDF.
        
        Returns:
            Contenu fichier PDF (bytes)
        """
        class FinancePDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, title, 0, 1, 'C')
                self.ln(10)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
        pdf = FinancePDF()
        pdf.add_page()
        
        # Section KPIs
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Indicateurs Cles', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        for key, value in summary.items():
            pdf.cell(0, 8, f'{key}: {value}', 0, 1)
        
        pdf.ln(10)
        
        # Sauvegarder
        from io import BytesIO
        output = BytesIO()
        pdf.output(output)
        output.seek(0)
        
        return output.getvalue()
    
    @staticmethod
    def to_csv(df: pd.DataFrame) -> str:
        """Exporte vers CSV."""
        return df.to_csv(index=False, encoding='utf-8-sig')
    
    @staticmethod
    def download_button(data: bytes, filename: str, mime: str):
        """Cree un bouton de telechargement Streamlit."""
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:{mime};base64,{b64}" download="{filename}">Telecharger {filename}</a>'
        return st.markdown(href, unsafe_allow_html=True)

# Usage dans UI
def render_export_buttons(df: pd.DataFrame, month: str):
    """Affiche boutons d'export."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        excel_data = ReportExporter.to_excel(df, f"Transactions_{month}")
        ReportExporter.download_button(
            excel_data,
            f"transactions_{month}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        csv_data = ReportExporter.to_csv(df).encode()
        ReportExporter.download_button(
            csv_data,
            f"transactions_{month}.csv",
            "text/csv"
        )
```

### Drill-Down Navigation

```python
"""
Navigation drill-down dans les donnees.
"""

class DrillDownNavigator:
    """Navigateur drill-down pour exploration."""
    
    def __init__(self):
        self.path = []
    
    def drill_down(
        self,
        df: pd.DataFrame,
        dimension: str,
        value: any
    ) -> pd.DataFrame:
        """
        Descend d'un niveau dans les donnees.
        
        Args:
            df: DataFrame actuel
            dimension: Colonne de filtrage
            value: Valeur a filtrer
            
        Returns:
            DataFrame filtre
        """
        filtered = df[df[dimension] == value]
        self.path.append({'dimension': dimension, 'value': value})
        
        return filtered
    
    def drill_up(self, levels: int = 1) -> pd.DataFrame:
        """
        Remonte d'un ou plusieurs niveaux.
        
        Returns:
            DataFrame au niveau superieur
        """
        for _ in range(levels):
            if self.path:
                self.path.pop()
        
        # Reconstruire le filtre
        df = get_all_transactions()
        for step in self.path:
            df = df[df[step['dimension']] == step['value']]
        
        return df
    
    def get_breadcrumb(self) -> list[dict]:
        """Retourne le fil d'Ariane."""
        return self.path
    
    def render_breadcrumb_ui(self):
        """Affiche le fil d'Ariane dans Streamlit."""
        if not self.path:
            return
        
        cols = st.columns(len(self.path) + 1)
        
        with cols[0]:
            if st.button("🏠 Accueil"):
                self.path = []
                st.rerun()
        
        for i, step in enumerate(self.path):
            with cols[i + 1]:
                st.write(f" > {step['dimension']}: {step['value']}")

# Usage
def render_dashboard_with_drilldown():
    """Dashboard avec capacite drill-down."""
    navigator = DrillDownNavigator()
    
    # Afficher fil d'Ariane
    navigator.render_breadcrumb_ui()
    
    # Donnees actuelles
    df = get_all_transactions()
    
    # Si on a un chemin, appliquer filtres
    for step in navigator.get_breadcrumb():
        df = df[df[step['dimension']] == step['value']]
    
    # Afficher graphique avec click handler
    selected_category = st.selectbox("Categorie", df['category_validated'].unique())
    
    if st.button("Drill Down"):
        df = navigator.drill_down(df, 'category_validated', selected_category)
        st.rerun()
```

---

**Version**: 1.1 - **COMPLETED**
**Ajouts**: Caching, Export Excel/PDF/CSV, Drill-down navigation
