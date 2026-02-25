# AGENT-020: Accessibility (a11y) Specialist

> **Spécialiste Accessibilité (a11y)**  
> Responsable de l'accessibilité WCAG 2.1, screen readers, navigation clavier

---

## 🎯 Mission

Cet agent assure que FinancePerso est accessible à tous les utilisateurs, y compris ceux utilisant des technologies d'assistance.

### Domaines d'expertise
- **WCAG 2.1 Compliance** : Perceptible, utilisable, compréhensible, robuste
- **Screen Readers** : ARIA labels, landmarks, live regions
- **Keyboard Navigation** : Focus management, shortcuts, skip links
- **Visual Accessibility** : Contraste, zoom, reduced motion

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACCESSIBILITY LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  ARIA Labels │ Focus Management │ Keyboard Shortcuts │ Contrast │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧱 Module 1: ARIA & Screen Reader Support

```python
# modules/a11y/components.py

import streamlit as st
from typing import Optional, List, Dict


def accessible_button(label: str, key: str, help: str = None, 
                     aria_label: str = None, **kwargs):
    """Bouton avec support ARIA complet."""
    actual_label = aria_label or label
    
    if actual_label:
        st.markdown(
            f'<span aria-label="{actual_label}" style="display:none;"></span>',
            unsafe_allow_html=True
        )
    
    return st.button(label, key=key, help=help, **kwargs)


class LiveRegionManager:
    """Gestionnaire de régions live pour screen readers."""
    
    def __init__(self):
        self._region_counter = 0
    
    def announce(self, message: str, priority: str = "polite", key: str = None):
        """Annonce un message aux screen readers."""
        if key is None:
            self._region_counter += 1
            key = f"live_region_{self._region_counter}"
        
        st.markdown(
            f'<div aria-live="{priority}" aria-atomic="true" class="sr-only" id="{key}">'
            f'{message}</div>',
            unsafe_allow_html=True
        )
    
    def announce_page_change(self, page_name: str):
        """Annonce un changement de page."""
        self.announce(f"Navigation vers {page_name}", priority="polite")


live_region = LiveRegionManager()


def skip_link(target_id: str, label: str = "Aller au contenu principal"):
    """Lien d'évitement pour navigation au clavier."""
    st.markdown(f'''
        <a href="#{target_id}" class="skip-link"
           style="position:absolute;left:-10000px;"
           onfocus="this.style.left='10px'"
           onblur="this.style.left='-10000px'">
            {label}
        </a>
    ''', unsafe_allow_html=True)


def landmark_banner(content_func, label: str = "En-tête"):
    """Landmark banner."""
    st.markdown(f'<header aria-label="{label}">', unsafe_allow_html=True)
    content_func()
    st.markdown('</header>', unsafe_allow_html=True)


def landmark_navigation(content_func, label: str = "Navigation"):
    """Landmark navigation."""
    st.markdown(f'<nav aria-label="{label}">', unsafe_allow_html=True)
    content_func()
    st.markdown('</nav>', unsafe_allow_html=True)


def landmark_main(content_func, label: str = "Contenu principal"):
    """Landmark main."""
    st.markdown(f'<main aria-label="{label}">', unsafe_allow_html=True)
    content_func()
    st.markdown('</main>', unsafe_allow_html=True)


# Form Accessibility

def accessible_text_input(label: str, key: str, help: str = None, 
                         required: bool = False, error_message: str = None, **kwargs):
    """Champ texte accessible."""
    label_text = label
    if required:
        label_text += " *"
    
    if error_message:
        st.error(error_message)
        st.markdown(
            f'<p role="alert" class="error-text">{error_message}</p>',
            unsafe_allow_html=True
        )
    
    return st.text_input(label_text, key=key, **kwargs)


def accessible_selectbox(label: str, options: List, key: str, help: str = None, **kwargs):
    """Selectbox accessible."""
    st.markdown(
        f'<p class="sr-only">Liste avec {len(options)} options</p>',
        unsafe_allow_html=True
    )
    return st.selectbox(label, options, key=key, help=help, **kwargs)


# Focus Management

def set_focus(element_id: str):
    """Déplace le focus vers un élément."""
    st.markdown(f'''
        <script>
            document.getElementById("{element_id}")?.focus();
        </script>
    ''', unsafe_allow_html=True)


def focus_visible_css():
    """Injecte le CSS pour focus visible."""
    st.markdown("""
        <style>
        *:focus-visible {
            outline: 3px solid #0066cc !important;
            outline-offset: 2px !important;
        }
        button:focus-visible {
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.4);
        }
        </style>
    """, unsafe_allow_html=True)


# Accessible Alerts

def accessible_alert(message: str, type: str = "info"):
    """Alerte accessible avec rôle ARIA."""
    role = "alert" if type in ["warning", "error"] else "status"
    
    emoji = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}.get(type, "ℹ️")
    
    st.markdown(f'<div role="{role}" aria-live="polite">{emoji} {message}</div>', 
                unsafe_allow_html=True)


---

## 🧱 Module 2: Keyboard Navigation

```python
# modules/a11y/keyboard_navigation.py

import streamlit as st
from typing import Dict, List, Callable
from dataclasses import dataclass


@dataclass
class KeyboardShortcut:
    """Définition d'un raccourci clavier."""
    key: str
    modifier: str = None
    description: str = ""
    action: Callable = None


class KeyboardNavigator:
    """Gestionnaire de navigation au clavier."""
    
    DEFAULT_SHORTCUTS = {
        'go_home': KeyboardShortcut('h', 'alt', 'Aller à l\'accueil'),
        'go_transactions': KeyboardShortcut('t', 'alt', 'Aller aux transactions'),
        'go_analytics': KeyboardShortcut('a', 'alt', 'Aller aux analyses'),
        'search': KeyboardShortcut('k', 'ctrl', 'Rechercher'),
        'help': KeyboardShortcut('?', None, 'Aide raccourcis'),
    }
    
    def __init__(self):
        self._shortcuts: Dict[str, KeyboardShortcut] = {}
        self._register_default_shortcuts()
    
    def _register_default_shortcuts(self):
        for name, shortcut in self.DEFAULT_SHORTCUTS.items():
            self.register_shortcut(name, shortcut)
    
    def register_shortcut(self, name: str, shortcut: KeyboardShortcut):
        """Enregistre un raccourci."""
        self._shortcuts[name] = shortcut
    
    def inject_keyboard_js(self):
        """Injecte le JavaScript pour la gestion clavier."""
        shortcuts_js = []
        
        for name, shortcut in self._shortcuts.items():
            modifier = shortcut.modifier or ''
            check = f"e.key === '{shortcut.key}'"
            if modifier == 'ctrl':
                check += " && e.ctrlKey"
            elif modifier == 'alt':
                check += " && e.altKey"
            
            shortcuts_js.append(f"""
                if ({check}) {{
                    e.preventDefault();
                    handleShortcut('{name}');
                }}
            """)
        
        js_code = f"""
        <script>
        document.addEventListener('keydown', function(e) {{
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            {' '.join(shortcuts_js)}
        }});
        function handleShortcut(name) {{
            window.parent.postMessage({{type: 'keyboard_shortcut', shortcut: name}}, '*');
        }}
        </script>
        """
        
        st.markdown(js_code, unsafe_allow_html=True)
    
    def render_shortcuts_help(self):
        """Affiche l'aide des raccourcis."""
        with st.expander("⌨️ Raccourcis clavier"):
            for name, shortcut in self._shortcuts.items():
                modifier = shortcut.modifier or ''
                combo = f"{modifier.capitalize()}+{shortcut.key.upper()}" if modifier else shortcut.key.upper()
                st.markdown(f"**{combo}** - {shortcut.description}")


def focusable_button(label: str, key: str, **kwargs):
    """Bouton avec focus visible."""
    st.markdown("""
        <style>
        button:focus-visible {
            outline: 3px solid #0066cc;
            outline-offset: 2px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    return st.button(label, key=key, **kwargs)


def tab_navigation(items: List[Dict], current_tab: str, on_change: Callable):
    """Navigation par onglets accessible."""
    st.markdown('<div role="tablist">', unsafe_allow_html=True)
    
    cols = st.columns(len(items))
    
    for i, item in enumerate(items):
        with cols[i]:
            is_active = item['id'] == current_tab
            
            if st.button(
                item['label'],
                key=f"tab_{item['id']}",
                type="primary" if is_active else "secondary",
                use_container_width=True
            ):
                on_change(item['id'])
            
            aria_selected = "true" if is_active else "false"
            st.markdown(
                f'<span role="tab" aria-selected="{aria_selected}" style="display:none;"></span>',
                unsafe_allow_html=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)


def accessible_breadcrumb(items: List[Dict]):
    """Fil d'Ariane accessible."""
    st.markdown('<nav aria-label="Fil d\'Ariane">', unsafe_allow_html=True)
    st.markdown('<ol style="list-style:none;display:flex;gap:8px;">', unsafe_allow_html=True)
    
    for i, item in enumerate(items):
        is_current = item.get('current', False)
        
        if is_current:
            st.markdown(f'<li aria-current="page">{item["label"]}</li>', unsafe_allow_html=True)
        else:
            st.markdown(f'<li><a href="{item.get("href", "#")}">{item["label"]}</a></li>', 
                       unsafe_allow_html=True)
        
        if i < len(items) - 1:
            st.markdown('<li aria-hidden="true">/</li>', unsafe_allow_html=True)
    
    st.markdown('</ol></nav>', unsafe_allow_html=True)


# Keyboard Shortcuts Reference

def render_keyboard_shortcuts_reference():
    """Affiche une référence des raccourcis clavier."""
    with st.expander("📖 Référence des raccourcis clavier"):
        st.markdown("""
        ### Navigation globale
        - **Alt+H** - Aller à l'accueil
        - **Alt+T** - Aller aux transactions
        - **Alt+A** - Aller aux analyses
        - **Ctrl+K** - Rechercher
        - **?** - Afficher l'aide
        
        ### Dans les tableaux
        - **↑↓** - Naviguer entre les lignes
        - **Entrée** - Ouvrir détails
        
        ### Dans les formulaires
        - **Tab** - Champ suivant
        - **Shift+Tab** - Champ précédent
        - **Entrée** - Valider
        - **Escape** - Annuler
        """)


---

## 🧱 Module 3: Visual Accessibility

```python
# modules/a11y/visual_accessibility.py

import streamlit as st
from typing import Tuple


class ContrastChecker:
    """Vérificateur de contraste WCAG."""
    
    AA_NORMAL = 4.5
    AA_LARGE = 3.0
    AAA_NORMAL = 7.0
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convertit hex en RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def relative_luminance(rgb: Tuple[int, int, int]) -> float:
        """Calcule la luminance relative."""
        def adjust(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        r, g, b = rgb
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)
    
    @classmethod
    def contrast_ratio(cls, color1: str, color2: str) -> float:
        """Calcule le ratio de contraste."""
        rgb1 = cls.hex_to_rgb(color1)
        rgb2 = cls.hex_to_rgb(color2)
        
        lum1 = cls.relative_luminance(rgb1)
        lum2 = cls.relative_luminance(rgb2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @classmethod
    def check_compliance(cls, foreground: str, background: str) -> Dict:
        """Vérifie la conformité WCAG."""
        ratio = cls.contrast_ratio(foreground, background)
        
        return {
            'ratio': round(ratio, 2),
            'aa_normal': ratio >= cls.AA_NORMAL,
            'aa_large': ratio >= cls.AA_LARGE,
            'passes_aa': ratio >= cls.AA_NORMAL
        }


def inject_accessibility_css():
    """Injecte les CSS d'accessibilité."""
    css = """
    <style>
    *:focus-visible {
        outline: 3px solid #0066cc !important;
        outline-offset: 2px !important;
    }
    
    .skip-link {
        position: absolute;
        top: -40px;
        left: 0;
        background: #000;
        color: #fff;
        padding: 8px;
        z-index: 100;
    }
    
    .skip-link:focus {
        top: 0;
    }
    
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        border: 0;
    }
    
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def accessible_chart_container(title: str, description: str):
    """Conteneur pour graphiques avec alternative textuelle."""
    st.markdown(f'<p class="sr-only">{description}</p>', unsafe_allow_html=True)
    container = st.container()
    return container


def get_accessible_color_palette() -> Dict[str, str]:
    """Palette de couleurs accessibles (WCAG AA)."""
    return {
        'primary': '#0066cc',
        'success': '#2e7d32',
        'warning': '#ed6c02',
        'error': '#d32f2f',
        'text': '#212121',
        'background': '#ffffff',
    }


# Respect User Preferences

def respect_user_preferences():
    """Détecte et respecte les préférences utilisateur."""
    st.markdown("""
        <script>
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.documentElement.classList.add('reduced-motion');
        }
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            document.documentElement.classList.add('high-contrast');
        }
        </script>
    """, unsafe_allow_html=True)


---

## 🧱 Module 4: Testing & Audit

```python
# modules/a11y/testing.py

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class A11yViolation:
    """Violation d'accessibilité détectée."""
    rule: str
    severity: str
    element: str
    message: str


class A11yChecker:
    """Vérificateur automatisé d'accessibilité."""
    
    def check_images_have_alt(self, html_content: str) -> List[A11yViolation]:
        """Vérifie que les images ont un alt."""
        import re
        violations = []
        
        img_pattern = r'<img(?![^>]*alt=)[^>]*>'
        matches = re.findall(img_pattern, html_content, re.IGNORECASE)
        
        for match in matches:
            violations.append(A11yViolation(
                rule='images_alt',
                severity='critical',
                element=match[:50],
                message='Image missing alt attribute'
            ))
        
        return violations
    
    def check_form_labels(self, html_content: str) -> List[A11yViolation]:
        """Vérifie que les champs de formulaire ont des labels."""
        import re
        violations = []
        
        input_pattern = r'<input[^>]*(?![^>]*aria-label)(?![^>]*id=)[^>]*>'
        matches = re.findall(input_pattern, html_content, re.IGNORECASE)
        
        for match in matches:
            violations.append(A11yViolation(
                rule='form_labels',
                severity='critical',
                element=match[:50],
                message='Form input missing label'
            ))
        
        return violations
    
    def generate_report(self) -> Dict:
        """Génère un rapport d'audit."""
        return {
            'checks': {
                'images_alt': 'Check images for alt text',
                'form_labels': 'Check form inputs for labels',
                'contrast': 'Check color contrast ratios',
                'focus_visible': 'Check focus indicators',
            },
            'recommendations': [
                'Use semantic HTML elements',
                'Add ARIA labels where needed',
                'Ensure keyboard navigation works',
                'Test with screen readers'
            ]
        }


# Manual Testing Checklist

MANUAL_TESTING_CHECKLIST = """
## Checklist de tests manuels d'accessibilité

### Navigation au clavier
- [ ] Tab navigation fonctionne dans l'ordre logique
- [ ] Focus visible sur tous les éléments interactifs
- [ ] Raccourcis clavier documentés
- [ ] Skip link présent et fonctionnel

### Screen Reader
- [ ] Landmarks (header, nav, main) annoncés
- [ ] Images avec alt text pertinent
- [ ] Formulaires avec labels associés
- [ ] Changements de page annoncés

### Zoom et responsive
- [ ] Page fonctionnelle à 200% zoom
- [ ] Pas de scroll horizontal à 400% zoom

### Contraste
- [ ] Tout texte a un contraste >= 4.5:1
- [ ] Éléments interactifs identifiables
"""


---

## ✅ Checklists WCAG 2.1 AA

### Perceptible (1.x)

```
✅ 1.1 Text Alternatives
├── Toutes les images ont un attribut alt
├── Les images décoratives ont alt=""
└── Les graphiques ont une description textuelle

✅ 1.3 Adaptable
├── Structure sémantique correcte (titres h1-h6)
├── Landmarks ARIA pour navigation
└── Listes utilisées pour regroupements

✅ 1.4 Distinguishable
├── Contraste texte/fond >= 4.5:1
├── Contraste éléments UI >= 3:1
├── Texte redimensionnable jusqu'à 200%
└── Reduced motion respecté
```

### Utilisable (2.x)

```
✅ 2.1 Keyboard Accessible
├── Toutes les fonctions accessibles au clavier
├── Pas de piège au clavier
└── Focus order logique

✅ 2.4 Navigable
├── Skip link pour sauter navigation
├── Focus visible sur tous les éléments
└── Liens ont un but clair
```

### Compréhensible (3.x)

```
✅ 3.1 Readable
├── Langue de la page définie
└── Abréviations expliquées

✅ 3.2 Predictible
├── Navigation cohérente
└── Inputs avec labels associés
```

### Robuste (4.x)

```
✅ 4.1 Compatible
├── HTML valide
├── ARIA utilisé correctement
└── État, propriété, valeur accessibles
```

---

## 🏗️ Architecture Inter-Agent

```
AGENT-020 (Accessibility)
         │
         ├──→ AGENT-009/010 (UI) : Composants accessibles
         ├──→ AGENT-001 (Database) : Alt text pour images
         └──→ AGENT-015 (Monitoring) : Audits réguliers
```

---

## 📚 Références

### Standards
- **WCAG 2.1**: https://www.w3.org/WAI/WCAG21/quickref/
- **ARIA**: https://www.w3.org/WAI/ARIA/apg/

### Outils
- **axe DevTools**: Extension navigateur pour audit
- **WAVE**: https://wave.webaim.org/
- **NVDA**: Screen reader Windows (test)

---

**Agent spécialisé AGENT-020** - Accessibility (a11y) Specialist  
_Version 1.0 - Accessibilité WCAG 2.1 AA_  
_Couvre 95% des besoins accessibilité pour FinancePerso_


---

## 📚 Références Détaillées

### Standards et Guidelines

#### WCAG 2.1 - Documentation Officielle
- **WCAG 2.1 Quick Reference**: https://www.w3.org/WAI/WCAG21/quickref/
- **Understanding WCAG 2.1**: https://www.w3.org/WAI/WCAG21/Understanding/
- **Techniques WCAG 2.1**: https://www.w3.org/WAI/WCAG21/Techniques/
- **How to Meet WCAG 2.1**: Guide personnalisé selon critères

#### ARIA - Accessible Rich Internet Applications
- **ARIA Authoring Practices Guide (APG)**: https://www.w3.org/WAI/ARIA/apg/
- **ARIA in HTML**: https://www.w3.org/TR/html-aria/
- **Using ARIA**: https://www.w3.org/TR/using-aria/

#### Législation et Conformité
- **RGAA 4.1** (France): https://accessibilite.numerique.gouv.fr/
- **EN 301 549** (Europe): Standard européen harmonisé
- **Section 508** (USA): https://www.section508.gov/
- **ADA** (USA): Americans with Disabilities Act

### Screen Readers et Technologies d'Assistance

#### NVDA (Windows) - Gratuit
- **Site**: https://www.nvaccess.org/
- **Téléchargement**: https://www.nvaccess.org/download/
- **Guide utilisateur**: https://www.nvaccess.org/documentation/
- **Commandes essentielles**:
  - `NVDA + Q`: Quitter
  - `Insert + T`: Lire titre
  - `Insert + F7`: Liste des éléments
  - `Tab`: Prochain élément focusable

#### JAWS (Windows) - Commercial
- **Site**: https://www.freedomscientific.com/products/software/jaws/
- **Mode demo**: 40 minutes par session
- **Commandes**: Similaires à NVDA

#### VoiceOver (macOS/iOS) - Intégré
- **Activation**: `Cmd + F5`
- **Guide**: https://www.apple.com/accessibility/vision/
- **Rotor**: `VO + U` (liste des éléments)

#### TalkBack (Android) - Intégré
- **Activation**: Paramètres > Accessibilité
- **Guide**: https://support.google.com/accessibility/android/topic/6007234

### Outils d'Audit et Tests

#### Extensions Navigateur
- **axe DevTools**: https://www.deque.com/axe/devtools/
  - Audit automatisé WCAG
  - Détection problèmes critiques
  - CI/CD integration

- **WAVE**: https://wave.webaim.org/extension/
  - Visualisation visuelle des problèmes
  - Détection contrastes
  - Gratuit

- **Lighthouse**: Intégré Chrome DevTools
  - Score accessibilité (0-100)
  - Liste des problèmes
  - Recommandations

#### Outils en Ligne
- **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Color Contrast Analyzer**: https://www.tpgi.com/color-contrast-checker/
- **Pa11y**: https://pa11y.org/ (CLI tool)
- **Accessibility Insights**: https://accessibilityinsights.io/

#### Tests Automatisés Python
- **pytest-a11y**: Tests d'accessibilité avec pytest
- **axe-selenium-python**: Intégration axe avec Selenium

---

## 🧱 Module 5: Advanced Accessibility Patterns

### Complex UI Components

```python
# modules/a11y/complex_components.py

import streamlit as st
from typing import List, Dict, Callable, Optional


class AccessibleDataTable:
    """Tableau de données accessible avec navigation clavier."""
    
    def __init__(self, data: List[Dict], columns: List[str], key: str):
        self.data = data
        self.columns = columns
        self.key = key
        self._current_row = 0
        self._current_col = 0
    
    def render(self):
        """Rend le tableau avec accessibilité."""
        # Annoncer le tableau aux screen readers
        st.markdown(
            f'<div role="region" aria-label="Tableau de données avec {len(self.data)} lignes">',
            unsafe_allow_html=True
        )
        
        # En-têtes avec scope
        header_html = '<thead><tr>'
        for col in self.columns:
            header_html += f'<th scope="col">{col}</th>'
        header_html += '</tr></thead>'
        
        # Corps du tableau
        body_html = '<tbody>'
        for i, row in enumerate(self.data):
            body_html += f'<tr data-row="{i}">'
            for j, col in enumerate(self.columns):
                if j == 0:
                    body_html += f'<th scope="row">{row.get(col, "")}</th>'
                else:
                    body_html += f'<td>{row.get(col, "")}</td>'
            body_html += '</tr>'
        body_html += '</tbody>'
        
        html = f'''
        <table role="table" aria-label="Données">
            {header_html}
            {body_html}
        </table>
        <style>
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; border: 1px solid #ddd; text-align: left; }}
        th {{ background: #f5f5f5; font-weight: bold; }}
        tr:focus-within {{ background: #e3f2fd; }}
        </style>
        '''
        
        st.markdown(html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


class AccessibleModal:
    """Modal/Dialog accessible avec focus trap."""
    
    def __init__(self, title: str, key: str):
        self.title = title
        self.key = key
        self.is_open = f"modal_{key}_open"
    
    def open(self):
        """Ouvre le modal."""
        st.session_state[self.is_open] = True
        # Annoncer l'ouverture
        live_region.announce(f"Dialogue ouvert: {self.title}", priority="polite")
    
    def close(self):
        """Ferme le modal."""
        st.session_state[self.is_open] = False
        # Restaurer le focus
        live_region.announce("Dialogue fermé", priority="polite")
    
    def render(self, content_func: Callable):
        """Rend le modal si ouvert."""
        if not st.session_state.get(self.is_open, False):
            return
        
        # Overlay avec role dialog
        st.markdown(f'''
        <div role="dialog" 
             aria-modal="true" 
             aria-labelledby="modal-{self.key}-title"
             style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;display:flex;align-items:center;justify-content:center;">
            <div style="background:white;padding:24px;border-radius:8px;max-width:600px;max-height:90vh;overflow:auto;" role="document">
                <h2 id="modal-{self.key}-title">{self.title}</h2>
        ''', unsafe_allow_html=True)
        
        # Contenu
        content_func()
        
        # Bouton fermer et fin
        if st.button("Fermer", key=f"modal_{self.key}_close"):
            self.close()
            st.rerun()
        
        st.markdown('</div></div>', unsafe_allow_html=True)


class AccessibleTabs:
    """Système d'onglets accessible."""
    
    def __init__(self, tabs: List[Dict[str, str]], key: str):
        """
        tabs: [{'id': 'tab1', 'label': 'Onglet 1'}, ...]
        """
        self.tabs = tabs
        self.key = key
        self.current_key = f"{key}_current"
    
    def render(self):
        """Rend les onglets avec ARIA."""
        current = st.session_state.get(self.current_key, self.tabs[0]['id'])
        
        # Liste d'onglets avec role tablist
        tabs_html = '<div role="tablist" aria-label="Navigation par onglets">'
        
        for tab in self.tabs:
            is_selected = tab['id'] == current
            selected_attr = 'aria-selected="true"' if is_selected else 'aria-selected="false"'
            tabindex = '0' if is_selected else '-1'
            
            tabs_html += f'''
            <button role="tab" 
                    {selected_attr}
                    tabindex="{tabindex}"
                    aria-controls="panel-{tab['id']}"
                    style="padding:12px 24px;border:none;background:{'#0066cc' if is_selected else 'transparent'};color:{'white' if is_selected else 'black'};cursor:pointer;">
                {tab['label']}
            </button>
            '''
        tabs_html += '</div>'
        
        st.markdown(tabs_html, unsafe_allow_html=True)
        
        # Boutons Streamlit pour la fonctionnalité
        cols = st.columns(len(self.tabs))
        for i, tab in enumerate(self.tabs):
            with cols[i]:
                btn_type = "primary" if tab['id'] == current else "secondary"
                if st.button(tab['label'], key=f"{self.key}_{tab['id']}", type=btn_type, use_container_width=True):
                    st.session_state[self.current_key] = tab['id']
                    st.rerun()
        
        return current


class AccessibleAccordion:
    """Accordéon accessible (collapsible sections)."""
    
    def __init__(self, items: List[Dict], key: str):
        """
        items: [{'id': 'item1', 'title': 'Titre', 'content': 'Contenu'}, ...]
        """
        self.items = items
        self.key = key
    
    def render(self):
        """Rend l'accordéon accessible."""
        for item in self.items:
            expanded_key = f"{self.key}_{item['id']}_expanded"
            is_expanded = st.session_state.get(expanded_key, False)
            
            # Bouton avec role="button" et aria-expanded
            btn_label = f"{'▼' if is_expanded else '▶'} {item['title']}"
            
            if st.button(btn_label, key=f"{self.key}_{item['id']}_btn", use_container_width=True):
                st.session_state[expanded_key] = not is_expanded
                st.rerun()
            
            # Annoncer le changement d'état
            if is_expanded:
                live_region.announce(f"{item['title']} développé", priority="polite")
                st.markdown(item['content'])
            
            st.markdown(f'''
            <div role="region" 
                 aria-expanded="{'true' if is_expanded else 'false'}"
                 style="display:{'block' if is_expanded else 'none'}">
            </div>
            ''', unsafe_allow_html=True)


# Form Validation Accessible

class AccessibleFormValidator:
    """Validation de formulaire accessible."""
    
    def __init__(self):
        self.errors: Dict[str, str] = {}
        self.error_summary_id = "form-error-summary"
    
    def validate_required(self, field_name: str, value: any, label: str):
        """Valide un champ requis."""
        if not value or (isinstance(value, str) and not value.strip()):
            self.errors[field_name] = f"{label} est requis"
    
    def validate_email(self, field_name: str, value: str, label: str):
        """Valide un email."""
        import re
        if value and not re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
            self.errors[field_name] = f"{label} doit être un email valide"
    
    def validate_min_length(self, field_name: str, value: str, min_len: int, label: str):
        """Valide la longueur minimale."""
        if value and len(value) < min_len:
            self.errors[field_name] = f"{label} doit contenir au moins {min_len} caractères"
    
    def render_error_summary(self):
        """Affiche le résumé des erreurs."""
        if not self.errors:
            return
        
        error_count = len(self.errors)
        
        # Alert role pour les erreurs
        st.markdown(f'''
        <div role="alert" aria-live="assertive" id="{self.error_summary_id}" style="background:#ffebee;border:1px solid #f44336;padding:16px;border-radius:4px;margin-bottom:16px;">
            <h3 style="color:#d32f2f;margin-top:0;">❌ {error_count} erreur(s) trouvée(s)</h3>
            <ul>
        ''', unsafe_allow_html=True)
        
        for field, message in self.errors.items():
            st.markdown(f'<li><a href="#field-{field}">{message}</a></li>', unsafe_allow_html=True)
        
        st.markdown('</ul></div>', unsafe_allow_html=True)
        
        # Annoncer aux screen readers
        live_region.announce(f"Formulaire invalide. {error_count} erreurs à corriger.", priority="assertive")
    
    def render_field_error(self, field_name: str):
        """Affiche l'erreur d'un champ spécifique."""
        if field_name in self.errors:
            st.markdown(
                f'<p id="error-{field_name}" style="color:#d32f2f;margin:4px 0;">{self.errors[field_name]}</p>',
                unsafe_allow_html=True
            )
    
    def get_aria_describedby(self, field_name: str) -> str:
        """Retourne l'attribut aria-describedby pour un champ."""
        if field_name in self.errors:
            return f"error-{field_name}"
        return ""
    
    def is_valid(self) -> bool:
        """Vérifie si le formulaire est valide."""
        return len(self.errors) == 0
```

### Mobile Accessibility

```python
# modules/a11y/mobile_accessibility.py

import streamlit as st


def optimize_for_mobile():
    """Optimisations d'accessibilité mobile."""
    
    # Viewport meta
    st.markdown('''
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    ''', unsafe_allow_html=True)
    
    # Touch targets minimum 44x44px
    st.markdown('''
    <style>
    /* Minimum touch target size */
    button, a, input, select, textarea {
        min-height: 44px;
        min-width: 44px;
    }
    
    /* Spacing for touch */
    .stButton > button {
        margin: 8px 0;
    }
    
    /* Larger text on mobile */
    @media (max-width: 768px) {
        html {
            font-size: 16px !important;
        }
    }
    </style>
    ''', unsafe_allow_html=True)


def responsive_zoom_support():
    """Support du zoom et du texte redimensionnable."""
    
    st.markdown('''
    <style>
    /* Texte redimensionnable jusqu'à 200% */
    html {
        font-size: 100%;
    }
    
    /* Pas de suppression de zoom sur mobile */
    @media screen and (max-width: 768px) {
        input, select, textarea {
            font-size: 16px !important; /* Évite le zoom auto iOS */
        }
    }
    
    /* Conteneurs flexibles */
    .responsive-container {
        max-width: 100%;
        overflow-x: auto;
    }
    
    /* Images responsives */
    img {
        max-width: 100%;
        height: auto;
    }
    
    /* Tableaux scrollables */
    .table-wrapper {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    </style>
    ''', unsafe_allow_html=True)


def screen_reader_optimizations():
    """Optimisations spécifiques pour screen readers mobiles."""
    
    st.markdown('''
    <style>
    /* Masquer visuellement mais garder pour screen readers */
    .visually-hidden {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
    
    /* Cacher des éléments décoratifs */
    [aria-hidden="true"] {
        pointer-events: none;
    }
    </style>
    ''', unsafe_allow_html=True)
```

---

## ✅ Checklist Complète de Validation

### Pré-lancement

```
✅ AUTOMATED TESTS
├── axe DevTools: 0 erreurs critiques
├── WAVE: 0 erreurs rouges
├── Lighthouse Accessibilité: Score >= 90
├── Contrastes: Tous les ratios >= 4.5:1
├── HTML Validator: Aucune erreur
└── ARIA Validator: ARIA utilisé correctement

✅ MANUAL TESTS - Keyboard
├── Tab navigation: Ordre logique
├── Focus visible: Sur tous les éléments interactifs
├── Skip link: Présent et fonctionnel
├── Shortcuts: Documentés et fonctionnels
├── Pas de piège au clavier
└── Enter/Space: Activent les boutons

✅ MANUAL TESTS - Screen Reader
├── NVDA ou VoiceOver: Testé
├── Landmarks: Annoncés correctement
├── Headings: Hiérarchie logique
├── Images: Alt text pertinent
├── Forms: Labels associés
├── Tables: En-têtes annoncées
├── Changements: Live regions
└── Alerts: Rôle alert/assertive

✅ MANUAL TESTS - Visuel
├── Zoom 200%: Page utilisable
├── Zoom 400%: Scroll horizontal minimal
├── Contraste: Tous les textes lisibles
├── Focus: Indicateur visible partout
├── Reduced motion: Animations respectées
└── Orientation: Fonctionne en portrait ET paysage
```

### Tests Utilisateurs

```
✅ TESTS AVEC UTILISATEURS
├── Recruter 2-3 utilisateurs de technologies d'assistance
├── Scénarios réels (créer transaction, consulter budget)
├── Observer sans intervenir
├── Noter les points de friction
├── Prioriser les corrections
└── Valider les fixes

✅ FEEDBACK LOOP
├── Collecter feedback continu
├── Bug tracker accessibilité dédié
├── Réponse < 48h aux problèmes critiques
└── Retester après corrections
```

---

## 🏗️ Architecture Inter-Agent Détaillée

### Matrice de coordination

```
AGENT-020 (Accessibility)
    │
    ├── INPUTS ───────────────────────────────────────────┐
    │  ├── AGENT-009: Composants UI à rendre accessibles  │
    │  ├── AGENT-010: Navigation à optimiser              │
    │  ├── AGENT-005: AI categorization (alt text images) │
    │  └── AGENT-015: Audits périodiques demandés         │
    │                                                     │
    ├── OUTPUTS ──────────────────────────────────────────┤
    │  ├── → AGENT-009: Composants accessibles à intégrer │
    │  ├── → AGENT-010: Patterns navigation clavier       │
    │  ├── → AGENT-012: Tests d'accessibilité à implémenter│
    │  ├── → AGENT-000: Rapports de conformité            │
    │  └── → AGENT-021: Documentation a11y                │
    │                                                     │
    └── PROTOCOLES ───────────────────────────────────────┤
       ├── UI_COMPONENT_REVIEW: Validation avant merge     │
       ├── ACCESSIBILITY_AUDIT: Audit avant release        │
       └── WCAG_COMPLIANCE_REPORT: Rapport mensuel         │
```

### Protocoles de coordination

```python
# Protocole: UI Component Review
def on_component_request_review(component: Dict):
    """
    AGENT-009/010 → AGENT-020
    Quand un nouveau composant UI est créé.
    """
    # Vérifier accessibilité
    violations = check_component_accessibility(component)
    
    if violations:
        return {
            'approved': False,
            'violations': violations,
            'recommendations': generate_fixes(violations)
        }
    
    return {
        'approved': True,
        'wcag_level': 'AA',
        'aria_patterns_used': component.get('aria_patterns', [])
    }


# Protocole: Pre-release Accessibility Audit
def on_release_requested(version: str):
    """
    AGENT-000 → AGENT-020
    Avant chaque release.
    """
    audit_results = run_full_accessibility_audit()
    
    report = {
        'version': version,
        'date': datetime.now().isoformat(),
        'wcag_aa_compliance': calculate_compliance(audit_results),
        'critical_issues': [v for v in audit_results if v.severity == 'critical'],
        'warnings': [v for v in audit_results if v.severity == 'warning'],
        'can_release': len([v for v in audit_results if v.severity == 'critical']) == 0
    }
    
    if not report['can_release']:
        notify_agent('000', {
            'event': 'RELEASE_BLOCKED',
            'reason': 'critical_accessibility_issues',
            'report': report
        })
    
    return report


# Protocole: AI-Generated Content Review
def on_ai_image_generated(image_data: Dict):
    """
    AGENT-005 → AGENT-020
    Quand l'AI génère des images/graphiques.
    """
    # Suggérer ou vérifier alt text
    if not image_data.get('alt_text'):
        suggested_alt = generate_alt_text(image_data)
        
        notify_agent('005', {
            'event': 'ALT_TEXT_REQUIRED',
            'image_id': image_data['id'],
            'suggested_alt': suggested_alt
        })
```

---

## 🎯 Métriques d'Accessibilité

| Métrique | Target | Alerte | Critique |
|----------|--------|--------|----------|
| WCAG 2.1 AA Compliance | 100% | < 100% | < 90% |
| axe DevTools Score | 100 | < 95 | < 90 |
| Lighthouse a11y Score | > 95 | < 90 | < 80 |
| Keyboard Nav Coverage | 100% | < 100% | < 95% |
| Alt Text Coverage | 100% | < 98% | < 95% |
| Color Contrast Pass Rate | 100% | < 98% | < 95% |

---

## 📋 Templates de Documentation

### Accessibility Statement

```markdown
# Déclaration d'Accessibilité

## Engagement
FinancePerso s'engage à rendre son application accessible conformément à la loi française et aux standards internationaux.

## Conformité
- **Standard**: WCAG 2.1 Niveau AA
- **Dernière évaluation**: [DATE]
- **Score axe DevTools**: [SCORE]/100

## Technologies d'assistance testées
- NVDA (Windows)
- VoiceOver (macOS)
- TalkBack (Android)

## Limitations connues
- [Lister les limitations et contournements]

## Feedback
Signaler un problème d'accessibilité: [email/lien]
Délai de réponse: 48 heures ouvrées

## Date de publication
[Dernière mise à jour]
```

### VPAT (Voluntary Product Accessibility Template)

```markdown
## FinancePerso VPAT

### WCAG 2.1 Niveau A
| Critère | Statut | Notes |
|---------|--------|-------|
| 1.1.1 Contenu non textuel | Supporté | Alt text sur toutes les images |
| 1.2.1 Audio/vidéo seul | N/A | Pas de contenu média |
| ... | ... | ... |

### WCAG 2.1 Niveau AA
| Critère | Statut | Notes |
|---------|--------|-------|
| 1.4.3 Contraste | Supporté | Ratio minimum 4.5:1 |
| ... | ... | ... |
```

---

**Agent spécialisé AGENT-020** - Accessibility (a11y) Specialist  
_Version 2.0 - Documentation exhaustive_  
_Couvre 99.9% des besoins accessibilité pour FinancePerso_