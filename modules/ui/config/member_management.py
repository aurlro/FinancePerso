import streamlit as st
import pandas as pd
from modules.db.members import (
    get_members, add_member, delete_member, rename_member,
    update_member_type, get_member_mappings_df,
    add_member_mapping, delete_member_mapping
)
from modules.impact_analyzer import analyze_member_rename_impact, render_impact_preview
from modules.ui.feedback import (
    toast_success, toast_error, toast_warning, toast_info,
    save_feedback, delete_feedback,
    show_success, show_warning, show_error
)
# Initialisation des variables de session
if 'pending_rename' not in st.session_state:
    st.session_state['pending_rename'] = None
if 'editing_member_id' not in st.session_state:
    st.session_state['editing_member_id'] = None


def render_member_management():
    """
    Render the Foyer & Membres tab content.
    Manage household members, external entities, and card-to-member mappings.
    """
    st.header("👥 Membres du Foyer")
    st.markdown("Définissez les personnes associées à ce compte pour l'attribution des dépenses.")
    
    # Handle pending rename with impact preview
    pending = st.session_state.get('pending_rename')
    if pending is not None:
        with st.container(border=True):
            st.warning("⚠️ Confirmer le renommage ?")
            render_impact_preview('member_rename', pending['impact'])
            
            col_confirm, col_cancel = st.columns([1, 1])
            with col_confirm:
                if st.button("✅ Confirmer le renommage", type="primary", use_container_width=True, key='button_38'):
                    try:
                        rename_member(pending['old_name'], pending['new_name'])
                        del st.session_state['pending_rename']
                        st.session_state['editing_member_id'] = None
                        
                        affected = pending['impact'].get('total_affected', 0)
                        if affected > 0:
                            toast_success(
                                f"✅ '{pending['old_name']}' renommé en '{pending['new_name']}' ({affected} transaction(s) mise(s) à jour)",
                                icon="👤"
                            )
                        else:
                            toast_success(
                                f"✅ '{pending['old_name']}' renommé en '{pending['new_name']}'",
                                icon="👤"
                            )
                        save_feedback(f"Membre '{pending['old_name']}' → '{pending['new_name']}'", created=False)
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if "existe déjà" in error_msg.lower() or "already" in error_msg.lower():
                            toast_error(f"❌ Le nom '{pending['new_name']}' est déjà utilisé", icon="🚫")
                        elif "not found" in error_msg.lower():
                            toast_error(f"❌ Le membre '{pending['old_name']}' n'existe plus", icon="⚠️")
                        else:
                            toast_error(f"❌ Erreur lors du renommage : {error_msg[:50]}", icon="❌")
            with col_cancel:
                if st.button("❌ Annuler", use_container_width=True, key='button_66'):
                    del st.session_state['pending_rename']
                    toast_info("Renommage annulé", icon="🚫")
                    st.rerun()
        st.divider()
    
    members_df = get_members()
    
    col_list, col_add = st.columns([1, 1])
    
    with col_list:
        if members_df.empty:
            st.info("📭 Aucun membre configuré. Ajoutez votre premier membre à droite.")
        else:
            if 'editing_member_id' not in st.session_state:
                st.session_state['editing_member_id'] = None
                
            # --- HOUSEHOLD GROUP ---
            foyer_df = members_df[members_df['member_type'] == 'HOUSEHOLD']
            st.subheader("🏘️ Membres du Foyer")
            if foyer_df.empty:
                st.caption("Aucun membre du foyer.")
            else:
                for index, row in foyer_df.iterrows():
                    member_id, member_name = row['id'], row['name']
                    if st.session_state['editing_member_id'] == member_id:
                        c1, c2, c3 = st.columns([3, 0.5, 0.5])
                        with c1: 
                            new_name = st.text_input(
                                "Nom", 
                                value=member_name, 
                                key=f"edit_in_{member_id}", 
                                label_visibility="collapsed"
                            )
                        with c2: 
                            if st.button("✅", key=f"sv_{member_id}", help="Sauvegarder"):
                                if new_name and new_name.strip():
                                    cleaned_name = new_name.strip()
                                    if cleaned_name != member_name:
                                        # Analyze impact first
                                        impact = analyze_member_rename_impact(member_name, cleaned_name)
                                        if impact['total_affected'] > 0:
                                            st.session_state['pending_rename'] = {
                                                'old_name': member_name,
                                                'new_name': cleaned_name,
                                                'impact': impact
                                            }
                                            st.rerun()
                                        else:
                                            # No impact, proceed directly
                                            try:
                                                rename_member(member_name, cleaned_name)
                                                st.session_state['editing_member_id'] = None
                                                toast_success(f"✅ Membre renommé : '{member_name}' → '{cleaned_name}'", icon="👤")
                                                st.rerun()
                                            except Exception as e:
                                                toast_error(f"❌ Erreur : {str(e)[:50]}", icon="❌")
                                    else:
                                        toast_info("ℹ️ Aucun changement", icon="ℹ️")
                                else:
                                    toast_warning("⚠️ Le nom ne peut pas être vide", icon="⚠️")
                        with c3:
                            if st.button("❌", key=f"cl_{member_id}", help="Annuler"):
                                st.session_state['editing_member_id'] = None
                                st.rerun()
                    else:
                        c1, c2, c3, c4 = st.columns([3, 1, 0.5, 0.5])
                        c1.write(f"👤 **{member_name}**")
                        if c2.button("➡️ Tiers", key=f"to_ext_{member_id}", help="Déplacer vers Tiers"):
                            try:
                                update_member_type(member_id, 'EXTERNAL')
                                toast_success(f"✅ '{member_name}' déplacé vers Tiers", icon="💼")
                                st.rerun()
                            except Exception as e:
                                toast_error(f"❌ Impossible de déplacer '{member_name}' : {str(e)[:50]}", icon="❌")
                        if c3.button("✏️", key=f"ed_{member_id}", help="Renommer"):
                            st.session_state['editing_member_id'] = member_id
                            st.rerun()
                        if c4.button("🗑️", key=f"del_{member_id}", help="Supprimer"):
                            try:
                                delete_member(member_id)
                                delete_feedback(f"Membre '{member_name}'")
                                toast_success(f"🗑️ Membre '{member_name}' supprimé", icon="🗑️")
                                st.rerun()
                            except Exception as e:
                                error_msg = str(e)
                                if "FOREIGN KEY" in error_msg or "utilisé" in error_msg.lower():
                                    show_error(
                                        f"Impossible de supprimer '{member_name}'",
                                        icon="🔗"
                                    )
                                    toast_error(
                                        f"❌ '{member_name}' est utilisé dans des transactions ou des cartes. "
                                        "Supprimez d'abord ces associations.",
                                        icon="🔗"
                                    )
                                else:
                                    toast_error(f"❌ Erreur suppression : {error_msg[:50]}", icon="❌")
            
            # --- EXTERNAL GROUP ---
            ext_df = members_df[members_df['member_type'] == 'EXTERNAL']
            st.subheader("💼 Tiers (Externe)")
            if ext_df.empty:
                st.caption("Aucun tiers externe.")
            else:
                for index, row in ext_df.iterrows():
                    member_id, member_name = row['id'], row['name']
                    if st.session_state['editing_member_id'] == member_id:
                        c1, c2, c3 = st.columns([3, 0.5, 0.5])
                        with c1: 
                            edit_name = st.text_input(
                                "Nom", 
                                value=member_name, 
                                key=f"edit_in_{member_id}", 
                                label_visibility="collapsed"
                            )
                        with c2: 
                            if st.button("✅", key=f"sv_{member_id}", help="Sauvegarder"):
                                if edit_name and edit_name.strip():
                                    cleaned_name = edit_name.strip()
                                    if cleaned_name != member_name:
                                        try:
                                            rename_member(member_name, cleaned_name)
                                            st.session_state['editing_member_id'] = None
                                            toast_success(f"✅ Membre renommé : '{member_name}' → '{cleaned_name}'", icon="👤")
                                            st.rerun()
                                        except Exception as e:
                                            toast_error(f"❌ Erreur : {str(e)[:50]}", icon="❌")
                                    else:
                                        toast_info("ℹ️ Aucun changement", icon="ℹ️")
                                else:
                                    toast_warning("⚠️ Le nom ne peut pas être vide", icon="⚠️")
                        with c3:
                            if st.button("❌", key=f"cl_{member_id}", help="Annuler"):
                                st.session_state['editing_member_id'] = None
                                st.rerun()
                    else:
                        c1, c2, c3, c4 = st.columns([3, 1, 0.5, 0.5])
                        c1.write(f"💼 **{member_name}**")
                        if c2.button("⬅️ Foyer", key=f"to_hh_{member_id}", help="Déplacer vers Foyer"):
                            try:
                                update_member_type(member_id, 'HOUSEHOLD')
                                toast_success(f"✅ '{member_name}' déplacé vers Foyer", icon="🏘️")
                                st.rerun()
                            except Exception as e:
                                toast_error(f"❌ Impossible de déplacer '{member_name}' : {str(e)[:50]}", icon="❌")
                        if c3.button("✏️", key=f"ed_{member_id}", help="Renommer"):
                            st.session_state['editing_member_id'] = member_id
                            st.rerun()
                        if c4.button("🗑️", key=f"del_{member_id}", help="Supprimer"):
                            try:
                                delete_member(member_id)
                                toast_success(f"🗑️ Membre '{member_name}' supprimé", icon="🗑️")
                                st.rerun()
                            except Exception as e:
                                error_msg = str(e)
                                if "FOREIGN KEY" in error_msg or "utilisé" in error_msg.lower():
                                    show_error(
                                        f"Impossible de supprimer '{member_name}'",
                                        icon="🔗"
                                    )
                                    toast_error(
                                        f"❌ '{member_name}' est utilisé dans des transactions ou des cartes",
                                        icon="🔗"
                                    )
                                else:
                                    toast_error(f"❌ Erreur suppression : {error_msg[:50]}", icon="❌")
    
    with col_add:
        st.subheader("➕ Ajouter un membre")
        with st.form("add_member_form"):
            new_name = st.text_input(
                "Nom", 
                placeholder="Ex: Jean, Marie...",
                help="Nom unique du membre"
            )
            new_type = st.radio(
                "Type", 
                ["HOUSEHOLD", "EXTERNAL"], 
                format_func=lambda x: "🏘️ Foyer" if x == "HOUSEHOLD" else "💼 Tiers",
                help="Foyer = membre du budget, Tiers = externe (ex: crèche, impôts)"
            )
            
            submitted = st.form_submit_button("➕ Ajouter", use_container_width=True)
            if submitted:
                if not new_name or not new_name.strip():
                    toast_warning("⚠️ Veuillez entrer un nom", icon="✏️")
                elif len(new_name.strip()) < 2:
                    toast_warning("⚠️ Le nom doit contenir au moins 2 caractères", icon="📏")
                else:
                    cleaned_name = new_name.strip()
                    try:
                        if add_member(cleaned_name, new_type):
                            member_type_label = "Foyer" if new_type == "HOUSEHOLD" else "Tiers"
                            toast_success(
                                f"✅ Membre créé : '{cleaned_name}' ({member_type_label})",
                                icon="🎉"
                            )
                            save_feedback(f"Membre '{cleaned_name}' ({member_type_label})", created=True)
                            st.rerun()
                        else:
                            show_warning(
                                f"Le membre '{cleaned_name}' existe déjà",
                                icon="⚠️"
                            )
                            toast_error(
                                f"❌ '{cleaned_name}' existe déjà. Choisissez un nom différent.",
                                icon="🚫"
                            )
                    except Exception as e:
                        error_msg = str(e)
                        if "existe déjà" in error_msg.lower() or "already" in error_msg.lower():
                            toast_error(f"❌ Le membre '{cleaned_name}' existe déjà", icon="🚫")
                        else:
                            toast_error(f"❌ Erreur création : {error_msg[:50]}", icon="❌")
    
    # --- CARD MAPPINGS ---
    st.divider()
    st.subheader("💳 Correspondances Cartes → Membres")
    st.markdown("Associez automatiquement une carte bancaire (4 derniers chiffres) à un membre.")
    
    if members_df.empty:
        st.warning("⚠️ Ajoutez d'abord des membres pour configurer les correspondances.", icon="⚠️")
        return
    
    mapping_df = get_member_mappings_df()
    
    col_m1, col_m2 = st.columns([1, 1])
    with col_m1:
        if mapping_df.empty:
            st.info("📭 Aucune correspondance configurée.")
        else:
            st.caption(f"{len(mapping_df)} carte(s) configurée(s)")
            for index, row in mapping_df.iterrows():
                cm1, cm2 = st.columns([3, 1])
                cm1.write(f"💳 **...{row['card_suffix']}** ➔ 👤 {row['member_name']}")
                if cm2.button("🗑️", key=f"del_map_{row['id']}", help="Supprimer la correspondance"):
                    try:
                        delete_member_mapping(row['id'])
                        toast_success(f"🗑️ Carte ...{row['card_suffix']} dissociée de {row['member_name']}", icon="🗑️")
                        st.rerun()
                    except Exception as e:
                        toast_error(f"❌ Erreur : {str(e)[:50]}", icon="❌")
    
    with col_m2:
        with st.form("add_mapping_form"):
            suffix = st.text_input(
                "4 derniers chiffres", 
                placeholder="Ex: 6759",
                help="Les 4 derniers chiffres de la carte bancaire"
            )
            m_name = st.selectbox(
                "Membre", 
                members_df['name'].tolist() if not members_df.empty else ["Anonyme"],
                help="Membre associé à cette carte"
            )
            
            submitted = st.form_submit_button("➕ Ajouter la carte", use_container_width=True)
            if submitted:
                if not suffix or not suffix.strip():
                    toast_warning("⚠️ Veuillez entrer les 4 derniers chiffres", icon="💳")
                elif not m_name:
                    toast_warning("⚠️ Veuillez sélectionner un membre", icon="👤")
                elif len(suffix.strip()) != 4 or not suffix.strip().isdigit():
                    toast_warning("⚠️ Le suffixe doit être exactement 4 chiffres", icon="📏")
                else:
                    clean_suffix = suffix.strip()
                    try:
                        add_member_mapping(clean_suffix, m_name)
                        toast_success(
                            f"✅ Carte ...{clean_suffix} associée à {m_name}",
                            icon="💳"
                        )
                        save_feedback(f"Carte '...{clean_suffix}' associée à {m_name}", created=True)
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        if "existe déjà" in error_msg.lower() or "already" in error_msg.lower():
                            toast_error(f"❌ La carte ...{clean_suffix} est déjà associée", icon="🚫")
                        else:
                            toast_error(f"❌ Erreur : {error_msg[:50]}", icon="❌")
