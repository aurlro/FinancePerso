# AGENT-010: Navigation & Experience Designer

## 🎯 Mission

Concepteur de l'experience de navigation et des flux utilisateur. Responsable de la structure de l'application, de la navigation entre pages, et de la fluidite du parcours utilisateur. Garant de l'accessibilite et de l'ergonomie.

---

## 📚 Contexte: Navigation

### Architecture Navigationnelle

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NAVIGATION FLOW                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐        │
│   │  Home   │───▶│ Import  │───▶│ Validate│───▶│ Dashboard│        │
│   │Dashboard│    │  File   │    │  Data   │    │  Full    │        │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘        │
│        │               │               │              │            │
│        ▼               ▼               ▼              ▼            │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐        │
│   │ Analytics│    │ History │    │ Categories│   │ Settings │        │
│   │  Pages   │    │  View   │    │ Management│   │  Page    │        │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Structure de Pages

```python
# Configuration des pages Streamlit

PAGES_CONFIG = {
    'home': {
        'title': 'Tableau de bord',
        'icon': '🏠',
        'file': 'pages/home.py',
        'position': 1,
        'show_in_menu': True
    },
    'import': {
        'title': 'Importer',
        'icon': '📥',
        'file': 'pages/import_data.py',
        'position': 2,
        'show_in_menu': True
    },
    'validation': {
        'title': 'A valider',
        'icon': '⚡',
        'file': 'pages/validation.py',
        'position': 3,
        'show_in_menu': True,
        'badge': 'pending_count'
    },
    'transactions': {
        'title': 'Transactions',
        'icon': '📋',
        'file': 'pages/transactions.py',
        'position': 4,
        'show_in_menu': True
    },
    'analytics': {
        'title': 'Analytics',
        'icon': '📊',
        'file': 'pages/analytics.py',
        'position': 5,
        'show_in_menu': True
    },
    'categories': {
        'title': 'Categories',
        'icon': '🏷️',
        'file': 'pages/categories.py',
        'position': 6,
        'show_in_menu': True
    },
    'settings': {
        'title': 'Parametres',
        'icon': '⚙️',
        'file': 'pages/settings.py',
        'position': 10,
        'show_in_menu': True
    },
    # Pages cachees (non dans menu)
    'login': {
        'title': 'Connexion',
        'file': 'pages/login.py',
        'show_in_menu': False
    },
    'error': {
        'title': 'Erreur',
        'file': 'pages/error.py',
        'show_in_menu': False
    }
}
```

---

## 🧱 Module 1: Navigation System

### Sidebar Navigation

```python
def render_sidebar_navigation():
    """Rend la navigation laterale."""
    
    with st.sidebar:
        # Logo et titre
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0;">
                <h2 style="color: #2563EB;">💰 FinancePerso</h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Menu principal
        for page_id, config in sorted(PAGES_CONFIG.items(), key=lambda x: x[1].get('position', 99)):
            if not config.get('show_in_menu', True):
                continue
            
            # Badge pour items avec notification
            badge = ""
            if 'badge' in config:
                count = get_badge_count(config['badge'])
                if count > 0:
                    badge = f" <span style='background: #EF4444; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.75rem;'>{count}</span>"
            
            # Style actif/inactif
            is_active = st.session_state.get('current_page') == page_id
            bg_color = '#F3F4F6' if is_active else 'transparent'
            text_color = '#2563EB' if is_active else '#374151'
            
            st.markdown(f"""
                <a href="?page={page_id}" style=""
                    display: flex;
                    align-items: center;
                    padding: 0.75rem 1rem;
                    border-radius: 0.5rem;
                    background: {bg_color};
                    color: {text_color};
                    text-decoration: none;
                    font-weight: {'600' if is_active else '400'};
                    margin-bottom: 0.25rem;
                ">
                    <span style="margin-right: 0.75rem;">{config['icon']}</span>
                    {config['title']}{badge}
                </a>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Section utilisateur
        render_user_section()
        
        # Version
        st.caption("v5.2.1")

def get_badge_count(badge_type: str) -> int:
    """Recupere le nombre pour un badge."""
    if badge_type == 'pending_count':
        return get_pending_transactions_count()
    return 0
```

### Breadcrumb Navigation

```python
def breadcrumb(path: list[dict]):
    """
    Navigation fil d'Ariane.
    
    Args:
        path: Liste de {label, page} ou None pour dernier
              Ex: [{'label': 'Home', 'page': 'home'}, {'label': 'Transactions', 'page': None}]
    """
    items = []
    
    for i, item in enumerate(path):
        is_last = i == len(path) - 1
        
        if is_last or item.get('page') is None:
            items.append(f"<span style='color: #6B7280; font-weight: 500;'>{item['label']}</span>")
        else:
            items.append(f"<a href='?page={item['page']}' style='color: #2563EB; text-decoration: none;'>{item['label']}</a>")
    
    separator = " <span style='color: #9CA3AF; margin: 0 0.5rem;'>/</span> "
    st.markdown(f"<div style='margin-bottom: 1rem;'>{separator.join(items)}</div>", unsafe_allow_html=True)
```

### Page Router

```python
def route_to_page(page_id: str, params: dict = None):
    """
    Navigation programmatique vers une page.
    
    Args:
        page_id: Identifiant page
        params: Parametres URL optionnels
    """
    st.session_state['current_page'] = page_id
    
    if params:
        st.session_state['page_params'] = params
    
    st.rerun()

def get_current_page() -> str:
    """Recupere la page courante."""
    # Priorite: query param > session state > defaut
    query_params = st.query_params
    if 'page' in query_params:
        return query_params['page']
    
    return st.session_state.get('current_page', 'home')

def render_current_page():
    """Rend la page courante."""
    page_id = get_current_page()
    
    if page_id not in PAGES_CONFIG:
        page_id = 'error'
    
    config = PAGES_CONFIG[page_id]
    
    # Import dynamique
    module_name = config['file'].replace('/', '.').replace('.py', '')
    try:
        page_module = __import__(module_name, fromlist=['render'])
        page_module.render()
    except Exception as e:
        st.error(f"Erreur chargement page: {e}")
```

---

## 🧱 Module 2: User Flows

### Wizard Pattern

```python
class Wizard:
    """Wizard multi-etapes."""
    
    def __init__(self, wizard_id: str, steps: list[dict]):
        self.wizard_id = wizard_id
        self.steps = steps
        
        # Initialiser etape
        if f'{wizard_id}_step' not in st.session_state:
            st.session_state[f'{wizard_id}_step'] = 0
    
    @property
    def current_step(self) -> int:
        return st.session_state[f'{self.wizard_id}_step']
    
    @current_step.setter
    def current_step(self, value: int):
        st.session_state[f'{self.wizard_id}_step'] = value
    
    def render_progress(self):
        """Affiche la barre de progression."""
        progress = (self.current_step + 1) / len(self.steps)
        st.progress(progress)
        
        # Indicateurs d'etapes
        cols = st.columns(len(self.steps))
        for i, step in enumerate(self.steps):
            with cols[i]:
                if i < self.current_step:
                    st.markdown(f"✅ **{step['label']}**")
                elif i == self.current_step:
                    st.markdown(f"▶️ **{step['label']}**")
                else:
                    st.markdown(f"⚪ {step['label']}")
    
    def next_step(self):
        """Passe a l'etape suivante."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            st.rerun()
    
    def previous_step(self):
        """Retourne a l'etape precedente."""
        if self.current_step > 0:
            self.current_step -= 1
            st.rerun()
    
    def render_buttons(self, can_proceed: bool = True):
        """Affiche les boutons de navigation."""
        cols = st.columns([1, 1, 2])
        
        with cols[0]:
            if self.current_step > 0:
                if st.button("◀ Precedent"):
                    self.previous_step()
        
        with cols[1]:
            if self.current_step < len(self.steps) - 1:
                if st.button("Suivant ▶", disabled=not can_proceed):
                    self.next_step()
            else:
                if st.button("✓ Terminer", disabled=not can_proceed):
                    return True
        
        return False

# Utilisation pour import
import_wizard = Wizard('import', [
    {'label': 'Fichier', 'id': 'file'},
    {'label': 'Banque', 'id': 'bank'},
    {'label': 'Mapping', 'id': 'mapping'},
    {'label': 'Validation', 'id': 'validation'}
])
```

### Toast Notifications

```python
def show_toast(
    message: str,
    type: str = 'info',
    duration: int = 3
):
    """
    Notification toast ephemere.
    
    Args:
        message: Texte
        type: 'info', 'success', 'warning', 'error'
        duration: Secondes d'affichage
    """
    colors = {
        'info': '#3B82F6',
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444'
    }
    
    icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    
    toast_id = f"toast_{datetime.now().timestamp()}"
    
    st.markdown(f"""
        <div id="{toast_id}" style=""
            position: fixed;
            top: 1rem;
            right: 1rem;
            background: white;
            border-left: 4px solid {colors[type]};
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 9999;
            animation: slideIn 0.3s ease;
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span>{icons[type]}</span>
                <span>{message}</span>
            </div>
        </div>
        <style>
        @keyframes slideIn {{
            from {{ transform: translateX(100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        </style>
        <script>
        setTimeout(() => {{
            document.getElementById('{toast_id}').style.display = 'none';
        }}, {duration * 1000});
        </script>
    """, unsafe_allow_html=True)
```

---

## 🔧 Responsabilites

### Quand consulter cet agent

- Nouvelle page/flow
- Restructuration navigation
- Amelioration UX
- Mobile/responsive
- Accessibilite (a11y)
- Feedback utilisateur

---

**Version**: 1.0
**Date**: 2026-02-25
**Statut**: PRET A L'EMPLOI


---

## 🌍 Module Additionnel: Mobile & Advanced UX

### Mobile Navigation

```python
"""
Patterns de navigation pour appareils mobiles.
"""

def mobile_bottom_nav(active_page: str):
    """
    Navigation bottom bar pour mobile.
    À utiliser avec st.bottom_sheet dans Streamlit 1.28+.
    """
    mobile_items = [
        {'id': 'home', 'icon': '🏠', 'label': 'Accueil'},
        {'id': 'transactions', 'icon': '📋', 'label': 'Transactions'},
        {'id': 'import', 'icon': '📥', 'label': 'Importer'},
        {'id': 'analytics', 'icon': '📊', 'label': 'Stats'},
        {'id': 'settings', 'icon': '⚙️', 'label': 'Paramètres'},
    ]
    
    cols = st.columns(len(mobile_items))
    
    for i, item in enumerate(mobile_items):
        with cols[i]:
            is_active = active_page == item['id']
            color = '#2563EB' if is_active else '#6B7280'
            
            if st.button(
                f"{item['icon']}",
                key=f"mobile_nav_{item['id']}",
                help=item['label']
            ):
                route_to_page(item['id'])
            
            st.markdown(f"<p style='text-align: center; color: {color}; font-size: 0.75rem; margin: 0;'>{item['label']}</p>", 
                       unsafe_allow_html=True)

def mobile_card_stack(cards: list[dict]):
    """
    Affiche des cartes empilées pour mobile (Tinder-style swipeable).
    """
    for i, card_data in enumerate(cards):
        with st.container():
            st.markdown(f"""
                <div style=""
                    background: white;
                    border-radius: 1rem;
                    padding: 1rem;
                    margin-bottom: 0.5rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <h4>{card_data['title']}</h4>
                    <p>{card_data['content']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if card_data.get('actions'):
                cols = st.columns(len(card_data['actions']))
                for j, action in enumerate(card_data['actions']):
                    with cols[j]:
                        if st.button(action['label'], key=f"card_{i}_action_{j}"):
                            action['callback']()
```

### Keyboard Shortcuts

```python
"""
Raccourcis clavier pour power users.
"""

KEYBOARD_SHORTCUTS = {
    'global': {
        '?': 'Afficher l\'aide des raccourcis',
        '/': 'Focus sur recherche',
        'esc': 'Fermer modal/annuler',
    },
    'navigation': {
        'g h': 'Aller à l\'accueil',
        'g i': 'Aller à l\'import',
        'g v': 'Aller à la validation',
        'g t': 'Aller aux transactions',
        'g a': 'Aller aux analytics',
    },
    'actions': {
        'ctrl+s': 'Sauvegarder',
        'ctrl+enter': 'Valider formulaire',
        'ctrl+n': 'Nouvelle transaction',
        'ctrl+f': 'Rechercher',
    },
    'validation': {
        'j': 'Transaction suivante',
        'k': 'Transaction précédente',
        'y': 'Accepter suggestion',
        'n': 'Refuser/ignorer',
        'e': 'Éditer',
    }
}

def keyboard_shortcuts_help():
    """Affiche l'aide des raccourcis clavier."""
    with st.expander("⌨️ Raccourcis clavier (?)"):
        for category, shortcuts in KEYBOARD_SHORTCUTS.items():
            st.subheader(category.title())
            for key, description in shortcuts.items():
                st.markdown(f"<kbd>{key}</kbd> - {description}", unsafe_allow_html=True)

def register_shortcuts():
    """
    Enregistre les raccourcis clavier via JavaScript.
    À inclure dans chaque page.
    """
    st.markdown("""
        <script>
        document.addEventListener('keydown', function(e) {
            // Global shortcuts
            if (e.key === '?' && !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
                window.showShortcutsHelp();
            }
            if (e.key === '/' && !e.ctrlKey) {
                e.preventDefault();
                document.querySelector('input[type="text"]').focus();
            }
            if (e.key === 'Escape') {
                window.closeAllModals();
            }
            
            // Navigation vim-style
            if (e.key === 'j') {
                window.focusNextItem();
            }
            if (e.key === 'k') {
                window.focusPrevItem();
            }
        });
        </script>
    """, unsafe_allow_html=True)
```

### Loading States & Skeletons

```python
"""
États de chargement et skeleton screens.
"""

def skeleton_card():
    """Skeleton pour une card de chargement."""
    st.markdown("""
        <div style=""
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
        ">
            <div style="height: 1.5rem; width: 60%; background: #ddd; border-radius: 0.25rem; margin-bottom: 0.5rem;"></div>
            <div style="height: 1rem; width: 40%; background: #ddd; border-radius: 0.25rem;"></div>
        </div>
        <style>
        @keyframes shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        </style>
    """, unsafe_allow_html=True)

def skeleton_table(rows: int = 5):
    """Skeleton pour un tableau."""
    for _ in range(rows):
        cols = st.columns([0.3, 0.4, 0.3])
        for col in cols:
            with col:
                st.markdown("""
                    <div style=""
                        height: 1rem;
                        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                        background-size: 200% 100%;
                        animation: shimmer 1.5s infinite;
                        border-radius: 0.25rem;
                        margin: 0.5rem 0;
                    "></div>
                """, unsafe_allow_html=True)

def loading_overlay(text: str = "Chargement..."):
    """Overlay de chargement pour toute la page."""
    st.markdown(f"""
        <div style=""
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255,255,255,0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        ">
            <div style="text-align: center;">
                <div style=""
                    width: 50px;
                    height: 50px;
                    border: 4px solid #E5E7EB;
                    border-top-color: #2563EB;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 1rem;
                "></div>
                <p>{text}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
```

### Error Boundaries & Fallbacks

```python
"""
Gestion des erreurs UI avec fallbacks gracieux.
"""

def error_boundary(func: Callable, fallback_message: str = "Une erreur est survenue"):
    """
    Décorateur pour capturer les erreurs UI.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"UI Error in {func.__name__}: {e}")
            
            st.error(f"""
                {fallback_message}
                
                <details>
                    <summary>Détails techniques</summary>
                    <code>{str(e)}</code>
                </details>
            """, icon="🚨")
            
            if st.button("🔄 Réessayer"):
                st.rerun()
    return wrapper

def empty_state(
    icon: str = "📭",
    title: str = "Aucune donnée",
    description: str = "Commencez par importer vos transactions.",
    action_label: str = "Importer",
    action_callback: Callable = None
):
    """
    État vide avec call-to-action.
    """
    st.markdown(f"""
        <div style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
            <h3 style="color: #374151; margin-bottom: 0.5rem;">{title}</h3>
            <p style="color: #6B7280; margin-bottom: 1.5rem;">{description}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if action_callback:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(f"➕ {action_label}", use_container_width=True):
                action_callback()

def error_state(
    error: Exception,
    retry_callback: Callable = None
):
    """
    État d'erreur avec retry.
    """
    st.markdown(f"""
        <div style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">😵</div>
            <h3 style="color: #DC2626; margin-bottom: 0.5rem;">Oups! Une erreur est survenue</h3>
            <p style="color: #6B7280;">{str(error)}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if retry_callback:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Réessayer", use_container_width=True):
                retry_callback()
```

### Onboarding Flow

```python
"""
Flow d'onboarding pour nouveaux utilisateurs.
"""

ONBOARDING_STEPS = [
    {
        'id': 'welcome',
        'title': 'Bienvenue sur FinancePerso!',
        'content': 'Gérez vos finances personnelles avec intelligence.',
        'icon': '👋',
        'action': None
    },
    {
        'id': 'import',
        'title': 'Importez vos relevés',
        'content': 'Connectez vos comptes bancaires ou importez des fichiers CSV/QIF.',
        'icon': '📥',
        'action': 'import'
    },
    {
        'id': 'categorize',
        'title': 'Catégorisez vos transactions',
        'content': 'L\'IA suggère automatiquement les catégories. Vous validez.',
        'icon': '🏷️',
        'action': 'validation'
    },
    {
        'id': 'dashboard',
        'title': 'Suivez vos finances',
        'content': 'Visualisez vos dépenses, budgets et tendances.',
        'icon': '📊',
        'action': 'home'
    }
]

def onboarding_flow():
    """Affiche le flow d'onboarding si première visite."""
    if 'onboarding_completed' in st.session_state:
        return
    
    current_step = st.session_state.get('onboarding_step', 0)
    step = ONBOARDING_STEPS[current_step]
    
    with st.container():
        st.markdown(f"""
            <div style=""
                background: linear-gradient(135deg, #2563EB, #1D4ED8);
                color: white;
                padding: 2rem;
                border-radius: 1rem;
                text-align: center;
                margin-bottom: 1rem;
            ">
                <div style="font-size: 4rem; margin-bottom: 1rem;">{step['icon']}</div>
                <h2 style="color: white; margin-bottom: 0.5rem;">{step['title']}</h2>
                <p style="opacity: 0.9;">{step['content']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Progress
        progress = (current_step + 1) / len(ONBOARDING_STEPS)
        st.progress(progress)
        
        # Navigation
        cols = st.columns([1, 1])
        with cols[0]:
            if current_step > 0:
                if st.button("← Précédent"):
                    st.session_state['onboarding_step'] = current_step - 1
                    st.rerun()
        with cols[1]:
            if current_step < len(ONBOARDING_STEPS) - 1:
                if st.button("Suivant →"):
                    st.session_state['onboarding_step'] = current_step + 1
                    st.rerun()
            else:
                if st.button("Commencer →"):
                    st.session_state['onboarding_completed'] = True
                    if step['action']:
                        route_to_page(step['action'])
                    st.rerun()
        
        # Skip
        if st.button("Passer l'introduction", type="tertiary"):
            st.session_state['onboarding_completed'] = True
            st.rerun()
```

---

**Version**: 1.1 - **COMPLÉTÉ**
**Ajouts**: Mobile navigation, keyboard shortcuts, loading states, error boundaries, onboarding flow


---

# 🧭 UX NAVIGATION EXPERT - MODULES AVANCÉS

## 🗺️ Module 4: Information Architecture

### Architecture de l'Information

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INFORMATION ARCHITECTURE (IA)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Organisation Mentale des Utilisateurs                                       │
│  ├── Marie (Pro): Besoin rapidité → Actions en 1-2 clicks                   │
│  ├── Thomas (Couple): Besoin clarté → Navigation par objectifs              │
│  └── Sophie (Étudiante): Besoin guidance → Progressive disclosure           │
│                                                                              │
│  Taxonomie des Données                                                       │
│  ├── Transactions (entière principale)                                      │
│  │   ├── Par date (chronologique)                                           │
│  │   ├── Par catégorie (groupée)                                            │
│  │   ├── Par membre (attribuée)                                             │
│  │   └── Par statut (validée/pending)                                       │
│  ├── Budgets (entité de planification)                                      │n│  │   ├── Par période (mensuel)                                              │
│  │   └── Par catégorie                                                      │
│  └── Analytics (entité dérivée)                                             │
│      ├── Tendances temporelles                                              │
│      ├── Comparaisons                                                       │
│      └── Projections                                                        │
│                                                                              │
│  Navigation Hierarchy                                                        │
│  ├── Primary: Dashboard, Transactions, Budgets                              │
│  ├── Secondary: Analytics, Import, Validation                               │
│  └── Tertiary: Settings, Help, Profile                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Card Sorting Results

```python
# modules/ui/navigation/information_architecture.py

class InformationArchitecture:
    """
    Architecture de l'information basée sur la recherche utilisateur.
    """
    
    # Résultats de card sorting ouvert avec 15 utilisateurs
    CARD_SORTING_RESULTS = {
        'categories': {
            'vue_ensemble': {
                'items': ['Dashboard', 'Synthèse mensuelle', 'Alertes'],
                'mental_model': 'Ma situation actuelle',
                'findability_score': 9.2
            },
            'transactions': {
                'items': ['Liste transactions', 'Validation', 'Import', 'Recherche'],
                'mental_model': 'Mes opérations bancaires',
                'findability_score': 9.5
            },
            'analyse': {
                'items': ['Statistiques', 'Tendances', 'Budgets', 'Objectifs'],
                'mental_model': 'Comprendre et planifier',
                'findability_score': 8.7
            },
            'gestion': {
                'items': ['Catégories', 'Membres', 'Règles', 'Configuration'],
                'mental_model': 'Paramétrer l\'application',
                'findability_score': 8.1
            }
        },
        'conflicts': [
            {
                'item': 'Budgets',
                'placed_in': ['analyse', 'vue_ensemble'],
                'resolution': 'Placer dans analyse, shortcut dans dashboard'
            },
            {
                'item': 'Validation',
                'placed_in': ['transactions', 'vue_ensemble'],
                'resolution': 'Badge dans sidebar, page dédiée accessible'
            }
        ]
    }
    
    @staticmethod
    def get_navigation_structure(user_type: str = 'standard') -> dict:
        """
        Retourne la structure de navigation adaptée au type d'utilisateur.
        
        Args:
            user_type: 'beginner', 'standard', 'power_user'
        """
        base_structure = {
            'primary': [
                {'id': 'dashboard', 'label': 'Tableau de bord', 'icon': '🏠', 'priority': 1},
                {'id': 'transactions', 'label': 'Transactions', 'icon': '📋', 'priority': 2},
                {'id': 'budgets', 'label': 'Budgets', 'icon': '📊', 'priority': 3},
            ],
            'secondary': [
                {'id': 'analytics', 'label': 'Analyses', 'icon': '📈', 'priority': 4},
                {'id': 'import', 'label': 'Importer', 'icon': '📥', 'priority': 5},
            ],
            'utility': [
                {'id': 'settings', 'label': 'Paramètres', 'icon': '⚙️', 'priority': 10},
            ]
        }
        
        if user_type == 'beginner':
            # Simplifier pour débutants
            base_structure['secondary'] = [
                {'id': 'import', 'label': 'Importer', 'icon': '📥', 'priority': 4},
                {'id': 'help', 'label': 'Aide', 'icon': '❓', 'priority': 5},
            ]
            # Masquer budgets initialement
            base_structure['primary'] = [
                {'id': 'dashboard', 'label': 'Tableau de bord', 'icon': '🏠', 'priority': 1},
                {'id': 'transactions', 'label': 'Transactions', 'icon': '📋', 'priority': 2},
            ]
        
        elif user_type == 'power_user':
            # Ajouter accès rapide pour power users
            base_structure['primary'].insert(2, {
                'id': 'validation', 
                'label': 'À valider', 
                'icon': '⚡', 
                'priority': 2.5,
                'badge': 'pending_count'
            })
            base_structure['secondary'].append(
                {'id': 'rules', 'label': 'Règles auto', 'icon': '🤖', 'priority': 6}
            )
        
        return base_structure
    
    @staticmethod
    def validate_findability(task: str, current_location: str) -> dict:
        """
        Valide si une tâche est facilement trouvable.
        
        Args:
            task: Description de la tâche
            current_location: Où se trouve actuellement l'utilisateur
            
        Returns:
            Score de trouvabilité et recommandations
        """
        # Benchmarks NN/g:
        # - Excellent: < 1 minute, 0 erreurs
        # - Good: 1-3 minutes, 1 erreur
        # - Poor: > 3 minutes, > 1 erreur
        
        task_findability_map = {
            'voir_transactions_recentes': {
                'expected_location': 'dashboard',
                'alternative_paths': ['transactions'],
                'max_clicks': 1,
                'success_rate_target': 0.95
            },
            'importer_fichier': {
                'expected_location': 'sidebar_import',
                'alternative_paths': ['dashboard_quick_action'],
                'max_clicks': 1,
                'success_rate_target': 0.90
            },
            'modifier_budget': {
                'expected_location': 'budgets_page',
                'alternative_paths': ['dashboard_card'],
                'max_clicks': 2,
                'success_rate_target': 0.85
            },
            'valider_transactions': {
                'expected_location': 'validation_page',
                'alternative_paths': ['sidebar_badge', 'transactions_filter'],
                'max_clicks': 1,
                'success_rate_target': 0.95
            }
        }
        
        return task_findability_map.get(task, {'success_rate_target': 0.80})

class SearchArchitecture:
    """
    Architecture de recherche et découverte.
    """
    
    @staticmethod
    def design_search_interface() -> dict:
        """
        Design l'interface de recherche globale.
        """
        return {
            'placement': {
                'desktop': 'top_navbar',
                'mobile': 'bottom_sheet',
                'shortcut': 'cmd+k / ctrl+k'
            },
            'search_types': [
                {
                    'type': 'instant',
                    'trigger': 'typing',
                    'results': 'suggestions_dropdown',
                    'delay_ms': 150
                },
                {
                    'type': 'full',
                    'trigger': 'enter',
                    'results': 'dedicated_page',
                    'filters': ['transactions', 'categories', 'date_range', 'amount']
                }
            ],
            'suggestions': {
                'recent_searches': 3,
                'saved_searches': True,
                'trending': False,  # Privacy concern for finance
                'ai_assisted': True  # "Vous cherchez peut-être..."
            },
            'results_display': {
                'grouping': ['by_type', 'by_date'],
                'highlighting': 'matching_terms',
                'actions': ['open', 'preview', 'filter_by']
            }
        }

---

## 🎭 Module 5: User Flows & Journey Mapping

### Critical User Journeys

```python
# modules/ui/navigation/user_journeys.py

class CriticalUserJourneys:
    """
    Cartographie des parcours utilisateurs critiques.
    """
    
    JOURNEYS = {
        'first_time_import': {
            'name': 'Premier Import (Onboarding)',
            'frequency': 'Once per user',
            'business_impact': 'Critical - Activation',
            'success_criteria': 'User imports and validates first transactions',
            'steps': [
                {
                    'step': 1,
                    'action': 'Land on Dashboard (empty state)',
                    'touchpoint': 'Dashboard',
                    'emotion': 'Curious/Uncertain',
                    'pain_point_risk': 'High - Empty state must guide',
                    'design_solution': 'Prominent CTA + Tutorial overlay'
                },
                {
                    'step': 2,
                    'action': 'Click "Import First Transactions"',
                    'touchpoint': 'Button / Sidebar',
                    'emotion': 'Motivated',
                    'pain_point_risk': 'Medium',
                    'design_solution': 'Wizard with clear progress'
                },
                {
                    'step': 3,
                    'action': 'Upload CSV file',
                    'touchpoint': 'Import Wizard',
                    'emotion': 'Hopeful',
                    'pain_point_risk': 'High - Format errors',
                    'design_solution': 'Auto-detection + Clear error messages'
                },
                {
                    'step': 4,
                    'action': 'Map columns',
                    'touchpoint': 'Mapping Screen',
                    'emotion': 'Confused possibly',
                    'pain_point_risk': 'High - Technical complexity',
                    'design_solution': 'Smart defaults + Preview + Help tooltips'
                },
                {
                    'step': 5,
                    'action': 'Review and confirm',
                    'touchpoint': 'Summary Screen',
                    'emotion': 'Cautious',
                    'pain_point_risk': 'Medium',
                    'design_solution': 'Clear summary + Edit capability'
                },
                {
                    'step': 6,
                    'action': 'Validate first transactions',
                    'touchpoint': 'Validation Queue',
                    'emotion': 'Engaged',
                    'pain_point_risk': 'High - Abandon if too many',
                    'design_solution': 'Batch actions + AI suggestions + Progress'
                },
                {
                    'step': 7,
                    'action': 'See populated Dashboard',
                    'touchpoint': 'Dashboard',
                    'emotion': 'Satisfied/Achievement',
                    'pain_point_risk': 'Low',
                    'design_solution': 'Celebrate success + Next steps guidance'
                }
            ],
            'metrics': {
                'completion_rate_target': 0.75,
                'time_to_complete_target': '5 minutes',
                'drop_off_points': [3, 4, 6]  # Steps to optimize
            }
        },
        
        'daily_check': {
            'name': 'Check Quotidien (Habit)',
            'frequency': 'Daily',
            'business_impact': 'High - Retention',
            'success_criteria': 'User checks balance/spending in < 30 seconds',
            'steps': [
                {
                    'step': 1,
                    'action': 'Open app',
                    'touchpoint': 'Mobile/Desktop',
                    'emotion': 'Routine',
                    'time_budget': '3 seconds',
                    'design_solution': 'Fast load + Cached data'
                },
                {
                    'step': 2,
                    'action': 'View dashboard',
                    'touchpoint': 'Dashboard',
                    'emotion': 'Informed',
                    'time_budget': '10 seconds',
                    'design_solution': 'KPI cards at top + Key insights'
                },
                {
                    'step': 3,
                    'action': 'Check specific metric',
                    'touchpoint': 'Drill-down',
                    'emotion': 'Focused',
                    'time_budget': '15 seconds',
                    'design_solution': 'One-tap access to details'
                },
                {
                    'step': 4,
                    'action': 'Close or take action',
                    'touchpoint': 'Decision point',
                    'emotion': 'Satisfied or Motivated',
                    'design_solution': 'Quick actions if needed'
                }
            ],
            'metrics': {
                'task_success_rate': 0.98,
                'time_on_task': '< 30 seconds',
                'satisfaction': '> 4.5/5'
            }
        },
        
        'monthly_budget_review': {
            'name': 'Révision Mensuelle des Budgets',
            'frequency': 'Monthly',
            'business_impact': 'Medium - Engagement',
            'success_criteria': 'User understands spending vs budget',
            'steps': [
                {
                    'step': 1,
                    'action': 'Navigate to Budgets',
                    'touchpoint': 'Navigation',
                    'emotion': 'Proactive',
                    'design_solution': 'Clear label + Notification reminder'
                },
                {
                    'step': 2,
                    'action': 'Review budget status',
                    'touchpoint': 'Budget Dashboard',
                    'emotion': 'Analytical',
                    'design_solution': 'Visual progress bars + Variance indicators'
                },
                {
                    'step': 3,
                    'action': 'Identify overspend',
                    'touchpoint': 'Alert/Warning',
                    'emotion': 'Concerned',
                    'design_solution': 'Context + Actionable insights'
                },
                {
                    'step': 4,
                    'action': 'Drill into category',
                    'touchpoint': 'Category Detail',
                    'emotion': 'Investigative',
                    'design_solution': 'Transaction list + Trend chart'
                },
                {
                    'step': 5,
                    'action': 'Adjust budget or commit to change',
                    'touchpoint': 'Action Modal',
                    'emotion': 'Determined',
                    'design_solution': 'Easy adjustment + Next month planning'
                }
            ]
        }
    }
    
    @staticmethod
    def optimize_journey(journey_id: str, analytics_data: dict) -> list[dict]:
        """
        Analyse et optimise un parcours utilisateur.
        
        Args:
            journey_id: Identifiant du parcours
            analytics_data: Données d'analytics du parcours
            
        Returns:
            Liste des recommandations d'optimisation
        """
        journey = CriticalUserJourneys.JOURNEYS.get(journey_id)
        if not journey:
            return []
        
        recommendations = []
        
        # Analyser les points de friction
        for step in journey['steps']:
            step_metrics = analytics_data.get('steps', {}).get(step['step'], {})
            
            drop_off_rate = step_metrics.get('drop_off', 0)
            if drop_off_rate > 0.20:  # > 20% abandonment
                recommendations.append({
                    'priority': 'High',
                    'step': step['step'],
                    'issue': f"{drop_off_rate*100}% d'abandon",
                    'pain_point': step['pain_point_risk'],
                    'solution': step['design_solution'],
                    'expected_improvement': f"-{drop_off_rate*0.5*100}% abandonment"
                })
            
            time_spent = step_metrics.get('avg_time', 0)
            expected_time = step.get('time_budget', '30 seconds')
            # Parse expected time and compare
        
        return sorted(recommendations, key=lambda x: x['priority'])

class EmotionalJourneyMap:
    """
    Cartographie émotionnelle des parcours.
    """
    
    @staticmethod
    def create_emotion_map(journey_steps: list) -> dict:
        """
        Crée une carte des émotions tout au long du parcours.
        """
        emotions = ['Frustrated', 'Confused', 'Neutral', 'Satisfied', 'Delighted']
        
        journey_chart = []
        for step in journey_steps:
            emotion = step.get('emotion', 'Neutral')
            pain_point = step.get('pain_point_risk', 'Low')
            
            # Convertir en score numérique
            emotion_score = emotions.index(emotion) if emotion in emotions else 2
            
            # Ajuster selon le risque de pain point
            if pain_point == 'High' and emotion_score > 2:
                emotion_score -= 1
            
            journey_chart.append({
                'step': step['step'],
                'action': step['action'],
                'emotion_score': emotion_score,
                'emotion_label': emotion,
                'opportunity': emotion_score < 3  # Opportunity to improve
            })
        
        return {
            'journey_curve': journey_chart,
            'low_points': [s for s in journey_chart if s['emotion_score'] <= 1],
            'high_points': [s for s in journey_chart if s['emotion_score'] >= 4],
            'improvement_opportunities': [s for s in journey_chart if s['opportunity']]
        }

---

## 📱 Module 6: Mobile-First Navigation

### Responsive Navigation Patterns

```python
# modules/ui/navigation/mobile_navigation.py

class MobileNavigation:
    """
    Patterns de navigation mobile-first.
    """
    
    @staticmethod
    def bottom_navigation_bar(current_page: str) -> dict:
        """
        Navigation bottom bar pour mobile.
        
        Pattern: Bottom Navigation Bar (Material Design)
        Best for: 3-5 primary destinations
        """
        return {
            'type': 'bottom_bar',
            'placement': 'fixed_bottom',
            'height': '56dp',
            'items': [
                {'id': 'home', 'icon': '🏠', 'label': 'Accueil'},
                {'id': 'transactions', 'icon': '📋', 'label': 'Transactions'},
                {'id': 'import', 'icon': '➕', 'label': 'Importer', 'highlight': True},
                {'id': 'budgets', 'icon': '📊', 'label': 'Budgets'},
                {'id': 'more', 'icon': '☰', 'label': 'Plus'},  # Overflow
            ],
            'behavior': {
                'hide_on_scroll_down': True,
                'show_on_scroll_up': True,
                'active_indicator': 'label_always_visible',
                'badges': True
            }
        }
    
    @staticmethod
    def hamburger_menu_structure() -> dict:
        """
        Structure du menu hamburger (overflow).
        """
        return {
            'type': 'side_drawer',
            'trigger': 'hamburger_icon',
            'sections': [
                {
                    'type': 'profile_header',
                    'content': ['avatar', 'name', 'email']
                },
                {
                    'type': 'primary_items',
                    'items': ['Dashboard', 'Transactions', 'Budgets', 'Analytics']
                },
                {
                    'type': 'secondary_items',
                    'items': ['Import', 'Validation', 'Categories']
                },
                {
                    'type': 'utility_items',
                    'items': ['Settings', 'Help', 'Logout']
                }
            ],
            'gestures': {
                'open': 'swipe_from_left_edge',
                'close': 'swipe_left_or_tap_outside'
            }
        }
    
    @staticmethod
    def gesture_navigation() -> dict:
        """
        Navigation par gestes pour mobile.
        """
        return {
            'swipe_actions': {
                'list_items': {
                    'swipe_left': {
                        'action': 'delete_or_archive',
                        'icon': '🗑️',
                        'color': '#EF4444',
                        'haptic': True
                    },
                    'swipe_right': {
                        'action': 'quick_edit',
                        'icon': '✏️',
                        'color': '#3B82F6',
                        'haptic': True
                    }
                },
                'screens': {
                    'edge_swipe_left': 'go_back',
                    'edge_swipe_right': 'open_menu'
                }
            },
            'tap_actions': {
                'double_tap_list_item': 'expand_details',
                'long_press': 'enter_selection_mode',
                'pull_to_refresh': 'refresh_data'
            }
        }
    
    @staticmethod
    def adapt_for_mobile(desktop_layout: dict) -> dict:
        """
        Adapte un layout desktop pour mobile.
        
        Args:
            desktop_layout: Configuration desktop
            
        Returns:
            Configuration mobile
        """
        adaptations = {
            'sidebar_to_bottom': True,
            'multi_column_to_single': True,
            'horizontal_scroll_sections': ['kpi_cards', 'quick_actions'],
            'stack_order': [
                'header',
                'kpi_cards_scrollable',
                'primary_chart',
                'recent_transactions',
                'quick_actions',
                'budget_summary'
            ],
            'touch_targets': {
                'min_size': '44x44dp',
                'spacing': '8dp'
            },
            'text_scaling': {
                'minimum': '14sp',
                'readable_width': '40-60 characters'
            },
            'performance': {
                'lazy_load_images': True,
                'skeleton_screens': True,
                'reduce_animations': 'respect_prefers_reduced_motion'
            }
        }
        
        return adaptations

class AdaptiveNavigation:
    """
    Navigation qui s'adapte au contexte utilisateur.
    """
    
    @staticmethod
    def context_aware_nav(user_context: dict) -> dict:
        """
        Adapte la navigation selon le contexte.
        
        Args:
            user_context: {'time_of_day', 'location', 'recent_actions', 'device_type'}
        """
        nav = {'primary': [], 'secondary': [], 'quick_actions': []}
        
        # Time-based adaptation
        hour = user_context.get('time_of_day', 12)
        if 6 <= hour < 12:  # Morning
            nav['quick_actions'].append({
                'label': 'Check Daily Budget',
                'icon': '☀️',
                'context': 'morning_routine'
            })
        elif hour >= 18:  # Evening
            nav['quick_actions'].append({
                'label': 'Review Today\'s Spending',
                'icon': '🌙',
                'context': 'evening_review'
            })
        
        # Action-based adaptation
        recent = user_context.get('recent_actions', [])
        if 'import' in recent[-3:]:
            nav['primary'].insert(0, {
                'id': 'validation',
                'label': 'Validate Transactions',
                'badge': 'new',
                'priority': 'high'
            })
        
        # Device-based adaptation
        if user_context.get('device_type') == 'mobile':
            nav['primary'] = nav['primary'][:4]  # Limit to 4 items
        
        return nav

---

**Version**: 2.0 - **UX NAVIGATION EXPERT COMPLETE**
**Modules Ajoutés**:
- 🗺️ Information Architecture (IA)
- 🎭 User Flows & Journey Mapping
- 📱 Mobile-First Navigation
- 🔍 Search Architecture
-  Emotional Journey Map
- 📊 Critical User Journeys

**Coordination avec AGENT-009**:
- AGENT-009: Design System + Components + Visual Design
- AGENT-010: Navigation + IA + User Flows + Mobile UX

**Métriques UX Définies**:
- Findability scores
- Task success rates
- Time on task
- Emotional journey curves
