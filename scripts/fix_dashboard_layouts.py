#!/usr/bin/env python3
"""
Script de nettoyage des layouts de dashboard.
Usage: python scripts/fix_dashboard_layouts.py [scenario]

Scénarios:
  repair    - Répare automatiquement les problèmes (défaut)
  reset     - Reset complet aux valeurs par défaut
  clean     - Supprime uniquement les widgets corrompus
  validate  - Vérifie sans modifier
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db.dashboard_cleanup import (
    DashboardCleanupManager, 
    CleanupScenario,
    run_startup_cleanup,
    reset_dashboard
)


def main():
    scenario_map = {
        'repair': CleanupScenario.AUTO_REPAIR,
        'reset': CleanupScenario.RESET_DEFAULT,
        'clean': CleanupScenario.CLEAN_CORRUPTED,
        'validate': CleanupScenario.VALIDATE_ONLY,
    }
    
    scenario_name = sys.argv[1] if len(sys.argv) > 1 else 'repair'
    scenario = scenario_map.get(scenario_name, CleanupScenario.AUTO_REPAIR)
    
    print("=" * 60)
    print("🔧 Dashboard Cleanup Tool")
    print("=" * 60)
    print(f"Scenario: {scenario.value}")
    print()
    
    manager = DashboardCleanupManager()
    result = manager.run_cleanup(scenario)
    
    # Affichage des résultats
    status = "✅" if result.success else "❌"
    print(f"{status} Success: {result.success}")
    print(f"📊 Widgets checked: {result.widgets_checked}")
    print(f"🔧 Widgets fixed: {result.widgets_fixed}")
    print(f"🗑️  Widgets removed: {result.widgets_removed}")
    print()
    print(f"📝 Message: {result.message}")
    
    if result.errors:
        print()
        print("⚠️  Errors:")
        for error in result.errors[:10]:  # Limiter l'affichage
            print(f"   - {error}")
        if len(result.errors) > 10:
            print(f"   ... and {len(result.errors) - 10} more")
    
    print()
    print("=" * 60)
    
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
