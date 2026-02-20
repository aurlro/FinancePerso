"""UI Organisms - Sections complètes.

Les organisms sont des composants complexes qui combinent
plusieurs molecules pour former des sections fonctionnelles.

Examples:
    from modules.ui_v2.organisms.dialogs import confirm_delete, confirm_action
    from modules.ui_v2.organisms.flash_messages import set_flash, display_flashes
    from modules.ui_v2.organisms.progress import progress_tracker
"""

from modules.ui_v2.organisms.dialogs import confirm_delete, confirm_action
from modules.ui_v2.organisms.flash_messages import set_flash_message, display_flash_messages

__all__ = [
    "confirm_delete",
    "confirm_action",
    "set_flash_message",
    "display_flash_messages",
]
