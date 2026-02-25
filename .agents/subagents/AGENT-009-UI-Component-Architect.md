# AGENT-009: UI Component Architect

## 🎯 Mission

Architecte du Design System et des composants UI de FinancePerso. Responsable de la bibliotheque de composants reutilisables, de la coherence visuelle et de l'experience utilisateur coherente. Garant de l'esthetique et de la fonctionnalite.

---

## 📚 Contexte: Design System

### Philosophie
> "Un bon composant est reutilisable, accessible, et raconte une histoire claire."

### Architecture UI

```
┌─────────────────────────────────────────────────────────────────────┐
│                    UI COMPONENT ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  DESIGN TOKENS                                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Colors | Typography | Spacing | Shadows | Breakpoints       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                       │
│  ATOMIC COMPONENTS                                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Button | Input | Card | Badge | Icon | Divider              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                       │
│  MOLECULAR COMPONENTS                                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Form Field | KPI Card | Transaction Row | Filter Bar        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ↓                                       │
│  ORGANISMS                                                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Transaction Table | Dashboard Widget | Import Wizard        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Palette de Couleurs

```python
# modules/ui/design_system.py

COLORS = {
    # Primary
    'primary': '#2563EB',
    'primary_light': '#3B82F6',
    'primary_dark': '#1D4ED8',
    
    # Secondary
    'secondary': '#64748B',
    'secondary_light': '#94A3B8',
    
    # Success / Error / Warning
    'success': '#10B981',
    'error': '#EF4444',
    'warning': '#F59E0B',
    'info': '#3B82F6',
    
    # Grays
    'gray_50': '#F9FAFB',
    'gray_100': '#F3F4F6',
    'gray_200': '#E5E7EB',
    'gray_300': '#D1D5DB',
    'gray_400': '#9CA3AF',
    'gray_500': '#6B7280',
    'gray_600': '#4B5563',
    'gray_700': '#374151',
    'gray_800': '#1F2937',
    'gray_900': '#111827',
    
    # Backgrounds
    'bg_primary': '#FFFFFF',
    'bg_secondary': '#F9FAFB',
    'bg_tertiary': '#F3F4F6',
}

TYPOGRAPHY = {
    'font_family': 'Inter, system-ui, sans-serif',
    'sizes': {
        'xs': '0.75rem',    # 12px
        'sm': '0.875rem',   # 14px
        'base': '1rem',     # 16px
        'lg': '1.125rem',   # 18px
        'xl': '1.25rem',    # 20px
        '2xl': '1.5rem',    # 24px
        '3xl': '1.875rem',  # 30px
        '4xl': '2.25rem',   # 36px
    }
}

SPACING = {
    'xs': '0.25rem',   # 4px
    'sm': '0.5rem',    # 8px
    'md': '1rem',      # 16px
    'lg': '1.5rem',    # 24px
    'xl': '2rem',      # 32px
    '2xl': '3rem',     # 48px
}
```

---

## 🧱 Module 1: Atomic Components

### Boutons

```python
def button(
    label: str,
    key: str,
    type: str = 'primary',
    size: str = 'md',
    disabled: bool = False,
    icon: str = None,
    on_click: Callable = None
):
    """
    Bouton standardise.
    
    Args:
        label: Texte du bouton
        key: Cle unique Streamlit
        type: 'primary', 'secondary', 'danger', 'ghost'
        size: 'sm', 'md', 'lg'
        disabled: Desactive
        icon: Emoji ou icone (optionnel)
        on_click: Callback
        
    Returns:
        True si clique
    """
    styles = {
        'primary': f"""
            background-color: {COLORS['primary']};
            color: white;
            border: none;
        """,
        'secondary': f"""
            background-color: white;
            color: {COLORS['gray_700']};
            border: 1px solid {COLORS['gray_300']};
        """,
        'danger': f"""
            background-color: {COLORS['error']};
            color: white;
            border: none;
        """,
        'ghost': f"""
            background-color: transparent;
            color: {COLORS['primary']};
            border: none;
        """
    }
    
    sizes = {
        'sm': 'padding: 0.375rem 0.75rem; font-size: 0.875rem;',
        'md': 'padding: 0.5rem 1rem; font-size: 1rem;',
        'lg': 'padding: 0.75rem 1.5rem; font-size: 1.125rem;'
    }
    
    css = f"""
        <style>
        .btn-{key} {{
            {styles[type]}
            {sizes[size]}
            border-radius: 0.375rem;
            font-weight: 500;
            cursor: {'not-allowed' if disabled else 'pointer'};
            opacity: {0.5 if disabled else 1};
            transition: all 0.2s;
        }}
        .btn-{key}:hover {{
            opacity: {0.8 if not disabled else 0.5};
        }}
        </style>
    """
    
    label_with_icon = f"{icon} {label}" if icon else label
    
    st.markdown(css, unsafe_allow_html=True)
    return st.button(label_with_icon, key=key, disabled=disabled, on_click=on_click)
```

### Cards

```python
def card(
    content: str,
    title: str = None,
    icon: str = None,
    accent_color: str = None,
    footer: str = None
):
    """
    Card container.
    
    Args:
        content: Contenu HTML ou texte
        title: Titre de la card
        icon: Emoji d'icone
        accent_color: Couleur d'accent (bordure gauche)
        footer: Contenu du footer
    """
    accent_style = f"border-left: 4px solid {accent_color};" if accent_color else ""
    
    header = f"""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
            <span style="font-size: 1.25rem;">{icon}</span>
            <h3 style="margin: 0; font-size: 1.125rem; font-weight: 600;">{title}</h3>
        </div>
    """ if title else ""
    
    footer_html = f"""
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid {COLORS['gray_200']};">
            {footer}
        </div>
    """ if footer else ""
    
    card_html = f"""
        <div style=""
            background: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            {accent_style}
        ">
            {header}
            <div>{content}</div>
            {footer_html}
        </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

# Variantes specialisees
def kpi_card(
    title: str,
    value: str,
    trend: str = None,
    trend_up: bool = True,
    icon: str = None,
    color: str = 'primary'
):
    """Card pour indicateurs KPI."""
    trend_color = COLORS['success'] if trend_up else COLORS['error']
    trend_icon = '↑' if trend_up else '↓'
    
    trend_html = f"""
        <div style="color: {trend_color}; font-size: 0.875rem; font-weight: 500;">
            {trend_icon} {trend}
        </div>
    """ if trend else ""
    
    content = f"""
        <div style="font-size: 2rem; font-weight: 700; color: {COLORS['gray_900']};">
            {value}
        </div>
        <div style="color: {COLORS['gray_500']}; font-size: 0.875rem;">
            {title}
        </div>
        {trend_html}
    """
    
    card(content, icon=icon, accent_color=COLORS[color])
```

### Badges

```python
def badge(
    text: str,
    type: str = 'default',
    size: str = 'md'
):
    """
    Badge pour statuts et labels.
    
    Args:
        text: Texte du badge
        type: 'default', 'success', 'warning', 'error', 'info'
        size: 'sm', 'md', 'lg'
    """
    styles = {
        'default': f"background: {COLORS['gray_100']}; color: {COLORS['gray_700']};",
        'success': f"background: #D1FAE5; color: #065F46;",
        'warning': f"background: #FEF3C7; color: #92400E;",
        'error': f"background: #FEE2E2; color: #991B1B;",
        'info': f"background: #DBEAFE; color: #1E40AF;"
    }
    
    sizes = {
        'sm': 'padding: 0.125rem 0.5rem; font-size: 0.75rem;',
        'md': 'padding: 0.25rem 0.75rem; font-size: 0.875rem;',
        'lg': 'padding: 0.375rem 1rem; font-size: 1rem;'
    }
    
    st.markdown(f"""
        <span style=""
            display: inline-flex;
            align-items: center;
            border-radius: 9999px;
            font-weight: 500;
            {styles[type]}
            {sizes[size]}
        ">
            {text}
        </span>
    """, unsafe_allow_html=True)
```

---

## 🧬 Module 2: Molecular Components

### Formulaires

```python
def form_field(
    label: str,
    help: str = None,
    required: bool = False,
    error: str = None
):
    """
    Wrapper pour champ de formulaire avec label et erreur.
    """
    label_text = f"{label} {'*' if required else ''}"
    
    if help:
        st.caption(help)
    
    st.markdown(f"**{label_text}**")
    
    if error:
        st.error(error)

def text_input_field(
    label: str,
    key: str,
    value: str = "",
    placeholder: str = None,
    help: str = None,
    required: bool = False,
    validate: Callable = None
) -> str:
    """Input texte avec validation."""
    form_field(label, help, required)
    
    result = st.text_input(
        label="",
        value=value,
        key=key,
        placeholder=placeholder,
        label_visibility="collapsed"
    )
    
    if validate and result:
        is_valid, error_msg = validate(result)
        if not is_valid:
            st.error(error_msg)
    
    return result
```

### Transaction Row

```python
def transaction_row(
    tx: dict,
    on_categorize: Callable = None,
    on_edit: Callable = None,
    selected: bool = False
):
    """
    Ligne de transaction pour liste.
    
    Args:
        tx: Donnees transaction
        on_categorize: Callback categorization
        on_edit: Callback edition
        selected: Selectionnee
    """
    cols = st.columns([0.05, 0.25, 0.15, 0.15, 0.15, 0.25])
    
    with cols[0]:
        st.checkbox("", value=selected, key=f"select_{tx['id']}")
    
    with cols[1]:
        st.markdown(f"**{tx['label'][:30]}...**" if len(tx['label']) > 30 else f"**{tx['label']}**")
        st.caption(tx['date'])
    
    with cols[2]:
        amount_color = 'success' if tx['amount'] > 0 else 'error'
        st.markdown(f":{amount_color}[{tx['amount']:,.2f} €]")
    
    with cols[3]:
        badge(tx['category_validated'], type='default')
    
    with cols[4]:
        if tx.get('status') == 'validated':
            badge("✓ Valide", type='success', size='sm')
        else:
            badge("⏳ En attente", type='warning', size='sm')
    
    with cols[5]:
        if on_categorize:
            if st.button("📂", key=f"cat_{tx['id']}"):
                on_categorize(tx)
        if on_edit:
            if st.button("✏️", key=f"edit_{tx['id']}"):
                on_edit(tx)
```

### Filter Bar

```python
def filter_bar(
    filters: dict,
    on_change: Callable = None
) -> dict:
    """
    Barre de filtres pour listes.
    
    Returns:
        Filtres actifs
    """
    with st.container():
        cols = st.columns(len(filters) + 1)
        
        active_filters = {}
        
        for i, (key, config) in enumerate(filters.items()):
            with cols[i]:
                if config['type'] == 'select':
                    value = st.selectbox(
                        config['label'],
                        options=config['options'],
                        key=f"filter_{key}"
                    )
                    if value != 'Tous':
                        active_filters[key] = value
                
                elif config['type'] == 'date_range':
                    value = st.date_input(
                        config['label'],
                        value=config.get('default'),
                        key=f"filter_{key}"
                    )
                    active_filters[key] = value
                
                elif config['type'] == 'search':
                    value = st.text_input(
                        config['label'],
                        placeholder=config.get('placeholder'),
                        key=f"filter_{key}"
                    )
                    if value:
                        active_filters[key] = value
        
        with cols[-1]:
            if st.button("🗑️ Reinitialiser"):
                active_filters = {}
                st.rerun()
        
        # Afficher filtres actifs
        if active_filters:
            st.write("Filtres actifs:")
            for key, value in active_filters.items():
                st.caption(f"{key}: {value}")
        
        return active_filters
```

---

## 🔧 Responsabilites

### Quand consulter cet agent

- Nouveau composant UI
- Modification Design System
- Refactoring visuel
- Ajout d'icone/illustration
- Responsive design
- Accessibilite (a11y)

---

**Version**: 1.0
**Date**: 2026-02-25
**Statut**: PRET A L'EMPLOI


---

## 🌍 Module Additionnel: Responsive & Accessibility

### Breakpoints Responsive

```python
"""
Gestion des breakpoints pour design responsive.
"""

BREAKPOINTS = {
    'sm': 640,   # Mobile landscape
    'md': 768,   # Tablet
    'lg': 1024,  # Desktop
    'xl': 1280,  # Large desktop
    '2xl': 1536  # Extra large
}

def get_responsive_columns(base: int, md: int = None, lg: int = None) -> int:
    """
    Retourne le nombre de colonnes adapté à l'écran.
    
    Usage:
        cols = get_responsive_columns(1, md=2, lg=4)
        st.columns(cols)
    """
    # Streamlit ne permet pas de détecter la largeur facilement
    # On utilise une approche par container
    try:
        # Estimate based on container width (heuristic)
        width = st.session_state.get('viewport_width', 1024)
        if width >= BREAKPOINTS['lg'] and lg:
            return lg
        if width >= BREAKPOINTS['md'] and md:
            return md
        return base
    except:
        return base

def responsive_grid(items: list, cols_sm: int = 1, cols_md: int = 2, cols_lg: int = 4):
    """
    Affiche une grille responsive.
    
    Args:
        items: Liste des éléments à afficher
        cols_sm: Colonnes sur mobile
        cols_md: Colonces sur tablet
        cols_lg: Colonnes sur desktop
    """
    # Pour Streamlit, on utilise une approche simple
    # car on ne peut pas détecter la largeur en temps réel
    cols = st.columns(cols_lg)
    
    for i, item in enumerate(items):
        with cols[i % cols_lg]:
            yield item
```

### Dark Mode Support

```python
"""
Support du mode sombre pour Streamlit.
"""

THEME = {
    'light': {
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F9FAFB',
        'bg_tertiary': '#F3F4F6',
        'text_primary': '#111827',
        'text_secondary': '#6B7280',
        'border': '#E5E7EB',
        'card_shadow': '0 1px 3px rgba(0,0,0,0.1)'
    },
    'dark': {
        'bg_primary': '#111827',
        'bg_secondary': '#1F2937',
        'bg_tertiary': '#374151',
        'text_primary': '#F9FAFB',
        'text_secondary': '#9CA3AF',
        'border': '#374151',
        'card_shadow': '0 1px 3px rgba(0,0,0,0.5)'
    }
}

def get_theme() -> dict:
    """Retourne le thème actuel."""
    # Streamlit utilise le thème system par défaut
    # On peut le détecter via le paramètre de config
    import os
    theme = os.getenv('STREAMLIT_THEME_BASE', 'light')
    return THEME.get(theme, THEME['light'])

def themed_card(content: str, title: str = None) -> str:
    """Card avec thème automatique."""
    theme = get_theme()
    
    return f"""
        <div style=""
            background: {theme['bg_secondary']};
            color: {theme['text_primary']};
            border: 1px solid {theme['border']};
            border-radius: 0.5rem;
            padding: 1.5rem;
            box-shadow: {theme['card_shadow']};
        ">
            {f'<h3 style="color: {theme["text_primary"]}; margin-top: 0;">{title}</h3>' if title else ''}
            {content}
        </div>
    """
```

### Accessibilité (a11y)

```python
"""
Helpers pour accessibilité WCAG 2.1 AA.
"""

# Contraste minimum 4.5:1 pour texte normal
# Contraste minimum 3:1 pour texte large (18pt+ ou 14pt bold)

ACCESSIBILITY = {
    'focus_ring': '0 0 0 3px rgba(37, 99, 235, 0.4)',
    'focus_outline': '2px solid #2563EB',
    'min_touch_size': '44px',  # WCAG 2.5.5
    'screen_reader_only': """
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    """
}

def accessible_button(label: str, aria_label: str = None, key: str = None) -> bool:
    """
    Bouton avec support accessibilité complet.
    
    Args:
        label: Texte visible
        aria_label: Description pour lecteurs d'écran
        key: Clé unique Streamlit
    """
    # Streamlit génère automatiquement des attributs ARIA
    # mais on peut améliorer avec des tooltips
    help_text = aria_label if aria_label else label
    return st.button(label, key=key, help=help_text)

def color_contrast_check(foreground: str, background: str) -> tuple[bool, float]:
    """
    Vérifie le contraste entre deux couleurs.
    
    Returns:
        (passe WCAG AA, ratio de contraste)
    """
    def luminance(hex_color: str) -> float:
        """Calcule la luminance relative."""
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
        
        def adjust(c):
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)
    
    lum1, lum2 = luminance(foreground), luminance(background)
    ratio = (max(lum1, lum2) + 0.05) / (min(lum1, lum2) + 0.05)
    
    return ratio >= 4.5, ratio

def skip_to_main_content():
    """
    Lien d'évitement pour navigation clavier.
    À placer en haut de chaque page.
    """
    st.markdown("""
        <a href="#main-content" style=""
            position: absolute;
            top: -40px;
            left: 0;
            background: #2563EB;
            color: white;
            padding: 8px;
            text-decoration: none;
            z-index: 100;
        ""
            onfocus="this.style.top='0'" 
            onblur="this.style.top='-40px'"
        >
            Aller au contenu principal
        </a>
        <div id="main-content"></div>
    """, unsafe_allow_html=True)
```

### Animations & Transitions

```python
"""
Animations CSS pour feedback utilisateur.
"""

ANIMATIONS = {
    'fade_in': """
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        animation: fadeIn 0.3s ease-in;
    """,
    'slide_up': """
        @keyframes slideUp {
            from { transform: translateY(10px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        animation: slideUp 0.3s ease-out;
    """,
    'pulse': """
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    """,
    'spin': """
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        animation: spin 1s linear infinite;
    """
}

def loading_spinner(text: str = "Chargement..."):
    """Spinner de chargement avec animation."""
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 0.5rem; padding: 1rem;">
            <div style=""
                width: 20px;
                height: 20px;
                border: 3px solid #E5E7EB;
                border-top-color: #2563EB;
                border-radius: 50%;
                {ANIMATIONS['spin']}
            "></div>
            <span>{text}</span>
        </div>
    """, unsafe_allow_html=True)

def animated_number(value: float, prefix: str = "", suffix: str = ""):
    """
    Affiche un nombre avec animation d'incrémentation.
    """
    # Streamlit limitation: pas d'animation JS facile
    # On affiche directement avec style
    st.markdown(f"""
        <div style=""
            font-size: 2rem;
            font-weight: 700;
            color: {COLORS['gray_900']};
            {ANIMATIONS['fade_in']}
        ">
            {prefix}{value:,.2f}{suffix}
        </div>
    """, unsafe_allow_html=True)
```

### Icon System

```python
"""
Système d'icônes standardisées.
"""

ICONS = {
    # Navigation
    'home': '🏠',
    'dashboard': '📊',
    'settings': '⚙️',
    'back': '◀️',
    'forward': '▶️',
    
    # Actions
    'add': '➕',
    'edit': '✏️',
    'delete': '🗑️',
    'save': '💾',
    'cancel': '❌',
    'confirm': '✅',
    'search': '🔍',
    'filter': '🔽',
    'refresh': '🔄',
    'download': '⬇️',
    'upload': '⬆️',
    
    # Finance
    'money': '💰',
    'expense': '💸',
    'income': '💵',
    'budget': '📋',
    'transaction': '🧾',
    'bank': '🏦',
    'card': '💳',
    
    # Status
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'pending': '⏳',
    'loading': '⏳',
    
    # Categories
    'food': '🍽️',
    'transport': '🚗',
    'housing': '🏠',
    'health': '🏥',
    'leisure': '🎮',
    'shopping': '🛍️',
    'education': '📚',
    'travel': '✈️',
}

def icon(name: str, default: str = '❓') -> str:
    """Retourne l'emoji icône."""
    return ICONS.get(name, default)

def icon_button(icon_name: str, tooltip: str = None, key: str = None) -> bool:
    """Bouton avec icône uniquement."""
    label = icon(icon_name)
    return st.button(label, key=key, help=tooltip)
```

---

**Version**: 1.1 - **COMPLÉTÉ**
**Ajouts**: Responsive design, dark mode, accessibility WCAG, animations, icon system


---

# 🎨 PRODUCT DESIGN EXPERT - MODULES AVANCÉS

## 🧠 Module 5: UX Research & Methodology

### Design Thinking Process

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DESIGN THINKING PROCESS                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. EMPATHIZE          2. DEFINE           3. IDEATE                 │
│  ┌─────────────┐      ┌─────────────┐     ┌─────────────┐           │
│  │ User        │      │ Problem     │     │ Brainstorm  │           │
│  │ Research    │  →   │ Statements  │  →  │ Solutions   │           │
│  │ Interviews  │      │ Personas    │     │ Crazy 8s    │           │
│  │ Analytics   │      │ JTBD        │     │ Mind Maps   │           │
│  └─────────────┘      └─────────────┘     └─────────────┘           │
│         │                   │                   │                    │
│         └───────────────────┴───────────────────┘                    │
│                         ↓                                            │
│  4. PROTOTYPE          5. TEST            6. ITERATE                 │
│  ┌─────────────┐      ┌─────────────┐     ┌─────────────┐           │
│  │ Wireframes  │      │ Usability   │     │ A/B Tests   │           │
│  │ Mockups     │  →   │ User Tests  │  →  │ Analytics   │           │
│  │ Clickable   │      │ Feedback    │     │ Refinement  │           │
│  │ Prototypes  │      │ Surveys     │     │ Updates     │           │
│  └─────────────┘      └─────────────┘     └─────────────┘           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### User Research Methods

```python
# modules/ui/ux_research/user_research.py

class UserResearchFramework:
    """
    Framework de recherche utilisateur pour FinancePerso.
    """
    
    RESEARCH_METHODS = {
        'interviews': {
            'type': 'qualitative',
            'duration': '30-60min',
            'participants': '5-8 users',
            'goal': 'Deep insights, motivations, pain points'
        },
        'surveys': {
            'type': 'quantitative',
            'duration': '5-10min',
            'participants': '100+ users',
            'goal': 'Validate hypotheses, measure satisfaction'
        },
        'usability_testing': {
            'type': 'mixed',
            'duration': '15-30min',
            'participants': '5 users',
            'goal': 'Identify friction points, validate flows'
        },
        'card_sorting': {
            'type': 'qualitative',
            'duration': '20min',
            'participants': '10+ users',
            'goal': 'Information architecture validation'
        },
        'heatmaps': {
            'type': 'behavioral',
            'duration': 'ongoing',
            'participants': 'all users',
            'goal': 'Understand click patterns, attention areas'
        },
        'session_recordings': {
            'type': 'behavioral',
            'duration': 'ongoing',
            'participants': 'sample',
            'goal': 'Observe real usage patterns'
        }
    }
    
    @staticmethod
    def create_interview_guide(objective: str, topics: list) -> dict:
        """
        Crée un guide d'entretien utilisateur.
        
        Args:
            objective: But de la recherche
            topics: Sujets à aborder
            
        Returns:
            Structure du guide d'entretien
        """
        return {
            'introduction': {
                'duration': '2min',
                'script': f"""
                Bonjour et merci de participer à cette étude.
                Aujourd'hui, nous allons discuter de {objective}.
                Il n'y a pas de bonnes ou mauvaises réponses.
                L'entretien durera environ 30 minutes.
                """,
                'consent': 'Enregistrement audio accepté?'
            },
            'warm_up': {
                'duration': '5min',
                'questions': [
                    'Parlez-moi de vous et de votre situation financière.',
                    'Comment gérez-vous vos finances aujourd\'hui?',
                    'Quels outils utilisez-vous?'
                ]
            },
            'main_topics': [
                {
                    'topic': topic,
                    'duration': '7min',
                    'questions': [
                        f'Parlez-moi de votre expérience avec {topic}.',
                        f'Quels sont les défis que vous rencontrez avec {topic}?',
                        f'Comment imaginez-vous la solution idéale pour {topic}?',
                        f'Pouvez-vous me décrire un moment récent où {topic} était problématique?'
                    ],
                    'probes': [
                        'Pouvez-vous m\'en dire plus?',
                        'Pourquoi est-ce important pour vous?',
                        'Comment vous sentiez-vous à ce moment?'
                    ]
                }
                for topic in topics
            ],
            'closing': {
                'duration': '3min',
                'questions': [
                    'Y a-t-il autre chose que vous aimeriez ajouter?',
                    'Si vous pouviez changer une chose, ce serait quoi?',
                    'Auriez-vous des questions pour moi?'
                ],
                'thanks': 'Merci beaucoup pour votre temps et vos retours.'
            }
        }
    
    @staticmethod
    def analyze_interview_notes(notes: list[dict]) -> dict:
        """
        Analyse les notes d'entretien avec la méthode d'affinité.
        
        Returns:
            Insights organisés par thème
        """
        # Méthode d'affinité: regrouper par similarité
        themes = {}
        pain_points = []
        opportunities = []
        quotes = []
        
        for note in notes:
            # Extraire citations verbatim
            if note.get('is_quote'):
                quotes.append({
                    'text': note['content'],
                    'user': note['participant_id'],
                    'context': note['topic']
                })
            
            # Identifier pain points
            if note.get('sentiment') == 'negative' or 'problème' in note['content'].lower():
                pain_points.append({
                    'description': note['content'],
                    'frequency': note.get('frequency', 1),
                    'severity': note.get('severity', 'medium')
                })
            
            # Identifier opportunités
            if 'aimerait' in note['content'].lower() or 'besoin' in note['content'].lower():
                opportunities.append({
                    'description': note['content'],
                    'impact': note.get('impact', 'medium'),
                    'feasibility': note.get('feasibility', 'medium')
                })
            
            # Regrouper par thème
            theme = note.get('theme', 'Autre')
            if theme not in themes:
                themes[theme] = []
            themes[theme].append(note['content'])
        
        return {
            'themes': themes,
            'pain_points': sorted(pain_points, key=lambda x: x['severity'], reverse=True),
            'opportunities': sorted(opportunities, key=lambda x: x['impact'], reverse=True),
            'key_quotes': quotes[:10]  # Top 10 citations
        }

class PersonaBuilder:
    """
    Construction de personas utilisateurs.
    """
    
    PERSONA_TEMPLATE = {
        'name': '',
        'age': 0,
        'occupation': '',
        'location': '',
        'tech_savviness': 'low/medium/high',
        'financial_situation': '',
        'goals': [],
        'frustrations': [],
        'motivations': [],
        'behaviors': [],
        'tools_used': [],
        'quote': ''
    }
    
    @classmethod
    def create_finance_personas(cls) -> dict:
        """
        Crée les personas types pour FinancePerso.
        
        Returns:
            Dict de personas
        """
        return {
            'marie_busy_professional': {
                'name': 'Marie',
                'age': 32,
                'occupation': 'Consultante',
                'location': 'Paris',
                'tech_savviness': 'high',
                'financial_situation': 'Revenus élevés, peu de temps',
                'goals': [
                    'Suivre ses dépenses sans effort',
                    'Optimiser son épargne',
                    'Préparer des projets (voyage, achat)'
                ],
                'frustrations': [
                    'Pas le temps de saisir manuellement',
                    'Outils existants trop complexes',
                    'Manque de visibilité sur ses finances'
                ],
                'motivations': [
                    'Indépendance financière',
                    'Sérénité',
                    'Projets concrets'
                ],
                'behaviors': [
                    'Utilise son smartphone pour tout',
                    'Préfère les automatisations',
                    'Aime les résumés visuels'
                ],
                'tools_used': ['Banque mobile', 'Excel', 'Notion'],
                'quote': 'Je veux savoir où va mon argent sans y passer des heures.'
            },
            'thomas_couple_planner': {
                'name': 'Thomas',
                'age': 38,
                'occupation': 'Ingénieur',
                'location': 'Lyon',
                'tech_savviness': 'medium',
                'financial_situation': 'Revenus stables, foyer à gérer',
                'goals': [
                    'Gérer les finances du couple',
                    'Planifier les vacances en famille',
                    'Préparer l\'avenir des enfants'
                ],
                'frustrations': [
                    'Difficulté à suivre qui dépense quoi',
                    'Budget vacances toujours dépassé',
                    'Pas de vision partagée avec sa compagne'
                ],
                'motivations': [
                    'Harmonie dans le couple',
                    'Sécurité familiale',
                    'Projets familiaux'
                ],
                'behaviors': [
                    'Consulte ses finances le weekend',
                    'Aime discuter budget avec sa compagne',
                    'Préfère les tableaux et graphiques'
                ],
                'tools_used': ['Banque en ligne', 'Google Sheets', 'Splitwise'],
                'quote': 'J\'ai besoin de transparence pour éviter les tensions sur l\'argent.'
            },
            'sophie_student_budget': {
                'name': 'Sophie',
                'age': 22,
                'occupation': 'Étudiante en Master',
                'location': 'Bordeaux',
                'tech_savviness': 'high',
                'financial_situation': 'Budget serré, alternance',
                'goals': [
                    'Tenir son budget mensuel',
                    'Épargner pour des voyages',
                    'Devenir autonome financièrement'
                ],
                'frustrations': [
                    'Dépenses imprévues qui foutent tout en l\'air',
                    'Manque d\'expérience en gestion d\'argent',
                    'Peur du découvert'
                ],
                'motivations': [
                    'Liberté financière',
                    'Voyages avec amis',
                    'Fierté personnelle'
                ],
                'behaviors': [
                    'Vérifie son solde quotidiennement',
                    'Aime les défis (no-spend challenges)',
                    'Très active sur les réseaux'
                ],
                'tools_used': ['App banque', 'Notes iPhone', 'Instagram'],
                'quote': 'Je veux profiter de la vie sans finir à découvert chaque mois.'
            }
        }

class JTBDFramework:
    """
    Jobs-To-Be-Done Framework.
    """
    
    @staticmethod
    def define_jtbd(job_statement: str, circumstances: list, desired_outcome: str) -> dict:
        """
        Définit un Job-To-Be-Done.
        
        Template: "When I [circumstance], I want to [job], so I can [outcome]."
        
        Returns:
            Structure JTBD complète
        """
        return {
            'job_statement': job_statement,
            'circumstances': circumstances,
            'functional_job': '',
            'emotional_jobs': {
                'personal': '',  # How I want to feel
                'social': ''     # How I want others to see me
            },
            'desired_outcome': desired_outcome,
            'success_metrics': [],
            'current_solutions': [],
            'pain_points': [],
            'opportunities': []
        }
    
    @classmethod
    def get_finance_jtbd(cls) -> list[dict]:
        """Liste des JTBD pour FinancePerso."""
        return [
            {
                'job': 'Surveiller mes dépenses quotidiennes',
                'when': 'Quand je fais mes courses ou achats en ligne',
                'want': 'Je veux voir immédiatement l\'impact sur mon budget',
                'so': 'Je peux ajuster mes dépenses le reste du mois',
                'importance': 5,
                'satisfaction': 2
            },
            {
                'job': 'Comprendre mes habitudes de dépense',
                'when': 'À la fin du mois',
                'want': 'Je veux voir où je dépasse et pourquoi',
                'so': 'Je peux corriger le tir le mois suivant',
                'importance': 5,
                'satisfaction': 3
            },
            {
                'job': 'Partager les finances en couple',
                'when': 'Quand je discute budget avec mon conjoint',
                'want': 'Je veux avoir une vision claire et partagée',
                'so': 'Nous pouvons prendre des décisions ensemble sans conflit',
                'importance': 4,
                'satisfaction': 2
            }
        ]
```

---

## 🎨 Module 6: Wireframing & Prototyping

### Wireframe System

```python
# modules/ui/design/wireframes.py

class WireframeSystem:
    """
    Système de wireframing pour FinancePerso.
    """
    
    # Grille de base
    GRID = {
        'columns': 12,
        'gutter': '24px',
        'margin': '48px',
        'max_width': '1440px'
    }
    
    # Breakpoints
    BREAKPOINTS = {
        'mobile': '0-639px',
        'tablet': '640-1023px',
        'desktop': '1024-1439px',
        'large': '1440px+'
    }
    
    @staticmethod
    def wireframe_specs() -> dict:
        """Spécifications de wireframing."""
        return {
            'colors': {
                'canvas': '#F5F5F5',
                'artboard': '#FFFFFF',
                'grid': '#E0E0E0',
                'component': '#D0D0D0',
                'text': '#333333',
                'annotation': '#FF6B6B'
            },
            'typography': {
                'h1': {'size': '24px', 'weight': 'bold'},
                'h2': {'size': '20px', 'weight': 'bold'},
                'h3': {'size': '16px', 'weight': 'bold'},
                'body': {'size': '14px', 'weight': 'normal'},
                'caption': {'size': '12px', 'weight': 'normal'}
            },
            'spacing_scale': [4, 8, 12, 16, 24, 32, 48, 64, 96],
            'components': {
                'button': {'height': 40, 'padding': '0 16px', 'radius': 4},
                'input': {'height': 40, 'padding': '0 12px', 'radius': 4},
                'card': {'padding': 24, 'radius': 8},
                'modal': {'padding': 32, 'radius': 12}
            }
        }

class PageWireframes:
    """
    Wireframes pour chaque page de l'application.
    """
    
    @staticmethod
    def dashboard_wireframe() -> dict:
        """
        Wireframe du Dashboard.
        
        Structure:
        ┌─────────────────────────────────────────┐
        │ Header: Logo | Nav | User               │
        ├─────────────────────────────────────────┤
        │ ┌─────────────────────────────────┐     │
        │ │ KPI Cards Row (4 cards)         │     │
        │ └─────────────────────────────────┘     │
        │ ┌──────────────┐  ┌───────────────┐     │
        │ │ Chart:       │  │ Recent Tx     │     │
        │ │ Monthly      │  │ List          │     │
        │ │ Trend        │  │ (5 items)     │     │
        │ └──────────────┘  └───────────────┘     │
        │ ┌─────────────────────────────────┐     │
        │ │ Budget Progress Bars            │     │
        │ └─────────────────────────────────┘     │
        │ ┌─────────────────────────────────┐     │
        │ │ Quick Actions Row               │     │
        │ └─────────────────────────────────┘     │
        └─────────────────────────────────────────┘
        """
        return {
            'layout': {
                'type': 'grid',
                'rows': [
                    {'height': 'auto', 'component': 'header'},
                    {'height': 'auto', 'component': 'kpi_cards'},
                    {'height': '400px', 'component': 'main_content', 'columns': 2},
                    {'height': 'auto', 'component': 'budget_section'},
                    {'height': 'auto', 'component': 'quick_actions'}
                ]
            },
            'components': {
                'kpi_cards': {
                    'type': 'grid',
                    'columns': 4,
                    'items': [
                        {'label': 'Solde', 'value': '€X,XXX', 'trend': '+X%'},
                        {'label': 'Dépenses', 'value': '€X,XXX', 'trend': '-X%'},
                        {'label': 'Budget Restant', 'value': '€X,XXX', 'progress': 'XX%'},
                        {'label': 'Épargne', 'value': '€X,XXX', 'goal': 'XX%'}
                    ]
                },
                'main_content': {
                    'left': {
                        'width': 8,
                        'component': 'chart',
                        'title': 'Évolution Mensuelle',
                        'chart_type': 'line'
                    },
                    'right': {
                        'width': 4,
                        'component': 'list',
                        'title': 'Transactions Récentes',
                        'items': 5
                    }
                },
                'budget_section': {
                    'title': 'Suivi des Budgets',
                    'component': 'progress_bars',
                    'items': [
                        {'category': 'Alimentation', 'current': 450, 'max': 500},
                        {'category': 'Transport', 'current': 120, 'max': 200},
                        {'category': 'Loisirs', 'current': 180, 'max': 150}
                    ]
                },
                'quick_actions': {
                    'type': 'button_row',
                    'actions': ['Importer', 'Nouvelle Transaction', 'Voir Rapports']
                }
            },
            'responsive': {
                'tablet': {
                    'kpi_cards': {'columns': 2},
                    'main_content': {'stacked': True}
                },
                'mobile': {
                    'kpi_cards': {'columns': 1, 'scrollable': True},
                    'main_content': {'stacked': True},
                    'quick_actions': {'type': 'bottom_sheet'}
                }
            }
        }
    
    @staticmethod
    def validation_queue_wireframe() -> dict:
        """
        Wireframe de la file de validation.
        
        Structure:
        ┌─────────────────────────────────────────┐
        │ Header: À Valider (42) | Filtres ▼     │
        ├─────────────────────────────────────────┤
        │ ┌─────────────────────────────────┐     │
        │ │ Barre d'actions batch           │     │
        │ │ [Select All] [Valider] [Ignorer]│     │
        │ └─────────────────────────────────┘     │
        │ ┌─────────────────────────────────┐     │
        │ │ Transaction Item                │     │
        │ │ ○ | Label | Date | Montant | AI │     │
        │ │     Suggestion: Alimentation    │     │
        │ │     [✓] [✏️] [⏭️]               │     │
        │ └─────────────────────────────────┘     │
        │ ┌─────────────────────────────────┐     │
        │ │ Transaction Item                │     │
        │ │ ...                             │     │
        │ └─────────────────────────────────┘     │
        │ ┌─────────────────────────────────┐     │
        │ │ Pagination: < 1 2 3 ... >      │     │
        │ └─────────────────────────────────┘     │
        └─────────────────────────────────────────┘
        """
        return {
            'layout': {
                'header': {
                    'title': 'À Valider',
                    'badge_count': True,
                    'actions': ['filter', 'sort', 'search']
                },
                'batch_actions': {
                    'visible_when': 'items_selected',
                    'actions': [
                        {'label': 'Tout sélectionner', 'type': 'checkbox'},
                        {'label': 'Valider', 'type': 'primary'},
                        {'label': 'Ignorer', 'type': 'secondary'},
                        {'label': 'Catégoriser', 'type': 'secondary'}
                    ]
                },
                'list': {
                    'item_component': 'transaction_validation_card',
                    'item_structure': {
                        'row1': ['checkbox', 'label', 'date', 'amount', 'priority_badge'],
                        'row2': ['ai_suggestion', 'confidence_indicator'],
                        'actions': ['accept', 'edit', 'skip']
                    }
                },
                'empty_state': {
                    'icon': '🎉',
                    'title': 'Tout est à jour!',
                    'message': 'Aucune transaction en attente de validation.',
                    'action': 'Importer des transactions'
                }
            },
            'interactions': {
                'swipe_left': 'skip',
                'swipe_right': 'accept',
                'tap': 'edit',
                'long_press': 'select'
            }
        }
    
    @staticmethod
    def import_flow_wireframe() -> dict:
        """
        Wireframe du flow d'import (Wizard).
        
        Step 1: Upload
        ┌─────────────────────────────────────────┐
        │ Étape 1/4: Import de Fichier            │
        │ [========>                    ] 25%     │
        ├─────────────────────────────────────────┤
        │                                         │
        │     ┌─────────────────────────┐         │
        │     │                         │         │
        │     │    📁 ZONE DE DROP      │         │
        │     │                         │         │
        │     │  Glissez votre fichier  │         │
        │     │      ou cliquez         │         │
        │     │                         │         │
        │     └─────────────────────────┘         │
        │                                         │
        │  Formats supportés: CSV, QIF, OFX      │
        │                                         │
        │              [Continuer →]              │
        │                                         │
        └─────────────────────────────────────────┘
        
        Step 2: Bank Selection
        ┌─────────────────────────────────────────┐
        │ Étape 2/4: Sélection de la Banque       │
        ├─────────────────────────────────────────┤
        │                                         │
        │  Sélectionnez votre banque:             │
        │                                         │
        │  [🏦 Boursorama  ] [🏦 Société Générale] │
        │  [🏦 Crédit Mutuel] [🏦 Autre...      ] │
        │                                         │
        │  [← Retour]    [Continuer →]            │
        │                                         │
        └─────────────────────────────────────────┘
        
        Step 3: Mapping
        ┌─────────────────────────────────────────┐
        │ Étape 3/4: Mapping des Colonnes         │
        ├─────────────────────────────────────────┤
        │                                         │
        │  Colonnes détectées:                    │
        │                                         │
        │  Date      → Date              [✓]      │
        │  Libellé   → Label             [✓]      │
        │  Montant   → Montant           [✓]      │
        │  Catégorie → Catégorie (opt.)  [○]      │
        │                                         │
        │  [← Retour]    [Continuer →]            │
        │                                         │
        └─────────────────────────────────────────┘
        
        Step 4: Validation
        ┌─────────────────────────────────────────┐
        │ Étape 4/4: Validation                   │
        ├─────────────────────────────────────────┤
        │                                         │
        │  Résumé de l'import:                    │
        │                                         │
        │  📊 42 transactions détectées           │
        │  ✅ 40 transactions nouvelles           │
        │  ⚠️  2 doublons détectés                │
        │                                         │
        │  [Voir les doublons]                    │
        │                                         │
        │  [← Retour]    [✓ Confirmer l'import]   │
        │                                         │
        └─────────────────────────────────────────┘
        """
        return {
            'wizard_structure': {
                'steps': 4,
                'progress_indicator': 'bar',
                'navigation': 'sequential',  # Can only go forward after validation
                'allow_skip': False,
                'allow_back': True
            },
            'steps': [
                {
                    'id': 'upload',
                    'title': 'Import de Fichier',
                    'component': 'file_uploader',
                    'validation': 'file_format',
                    'help_text': 'Formats supportés: CSV, QIF, OFX'
                },
                {
                    'id': 'bank_selection',
                    'title': 'Sélection de la Banque',
                    'component': 'bank_selector',
                    'options': ['Boursorama', 'Société Générale', 'Crédit Mutuel', 'Autre'],
                    'validation': 'required'
                },
                {
                    'id': 'mapping',
                    'title': 'Mapping des Colonnes',
                    'component': 'column_mapper',
                    'auto_detect': True,
                    'manual_override': True,
                    'validation': 'required_fields_mapped'
                },
                {
                    'id': 'validation',
                    'title': 'Validation',
                    'component': 'import_summary',
                    'show_preview': True,
                    'show_duplicates': True,
                    'final_action': 'confirm_import'
                }
            ]
        }

class Prototyping:
    """
    Création de prototypes interactifs.
    """
    
    @staticmethod
    def create_clickable_prototype(flow: list[dict]) -> dict:
        """
        Définit un prototype cliquable.
        
        Args:
            flow: Liste des écrans et transitions
            
        Returns:
            Structure de prototype
        """
        return {
            'prototype_type': 'clickable',
            'tool': 'Figma/Streamlit',
            'screens': flow,
            'interactions': [
                {
                    'trigger': 'click',
                    'element': 'button_primary',
                    'action': 'navigate_to',
                    'target': 'next_screen'
                },
                {
                    'trigger': 'hover',
                    'element': 'card',
                    'action': 'show_tooltip'
                },
                {
                    'trigger': 'scroll',
                    'element': 'list',
                    'action': 'load_more'
                }
            ],
            'hotspots': [
                {
                    'screen': 'dashboard',
                    'coordinates': {'x': 100, 'y': 200, 'width': 120, 'height': 40},
                    'action': 'navigate',
                    'target': 'transactions'
                }
            ]
        }
    
    @staticmethod
    def define_micro_interactions() -> dict:
        """Définit les micro-interactions."""
        return {
            'button_hover': {
                'duration': '200ms',
                'easing': 'ease-out',
                'properties': {
                    'transform': 'translateY(-2px)',
                    'box_shadow': '0 4px 12px rgba(0,0,0,0.15)'
                }
            },
            'button_click': {
                'duration': '100ms',
                'properties': {
                    'transform': 'scale(0.98)'
                }
            },
            'card_hover': {
                'duration': '300ms',
                'properties': {
                    'transform': 'translateY(-4px)',
                    'box_shadow': '0 8px 24px rgba(0,0,0,0.12)'
                }
            },
            'toast_appear': {
                'duration': '300ms',
                'easing': 'cubic-bezier(0.4, 0, 0.2, 1)',
                'properties': {
                    'opacity': [0, 1],
                    'transform': ['translateY(-20px)', 'translateY(0)']
                }
            },
            'loading_skeleton': {
                'duration': '1.5s',
                'easing': 'linear',
                'properties': {
                    'background': 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
                    'background_size': '200% 100%',
                    'animation': 'shimmer 1.5s infinite'
                }
            },
            'success_checkmark': {
                'duration': '600ms',
                'stagger': [
                    {'property': 'stroke-dashoffset', 'delay': 0, 'from': 100, 'to': 0},
                    {'property': 'scale', 'delay': 300, 'from': 0.8, 'to': 1}
                ]
            }
        }
```

---

## 🎯 Module 7: Design Critique & Review

### Design Review Process

```python
# modules/ui/design/design_review.py

class DesignReviewFramework:
    """
    Framework de revue de design structurée.
    """
    
    REVIEW_CATEGORIES = {
        'usability': {
            'name': 'Utilisabilité',
            'questions': [
                'L\'objectif de la page est-il clair en 5 secondes?',
                'L\'utilisateur sait-il quoi faire en premier?',
                'Les actions principales sont-elles visibles?',
                'Y a-t-il des éléments de confusion ou d\'ambiguïté?',
                'Le feedback est-il clair pour chaque action?'
            ]
        },
        'accessibility': {
            'name': 'Accessibilité',
            'questions': [
                'Le contraste est-il suffisant (WCAG AA)?',
                'Les éléments interactifs sont-ils accessibles au clavier?',
                'Les images ont-elles des alternatives textuelles?',
                'La hiérarchie des titres est-elle logique?',
                'Les messages d\'erreur sont-ils compréhensibles?'
            ]
        },
        'visual_design': {
            'name': 'Design Visuel',
            'questions': [
                'La hiérarchie visuelle est-elle claire?',
                'Les espacements sont-ils cohérents?',
                'La typographie est-elle lisible?',
                'Les couleurs sont-elles utilisées de manière cohérente?',
                'Le design respecte-t-il le Design System?'
            ]
        },
        'performance': {
            'name': 'Performance',
            'questions': [
                'Le temps de chargement initial est-il < 3s?',
                'Les interactions sont-elles fluides (< 100ms)?',
                'Les états de chargement sont-ils gérés?',
                'Les images sont-elles optimisées?',
                'Le cache est-il utilisé efficacement?'
            ]
        },
        'content': {
            'name': 'Contenu',
            'questions': [
                'Le texte est-il clair et concis?',
                'Le ton est-il approprié?',
                'Les labels sont-ils compréhensibles?',
                'Y a-t-il des fautes d\'orthographe?',
                'Les textes d\'aide sont-ils utiles?'
            ]
        }
    }
    
    @staticmethod
    def conduct_heuristic_evaluation(interface: dict) -> dict:
        """
        Réalise une évaluation heuristique.
        
        Args:
            interface: Description de l'interface à évaluer
            
        Returns:
            Rapport d'évaluation
        """
        heuristics = [
            {
                'name': 'Visibilité du statut système',
                'description': 'Le système doit informer l\'utilisateur sur ce qui se passe',
                'severity_weights': {'critical': 3, 'major': 2, 'minor': 1}
            },
            {
                'name': 'Correspondance avec le monde réel',
                'description': 'Le langage doit être celui de l\'utilisateur',
                'severity_weights': {'critical': 3, 'major': 2, 'minor': 1}
            },
            {
                'name': 'Contrôle et liberté utilisateur',
                'description': 'Undo et redo doivent être disponibles',
                'severity_weights': {'critical': 3, 'major': 2, 'minor': 1}
            },
            {
                'name': 'Cohérence et standards',
                'description': 'Les mêmes actions doivent avoir le même effet',
                'severity_weights': {'critical': 2, 'major': 2, 'minor': 1}
            },
            {
                'name': 'Prévention des erreurs',
                'description': 'Mieux vaut prévenir que guérir',
                'severity_weights': {'critical': 3, 'major': 2, 'minor': 1}
            },
            {
                'name': 'Reconnaissance plutôt que rappel',
                'description': 'Rendre les options visibles',
                'severity_weights': {'critical': 2, 'major': 2, 'minor': 1}
            },
            {
                'name': 'Flexibilité et efficacité',
                'description': 'Raccourcis pour experts',
                'severity_weights': {'critical': 1, 'major': 2, 'minor': 1}
            },
            {
                'name': 'Design esthétique et minimaliste',
                'description': 'Pas d\'information non pertinente',
                'severity_weights': {'critical': 1, 'major': 1, 'minor': 1}
            },
            {
                'name': 'Aide à la reconnaissance des erreurs',
                'description': 'Messages d\'erreur clairs',
                'severity_weights': {'critical': 3, 'major': 2, 'minor': 1}
            },
            {
                'name': 'Aide et documentation',
                'description': 'Documentation facile à trouver',
                'severity_weights': {'critical': 1, 'major': 1, 'minor': 1}
            }
        ]
        
        findings = []
        for heuristic in heuristics:
            # Évaluer chaque heuristique
            score = interface.get('heuristic_scores', {}).get(heuristic['name'], 0)
            if score < 3:  # Si problème détecté
                findings.append({
                    'heuristic': heuristic['name'],
                    'severity': 'major' if score == 1 else 'minor',
                    'description': f'Violation de: {heuristic["description"]}',
                    'recommendation': 'À corriger'
                })
        
        return {
            'total_score': sum(f['severity'] == 'major' for f in findings),
            'findings': findings,
            'priority_actions': [f for f in findings if f['severity'] == 'major'][:3]
        }
    
    @staticmethod
    def design_critique_session(design: dict, reviewers: list) -> dict:
        """
        Structure une session de design critique.
        
        Format: "I like, I wish, What if"
        """
        return {
            'format': 'i_like_i_wish_what_if',
            'timebox': '30 minutes',
            'roles': {
                'presenter': 'Présente le design (5min)',
                'reviewers': 'Donnent feedback (15min)',
                'notetaker': 'Prend des notes (tout le temps)'
            },
            'structure': [
                {
                    'phase': 'Presentation',
                    'duration': '5min',
                    'rules': [
                        'Présenter le contexte et les objectifs',
                        'Expliquer les contraintes',
                        'Ne pas défendre le design encore'
                    ]
                },
                {
                    'phase': 'Feedback - "I Like"',
                    'duration': '5min',
                    'rules': [
                        'Commencer par le positif',
                        'Être spécifique',
                        'Exemple: "J\'aime la clarté de la hiérarchie visuelle"'
                    ]
                },
                {
                    'phase': 'Feedback - "I Wish"',
                    'duration': '5min',
                    'rules': [
                        'Exprimer les préoccupations',
                        'Utiliser "Je souhaiterais que..."',
                        'Exemple: "Je souhaiterais que le bouton principal soit plus visible"'
                    ]
                },
                {
                    'phase': 'Feedback - "What If"',
                    'duration': '5min',
                    'rules': [
                        'Proposer des alternatives',
                        'Brainstormer',
                        'Exemple: "Et si on essayait une mise en page en grille?"'
                    ]
                },
                {
                    'phase': 'Discussion',
                    'duration': '10min',
                    'rules': [
                        'Le présentateur peut répondre',
                        'Prioriser les actions',
                        'Définir les prochaines étapes'
                    ]
                }
            ],
            'output': {
                'action_items': [],
                'design_changes': [],
                'questions_to_explore': []
            }
        }

class DesignQualityChecklist:
    """
    Checklist de qualité design complète.
    """
    
    @staticmethod
    def get_complete_checklist() -> dict:
        """Retourne la checklist complète de qualité design."""
        return {
            'before_design': [
                '☐ Le problème utilisateur est-il bien défini?',
                '☐ Les personas sont-ils identifiés?',
                '☐ Les JTBD sont-ils clarifiés?',
                '☐ Les contraintes techniques sont-elles connues?',
                '☐ Les métriques de succès sont-elles définies?'
            ],
            'during_design': [
                '☐ Le design répond-il au problème utilisateur?',
                '☐ La hiérarchie visuelle est-elle claire?',
                '☐ Les patterns existants sont-ils réutilisés?',
                '☐ Les états d\'erreur sont-ils conçus?',
                '☐ Les états vides sont-ils conçus?',
                '☐ Le responsive est-il pris en compte?',
                '☐ L\'accessibilité est-elle considérée?'
            ],
            'before_development': [
                '☐ Le design a-t-il été revu par un pair?',
                '☐ Les specs sont-elles complètes?',
                '☐ Les assets sont-ils exportés?',
                '☐ Les animations sont-elles documentées?',
                '☐ Les textes sont-ils finalisés et relus?'
            ],
            'after_development': [
                '☐ Le design correspond-il à la maquette?',
                '☐ Les interactions fonctionnent-elles?',
                '☐ Les performances sont-elles acceptables?',
                '☐ L\'accessibilité est-elle implémentée?',
                '☐ Les tests utilisateurs sont-ils passés?'
            ]
        }
```

---

**Version**: 2.0 - **PRODUCT DESIGN EXPERT COMPLETE**  
**Modules Ajoutés**:
- 🧠 UX Research & Methodology
- 🎨 Wireframing & Prototyping  
- 🎯 Design Critique & Review
- 📊 User Research Framework
- 👥 Persona Builder
- 💡 JTBD Framework
- ✅ Design Quality Checklist

**Total Agent**: ~60+ KB de documentation design expert
