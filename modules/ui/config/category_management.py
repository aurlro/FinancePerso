import streamlit as st
from modules.data_manager import (
    get_categories_df, add_category, delete_category,
    update_category_emoji, update_category_fixed,
    update_category_suggested_tags
)

def render_category_management():
    """
    Render the Catégories tab content.
    Manage spending categories with emojis, fixed flags, and suggested tags.
    """
    st.header("Gestion des Catégories")
    st.markdown("Personnalisez les catégories de dépenses pour votre budget.")
    
    # List categories
    cats_df = get_categories_df()
    
    col_list_cat, col_add_cat = st.columns([1, 1])
    
    with col_list_cat:
        st.subheader("Catégories existantes")
        if cats_df.empty:
            st.info("Aucune catégorie configurée.")
        else:
            for index, row in cats_df.iterrows():
                with st.expander(f"{row['emoji']} {row['name']} {' (Fixe)' if row['is_fixed'] else ''}", expanded=False):
                    c1, c2 = st.columns([3, 1])
                    new_emoji = c1.text_input("Emoji", value=row['emoji'], key=f"emoji_val_{row['id']}")
                    is_fixed = c1.checkbox("Dépense Fixe (ex: Loyer, Abonnement)", value=bool(row['is_fixed']), key=f"fixed_val_{row['id']}")
                    
                    suggested_tags_val = row.get('suggested_tags', '') if row.get('suggested_tags') else ''
                    new_suggested_tags = c1.text_input("Tags suggérés (séparés par des virgules)", value=suggested_tags_val, key=f"tags_val_{row['id']}")
                    
                    if c1.button("Mettre à jour", key=f"upd_cat_{row['id']}"):
                        update_category_emoji(row['id'], new_emoji)
                        update_category_fixed(row['id'], int(is_fixed))
                        update_category_suggested_tags(row['id'], new_suggested_tags)
                        st.rerun()
                    
                    if c2.button("🗑️ Supprimer", key=f"del_cat_{row['id']}"):
                        delete_category(row['id'])
                        st.rerun()

    with col_add_cat:
        st.subheader("Ajouter une catégorie")
        with st.form("add_cat_form"):
            col_a1, col_a2, col_a3 = st.columns([3, 1, 1])
            new_cat_name = col_a1.text_input("Nom de la catégorie", placeholder="Ex: Enfants...")
            new_cat_emoji = col_a2.text_input("Emoji", value="🏷️")
            new_is_fixed = col_a3.checkbox("Fixe", value=False)
            
            if st.form_submit_button("Ajouter"):
                if new_cat_name:
                    if add_category(new_cat_name, new_cat_emoji, int(new_is_fixed)):
                        st.success(f"Catégorie '{new_cat_name}' ajoutée !")
                        st.rerun()
                    else:
                        st.error("Cette catégorie existe déjà.")
                else:
                    st.warning("Veuillez entrer un nom.")
