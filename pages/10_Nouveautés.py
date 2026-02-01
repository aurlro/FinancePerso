import streamlit as st
import os
import re
from datetime import datetime
from modules.ui import load_css
from modules.ui.layout import render_app_info
from modules.ui.feedback import render_scroll_to_top
from modules.ui.changelog_parser import parse_changelog
from modules.update_manager import get_update_manager, VersionEntry

st.set_page_config(page_title="Nouveautés", page_icon="🎁", layout="wide")
load_css()

st.title("🎁 Nouveautés & Mises à jour")

# --- UPDATE SECTION (Admin) ---
with st.expander("🔧 Mettre à jour la documentation (Admin)", expanded=False):
    st.markdown("""
    Cette section permet de créer une nouvelle version et de mettre à jour :
    - **CHANGELOG.md** - Historique des versions
    - **AGENTS.md** - Guide pour les assistants IA
    - **modules/constants.py** - Numéro de version
    """)
    
    manager = get_update_manager()
    current_version = manager.get_current_version()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"Version actuelle : **v{current_version}**")
    
    with col2:
        bump_type = st.selectbox(
            "Type de mise à jour",
            options=[("patch", "🔧 Correction (patch)"), ("minor", "✨ Fonctionnalité (minor)"), ("major", "🚀 Majeure (major)")],
            format_func=lambda x: x[1]
        )[0]
        
        new_version = manager.bump_version(current_version, bump_type)
        st.success(f"Nouvelle version : **v{new_version}**")
    
    # Update form
    with st.form("update_form"):
        update_title = st.text_input(
            "Titre de la mise à jour",
            placeholder="Ex: Nouvelle fonctionnalité X - Refonte complète",
            help="Décrivez brièvement le thème principal de cette mise à jour"
        )
        
        st.subheader("📝 Changements")
        
        col_added, col_fixed, col_perf = st.columns(3)
        
        with col_added:
            st.markdown("**✨ Nouveautés**")
            added = st.text_area(
                "Liste (une par ligne)",
                placeholder="- Nouvelle fonction X\n- Amélioration Y",
                key="added_changes",
                height=150
            )
        
        with col_fixed:
            st.markdown("**🐛 Corrections**")
            fixed = st.text_area(
                "Liste (une par ligne)",
                placeholder="- Bug Z corrigé\n- Problème W résolu",
                key="fixed_changes",
                height=150
            )
        
        with col_perf:
            st.markdown("**⚡ Performance**")
            perf = st.text_area(
                "Liste (une par ligne)",
                placeholder="- Optimisation A\n- Cache B amélioré",
                key="perf_changes",
                height=150
            )
        
        st.subheader("📁 Fichiers modifiés")
        files_modified = st.text_area(
            "Liste des fichiers (un par ligne)",
            placeholder="modules/nouveau.py\npages/1_Import.py",
            help="Liste des fichiers principaux modifiés dans cette version"
        )
        
        breaking = st.checkbox("⚠️ Contient des breaking changes", key='checkbox_88')
        breaking_changes = None
        if breaking:
            breaking_changes = st.text_area(
                "Breaking changes (une par ligne)",
                placeholder="- API X modifiée\n- Dépréciation de Y"
            )
        
        submitted = st.form_submit_button("🚀 Créer la mise à jour", type="primary", use_container_width=True)
        
        if submitted:
            if not update_title:
                st.error("❌ Veuillez entrer un titre pour la mise à jour")
            elif not added and not fixed and not perf:
                st.error("❌ Veuillez entrer au moins un changement")
            else:
                # Build changes dict
                changes = {}
                if added.strip():
                    changes["added"] = [line.strip() for line in added.split('\n') if line.strip()]
                if fixed.strip():
                    changes["fixed"] = [line.strip() for line in fixed.split('\n') if line.strip()]
                if perf.strip():
                    changes["performance"] = [line.strip() for line in perf.split('\n') if line.strip()]
                
                files_list = [f.strip() for f in files_modified.split('\n') if f.strip()] if files_modified else []
                breaking_list = [b.strip() for b in breaking_changes.split('\n') if b.strip()] if breaking_changes else None
                
                # Create update
                with st.spinner("Mise à jour en cours..."):
                    success, version = manager.create_update(
                        title=update_title,
                        changes=changes,
                        bump_type=bump_type,
                        files_modified=files_list,
                        breaking_changes=breaking_list
                    )
                
                if success:
                    st.success(f"✅ Mise à jour v{version} créée avec succès !")
                    st.balloons()
                    
                    # Show what was updated
                    st.markdown("### 📄 Fichiers mis à jour :")
                    st.markdown(f"- **CHANGELOG.md** - Nouvelle entrée v{version}")
                    st.markdown(f"- **AGENTS.md** - Version et date mises à jour")
                    st.markdown(f"- **modules/constants.py** - APP_VERSION = \"{version}\"")
                    
                    st.info("📝 N'oubliez pas de commit et push ces changements !")
                    
                    # Refresh the page to show new changelog
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de la création de la mise à jour. Vérifiez les logs.")

# Path to changelog
CHANGELOG_PATH = os.path.join(os.getcwd(), "CHANGELOG.md")

# Parse changelog
versions = parse_changelog(CHANGELOG_PATH)

st.markdown("### 📜 Historique des versions")

if not versions:
    st.info("Aucun historique disponible dans CHANGELOG.md")
else:
    for v in versions:
        with st.container(border=True):
            col_ver, col_content = st.columns([1, 4])
            with col_ver:
                st.markdown(f"### `v{v['version']}`")
                if v['date']:
                    # Try to format date nicely if possible
                    try:
                        date_obj = datetime.strptime(v['date'], "%Y-%m-%d")
                        formatted_date = date_obj.strftime("%d %B %Y")
                        st.caption(formatted_date)
                    except (ValueError, TypeError) as e:
                        # Fallback to raw date string if parsing fails
                        st.caption(v['date'])
                
                # Extract main category or subtitle if possible from content
                # (Look for first ### header)
                first_header = re.search(r'### (.*)', v['content'])
                if first_header:
                    st.caption(f"✨ {first_header.group(1)}")
                    
            with col_content:
                st.markdown(v['content'])
        
        st.markdown(" ") # Spacer

st.divider()

render_scroll_to_top()
render_app_info()
