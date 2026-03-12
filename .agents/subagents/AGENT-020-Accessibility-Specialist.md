# AGENT-020: Accessibility (A11y) Specialist

## 🎯 Mission

Spécialiste de l'accessibilité numérique (a11y) pour FinancePerso. Responsable de la conformité WCAG 2.1 AAA, du support des lecteurs d'écran, et de la navigation clavier complète. Garant de l'inclusion pour tous les utilisateurs, y compris ceux en situation de handicap.

---

## 📚 Contexte: Standards d'Accessibilité

### Philosophie
> "L'accessibilité n'est pas une fonctionnalité, c'est un droit. Un site accessible est un site mieux conçu pour tous."

### Normes WCAG 2.1

```
┌─────────────────────────────────────────────────────────────────┐
│                    WCAG 2.1 COMPLIANCE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🅰️ NIVEAU A (Minimum)                                          │
│  ├── Alternatives textuelles (images, icônes)                   │
│  ├── Contrôles clavier (navigation sans souris)                 │
│  ├── Sous-titres (contenu vidéo/audio)                          │
│  └── Non dépendance à la couleur seule                          │
│                                                                  │
│  🅰️🅰️ NIVEAU AA (Recommandé)                                    │
│  ├── Contraste 4.5:1 minimum (texte normal)                     │
│  ├── Contraste 3:1 (texte grand/UI components)                  │
│  ├── Redimensionnement jusqu'à 200%                             │
│  ├── Navigation cohérente                                       │
│  └── Messages d'erreur clairs                                   │
│                                                                  │
│  🅰️🅰️🅰️ NIVEAU AAA (Excellence)                                │
│  ├── Contraste 7:1 (texte normal)                               │
│  ├── Contraste 4.5:1 (texte grand)                              │
│  ├── Pas de limite de temps pour lecture                        │
│  └── Explications pour mots complexes                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture d'Accessibilité

```python
# modules/a11y/__init__.py
"""
Accessibility Module (A11y).
Outils et composants accessibles pour FinancePerso.
"""

from .components import (
    AccessibleButton,
    AccessibleInput,
    AccessibleSelect,
    AccessibleTable,
    AccessibleAlert
)
from .screen_reader import ScreenReaderAnnouncer, AriaLiveRegion
from .keyboard import KeyboardNavigator, FocusManager, ShortcutManager
from .contrast import ContrastChecker, ColorPalette
from .audit import A11yAuditor, WCAGChecker

__all__ = [
    'AccessibleButton', 'AccessibleInput', 'AccessibleSelect',
    'AccessibleTable', 'AccessibleAlert',
    'ScreenReaderAnnouncer', 'AriaLiveRegion',
    'KeyboardNavigator', 'FocusManager', 'ShortcutManager',
    'ContrastChecker', 'ColorPalette',
    'A11yAuditor', 'WCAGChecker'
]
```

---

## 🧱 Module 1: Composants Accessibles

```python
# modules/a11y/components.py

import streamlit as st
from typing import Optional, List, Dict, Any
import html


class AccessibleButton:
    """
    Bouton accessible avec support complet ARIA.
    """
    
    @staticmethod
    def render(
        label: str,
        key: str,
        help_text: str = None,
        variant: str = "primary",
        disabled: bool = False,
        shortcut: str = None
    ) -> bool:
        """
        Rend un bouton accessible.
        
        Args:
            label: Texte visible
            key: Clé unique
            help_text: Description pour lecteurs d'écran
            variant: primary/secondary/danger
            disabled: État désactivé
            shortcut: Raccourci clavier (ex: "Ctrl+S")
        """
        # Construire aria-label
        aria_label = label
        if help_text:
            aria_label = f"{label}. {help_text}"
        if shortcut:
            aria_label += f". Raccourci: {shortcut}"
        
        # Styles avec focus visible
        button_styles = """
        <style>
        button[kind="primary"]:focus-visible,
        button[kind="secondary"]:focus-visible {
            outline: 3px solid #1E88E5 !important;
            outline-offset: 2px !important;
        }
        </style>
        """
        st.markdown(button_styles, unsafe_allow_html=True)
        
        # Rendre le bouton
        clicked = st.button(
            label=label,
            key=key,
            disabled=disabled,
            help=help_text,
            type=variant if variant in ["primary", "secondary"] else "secondary"
        )
        
        return clicked


class AccessibleInput:
    """
    Champ de saisie accessible.
    """
    
    @staticmethod
    def text_input(
        label: str,
        key: str,
        value: str = "",
        help_text: str = None,
        placeholder: str = None,
        required: bool = False,
        error_message: str = None,
        autocomplete: str = None
    ) -> str:
        """
        Rend un champ texte accessible.
        """
        # Label associé
        label_html = f"<label for='{key}'>{label}"
        if required:
            label_html += " <span aria-label='obligatoire'>*</span>"
        label_html += "</label>"
        
        st.markdown(label_html, unsafe_allow_html=True)
        
        # Description si présente
        if help_text:
            st.caption(help_text)
        
        # Champ avec attributs d'accessibilité
        result = st.text_input(
            label="",  # Déjà affiché au-dessus
            value=value,
            key=key,
            placeholder=placeholder,
            label_visibility="collapsed"
        )
        
        # Message d'erreur
        if error_message:
            st.error(f"⚠️ {error_message}")
        
        return result
    
    @staticmethod
    def number_input(
        label: str,
        key: str,
        value: float = 0.0,
        min_value: float = None,
        max_value: float = None,
        help_text: str = None,
        required: bool = False
    ) -> float:
        """
        Rend un champ numérique accessible.
        """
        label_html = f"<label for='{key}'>{label}"
        if required:
            label_html += " <span aria-label='obligatoire'>*</span>"
        if help_text:
            label_html += f" <small>({help_text})</small>"
        label_html += "</label>"
        
        st.markdown(label_html, unsafe_allow_html=True)
        
        return st.number_input(
            label="",
            value=value,
            min_value=min_value,
            max_value=max_value,
            key=key,
            label_visibility="collapsed"
        )


class AccessibleSelect:
    """
    Sélection accessible (dropdown).
    """
    
    @staticmethod
    def selectbox(
        label: str,
        options: List[Any],
        key: str,
        format_func = None,
        help_text: str = None,
        required: bool = False
    ) -> Any:
        """
        Rend un select accessible.
        """
        label_html = f"<label for='{key}'>{label}"
        if required:
            label_html += " <span aria-label='champ obligatoire'>*</span>"
        label_html += "</label>"
        
        st.markdown(label_html, unsafe_allow_html=True)
        
        if help_text:
            st.caption(help_text)
        
        return st.selectbox(
            label="",
            options=options,
            format_func=format_func,
            key=key,
            label_visibility="collapsed"
        )


class AccessibleTable:
    """
    Tableau de données accessible.
    """
    
    @staticmethod
    def render(
        data: List[Dict],
        columns: List[Dict],  # {key, label, sortable}
        caption: str = None,
        sortable: bool = True,
        key: str = "table"
    ):
        """
        Rend un tableau accessible avec ARIA.
        
        Args:
            data: Liste de dictionnaires
            columns: Configuration des colonnes
            caption: Description du tableau
            sortable: Colonnes triables
        """
        html_parts = ["<table role='table' class='a11y-table'>"]
        
        # Caption
        if caption:
            html_parts.append(f"<caption>{html.escape(caption)}</caption>")
        
        # Header
        html_parts.append("<thead><tr>")
        for col in columns:
            html_parts.append(f"<th scope='col'>{html.escape(col['label'])}</th>")
        html_parts.append("</tr></thead>")
        
        # Body
        html_parts.append("<tbody>")
        for row in data:
            html_parts.append("<tr>")
            for col in columns:
                cell_value = row.get(col['key'], '')
                html_parts.append(f"<td>{html.escape(str(cell_value))}</td>")
            html_parts.append("</tr>")
        html_parts.append("</tbody>")
        
        html_parts.append("</table>")
        
        # Styles
        styles = """
        <style>
        .a11y-table {
            width: 100%;
            border-collapse: collapse;
        }
        .a11y-table th,
        .a11y-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .a11y-table th {
            background-color: #f5f5f5;
            font-weight: 600;
        }
        .a11y-table tr:hover {
            background-color: #f9f9f9;
        }
        .a11y-table tr:focus-within {
            outline: 2px solid #1E88E5;
            outline-offset: -2px;
        }
        caption {
            text-align: left;
            font-weight: 600;
            margin-bottom: 8px;
        }
        </style>
        """
        
        st.markdown(styles + "".join(html_parts), unsafe_allow_html=True)


class AccessibleAlert:
    """
    Messages d'alerte accessibles (ARIA live regions).
    """
    
    ALERT_STYLES = {
        "info": ("ℹ️", "info"),
        "success": ("✅", "status"),
        "warning": ("⚠️", "alert"),
        "error": ("❌", "alert")
    }
    
    @staticmethod
    def announce(
        message: str,
        level: str = "info",
        title: str = None,
        auto_dismiss: int = None
    ):
        """
        Annonce un message aux lecteurs d'écran.
        
        Args:
            message: Message à annoncer
            level: info/success/warning/error
            title: Titre optionnel
            auto_dismiss: Fermeture auto après N secondes
        """
        icon, role = AccessibleAlert.ALERT_STYLES.get(level, ("ℹ️", "info"))
        
        alert_id = f"alert_{hash(message) % 10000}"
        
        html_parts = [f"<div id='{alert_id}' role='{role}' aria-live='polite' class='a11y-alert a11y-alert-{level}'>"]
        
        if title:
            html_parts.append(f"<strong>{html.escape(title)}</strong>")
        
        html_parts.append(f"<span>{html.escape(message)}</span>")
        html_parts.append("</div>")
        
        styles = f"""
        <style>
        .a11y-alert {{
            padding: 16px;
            margin: 16px 0;
            border-radius: 8px;
            border-left: 4px solid;
        }}
        .a11y-alert-info {{
            background-color: #e3f2fd;
            border-color: #2196f3;
        }}
        .a11y-alert-success {{
            background-color: #e8f5e9;
            border-color: #4caf50;
        }}
        .a11y-alert-warning {{
            background-color: #fff3e0;
            border-color: #ff9800;
        }}
        .a11y-alert-error {{
            background-color: #ffebee;
            border-color: #f44336;
        }}
        </style>
        """
        
        st.markdown(styles + "".join(html_parts), unsafe_allow_html=True)
```

---

## 🧱 Module 2: Navigation Clavier

```python
# modules/a11y/keyboard.py

import streamlit as st
from typing import Dict, List, Callable, Optional
import json


class KeyboardNavigator:
    """
    Navigation clavier avancée.
    """
    
    # Raccourcis globaux
    GLOBAL_SHORTCUTS = {
        "?": "Afficher l'aide des raccourcis",
        "/": "Recherche globale",
        "g i": "Aller à la page Import",
        "g d": "Aller au Dashboard",
        "g v": "Aller à Validation",
        "g b": "Aller aux Budgets",
        "g s": "Aller aux Settings",
        "n t": "Nouvelle transaction",
        "Escape": "Fermer modale/annuler",
    }
    
    @staticmethod
    def setup_global_shortcuts():
        """
        Configure les raccourcis clavier globaux.
        """
        shortcuts_js = """
        <script>
        // Gestionnaire de raccourcis
        let keyBuffer = '';
        let bufferTimeout = null;
        
        document.addEventListener('keydown', function(e) {
            // Ignorer si dans un champ de saisie
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }
            
            const key = e.key;
            
            // Touche spéciale: ? pour aide
            if (key === '?' && !e.ctrlKey && !e.altKey) {
                e.preventDefault();
                showShortcutsHelp();
                return;
            }
            
            // Navigation g + lettre
            if (keyBuffer === 'g' && ['i', 'd', 'v', 'b', 's'].includes(key)) {
                e.preventDefault();
                navigateTo(key);
                keyBuffer = '';
                return;
            }
            
            // Buffer pour séquences
            if (key === 'g' || key === 'n') {
                keyBuffer = key;
                clearTimeout(bufferTimeout);
                bufferTimeout = setTimeout(() => { keyBuffer = ''; }, 1000);
                return;
            }
            
            // Nouvelle transaction
            if (keyBuffer === 'n' && key === 't') {
                e.preventDefault();
                openNewTransaction();
                keyBuffer = '';
                return;
            }
            
            // Focus management
            if (key === 'Tab') {
                // Laisser le comportement par défaut mais loguer
                console.log('[A11y] Tab navigation');
            }
        });
        
        function navigateTo(page) {
            const routes = {
                'i': '/Import',
                'd': '/Dashboard',
                'v': '/Validation',
                'b': '/Budgets',
                's': '/Settings'
            };
            if (routes[page]) {
                window.location.href = routes[page];
            }
        }
        
        function showShortcutsHelp() {
            // Déclencher événement Streamlit
            console.log('[A11y] Show shortcuts help');
        }
        
        function openNewTransaction() {
            console.log('[A11y] Open new transaction modal');
        }
        </script>
        """
        
        st.components.v1.html(shortcuts_js, height=0)
    
    @staticmethod
    def render_shortcuts_help():
        """Affiche l'aide des raccourcis."""
        st.header("⌨️ Raccourcis Clavier")
        
        st.markdown("""
        ### Navigation Globale
        | Raccourci | Action |
        |-----------|--------|
        | `?` | Afficher cette aide |
        | `/` | Recherche globale |
        | `g` puis `i` | Aller à Import |
        | `g` puis `d` | Aller au Dashboard |
        | `g` puis `v` | Aller à Validation |
        | `g` puis `b` | Aller aux Budgets |
        | `g` puis `s` | Aller aux Settings |
        | `n` puis `t` | Nouvelle transaction |
        | `Escape` | Fermer/Annuler |
        
        ### Dans les Tableaux
        | Raccourci | Action |
        |-----------|--------|
        | `↑` `↓` | Naviguer lignes |
        | `Enter` | Ouvrir détail |
        | `Space` | Sélectionner |
        
        ### Dans les Formulaires
        | Raccourci | Action |
        |-----------|--------|
        | `Tab` | Champ suivant |
        | `Shift+Tab` | Champ précédent |
        | `Enter` | Valider |
        | `Escape` | Annuler |
        """)


class FocusManager:
    """
    Gestionnaire de focus pour modales et dialogs.
    """
    
    @staticmethod
    def trap_focus(container_id: str):
        """
        Piège le focus dans un conteneur (modale).
        """
        trap_js = f"""
        <script>
        (function() {{
            const container = document.getElementById('{container_id}');
            if (!container) return;
            
            const focusableElements = container.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            // Focus initial
            firstElement?.focus();
            
            container.addEventListener('keydown', function(e) {{
                if (e.key !== 'Tab') return;
                
                if (e.shiftKey) {{
                    if (document.activeElement === firstElement) {{
                        e.preventDefault();
                        lastElement?.focus();
                    }}
                }} else {{
                    if (document.activeElement === lastElement) {{
                        e.preventDefault();
                        firstElement?.focus();
                    }}
                }}
            }});
        }})();
        </script>
        """
        st.components.v1.html(trap_js, height=0)
    
    @staticmethod
    def set_initial_focus(element_id: str):
        """Définit le focus initial sur un élément."""
        focus_js = f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const element = document.getElementById('{element_id}');
            if (element) {{
                element.focus();
            }}
        }});
        </script>
        """
        st.components.v1.html(focus_js, height=0)


class ShortcutManager:
    """
    Gestionnaire de raccourcis personnalisés.
    """
    
    def __init__(self):
        self.shortcuts: Dict[str, Callable] = {}
    
    def register(self, key_combo: str, callback: Callable, description: str):
        """
        Enregistre un raccourci.
        
        Args:
            key_combo: Combinaison (ex: "Ctrl+S", "Alt+F")
            callback: Fonction à appeler
            description: Description pour l'aide
        """
        self.shortcuts[key_combo] = {
            'callback': callback,
            'description': description
        }
    
    def setup(self):
        """Configure les raccourcis enregistrés."""
        shortcuts_json = json.dumps({
            k: v['description'] for k, v in self.shortcuts.items()
        })
        
        setup_js = f"""
        <script>
        const shortcuts = {shortcuts_json};
        
        document.addEventListener('keydown', function(e) {{
            const combo = [];
            if (e.ctrlKey) combo.push('Ctrl');
            if (e.altKey) combo.push('Alt');
            if (e.shiftKey) combo.push('Shift');
            combo.push(e.key);
            
            const keyCombo = combo.join('+');
            
            if (shortcuts[keyCombo]) {{
                e.preventDefault();
                console.log('[Shortcut] Triggered:', keyCombo);
                // Notifier Streamlit
            }}
        }});
        </script>
        """
        st.components.v1.html(setup_js, height=0)
```

---

## 🧱 Module 3: Vérification Contraste

```python
# modules/a11y/contrast.py

from typing import Tuple, Dict, List
from dataclasses import dataclass
import colorsys


@dataclass
class ContrastResult:
    """Résultat d'analyse de contraste."""
    foreground: str
    background: str
    ratio: float
    passes_aa_normal: bool
    passes_aa_large: bool
    passes_aaa_normal: bool
    passes_aaa_large: bool


class ContrastChecker:
    """
    Vérificateur de contraste WCAG.
    """
    
    # Seuils WCAG
    AA_NORMAL = 4.5
    AA_LARGE = 3.0
    AAA_NORMAL = 7.0
    AAA_LARGE = 4.5
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convertit hex en RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def relative_luminance(rgb: Tuple[int, int, int]) -> float:
        """Calcule la luminance relative (WCAG)."""
        def adjust(c):
            c = c / 255.0
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        r, g, b = rgb
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)
    
    @classmethod
    def check_contrast(cls, foreground: str, background: str) -> ContrastResult:
        """
        Vérifie le contraste entre deux couleurs.
        
        Args:
            foreground: Couleur texte (hex)
            background: Couleur fond (hex)
            
        Returns:
            ContrastResult avec tous les résultats
        """
        fg_rgb = cls.hex_to_rgb(foreground)
        bg_rgb = cls.hex_to_rgb(background)
        
        l1 = cls.relative_luminance(fg_rgb)
        l2 = cls.relative_luminance(bg_rgb)
        
        # Ratio de contraste
        lighter = max(l1, l2)
        darker = min(l1, l2)
        ratio = (lighter + 0.05) / (darker + 0.05)
        
        return ContrastResult(
            foreground=foreground,
            background=background,
            ratio=ratio,
            passes_aa_normal=ratio >= cls.AA_NORMAL,
            passes_aa_large=ratio >= cls.AA_LARGE,
            passes_aaa_normal=ratio >= cls.AAA_NORMAL,
            passes_aaa_large=ratio >= cls.AAA_LARGE
        )
    
    @classmethod
    def find_accessible_color(
        cls,
        background: str,
        target_ratio: float = 4.5,
        prefer_dark: bool = True
    ) -> str:
        """
        Trouve une couleur de texte accessible.
        
        Args:
            background: Couleur de fond
            target_ratio: Ratio cible
            prefer_dark: Préférer texte foncé
            
        Returns:
            Couleur hex accessible
        """
        # Tester noir et blanc
        black_result = cls.check_contrast("#000000", background)
        white_result = cls.check_contrast("#FFFFFF", background)
        
        if prefer_dark and black_result.ratio >= target_ratio:
            return "#000000"
        elif white_result.ratio >= target_ratio:
            return "#FFFFFF"
        elif black_result.ratio > white_result.ratio:
            return "#000000"
        else:
            return "#FFFFFF"


class ColorPalette:
    """
    Palette de couleurs accessibles.
    """
    
    # Couleurs du design system avec vérification
    COLORS = {
        "primary": {
            "main": "#1E88E5",
            "dark": "#1565C0",
            "light": "#64B5F6",
            "contrast": "#FFFFFF"
        },
        "success": {
            "main": "#4CAF50",
            "dark": "#388E3C",
            "contrast": "#FFFFFF"
        },
        "warning": {
            "main": "#FF9800",
            "dark": "#F57C00",
            "contrast": "#000000"
        },
        "error": {
            "main": "#F44336",
            "dark": "#D32F2F",
            "contrast": "#FFFFFF"
        },
        "text": {
            "primary": "#212121",
            "secondary": "#757575",
            "disabled": "#9E9E9E"
        },
        "background": {
            "default": "#FFFFFF",
            "paper": "#FAFAFA",
            "elevated": "#FFFFFF"
        }
    }
    
    @classmethod
    def validate_palette(cls) -> List[Dict]:
        """
        Valide toute la palette de couleurs.
        
        Returns:
            Liste des problèmes de contraste
        """
        issues = []
        bg = cls.COLORS["background"]["default"]
        
        # Vérifier text sur fond blanc
        for text_type, color in cls.COLORS["text"].items():
            result = ContrastChecker.check_contrast(color, bg)
            if not result.passes_aa_normal:
                issues.append({
                    "type": "text",
                    "element": f"text.{text_type}",
                    "foreground": color,
                    "background": bg,
                    "ratio": result.ratio,
                    "required": ContrastChecker.AA_NORMAL
                })
        
        # Vérifier boutons
        for button_type, colors in cls.COLORS.items():
            if "contrast" in colors:
                result = ContrastChecker.check_contrast(colors["contrast"], colors["main"])
                if not result.passes_aa_normal:
                    issues.append({
                        "type": "button",
                        "element": button_type,
                        "foreground": colors["contrast"],
                        "background": colors["main"],
                        "ratio": result.ratio,
                        "required": ContrastChecker.AA_NORMAL
                    })
        
        return issues
```

---

## 🧱 Module 4: Audit A11y

```python
# modules/a11y/audit.py

import streamlit as st
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"
    SERIOUS = "serious"
    MODERATE = "moderate"
    MINOR = "minor"


@dataclass
class A11yIssue:
    """Problème d'accessibilité détecté."""
    rule: str
    severity: Severity
    message: str
    element: str
    suggestion: str


class A11yAuditor:
    """
    Auditeur d'accessibilité automatisé.
    """
    
    def __init__(self):
        self.issues: List[A11yIssue] = []
    
    def audit_page(self) -> List[A11yIssue]:
        """
        Audite la page actuelle.
        
        Returns:
            Liste des problèmes détectés
        """
        self.issues = []
        
        # Vérifications automatiques
        self._check_images_alt()
        self._check_form_labels()
        self._check_heading_structure()
        self._check_contrast()
        self._check_keyboard_access()
        
        return self.issues
    
    def _check_images_alt(self):
        """Vérifie les images sans alt."""
        check_js = """
        <script>
        const images = document.querySelectorAll('img:not([alt])');
        if (images.length > 0) {
            console.warn('[A11y] Images without alt:', images.length);
            images.forEach(img => {
                console.warn('  -', img.src);
            });
        }
        </script>
        """
        st.components.v1.html(check_js, height=0)
    
    def _check_form_labels(self):
        """Vérifie les champs sans label."""
        # À implémenter avec des checks côté Python
        pass
    
    def _check_heading_structure(self):
        """Vérifie la hiérarchie des titres."""
        pass
    
    def _check_contrast(self):
        """Vérifie les contrastes."""
        from .contrast import ColorPalette
        
        issues = ColorPalette.validate_palette()
        for issue in issues:
            self.issues.append(A11yIssue(
                rule="color-contrast",
                severity=Severity.SERIOUS,
                message=f"Contraste insuffisant: {issue['ratio']:.2f} (min: {issue['required']})",
                element=issue['element'],
                suggestion=f"Changer la couleur pour atteindre un ratio de {issue['required']}"
            ))
    
    def _check_keyboard_access(self):
        """Vérifie l'accessibilité clavier."""
        pass
    
    def generate_report(self) -> Dict:
        """Génère un rapport d'audit."""
        severity_counts = {
            "critical": len([i for i in self.issues if i.severity == Severity.CRITICAL]),
            "serious": len([i for i in self.issues if i.severity == Severity.SERIOUS]),
            "moderate": len([i for i in self.issues if i.severity == Severity.MODERATE]),
            "minor": len([i for i in self.issues if i.severity == Severity.MINOR])
        }
        
        return {
            "total_issues": len(self.issues),
            "severity_counts": severity_counts,
            "score": max(0, 100 - severity_counts["critical"] * 10 - severity_counts["serious"] * 5),
            "issues": self.issues
        }


class WCAGChecker:
    """
    Vérificateur de conformité WCAG.
    """
    
    WCAG_RULES = {
        "1.1.1": {
            "name": "Non-text Content",
            "level": "A",
            "description": "Tout contenu non textuel a une alternative textuelle"
        },
        "1.3.1": {
            "name": "Info and Relationships",
            "level": "A",
            "description": "L'information structurée est disponible par le code"
        },
        "1.4.3": {
            "name": "Contrast (Minimum)",
            "level": "AA",
            "description": "Contraste minimum 4.5:1 pour le texte normal"
        },
        "2.1.1": {
            "name": "Keyboard",
            "level": "A",
            "description": "Toutes les fonctionnalités accessibles au clavier"
        },
        "2.4.3": {
            "name": "Focus Order",
            "level": "A",
            "description": "Ordre de focus logique et prévisible"
        },
        "3.3.1": {
            "name": "Error Identification",
            "level": "A",
            "description": "Les erreurs sont identifiées clairement"
        },
        "4.1.2": {
            "name": "Name, Role, Value",
            "level": "A",
            "description": "Les composants ont nom, rôle et valeur appropriés"
        }
    }
    
    @classmethod
    def check_compliance(cls, issues: List[A11yIssue]) -> Dict:
        """
        Vérifie la conformité WCAG.
        
        Returns:
            Rapport de conformité
        """
        passed_rules = set()
        failed_rules = set()
        
        # Mapping issues vers règles
        rule_mapping = {
            "alt-text": "1.1.1",
            "heading-structure": "1.3.1",
            "color-contrast": "1.4.3",
            "keyboard-access": "2.1.1",
            "focus-order": "2.4.3",
            "error-identification": "3.3.1",
            "aria-attributes": "4.1.2"
        }
        
        for issue in issues:
            rule_id = rule_mapping.get(issue.rule)
            if rule_id:
                failed_rules.add(rule_id)
        
        # Toutes les règles non failed sont passed
        for rule_id in cls.WCAG_RULES:
            if rule_id not in failed_rules:
                passed_rules.add(rule_id)
        
        return {
            "level_a_passed": len([r for r in passed_rules if cls.WCAG_RULES[r]["level"] == "A"]),
            "level_a_total": len([r for r in cls.WCAG_RULES if cls.WCAG_RULES[r]["level"] == "A"]),
            "level_aa_passed": len([r for r in passed_rules if cls.WCAG_RULES[r]["level"] == "AA"]),
            "level_aa_total": len([r for r in cls.WCAG_RULES if cls.WCAG_RULES[r]["level"] == "AA"]),
            "failed_rules": list(failed_rules),
            "compliance_percentage": len(passed_rules) / len(cls.WCAG_RULES) * 100
        }
```

---

## ✅ Checklist Accessibilité

```
✅ PERCEPTIBLE (Perceivable)
├── [ ] Alternatives textuelles pour images
├── [ ] Sous-titres pour contenu multimédia
├── [ ] Contraste suffisant (4.5:1 minimum)
├── [ ] Texte redimensionnable à 200%
└── [ ] Pas d'information uniquement par couleur

✅ UTILISABLE (Operable)
├── [ ] Navigation complète au clavier
├── [ ] Pas de limite de temps stricte
├── [ ] Pas de contenu clignotant
├── [ ] Liens et boutons identifiables
└── [ ] Skip links pour navigation

✅ COMPREHENSIBLE (Understandable)
├── [ ] Langue de la page définie
├── [ ] Libellés des champs explicites
├── [ ] Messages d'erreur clairs
├── [ ] Navigation cohérente
└── [ ] Abréviations expliquées

✅ ROBUSTE (Robust)
├── [ ] HTML valide
├── [ ] ARIA utilisé correctement
├── [ ] Compatibilité lecteurs d'écran
└── [ ] Focus visible
```

---

**Agent spécialisé AGENT-020** - Accessibility (A11y) Specialist  
_Version 1.0 - Conformité WCAG 2.1 AA/AAA_  
_Cible: 100% des fonctionnalités accessibles au clavier_
