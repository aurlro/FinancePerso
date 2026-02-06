"""
Quick test script for new UI components.
Run with: streamlit run test_components.py
"""
import streamlit as st
from modules.ui.components.tag_manager import render_smart_tag_selector
from modules.ui.components.member_selector import render_member_selector

st.set_page_config(page_title="Component Test", page_icon="🧪")

st.title("🧪 UI Component Tests")

st.header("1. Tag Manager Test")
st.markdown("Testing tag selection with creation and suggestions")

selected_tags = render_smart_tag_selector(
    transaction_id=999,
    current_tags=["Courses", "Bio"],
    category="Alimentation",
    key_suffix="_test"
)

st.write("**Selected tags:**", selected_tags)

st.divider()

st.header("2. Member Selector Test")
st.markdown("Testing member selection with type icons")

members = ["Aurélien", "Élise", "CPAM"]
member_types = {
    "Aurélien": "HOUSEHOLD",
    "Élise": "HOUSEHOLD",
    "CPAM": "EXTERNAL"
}

selected_member = render_member_selector(
    label="👤 Payeur",
    current_value="Aurélien",
    all_members=members,
    member_type_map=member_types,
    key="test_member"
)

st.write("**Selected member:**", selected_member)

st.divider()
st.success("✅ Component tests running successfully!")
