"""
Composants UI pour la gestion des récurrences détectées.
Permet de confirmer, rejeter et gérer les récurrences.
"""
import streamlit as st
import pandas as pd
from typing import Callable, Dict, Any, List
from modules.db.recurrence_feedback import (
    set_recurrence_feedback,
    get_recurrence_feedback,
    get_all_feedback,
    delete_feedback,
    get_feedback_stats,
    is_pattern_rejected,
    is_pattern_confirmed
)


def render_recurrence_card(
    row: pd.Series,
    on_confirm: Callable,
    on_reject: Callable,
    cat_emoji_map: Dict[str, str] = None
):
    """
    Render a recurrence detection card with user feedback buttons.
    
    Args:
        row: DataFrame row with recurrence data
        on_confirm: Callback when user confirms it's recurring
        on_reject: Callback when user rejects it
        cat_emoji_map: Optional category emoji mapping
    """
    label = row['label']
    category = row.get('category', '')
    
    # Check if already has feedback
    existing_feedback = get_recurrence_feedback(label, category)
    
    # Determine status color
    if existing_feedback:
        if existing_feedback['user_feedback'] == 'confirmed':
            border_color = "#22c55e"
            bg_color = "#f0fdf4"
            status_icon = "✅"
            status_text = "Confirmée"
        else:
            border_color = "#ef4444"
            bg_color = "#fef2f2"
            status_icon = "❌"
            status_text = "Rejetée"
    else:
        border_color = "#e2e8f0"
        bg_color = "#ffffff"
        status_icon = "🤔"
        status_text = "À vérifier"
    
    # Card container
    st.markdown(f"""
    <div style='
        border-left: 4px solid {border_color};
        background: {bg_color};
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        border: 1px solid {border_color};
    '>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content columns
    cat_name = category
    emoji = cat_emoji_map.get(cat_name, "🏷️") if cat_emoji_map else "🏷️"
    
    c1, c2, c3, c4, c5 = st.columns([2.5, 1, 1, 1, 0.5])
    
    with c1:
        display_label = label
        if len(row.get('sample_labels', [])) > 1:
            display_label = f"{label} *(+{len(row['sample_labels'])-1} variantes)*"
        
        st.markdown(f"**{emoji} {display_label}**")
        st.caption(f"{row['count']} occurrences")
        
        # Show status badge
        if existing_feedback:
            badge_color = "green" if existing_feedback['user_feedback'] == 'confirmed' else "red"
            st.markdown(f":{badge_color}-badge[{status_text}]")
    
    with c2:
        amount = row['avg_amount']
        st.markdown(f"**{abs(amount):,.2f} €**")
        st.caption("Montant moyen")
    
    with c3:
        st.markdown(f"**{row['frequency_label']}**")
        st.caption(f"~{row['frequency_days']:.0f} jours")
    
    with c4:
        st.markdown(f":grey[{row['last_date']}]")
        st.caption("Dernière")
    
    with c5:
        var_color = "🟢" if row['variability'] == 'Fixe' else "🟡"
        st.markdown(f"{var_color}")
        st.caption(row['variability'])
    
    # Feedback buttons row
    st.markdown("**Votre avis :**")
    
    btn_cols = st.columns([1, 1, 1, 2])
    
    with btn_cols[0]:
        if existing_feedback and existing_feedback['user_feedback'] == 'confirmed':
            if st.button("✅ Confirmée", key=f"btn_conf_{label[:30]}", 
                        type="primary", use_container_width=True):
                pass  # Already confirmed
        else:
            if st.button("✅ C'est une récurrence", key=f"btn_conf_{label[:30]}", 
                        type="secondary", use_container_width=True):
                on_confirm(label, category)
    
    with btn_cols[1]:
        if existing_feedback and existing_feedback['user_feedback'] == 'rejected':
            if st.button("❌ Rejetée", key=f"btn_rej_{label[:30]}", 
                        type="primary", use_container_width=True):
                pass  # Already rejected
        else:
            if st.button("❌ Pas une récurrence", key=f"btn_rej_{label[:30]}", 
                        type="secondary", use_container_width=True):
                on_reject(label, category)
    
    with btn_cols[2]:
        if existing_feedback:
            if st.button("🔄 Réinitialiser", key=f"btn_reset_{label[:30]}", 
                        use_container_width=True):
                delete_feedback(label, category)
                st.rerun()
    
    with btn_cols[3]:
        if existing_feedback and existing_feedback.get('notes'):
            st.caption(f"💬 {existing_feedback['notes']}")
        else:
            # Quick note input
            note_key = f"note_{label[:30]}"
            note = st.text_input("Note (optionnel)", key=note_key, 
                                placeholder="Pourquoi ?", label_visibility="collapsed")
            if note:
                st.session_state[f'pending_note_{label}'] = note


def render_feedback_summary():
    """Render summary of user's feedback on recurrences."""
    stats = get_feedback_stats()
    
    if stats['total'] == 0:
        return
    
    st.subheader("📊 Vos validations")
    
    cols = st.columns(3)
    
    with cols[0]:
        st.metric("Total vérifié", stats['total'])
    with cols[1]:
        st.metric("✅ Confirmées", stats['confirmed'])
    with cols[2]:
        st.metric("❌ Rejetées", stats['rejected'])


def render_confirmed_recurring_section(
    recurring_df: pd.DataFrame,
    cat_emoji_map: Dict[str, str] = None
):
    """Render section showing user-confirmed recurrences."""
    from modules.db.recurrence_feedback import get_confirmed_recurring
    
    confirmed_patterns = get_confirmed_recurring()
    
    if not confirmed_patterns:
        return
    
    st.divider()
    st.subheader(f"✅ Récurrences confirmées ({len(confirmed_patterns)})")
    
    # Filter dataframe to show only confirmed
    confirmed_df = recurring_df[recurring_df['label'].isin(confirmed_patterns)]
    
    if confirmed_df.empty:
        st.info("Les patterns confirmés n'apparaissent pas dans les détections actuelles.")
        return
    
    with st.expander("Voir les récurrences confirmées", expanded=False):
        for _, row in confirmed_df.iterrows():
            cat_name = row['category']
            emoji = cat_emoji_map.get(cat_name, "🏷️") if cat_emoji_map else "🏷️"
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{emoji} {row['label']}**")
            with col2:
                st.markdown(f"{abs(row['avg_amount']):,.2f} €")
            with col3:
                if st.button("🔄 Annuler", key=f"undo_conf_{row['label'][:30]}"):
                    delete_feedback(row['label'], row['category'])
                    st.rerun()


def render_rejected_recurring_section():
    """Render section showing rejected (false positive) recurrences."""
    rejected = get_all_feedback(status='rejected')
    
    if not rejected:
        return
    
    st.divider()
    st.subheader(f"❌ Faux positifs exclus ({len(rejected)})")
    
    with st.expander("Voir les récurrences rejetées", expanded=False):
        for item in rejected:
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**{item['label_pattern']}**")
                if item['category']:
                    st.caption(f"Catégorie : {item['category']}")
            with col2:
                if item.get('notes'):
                    st.caption(f"💬 {item['notes']}")
            with col3:
                if st.button("🔄 Restaurer", key=f"undo_rej_{item['id']}"):
                    delete_feedback(item['label_pattern'], item['category'])
                    st.rerun()


def render_manual_add_section(on_add: Callable):
    """Render section to manually add a recurring pattern."""
    st.divider()
    st.subheader("➕ Ajouter manuellement une récurrence")
    
    with st.form("manual_recurrence"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            label_pattern = st.text_input(
                "Libellé ou pattern",
                placeholder="Ex: NETFLIX, SALAIRE, EDF..."
            )
        
        with col2:
            from modules.db.categories import get_categories
            categories = get_categories()
            category = st.selectbox(
                "Catégorie",
                options=[""] + categories,
                format_func=lambda x: "Toutes catégories" if x == "" else x
            )
        
        col3, col4 = st.columns(2)
        with col3:
            amount = st.number_input(
                "Montant estimé (€)",
                value=0.0,
                step=10.0
            )
        with col4:
            frequency = st.selectbox(
                "Fréquence",
                options=["Mensuel", "Trimestriel", "Annuel", "Variable"],
                index=0
            )
        
        notes = st.text_area(
            "Notes",
            placeholder="Pourquoi cette opération est récurrente...",
            height=80
        )
        
        submitted = st.form_submit_button("✅ Ajouter comme récurrence", type="primary")
        
        if submitted and label_pattern:
            # Save as confirmed recurrence
            success = set_recurrence_feedback(
                label_pattern=label_pattern.upper(),
                is_recurring=True,
                category=category if category else None,
                notes=notes or f"Ajouté manuellement - {frequency} - {amount:.2f}€"
            )
            if success:
                st.success(f"✅ '{label_pattern}' ajouté comme récurrence !")
                on_add(label_pattern, category)
            else:
                st.error("❌ Erreur lors de l'ajout")


def filter_by_user_feedback(
    recurring_df: pd.DataFrame,
    show_confirmed: bool = True,
    show_rejected: bool = False,
    show_pending: bool = True
) -> pd.DataFrame:
    """
    Filter recurrence dataframe based on user feedback.
    
    Args:
        recurring_df: DataFrame with detected recurrences
        show_confirmed: Include confirmed recurrences
        show_rejected: Include rejected recurrences
        show_pending: Include pending (not yet validated) recurrences
        
    Returns:
        Filtered DataFrame
    """
    if recurring_df.empty:
        return recurring_df
    
    mask = pd.Series([False] * len(recurring_df), index=recurring_df.index)
    
    for idx, row in recurring_df.iterrows():
        label = row['label']
        category = row.get('category', '')
        
        existing = get_recurrence_feedback(label, category)
        
        if existing:
            if existing['user_feedback'] == 'confirmed' and show_confirmed:
                mask.iloc[idx] = True
            elif existing['user_feedback'] == 'rejected' and show_rejected:
                mask.iloc[idx] = True
        else:
            if show_pending:
                mask.iloc[idx] = True
    
    return recurring_df[mask]


def get_validation_status_badge(label: str, category: str = None) -> str:
    """Get a status badge emoji for a recurrence pattern."""
    if is_pattern_confirmed(label, category):
        return "✅"
    elif is_pattern_rejected(label, category):
        return "❌"
    else:
        return "🤔"


def render_batch_validation_actions(
    selected_labels: List[str],
    on_batch_confirm: Callable,
    on_batch_reject: Callable
):
    """Render batch actions for multiple selected recurrences."""
    if not selected_labels:
        return
    
    st.markdown(f"**{len(selected_labels)} éléments sélectionnés**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Tout confirmer", type="primary", use_container_width=True):
            for label in selected_labels:
                set_recurrence_feedback(label, is_recurring=True)
            on_batch_confirm()
    
    with col2:
        if st.button("❌ Tout rejeter", use_container_width=True):
            for label in selected_labels:
                set_recurrence_feedback(label, is_recurring=False)
            on_batch_reject()
