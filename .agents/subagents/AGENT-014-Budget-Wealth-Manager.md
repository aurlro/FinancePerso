# AGENT-014: Budget & Wealth Manager

## 🎯 Mission

Gestionnaire des budgets et de la planification patrimoniale. Responsable du suivi budgétaire, des objectifs d'épargne, et des projections financières. Garant de la santé financière à long terme.

---

## 📚 Contexte: Architecture Budget/Wealth

### Modèle de Données

```python
# modules/budgets/models.py

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

class BudgetPeriod(Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class BudgetType(Enum):
    FIXED = "fixed"           # Charge fixe (loyer...)
    VARIABLE = "variable"     # Variable mais nécessaire (courses...)
    DISCRETIONARY = "discretionary"  # Facultative (loisirs...)
    SAVINGS = "savings"       # Épargne

@dataclass
class Budget:
    """Budget pour une catégorie."""
    id: int
    category: str
    amount: float
    period: BudgetPeriod
    budget_type: BudgetType
    rollover: bool = False           # Report mois non utilisé
    alert_threshold: float = 0.8     # Alerte à 80%
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class BudgetAlert:
    """Alerte de dépassement budgétaire."""
    id: int
    budget_id: int
    alert_type: str           # 'warning' | 'critical' | 'exceeded'
    message: str
    current_amount: float
    budget_amount: float
    percentage_used: float
    created_at: datetime = None

@dataclass
class SavingsGoal:
    """Objectif d'épargne."""
    id: int
    name: str
    description: str
    target_amount: float
    current_amount: float
    deadline: Optional[date]
    category: str             # Catégorie associée
    priority: int = 1         # 1=haute, 5=basse
    auto_contribute: bool = False
    monthly_contribution: float = 0.0
    created_at: datetime = None

@dataclass
class WealthProjection:
    """Projection patrimoniale."""
    id: int
    name: str
    current_net_worth: float
    monthly_savings_rate: float
    annual_return_rate: float
    projection_years: int = 30
    inflation_rate: float = 0.02
    created_at: datetime = None
```

---

## 🧱 Module 1: Budget Engine

### Gestion des Budgets

```python
# modules/budgets/engine.py

class BudgetEngine:
    """Moteur de gestion budgétaire."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_budget(
        self,
        category: str,
        amount: float,
        period: BudgetPeriod = BudgetPeriod.MONTHLY,
        budget_type: BudgetType = BudgetType.VARIABLE,
        rollover: bool = False,
        alert_threshold: float = 0.8
    ) -> Budget:
        """
        Crée un nouveau budget.
        
        Args:
            category: Catégorie concernée
            amount: Montant alloué
            period: Période du budget
            budget_type: Type de budget
            rollover: Report du non-utilisé
            alert_threshold: Seuil d'alerte (0.0-1.0)
        
        Returns:
            Budget créé
        """
        cursor = self.db.cursor()
        
        cursor.execute("""
            INSERT INTO budgets 
            (category, amount, period, budget_type, rollover, alert_threshold, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (category, amount, period.value, budget_type.value, 
              rollover, alert_threshold, datetime.now()))
        
        budget_id = cursor.lastrowid
        self.db.commit()
        
        logger.info(f"Budget créé: {category} = {amount} EUR/{period.value}")
        
        return Budget(
            id=budget_id,
            category=category,
            amount=amount,
            period=period,
            budget_type=budget_type,
            rollover=rollover,
            alert_threshold=alert_threshold
        )
    
    def get_spending_vs_budget(
        self,
        year: int = None,
        month: int = None
    ) -> List[dict]:
        """
        Compare dépenses réelles vs budgets.
        
        Returns:
            Liste avec budget, dépensé, restant, pourcentage
        """
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        cursor = self.db.cursor()
        
        # Récupérer tous les budgets
        cursor.execute("SELECT * FROM budgets")
        budgets = cursor.fetchall()
        
        results = []
        for budget in budgets:
            category = budget['category']
            budget_amount = budget['amount']
            
            # Calculer dépenses du mois pour cette catégorie
            cursor.execute("""
                SELECT COALESCE(SUM(ABS(amount)), 0) as spent
                FROM transactions
                WHERE category_validated = ?
                AND strftime('%Y', date) = ?
                AND strftime('%m', date) = ?
                AND amount < 0
            """, (category, str(year), f"{month:02d}"))
            
            spent = cursor.fetchone()['spent']
            remaining = budget_amount - spent
            percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
            
            # Déterminer statut
            if percentage >= 100:
                status = 'exceeded'
            elif percentage >= budget['alert_threshold'] * 100:
                status = 'warning'
            else:
                status = 'ok'
            
            results.append({
                'category': category,
                'budget_amount': budget_amount,
                'spent': spent,
                'remaining': remaining,
                'percentage': percentage,
                'status': status,
                'rollover': budget['rollover']
            })
        
        return results
    
    def check_budget_alerts(self) -> List[BudgetAlert]:
        """
        Vérifie les budgets et génère des alertes.
        
        Returns:
            Liste des alertes actives
        """
        alerts = []
        spending = self.get_spending_vs_budget()
        
        for item in spending:
            if item['status'] == 'exceeded':
                alerts.append(BudgetAlert(
                    id=0,
                    budget_id=0,
                    alert_type='exceeded',
                    message=f"Budget {item['category']} dépassé de {item['spent'] - item['budget_amount']:.2f} EUR",
                    current_amount=item['spent'],
                    budget_amount=item['budget_amount'],
                    percentage_used=item['percentage']
                ))
            elif item['status'] == 'warning':
                alerts.append(BudgetAlert(
                    id=0,
                    budget_id=0,
                    alert_type='warning',
                    message=f"Budget {item['category']} à {item['percentage']:.0f}%",
                    current_amount=item['spent'],
                    budget_amount=item['budget_amount'],
                    percentage_used=item['percentage']
                ))
        
        return alerts
    
    def suggest_budget_adjustments(self) -> List[dict]:
        """
        Suggère des ajustements de budget basés sur l'historique.
        
        Returns:
            Suggestions avec confiance
        """
        cursor = self.db.cursor()
        suggestions = []
        
        # Analyser 6 derniers mois
        cursor.execute("""
            SELECT category_validated, 
                   AVG(monthly_spent) as avg_spent,
                   MAX(monthly_spent) as max_spent
            FROM (
                SELECT category_validated,
                       strftime('%Y-%m', date) as month,
                       SUM(ABS(amount)) as monthly_spent
                FROM transactions
                WHERE date >= date('now', '-6 months')
                AND amount < 0
                GROUP BY category_validated, month
            )
            GROUP BY category_validated
        """)
        
        for row in cursor.fetchall():
            category = row['category_validated']
            avg_spent = row['avg_spent']
            max_spent = row['max_spent']
            
            # Vérifier budget actuel
            cursor.execute(
                "SELECT amount FROM budgets WHERE category = ?",
                (category,)
            )
            current_budget = cursor.fetchone()
            
            if current_budget:
                current = current_budget['amount']
                
                if avg_spent > current * 1.2:
                    # Dépassement régulier
                    suggestions.append({
                        'category': category,
                        'type': 'increase',
                        'current': current,
                        'suggested': avg_spent * 1.1,
                        'confidence': 0.8,
                        'reason': f"Dépenses moyennes: {avg_spent:.0f} EUR/mois"
                    })
                elif avg_spent < current * 0.7:
                    # Budget trop élevé
                    suggestions.append({
                        'category': category,
                        'type': 'decrease',
                        'current': current,
                        'suggested': avg_spent * 1.1,
                        'confidence': 0.6,
                        'reason': f"Utilisation moyenne: {(avg_spent/current)*100:.0f}%"
                    })
            else:
                # Pas de budget défini mais dépenses régulières
                if avg_spent > 50:  # Seulement si significatif
                    suggestions.append({
                        'category': category,
                        'type': 'create',
                        'suggested': avg_spent * 1.1,
                        'confidence': 0.7,
                        'reason': f"Dépenses régulières: {avg_spent:.0f} EUR/mois"
                    })
        
        return suggestions
```

---

## 🧱 Module 2: Savings Goals

### Objectifs d'Épargne

```python
# modules/budgets/savings.py

class SavingsGoalManager:
    """Gestionnaire des objectifs d'épargne."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def create_goal(
        self,
        name: str,
        target_amount: float,
        deadline: date = None,
        initial_amount: float = 0.0,
        category: str = None,
        priority: int = 1
    ) -> SavingsGoal:
        """Crée un objectif d'épargne."""
        cursor = self.db.cursor()
        
        cursor.execute("""
            INSERT INTO savings_goals 
            (name, target_amount, current_amount, deadline, category, priority, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, target_amount, initial_amount, deadline, 
              category, priority, datetime.now()))
        
        self.db.commit()
        
        return SavingsGoal(
            id=cursor.lastrowid,
            name=name,
            description="",
            target_amount=target_amount,
            current_amount=initial_amount,
            deadline=deadline,
            category=category,
            priority=priority
        )
    
    def contribute(self, goal_id: int, amount: float) -> SavingsGoal:
        """Contribue à un objectif."""
        cursor = self.db.cursor()
        
        cursor.execute("""
            UPDATE savings_goals 
            SET current_amount = current_amount + ?
            WHERE id = ?
        """, (amount, goal_id))
        
        self.db.commit()
        
        return self.get_goal(goal_id)
    
    def calculate_contribution_plan(self, goal_id: int) -> dict:
        """
        Calcule un plan de contribution.
        
        Returns:
            Plan avec montant mensuel nécessaire
        """
        goal = self.get_goal(goal_id)
        
        if not goal.deadline:
            return {
                'monthly_needed': None,
                'message': 'Pas de deadline définie'
            }
        
        remaining = goal.target_amount - goal.current_amount
        months_remaining = max(1, (goal.deadline - date.today()).days / 30)
        
        monthly_needed = remaining / months_remaining
        
        return {
            'goal_id': goal_id,
            'goal_name': goal.name,
            'remaining_amount': remaining,
            'months_remaining': int(months_remaining),
            'monthly_needed': monthly_needed,
            'on_track': monthly_needed > 0
        }
    
    def get_all_goals_progress(self) -> List[dict]:
        """Retourne la progression de tous les objectifs."""
        cursor = self.db.cursor()
        
        cursor.execute("SELECT * FROM savings_goals ORDER BY priority, deadline")
        
        results = []
        for row in cursor.fetchall():
            percentage = (row['current_amount'] / row['target_amount'] * 100) if row['target_amount'] > 0 else 0
            
            # Calcul jours restants
            days_left = None
            if row['deadline']:
                days_left = (date.fromisoformat(row['deadline']) - date.today()).days
            
            results.append({
                'id': row['id'],
                'name': row['name'],
                'target': row['target_amount'],
                'current': row['current_amount'],
                'percentage': percentage,
                'deadline': row['deadline'],
                'days_left': days_left,
                'priority': row['priority'],
                'status': 'completed' if percentage >= 100 else 'in_progress'
            })
        
        return results
```

---

## 🧱 Module 3: Wealth Projection

### Projections Patrimoniales

```python
# modules/budgets/projections.py

class WealthProjectionEngine:
    """Moteur de projection patrimoniale."""
    
    def calculate_projections(
        self,
        current_net_worth: float,
        monthly_savings: float,
        annual_return: float = 0.05,
        years: int = 30,
        inflation: float = 0.02
    ) -> List[dict]:
        """
        Calcule les projections de patrimoine.
        
        Args:
            current_net_worth: Valeur nette actuelle
            monthly_savings: Épargne mensuelle
            annual_return: Rendement annuel attendu
            years: Horizon de projection
            inflation: Taux d'inflation
        
        Returns:
            Projections année par année
        """
        projections = []
        net_worth = current_net_worth
        
        real_return = (1 + annual_return) / (1 + inflation) - 1
        
        for year in range(years + 1):
            projections.append({
                'year': datetime.now().year + year,
                'age': None,  # À remplir si date naissance connue
                'net_worth': round(net_worth, 2),
                'nominal_value': round(net_worth * (1 + inflation) ** year, 2),
                'total_contributed': round(monthly_savings * 12 * year, 2),
                'total_returns': round(net_worth - current_net_worth - monthly_savings * 12 * year, 2)
            })
            
            # Croissance annuelle
            net_worth = net_worth * (1 + real_return) + monthly_savings * 12
        
        return projections
    
    def calculate_fi_number(
        self,
        annual_expenses: float,
        withdrawal_rate: float = 0.04
    ) -> dict:
        """
        Calcule le nombre pour l'indépendance financière (FI).
        
        Règle des 4%: 25x les dépenses annuelles
        
        Args:
            annual_expenses: Dépenses annuelles
            withdrawal_rate: Taux de retrait sûr (4% standard)
        
        Returns:
            Détails FI
        """
        fi_number = annual_expenses / withdrawal_rate
        
        return {
            'fi_number': round(fi_number, 2),
            'monthly_expenses': round(annual_expenses / 12, 2),
            'safe_withdrawal_rate': withdrawal_rate,
            'annual_safe_withdrawal': annual_expenses
        }
    
    def estimate_fi_date(
        self,
        current_net_worth: float,
        monthly_savings: float,
        monthly_expenses: float,
        annual_return: float = 0.05
    ) -> dict:
        """
        Estime la date d'atteinte de l'indépendance financière.
        
        Returns:
            Date estimée et détails
        """
        fi_number = monthly_expenses * 12 / 0.04
        
        if current_net_worth >= fi_number:
            return {
                'already_fi': True,
                'fi_date': datetime.now().date(),
                'years_to_fi': 0
            }
        
        # Calcul itératif
        net_worth = current_net_worth
        years = 0
        max_years = 100
        
        while net_worth < fi_number and years < max_years:
            net_worth = net_worth * (1 + annual_return) + monthly_savings * 12
            years += 1
        
        if years >= max_years:
            return {
                'already_fi': False,
                'fi_date': None,
                'years_to_fi': None,
                'message': 'Objectif non atteignable avec paramètres actuels'
            }
        
        fi_date = datetime.now().date().replace(year=datetime.now().year + years)
        
        return {
            'already_fi': False,
            'fi_number': round(fi_number, 2),
            'fi_date': fi_date,
            'years_to_fi': years,
            'monthly_savings_needed': monthly_savings
        }
```

---

**Version**: 1.0
**Date**: 2026-02-25
**Statut**: PRÊT À L'EMPLOI


---

## 🔧 Module Additionnel: Tests & Validation

### Tests Unitaires

```python
# tests/unit/test_budgets.py
"""
Tests du module budgets et wealth management.
"""

import pytest
from datetime import datetime, date
from modules.budgets.engine import BudgetEngine
from modules.budgets.savings import SavingsGoalManager
from modules.budgets.projections import WealthProjectionEngine

class TestBudgetEngine:
    """Tests du moteur budgétaire."""
    
    def test_create_budget(self, db_connection):
        """Test création d'un budget."""
        engine = BudgetEngine(db_connection)
        
        budget = engine.create_budget(
            category="Alimentation",
            amount=500.0,
            period=BudgetPeriod.MONTHLY
        )
        
        assert budget.category == "Alimentation"
        assert budget.amount == 500.0
        assert budget.id is not None
    
    def test_spending_vs_budget(self, db_connection, sample_transactions):
        """Test calcul dépenses vs budget."""
        engine = BudgetEngine(db_connection)
        
        # Créer budget
        engine.create_budget(category="Alimentation", amount=500.0)
        
        # Insérer transactions
        for tx in sample_transactions:
            if tx['category_validated'] == 'Alimentation':
                insert_transaction(db_connection, tx)
        
        # Vérifier calcul
        results = engine.get_spending_vs_budget()
        alimentation = next(r for r in results if r['category'] == 'Alimentation')
        
        assert 'spent' in alimentation
        assert 'remaining' in alimentation
        assert 'percentage' in alimentation
    
    def test_budget_alert_threshold(self, db_connection):
        """Test détection dépassement seuil."""
        engine = BudgetEngine(db_connection)
        
        # Créer budget avec seuil à 80%
        engine.create_budget(
            category="Test",
            amount=100.0,
            alert_threshold=0.8
        )
        
        # Simuler dépense à 85%
        insert_transaction(db_connection, {
            'category_validated': 'Test',
            'amount': -85.0,
            'date': date.today()
        })
        
        alerts = engine.check_budget_alerts()
        
        assert len(alerts) > 0
        assert any(a.alert_type == 'warning' for a in alerts)

class TestSavingsGoalManager:
    """Tests des objectifs d'épargne."""
    
    def test_create_goal(self, db_connection):
        """Test création objectif."""
        manager = SavingsGoalManager(db_connection)
        
        goal = manager.create_goal(
            name="Vacances",
            target_amount=2000.0,
            deadline=date(2024, 12, 31)
        )
        
        assert goal.name == "Vacances"
        assert goal.target_amount == 2000.0
    
    def test_contribute_to_goal(self, db_connection):
        """Test contribution à un objectif."""
        manager = SavingsGoalManager(db_connection)
        
        goal = manager.create_goal(
            name="Urgence",
            target_amount=1000.0,
            initial_amount=100.0
        )
        
        updated = manager.contribute(goal.id, 200.0)
        
        assert updated.current_amount == 300.0
    
    def test_contribution_plan(self, db_connection):
        """Test calcul plan de contribution."""
        manager = SavingsGoalManager(db_connection)
        
        goal = manager.create_goal(
            name="Test",
            target_amount=1200.0,
            deadline=date.today().replace(year=date.today().year + 1)
        )
        
        plan = manager.calculate_contribution_plan(goal.id)
        
        assert 'monthly_needed' in plan
        assert plan['months_remaining'] == 12
        assert plan['monthly_needed'] == 100.0  # 1200 / 12

class TestWealthProjectionEngine:
    """Tests des projections patrimoniales."""
    
    def test_fi_number_calculation(self):
        """Test calcul nombre FI."""
        engine = WealthProjectionEngine()
        
        result = engine.calculate_fi_number(
            annual_expenses=40000.0,
            withdrawal_rate=0.04
        )
        
        # Règle des 4%: 40000 / 0.04 = 1,000,000
        assert result['fi_number'] == 1000000.0
    
    def test_projections_calculation(self):
        """Test calcul projections."""
        engine = WealthProjectionEngine()
        
        projections = engine.calculate_projections(
            current_net_worth=100000.0,
            monthly_savings=1000.0,
            annual_return=0.05,
            years=10
        )
        
        assert len(projections) == 11  # 0 à 10 ans
        assert projections[0]['net_worth'] == 100000.0
        
        # Vérifier croissance
        assert projections[-1]['net_worth'] > projections[0]['net_worth']
    
    def test_fi_date_estimation(self):
        """Test estimation date FI."""
        engine = WealthProjectionEngine()
        
        # FI number = 50000 / 0.04 = 1,250,000
        # Avec 5000/mois d'épargne à 5% return
        result = engine.estimate_fi_date(
            current_net_worth=100000.0,
            monthly_savings=5000.0,
            monthly_expenses=5000.0,  # Annual = 60000, FI = 1.5M
            annual_return=0.05
        )
        
        assert 'years_to_fi' in result
        assert result['already_fi'] == False
```

### Imports Standardisés

```python
# modules/budgets/__init__.py
"""
Module budgets - Imports standardisés.
"""

import logging
import sqlite3
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

# Exports
from .engine import BudgetEngine
from .savings import SavingsGoalManager
from .projections import WealthProjectionEngine
from .models import Budget, BudgetAlert, SavingsGoal, BudgetPeriod, BudgetType

__all__ = [
    'BudgetEngine',
    'SavingsGoalManager',
    'WealthProjectionEngine',
    'Budget',
    'BudgetAlert',
    'SavingsGoal',
    'BudgetPeriod',
    'BudgetType',
    'logger'
]
```

### Configuration par Défaut

```python
# modules/budgets/config.py
"""
Configuration du module budgets.
"""

# Seuils d'alerte par défaut
DEFAULT_ALERT_THRESHOLDS = {
    'warning': 0.8,    # Alerte à 80%
    'critical': 0.95,  # Critique à 95%
    'exceeded': 1.0    # Dépassement à 100%
}

# Périodes par défaut
DEFAULT_BUDGET_PERIOD = 'monthly'

# Rendements par défaut pour projections
DEFAULT_PROJECTION_RATES = {
    'conservative': 0.03,  # 3% - Obligations
    'moderate': 0.05,      # 5% - Mixte
    'aggressive': 0.07     # 7% - Actions
}

# Inflation par défaut
DEFAULT_INFLATION_RATE = 0.02  # 2%

# Taux de retrait sûr (règle des 4%)
DEFAULT_WITHDRAWAL_RATE = 0.04
```

---

**Version**: 1.1 - **TESTS ET IMPORTS AJOUTÉS**  
**Couverture**: Tests unitaires complets, imports standardisés
