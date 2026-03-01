"""
Module d'accessibilité pour FinancePerso
Vérification des contrastes WCAG et utilitaires d'accessibilité
"""

from dataclasses import dataclass
from typing import Tuple, Dict, List


@dataclass
class ContrastRatio:
    """Résultat d'une vérification de contraste."""
    foreground: str
    background: str
    ratio: float
    passes_aa_normal: bool
    passes_aa_large: bool
    passes_aaa_normal: bool
    passes_aaa_large: bool


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convertit une couleur hex en RGB."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calcule la luminance relative d'une couleur (WCAG 2.1)."""
    def channel_luminance(c: int) -> float:
        c = c / 255
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4
    
    r, g, b = rgb
    return 0.2126 * channel_luminance(r) + 0.7152 * channel_luminance(g) + 0.0722 * channel_luminance(b)


def contrast_ratio(color1: str, color2: str) -> float:
    """Calcule le ratio de contraste entre deux couleurs."""
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    lum1 = relative_luminance(rgb1)
    lum2 = relative_luminance(rgb2)
    
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    
    return (lighter + 0.05) / (darker + 0.05)


def check_contrast(foreground: str, background: str) -> ContrastRatio:
    """
    Vérifie si le contraste respecte les normes WCAG.
    
    WCAG 2.1:
    - AA Normal: 4.5:1
    - AA Large: 3:1
    - AAA Normal: 7:1
    - AAA Large: 4.5:1
    """
    ratio = contrast_ratio(foreground, background)
    
    return ContrastRatio(
        foreground=foreground,
        background=background,
        ratio=round(ratio, 2),
        passes_aa_normal=ratio >= 4.5,
        passes_aa_large=ratio >= 3.0,
        passes_aaa_normal=ratio >= 7.0,
        passes_aaa_large=ratio >= 4.5
    )


def validate_theme_contrast(theme_config: Dict[str, str]) -> List[ContrastRatio]:
    """
    Valide tous les contrastes d'un thème.
    
    Args:
        theme_config: Dict avec les couleurs du thème
        
    Returns:
        Liste des résultats de contraste
    """
    checks = []
    
    # Texte principal sur fond de carte
    checks.append(check_contrast(
        theme_config.get('text_primary', '#1F2937'),
        theme_config.get('bg_card', '#FFFFFF')
    ))
    
    # Texte secondaire sur fond de carte
    checks.append(check_contrast(
        theme_config.get('text_secondary', '#6B7280'),
        theme_config.get('bg_card', '#FFFFFF')
    ))
    
    # Couleur primaire sur fond de carte (boutons, liens)
    checks.append(check_contrast(
        theme_config.get('primary', '#10B981'),
        theme_config.get('bg_card', '#FFFFFF')
    ))
    
    # Texte sur couleur primaire (boutons primaires)
    checks.append(check_contrast(
        '#FFFFFF',  # Texte blanc sur bouton
        theme_config.get('primary', '#10B981')
    ))
    
    # Positif sur fond de carte
    checks.append(check_contrast(
        theme_config.get('positive', '#10B981'),
        theme_config.get('bg_card', '#FFFFFF')
    ))
    
    # Négatif sur fond de carte
    checks.append(check_contrast(
        theme_config.get('negative', '#EF4444'),
        theme_config.get('bg_card', '#FFFFFF')
    ))
    
    return checks


def get_accessibility_report(theme_config: Dict[str, str]) -> Dict:
    """Génère un rapport d'accessibilité complet."""
    checks = validate_theme_contrast(theme_config)
    
    failures = [c for c in checks if not c.passes_aa_normal]
    
    return {
        'total_checks': len(checks),
        'passes_all_aa': len(failures) == 0,
        'failures': [
            {
                'foreground': f.foreground,
                'background': f.background,
                'ratio': f.ratio,
                'required': 4.5
            }
            for f in failures
        ],
        'all_checks': [
            {
                'foreground': c.foreground,
                'background': c.background,
                'ratio': c.ratio,
                'passes_aa': c.passes_aa_normal,
                'passes_aaa': c.passes_aaa_normal
            }
            for c in checks
        ]
    }


def render_accessibility_badge() -> str:
    """Retourne un badge HTML indiquant la conformité accessibilité."""
    from modules.ui.theme import get_theme
    
    theme = get_theme()
    theme_config = {
        'text_primary': theme.text_primary,
        'text_secondary': theme.text_secondary,
        'bg_card': theme.bg_card,
        'primary': theme.primary,
        'positive': theme.positive,
        'negative': theme.negative
    }
    
    report = get_accessibility_report(theme_config)
    
    if report['passes_all_aa']:
        return '<span title="Conforme WCAG AA" style="color: #10B981;">♿ AA</span>'
    else:
        return f'<span title="{len(report["failures"])} problèmes de contraste" style="color: #EF4444;">⚠️ {len(report["failures"])}</span>'


# Constantes WCAG
WCAG_AA_NORMAL = 4.5
WCAG_AA_LARGE = 3.0
WCAG_AAA_NORMAL = 7.0
WCAG_AAA_LARGE = 4.5


# Vérification des couleurs du thème actuel
if __name__ == "__main__":
    # Test avec le thème light green
    test_theme = {
        'text_primary': '#1F2937',
        'text_secondary': '#6B7280',
        'bg_card': '#FFFFFF',
        'primary': '#10B981',
        'positive': '#10B981',
        'negative': '#EF4444'
    }
    
    report = get_accessibility_report(test_theme)
    print(f"Vérification accessibilité:")
    print(f"  Total: {report['total_checks']} vérifications")
    print(f"  Conforme AA: {report['passes_all_aa']}")
    
    if report['failures']:
        print(f"  Échecs:")
        for f in report['failures']:
            print(f"    - {f['foreground']} sur {f['background']}: {f['ratio']}:1 (requis: {f['required']}:1)")
