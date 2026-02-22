"""UI Module v2 - Atomic Design Pattern.

Nouvelle architecture UI basée sur le pattern Atomic Design :
- Atoms: Éléments de base (icônes, couleurs, typographie)
- Molecules: Composants composés (toasts, banners, boutons)
- Organisms: Sections complètes (dialogs, flash messages)
- Templates: Layouts de page

Migration depuis l'ancienne structure:
    # Ancien (deprecated)
    from modules.ui.feedback import toast_success
    
    # Nouveau (recommandé)
    from modules.ui_v2.molecules.toasts import toast_success
"""

from modules.ui_v2.atoms.icons import IconSet
from modules.ui_v2.atoms.colors import ColorScheme

__all__ = ["IconSet", "ColorScheme"]
