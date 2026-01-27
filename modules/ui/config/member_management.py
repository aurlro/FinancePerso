import streamlit as st
import pandas as pd
from modules.data_manager import (
    get_members, add_member, delete_member, rename_member,
    update_member_type, get_member_mappings_df,
    add_member_mapping, delete_member_mapping
)

def render_member_management():
    """
    Render the Foyer & Membres tab content.
    Manage household members, external entities, and card-to-member mappings.
    """
    st.header("Membres du Foyer")
    st.markdown("Définissez les personnes associées à ce compte pour l'attribution des dépenses.")
    
    members_df = get_members()
    
    col_list, col_add = st.columns([1, 1])
    
    with col_list:
        if members_df.empty:
            st.info("Aucun membre configuré.")
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
                        with c1: st.text_input("Nom", value=member_name, key=f"edit_in_{member_id}", label_visibility="collapsed")
                        with c2: 
                            if st.button("✅", key=f"sv_{member_id}"):
                                rename_member(member_name, st.session_state[f"edit_in_{member_id}"])
                                st.session_state['editing_member_id'] = None
                                st.rerun()
                        with c3:
                            if st.button("❌", key=f"cl_{member_id}"):
                                st.session_state['editing_member_id'] = None
                                st.rerun()
                    else:
                        c1, c2, c3, c4 = st.columns([3, 1, 0.5, 0.5])
                        c1.write(f"👤 **{member_name}**")
                        if c2.button("➡️ Tiers", key=f"to_ext_{member_id}", help="Déplacer vers Tiers"):
                            update_member_type(member_id, 'EXTERNAL')
                            st.rerun()
                        if c3.button("✏️", key=f"ed_{member_id}"):
                            st.session_state['editing_member_id'] = member_id
                            st.rerun()
                        if c4.button("🗑️", key=f"del_{member_id}"):
                            delete_member(member_id)
                            st.rerun()
            
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
                        with c1: st.text_input("Nom", value=member_name, key=f"edit_in_{member_id}", label_visibility="collapsed")
                        with c2: 
                            if st.button("✅", key=f"sv_{member_id}"):
                                rename_member(member_name, st.session_state[f"edit_in_{member_id}"])
                                st.session_state['editing_member_id'] = None
                                st.rerun()
                        with c3:
                            if st.button("❌", key=f"cl_{member_id}"):
                                st.session_state['editing_member_id'] = None
                                st.rerun()
                    else:
                        c1, c2, c3, c4 = st.columns([3, 1, 0.5, 0.5])
                        c1.write(f"💼 **{member_name}**")
                        if c2.button("⬅️ Foyer", key=f"to_hh_{member_id}", help="Déplacer vers Foyer"):
                            update_member_type(member_id, 'HOUSEHOLD')
                            st.rerun()
                        if c3.button("✏️", key=f"ed_{member_id}"):
                            st.session_state['editing_member_id'] = member_id
                            st.rerun()
                        if c4.button("🗑️", key=f"del_{member_id}"):
                            delete_member(member_id)
                            st.rerun()
    
    with col_add:
        st.subheader("Ajouter un membre")
        with st.form("add_member_form"):
            new_name = st.text_input("Nom", placeholder="Ex: Jean")
            new_type = st.radio("Type", ["HOUSEHOLD", "EXTERNAL"], format_func=lambda x: "🏘️ Foyer" if x == "HOUSEHOLD" else "💼 Tiers")
            if st.form_submit_button("Ajouter"):
                if new_name:
                    if add_member(new_name, new_type):
                        st.success(f"Membre '{new_name}' ajouté !")
                        st.rerun()
                    else:
                        st.error("Ce membre existe déjà.")
                else:
                    st.warning("Veuillez entrer un nom.")
    
    # --- CARD MAPPINGS ---
    st.divider()
    st.subheader("💳 Correspondances Cartes → Membres")
    st.markdown("Associez automatiquement une carte bancaire (4 derniers chiffres) à un membre.")
    
    if members_df.empty:
        st.warning("Ajoutez d'abord des membres pour configurer les correspondances.")
        return
    
    mapping_df = get_member_mappings_df()
    
    col_m1, col_m2 = st.columns([1, 1])
    with col_m1:
        if mapping_df.empty:
            st.info("Aucune correspondance configurée.")
        else:
            for index, row in mapping_df.iterrows():
                cm1, cm2 = st.columns([3, 1])
                cm1.write(f"💳 **{row['card_suffix']}** ➔ {row['member_name']}")
                if cm2.button("🗑️", key=f"del_map_{row['id']}"):
                    delete_member_mapping(row['id'])
                    st.rerun()
    
    with col_m2:
        with st.form("add_mapping_form"):
            suffix = st.text_input("4 derniers chiffres", placeholder="Ex: 6759")
            m_name = st.selectbox("Membre", members_df['name'].tolist() if not members_df.empty else ["Anonyme"])
            if st.form_submit_button("Ajouter la carte"):
                if suffix and m_name:
                    add_member_mapping(suffix, m_name)
                    st.success("Mise à jour effectuée !")
                    st.rerun()
