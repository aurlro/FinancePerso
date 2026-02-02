"""
Audit Tab - Contrôle qualité des données et correction d'anomalies.
"""
import streamlit as st
import time
from typing import Callable
from modules.db.transactions import get_all_transactions, update_transaction_category
from modules.db.rules import add_learning_rule
from modules.categorization import clean_label
from modules.ai.audit_engine import run_full_audit, get_audit_summary
from modules.ui.assistant.state import (
    get_assistant_state, set_assistant_state,
    add_to_corrected, remove_from_corrected,
    add_to_hidden, remove_from_hidden,
    toggle_bulk_selection, clear_bulk_selection
)
from modules.ui.assistant.components import (
    render_progress_card,
    render_empty_state,
    render_anomaly_card,
    render_audit_summary_cards
)


def render_audit_tab():
    """Render the audit quality control tab."""
    st.header("🎯 Audit Qualité")
    st.markdown("Détectez et corrigez les incohérences dans vos données.")
    
    # Initialize state
    audit_results = get_assistant_state('audit_results')
    audit_corrected = get_assistant_state('audit_corrected') or []
    audit_hidden = get_assistant_state('audit_hidden') or []
    
    # Launch audit button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🔎 Lancer l'analyse complète", type="primary", use_container_width=True):
            launch_audit()
    
    with col2:
        if audit_results:
            show_corrected = st.checkbox("Afficher corrigées", 
                                        value=get_assistant_state('show_corrected'),
                                        key="show_corrected_cb")
            show_hidden = st.checkbox("Afficher ignorées", 
                                     value=get_assistant_state('show_hidden'),
                                     key="show_hidden_cb")
            set_assistant_state('show_corrected', show_corrected)
            set_assistant_state('show_hidden', show_hidden)
    
    # Results section
    if audit_results is None:
        render_empty_state(
            icon="🔍",
            title="Aucun audit réalisé",
            description="Lancez une analyse pour détecter les incohérences et anomalies de catégorisation.",
            actions=[]
        )
        return
    
    if not audit_results:
        render_empty_state(
            icon="✨",
            title="Tout est parfait !",
            description="Aucune anomalie détectée. Vos données sont impeccables.",
            actions=[
                ("📈 Voir les tendances", lambda: st.session_state.update({'active_tab': 'analytics'})),
            ]
        )
        return
    
    # Summary cards
    stats = get_audit_summary(audit_results, audit_corrected, audit_hidden)
    render_audit_summary_cards(stats)
    
    # Bulk actions
    if stats['pending'] > 0:
        render_bulk_actions(audit_results)
    
    st.divider()
    
    # Anomalies list
    st.subheader(f"📋 Anomalies ({stats['pending']} en attente)")
    
    show_corrected = get_assistant_state('show_corrected')
    show_hidden = get_assistant_state('show_hidden')
    bulk_selection = get_assistant_state('audit_bulk_selection') or []
    
    visible_count = 0
    for i, item in enumerate(audit_results):
        is_corrected = i in audit_corrected
        is_hidden = i in audit_hidden
        
        # Skip based on filters
        if is_hidden and not show_hidden:
            continue
        if is_corrected and not show_corrected:
            continue
        
        visible_count += 1
        
        render_anomaly_card(
            index=i,
            item=item,
            is_corrected=is_corrected,
            is_hidden=is_hidden,
            is_selected=i in bulk_selection,
            on_select=on_anomaly_select,
            on_correct=on_anomaly_correct,
            on_hide=on_anomaly_hide,
            on_apply=on_anomaly_apply if not is_corrected else None
        )
        
        # Transaction editor for uncorrected items
        if not is_corrected and not is_hidden:
            render_transaction_editor(i, item)
    
    if visible_count == 0:
        st.info("Aucune anomalie à afficher avec les filtres actuels.")


def launch_audit():
    """Launch the full audit with progress tracking."""
    df = get_all_transactions()
    
    if df.empty:
        st.warning("Pas de transactions à analyser.")
        return
    
    # Progress UI
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Loading
    status_text.info("📊 Chargement des transactions...")
    progress_bar.progress(15)
    time.sleep(0.3)
    
    # Step 2: Detect inconsistencies
    status_text.info("🔍 Détection des incohérences...")
    progress_bar.progress(40)
    
    # Step 3: AI audit
    status_text.info("🤖 Analyse IA...")
    progress_bar.progress(75)
    
    # Run audit
    results = run_full_audit(df, use_ai=True)
    
    # Finalize
    progress_bar.progress(100)
    status_text.success(f"✅ Analyse terminée ! {results['total_anomalies']} anomalies trouvées")
    time.sleep(0.8)
    
    progress_bar.empty()
    status_text.empty()
    
    # Save results
    set_assistant_state('audit_results', results['inconsistencies'] + results['ai_suggestions'])
    set_assistant_state('audit_corrected', [])
    set_assistant_state('audit_hidden', [])
    set_assistant_state('audit_bulk_selection', [])
    
    st.rerun()


def render_bulk_actions(audit_results: list):
    """Render bulk action buttons."""
    st.markdown("**Actions en masse**")
    
    cols = st.columns([2, 2, 2, 3])
    
    with cols[0]:
        if st.button("📋 Tout sélectionner", use_container_width=True, key="bulk_select_all"):
            set_assistant_state('audit_bulk_selection', list(range(len(audit_results))))
            st.rerun()
    
    with cols[1]:
        if st.button("❌ Désélectionner", use_container_width=True, key="bulk_deselect"):
            clear_bulk_selection()
            st.rerun()
    
    with cols[2]:
        if st.button("🗑️ Ignorer sélection", use_container_width=True, key="bulk_ignore"):
            bulk_hide_selected()
    
    with cols[3]:
        selected_count = len(get_assistant_state('audit_bulk_selection') or [])
        if selected_count > 0:
            if st.button(f"🧠 Créer règles ({selected_count})", 
                        use_container_width=True, type="primary", key="bulk_rules"):
                set_assistant_state('confirm_bulk_rules', True)
                st.rerun()
        else:
            st.button("🧠 Créer règles", use_container_width=True, type="primary",
                     disabled=True, key="bulk_rules")
    
    # Confirmation dialog
    if get_assistant_state('confirm_bulk_rules'):
        render_bulk_confirmation()


def render_bulk_confirmation():
    """Render confirmation dialog for bulk rule creation."""
    selected = get_assistant_state('audit_bulk_selection') or []
    audit_results = get_assistant_state('audit_results') or []
    
    st.warning(f"⚠️ Créer {len(selected)} règles d'apprentissage ?")
    
    cols = st.columns([1, 1])
    
    with cols[0]:
        if st.button("✅ Confirmer", type="primary", key="confirm_bulk_yes"):
            rules_count = 0
            for idx in selected:
                if idx < len(audit_results):
                    item = audit_results[idx]
                    suggested = item.get('suggested_category')
                    if suggested:
                        pattern = clean_label(item['label'])
                        if add_learning_rule(pattern, suggested, priority=5):
                            rules_count += 1
            
            set_assistant_state('confirm_bulk_rules', False)
            clear_bulk_selection()
            
            if rules_count > 0:
                st.success(f"✅ {rules_count} règles créées !")
                st.toast(f"🧠 {rules_count} règles mémorisées", icon="🧠")
                st.rerun()
    
    with cols[1]:
        if st.button("❌ Annuler", key="confirm_bulk_no"):
            set_assistant_state('confirm_bulk_rules', False)
            st.rerun()


def render_transaction_editor(index: int, item: dict):
    """Render transaction editor for an anomaly."""
    tx_ids = item['rows']['id'].tolist()
    
    from modules.ui.components.transaction_drill_down import render_transaction_drill_down
    
    render_transaction_drill_down(
        category=item.get('suggested_category') or item['rows'].iloc[0]['category_validated'],
        transaction_ids=tx_ids,
        key_prefix=f"audit_drill_{index}",
        show_anomaly_management=False
    )


def on_anomaly_select(index: int, selected: bool):
    """Handle anomaly selection toggle."""
    toggle_bulk_selection(index, selected)
    st.rerun()


def on_anomaly_correct(index: int):
    """Handle marking anomaly as corrected."""
    if index in (get_assistant_state('audit_corrected') or []):
        remove_from_corrected(index)
    else:
        add_to_corrected(index)
    st.rerun()


def on_anomaly_hide(index: int):
    """Handle hiding anomaly."""
    if index in (get_assistant_state('audit_hidden') or []):
        remove_from_hidden(index)
    else:
        add_to_hidden(index)
    st.rerun()


def on_anomaly_apply(index: int):
    """Handle applying suggested category to anomaly."""
    audit_results = get_assistant_state('audit_results') or []
    if index >= len(audit_results):
        return
    
    item = audit_results[index]
    suggested = item.get('suggested_category')
    
    if not suggested:
        return
    
    tx_ids = item['rows']['id'].tolist()
    
    # Apply to all transactions
    for tx_id in tx_ids:
        update_transaction_category(tx_id, suggested)
        add_learning_rule(clean_label(item['label']), suggested, priority=5)
    
    # Mark as corrected
    add_to_corrected(index)
    
    # Invalidate caches
    from modules.cache_manager import invalidate_transaction_caches, invalidate_rule_caches
    invalidate_transaction_caches()
    invalidate_rule_caches()
    
    st.success(f"✅ Catégorie '{suggested}' appliquée à {len(tx_ids)} transactions !")
    st.toast("Catégorie corrigée et mémorisée", icon="🧠")
    st.rerun()


def bulk_hide_selected():
    """Hide all selected anomalies."""
    selected = get_assistant_state('audit_bulk_selection') or []
    hidden = get_assistant_state('audit_hidden') or []
    
    for idx in selected:
        if idx not in hidden:
            hidden.append(idx)
    
    set_assistant_state('audit_hidden', hidden)
    clear_bulk_selection()
    st.rerun()
