"""
Intelligent Suggestions Engine for FinancePerso.

Analyzes user data to provide actionable recommendations for:
- Category optimization
- Rule creation
- Budget adjustments
- Member mapping
- Duplicate detection
- Spending pattern improvements
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from modules.logger import logger


@dataclass
class Suggestion:
    """A single intelligent suggestion."""
    id: str
    type: str  # 'category', 'rule', 'budget', 'member', 'duplicate', 'pattern'
    priority: str  # 'high', 'medium', 'low'
    title: str
    description: str
    action_label: str
    action_data: Dict[str, Any]
    impact_score: int  # 0-100
    auto_fixable: bool = False


class SmartSuggestionEngine:
    """Engine for generating intelligent suggestions based on data analysis."""
    
    def __init__(self, transactions_df: pd.DataFrame, rules_df: pd.DataFrame, 
                 budgets_df: pd.DataFrame, members_df: pd.DataFrame):
        self.transactions = transactions_df
        self.rules = rules_df
        self.budgets = budgets_df
        self.members = members_df
        self.suggestions: List[Suggestion] = []
        
    def analyze_all(self) -> List[Suggestion]:
        """Run all analyses and return combined suggestions."""
        self.suggestions = []
        
        if self.transactions.empty:
            return []
        
        try:
            # Rule & Category Analysis
            self._analyze_uncategorized_transactions()
            self._analyze_frequent_patterns()
            self._analyze_missing_rules()
            self._analyze_missing_recurring_patterns()
            self._analyze_category_consolidation()
            
            # Budget Analysis
            self._analyze_budget_overruns()
            self._analyze_empty_budget_categories()
            self._analyze_savings_opportunities()
            
            # Member Analysis
            self._analyze_unknown_members()
            self._analyze_frequent_beneficiaries()
            
            # Pattern & Anomaly Analysis
            self._analyze_potential_duplicates()
            self._analyze_spending_anomalies()
            self._analyze_subscription_increases()
            self._analyze_unusual_large_amounts()
            
            # Income Analysis
            self._analyze_income_variations()
            
            # Tag Analysis
            self._analyze_missing_tags()
            
            # Sort by impact score (descending)
            self.suggestions.sort(key=lambda x: x.impact_score, reverse=True)
            
        except Exception as e:
            logger.error(f"Error in smart suggestion analysis: {e}")
        
        return self.suggestions
    
    def _analyze_uncategorized_transactions(self):
        """Suggest creating rules for frequently uncategorized transactions."""
        pending = self.transactions[self.transactions['status'] == 'pending']
        
        if pending.empty:
            return
        
        # Group by label and count
        label_counts = pending['label'].value_counts().head(5)
        
        for label, count in label_counts.items():
            if count >= 3:  # Only suggest if appears multiple times
                self.suggestions.append(Suggestion(
                    id=f"uncat_{hash(label) % 10000}",
                    type="rule",
                    priority="high",
                    title=f"📋 {count} transactions non catégorisées : '{label[:40]}...'" if len(label) > 40 else f"📋 {count} transactions non catégorisées : '{label}'",
                    description=f"Cette transaction apparaît {count} fois sans catégorie. Créez une règle pour la catégoriser automatiquement.",
                    action_label="Créer une règle",
                    action_data={
                        "pattern": label[:30],
                        "type": "create_rule",
                        "suggested_category": self._guess_category_from_label(label)
                    },
                    impact_score=min(count * 10, 100),
                    auto_fixable=False
                ))
    
    def _analyze_frequent_patterns(self):
        """Analyze frequent transaction patterns for rule creation."""
        validated = self.transactions[self.transactions['status'] == 'validated']
        
        if validated.empty:
            return
        
        # Find merchants/labels that appear frequently with same category
        grouped = validated.groupby(['label', 'category_validated']).size().reset_index(name='count')
        frequent = grouped[grouped['count'] >= 5].sort_values('count', ascending=False).head(5)
        
        # Check if these already have rules
        existing_patterns = set(self.rules['pattern'].str.lower().tolist()) if not self.rules.empty else set()
        
        for _, row in frequent.iterrows():
            pattern_lower = row['label'].lower()
            if pattern_lower not in existing_patterns and len(row['label']) > 5:
                self.suggestions.append(Suggestion(
                    id=f"freq_{hash(row['label']) % 10000}",
                    type="rule",
                    priority="medium",
                    title=f"🔄 Pattern fréquent détecté : '{row['label'][:40]}...'" if len(row['label']) > 40 else f"🔄 Pattern fréquent : '{row['label']}'",
                    description=f"{row['count']} transactions avec la catégorie '{row['category_validated']}'. Une règle permettrait d'automatiser.",
                    action_label="Créer règle auto",
                    action_data={
                        "pattern": row['label'][:30],
                        "category": row['category_validated'],
                        "type": "create_rule"
                    },
                    impact_score=min(row['count'] * 5, 80),
                    auto_fixable=True
                ))
    
    def _analyze_budget_overruns(self):
        """Analyze budget overruns and suggest adjustments."""
        if self.budgets.empty or self.transactions.empty:
            return
        
        # Calculate spending per category for current month
        current_month = datetime.now().strftime('%Y-%m')
        month_df = self.transactions[
            (self.transactions['date'].str.startswith(current_month)) &
            (self.transactions['amount'] < 0)  # Expenses only
        ]
        
        spending_by_cat = month_df.groupby('category_validated')['amount'].sum().abs()
        
        for _, budget_row in self.budgets.iterrows():
            category = budget_row['category']
            budget_amount = budget_row['amount']
            spent = spending_by_cat.get(category, 0)
            
            if spent > budget_amount * 1.1:  # Over budget by 10%
                overspend_pct = int((spent / budget_amount - 1) * 100)
                self.suggestions.append(Suggestion(
                    id=f"budget_{hash(category) % 10000}",
                    type="budget",
                    priority="high" if overspend_pct > 50 else "medium",
                    title=f"💰 Dépassement budget : {category}",
                    description=f"Dépensé : {spent:.0f}€ / Budget : {budget_amount:.0f}€ (+{overspend_pct}%). Ajustez votre budget ou surveillez vos dépenses.",
                    action_label="Ajuster le budget",
                    action_data={
                        "category": category,
                        "current_budget": budget_amount,
                        "suggested_budget": int(spent * 1.1),
                        "type": "adjust_budget"
                    },
                    impact_score=min(overspend_pct, 100),
                    auto_fixable=False
                ))
            elif spent < budget_amount * 0.5:  # Under budget by 50%
                self.suggestions.append(Suggestion(
                    id=f"budget_under_{hash(category) % 10000}",
                    type="budget",
                    priority="low",
                    title=f"💡 Budget surévalué : {category}",
                    description=f"Vous n'utilisez que {spent:.0f}€ sur {budget_amount:.0f}€. Envisagez de réduire ce budget.",
                    action_label="Voir détails",
                    action_data={
                        "category": category,
                        "type": "view_budget"
                    },
                    impact_score=30,
                    auto_fixable=False
                ))
    
    def _analyze_unknown_members(self):
        """Suggest member mappings for transactions with unknown members."""
        unknown_df = self.transactions[self.transactions['member'] == 'Inconnu']
        
        if unknown_df.empty:
            return
        
        # Group by card suffix
        card_groups = unknown_df[unknown_df['card_suffix'].notna()].groupby('card_suffix').size()
        
        for card_suffix, count in card_groups.head(3).items():
            if count >= 3:
                self.suggestions.append(Suggestion(
                    id=f"member_card_{card_suffix}",
                    type="member",
                    priority="medium",
                    title=f"💳 Carte non identifiée : ...{card_suffix}",
                    description=f"{count} transactions avec cette carte n'ont pas de membre attribué. Mappez cette carte pour une attribution automatique.",
                    action_label="Mapper la carte",
                    action_data={
                        "card_suffix": card_suffix,
                        "type": "map_card"
                    },
                    impact_score=min(count * 8, 90),
                    auto_fixable=False
                ))
        
        # Group by account
        account_groups = unknown_df[unknown_df['account_label'].notna()].groupby('account_label').size()
        
        for account, count in account_groups.head(2).items():
            if count >= 5:
                self.suggestions.append(Suggestion(
                    id=f"member_acc_{hash(account) % 10000}",
                    type="member",
                    priority="high",
                    title=f"🏦 Compte sans membre par défaut : {account}",
                    description=f"{count} transactions 'Inconnu' sur ce compte. Définissez un membre par défaut pour ce compte.",
                    action_label="Définir membre",
                    action_data={
                        "account_label": account,
                        "type": "map_account"
                    },
                    impact_score=min(count * 5, 85),
                    auto_fixable=False
                ))
    
    def _analyze_potential_duplicates(self):
        """Detect potential duplicate transactions."""
        # Group by date, label, amount
        grouped = self.transactions.groupby(['date', 'label', 'amount']).size().reset_index(name='count')
        duplicates = grouped[grouped['count'] > 1]
        
        if not duplicates.empty:
            total_duplicates = duplicates['count'].sum() - len(duplicates)
            self.suggestions.append(Suggestion(
                id="potential_duplicates",
                type="duplicate",
                priority="high" if total_duplicates > 5 else "medium",
                title=f"⚠️ {total_duplicates} transaction(s) potentiellement en double",
                description="Certaines transactions apparaissent plusieurs fois avec la même date, libellé et montant. Vérifiez s'il s'agit de vrais doublons.",
                action_label="Voir les doublons",
                action_data={
                    "type": "view_duplicates",
                    "count": total_duplicates
                },
                impact_score=min(total_duplicates * 15, 100),
                auto_fixable=False
            ))
    
    def _analyze_category_consolidation(self):
        """Suggest consolidating similar categories."""
        if self.transactions.empty:
            return
        
        categories = self.transactions['category_validated'].unique()
        
        # Find similar category names
        similar_pairs = []
        for i, cat1 in enumerate(categories):
            for cat2 in categories[i+1:]:
                # Simple similarity check
                if self._categories_similar(cat1, cat2):
                    similar_pairs.append((cat1, cat2))
        
        for cat1, cat2 in similar_pairs[:2]:
            count1 = len(self.transactions[self.transactions['category_validated'] == cat1])
            count2 = len(self.transactions[self.transactions['category_validated'] == cat2])
            
            self.suggestions.append(Suggestion(
                id=f"consolidate_{hash(cat1 + cat2) % 10000}",
                type="category",
                priority="low",
                title=f"🏷️ Catégories similaires : '{cat1}' et '{cat2}'",
                description=f"Ces catégories ont des noms similaires ({count1} et {count2} transactions). Envisagez de les fusionner.",
                action_label="Fusionner",
                action_data={
                    "source": cat1,
                    "target": cat2,
                    "type": "merge_categories"
                },
                impact_score=40,
                auto_fixable=False
            ))
    
    def _analyze_missing_rules(self):
        """Analyze transactions that could benefit from new rules."""
        validated = self.transactions[self.transactions['status'] == 'validated']
        
        if validated.empty or self.rules.empty:
            return
        
        # Find labels that are manually categorized but have no rule
        existing_patterns = set(self.rules['pattern'].str.lower().tolist())
        
        # Get top manually categorized labels
        manual_cats = validated[validated['category_validated'] != 'Inconnu']
        label_cat_pairs = manual_cats.groupby(['label', 'category_validated']).size().reset_index(name='count')
        
        for _, row in label_cat_pairs.head(10).iterrows():
            pattern = row['label'][:20]  # Use prefix as pattern
            if pattern.lower() not in existing_patterns and row['count'] >= 3:
                self.suggestions.append(Suggestion(
                    id=f"missing_rule_{hash(row['label']) % 10000}",
                    type="rule",
                    priority="medium",
                    title=f"📝 Règle manquante : '{pattern}...' → {row['category_validated']}",
                    description=f"{row['count']} transactions manuellement catégorisées. Une règle automatiserait cela.",
                    action_label="Créer règle",
                    action_data={
                        "pattern": pattern,
                        "category": row['category_validated'],
                        "type": "create_rule"
                    },
                    impact_score=min(row['count'] * 8, 75),
                    auto_fixable=True
                ))
                break  # Only suggest one to avoid overwhelming
    
    def _analyze_spending_anomalies(self):
        """Detect unusual spending patterns."""
        expenses = self.transactions[self.transactions['amount'] < 0]
        
        if expenses.empty:
            return
        
        # Find categories with sudden spike compared to average
        expenses['month'] = expenses['date'].str[:7]
        current_month = datetime.now().strftime('%Y-%m')
        
        current_expenses = expenses[expenses['month'] == current_month]
        
        if len(current_expenses) < 5:
            return
        
        # Calculate category averages (excluding current month)
        historical = expenses[expenses['month'] != current_month]
        
        if historical.empty:
            return
        
        cat_averages = historical.groupby('category_validated')['amount'].mean().abs()
        current_totals = current_expenses.groupby('category_validated')['amount'].sum().abs()
        
        for category, current_total in current_totals.items():
            avg_monthly = cat_averages.get(category, 0)
            
            if avg_monthly > 0 and current_total > avg_monthly * 2:
                spike_pct = int((current_total / avg_monthly - 1) * 100)
                
                self.suggestions.append(Suggestion(
                    id=f"spike_{hash(category) % 10000}",
                    type="pattern",
                    priority="medium",
                    title=f"📈 Pic de dépenses : {category} (+{spike_pct}%)",
                    description=f"Ce mois : {current_total:.0f}€ vs moyenne : {avg_monthly:.0f}€. Vérifiez s'il s'agit de dépenses exceptionnelles.",
                    action_label="Explorer",
                    action_data={
                        "category": category,
                        "type": "explore_category"
                    },
                    impact_score=min(spike_pct, 100),
                    auto_fixable=False
                ))
                break  # Only one spike suggestion
    
    def _analyze_subscription_increases(self):
        """Detect subscription price increases."""
        # Find recurring transactions (same label, monthly, similar amount)
        expenses = self.transactions[self.transactions['amount'] < 0].copy()
        
        if len(expenses) < 10:
            return
        
        # Group by label and analyze price evolution
        expenses['month'] = expenses['date'].str[:7]
        expenses['amount_abs'] = expenses['amount'].abs()
        
        # Find labels with multiple months
        label_months = expenses.groupby('label')['month'].nunique()
        recurring_labels = label_months[label_months >= 3].index
        
        for label in recurring_labels[:3]:  # Limit to 3
            label_df = expenses[expenses['label'] == label]
            monthly_avg = label_df.groupby('month')['amount_abs'].mean()
            
            if len(monthly_avg) >= 3:
                # Check for increasing trend
                first_avg = monthly_avg.iloc[0]
                last_avg = monthly_avg.iloc[-1]
                
                if last_avg > first_avg * 1.15:  # 15% increase
                    increase_pct = int((last_avg / first_avg - 1) * 100)
                    
                    self.suggestions.append(Suggestion(
                        id=f"sub_inc_{hash(label) % 10000}",
                        type="pattern",
                        priority="high",
                        title=f"💳 Augmentation d'abonnement : {label[:40]}..." if len(label) > 40 else f"💳 Augmentation : {label}",
                        description=f"L'abonnement a augmenté de {increase_pct}% ({first_avg:.0f}€ → {last_avg:.0f}€). Vérifiez si c'est justifié ou négociez.",
                        action_label="Voir l'évolution",
                        action_data={
                            "label": label,
                            "type": "view_subscription"
                        },
                        impact_score=min(increase_pct, 100),
                        auto_fixable=False
                    ))
    
    def _analyze_income_variations(self):
        """Detect income variations (drops or increases)."""
        income = self.transactions[self.transactions['amount'] > 0]
        
        if income.empty:
            return
        
        income['month'] = income['date'].str[:7]
        monthly_income = income.groupby('month')['amount'].sum()
        
        if len(monthly_income) < 3:
            return
        
        # Calculate average excluding last month
        historical_avg = monthly_income.iloc[:-1].mean()
        last_month = monthly_income.iloc[-1]
        
        variation_pct = abs((last_month - historical_avg) / historical_avg * 100)
        
        if variation_pct > 20:  # Significant variation
            if last_month < historical_avg:
                self.suggestions.append(Suggestion(
                    id="income_drop",
                    type="pattern",
                    priority="high",
                    title=f"📉 Baisse des revenus ({variation_pct:.0f}%)",
                    description=f"Revenus du mois : {last_month:.0f}€ vs moyenne : {historical_avg:.0f}€. Vérifiez vos sources de revenus.",
                    action_label="Analyser",
                    action_data={"type": "view_income_analysis"},
                    impact_score=min(int(variation_pct), 100),
                    auto_fixable=False
                ))
            else:
                self.suggestions.append(Suggestion(
                    id="income_increase",
                    type="pattern",
                    priority="low",
                    title=f"📈 Hausse des revenus (+{variation_pct:.0f}%)",
                    description=f"Excellent ! Revenus du mois : {last_month:.0f}€ vs moyenne : {historical_avg:.0f}€.",
                    action_label="Voir détails",
                    action_data={"type": "view_income_analysis"},
                    impact_score=min(int(variation_pct / 2), 100),
                    auto_fixable=False
                ))
    
    def _analyze_empty_budget_categories(self):
        """Find budget categories with no transactions."""
        if self.budgets.empty:
            return
        
        current_month = datetime.now().strftime('%Y-%m')
        month_df = self.transactions[
            (self.transactions['date'].str.startswith(current_month)) &
            (self.transactions['amount'] < 0)
        ]
        
        used_categories = set(month_df['category_validated'].unique())
        
        for _, budget in self.budgets.iterrows():
            category = budget['category']
            if category not in used_categories and category != 'Inconnu':
                self.suggestions.append(Suggestion(
                    id=f"empty_budget_{hash(category) % 10000}",
                    type="budget",
                    priority="low",
                    title=f"💤 Catégorie inactive : {category}",
                    description=f"Budget défini ({budget['amount']:.0f}€) mais aucune dépense ce mois. Surveillez ou ajustez le budget.",
                    action_label="Voir budget",
                    action_data={
                        "category": category,
                        "type": "view_budget"
                    },
                    impact_score=25,
                    auto_fixable=False
                ))
    
    def _analyze_missing_recurring_patterns(self):
        """Detect recurring monthly patterns that aren't tracked."""
        expenses = self.transactions[self.transactions['amount'] < 0].copy()
        
        if len(expenses) < 20:
            return
        
        expenses['month'] = expenses['date'].str[:7]
        expenses['day'] = pd.to_datetime(expenses['date']).dt.day
        
        # Group by label and check monthly recurrence
        label_analysis = expenses.groupby('label').agg({
            'month': 'nunique',
            'amount': ['mean', 'std'],
            'date': 'count'
        }).reset_index()
        
        label_analysis.columns = ['label', 'unique_months', 'avg_amount', 'amount_std', 'count']
        
        # Find labels that appear regularly with similar amounts
        recurring = label_analysis[
            (label_analysis['unique_months'] >= 3) &
            (label_analysis['count'] >= 3) &
            (label_analysis['amount_std'] < abs(label_analysis['avg_amount']) * 0.2)  # Consistent amounts
        ]
        
        for _, row in recurring.head(2).iterrows():
            label = row['label']
            avg_amount = abs(row['avg_amount'])
            
            # Check if already has a rule
            has_rule = False
            if not self.rules.empty:
                has_rule = any(label.lower() in str(p).lower() for p in self.rules['pattern'])
            
            if not has_rule and len(label) > 5:
                self.suggestions.append(Suggestion(
                    id=f"recurring_{hash(label) % 10000}",
                    type="rule",
                    priority="medium",
                    title=f"🔄 Dépense récurrente détectée : {label[:40]}..." if len(label) > 40 else f"🔄 Récurrente : {label}",
                    description=f"Environ {avg_amount:.0f}€/mois sur {int(row['unique_months'])} mois. Créez une règle pour suivre automatiquement.",
                    action_label="Créer règle",
                    action_data={
                        "pattern": label[:25],
                        "type": "create_rule",
                        "suggested_category": self._guess_category_from_label(label)
                    },
                    impact_score=min(int(row['unique_months']) * 15, 85),
                    auto_fixable=True
                ))
    
    def _analyze_unusual_large_amounts(self):
        """Detect unusually large transactions."""
        expenses = self.transactions[self.transactions['amount'] < 0]
        
        if len(expenses) < 10:
            return
        
        # Calculate percentiles per category
        for category in expenses['category_validated'].unique():
            if category == 'Inconnu':
                continue
                
            cat_expenses = expenses[expenses['category_validated'] == category]['amount'].abs()
            
            if len(cat_expenses) < 5:
                continue
            
            q90 = cat_expenses.quantile(0.90)
            q50 = cat_expenses.median()
            
            # Find transactions above 90th percentile
            large_txns = expenses[
                (expenses['category_validated'] == category) &
                (expenses['amount'].abs() > q90 * 1.5) &
                (expenses['amount'].abs() > q50 * 3)  # At least 3x median
            ]
            
            if not large_txns.empty:
                txn = large_txns.iloc[0]  # Take the most recent
                amount = abs(txn['amount'])
                
                self.suggestions.append(Suggestion(
                    id=f"large_{hash(str(txn['id'])) % 10000}",
                    type="pattern",
                    priority="medium",
                    title=f"💰 Montant inhabituel : {amount:.0f}€ ({category})",
                    description=f"Cette transaction est anormalement élevée pour la catégorie '{category}'. Vérifiez qu'elle est correctement catégorisée.",
                    action_label="Vérifier",
                    action_data={
                        "transaction_id": txn['id'],
                        "type": "view_transaction"
                    },
                    impact_score=min(int(amount / q50), 100),
                    auto_fixable=False
                ))
                break  # Only one suggestion of this type
    
    def _analyze_frequent_beneficiaries(self):
        """Suggest mapping frequent beneficiaries."""
        # Check beneficiary field
        if 'beneficiary' not in self.transactions.columns:
            return
        
        beneficiaries = self.transactions[
            (self.transactions['beneficiary'].notna()) &
            (self.transactions['beneficiary'] != '') &
            (self.transactions['beneficiary'] != 'Inconnu') &
            (self.transactions['beneficiary'] != 'Famille')
        ]
        
        if beneficiaries.empty:
            return
        
        # Count by beneficiary
        ben_counts = beneficiaries['beneficiary'].value_counts().head(5)
        
        # Get existing member names
        existing_members = set()
        if not self.members.empty:
            existing_members = set(self.members['name'].str.lower().tolist())
        
        for beneficiary, count in ben_counts.items():
            if count >= 5 and beneficiary.lower() not in existing_members:
                self.suggestions.append(Suggestion(
                    id=f"benef_{hash(beneficiary) % 10000}",
                    type="member",
                    priority="low",
                    title=f"👤 Bénéficiaire fréquent : {beneficiary}",
                    description=f"{count} transactions vers '{beneficiary}'. Ajoutez comme membre pour de meilleures statistiques.",
                    action_label="Ajouter membre",
                    action_data={
                        "name": beneficiary,
                        "type": "add_member"
                    },
                    impact_score=min(count * 5, 60),
                    auto_fixable=False
                ))
    
    def _analyze_savings_opportunities(self):
        """Analyze savings rate and suggest improvements."""
        # Calculate savings rate by month
        self.transactions['month'] = self.transactions['date'].str[:7]
        
        monthly_data = []
        for month, group in self.transactions.groupby('month'):
            income = group[group['amount'] > 0]['amount'].sum()
            expenses = abs(group[group['amount'] < 0]['amount'].sum())
            savings = income - expenses
            savings_rate = (savings / income * 100) if income > 0 else 0
            
            monthly_data.append({
                'month': month,
                'income': income,
                'expenses': expenses,
                'savings': savings,
                'savings_rate': savings_rate
            })
        
        if len(monthly_data) < 2:
            return
        
        # Check current month savings rate
        current = monthly_data[-1]
        avg_rate = sum(m['savings_rate'] for m in monthly_data[:-1]) / len(monthly_data[:-1])
        
        if current['savings_rate'] < 10 and current['savings_rate'] < avg_rate - 5:
            self.suggestions.append(Suggestion(
                id="low_savings",
                type="budget",
                priority="medium",
                title=f"💡 Taux d'épargne faible ({current['savings_rate']:.0f}%)",
                description=f"Votre taux d'épargne est inférieur à la moyenne ({avg_rate:.0f}%). Objectif recommandé : 20%.",
                action_label="Voir analyse",
                action_data={"type": "view_savings_analysis"},
                impact_score=70,
                auto_fixable=False
            ))
        elif current['savings_rate'] >= 20:
            self.suggestions.append(Suggestion(
                id="good_savings",
                type="budget",
                priority="low",
                title=f"🎯 Excellent taux d'épargne ({current['savings_rate']:.0f}%)",
                description="Bravo ! Vous épargnez plus de 20% de vos revenus. Continuez ainsi !",
                action_label="Continuer",
                action_data={"type": "view_savings_analysis"},
                impact_score=30,
                auto_fixable=False
            ))
    
    def _analyze_missing_tags(self):
        """Suggest adding tags to untagged transactions."""
        # Check if tags column exists
        if 'tags' not in self.transactions.columns:
            return
        
        untagged = self.transactions[
            (self.transactions['tags'].isna()) | 
            (self.transactions['tags'] == '')
        ]
        
        if len(untagged) < 10:
            return
        
        # Group by category
        untagged_by_cat = untagged.groupby('category_validated').size().sort_values(ascending=False)
        
        for category, count in untagged_by_cat.head(2).items():
            if category == 'Inconnu':
                continue
                
            self.suggestions.append(Suggestion(
                id=f"tags_{hash(category) % 10000}",
                type="category",
                priority="low",
                title=f"🏷️ Transactions sans tags : {category} ({count})",
                description=f"{count} transactions dans '{category}' n'ont pas de tags. Les tags améliorent l'analyse.",
                action_label="Ajouter tags",
                action_data={
                    "category": category,
                    "type": "add_tags"
                },
                impact_score=min(count * 2, 40),
                auto_fixable=False
            ))
    
    def _guess_category_from_label(self, label: str) -> str:
        """Try to guess category from label keywords."""
        label_upper = label.upper()
        
        keywords_map = {
            'Alimentation': ['SUPER', 'CARREFOUR', 'LECLERC', 'AUCHAN', 'LIDL', 'ALDI', 'CASINO', 'FRANPRIX'],
            'Transport': ['SNCF', 'RATP', 'UBER', 'BOLT', 'TAXI', 'PARKING', 'ESSENCE', 'TOTAL', 'SHELL'],
            'Restaurants': ['RESTO', 'MCDO', 'KFC', 'SUSHI', 'PIZZA', 'RESTAURANT', 'BRASSERIE'],
            'Santé': ['PHARMA', 'MEDIC', 'DENTISTE', 'DOCTEUR', 'HOPITAL', 'CLINIQUE'],
            'Loisirs': ['NETFLIX', 'SPOTIFY', 'DISNEY', 'PRIME', 'CINEMA', 'THEATRE'],
            'Shopping': ['AMAZON', 'CDISCOUNT', 'FNAC', 'DARTY', 'BOULANGER', 'DECATHLON'],
            'Services': ['EDF', 'GAZ', 'ORANGE', 'SFR', 'FREE', 'BOUYGUES', 'CANAL'],
        }
        
        for category, keywords in keywords_map.items():
            if any(kw in label_upper for kw in keywords):
                return category
        
        return "Inconnu"
    
    def _categories_similar(self, cat1: str, cat2: str) -> bool:
        """Check if two category names are similar."""
        # Simple similarity metrics
        c1, c2 = cat1.lower(), cat2.lower()
        
        # One contains the other
        if c1 in c2 or c2 in c1:
            return True
        
        # Edit distance (simplified)
        if abs(len(c1) - len(c2)) <= 2:
            common = sum(1 for a, b in zip(sorted(c1), sorted(c2)) if a == b)
            if common >= min(len(c1), len(c2)) * 0.7:
                return True
        
        return False


def get_smart_suggestions(transactions_df: pd.DataFrame, 
                          rules_df: pd.DataFrame,
                          budgets_df: pd.DataFrame,
                          members_df: pd.DataFrame) -> List[Suggestion]:
    """
    Get intelligent suggestions based on data analysis.
    
    Args:
        transactions_df: All transactions
        rules_df: Learning rules
        budgets_df: Budget definitions
        members_df: Members list
        
    Returns:
        List of Suggestion objects sorted by impact
    """
    engine = SmartSuggestionEngine(transactions_df, rules_df, budgets_df, members_df)
    return engine.analyze_all()


def get_suggestions_by_type(suggestions: List[Suggestion], 
                            suggestion_type: str) -> List[Suggestion]:
    """Filter suggestions by type."""
    return [s for s in suggestions if s.type == suggestion_type]


def get_suggestions_by_priority(suggestions: List[Suggestion], 
                                priority: str) -> List[Suggestion]:
    """Filter suggestions by priority."""
    return [s for s in suggestions if s.priority == priority]
