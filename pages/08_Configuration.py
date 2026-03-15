# -*- coding: utf-8 -*-
"""
Page Configuration avec Design System V5.5.

Nouvelle version utilisant les composants modernes.
"""

import streamlit as st

from modules.db.migrations import init_db
from modules.ui import load_css
from modules.ui.pages.settings import render_settings_page

# Page Setup
st.set_page_config(page_title="⚙️ Paramètres", page_icon="⚙️", layout="wide")
load_css()
init_db()  # Ensure tables exist

# Render the new unified settings page with Design System V5.5
render_settings_page()
