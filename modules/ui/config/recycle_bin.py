"""
Recycle Bin UI Component - Interface de gestion de la corbeille
"""

import streamlit as st
import pandas as pd

from modules.db.recycle_bin import (
    get_recycle_bin_contents,
    restore_transaction,
    permanently_delete,
    purge_expired_items,
    get_recycle_bin_stats,
)
from modules.ui.feedback import toast_success, toast_error, toast_info


def render_recycle_bin_manager():
    """Render the recycle bin management interface."""
    
    st.subheader("🗑️ Corbeille")
    st.markdown("Les transactions supprimées sont conservées 30 jours avant suppression définitive.")
    
    # Statistics
    stats = get_recycle_bin_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Éléments dans la corbeille", stats['total_items'])
    with col2:
        st.metric("Éléments restaurés", stats['restored'])
    with col3:
        if stats['expired'] > 0:
            st.metric("À purger", stats['expired'])
    
    # Purge expired button
    if stats['expired'] > 0:
        if st.button("🧹 Purger les éléments expirés", type="secondary"):
            purged = purge_expired_items()
            if purged > 0:
                toast_success(f"{purged} élément(s) supprimé(s) définitivement")
                st.rerun()
    
    st.divider()
    
    # Get recycle bin contents
    df = get_recycle_bin_contents(limit=100)
    
    if df.empty:
        st.info("La corbeille est vide.")
        return
    
    # Display items
    st.markdown(f"#### 📋 Éléments récupérables ({len(df)})")
    
    for _, row in df.iterrows():
        with st.container(border=True):
            cols = st.columns([3, 2, 1, 1, 1])
            
            with cols[0]:
                label = row['label'][:40] if row['label'] else "Sans libellé"
                st.markdown(f"**{label}**")
                st.caption(f"ID original: {row['original_id']}")
            
            with cols[1]:
                amount = row['amount'] if pd.notna(row['amount']) else 0
                date = row['date'] if pd.notna(row['date']) else "?"
                color = "green" if amount > 0 else "red"
                st.markdown(f":{color}[**{abs(amount):,.2f} €**]")
                st.caption(f"📅 {date}")
            
            with cols[2]:
                category = row['category'] if pd.notna(row['category']) else "Non catégorisé"
                st.caption(f"🏷️ {category}")
            
            with cols[3]:
                # Restore button
                if st.button(
                    "↩️ Restaurer",
                    key=f"restore_{row['recycle_id']}",
                    use_container_width=True
                ):
                    success, msg = restore_transaction(row['recycle_id'])
                    if success:
                        toast_success(msg)
                        st.rerun()
                    else:
                        toast_error(msg)
            
            with cols[4]:
                # Permanent delete with confirmation
                if st.button(
                    "🗑️ Supprimer",
                    key=f"delete_{row['recycle_id']}",
                    use_container_width=True
                ):
                    # Store in session state for confirmation
                    st.session_state[f"confirm_delete_{row['recycle_id']}"] = True
                    st.rerun()
    
    # Handle confirmations
    for key in list(st.session_state.keys()):
        if key.startswith("confirm_delete_"):
            recycle_id = int(key.split("_")[-1])
            
            with st.container(border=True):
                st.warning("⚠️ Cette action est irréversible!")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Confirmer la suppression", key=f"confirm_{recycle_id}"):
                        success, msg = permanently_delete(recycle_id)
                        if success:
                            toast_success(msg)
                        else:
                            toast_error(msg)
                        del st.session_state[key]
                        st.rerun()
                
                with col2:
                    if st.button("❌ Annuler", key=f"cancel_{recycle_id}"):
                        del st.session_state[key]
                        st.rerun()


def render_recycle_bin_mini():
    """Render a mini version for dashboards (just the count and quick access)."""
    
    stats = get_recycle_bin_stats()
    
    if stats['total_items'] > 0:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"🗑️ **{stats['total_items']}** transaction(s) dans la corbeille")
                st.caption("Vous pouvez les restaurer dans les 30 jours suivant la suppression")
            
            with col2:
                if st.button("Voir la corbeille", use_container_width=True):
                    st.session_state["config_tab"] = "Sauvegarde & Données"
                    st.rerun()
