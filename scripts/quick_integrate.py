#!/usr/bin/env python3
"""
Script d'intégration rapide - Quick Win
========================================

Intègre immédiatement les nouvelles vues Phases 4-5-6 dans app.py

Usage:
    python scripts/quick_integrate.py

⚠️  Fait une sauvegarde de app.py avant!
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path


def backup_app_py():
    """Crée une sauvegarde de app.py"""
    app_path = Path("app.py")
    if not app_path.exists():
        print("❌ app.py non trouvé!")
        return False
    
    backup_path = Path(f"app.py.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy(app_path, backup_path)
    print(f"✅ Sauvegarde créée: {backup_path}")
    return True


def integrate_views():
    """Ajoute les imports et la navigation pour les nouvelles vues"""
    
    integration_code = '''
# ============================================================
# INTEGRATION PHASES 4-5-6 - Auto-generated
# ============================================================

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

# Imports des nouvelles vues
try:
    from views.subscriptions import render_subscriptions_page
    from views.projections import render_projections_page
    from views.wealth_view import render_wealth_dashboard
    NEW_VIEWS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Certaines vues ne sont pas disponibles: {e}")
    NEW_VIEWS_AVAILABLE = False

# Imports Design System
try:
    from modules.ui import apply_vibe_theme
    DESIGN_SYSTEM_AVAILABLE = True
except ImportError:
    DESIGN_SYSTEM_AVAILABLE = False

'''

    navigation_code = '''
# ============================================================
# NAVIGATION NOUVELLES FONCTIONNALITÉS
# ============================================================

if NEW_VIEWS_AVAILABLE:
    st.sidebar.markdown("---")
    st.sidebar.header("🆕 Nouveautés v5.4")
    
    new_features = {
        "📊 Patrimoine 360°": render_wealth_dashboard if 'render_wealth_dashboard' in locals() else None,
        "📈 Projections": render_projections_page if 'render_projections_page' in locals() else None,
        "🔄 Abonnements": render_subscriptions_page if 'render_subscriptions_page' in locals() else None,
    }
    
    # Filtrer les fonctionnalités non disponibles
    new_features = {k: v for k, v in new_features.items() if v is not None}
    
    if new_features:
        selected_feature = st.sidebar.radio(
            "Explorer",
            ["🏠 Dashboard"] + list(new_features.keys()),
            key="new_features_nav"
        )
        
        if selected_feature != "🏠 Dashboard":
            st.sidebar.markdown("---")
            # Afficher la vue sélectionnée
            if selected_feature == "📊 Patrimoine 360°":
                render_wealth_dashboard()
                st.stop()
            elif selected_feature == "📈 Projections":
                render_projections_page()
                st.stop()
            elif selected_feature == "🔄 Abonnements":
                render_subscriptions_page()
                st.stop()

'''

    return integration_code, navigation_code


def patch_app_py():
    """Modifie app.py pour intégrer les nouvelles vues"""
    
    app_path = Path("app.py")
    if not app_path.exists():
        print("❌ app.py non trouvé!")
        return False
    
    # Lire le contenu actuel
    content = app_path.read_text(encoding='utf-8')
    
    # Vérifier si déjà patché
    if "INTEGRATION PHASES 4-5-6" in content:
        print("⚠️  app.py semble déjà patché!")
        return False
    
    integration_code, navigation_code = integrate_views()
    
    # Trouver la position d'insertion (après les imports)
    lines = content.split('\n')
    import_end = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            import_end = i + 1
    
    # Insérer le code d'intégration après les imports
    lines.insert(import_end, integration_code)
    
    # Trouver la position pour la navigation (après la sidebar principale)
    # On cherche un bon endroit pour insérer
    for i, line in enumerate(lines):
        if 'st.sidebar' in line and 'radio' in line:
            # Insérer après la dernière sidebar
            insert_pos = i + 2
            lines.insert(insert_pos, navigation_code)
            break
    else:
        # Si pas trouvé, ajouter à la fin
        lines.append(navigation_code)
    
    # Écrire le nouveau contenu
    new_content = '\n'.join(lines)
    app_path.write_text(new_content, encoding='utf-8')
    
    print("✅ app.py patché avec succès!")
    print("\n📝 Changements effectués:")
    print("   1. Ajout des imports des vues (subscriptions, projections, wealth)")
    print("   2. Ajout du menu 'Nouveautés v5.4' dans la sidebar")
    print("   3. Navigation vers les nouvelles fonctionnalités")
    
    return True


def main():
    """Fonction principale"""
    print("=" * 60)
    print("INTEGRATION RAPIDE - Phases 4-5-6")
    print("=" * 60)
    print()
    
    # Vérifier que les fichiers existent
    required_files = [
        "views/subscriptions.py",
        "views/projections.py",
        "views/wealth_view.py",
    ]
    
    missing = []
    for f in required_files:
        if not Path(f).exists():
            missing.append(f)
    
    if missing:
        print("❌ Fichiers manquants:")
        for f in missing:
            print(f"   - {f}")
        print("\n💡 Vérifiez que les phases 4-5-6 sont bien créées.")
        return 1
    
    print("✅ Tous les fichiers de vues sont présents")
    print()
    
    # Backup
    if not backup_app_py():
        return 1
    
    print()
    
    # Patch
    if not patch_app_py():
        return 1
    
    print()
    print("=" * 60)
    print("✅ INTEGRATION TERMINÉE!")
    print("=" * 60)
    print()
    print("🚀 Prochaines étapes:")
    print("   1. Lancer: streamlit run app.py")
    print("   2. Vérifier le menu '🆕 Nouveautés v5.4' dans la sidebar")
    print("   3. Tester les nouvelles fonctionnalités")
    print()
    print("⚠️  En cas de problème:")
    print("   - Restaurer: cp app.py.backup.XXX app.py")
    print("   - Vérifier les logs d'erreur")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
