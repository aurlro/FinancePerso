"""Member management UI component - Simplified."""

import streamlit as st

from modules.db.members import add_member, get_all_member_names


def render_member_management() -> None:
    """Render member management section."""
    st.subheader("👥 Gestion des membres")

    members = get_all_member_names()

    st.write("Membres actuels:")
    for member in members:
        st.write(f"- {member}")

    st.divider()
    st.write("Ajouter un membre:")

    new_member = st.text_input("Nom du membre", key="new_member_name")
    if st.button("Ajouter", key="add_member_btn"):
        if new_member:
            try:
                add_member(new_member)
                st.success(f"Membre '{new_member}' ajouté!")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur: {e}")
