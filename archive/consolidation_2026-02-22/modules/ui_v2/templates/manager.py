"""Dashboard Layout Manager for UI v2.

Gestionnaire de layout avec mode Preview et persistance en base de données.
"""

from typing import Any

import streamlit as st

from modules.db.dashboard_layouts import (
    get_active_layout,
    get_layout as get_layout_from_db,
    list_layouts,
    save_layout,
)
from modules.logger import logger
from modules.ui_v2.templates.layouts import DashboardWidget, DEFAULT_LAYOUT


class DashboardLayoutManager:
    """Gestionnaire de layout avec mode Preview et persistance DB.

    Cette classe gère le cycle de vie des layouts de dashboard:
    - Chargement depuis la base de données
    - Mode preview pour modifications temporaires
    - Sauvegarde et persistance
    - Gestion des widgets (position, visibilité)

    Attributes:
        layout_key: Clé unique pour ce layout dans le session_state
        preview_key: Clé pour le mode preview
    """

    def __init__(self, layout_key: str = "dashboard_layout"):
        """Initialise le gestionnaire de layout.

        Args:
            layout_key: Clé unique pour identifier ce layout
        """
        self.layout_key = layout_key
        self.preview_key = f"{layout_key}_preview"
        self._init_from_db()

    def _init_from_db(self) -> None:
        """Initialise le layout depuis la base de données."""
        if self.layout_key not in st.session_state:
            # Charger depuis la DB
            db_layout = get_active_layout()
            if db_layout:
                st.session_state[self.layout_key] = db_layout
            else:
                # Fallback aux valeurs par défaut
                st.session_state[self.layout_key] = [w.to_dict() for w in DEFAULT_LAYOUT]

    def get_layout(self, use_preview: bool = False) -> list[DashboardWidget]:
        """Récupère le layout actuel ou le preview.

        Args:
            use_preview: Si True, utilise le layout en cours de modification

        Returns:
            Liste des widgets visibles
        """
        key = self.preview_key if use_preview else self.layout_key
        layout_data = st.session_state.get(key, [])

        widgets = []
        for w in layout_data:
            if not w.get("visible", True):
                continue
            try:
                widget = DashboardWidget.from_dict(w)
                widgets.append(widget)
            except Exception as e:
                logger.warning(f"Skipping corrupted widget: {e}")
                continue

        # Si aucun widget valide, retourner le défaut
        if not widgets:
            logger.info("No valid widgets found, using default layout")
            return [w for w in DEFAULT_LAYOUT if w.visible]

        return widgets

    def get_all_widgets(self, use_preview: bool = False) -> list[DashboardWidget]:
        """Récupère tous les widgets (même cachés).

        Args:
            use_preview: Si True, utilise le layout preview

        Returns:
            Liste de tous les widgets
        """
        key = self.preview_key if use_preview else self.layout_key
        layout_data = st.session_state.get(key, [])
        return [DashboardWidget.from_dict(w) for w in layout_data]

    def start_preview(self) -> None:
        """Démarre le mode preview (copie le layout actuel)."""
        current = st.session_state.get(self.layout_key, [])
        st.session_state[self.preview_key] = [w.copy() for w in current]
        st.session_state[f"{self.layout_key}_preview_mode"] = True

    def cancel_preview(self) -> None:
        """Annule le mode preview et nettoie le session_state."""
        if self.preview_key in st.session_state:
            del st.session_state[self.preview_key]
        st.session_state[f"{self.layout_key}_preview_mode"] = False

    def apply_preview(self, layout_name: str = "custom") -> bool:
        """Applique le layout preview et le sauvegarde en DB.

        Args:
            layout_name: Nom du layout à sauvegarder

        Returns:
            True si la sauvegarde a réussi
        """
        preview = st.session_state.get(self.preview_key)
        if preview:
            # Met à jour le layout actif
            st.session_state[self.layout_key] = preview.copy()

            # Sauvegarde en DB
            success = save_layout(layout_name, preview, set_active=True)

            # Nettoie le preview
            self.cancel_preview()
            return success
        return False

    def is_preview_mode(self) -> bool:
        """Vérifie si on est en mode preview.

        Returns:
            True si en mode preview
        """
        return st.session_state.get(f"{self.layout_key}_preview_mode", False)

    def update_preview(self, widgets: list[DashboardWidget]) -> None:
        """Met à jour le layout en preview.

        Args:
            widgets: Liste des widgets à mettre en preview
        """
        st.session_state[self.preview_key] = [w.to_dict() for w in widgets]

    def move_widget(self, widget_id: str, new_position: int, use_preview: bool = True) -> None:
        """Déplace un widget à une nouvelle position.

        Args:
            widget_id: ID du widget à déplacer
            new_position: Nouvelle position (1-based)
            use_preview: Si True, modifie le preview
        """
        key = self.preview_key if use_preview else self.layout_key
        widgets_data = st.session_state.get(key, [])
        widgets = [DashboardWidget.from_dict(w) for w in widgets_data]

        widget = next((w for w in widgets if w.id == widget_id), None)
        if widget:
            # Retirer le widget de sa position actuelle
            widgets = [w for w in widgets if w.id != widget_id]
            # Insérer à la nouvelle position
            widget.position = new_position
            widgets.insert(min(new_position - 1, len(widgets)), widget)

            # Réindexer toutes les positions
            for i, w in enumerate(widgets, 1):
                w.position = i

            st.session_state[key] = [w.to_dict() for w in widgets]

    def toggle_widget_visibility(self, widget_id: str, use_preview: bool = True) -> None:
        """Active/désactive la visibilité d'un widget.

        Args:
            widget_id: ID du widget à basculer
            use_preview: Si True, modifie le preview
        """
        key = self.preview_key if use_preview else self.layout_key
        widgets_data = st.session_state.get(key, [])
        widgets = [DashboardWidget.from_dict(w) for w in widgets_data]

        for w in widgets:
            if w.id == widget_id:
                w.visible = not w.visible
                break

        st.session_state[key] = [w.to_dict() for w in widgets]

    def set_widget_size(self, widget_id: str, new_size: str, use_preview: bool = True) -> bool:
        """Change la taille d'un widget.

        Args:
            widget_id: ID du widget
            new_size: Nouvelle taille ('small', 'medium', 'large', 'full')
            use_preview: Si True, modifie le preview

        Returns:
            True si le widget a été trouvé et modifié
        """
        key = self.preview_key if use_preview else self.layout_key
        widgets_data = st.session_state.get(key, [])
        widgets = [DashboardWidget.from_dict(w) for w in widgets_data]

        for w in widgets:
            if w.id == widget_id:
                w.size = new_size
                st.session_state[key] = [w.to_dict() for w in widgets]
                return True
        return False

    def update_widget_config(self, widget_id: str, config: dict[str, Any], use_preview: bool = True) -> bool:
        """Met à jour la configuration d'un widget.

        Args:
            widget_id: ID du widget
            config: Nouvelle configuration (fusionnée avec l'existante)
            use_preview: Si True, modifie le preview

        Returns:
            True si le widget a été trouvé et modifié
        """
        key = self.preview_key if use_preview else self.layout_key
        widgets_data = st.session_state.get(key, [])
        widgets = [DashboardWidget.from_dict(w) for w in widgets_data]

        for w in widgets:
            if w.id == widget_id:
                w.config.update(config)
                st.session_state[key] = [w.to_dict() for w in widgets]
                return True
        return False

    def load_from_db(self, name: str) -> bool:
        """Charge un layout depuis la base de données.

        Args:
            name: Nom du layout à charger

        Returns:
            True si le layout a été trouvé et chargé
        """
        layout = get_layout_from_db(name)
        if layout:
            st.session_state[self.layout_key] = layout
            return True
        return False

    def reset_to_default(self) -> None:
        """Réinitialise au layout par défaut et sauvegarde."""
        st.session_state[self.layout_key] = [w.to_dict() for w in DEFAULT_LAYOUT]
        save_layout("default", st.session_state[self.layout_key], set_active=True)

    def save_current(self, name: str, set_active: bool = False) -> bool:
        """Sauvegarde le layout actuel.

        Args:
            name: Nom du layout
            set_active: Si True, définit comme layout actif

        Returns:
            True si la sauvegarde a réussi
        """
        current = st.session_state.get(self.layout_key, [])
        if current:
            return save_layout(name, current, set_active=set_active)
        return False

    def get_saved_layouts(self) -> list[dict[str, Any]]:
        """Récupère la liste des layouts sauvegardés.

        Returns:
            Liste des informations des layouts
        """
        return list_layouts()


__all__ = ["DashboardLayoutManager"]
