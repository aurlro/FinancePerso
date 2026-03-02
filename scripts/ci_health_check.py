#!/usr/bin/env python3
"""
CI Health Check - Vérifie la santé du projet avant commit/push
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔍 {description}...")
    # Force python3 explicitly
    cmd = cmd.replace("python ", "python3 ")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✅ {description} - OK")
        return True
    else:
        print(f"  ❌ {description} - FAILED")
        if result.stdout:
            print(result.stdout[:500])
        if result.stderr:
            print(result.stderr[:500])
        return False


def main():
    """Run all health checks."""
    print("=" * 60)
    print("🔬 CI HEALTH CHECK")
    print("=" * 60)
    
    checks = [
        ("python3 -m py_compile app.py", "Syntax Check (app.py)"),
        ("python3 .agents/doc_agent.py --check", "Documentation Check"),
        ("python3 -m pytest tests/test_essential.py -q", "Essential Tests"),
    ]
    
    # Optional checks (don't fail if tools not installed)
    optional_checks = [
        ("python3 -m ruff check modules/ pages/ tests/ --quiet 2>/dev/null || true", "Ruff Linting"),
        ("python3 -m black --check modules/ pages/ tests/ --quiet 2>/dev/null || true", "Black Formatting"),
    ]
    
    results = []
    
    # Run required checks
    for cmd, desc in checks:
        results.append(run_command(cmd, desc))
    
    # Run optional checks
    for cmd, desc in optional_checks:
        result = subprocess.run(cmd, shell=True, capture_output=True)
        if result.returncode == 0:
            print(f"  ✅ {desc} - OK")
        elif result.returncode == 1:
            print(f"  ⚠️  {desc} - Issues found (run 'make format' to fix)")
        else:
            print(f"  ⏭️  {desc} - Skipped (tool not installed)")
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL CHECKS PASSED")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
