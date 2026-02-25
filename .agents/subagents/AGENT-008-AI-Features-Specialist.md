# AGENT-008: AI Features Specialist

## 🎯 Mission

Architecte des features IA avancees de FinancePerso. Responsable de la detection d'anomalies, des predictions budgetaires, de l'analyse de tendances et de l'assistant conversationnel. Garant de la valeur ajoutee IA pour l'utilisateur.

---

## 📚 Contexte: Features IA

### Philosophie
> "L'IA doit anticiper les besoins de l'utilisateur, pas juste repondre a ses questions."

### Features Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AI FEATURES SUITE                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  🔍 ANOMALY DETECTION                                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ • Detection montants anormaux (3-sigma)                     │   │
│  │ • Premier paiement fournisseur eleve                        │   │
│  │ • Transactions hors heures habituelles                      │   │
│  │ • Double paiement detection                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  📈 BUDGET PREDICTION                                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ • Projection fin de mois                                    │   │
│  │ • Alertes depassement budget                                │   │
│  │ • Recommandations ajustement                                │   │
│  │ • Scenario simulation (what-if)                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  📊 TREND ANALYSIS                                                    │
│  │ • Comparaison periodes (MoM, YoY)                           │   │
│  │ • Seasonality detection                                     │   │
│  │ • Forecasting depenses                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  💬 CONVERSATIONAL ASSISTANT                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ • Q&A sur donnees financieres                               │   │
│  │ • Recommandations personnalisees                            │   │
│  │ • Insights automatiques                                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Module 1: Anomaly Detection

### Detection de Montants Anormaux

```python
"""
Detection d'anomalies statistiques.
"""

class AnomalyDetector:
    """Detecteur d'anomalies financieres."""
    
    def __init__(self):
        self.methods = {
            'statistical': self._detect_statistical_outliers,
            'isolation_forest': self._detect_isolation_outliers,
            'pattern_based': self._detect_pattern_anomalies
        }
    
    def detect_amount_outliers(
        self,
        df: pd.DataFrame,
        method: str = 'statistical',
        sensitivity: str = 'medium'
    ) -> pd.DataFrame:
        """
        Detecte les montants anormaux.
        
        Args:
            df: DataFrame transactions
            method: 'statistical', 'isolation_forest', 'pattern_based'
            sensitivity: 'low' (2-sigma), 'medium' (3-sigma), 'high' (1.5-sigma)
            
        Returns:
            DataFrame avec colonne 'is_anomaly' et 'anomaly_score'
        """
        thresholds = {'low': 2.0, 'medium': 3.0, 'high': 1.5}
        threshold = thresholds[sensitivity]
        
        df = df.copy()
        df['is_anomaly'] = False
        df['anomaly_score'] = 0.0
        df['anomaly_reason'] = ''
        
        # Par categorie
        for category in df['category_validated'].unique():
            cat_mask = df['category_validated'] == category
            cat_data = df[cat_mask]
            
            if len(cat_data) < 5:
                continue
            
            amounts = cat_data['amount'].abs()
            mean = amounts.mean()
            std = amounts.std()
            
            if std == 0:
                continue
            
            # Z-score
            z_scores = (amounts - mean) / std
            
            # Marquer anomalies
            anomaly_mask = z_scores > threshold
            df.loc[cat_mask & anomaly_mask, 'is_anomaly'] = True
            df.loc[cat_mask & anomaly_mask, 'anomaly_score'] = z_scores[anomaly_mask]
            df.loc[cat_mask & anomaly_mask, 'anomaly_reason'] = f'Amount > {threshold}x std from mean'
        
        return df
    
    def detect_first_time_high_amount(self, df: pd.DataFrame) -> list[dict]:
        """
        Detecte premiers paiements a un nouveau fournisseur avec montant eleve.
        
        Returns:
            Liste des anomalies detectees
        """
        anomalies = []
        
        # Grouper par libelle nettoye
        df['clean_label'] = df['label'].apply(clean_label)
        
        for label, group in df.groupby('clean_label'):
            if len(group) == 1:  # Premiere occurrence
                amount = abs(group.iloc[0]['amount'])
                
                if amount > 200:  # Seulement si > 200€
                    anomalies.append({
                        'type': 'first_time_high_amount',
                        'transaction_id': group.iloc[0]['id'],
                        'label': label,
                        'amount': amount,
                        'severity': 'high' if amount > 500 else 'medium',
                        'message': f'Premier paiement a {label} eleve: {amount:.2f} EUR'
                    })
        
        return anomalies
    
    def detect_duplicate_risk(self, df: pd.DataFrame, time_window_hours: int = 24) -> list[dict]:
        """
        Detecte risque de double paiement.
        
        Meme montant + meme label + meme jour = alerte
        """
        anomalies = []
        
        df['date'] = pd.to_datetime(df['date'])
        
        # Grouper par (date, label, amount)
        grouped = df.groupby([
            df['date'].dt.date,
            'label',
            'amount'
        ])
        
        for (date, label, amount), group in grouped:
            if len(group) > 1:
                # Verifier si c'est vraiment un doublon (pas legitime)
                time_diff = (group['date'].max() - group['date'].min()).total_seconds() / 3600
                
                if time_diff < time_window_hours:
                    anomalies.append({
                        'type': 'potential_duplicate',
                        'transactions': group['id'].tolist(),
                        'label': label,
                        'amount': amount,
                        'count': len(group),
                        'severity': 'high',
                        'message': f'{len(group)} transactions identiques detectees pour {label}'
                    })
        
        return anomalies
```

### Anomaly Alerting

```python
def check_and_alert_anomalies():
    """Verifie et alerte sur les anomalies."""
    detector = AnomalyDetector()
    
    # Recuperer transactions recentes
    df = get_recent_transactions(days=7)
    
    # Detecter
    df_with_anomalies = detector.detect_amount_outliers(df)
    anomalies = df_with_anomalies[df_with_anomalies['is_anomaly']]
    
    # Creer notifications
    for _, row in anomalies.iterrows():
        create_notification(
            type='anomaly_detected',
            severity='high' if row['anomaly_score'] > 4 else 'medium',
            message=f"Anomalie detectee: {row['label']} ({row['amount']:.2f} EUR)",
            data={
                'transaction_id': row['id'],
                'anomaly_score': row['anomaly_score'],
                'reason': row['anomaly_reason']
            }
        )
```

---

## 📈 Module 2: Budget Prediction

### Projection Financiere

```python
"""
Prediction et projection budgetaire.
"""

class BudgetPredictor:
    """Predictions budgetaires."""
    
    def __init__(self):
        self.confidence_threshold = 0.7
    
    def predict_month_end(
        self,
        current_date: datetime = None
    ) -> dict:
        """
        Predicte la situation en fin de mois.
        
        Returns:
            {
                'predicted_balance': float,
                'confidence': float,
                'predicted_expenses_by_category': dict,
                'risk_alerts': list,
                'recommendations': list
            }
        """
        if current_date is None:
            current_date = datetime.now()
        
        # Historique mois precedents
        history = get_monthly_history(months=6)
        
        # Depenses deja engagees ce mois
        current_spending = get_current_month_spending()
        
        # Projection par categorie
        predictions = {}
        total_predicted = 0
        
        for category in get_categories():
            # Moyenne historique
            avg = history[history['category'] == category]['amount'].mean()
            
            # Deja depense
            already_spent = current_spending.get(category, 0)
            
            # Reste du mois
            days_remaining = self._days_remaining_in_month(current_date)
            month_progress = current_date.day / self._days_in_month(current_date)
            
            # Projection
            if month_progress > 0.1:  # Assez de donnees
                daily_rate = already_spent / current_date.day
                predicted_remaining = daily_rate * days_remaining
            else:
                predicted_remaining = avg * (1 - month_progress)
            
            predicted_total = already_spent + predicted_remaining
            predictions[category] = {
                'predicted': predicted_total,
                'already_spent': already_spent,
                'remaining_budget': get_budget(category) - already_spent if has_budget(category) else None
            }
            
            total_predicted += predicted_total
        
        # Generer alertes et recommandations
        alerts = self._generate_alerts(predictions)
        recommendations = self._generate_recommendations(predictions)
        
        return {
            'predicted_total_expenses': total_predicted,
            'predicted_by_category': predictions,
            'confidence': self._calculate_confidence(month_progress),
            'risk_alerts': alerts,
            'recommendations': recommendations
        }
    
    def _generate_alerts(self, predictions: dict) -> list[dict]:
        """Genere les alertes de risque."""
        alerts = []
        
        for category, data in predictions.items():
            budget = data.get('remaining_budget')
            if budget is None:
                continue
            
            predicted = data['predicted']
            
            # Calculer depassement
            if predicted > budget * 1.2:
                alerts.append({
                    'category': category,
                    'severity': 'critical',
                    'message': f'Risque de depassement de 20%+ sur {category}',
                    'predicted': predicted,
                    'budget': budget
                })
            elif predicted > budget:
                alerts.append({
                    'category': category,
                    'severity': 'warning',
                    'message': f'Budget {category} probablement depasse',
                    'predicted': predicted,
                    'budget': budget
                })
        
        return alerts
    
    def _generate_recommendations(self, predictions: dict) -> list[str]:
        """Genere des recommandations."""
        recommendations = []
        
        # Trouver categories ou on peut economiser
        for category, data in predictions.items():
            avg_spending = get_average_spending(category, months=3)
            current_rate = data['already_spent'] / datetime.now().day
            
            if current_rate > avg_spending * 1.2:
                recommendations.append(
                    f"Vos depenses {category} sont superieures a la moyenne. "
                    f"Essayez de reduire pour ce mois."
                )
        
        return recommendations
```

---

## 💬 Module 3: Conversational Assistant

### Assistant IA

```python
"""
Assistant conversationnel pour Q&A financier.
"""

class FinancialAssistant:
    """Assistant conversationnel."""
    
    SYSTEM_PROMPT = """
Tu es un assistant financier personnel expert. Tu aides l'utilisateur a comprendre 
et gerer ses finances. Tu as acces a ses donnees de transactions.

Regles:
1. Reponds toujours en francais
2. Sois concis mais complet
3. Ne fais pas de recommandations d'investissement risquees
4. Propose des actions concretes quand pertinent
5. Si tu n'as pas l'info, dis-le clairement

Tu peux:
- Repondre sur les depenses par categorie
- Calculer des soldes et moyennes
- Identifier des tendances
- Suggerer des budgets
- Repondre sur des transactions specifiques
"""
    
    def __init__(self):
        self.provider = get_ai_provider()
        self.conversation_history = []
    
    def ask(self, question: str, context: dict = None) -> str:
        """
        Pose une question a l'assistant.
        
        Args:
            question: Question de l'utilisateur
            context: Contexte additionnel (date range, etc.)
            
        Returns:
            Reponse de l'assistant
        """
        # Enrichir avec donnees
        data_context = self._gather_context(question, context)
        
        # Construire prompt
        prompt = f"""
{self.SYSTEM_PROMPT}

Donnees utilisateur:
{data_context}

Historique conversation:
{self._format_history()}

Question: {question}

Reponds de maniere utile et actionnable:"""
        
        # Appeler IA
        response = self.provider.generate_text(prompt)
        
        # Sauvegarder historique
        self.conversation_history.append({
            'role': 'user',
            'content': question
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })
        
        return response
    
    def _gather_context(self, question: str, context: dict) -> str:
        """Collecte les donnees pertinentes."""
        context_parts = []
        
        # Determiner quelles donnees sont necessaires
        if 'categorie' in question.lower() or 'depense' in question.lower():
            # Donnees par categorie
            df = get_current_month_transactions()
            by_category = df[df['amount'] < 0].groupby('category_validated')['amount'].sum()
            
            context_parts.append("Depenses par categorie ce mois:")
            for cat, amount in by_category.items():
                context_parts.append(f"- {cat}: {abs(amount):.2f} EUR")
        
        if 'solde' in question.lower() or 'balance' in question.lower():
            # Soldes
            income = get_current_month_income()
            expenses = get_current_month_expenses()
            
            context_parts.append(f"\nSolde ce mois:")
            context_parts.append(f"- Revenus: {income:.2f} EUR")
            context_parts.append(f"- Depenses: {expenses:.2f} EUR")
            context_parts.append(f"- Balance: {income + expenses:.2f} EUR")
        
        return '\n'.join(context_parts) if context_parts else "Aucune donnee specifique"

# Exemples de questions supportees
EXAMPLE_QUESTIONS = [
    "Quelle est ma categorie de depense la plus elevee ce mois?",
    "Combien ai-je depense en restauration cette annee?",
    "Compare mes depenses ce mois au mois dernier",
    "Y a-t-il des anomalies dans mes transactions recentes?",
    "Quel budget me conseilles-tu pour les courses?",
    "Resume mes finances du mois dernier"
]
```

---

## 🔧 Responsabilites

### Quand consulter cet agent

- Nouvelle feature IA
- Tuning detection anomalies
- Amelioration assistant conversationnel
- Nouveau type de prediction
- Integration nouvelle analyse

---

**Version**: 1.0
**Date**: 2026-02-25
**Statut**: PRET A L'EMPLOI

---

## 🔧 Module Additionnel: Trend Analysis & Smart Suggestions

### Trend Analysis Avance

```python
"""
Analyse de tendances et comparaisons temporelles.
"""

class TrendAnalyzer:
    """Analyseur de tendances financieres."""
    
    def __init__(self):
        self.confidence_threshold = 0.8
    
    def compare_periods(
        self,
        period_type: str = 'month',
        current_offset: int = 0,
        previous_offset: int = 1
    ) -> dict:
        """
        Compare deux periodes (MoM, YoY).
        
        Args:
            period_type: 'month', 'quarter', 'year'
            current_offset: 0 = periode actuelle
            previous_offset: 1 = periode precedente
            
        Returns:
            {
                'current_period': str,
                'previous_period': str,
                'total_change_pct': float,
                'by_category': dict,
                'insights': list[str]
            }
        """
        # Determiner periodes
        current = self._get_period(period_type, current_offset)
        previous = self._get_period(period_type, previous_offset)
        
        # Recuperer donnees
        current_df = get_transactions_by_period(current, period_type)
        previous_df = get_transactions_by_period(previous, period_type)
        
        # Calculs globaux
        current_total = current_df[current_df['amount'] < 0]['amount'].sum()
        previous_total = previous_df[previous_df['amount'] < 0]['amount'].sum()
        
        change_pct = ((current_total - previous_total) / abs(previous_total) * 100) if previous_total != 0 else 0
        
        # Par categorie
        category_comparison = {}
        all_categories = set(current_df['category_validated'].unique()) | set(previous_df['category_validated'].unique())
        
        for cat in all_categories:
            current_cat = current_df[current_df['category_validated'] == cat]['amount'].sum()
            previous_cat = previous_df[previous_df['category_validated'] == cat]['amount'].sum()
            
            cat_change = ((current_cat - previous_cat) / abs(previous_cat) * 100) if previous_cat != 0 else 0
            
            category_comparison[cat] = {
                'current': current_cat,
                'previous': previous_cat,
                'change_pct': cat_change,
                'trend': 'up' if cat_change > 0 else 'down' if cat_change < 0 else 'stable'
            }
        
        # Generer insights
        insights = self._generate_trend_insights(category_comparison, change_pct)
        
        return {
            'current_period': current,
            'previous_period': previous,
            'total_change_pct': change_pct,
            'current_total': current_total,
            'previous_total': previous_total,
            'by_category': category_comparison,
            'insights': insights
        }
    
    def detect_seasonality(self, df: pd.DataFrame, category: str = None) -> dict:
        """
        Detecte les patterns saisonniers.
        
        Returns:
            {
                'has_seasonality': bool,
                'peak_months': list[int],
                'low_months': list[int],
                'seasonal_factor': dict
            }
        """
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        
        if category:
            df = df[df['category_validated'] == category]
        
        # Moyenne par mois
        monthly_avg = df.groupby('month')['amount'].mean()
        
        # Calculer facteur saisonnier
        overall_avg = df['amount'].mean()
        seasonal_factor = monthly_avg / overall_avg
        
        # Detecter pics et creux
        peak_months = monthly_avg[monthly_avg > overall_avg * 1.2].index.tolist()
        low_months = monthly_avg[monthly_avg < overall_avg * 0.8].index.tolist()
        
        return {
            'has_seasonality': len(peak_months) > 0 or len(low_months) > 0,
            'peak_months': peak_months,
            'low_months': low_months,
            'seasonal_factor': seasonal_factor.to_dict(),
            'monthly_average': monthly_avg.to_dict()
        }
    
    def forecast_expenses(
        self,
        months_ahead: int = 3,
        category: str = None
    ) -> dict:
        """
        Prevision des depenses futures.
        
        Args:
            months_ahead: Nombre de mois a prevoir
            category: Categorie specifique (None = toutes)
            
        Returns:
            {
                'forecast': list[dict],
                'confidence_interval': tuple,
                'method': str
            }
        """
        # Recuperer historique
        df = get_transactions_last_12_months()
        
        if category:
            df = df[df['category_validated'] == category]
        
        # Methode: Moyenne mobile + saisonnalite
        df['date'] = pd.to_datetime(df['date'])
        monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum()
        
        # Calculer tendance
        trend = monthly.rolling(window=3).mean()
        
        # Prevision
        forecast = []
        last_value = monthly.iloc[-1]
        trend_slope = (monthly.iloc[-1] - monthly.iloc[-3]) / 2
        
        for i in range(1, months_ahead + 1):
            predicted = last_value + trend_slope * i
            
            # Ajuster pour saisonnalite
            future_month = (datetime.now().month + i - 1) % 12 + 1
            seasonal = self._get_seasonal_factor(future_month, category)
            predicted *= seasonal
            
            forecast.append({
                'month': future_month,
                'predicted_amount': round(predicted, 2),
                'confidence': max(0.5, 1 - (i * 0.1))  # Diminue avec l'horizon
            })
        
        return {
            'forecast': forecast,
            'method': 'moving_average_with_seasonality',
            'trend_slope': trend_slope
        }
    
    def _generate_trend_insights(self, category_comparison: dict, total_change_pct: float) -> list[str]:
        """Genere des insights textuels."""
        insights = []
        
        # Insight global
        if abs(total_change_pct) > 20:
            direction = "augmente" if total_change_pct > 0 else "diminue"
            insights.append(f"Vos depenses ont {direction} de {abs(total_change_pct):.0f}%")
        
        # Categories les plus changeantes
        changes = [(cat, data['change_pct']) for cat, data in category_comparison.items()]
        changes.sort(key=lambda x: abs(x[1]), reverse=True)
        
        for cat, change in changes[:3]:
            if abs(change) > 30:
                direction = "hausse" if change > 0 else "baisse"
                insights.append(f"{cat}: forte {direction} ({change:+.0f}%)")
        
        return insights
```

### Smart Suggestions

```python
"""
Suggestions intelligentes basees sur l'historique.
"""

class SmartSuggestions:
    """Generateur de suggestions personnalisees."""
    
    def __init__(self):
        self.min_confidence = 0.6
    
    def get_all_suggestions(self) -> list[dict]:
        """
        Genere toutes les suggestions pertinentes.
        
        Returns:
            Liste de suggestions avec priorite
        """
        suggestions = []
        
        # 1. Suggestions de budget
        budget_suggestions = self._suggest_budget_adjustments()
        suggestions.extend(budget_suggestions)
        
        # 2. Suggestions de catégorisation
        cat_suggestions = self._suggest_categorization_rules()
        suggestions.extend(cat_suggestions)
        
        # 3. Suggestions d'economies
        savings_suggestions = self._suggest_savings_opportunities()
        suggestions.extend(savings_suggestions)
        
        # 4. Alertes preventives
        alert_suggestions = self._suggest_preventive_alerts()
        suggestions.extend(alert_suggestions)
        
        # Trier par priorite
        suggestions.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        return suggestions[:10]  # Top 10
    
    def _suggest_budget_adjustments(self) -> list[dict]:
        """Suggere des ajustements de budget."""
        suggestions = []
        
        for category in get_categories():
            history = get_spending_history(category, months=3)
            avg = sum(history) / len(history) if history else 0
            current_budget = get_budget(category)
            
            if current_budget is None:
                # Pas de budget defini
                if avg > 100:  # Seulement si depenses significatives
                    suggested = avg * 1.1  # +10% marge
                    suggestions.append({
                        'type': 'new_budget',
                        'category': category,
                        'message': f"Definir un budget pour {category} (~{suggested:.0f} EUR/mois)",
                        'suggested_amount': suggested,
                        'priority': 3
                    })
            elif avg > current_budget * 1.2:
                # Depassement regulier
                suggestions.append({
                    'type': 'increase_budget',
                    'category': category,
                    'message': f"Augmenter le budget {category} ({avg:.0f} EUR/mois en moyenne)",
                    'current': current_budget,
                    'suggested': avg * 1.1,
                    'priority': 4
                })
            elif avg < current_budget * 0.7:
                # Budget trop eleve
                suggestions.append({
                    'type': 'decrease_budget',
                    'category': category,
                    'message': f"Reduire le budget {category} (utilisation: {avg/current_budget:.0%})",
                    'suggested': avg * 1.1,
                    'priority': 2
                })
        
        return suggestions
    
    def _suggest_categorization_rules(self) -> list[dict]:
        """Suggere de nouvelles regles de categorisation."""
        suggestions = []
        
        # Trouver transactions souvent corrigees
        corrections = get_frequent_corrections(min_occurrences=3)
        
        for pattern, data in corrections.items():
            if data['confidence'] > self.min_confidence:
                suggestions.append({
                    'type': 'new_rule',
                    'pattern': pattern,
                    'category': data['correct_category'],
                    'message': f"Creer regle: '{pattern}' -> {data['correct_category']}",
                    'occurrences': data['count'],
                    'priority': 5
                })
        
        return suggestions
    
    def _suggest_savings_opportunities(self) -> list[dict]:
        """Identifie des opportunites d'economies."""
        suggestions = []
        
        # Abonnements detectes
        subscriptions = detect_subscriptions()
        for sub in subscriptions:
            if sub['monthly_cost'] > 50:
                suggestions.append({
                    'type': 'subscription_review',
                    'merchant': sub['merchant'],
                    'message': f"Revoir abonnement {sub['merchant']}: {sub['monthly_cost']:.0f} EUR/mois",
                    'annual_cost': sub['monthly_cost'] * 12,
                    'priority': 4
                })
        
        # Categories sur-ciblees
        spending = get_category_comparison_with_peers()  # Si donnees dispo
        
        return suggestions
    
    def _suggest_preventive_alerts(self) -> list[dict]:
        """Alertes preventives."""
        suggestions = []
        
        # Detecter fin de mois proche avec budget serre
        if datetime.now().day > 25:
            remaining_days = 30 - datetime.now().day
            
            for category in get_categories():
                budget = get_budget(category)
                spent = get_current_month_spending(category)
                
                if budget and spent > budget * 0.9:
                    remaining = budget - spent
                    daily_allowance = remaining / remaining_days
                    
                    suggestions.append({
                        'type': 'month_end_warning',
                        'category': category,
                        'message': f"{category}: {remaining:.0f} EUR pour {remaining_days} jours ({daily_allowance:.0f} EUR/jour)",
                        'priority': 5
                    })
        
        return suggestions
```

### Memoire Conversationnelle Avancee

```python
"""
Memoire long terme pour l'assistant conversationnel.
"""

class ConversationMemory:
    """Systeme de memoire pour l'assistant."""
    
    MAX_HISTORY = 10  # Messages recents
    MAX_TOKENS = 4000  # Limite contexte
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.short_term = []  # Messages recents
        self.long_term = []   # Faits importants extraits
    
    def add_message(self, role: str, content: str):
        """Ajoute un message a l'historique."""
        self.short_term.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now()
        })
        
        # Garder seulement les plus recents
        if len(self.short_term) > self.MAX_HISTORY:
            self.short_term = self.short_term[-self.MAX_HISTORY:]
        
        # Extraction de faits si reponse utilisateur
        if role == 'user':
            self._extract_facts(content)
    
    def _extract_facts(self, message: str):
        """Extrait les faits importants du message."""
        # Patterns a detecter
        patterns = {
            'income_change': r'(nouveau salaire|augmentation|promotion).*?(\d+)',
            'goal': r'(objectif|but|voudrais).*?(\d+).*?(euros|eur)',
            'preference': r'(prefere|aime|deteste).*?(categorie|spending)',
        }
        
        for fact_type, pattern in patterns.items():
            if re.search(pattern, message.lower()):
                self.long_term.append({
                    'type': fact_fact_type,
                    'content': message,
                    'extracted_at': datetime.now()
                })
    
    def get_context(self, question: str) -> str:
        """
        Construit le contexte pour une question.
        
        Selectionne:
        1. Historique recent pertinent
        2. Faits long terme pertinents
        3. Resume si trop long
        """
        context_parts = []
        
        # Faits long terme pertinents
        relevant_facts = self._find_relevant_facts(question)
        if relevant_facts:
            context_parts.append("Faits connus sur l'utilisateur:")
            for fact in relevant_facts:
                context_parts.append(f"- {fact['content']}")
        
        # Historique recent
        if self.short_term:
            context_parts.append("\nConversation recente:")
            for msg in self.short_term[-5:]:
                role = "Utilisateur" if msg['role'] == 'user' else "Assistant"
                context_parts.append(f"{role}: {msg['content'][:200]}...")
        
        return '\n'.join(context_parts)
    
    def _find_relevant_facts(self, question: str) -> list[dict]:
        """Trouve les faits pertinents pour la question."""
        keywords = set(question.lower().split())
        
        scored_facts = []
        for fact in self.long_term:
            fact_words = set(fact['content'].lower().split())
            score = len(keywords & fact_words)
            if score > 0:
                scored_facts.append((score, fact))
        
        scored_facts.sort(reverse=True)
        return [f for _, f in scored_facts[:3]]
    
    def clear(self):
        """Efface la memoire."""
        self.short_term = []
        self.long_term = []

class TokenAwarePromptBuilder:
    """Constructeur de prompts respectant les limites de tokens."""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.estimated_tokens = 0
    
    def estimate_tokens(self, text: str) -> int:
        """Estime le nombre de tokens."""
        # Regle approximative: 1 token ~= 4 caracteres pour l'anglais/francais
        return len(text) // 3
    
    def build_prompt(
        self,
        system_prompt: str,
        context: str,
        question: str,
        history: list[dict]
    ) -> str:
        """
        Construit un prompt qui tient dans la limite de tokens.
        
        Strategy:
        1. Commencer avec system + question
        2. Ajouter contexte
        3. Ajouter historique si place
        4. Tronquer si necessaire
        """
        # Base obligatoire
        base = f"{system_prompt}\n\nQuestion: {question}"
        base_tokens = self.estimate_tokens(base)
        
        remaining = self.max_tokens - base_tokens - 200  # Marge de securite
        
        # Ajouter contexte si place
        context_tokens = self.estimate_tokens(context)
        if context_tokens < remaining * 0.5:
            base = f"{system_prompt}\n\nContexte:\n{context}\n\nQuestion: {question}"
            remaining -= context_tokens
        else:
            # Resumer contexte
            summarized = self._summarize_context(context, remaining * 0.5)
            base = f"{system_prompt}\n\nContexte:\n{summarized}\n\nQuestion: {question}"
        
        # Ajouter historique si place
        history_text = self._format_history(history, remaining)
        if history_text:
            base = f"{base}\n\nHistorique:\n{history_text}"
        
        return base
    
    def _summarize_context(self, context: str, max_tokens: int) -> str:
        """Resume le contexte pour tenir dans la limite."""
        lines = context.split('\n')
        
        # Garder les lignes les plus importantes
        priority_lines = []
        other_lines = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['total', 'solde', 'budget', 'alerte']):
                priority_lines.append(line)
            else:
                other_lines.append(line)
        
        # Construire resume
        result = priority_lines[:5]
        
        remaining_tokens = max_tokens - self.estimate_tokens('\n'.join(result))
        
        for line in other_lines:
            if self.estimate_tokens(line) < remaining_tokens:
                result.append(line)
                remaining_tokens -= self.estimate_tokens(line)
            else:
                break
        
        return '\n'.join(result)
    
    def _format_history(self, history: list[dict], max_tokens: int) -> str:
        """Formate l'historique en respectant la limite."""
        formatted = []
        total_tokens = 0
        
        for msg in reversed(history[-5:]):  # 5 derniers messages
            line = f"{msg['role']}: {msg['content'][:100]}"
            line_tokens = self.estimate_tokens(line)
            
            if total_tokens + line_tokens > max_tokens:
                break
            
            formatted.insert(0, line)
            total_tokens += line_tokens
        
        return '\n'.join(formatted)
```

---

**Version**: 1.1 - **COMPLETED**
**Ajouts**: Trend analysis, seasonality, forecasting, smart suggestions, conversation memory, token management
