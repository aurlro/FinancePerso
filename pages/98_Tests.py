"""
Page Tests - Interface pour lancer les tests unitaires et d'intégration
"""
import streamlit as st
import subprocess
import sys
import os
from pathlib import Path
import json
import time

# Configuration de la page
st.set_page_config(
    page_title="Tests - FinancePerso",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Tests & Quality")

# Tabs pour organiser l'interface
tab1, tab2, tab3 = st.tabs(["🚀 Lancer Tests", "📊 Résultats", "📚 Documentation"])

with tab1:
    st.header("Lancer les Tests")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Catégorie de Tests")
        
        test_category = st.radio(
            "Sélectionnez les tests à lancer :",
            [
                "🌟 Tous les tests (293 tests)",
                "💾 Tests DB (79 tests)",
                "🧠 Tests AI (8 tests)",
                "🎨 Tests UI Components (67 tests)",
                "🔄 Tests Integration (25 tests)",
                "⚙️ Tests Logic & Others (114 tests)"
            ],
            help="Choisissez quelle catégorie de tests vous souhaitez exécuter"
        )
        
        # Options avancées
        with st.expander("⚙️ Options Avancées"):
            verbose = st.checkbox("Mode verbose (-vv)", value=False)
            stop_on_first = st.checkbox("Arrêter au premier échec (-x)", value=False)
            show_output = st.checkbox("Afficher les print() (-s)", value=False)
            coverage = st.checkbox("Calculer la coverage (--cov)", value=False)
            
            keyword_filter = st.text_input(
                "Filtrer par mot-clé",
                placeholder="Ex: 'budget', 'transaction', 'duplicate'...",
                help="Lancer uniquement les tests contenant ce mot-clé"
            )
    
    with col2:
        st.subheader("Actions")
        
        if st.button("▶️ Lancer les Tests", type="primary", use_container_width=True, key="btn_lancer_tests"):
            # Construction de la commande
            cmd = ["python3", "-m", "pytest"]
            
            # Ajouter la catégorie
            if "Tous" in test_category:
                pass  # Pas de filtre
            elif "DB" in test_category:
                cmd.append("db/")
            elif "UI" in test_category:
                cmd.append("ui/")
            elif "Integration" in test_category:
                cmd.append("test_integration.py")
            elif "AI" in test_category:
                cmd.append("ai/")
            elif "Logic" in test_category:
                cmd.extend(["test_utils.py", "test_analytics.py"])
            
            # Options
            if verbose:
                cmd.append("-vv")
            else:
                cmd.append("-v")
            
            if stop_on_first:
                cmd.append("-x")
            
            if show_output:
                cmd.append("-s")
            
            if coverage:
                cmd.extend(["--cov=modules", "--cov-report=term-missing"])
            
            if keyword_filter:
                cmd.extend(["-k", keyword_filter])
            
            # Ignorer .DS_Store
            cmd.extend(["--ignore=../.DS_Store", "--ignore=.DS_Store"])
            
            # Lancer les tests
            with st.spinner("🔄 Exécution des tests en cours..."):
                start_time = time.time()
                
                try:
                    # Changer vers le dossier tests
                    result = subprocess.run(
                        cmd,
                        cwd=os.path.join(os.getcwd(), "tests"),
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    execution_time = time.time() - start_time
                    
                    # Stocker les résultats en session state
                    st.session_state['last_test_result'] = {
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'returncode': result.returncode,
                        'execution_time': execution_time,
                        'command': ' '.join(cmd)
                    }
                    
                    # Afficher résumé
                    if result.returncode == 0:
                        st.success(f"✅ Tests réussis en {execution_time:.2f}s !")
                    else:
                        st.error(f"❌ Certains tests ont échoué (code: {result.returncode})")
                    
                    # Switch vers l'onglet résultats
                    st.info("👉 Consultez l'onglet 'Résultats' pour voir les détails")
                    
                except subprocess.TimeoutExpired:
                    st.error("⏱️ Timeout: Les tests ont pris plus de 2 minutes")
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'exécution: {e}")
        
        if st.button("🗑️ Nettoyer les caches", use_container_width=True):
            # Nettoyer les caches pytest
            cache_dirs = [
                os.path.join("tests", ".pytest_cache"),
                os.path.join("tests", "__pycache__"),
            ]
            
            cleaned = 0
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    import shutil
                    shutil.rmtree(cache_dir)
                    cleaned += 1
            
            st.success(f"✅ {cleaned} cache(s) nettoyé(s)")

with tab2:
    st.header("📊 Résultats des Tests")
    
    if 'last_test_result' in st.session_state:
        result = st.session_state['last_test_result']
        
        # Métriques
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_icon = "✅" if result['returncode'] == 0 else "❌"
            st.metric("Status", f"{status_icon} {'Success' if result['returncode'] == 0 else 'Failed'}")
        
        with col2:
            st.metric("Temps d'exécution", f"{result['execution_time']:.2f}s")
        
        with col3:
            st.metric("Code de sortie", result['returncode'])
        
        st.divider()
        
        # Commande exécutée
        st.subheader("Commande Exécutée")
        st.code(result['command'], language="bash")
        
        # Output
        st.subheader("Sortie des Tests")
        
        output = result['stdout'] + result['stderr']
        
        # Parser pour extraire des infos
        if "passed" in output:
            # Extraire le résumé
            lines = output.split('\n')
            for line in lines:
                if 'passed' in line or 'failed' in line or 'error' in line:
                    if '=====' in line:
                        st.info(line.strip('=').strip())
        
        # Output complet
        with st.expander("📝 Output Complet", expanded=True):
            st.text_area(
                "Sortie complète",
                value=output,
                height=400,
                label_visibility="collapsed"
            )
        
        # Bouton de téléchargement
        st.download_button(
            label="💾 Télécharger les résultats",
            data=output,
            file_name=f"test_results_{int(time.time())}.txt",
            mime="text/plain"
        )
        
    else:
        st.info("👆 Lancez d'abord des tests dans l'onglet '🚀 Lancer Tests'")
        
        # Afficher les stats du projet
        st.subheader("📈 Statistiques du Projet")
        
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        
        with stats_col1:
            st.metric("Tests Disponibles", "293")
            st.caption("108 DB + 8 AI + 54 UI + 18 Logic + 9 Integration")
        
        with stats_col2:
            st.metric("Coverage Estimée", "~75%")
            st.caption("Couverture globale du code")
        
        with stats_col3:
            st.metric("Modules Testés", "19")
            st.caption("Fichiers de test")

with tab3:
    st.header("📚 Documentation des Tests")
    
    st.markdown("""
    ## 🎯 Organisation des Tests
    
    Les tests sont organisés en **3 catégories principales** :
    
    ### 💾 Tests DB (108 tests)
    - **Transactions** (19) : CRUD, filtering, duplicates
    - **Catégories** (19) : CRUD, emojis, merging, ghosts
    - **Membres** (16) : CRUD, renaming, card mappings
    - **Tags** (13) : Normalisation, global delete
    - **Rules** (11) : Pattern matching, auto-categorization
    - **Budgets** (11) : CRUD, validation
    - **Audit** (8) : Orphans, transfers
    - **Stats** (8) : Analytics
    - **Migrations** (6) : Schema versioning
    
    ### 🎨 Tests UI Components (54 tests)
    - **KPI Cards** (7) : Trends calculation
    - **Category Charts** (6) : Data aggregation
    - **Progress Tracker** (8) : Progress logic
    - **Tag Manager** (11) : Tag validation
    - **Member Selector** (10) : Filtering
    - **Filters** (12) : Date/category filtering
    
    ### 🔄 Tests Integration (9 tests)
    - Import → Categorization workflow
    - Validation → Learning rules
    - Budget tracking
    - Audit workflows
    - End-to-end scenarios
    
    ---
    
    ## 🚀 Commandes CLI
    
    Si vous préférez lancer les tests en ligne de commande :
    
    ```bash
    # Tous les tests
    cd tests && ./run_tests.sh
    
    # Tests DB uniquement
    cd tests && ./run_tests.sh db/
    
    # Tests UI uniquement
    cd tests && ./run_tests.sh ui/
    
    # Tests d'intégration
    cd tests && ./run_tests.sh test_integration.py
    
    # Avec coverage
    cd tests && ./run_tests.sh --cov=modules --cov-report=html
    ```
    
    ---
    
    ## ⚠️ Note macOS
    
    À cause du problème `.DS_Store` (SIP protection), utilisez :
    - Le script `run_tests.sh` fourni
    - Ou supprimez les `.DS_Store` : `find . -name ".DS_Store" -delete`
    
    ---
    
    ## 📖 Plus d'infos
    
    Consultez `tests/README.md` pour la documentation complète.
    """)
    
    # Lien vers README
    readme_path = os.path.join("tests", "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            readme_content = f.read()
        
        with st.expander("📄 Voir tests/README.md"):
            st.markdown(readme_content)

# Footer
st.divider()

from modules.ui import render_scroll_to_top
render_scroll_to_top()

st.caption("🧪 Test Suite - 293 tests | ~82% coverage | Production Ready")
