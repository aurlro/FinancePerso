import streamlit as st
from modules.db.categories import (
    get_categories_df, add_category, delete_category,
    update_category_emoji, update_category_fixed,
    update_category_suggested_tags, merge_categories, get_categories
)
from modules.impact_analyzer import analyze_category_merge_impact, render_impact_preview
from modules.ui.feedback import (
    toast_success, toast_error, save_feedback, delete_feedback,
    show_success, show_warning
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
                        try:
                            update_category_emoji(row['id'], new_emoji)
                            update_category_fixed(row['id'], int(is_fixed))
                            update_category_suggested_tags(row['id'], new_suggested_tags)
                            save_feedback(f"Catégorie '{row['name']}'", created=False)
                            st.rerun()
                        except Exception as e:
                            toast_error(f"Erreur mise à jour : {e}", icon="❌")
                    
                    if c2.button("🗑️ Supprimer", key=f"del_cat_{row['id']}"):
                        try:
                            delete_category(row['id'])
                            delete_feedback(f"Catégorie '{row['name']}'")
                            st.rerun()
                        except Exception as e:
                            toast_error(f"Impossible de supprimer : {e}", icon="❌")

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
                        type_label = "fixe" if new_is_fixed else "variable"
                        save_feedback(f"Catégorie '{new_cat_name}' ({type_label})", created=True)
                        st.rerun()
                    else:
                        show_warning(f"La catégorie '{new_cat_name}' existe déjà", icon="⚠️")
                        toast_error("Cette catégorie existe déjà", icon="❌")
                else:
                    toast_warning("Veuillez entrer un nom", icon="⚠️")
    
    # --- CATEGORY MERGE SECTION ---
    st.divider()
    st.subheader("🔀 Fusionner des catégories")
    st.info("Transférez toutes les transactions d'une catégorie vers une autre.")
    
    all_cats = get_categories()
    if len(all_cats) >= 2:
        col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
        
        with col_m1:
            source_cat = st.selectbox(
                "Catégorie à absorber",
                all_cats,
                key="merge_source",
                help="Cette catégorie sera supprimée après la fusion"
            )
        
        with col_m2:
            target_options = [c for c in all_cats if c != source_cat]
            target_cat = st.selectbox(
                "Catégorie cible",
                target_options,
                key="merge_target",
                help="Cette catégorie recevra toutes les transactions"
            )
        
        # Preview impact
        if source_cat and target_cat:
            impact = analyze_category_merge_impact(source_cat, target_cat)
            render_impact_preview('category_merge', impact)
        
        with col_m3:
            st.markdown("<div style='height: 0.1rem;'></div>", unsafe_allow_html=True)
            if st.button("Fusionner", type="primary", use_container_width=True):
                if source_cat and target_cat and source_cat != target_cat:
                    try:
                        result = merge_categories(source_cat, target_cat)
                        count = result.get('transactions', 0)
                        toast_success(f"✅ {count} transactions transférées !", icon="🔀")
                        show_success(f"Catégorie '{source_cat}' fusionnée avec '{target_cat}' ({count} transactions)")
                        st.rerun()
                    except Exception as e:
                        toast_error(f"Erreur de fusion : {e}", icon="❌")
                else:
                    show_warning("Veuillez sélectionner deux catégories différentes", icon="⚠️")
                    toast_warning("Sélection invalide", icon="⚠️")
