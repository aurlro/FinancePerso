"""Script de migration vers Dashboard V5.5.

Ce script prépare la migration du dashboard legacy (02_Dashboard.py)
vers la nouvelle version V5.5 (Dashboard_Beta.py).

Usage:
    python scripts/migrate_to_v5_5.py [--check|--apply]

Options:
    --check    Vérifie l'état de la migration (défaut)
    --apply    Applique la migration (remplace 02_Dashboard.py)
"""

import argparse
import os
import shutil
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
PAGES_DIR = PROJECT_ROOT / "pages"


def get_dashboard_files():
    """Retourne les fichiers dashboard concernés."""
    return {
        "legacy": PAGES_DIR / "02_Dashboard.py",
        "beta": PAGES_DIR / "Dashboard_Beta.py",
        "test": PAGES_DIR / "99_Test_Dashboard.py",
        "backup": PAGES_DIR / "02_Dashboard_backup.py",
    }


def check_migration_status():
    """Vérifie l'état de la migration."""
    files = get_dashboard_files()

    print("=" * 60)
    print("ÉTAT DE LA MIGRATION V5.5")
    print("=" * 60)
    print()

    # Vérifier les fichiers
    for name, path in files.items():
        exists = "✅" if path.exists() else "❌"
        size = f"({path.stat().st_size:,} octets)" if path.exists() else ""
        print(f"{exists} {name:15} : {path.name} {size}")

    print()

    # Vérifier le feature flag
    constants_file = PROJECT_ROOT / "modules" / "constants.py"
    with open(constants_file, "r") as f:
        content = f.read()
        if "TEST_DASHBOARD_ENABLED = True" in content:
            print("✅ Feature flag TEST_DASHBOARD_ENABLED = True")
        elif "TEST_DASHBOARD_ENABLED = False" in content:
            print("⚠️  Feature flag TEST_DASHBOARD_ENABLED = False")
        else:
            print("❌ Feature flag non trouvé")

    print()

    # Recommandations
    if files["beta"].exists() and files["legacy"].exists():
        print("📋 Recommandation:")
        print("   Le Dashboard Beta est prêt à remplacer le legacy.")
        print("   Exécutez avec --apply pour effectuer la migration.")

    print()
    print("=" * 60)


def apply_migration():
    """Applique la migration."""
    files = get_dashboard_files()

    print("=" * 60)
    print("MIGRATION VERS V5.5")
    print("=" * 60)
    print()

    # Vérifications préalables
    if not files["beta"].exists():
        print("❌ Erreur: Dashboard_Beta.py n'existe pas!")
        return False

    if not files["legacy"].exists():
        print("⚠️  Le fichier 02_Dashboard.py n'existe pas.")
        print("   La migration a peut-être déjà été effectuée.")
        return False

    # Créer une sauvegarde
    if files["legacy"].exists():
        backup_path = files["backup"]
        counter = 1
        while backup_path.exists():
            backup_path = PAGES_DIR / f"02_Dashboard_backup_{counter}.py"
            counter += 1

        shutil.copy2(files["legacy"], backup_path)
        print(f"✅ Sauvegarde créée: {backup_path.name}")

    # Remplacer le fichier
    try:
        # Lire le contenu de Dashboard_Beta
        with open(files["beta"], "r") as f:
            beta_content = f.read()

        # Modifier le contenu pour remplacer 02_Dashboard
        new_content = (
            beta_content.replace('page_title="Dashboard Beta V5.5"', 'page_title="Synthèse"')
            .replace('page_icon="✨"', 'page_icon="📊"')
            .replace(
                'st.sidebar.title("💰 Dashboard Beta V5.5")', 'st.sidebar.title("💰 Synthèse")'
            )
        )

        # Écrire dans 02_Dashboard.py
        with open(files["legacy"], "w") as f:
            f.write(new_content)

        print("✅ 02_Dashboard.py mis à jour avec la version V5.5")

        # Renommer Dashboard_Beta en .deprecated
        deprecated_path = files["beta"].with_suffix(".deprecated")
        shutil.move(files["beta"], deprecated_path)
        print(f"✅ Dashboard_Beta.py renommé en {deprecated_path.name}")

        # Supprimer le test dashboard legacy
        if files["test"].exists():
            files["test"].unlink()
            print("✅ 99_Test_Dashboard.py supprimé")

        print()
        print("🎉 Migration terminée avec succès!")
        print()
        print("Prochaines étapes:")
        print("  1. Testez l'application: streamlit run app.py")
        print("  2. Vérifiez que le dashboard fonctionne correctement")
        print("  3. Supprimez les fichiers .backup et .deprecated si tout est OK")

    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

    print()
    print("=" * 60)
    return True


def rollback_migration():
    """Annule la migration."""
    files = get_dashboard_files()

    print("=" * 60)
    print("ROLLBACK MIGRATION V5.5")
    print("=" * 60)
    print()

    # Chercher les backups
    backups = list(PAGES_DIR.glob("02_Dashboard_backup*.py"))

    if not backups:
        print("❌ Aucune sauvegarde trouvée.")
        return False

    # Prendre le backup le plus récent
    latest_backup = max(backups, key=lambda p: p.stat().st_mtime)

    # Restaurer
    shutil.copy2(latest_backup, files["legacy"])
    print(f"✅ Restauré depuis: {latest_backup.name}")

    # Restaurer Dashboard_Beta si deprecated existe
    deprecated = files["beta"].with_suffix(".deprecated")
    if deprecated.exists():
        shutil.move(deprecated, files["beta"])
        print("✅ Dashboard_Beta.py restauré")

    print()
    print("🎉 Rollback terminé!")
    print()
    print("=" * 60)
    return True


def main():
    parser = argparse.ArgumentParser(description="Migration vers Dashboard V5.5")
    parser.add_argument(
        "--check", action="store_true", help="Vérifie l'état de la migration (défaut)"
    )
    parser.add_argument("--apply", action="store_true", help="Applique la migration")
    parser.add_argument("--rollback", action="store_true", help="Annule la migration")

    args = parser.parse_args()

    if args.apply:
        apply_migration()
    elif args.rollback:
        rollback_migration()
    else:
        check_migration_status()


if __name__ == "__main__":
    main()
