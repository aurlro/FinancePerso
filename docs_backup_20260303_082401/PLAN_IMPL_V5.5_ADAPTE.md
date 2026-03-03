# 🎨 Plan d'implémentation V5.5 - ADAPTÉ au code existant

> Basé sur l'analyse du code actuel - Réutilisation maximale des composants existants

---

## 📊 Analyse de l'existant

### ✅ Ce qui existe déjà (très complet !)

| Composant | Fichier | Statut |
|-----------|---------|--------|
| **Design Tokens** | `modules/ui/tokens/` | ✅ Colors, Typography, Spacing, BorderRadius |
| **Boutons** | `modules/ui/atoms/button.py` | ✅ Primary, Secondary, Danger, Ghost |
| **Cartes** | `modules/ui/molecules/card.py` | ✅ Default, Metric, Action, Empty, Alert |
| **État vide** | `modules/ui/molecules/empty_state.py` | ✅ Avec icône + 2 boutons |
| **Métriques** | `modules/ui/molecules/metric.py` | ✅ Avec tendances |
| **Design System** | `modules/ui/design_system.py` | ✅ Thème Vibe (dark mode) |
| **Feedback** | `modules/ui/feedback.py` | ✅ Toasts, banners, dialogs |

### 🔄 Différences avec les maquettes

| Aspect | Existant | Maquette | Action |
|--------|----------|----------|--------|
| **Thème** | Dark mode (slate) | Light mode (blanc/gris) | Ajouter thème light |
| **Welcome** | EmptyState générique | Card centrée avec icône cercle | Nouveau composant |
| **KPI Cards** | Card.metric (dark) | Style light avec icônes | Variante light |
| **Header** | Standard Streamlit | "Bonjour, Alex 👋" | Nouveau composant |

---

## 🏗️ Architecture cible

```
modules/ui/v5_5/                      # Nouveau namespace (pour isolement)
├── __init__.py
├── theme.py                          # Thème light mode (extension tokens)
├── components/
│   ├── __init__.py
│   ├── welcome_card.py               # ⭐ NOUVEAU - Card centrée maquette
│   ├── kpi_card.py                   # ⭐ NOUVEAU - Variante light mode
│   └── dashboard_header.py           # ⭐ NOUVEAU - "Bonjour, Alex"
├── dashboard/
│   ├── __init__.py
│   ├── dashboard_v5.py               # Dashboard complet
│   └── kpi_grid.py                   # Grille 4 KPIs
└── welcome/
    ├── __init__.py
    └── welcome_screen.py             # Écran d'accueil conditionnel

# Réutilisation des composants existants :
# - modules/ui/atoms/button.py → Button.primary/secondary
# - modules/ui/molecules/card.py → Card (base)
# - modules/ui/tokens/ → Colors, Typography, Spacing
```

---

## 📋 Plan de déploiement par phase

---

## Phase 0: Fondations - Thème Light (2-3h)

### 0.1 Extension des tokens pour light mode
**Fichier:** `modules/ui/v5_5/theme.py`

```python
"""Thème Light Mode pour FinancePerso V5.5

Extension des tokens existants pour le style maquette (light mode).
"""

from modules.ui.tokens import Colors as BaseColors, Spacing, Typography, BorderRadius

class LightColors:
    """Palette light mode - Maquette V5.5"""
    # Primary (Emerald comme dans maquette)
    PRIMARY = "#10B981"           # Vert émeraude
    PRIMARY_LIGHT = "#D1FAE5"     # Vert très clair (fond icône)
    PRIMARY_DARK = "#059669"      # Vert foncé
    
    # Background
    BG_PAGE = "#F9FAFB"           # Gris très clair (fond page)
    BG_CARD = "#FFFFFF"           # Blanc (cards)
    BG_SECONDARY = "#F3F4F6"      # Gris clair
    
    # Text
    TEXT_PRIMARY = "#1F2937"      # Gris foncé (titres)
    TEXT_SECONDARY = "#6B7280"    # Gris moyen (sous-titres)
    TEXT_MUTED = "#9CA3AF"        # Gris clair (hint)
    
    # Bordures
    BORDER = "#E5E7EB"            # Gris clair
    BORDER_LIGHT = "#F3F4F6"      # Gris très clair
    
    # Variations (comme dans maquette)
    POSITIVE = "#10B981"          # Vert
    NEGATIVE = "#EF4444"          # Rouge
    WARNING = "#F59E0B"           # Orange
    INFO = "#3B82F6"              # Bleu

class ThemeV5:
    """Thème complet V5.5"""
    colors = LightColors
    spacing = Spacing
    typography = Typography
    radius = BorderRadius
```

### 0.2 Styles CSS globaux light
```python
def get_light_theme_css() -> str:
    """CSS pour le thème light mode."""
    return """
    <style>
    /* Override pour light mode */
    .stApp {
        background-color: #F9FAFB !important;
    }
    
    h1, h2, h3 {
        color: #1F2937 !important;
    }
    
    /* Cards light */
    .v5-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
    """
```

**Livrable:** Thème light mode fonctionnel, cohabitation possible avec dark mode

---

## Phase 1: Welcome Component (3-4h)

### 1.1 Composant WelcomeCard
**Fichier:** `modules/ui/v5_5/components/welcome_card.py`

**Réutilisation:**
- ✅ `Button.primary()` et `Button.secondary()` existants
- ✅ Tokens `Spacing`, `BorderRadius` existants
- ❌ Créer : Layout centré avec icône dans cercle

```python
"""Welcome Card - Composant d'accueil V5.5"""

import streamlit as st
from typing import Callable, Optional
from modules.ui.atoms import Button
from modules.ui.v5_5.theme import LightColors, Spacing, BorderRadius

class WelcomeCard:
    """Card d'accueil centrée selon maquette.
    
    Usage:
        WelcomeCard.render(
            on_primary=lambda: st.switch_page("pages/1_Opérations.py"),
            on_secondary=lambda: show_guide()
        )
    """
    
    @staticmethod
    def render(
        on_primary: Optional[Callable] = None,
        on_secondary: Optional[Callable] = None,
        user_name: Optional[str] = None,
    ) -> None:
        """Rend la card d'accueil centrée."""
        
        # Container centré avec max-width
        st.markdown("""
        <style>
        .welcome-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 60vh;
            padding: 2rem;
        }
        .welcome-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 3rem;
            text-align: center;
            max-width: 480px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }
        .welcome-icon-circle {
            width: 80px;
            height: 80px;
            background: #D1FAE5;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            margin: 0 auto 1.5rem;
        }
        .welcome-title {
            font-size: 2rem;
            font-weight: 600;
            color: #1F2937;
            margin-bottom: 0.5rem;
        }
        .welcome-subtitle {
            font-size: 1.125rem;
            color: #1F2937;
            margin-bottom: 0.5rem;
        }
        .welcome-description {
            font-size: 1rem;
            color: #6B7280;
            margin-bottom: 2rem;
            line-height: 1.5;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Structure HTML
        st.markdown(f"""
        <div class="welcome-container">
            <div class="welcome-card">
                <div class="welcome-icon-circle">💰</div>
                <div class="welcome-title">👋 Bonjour{f', {user_name}' if user_name else ''} !</div>
                <div class="welcome-subtitle">Bienvenue dans votre espace financier</div>
                <div class="welcome-description">
                    Commencez par importer vos relevés bancaires pour 
                    visualiser vos finances, suivre vos budgets et atteindre vos 
                    objectifs d'épargne.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Boutons (centrés, en dessous de la card)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if Button.primary(
                "▶️ Importer mes relevés",
                key="welcome_import",
                on_click=on_primary,
                use_container_width=True
            ):
                pass
            
            if Button.secondary(
                "📖 Voir le guide",
                key="welcome_guide",
                on_click=on_secondary,
                use_container_width=True
            ):
                pass
```

**Différences avec EmptyState existant:**
- EmptyState : fond dégradé, bordure dashed, icône simple
- WelcomeCard : fond blanc, ombre, icône dans cercle coloré, texte hiérarchisé

### 1.2 Écran Welcome complet
**Fichier:** `modules/ui/v5_5/welcome/welcome_screen.py`

```python
"""Écran d'accueil V5.5"""

import streamlit as st
from modules.ui.v5_5.components.welcome_card import WelcomeCard
from modules.db.transactions import get_transactions_count

def render_welcome_screen():
    """Affiche l'écran d'accueil ou redirige."""
    
    # Vérifier si données existent
    if get_transactions_count() > 0:
        st.switch_page("pages/3_Synthèse_v5.py")
        return
    
    # Afficher welcome
    WelcomeCard.render(
        on_primary=lambda: st.switch_page("pages/1_Opérations.py"),
        on_secondary=lambda: show_guide_modal()
    )

def show_guide_modal():
    """Affiche le guide d'onboarding."""
    with st.modal("Guide de démarrage"):
        st.markdown("""
        ### 📖 Comment importer vos relevés
        
        1. **Téléchargez votre relevé** au format CSV depuis votre banque
        2. **Importez-le** dans la page Opérations
        3. **Laissez l'IA catégoriser** automatiquement
        4. **Validez** les transactions proposées
        """)
```

**Livrable:** Welcome card fonctionnelle, navigation opérationnelle

---

## Phase 2: KPI Cards (4-5h)

### 2.1 Composant KPICard (style maquette)
**Fichier:** `modules/ui/v5_5/components/kpi_card.py`

**Réutilisation:**
- ✅ `Card.metric()` comme base
- ✅ Tokens existants
- ❌ Ajouter : icône dans coin, style light, variations

```python
"""KPI Card - Style maquette V5.5 (light mode)"""

import streamlit as st
from typing import Optional, Tuple
from dataclasses import dataclass
from modules.ui.tokens import Colors, Spacing, BorderRadius

@dataclass
class KPIData:
    """Données d'un KPI."""
    label: str
    value: str
    value_color: str  # "positive", "negative", "neutral"
    icon: str
    icon_bg: str      # Couleur fond icône
    variation: Optional[str] = None  # "+13.8%"
    variation_label: Optional[str] = None  # "vs Janvier 2026"

class KPICard:
    """Carte KPI style maquette (light mode)."""
    
    @staticmethod
    def render(kpi: KPIData) -> None:
        """Rend une carte KPI."""
        
        # Couleurs de valeur
        value_colors = {
            "positive": "#10B981",
            "negative": "#EF4444",
            "neutral": "#1F2937"
        }
        
        variation_arrow = "↑" if kpi.value_color == "positive" else "↓"
        
        st.markdown(f"""
        <style>
        .kpi-card {{
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 1.5rem;
            position: relative;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .kpi-card:hover {{
            border-color: #10B981;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.08);
            transform: translateY(-2px);
            transition: all 0.2s ease;
        }}
        .kpi-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        .kpi-label {{
            font-size: 0.875rem;
            color: #6B7280;
            font-weight: 500;
        }}
        .kpi-icon {{
            width: 40px;
            height: 40px;
            background: {kpi.icon_bg};
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
        }}
        .kpi-value {{
            font-size: 1.875rem;
            font-weight: 700;
            color: {value_colors.get(kpi.value_color, '#1F2937')};
            margin-bottom: 0.5rem;
        }}
        .kpi-variation {{
            font-size: 0.875rem;
            color: #6B7280;
        }}
        .kpi-variation-positive {{
            color: #10B981;
        }}
        .kpi-variation-negative {{
            color: #EF4444;
        }}
        </style>
        
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-label">{kpi.label}</span>
                <div class="kpi-icon">{kpi.icon}</div>
            </div>
            <div class="kpi-value">{kpi.value}</div>
            <div class="kpi-variation">
                <span class="kpi-variation-{kpi.value_color}">{variation_arrow} {kpi.variation}</span>
                <span>{kpi.variation_label or ''}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
```

### 2.2 Grille de KPIs
**Fichier:** `modules/ui/v5_5/dashboard/kpi_grid.py`

```python
"""Grille de KPIs - 4 colonnes"""

import streamlit as st
from typing import List
from modules.ui.v5_5.components.kpi_card import KPICard, KPIData

def render_kpi_grid(kpis: List[KPIData]) -> None:
    """Affiche une grille de 4 KPIs."""
    cols = st.columns(4)
    
    for idx, kpi in enumerate(kpis):
        with cols[idx]:
            KPICard.render(kpi)

def calculate_kpis(month: str) -> List[KPIData]:
    """Calcule les 4 KPIs principaux."""
    from modules.db.transactions import get_monthly_summary
    
    summary = get_monthly_summary(month)
    
    return [
        KPIData(
            label="Reste à vivre",
            value=f"{summary['remaining']:,.2f} €",
            value_color="positive" if summary['remaining'] > 0 else "negative",
            icon="💚",
            icon_bg="#DCFCE7",
            variation=f"{summary['remaining_variation']:.1f}%",
            variation_label=f"vs {summary['previous_month']}"
        ),
        KPIData(
            label="Dépenses",
            value=f"-{summary['expenses']:,.2f} €",
            value_color="negative",
            icon="💳",
            icon_bg="#FEE2E2",
            variation=f"{summary['expenses_variation']:.1f}%",
            variation_label=f"vs {summary['previous_month']}"
        ),
        KPIData(
            label="Revenus",
            value=f"{summary['income']:,.2f} €",
            value_color="positive",
            icon="📈",
            icon_bg="#DBEAFE",
            variation=f"{summary['income_variation']:.1f}%",
            variation_label=f"vs {summary['previous_month']}"
        ),
        KPIData(
            label="Épargne",
            value=f"{summary['savings']:,.2f} €",
            value_color="positive" if summary['savings'] > 0 else "neutral",
            icon="🎯",
            icon_bg="#F3E8FF",
            variation=None,
            variation_label="🎉 Premier versement !" if summary['savings'] > 0 else None
        ),
    ]
```

**Livrable:** KPI Cards fonctionnelles avec données réelles

---

## Phase 3: Dashboard complet (4-5h)

### 3.1 Header personnalisé
**Fichier:** `modules/ui/v5_5/components/dashboard_header.py`

```python
"""Header du dashboard V5.5"""

import streamlit as st
from datetime import datetime

def render_dashboard_header(user_name: str, month: str):
    """Header style maquette: 'Bonjour, Alex 👋'"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <h1 style="font-size: 2rem; font-weight: 600; color: #1F2937; margin-bottom: 0.5rem;">
            Bonjour, {user_name} 👋
        </h1>
        <p style="color: #6B7280; font-size: 1rem;">
            Voici le résumé de vos finances pour {month}
        </p>
        """, unsafe_allow_html=True)
    
    with col2:
        # Sélecteur de mois aligné à droite
        months = get_available_months()
        selected = st.selectbox(
            "Période",
            options=months,
            index=months.index(month) if month in months else 0,
            label_visibility="collapsed"
        )
        return selected
```

### 3.2 Dashboard complet
**Fichier:** `modules/ui/v5_5/dashboard/dashboard_v5.py`

```python
"""Dashboard V5.5 complet"""

import streamlit as st
from modules.ui.v5_5.components.dashboard_header import render_dashboard_header
from modules.ui.v5_5.dashboard.kpi_grid import render_kpi_grid, calculate_kpis
from modules.ui.v5_5.dashboard.empty_state import render_dashboard_empty
from modules.db.transactions import get_transactions_count

def render_dashboard_v5():
    """Dashboard principal V5.5."""
    
    # Vérifier si données
    if get_transactions_count() == 0:
        render_dashboard_empty()
        return
    
    # 1. Header
    user = get_current_user()
    current_month = get_current_month_name()
    selected_month = render_dashboard_header(user.name, current_month)
    
    # 2. Section Vue d'ensemble
    st.markdown("""
    <h2 style="font-size: 1.25rem; color: #1F2937; margin-top: 2rem; margin-bottom: 1rem;">
        📊 Vue d'ensemble
    </h2>
    """, unsafe_allow_html=True)
    
    # 3. KPIs
    kpis = calculate_kpis(selected_month)
    render_kpi_grid(kpis)
    
    # 4. Deux colonnes
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("#### 📊 Répartition des dépenses")
        render_expenses_chart(selected_month)
    
    with col_right:
        st.markdown("#### 📝 Transactions récentes")
        render_recent_transactions(limit=5)
```

### 3.3 Dashboard Empty State
**Fichier:** `modules/ui/v5_5/dashboard/empty_state.py`

```python
"""Dashboard empty state avec onboarding"""

import streamlit as st
from modules.ui.v5_5.components.dashboard_header import render_dashboard_header

def render_dashboard_empty():
    """Dashboard quand pas encore de données."""
    
    user = get_current_user()
    render_dashboard_header(user.name, get_current_month())
    
    st.markdown("### 📊 Vue d'ensemble")
    
    # Card onboarding
    st.markdown("""
    <style>
    .onboarding-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        max-width: 600px;
        margin: 0 auto;
    }
    .onboarding-title {
        font-size: 1rem;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1.5rem;
    }
    .step {
        display: flex;
        align-items: flex-start;
        margin-bottom: 1rem;
        text-align: left;
    }
    .step-number {
        background: #10B981;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.875rem;
        margin-right: 1rem;
        flex-shrink: 0;
    }
    .step-text {
        color: #374151;
        font-size: 1rem;
        line-height: 1.5;
    }
    </style>
    
    <div class="onboarding-card">
        <div class="onboarding-title">💡 POUR BIEN DÉMARRER</div>
        
        <div class="step">
            <div class="step-number">1</div>
            <div class="step-text">Importez vos relevés bancaires au format CSV</div>
        </div>
        
        <div class="step">
            <div class="step-number">2</div>
            <div class="step-text">Laissez l'IA catégoriser automatiquement vos transactions</div>
        </div>
        
        <div class="step">
            <div class="step-number">3</div>
            <div class="step-text">Validez et visualisez vos premiers insights</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton guide
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📖 Voir le guide", use_container_width=True):
            show_guide()
```

**Livrable:** Dashboard complet avec données et empty state

---

## Phase 4: Intégration & Navigation (2-3h)

### 4.1 Page d'accueil
**Fichier:** `app_v5_5.py`

```python
"""Point d'entrée V5.5"""

import streamlit as st
from modules.ui.v5_5.theme import apply_light_theme
from modules.ui.v5_5.welcome.welcome_screen import render_welcome_screen
from modules.ui.v5_5.dashboard.dashboard_v5 import render_dashboard_v5
from modules.db.transactions import get_transactions_count

def main():
    """Application principale V5.5."""
    
    # Configuration
    st.set_page_config(
        page_title="FinancePerso",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Appliquer thème light
    apply_light_theme()
    
    # Router
    if get_transactions_count() == 0:
        render_welcome_screen()
    else:
        render_dashboard_v5()

if __name__ == "__main__":
    main()
```

### 4.2 Feature Flag
**Dans:** `modules/constants.py`

```python
# Feature flags
USE_V5_5_INTERFACE = True  # Activer la nouvelle interface
```

**Livrable:** Application V5.5 fonctionnelle et intégrée

---

## 📅 Calendrier réaliste

| Phase | Durée | Focus |
|-------|-------|-------|
| **Phase 0** | 2-3h | Thème light, tokens |
| **Phase 1** | 3-4h | Welcome card |
| **Phase 2** | 4-5h | KPI cards |
| **Phase 3** | 4-5h | Dashboard complet |
| **Phase 4** | 2-3h | Intégration |
| **Buffer** | 2h | Tests, corrections |
| **TOTAL** | **17-22h** | ~2-3 jours |

---

## ✅ Checklist de validation

### Avant chaque phase
- [ ] Réutiliser les composants existants au maximum
- [ ] Suivre les conventions du projet (tokens, atoms, molecules)
- [ ] Tester l'affichage sur différentes tailles d'écran

### Tests à réaliser
- [ ] Welcome s'affiche sans données
- [ ] Navigation Import/Guide fonctionne
- [ ] Dashboard s'affiche avec données
- [ ] 4 KPIs visibles avec bonnes valeurs
- [ ] Variations MoM calculées correctement
- [ ] Graphique et transactions récentes visibles
- [ ] Responsive (mobile/tablette/desktop)

---

## 🎯 Prochaine étape

**Prêt à démarrer ?** Je commence par :
1. **Phase 0** : Créer le thème light (`modules/ui/v5_5/theme.py`)
2. **Phase 1** : Créer le WelcomeCard

Ou veux-tu ajuster certaines parties du plan ? 🚀
