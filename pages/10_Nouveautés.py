import streamlit as st
import os
import re
from datetime import datetime
from modules.ui import load_css
from modules.ui.layout import render_app_info
from modules.ui.changelog_parser import parse_changelog

st.set_page_config(page_title="Nouveautés", page_icon="🎁", layout="wide")
load_css()

st.title("🎁 Nouveautés & Mises à jour")

# Path to changelog
CHANGELOG_PATH = os.path.join(os.getcwd(), "CHANGELOG.md")

# Parse changelog
versions = parse_changelog(CHANGELOG_PATH)

st.markdown("### Historique des versions")

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
                    except:
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

render_app_info()
