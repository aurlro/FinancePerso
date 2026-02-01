import streamlit as st
from modules.db.categories import (
    get_categories_df, add_category, delete_category,
    update_category_emoji, update_category_fixed,
    update_category_suggested_tags, merge_categories, get_categories
)
from modules.impact_analyzer import analyze_category_merge_impact, render_impact_preview
from modules.ui.feedback import (
    toast_success, toast_error, toast_warning, toast_info,
    save_feedback, delete_feedback,
    show_success, show_warning, show_error
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
            st.info("📭 Aucune catégorie configurée. Créez votre première catégorie à droite.")
        else:
            for index, row in cats_df.iterrows():
                with st.expander(f"{row['emoji']} {row['name']} {' (Fixe)' if row['is_fixed'] else ''}", expanded=False):
                    c1, c2 = st.columns([3, 1])
                    new_emoji = c1.text_input("Emoji", value=row['emoji'], key=f"emoji_val_{row['id']}")
                    is_fixed = c1.checkbox(
                        "Dépense Fixe (ex: Loyer, Abonnement)", 
                        value=bool(row['is_fixed']), 
                        key=f"fixed_val_{row['id']}"
                    )
                    
                    suggested_tags_val = row.get('suggested_tags', '') if row.get('suggested_tags') else ''
                    new_suggested_tags = c1.text_input(
                        "Tags suggérés (séparés par des virgules)", 
                        value=suggested_tags_val, 
                        key=f"tags_val_{row['id']}"
                    )
                    
                    if c1.button("💾 Mettre à jour", key=f"upd_cat_{row['id']}"):
                        try:
                            # Track changes for detailed feedback
                            changes = []
                            if new_emoji != row['emoji']:
                                changes.append(f"emoji {row['emoji']} → {new_emoji}")
                            if is_fixed != bool(row['is_fixed']):
                                changes.append("type 'fixe'" if is_fixed else "type 'variable'")
                            if new_suggested_tags != suggested_tags_val:
                                changes.append("tags suggérés")
                            
                            update_category_emoji(row['id'], new_emoji)
                            update_category_fixed(row['id'], int(is_fixed))
                            update_category_suggested_tags(row['id'], new_suggested_tags)
                            
                            if changes:
                                change_str = ", ".join(changes)
                                toast_success(f"✅ '{row['name']}' mis à jour : {change_str}", icon="💾")
                            else:
                                toast_info(f"ℹ️ Aucun changement pour '{row['name']}'", icon="ℹ️")
                            
                            save_feedback(f"Catégorie '{row['name']}'", created=False)
                            st.rerun()
                        except Exception as e:
                            error_msg = str(e)
                            if "UNIQUE constraint" in error_msg:
                                toast_error(f"❌ Impossible de modifier '{row['name']}' : conflit de données", icon="⚠️")
                            elif "FOREIGN KEY" in error_msg:
                                toast_error(f"❌ Modification impossible : catégorie utilisée ailleurs", icon="🔗")
                            else:
                                toast_error(f"❌ Erreur mise à jour de '{row['name']}' : {error_msg[:50]}", icon="❌")
                    
                    # Delete button with confirmation
                    if c2.button("🗑️ Supprimer", key=f"del_cat_{row['id']}"):
                        try:
                            delete_category(row['id'])
                            delete_feedback(f"Catégorie '{row['name']}'")
                            toast_success(f"🗑️ Catégorie '{row['name']}' supprimée avec succès", icon="🗑️")
                            st.rerun()
                        except Exception as e:
                            error_msg = str(e)
                            if "FOREIGN KEY" in error_msg:
                                show_error(
                                    f"Impossible de supprimer '{row['name']}'",
                                    icon="🔗"
                                )
                                toast_error(
                                    f"❌ '{row['name']}' est utilisée par des transactions ou des règles. "
                                    "Utilisez la fusion pour réattribuer ses transactions.", 
                                    icon="🔗"
                                )
                            elif "not found" in error_msg.lower() or "n'existe pas" in error_msg.lower():
                                toast_warning(f"⚠️ La catégorie '{row['name']}' n'existe plus", icon="⚠️")
                                st.rerun()
                            else:
                                toast_error(f"❌ Erreur suppression '{row['name']}' : {error_msg[:50]}", icon="❌")

    with col_add_cat:
        st.subheader("➕ Ajouter une catégorie")
        with st.form("add_cat_form"):
            col_a1, col_a2, col_a3 = st.columns([3, 1, 1])
            new_cat_name = col_a1.text_input(
                "Nom de la catégorie", 
                placeholder="Ex: Enfants, Sport...",
                help="Nom unique de la catégorie"
            )
            new_cat_emoji = col_a2.text_input("Emoji", value="🏷️", help="Emoji représentatif")
            new_is_fixed = col_a3.checkbox("Fixe", value=False, help="Dépense régulière ?")
            
            submitted = st.form_submit_button("➕ Ajouter", use_container_width=True)
            if submitted:
                if not new_cat_name or not new_cat_name.strip():
                    toast_warning("⚠️ Veuillez entrer un nom de catégorie", icon="✏️")
                elif len(new_cat_name.strip()) < 2:
                    toast_warning("⚠️ Le nom doit contenir au moins 2 caractères", icon="📏")
                else:
                    cat_name = new_cat_name.strip()
                    try:
                        if add_category(cat_name, new_cat_emoji, int(new_is_fixed)):
                            type_label = "dépense fixe" if new_is_fixed else "dépense variable"
                            toast_success(
                                f"✅ Catégorie créée : {new_cat_emoji} '{cat_name}' ({type_label})", 
                                icon="🎉"
                            )
                            save_feedback(f"Catégorie '{cat_name}'", created=True)
                            st.rerun()
                        else:
                            show_warning(
                                f"La catégorie '{cat_name}' existe déjà",
                                icon="⚠️"
                            )
                            toast_error(
                                f"❌ '{cat_name}' existe déjà. Choisissez un autre nom ou fusionnez les catégories.", 
                                icon="🚫"
                            )
                    except Exception as e:
                        error_msg = str(e)
                        if "UNIQUE constraint" in error_msg:
                            toast_error(f"❌ La catégorie '{cat_name}' existe déjà", icon="🚫")
                        else:
                            toast_error(f"❌ Erreur création : {error_msg[:50]}", icon="❌")
    
    # --- CATEGORY MERGE SECTION ---
    st.divider()
    st.subheader("🔀 Fusionner des catégories")
    st.info("Transférez toutes les transactions d'une catégorie vers une autre. La catégorie source sera supprimée.")
    
    all_cats = get_categories()
    if len(all_cats) < 2:
        st.warning("⚠️ Il faut au moins 2 catégories pour effectuer une fusion.", icon="⚠️")
    else:
        col_m1, col_m2, col_m3 = st.columns([2, 2, 1])
        
        with col_m1:
            source_cat = st.selectbox(
                "Catégorie source (sera supprimée)",
                all_cats,
                key="merge_source",
                help="Toutes ses transactions seront transférées, puis elle sera supprimée"
            )
        
        with col_m2:
            target_options = [c for c in all_cats if c != source_cat]
            target_cat = st.selectbox(
                "Catégorie cible (reçoit les transactions)",
                target_options,
                key="merge_target",
                help="Cette catégorie recevra toutes les transactions"
            )
        
        # Preview impact
        if source_cat and target_cat:
            impact = analyze_category_merge_impact(source_cat, target_cat)
            render_impact_preview('category_merge', impact)
        
        with col_m3:
            st.markdown("<div style='height: 1.6rem;'></div>", unsafe_allow_html=True)
            if st.button("🔀 Fusionner", type="primary", use_container_width=True, key='button_187'):
                if not source_cat or not target_cat:
                    toast_warning("⚠️ Veuillez sélectionner les deux catégories", icon="⚠️")
                elif source_cat == target_cat:
                    show_warning(
                        "Veuillez sélectionner deux catégories différentes",
                        icon="⚠️"
                    )
                    toast_error("❌ La source et la cible doivent être différentes", icon="🚫")
                else:
                    try:
                        with st.spinner(f"🔄 Fusion en cours : '{source_cat}' → '{target_cat}'..."):
                            result = merge_categories(source_cat, target_cat)
                        
                        tx_count = result.get('transactions', 0)
                        rules_count = result.get('rules', 0)
                        budget_transferred = result.get('budgets_transferred', False)
                        category_deleted = result.get('category_deleted', False)
                        
                        # Build detailed success message
                        messages = []
                        if tx_count > 0:
                            messages.append(f"• {tx_count} transaction(s) transférée(s)")
                        elif tx_count == 0:
                            messages.append(f"• Aucune transaction à transférer")
                        
                        if rules_count > 0:
                            messages.append(f"• {rules_count} règle(s) de catégorisation mise(s) à jour")
                        
                        if budget_transferred:
                            messages.append(f"• 💰 Budget transféré")
                        
                        if category_deleted:
                            messages.append(f"• 🗑️ Catégorie '{source_cat}' supprimée")
                        
                        success_msg = "\n".join(messages) if messages else "Fusion terminée"
                        
                        # Toast with summary
                        toast_success(
                            f"✅ '{source_cat}' fusionnée avec '{target_cat}'\n{success_msg}", 
                            icon="🔀"
                        )
                        
                        # Detailed success banner
                        with st.container(border=True):
                            st.markdown(f"**🔀 Fusion réussie**")
                            st.markdown(f"**'{source_cat}'** → **'{target_cat}'**")
                            if tx_count > 0:
                                st.markdown(f"✅ {tx_count} transaction(s) réattribuée(s)")
                            if rules_count > 0:
                                st.markdown(f"📋 {rules_count} règle(s) mise(s) à jour")
                            if budget_transferred:
                                st.markdown(f"💰 Budget ajouté à '{target_cat}'")
                            if category_deleted:
                                st.caption(f"🗑️ La catégorie '{source_cat}' n'existe plus")
                        
                        st.rerun()
                        
                    except ValueError as e:
                        error_msg = str(e)
                        show_error(f"Fusion impossible : {error_msg}", icon="🚫")
                        toast_error(f"❌ {error_msg}", icon="🚫")
                    except Exception as e:
                        error_msg = str(e)
                        if "not found" in error_msg.lower() or "n'existe pas" in error_msg.lower():
                            toast_error(f"❌ Une des catégories n'existe plus : {error_msg}", icon="⚠️")
                        elif "database" in error_msg.lower():
                            show_error(
                                "Erreur base de données lors de la fusion",
                                icon="💾"
                            )
                            toast_error(f"❌ Problème de base de données. Réessayez.", icon="💾")
                        else:
                            show_error(f"Impossible de fusionner : {error_msg}", icon="❌")
                            toast_error(f"❌ Échec de la fusion : {error_msg[:80]}", icon="❌")
