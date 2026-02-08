"""
Dashboard Cleanup Module
Gestion automatique et manuelle des problèmes de dashboard.
Peut être lancé au démarrage ou manuellement.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from modules.db.connection import get_db_connection
from modules.logger import logger


class CleanupScenario(Enum):
    """Scénarios de nettoyage disponibles."""

    AUTO_REPAIR = "auto_repair"  # Détecte et répare automatiquement
    RESET_DEFAULT = "reset_default"  # Reset complet aux valeurs par défaut
    CLEAN_CORRUPTED = "clean_corrupted"  # Supprime uniquement les widgets corrompus
    VALIDATE_ONLY = "validate_only"  # Vérifie sans modifier


@dataclass
class CleanupResult:
    """Résultat d'une opération de nettoyage."""

    scenario: CleanupScenario
    success: bool
    widgets_checked: int
    widgets_fixed: int
    widgets_removed: int
    errors: List[str]
    message: str


class DashboardCleanupManager:
    """
    Gestionnaire de nettoyage du dashboard.
    Peut fonctionner en mode automatique ou manuel.
    """

    # Layout par défaut (simplifié pour fallback)
    DEFAULT_LAYOUT_JSON = [
        {
            "id": "kpi_1",
            "type": "kpi_depenses",
            "title": "💸 Dépenses",
            "position": 1,
            "size": "small",
            "visible": True,
            "config": {},
        },
        {
            "id": "kpi_2",
            "type": "kpi_revenus",
            "title": "💰 Revenus",
            "position": 2,
            "size": "small",
            "visible": True,
            "config": {},
        },
        {
            "id": "kpi_3",
            "type": "kpi_solde",
            "title": "📊 Solde",
            "position": 3,
            "size": "small",
            "visible": True,
            "config": {},
        },
        {
            "id": "kpi_4",
            "type": "kpi_epargne",
            "title": "🎯 Taux d'épargne",
            "position": 4,
            "size": "small",
            "visible": True,
            "config": {},
        },
        {
            "id": "evol_1",
            "type": "evolution_chart",
            "title": "📈 Évolution",
            "position": 5,
            "size": "large",
            "visible": True,
            "config": {},
        },
        {
            "id": "sav_1",
            "type": "savings_trend",
            "title": "💹 Tendance épargne",
            "position": 6,
            "size": "medium",
            "visible": True,
            "config": {},
        },
        {
            "id": "cat_1",
            "type": "categories_chart",
            "title": "📊 Répartition",
            "position": 7,
            "size": "medium",
            "visible": True,
            "config": {},
        },
        {
            "id": "top_1",
            "type": "top_expenses",
            "title": "🔥 Top dépenses",
            "position": 8,
            "size": "medium",
            "visible": True,
            "config": {},
        },
    ]

    # Types de widgets valides
    VALID_WIDGET_TYPES = {
        "kpi_depenses",
        "kpi_revenus",
        "kpi_solde",
        "kpi_epargne",
        "evolution_chart",
        "savings_trend",
        "categories_chart",
        "top_expenses",
        "budget_tracker",
        "budget_alerts",
        "smart_recommendations",
        "monthly_stacked",
        "members_analysis",
        "tiers_analysis",
        "tags_analysis",
        "ai_insights",
    }

    def __init__(self):
        self.errors = []

    def run_cleanup(self, scenario: CleanupScenario = CleanupScenario.AUTO_REPAIR) -> CleanupResult:
        """
        Lance un scénario de nettoyage.

        Args:
            scenario: Scénario à exécuter

        Returns:
            CleanupResult avec les détails de l'opération
        """
        logger.info(f"Starting dashboard cleanup with scenario: {scenario.value}")

        if scenario == CleanupScenario.VALIDATE_ONLY:
            return self._validate_only()
        elif scenario == CleanupScenario.RESET_DEFAULT:
            return self._reset_to_default()
        elif scenario == CleanupScenario.CLEAN_CORRUPTED:
            return self._clean_corrupted()
        else:  # AUTO_REPAIR
            return self._auto_repair()

    def _validate_only(self) -> CleanupResult:
        """Valide les layouts sans modifier."""
        layouts = self._get_all_layouts()
        errors = []
        total_widgets = 0

        for layout in layouts:
            layout_id = layout.get("id", "unknown")
            widgets = self._parse_widgets(layout.get("layout_data", "[]"))
            total_widgets += len(widgets)

            for i, widget in enumerate(widgets):
                widget_errors = self._validate_widget(widget, f"layout {layout_id}, widget {i}")
                errors.extend(widget_errors)

        return CleanupResult(
            scenario=CleanupScenario.VALIDATE_ONLY,
            success=len(errors) == 0,
            widgets_checked=total_widgets,
            widgets_fixed=0,
            widgets_removed=0,
            errors=errors,
            message=f"Validation terminée: {len(errors)} erreur(s) trouvée(s) sur {total_widgets} widget(s)",
        )

    def _auto_repair(self) -> CleanupResult:
        """Répare automatiquement les problèmes détectés."""
        layouts = self._get_all_layouts()
        total_fixed = 0
        total_removed = 0
        total_checked = 0
        errors = []

        for layout in layouts:
            layout_id = layout.get("id")
            widgets = self._parse_widgets(layout.get("layout_data", "[]"))
            total_checked += len(widgets)

            repaired_widgets = []
            for widget in widgets:
                is_valid, repaired, was_fixed = self._repair_widget(widget)
                if is_valid:
                    repaired_widgets.append(repaired)
                    if was_fixed:
                        total_fixed += 1
                else:
                    total_removed += 1
                    errors.append(f"Widget supprimé (layout {layout_id}): {repaired}")

            # Sauvegarder si modifié
            if total_fixed > 0 or total_removed > 0:
                self._save_layout(layout_id, repaired_widgets)

        # Si aucun layout valide, créer le défaut
        if not layouts:
            self._create_default_layout()
            return CleanupResult(
                scenario=CleanupScenario.AUTO_REPAIR,
                success=True,
                widgets_checked=0,
                widgets_fixed=0,
                widgets_removed=0,
                errors=[],
                message="Aucun layout trouvé, layout par défaut créé",
            )

        return CleanupResult(
            scenario=CleanupScenario.AUTO_REPAIR,
            success=True,
            widgets_checked=total_checked,
            widgets_fixed=total_fixed,
            widgets_removed=total_removed,
            errors=errors,
            message=f"Réparation terminée: {total_fixed} widget(s) corrigé(s), {total_removed} supprimé(s)",
        )

    def _reset_to_default(self) -> CleanupResult:
        """Reset complet aux valeurs par défaut."""
        try:
            # Supprimer tous les layouts existants
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM dashboard_layouts")
                conn.commit()

            # Créer le layout par défaut
            self._create_default_layout()

            return CleanupResult(
                scenario=CleanupScenario.RESET_DEFAULT,
                success=True,
                widgets_checked=0,
                widgets_fixed=0,
                widgets_removed=0,
                errors=[],
                message="Reset complet effectué, layout par défaut restauré",
            )

        except Exception as e:
            logger.error(f"Error resetting dashboard: {e}")
            return CleanupResult(
                scenario=CleanupScenario.RESET_DEFAULT,
                success=False,
                widgets_checked=0,
                widgets_fixed=0,
                widgets_removed=0,
                errors=[str(e)],
                message=f"Erreur lors du reset: {e}",
            )

    def _clean_corrupted(self) -> CleanupResult:
        """Supprime uniquement les widgets corrompus."""
        return self._auto_repair()  # Même logique

    def _validate_widget(self, widget: Dict, context: str) -> List[str]:
        """Valide un widget et retourne les erreurs."""
        errors = []

        # Vérifier le type
        widget_type = widget.get("type")
        if not widget_type:
            errors.append(f"{context}: type manquant")
        elif isinstance(widget_type, str):
            if widget_type.lower() not in self.VALID_WIDGET_TYPES:
                errors.append(f"{context}: type inconnu '{widget_type}'")
        elif hasattr(widget_type, "value"):
            # C'est un Enum, vérifier la valeur
            if widget_type.value not in self.VALID_WIDGET_TYPES:
                errors.append(f"{context}: type Enum invalide '{widget_type.value}'")
        else:
            errors.append(f"{context}: type invalide '{type(widget_type)}'")

        # Vérifier les champs requis
        if not widget.get("id"):
            errors.append(f"{context}: id manquant")

        return errors

    def _repair_widget(self, widget: Dict) -> Tuple[bool, Dict, bool]:
        """
        Tente de réparer un widget corrompu.

        Returns:
            (is_valid, repaired_widget, was_fixed)
        """
        was_fixed = False
        repaired = dict(widget)  # Copie

        # Problème: type est un Enum WidgetType au lieu d'une string
        widget_type = widget.get("type")
        if hasattr(widget_type, "value"):
            # Convertir Enum en string
            repaired["type"] = widget_type.value
            was_fixed = True

        # Problème: type inconnu
        if isinstance(repaired.get("type"), str):
            type_str = repaired["type"].lower()
            if type_str not in self.VALID_WIDGET_TYPES:
                # Essayer de mapper vers un type valide
                if "kpi" in type_str or "depense" in type_str:
                    repaired["type"] = "kpi_depenses"
                    was_fixed = True
                elif "revenu" in type_str:
                    repaired["type"] = "kpi_revenus"
                    was_fixed = True
                else:
                    # Type vraiment inconnu, on ne peut pas réparer
                    return False, repaired, False

        # Problème: id manquant
        if not repaired.get("id"):
            import uuid

            repaired["id"] = f"auto_{uuid.uuid4().hex[:8]}"
            was_fixed = True

        # Problème: champs manquants avec valeurs par défaut
        if "visible" not in repaired:
            repaired["visible"] = True
            was_fixed = True
        if "config" not in repaired:
            repaired["config"] = {}
            was_fixed = True
        if "position" not in repaired:
            repaired["position"] = 99
            was_fixed = True
        if "size" not in repaired:
            repaired["size"] = "small"
            was_fixed = True
        if "title" not in repaired:
            repaired["title"] = "Widget"
            was_fixed = True

        return True, repaired, was_fixed

    def _get_all_layouts(self) -> List[Dict]:
        """Récupère tous les layouts de la base."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, name, layout_data, is_active 
                    FROM dashboard_layouts
                """
                )
                rows = cursor.fetchall()

                return [
                    {"id": row[0], "name": row[1], "layout_data": row[2], "is_active": row[3]}
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error fetching layouts: {e}")
            return []

    def _parse_widgets(self, layout_data: str) -> List[Dict]:
        """Parse les widgets depuis le JSON."""
        try:
            if isinstance(layout_data, str):
                return json.loads(layout_data)
            elif isinstance(layout_data, list):
                return layout_data
            else:
                return []
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in layout_data: {layout_data[:100]}...")
            return []

    def _save_layout(self, layout_id: int, widgets: List[Dict]):
        """Sauvegarde un layout modifié."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE dashboard_layouts SET layout_data = ? WHERE id = ?",
                    (json.dumps(widgets), layout_id),
                )
                conn.commit()
                logger.info(f"Layout {layout_id} updated with {len(widgets)} widgets")
        except Exception as e:
            logger.error(f"Error saving layout {layout_id}: {e}")

    def _create_default_layout(self):
        """Crée le layout par défaut."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO dashboard_layouts (name, layout_data, is_active, created_at)
                    VALUES (?, ?, ?, datetime('now'))
                    """,
                    ("Default", json.dumps(self.DEFAULT_LAYOUT_JSON), 1),
                )
                conn.commit()
                logger.info("Default layout created")
        except Exception as e:
            logger.error(f"Error creating default layout: {e}")


def run_startup_cleanup() -> CleanupResult:
    """
    Lance le nettoyage au démarrage de l'application.
    Mode AUTO_REPAIR silencieux.
    """
    manager = DashboardCleanupManager()
    result = manager.run_cleanup(CleanupScenario.AUTO_REPAIR)

    if result.widgets_fixed > 0 or result.widgets_removed > 0:
        logger.info(f"Dashboard cleanup: {result.message}")

    return result


def reset_dashboard() -> CleanupResult:
    """
    Reset complet du dashboard (pour usage manuel).
    """
    manager = DashboardCleanupManager()
    return manager.run_cleanup(CleanupScenario.RESET_DEFAULT)


# Pour usage en ligne de commande
if __name__ == "__main__":
    import sys

    # Setup logging for CLI usage
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cli_logger = logging.getLogger(__name__)

    scenario_map = {
        "repair": CleanupScenario.AUTO_REPAIR,
        "reset": CleanupScenario.RESET_DEFAULT,
        "clean": CleanupScenario.CLEAN_CORRUPTED,
        "validate": CleanupScenario.VALIDATE_ONLY,
    }

    scenario_name = sys.argv[1] if len(sys.argv) > 1 else "repair"
    scenario = scenario_map.get(scenario_name, CleanupScenario.AUTO_REPAIR)

    cli_logger.info(f"Running dashboard cleanup: {scenario.value}")
    cli_logger.info("=" * 60)

    manager = DashboardCleanupManager()
    result = manager.run_cleanup(scenario)

    cli_logger.info(f"Success: {result.success}")
    cli_logger.info(f"Widgets checked: {result.widgets_checked}")
    cli_logger.info(f"Widgets fixed: {result.widgets_fixed}")
    cli_logger.info(f"Widgets removed: {result.widgets_removed}")
    cli_logger.info(f"Message: {result.message}")

    if result.errors:
        cli_logger.info("\nErrors:")
        for error in result.errors:
            cli_logger.info(f"  - {error}")
