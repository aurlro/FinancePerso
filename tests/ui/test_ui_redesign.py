
import streamlit as st
import pandas as pd
from modules.ui import load_css
from modules.ui.validation.row_view import render_validation_row
from modules.ui.components.avatar_selector import render_avatar_selector
from modules.utils import clean_label

# Mock Data
all_members = ["Aurélien", "Élise", "Maison"]
all_categories = ["Alimentation", "Loisirs", "Transport", "Inconnu"]
cat_emoji_map = {"Alimentation": "🛒", "Loisirs": "🎉", "Transport": "🚗", "Inconnu": "❓"}

st.set_page_config(layout="wide")
load_css()

st.title("Test Validation Row UI")

row_data = {
    'id': 123,
    'label': "CARREFOUR HYPERMARCHE",
    'date': "04/02/2026",
    'total_amount': -154.30,
    'count': 1,
    'category': "Inconnu",
    'member': "Aurélien"
}

def on_validate(row_id, cat, mem):
    st.toast(f"Validated {row_id}: {cat} by {mem}")
    st.balloons()

st.subheader("Single Row Render")
render_validation_row(
    row_data=row_data,
    all_members=all_members,
    all_categories=all_categories,
    cat_emoji_map=cat_emoji_map,
    on_validate=on_validate,
    key_prefix="test_row"
)

st.subheader("Avatar Selector Test")
sel = render_avatar_selector("Test Avatar", all_members, "Aurélien", "test_av")
st.write(f"Selected: {sel}")
