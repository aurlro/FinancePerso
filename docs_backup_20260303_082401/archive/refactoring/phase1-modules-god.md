# Phase 1 : Découpage des Modules God

## Module 1: update_manager.py (531 lignes)

### Analyse

```python
# Structure actuelle
class UpdateManager:
    # Attributs (20 lignes)
    # __init__ (30 lignes)
    
    # Méthodes d'analyse Git (149 lignes)
    analyze_git_changes()
    _get_git_diff()
    _parse_diff()
    
    # Méthodes de création d'update (78 lignes)
    create_update()
    _build_summary()
    _categorize_changes()
    
    # Méthodes de version (45 lignes)
    bump_version()
    get_current_version()
    
    # Méthodes de changelog (89 lignes)
    update_changelog()
    parse_changelog()
    _format_entry()
```

### Structure cible

```
modules/update/                    # Nouveau package
├── __init__.py                    # Exports publics
├── models.py                      # Dataclasses
├── analyzer.py                    # Git analysis
├── creator.py                     # Update creation
├── version.py                     # Version management
├── changelog.py                   # Changelog operations
└── manager.py                     # Facade (classe legacy allégée)
```

### Implémentation

#### 1. models.py

```python
"""Data models for update management."""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class GitChange:
    """Represents a single git change."""
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    additions: int
    deletions: int
    diff_content: Optional[str] = None


@dataclass
class CategorizedChanges:
    """Changes grouped by category."""
    features: List[GitChange]
    fixes: List[GitChange]
    docs: List[GitChange]
    refactors: List[GitChange]
    tests: List[GitChange]
    other: List[GitChange]


@dataclass
class UpdateSummary:
    """Summary of an update."""
    version: str
    date: datetime
    title: str
    description: str
    changes: CategorizedChanges
    author: Optional[str] = None
```

#### 2. analyzer.py

```python
"""Git analysis module."""
import subprocess
import re
from typing import List, Optional
from pathlib import Path

from modules.update.models import GitChange


class GitAnalyzer:
    """Analyzes git repository for changes."""
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
    
    def analyze_changes(self, since_ref: Optional[str] = None) -> List[GitChange]:
        """
        Analyze git changes since a reference.
        
        Args:
            since_ref: Git ref to compare against (default: last tag)
            
        Returns:
            List of GitChange objects
        """
        ref = since_ref or self._get_last_tag()
        diff_output = self._get_git_diff(ref)
        return self._parse_diff(diff_output)
    
    def _get_last_tag(self) -> str:
        """Get the most recent git tag."""
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
        if result.returncode != 0:
            return "HEAD~10"  # Fallback
        return result.stdout.strip()
    
    def _get_git_diff(self, ref: str) -> str:
        """Get raw git diff output."""
        result = subprocess.run(
            ["git", "diff", ref, "HEAD", "--stat", "--numstat"],
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
        return result.stdout
    
    def _parse_diff(self, diff_output: str) -> List[GitChange]:
        """Parse git diff output into GitChange objects."""
        changes = []
        for line in diff_output.strip().split('\n'):
            if not line or line.startswith('-'):
                continue
            match = re.match(r'^(\d+)\s+(\d+)\s+(.+)$', line)
            if match:
                additions = int(match.group(1))
                deletions = int(match.group(2))
                file_path = match.group(3)
                
                change_type = self._classify_change(additions, deletions)
                
                changes.append(GitChange(
                    file_path=file_path,
                    change_type=change_type,
                    additions=additions,
                    deletions=deletions
                ))
        return changes
    
    def _classify_change(self, additions: int, deletions: int) -> str:
        """Classify change type based on additions/deletions."""
        if additions > 0 and deletions == 0:
            return 'added'
        elif additions == 0 and deletions > 0:
            return 'deleted'
        else:
            return 'modified'
```

#### 3. creator.py

```python
"""Update creation module."""
from typing import List
from datetime import datetime

from modules.update.models import GitChange, CategorizedChanges, UpdateSummary
from modules.logger import logger


class UpdateCreator:
    """Creates update summaries from git changes."""
    
    # Patterns pour catégoriser les commits/fichiers
    FEATURE_PATTERNS = ['feat:', 'feature:', 'add:', 'new:']
    FIX_PATTERNS = ['fix:', 'bugfix:', 'hotfix:', 'correct:']
    DOC_PATTERNS = ['doc:', 'docs:', 'readme:', 'comment:']
    TEST_PATTERNS = ['test:', 'tests:', 'spec:']
    REFACTOR_PATTERNS = ['refactor:', 'clean:', 'rework:', 'optimize:']
    
    def create_update(
        self,
        changes: List[GitChange],
        version: str,
        title: Optional[str] = None
    ) -> UpdateSummary:
        """
        Create an update summary from git changes.
        
        Args:
            changes: List of git changes
            version: Target version
            title: Optional update title
            
        Returns:
            UpdateSummary object
        """
        categorized = self._categorize_changes(changes)
        
        summary_title = title or self._build_title(categorized)
        description = self._build_description(categorized)
        
        return UpdateSummary(
            version=version,
            date=datetime.now(),
            title=summary_title,
            description=description,
            changes=categorized
        )
    
    def _categorize_changes(self, changes: List[GitChange]) -> CategorizedChanges:
        """Categorize changes by type."""
        result = CategorizedChanges(
            features=[], fixes=[], docs=[],
            refactors=[], tests=[], other=[]
        )
        
        for change in changes:
            category = self._determine_category(change.file_path)
            
            if category == 'feature':
                result.features.append(change)
            elif category == 'fix':
                result.fixes.append(change)
            elif category == 'doc':
                result.docs.append(change)
            elif category == 'test':
                result.tests.append(change)
            elif category == 'refactor':
                result.refactors.append(change)
            else:
                result.other.append(change)
        
        return result
    
    def _determine_category(self, file_path: str) -> str:
        """Determine category from file path or name."""
        lower_path = file_path.lower()
        
        if any(p in lower_path for p in ['test', 'spec']):
            return 'test'
        elif any(p in lower_path for p in ['doc', 'readme', '.md']):
            return 'doc'
        elif any(p in lower_path for p in ['refactor', 'clean']):
            return 'refactor'
        # ... etc
        
        return 'other'
    
    def _build_title(self, categorized: CategorizedChanges) -> str:
        """Build auto-title from changes."""
        if categorized.features:
            return f"Add {len(categorized.features)} new features"
        elif categorized.fixes:
            return f"Fix {len(categorized.fixes)} issues"
        else:
            return "Update dependencies and documentation"
    
    def _build_description(self, categorized: CategorizedChanges) -> str:
        """Build markdown description."""
        lines = []
        
        if categorized.features:
            lines.append("### 🚀 Features")
            for change in categorized.features[:5]:
                lines.append(f"- {change.file_path}")
        
        if categorized.fixes:
            lines.append("### 🐛 Fixes")
            for change in categorized.fixes[:5]:
                lines.append(f"- {change.file_path}")
        
        # ... etc
        
        return '\n'.join(lines)
```

#### 4. manager.py (Facade)

```python
"""UpdateManager - Facade allégée pour compatibilité."""
from typing import Optional

from modules.update.analyzer import GitAnalyzer
from modules.update.creator import UpdateCreator
from modules.update.version import VersionManager
from modules.update.changelog import ChangelogManager
from modules.update.models import UpdateSummary


class UpdateManager:
    """
    Facade pour la gestion des updates.
    
    Délegue à des modules spécialisés:
    - GitAnalyzer: Analyse git
    - UpdateCreator: Création de résumés
    - VersionManager: Gestion des versions
    - ChangelogManager: Gestion du changelog
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        self._analyzer = GitAnalyzer(repo_path)
        self._creator = UpdateCreator()
        self._version = VersionManager(repo_path)
        self._changelog = ChangelogManager(repo_path)
    
    def analyze_git_changes(self, since_ref: Optional[str] = None):
        """Analyze git changes."""
        return self._analyzer.analyze_changes(since_ref)
    
    def create_update(self, version: str, title: Optional[str] = None):
        """Create update summary."""
        changes = self._analyzer.analyze_changes()
        return self._creator.create_update(changes, version, title)
    
    def bump_version(self, bump_type: str = 'patch'):
        """Bump version."""
        return self._version.bump(bump_type)
    
    def update_changelog(self, update: UpdateSummary):
        """Update changelog."""
        return self._changelog.add_entry(update)
```

---

## Module 2: smart_suggestions.py (873 lignes)

### Analyse

```python
class SmartSuggestionEngine:
    # 16 types d'analyses différentes!
    
    analyze_budget_overrun()      # Budget
    analyze_trend_anomaly()       # Tendances
    analyze_savings_opportunity() # Épargne
    analyze_duplicate_risk()      # Doublons
    analyze_category_inconsistency()  # Catégories
    analyze_monthly_pattern()     # Patterns
    analyze_weekly_spike()        # Dépenses
    analyze_recurring_missed()    # Récurrences
    # ... et 8 autres
```

### Structure cible

```
ai/analyzers/                      # Nouveau package
├── __init__.py
├── base.py                        # Classe de base
├── models.py                      # Dataclasses résultats
├── budget/
│   ├── __init__.py
│   ├── overrun.py                 # Budget overrun
│   └── forecast.py                # Budget forecast
├── trends/
│   ├── __init__.py
│   ├── anomalies.py               # Trend anomalies
│   └── patterns.py                # Pattern detection
├── savings/
│   ├── __init__.py
│   ├── opportunities.py           # Savings opportunities
│   └── goals.py                   # Goals tracking
├── duplicates/
│   ├── __init__.py
│   └── detector.py                # Duplicate detection
├── categories/
│   ├── __init__.py
│   └── inconsistency.py           # Category issues
└── engine.py                      # Orchestrateur
```

### Implémentation

#### 1. base.py

```python
"""Base class for all analyzers."""
from abc import ABC, abstractmethod
from typing import Any, Dict
import pandas as pd


class BaseAnalyzer(ABC):
    """Base class for financial analyzers."""
    
    name: str = "base"
    description: str = "Base analyzer"
    
    def __init__(self, df: pd.DataFrame, config: Dict[str, Any] = None):
        self.df = df
        self.config = config or {}
    
    @abstractmethod
    def analyze(self) -> 'AnalysisResult':
        """Run analysis and return results."""
        pass
    
    def validate_data(self) -> bool:
        """Validate input data. Override if needed."""
        return self.df is not None and not self.df.empty


@dataclass
class AnalysisResult:
    """Result of an analysis."""
    analyzer: str
    priority: str  # 'high', 'medium', 'low'
    title: str
    description: str
    details: Dict[str, Any]
    action_items: List[str]
```

#### 2. Exemple: budget/overrun.py

```python
"""Budget overrun analyzer."""
from datetime import datetime
from typing import List

import pandas as pd

from ai.analyzers.base import BaseAnalyzer, AnalysisResult
from modules.db.budgets import get_budgets_dict


class BudgetOverrunAnalyzer(BaseAnalyzer):
    """Analyzes budget overruns."""
    
    name = "budget_overrun"
    description = "Detects budget overruns by category"
    
    def analyze(self) -> AnalysisResult:
        """Analyze budget overruns."""
        if not self.validate_data():
            return AnalysisResult(
                analyzer=self.name,
                priority='low',
                title="Pas assez de données",
                description="Ajoutez des transactions pour voir les analyses.",
                details={},
                action_items=[]
            )
        
        budgets = get_budgets_dict()
        overruns = self._detect_overruns(budgets)
        
        if not overruns:
            return AnalysisResult(
                analyzer=self.name,
                priority='low',
                title="✅ Budgets respectés",
                description="Aucun dépassement de budget détecté.",
                details={'overruns': []},
                action_items=[]
            )
        
        # Build result
        worst = max(overruns, key=lambda x: x['percentage'])
        
        return AnalysisResult(
            analyzer=self.name,
            priority='high' if worst['percentage'] > 150 else 'medium',
            title=f"🔥 Dépassement: {worst['category']}",
            description=f"{worst['category']}: {worst['spent']:.0f}€ / {worst['budget']:.0f}€",
            details={'overruns': overruns},
            action_items=[
                f"Réduire les dépenses en {worst['category']}",
                "Vérifier les transactions récurrentes"
            ]
        )
    
    def _detect_overruns(self, budgets: dict) -> List[dict]:
        """Detect budget overruns."""
        overruns = []
        
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        month_df = self.df[
            (self.df['date'].dt.month == current_month) &
            (self.df['date'].dt.year == current_year)
        ]
        
        for category, budget_amount in budgets.items():
            if budget_amount <= 0:
                continue
            
            spent = month_df[
                month_df['category_validated'] == category
            ]['amount'].sum()
            
            if abs(spent) > budget_amount:
                overruns.append({
                    'category': category,
                    'budget': budget_amount,
                    'spent': abs(spent),
                    'percentage': (abs(spent) / budget_amount) * 100
                })
        
        return sorted(overruns, key=lambda x: x['percentage'], reverse=True)
```

#### 3. engine.py

```python
"""Smart Suggestion Engine - Orchestrateur."""
from typing import List, Type
import pandas as pd

from ai.analyzers.base import BaseAnalyzer, AnalysisResult
# Import tous les analyzers
from ai.analyzers.budget.overrun import BudgetOverrunAnalyzer
from ai.analyzers.budget.forecast import BudgetForecastAnalyzer
from ai.analyzers.trends.anomalies import TrendAnomalyAnalyzer
from ai.analyzers.savings.opportunities import SavingsOpportunityAnalyzer
from ai.analyzers.duplicates.detector import DuplicateDetector
# ... etc


class SmartSuggestionEngine:
    """
    Engine that runs all analyzers and returns prioritized suggestions.
    """
    
    # Registry of available analyzers
    ANALYZERS: List[Type[BaseAnalyzer]] = [
        BudgetOverrunAnalyzer,
        BudgetForecastAnalyzer,
        TrendAnomalyAnalyzer,
        SavingsOpportunityAnalyzer,
        DuplicateDetector,
        # ... etc
    ]
    
    def __init__(self, df: pd.DataFrame, config: dict = None):
        self.df = df
        self.config = config or {}
    
    def analyze(self, analyzer_names: List[str] = None) -> List[AnalysisResult]:
        """
        Run analysis with specified analyzers (or all).
        
        Args:
            analyzer_names: List of analyzer names to run (None = all)
            
        Returns:
            List of AnalysisResult, sorted by priority
        """
        results = []
        
        for analyzer_class in self.ANALYZERS:
            # Skip if not in requested list
            if analyzer_names and analyzer_class.name not in analyzer_names:
                continue
            
            try:
                analyzer = analyzer_class(self.df, self.config)
                result = analyzer.analyze()
                results.append(result)
            except Exception as e:
                # Log error but continue with other analyzers
                from modules.logger import logger
                logger.error(f"Analyzer {analyzer_class.name} failed: {e}")
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        return sorted(results, key=lambda r: priority_order.get(r.priority, 3))
    
    def get_high_priority(self) -> List[AnalysisResult]:
        """Get only high priority suggestions."""
        return [r for r in self.analyze() if r.priority == 'high']
```

---

## Plan de migration

### Étape 1: Créer la structure (30 min)
```bash
mkdir -p modules/update/{analyzer,creator,version,changelog}
mkdir -p modules/ai/analyzers/{budget,trends,savings,duplicates,categories}
touch modules/update/__init__.py
```

### Étape 2: Migrer update_manager (3h)
```bash
# Créer les nouveaux fichiers
# Copier le code en extrayant méthode par méthode
# Vérifier que les tests passent à chaque étape
```

### Étape 3: Migrer smart_suggestions (4h)
```bash
# Créer BaseAnalyzer
# Migrer une analyse à la fois
# Tester individuellement
```

### Étape 4: Mise à jour imports (1h)
```bash
# Remplacer dans tous les fichiers:
sed -i '' 's/from modules.update_manager import/from modules.update.manager import/g'
sed -i '' 's/from modules.ai.smart_suggestions import/from modules.ai.analyzers.engine import/g'
```

---

## Estimation

| Module | Temps estimé | Risque |
|--------|-------------|--------|
| update_manager | 6h | Moyen (tests à préserver) |
| smart_suggestions | 8h | Moyen (logique complexe) |
| **Total Phase 1** | **14h** | **Moyen** |

---

**Priorité** : P0  
**Dépendances** : Résolution imports circulaires (recommandé avant)  
**Livrables** : Modules testés indépendamment
