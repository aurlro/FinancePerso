#!/usr/bin/env python3
"""
Script de lancement de l'API avec PYTHONPATH configuré.
Usage: python start_api.py
"""

import sys
from pathlib import Path

# Ajouter le root du projet au PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Maintenant on peut importer
from web.api.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,  # Disable reload for now
    )
