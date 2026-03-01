"""Assistant de configuration pour la Couple Edition."""

from __future__ import annotations

import streamlit as st

from modules.couple.card_mappings import (
    detect_cards_from_transactions,
    get_all_card_mappings,
    get_unknown_cards,
    save_card_mapping,
)
from modules.couple.couple_settings import (
    get_couple_settings,
    get_setup_progress,
    save_couple_settings,
)
from modules.db.members import get_members


def render_couple_setup():
    """Rend l'interface de configuration couple."""
    st.header("🔧 Configuration Couple", divider=True)
    
    # Vérifier la progression
    progress = get_setup_progress()
    
    # Barre de progression globale
    st.progress(progress['percentage'] / 100, text=f"Configuration: {progress['percentage']}%")
    
    # Étape 1: Définir les membres
    with st.container(border=True):
        st.subheader("👥 Étape 1: Membres du couple")
        _render_members_setup()
    
    # Étape 2: Définir l'utilisateur actuel
    with st.container(border=True):
        st.subheader("👤 Étape 2: Qui utilise l'application ?")
        _render_current_user_setup()
    
    # Étape 3: Mapper les cartes
    with st.container(border=True):
        st.subheader("💳 Étape 3: Attribution des cartes")
        _render_cards_setup()
    
    # Étape 4: Comptes joints
    with st.container(border=True):
        st.subheader("🏦 Étape 4: Comptes communs")
        _render_joint_accounts_setup()
    
    # Résumé si complet
    if progress['is_complete']:
        st.success("✅ Configuration couple terminée ! Le dashboard est disponible dans la Synthèse.")


def _render_members_setup():
    """Configure les membres A et B."""
    settings = get_couple_settings()
    members = get_members()
    
    if members.empty:
        st.warning("⚠️ Aucun membre défini. Créez d'abord des membres dans la section Membres.")
        return
    
    # Utiliser 'name' comme clé (la colonne 'id' ou 'emoji' peut ne pas exister)
    member_options = {row['name']: row['name'] for _, row in members.iterrows()}
    member_ids = list(member_options.keys())
    
    cols = st.columns(2)
    
    with cols[0]:
        st.markdown("**Membre A**")
        current_a = settings.get('member_a_id')
        a_index = member_ids.index(current_a) if current_a in member_ids else 0
        
        selected_a = st.selectbox(
            "Sélectionner",
            options=member_ids,
            format_func=lambda x: member_options[x],
            index=a_index,
            key="member_a_select",
            label_visibility="collapsed"
        )
    
    with cols[1]:
        st.markdown("**Membre B**")
        current_b = settings.get('member_b_id')
        # Filtrer pour ne pas sélectionner le même
        available_for_b = [m for m in member_ids if m != selected_a]
        b_index = available_for_b.index(current_b) if current_b in available_for_b else 0
        
        selected_b = st.selectbox(
            "Sélectionner",
            options=available_for_b,
            format_func=lambda x: member_options[x],
            index=min(b_index, len(available_for_b) - 1),
            key="member_b_select",
            label_visibility="collapsed"
        )
    
    if st.button("💾 Enregistrer les membres", type="primary"):
        if selected_a == selected_b:
            st.error("❌ Les deux membres doivent être différents !")
        else:
            if save_couple_settings(member_a_id=selected_a, member_b_id=selected_b):
                st.success("✅ Membres enregistrés !")
                st.rerun()
            else:
                st.error("❌ Erreur lors de l'enregistrement")


def _render_current_user_setup():
    """Configure l'utilisateur actuel."""
    settings = get_couple_settings()
    
    if not settings.get('member_a_id') or not settings.get('member_b_id'):
        st.info("⏳ Définissez d'abord les membres à l'étape 1.")
        return
    
    members = get_members()
    member_map = {m['id']: f"{m['emoji']} {m['name']}" for m in members}
    
    current = settings.get('current_user_id')
    
    # Options possibles
    options = [
        (settings['member_a_id'], member_map.get(settings['member_a_id'], 'Membre A')),
        (settings['member_b_id'], member_map.get(settings['member_b_id'], 'Membre B')),
    ]
    
    selected = st.radio(
        "Je suis :",
        options=[o[0] for o in options],
        format_func=lambda x: member_map.get(x, 'Inconnu'),
        index=0 if current == settings['member_a_id'] else 1 if current == settings['member_b_id'] else 0,
        key="current_user_radio",
        horizontal=True
    )
    
    if st.button("💾 Confirmer", key="save_current_user"):
        if save_couple_settings(current_user_id=selected):
            st.success("✅ Utilisateur défini !")
            st.rerun()


def _render_cards_setup():
    """Configure l'attribution des cartes."""
    settings = get_couple_settings()
    
    # Détecter automatiquement les nouvelles cartes
    new_cards = detect_cards_from_transactions()
    if new_cards:
        st.info(f"🔍 {len(new_cards)} nouvelle(s) carte(s) détectée(s) dans les transactions !")
    
    # Récupérer tous les mappings
    mappings = get_all_card_mappings(active_only=True)
    unknown_cards = get_unknown_cards()
    
    if not mappings and not unknown_cards:
        st.info("⏳ Aucune carte détectée. Importez d'abord des transactions.")
        return
    
    # Afficher les cartes configurées
    if mappings:
        st.markdown("**Cartes configurées:**")
        
        for mapping in mappings:
            with st.container(border=True):
                cols = st.columns([2, 2, 2, 1])
                
                with cols[0]:
                    st.markdown(f"**💳 ****{mapping['card_suffix']}**")
                
                with cols[1]:
                    # Type de compte
                    type_labels = {
                        'PERSONAL_A': '👤 Perso A',
                        'PERSONAL_B': '👤 Perso B',
                        'JOINT': '👥 Commun',
                        'UNKNOWN': '❓ Inconnu'
                    }
                    st.caption(type_labels.get(mapping['account_type'], mapping['account_type']))
                
                with cols[2]:
                    if mapping.get('member_name'):
                        st.caption(f"{mapping.get('member_emoji', '')} {mapping['member_name']}")
                
                with cols[3]:
                    if st.button("✏️", key=f"edit_card_{mapping['card_suffix']}"):
                        st.session_state[f"editing_card_{mapping['card_suffix']}"] = True
                
                # Formulaire d'édition
                if st.session_state.get(f"editing_card_{mapping['card_suffix']}"):
                    _render_card_editor(mapping)
    
    # Afficher les cartes non configurées
    if unknown_cards:
        st.markdown("**🆕 Cartes à configurer:**")
        
        for card in unknown_cards:
            with st.container(border=True):
                cols = st.columns([2, 2, 2, 1])
                
                with cols[0]:
                    st.markdown(f"**💳 ****{card['card_suffix']}**")
                    st.caption(f"{card['transaction_count']} transactions")
                
                with cols[1]:
                    st.caption(f"Vu du {card['first_seen']} au {card['last_seen']}")
                
                with cols[2]:
                    account_labels = card.get('account_labels', '')
                    if account_labels:
                        st.caption(f"Compte: {account_labels[:30]}...")
                
                with cols[3]:
                    if st.button("⚙️ Configurer", key=f"config_card_{card['card_suffix']}"):
                        st.session_state[f"editing_card_{card['card_suffix']}"] = True
                
                # Formulaire de configuration
                if st.session_state.get(f"editing_card_{card['card_suffix']}"):
                    _render_card_configurator(card, settings)


def _render_card_editor(mapping: dict):
    """Affiche l'éditeur pour une carte existante."""
    settings = get_couple_settings()
    
    st.divider()
    cols = st.columns([2, 2, 2, 1])
    
    with cols[0]:
        account_type = st.selectbox(
            "Type de compte",
            options=['PERSONAL_A', 'PERSONAL_B', 'JOINT', 'UNKNOWN'],
            index=['PERSONAL_A', 'PERSONAL_B', 'JOINT', 'UNKNOWN'].index(mapping['account_type']),
            key=f"edit_type_{mapping['card_suffix']}"
        )
    
    with cols[1]:
        members = get_members()
        member_options = [None] + [m['id'] for m in members]
        member_labels = {None: "— Aucun —", **{m['id']: f"{m['emoji']} {m['name']}" for m in members}}
        
        current_member = mapping.get('member_id')
        member_index = member_options.index(current_member) if current_member in member_options else 0
        
        member_id = st.selectbox(
            "Membre",
            options=member_options,
            format_func=lambda x: member_labels[x],
            index=member_index,
            key=f"edit_member_{mapping['card_suffix']}"
        )
    
    with cols[2]:
        label = st.text_input(
            "Libellé",
            value=mapping.get('label', f"Carte ****{mapping['card_suffix']}"),
            key=f"edit_label_{mapping['card_suffix']}"
        )
    
    with cols[3]:
        st.write("")
        st.write("")
        if st.button("💾", key=f"save_edit_{mapping['card_suffix']}", type="primary"):
            if save_card_mapping(mapping['card_suffix'], account_type, member_id, label):
                del st.session_state[f"editing_card_{mapping['card_suffix']}"]
                st.success("✅ Enregistré !")
                st.rerun()


def _render_card_configurator(card: dict, settings: dict):
    """Affiche le configurateur pour une nouvelle carte."""
    st.divider()
    
    card_suffix = card['card_suffix']
    
    cols = st.columns([2, 2, 2, 1])
    
    with cols[0]:
        account_type = st.selectbox(
            "Type de compte *",
            options=['UNKNOWN', 'PERSONAL_A', 'PERSONAL_B', 'JOINT'],
            format_func=lambda x: {
                'UNKNOWN': '❓ Inconnu',
                'PERSONAL_A': '👤 Perso A',
                'PERSONAL_B': '👤 Perso B',
                'JOINT': '👥 Commun'
            }.get(x, x),
            key=f"config_type_{card_suffix}"
        )
    
    with cols[1]:
        members = get_members()
        member_options = [None] + [m['id'] for m in members]
        member_labels = {None: "— Aucun —", **{m['id']: f"{m['emoji']} {m['name']}" for m in members}}
        
        member_id = st.selectbox(
            "Membre",
            options=member_options,
            format_func=lambda x: member_labels[x],
            key=f"config_member_{card_suffix}"
        )
    
    with cols[2]:
        default_label = f"Carte ****{card_suffix}"
        if card.get('account_labels'):
            default_label += f" ({card['account_labels'].split(',')[0][:20]})"
        
        label = st.text_input(
            "Libellé",
            value=default_label,
            key=f"config_label_{card_suffix}"
        )
    
    with cols[3]:
        st.write("")
        st.write("")
        if st.button("💾", key=f"save_config_{card_suffix}", type="primary"):
            if account_type == 'UNKNOWN':
                st.error("❌ Sélectionnez un type de compte")
            else:
                if save_card_mapping(card_suffix, account_type, member_id, label):
                    del st.session_state[f"editing_card_{card_suffix}"]
                    st.success("✅ Carte configurée !")
                    st.rerun()


def _render_joint_accounts_setup():
    """Configure les libellés de comptes joints."""
    settings = get_couple_settings()
    joint_labels = settings.get('joint_account_labels', [])
    
    st.markdown("**Libellés de comptes communs:**")
    st.caption("Les transactions sur ces comptes seront considérées comme communes.")
    
    # Afficher les labels existants
    for i, label in enumerate(joint_labels):
        cols = st.columns([4, 1])
        with cols[0]:
            st.text(label)
        with cols[1]:
            if st.button("🗑️", key=f"del_joint_{i}"):
                new_labels = [l for j, l in enumerate(joint_labels) if j != i]
                if save_couple_settings(joint_account_labels=new_labels):
                    st.rerun()
    
    # Ajouter un nouveau label
    new_label = st.text_input(
        "Ajouter un libellé de compte commun",
        placeholder="ex: COMPTE JOINT, LIVRET A, etc.",
        key="new_joint_label"
    )
    
    if st.button("➕ Ajouter", key="add_joint_label"):
        if new_label:
            if new_label.upper() not in [l.upper() for l in joint_labels]:
                new_labels = joint_labels + [new_label.upper()]
                if save_couple_settings(joint_account_labels=new_labels):
                    st.success(f"✅ '{new_label}' ajouté")
                    st.rerun()
            else:
                st.warning("Ce libellé existe déjà")
