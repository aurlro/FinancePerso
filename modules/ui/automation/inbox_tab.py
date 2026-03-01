"""
📥 Inbox Tab - Tout ce qui demande votre attention

Regroupe :
- Récurrences à valider (anciennement "Validation")
- Suggestions intelligentes (règles, mappings)
- Alertes (zombies, augmentations)

Objectif : Inbox Zero - tout traiter depuis un seul endroit
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from modules.ai.smart_suggestions import Suggestion, get_smart_suggestions
from modules.db.budgets import get_budgets
from modules.db.categories import get_categories_with_emojis
from modules.db.members import (
    add_account_member_mapping,
    add_member,
    add_member_mapping,
    get_members,
)
from modules.db.recurrence_feedback import (
    get_all_feedback,
    set_recurrence_feedback,
)
from modules.db.rules import get_learning_rules
from modules.db.transactions import get_all_transactions
from modules.logger import logger
from modules.recurring_detector import detect_recurring_payments_v2
from modules.ui.automation.alerts_section import render_alerts_section as render_alerts_panel
from modules.ui.automation.suggestion_actions import (
    execute_suggestion_action,
    render_action_inline_view,
)
from modules.ui.feedback import toast_error, toast_info, toast_success

# =============================================================================
# INBOX STATE MANAGEMENT
# =============================================================================

def init_inbox_state():
    """Initialize session state for inbox."""
    if "inbox_filter" not in st.session_state:
        st.session_state.inbox_filter = "all"  # all, recurrences, suggestions, alerts
    if "inbox_dismissed" not in st.session_state:
        st.session_state.inbox_dismissed = set()
    if "inbox_last_refresh" not in st.session_state:
        st.session_state.inbox_last_refresh = datetime.now()
    if "active_suggestion_result" not in st.session_state:
        st.session_state.active_suggestion_result = None  # Stores {suggestion_id, result}}


@st.cache_data(ttl=60)
def _fetch_inbox_data() -> tuple:
    """
    Fetch raw data for inbox count calculation with caching.
    
    Returns:
        tuple: (transactions_df, feedback_list, suggestions_list)
    """
    df = get_all_transactions()
    
    if df.empty:
        return df, [], []
    
    # Get recurring payments data
    validated_df = df[df["status"] == "validated"]
    recurring_df = detect_recurring_payments_v2(validated_df) if not validated_df.empty else pd.DataFrame()
    
    # Get feedback map
    feedback = get_all_feedback()
    
    # Get suggestions
    suggestions = get_smart_suggestions(df, get_learning_rules(), get_budgets(), get_members())
    
    return df, feedback, recurring_df, suggestions


def get_inbox_count() -> dict:
    """Get counts for inbox badge."""
    try:
        with st.spinner("Chargement..."):
            df, feedback, recurring_df, suggestions = _fetch_inbox_data()
        
        if df.empty:
            return {"total": 0, "recurrences": 0, "suggestions": 0, "alerts": 0}

        # Count recurrences to validate using vectorized operation
        feedback_map = {(f["label_pattern"], f["category"]): f["user_feedback"] for f in feedback}
        
        pending_recs = 0
        if not recurring_df.empty:
            # Vectorized operation instead of iterrows()
            pending_mask = recurring_df.apply(
                lambda row: (row["label"], row.get("category", "")) not in feedback_map,
                axis=1
            )
            pending_recs = pending_mask.sum()

        # Filter out dismissed suggestions
        suggestions = [s for s in suggestions if s.id not in st.session_state.get("inbox_dismissed", set())]

        return {
            "total": pending_recs + len(suggestions),
            "recurrences": pending_recs,
            "suggestions": len(suggestions),
            "alerts": 0,  # TODO: add zombie/increase alerts
        }
    except Exception as e:
        logger.error(f"Error getting inbox count: {e}")
        return {"total": 0, "recurrences": 0, "suggestions": 0, "alerts": 0}


# =============================================================================
# INBOX TAB RENDERER
# =============================================================================

def render_inbox_tab():
    """Render the unified inbox tab."""
    init_inbox_state()
    
    # Header avec compteurs
    counts = get_inbox_count()
    
    col_title, col_refresh = st.columns([3, 1])
    with col_title:
        st.header("📥 Vos actions en attente")
        if counts["total"] == 0:
            st.success("🎉 Tout est à jour ! Aucune action en attente.")
        else:
            st.caption(f"**{counts['total']}** élément(s) à traiter")
    
    with col_refresh:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.session_state.inbox_last_refresh = datetime.now()
            st.rerun()
    
    if counts["total"] == 0:
        _render_empty_inbox()
        return
    
    # Filtres
    st.divider()
    filter_cols = st.columns([1, 1, 1, 1, 2])
    
    filter_options = {
        "all": f"📋 Tout ({counts['total']})",
        "recurrences": f"🔁 Abonnements ({counts['recurrences']})",
        "suggestions": f"💡 Suggestions ({counts['suggestions']})",
        "alerts": f"⚠️ Alertes ({counts['alerts']})",
    }
    
    with filter_cols[0]:
        if st.button(filter_options["all"], use_container_width=True, 
                     type="primary" if st.session_state.inbox_filter == "all" else "secondary"):
            st.session_state.inbox_filter = "all"
            st.rerun()
    
    with filter_cols[1]:
        if st.button(filter_options["recurrences"], use_container_width=True,
                     type="primary" if st.session_state.inbox_filter == "recurrences" else "secondary"):
            st.session_state.inbox_filter = "recurrences"
            st.rerun()
    
    with filter_cols[2]:
        if st.button(filter_options["suggestions"], use_container_width=True,
                     type="primary" if st.session_state.inbox_filter == "suggestions" else "secondary"):
            st.session_state.inbox_filter = "suggestions"
            st.rerun()
    
    with filter_cols[3]:
        if st.button(filter_options["alerts"], use_container_width=True,
                     type="primary" if st.session_state.inbox_filter == "alerts" else "secondary"):
            st.session_state.inbox_filter = "alerts"
            st.rerun()
    
    st.divider()
    
    # Contenu selon le filtre
    current_filter = st.session_state.inbox_filter
    
    if current_filter in ["all", "recurrences"]:
        _render_recurrences_section(current_filter == "recurrences")
    
    if current_filter in ["all", "suggestions"]:
        _render_suggestions_section(current_filter == "suggestions")
    
    if current_filter in ["all", "alerts"]:
        _render_alerts_section(current_filter == "alerts")


def _render_empty_inbox():
    """Render empty state when inbox is clear."""
    st.html("""
    <div style="text-align: center; padding: 60px 20px;">
        <div style="font-size: 64px; margin-bottom: 20px;">🎉</div>
        <h2 style="margin-bottom: 10px; color: #22c55e;">Inbox Zero !</h2>
        <p style="color: #6b7280; max-width: 400px; margin: 0 auto;">
            Toutes les propositions de l'IA ont été traitées.<br>
            L'apprentissage continue en arrière-plan.
        </p>
    </div>
    """)


def _render_recurrences_section(standalone: bool = False):
    """Render recurrences pending validation."""
    df = get_all_transactions()
    if df.empty:
        if standalone:
            st.info("📭 Importez des transactions pour détecter vos abonnements.")
        return
    
    validated_df = df[df["status"] == "validated"]
    if validated_df.empty:
        if standalone:
            st.info("📭 Validez quelques transactions pour permettre la détection d'abonnements.")
        return
    
    # Détection
    with st.spinner("Analyse des abonnements...") if standalone else st.empty():
        recurring_df = detect_recurring_payments_v2(validated_df)
    
    if recurring_df.empty:
        if standalone:
            st.info("🔍 Aucun abonnement détecté pour le moment.")
        return
    
    # Enrichir avec feedback existant
    feedback = get_all_feedback()
    feedback_map = {(f["label_pattern"], f["category"]): f["user_feedback"] for f in feedback}
    
    # Filtrer uniquement les pending
    pending_mask = recurring_df.apply(
        lambda row: (row["label"], row.get("category", "")) not in feedback_map,
        axis=1
    )
    pending_df = recurring_df[pending_mask]
    
    if pending_df.empty:
        if standalone:
            st.success("✅ Tous les abonnements détectés ont été validés.")
        return
    
    # Affichage
    if not standalone:
        st.subheader(f"🔁 {len(pending_df)} abonnement(s) à confirmer")
    
    cat_emoji_map = get_categories_with_emojis()
    
    for _, row in pending_df.head(5).iterrows():
        _render_recurrence_card(row, cat_emoji_map)
    
    if len(pending_df) > 5:
        st.caption(f"... et {len(pending_df) - 5} autres")


def _render_recurrence_card(row: pd.Series, cat_emoji_map: dict):
    """Render a single recurrence card with inline actions."""
    label = row["label"]
    category = row.get("category", "")
    emoji = cat_emoji_map.get(category, "🏷️")
    
    with st.container(border=True):
        cols = st.columns([3, 1, 1, 2])
        
        with cols[0]:
            st.markdown(f"**{emoji} {label}**")
            st.caption(f"{row['count']} paiements • Dernier: {row['last_date']}")
        
        with cols[1]:
            amount = row["avg_amount"]
            color = "green" if amount > 0 else "red"
            st.markdown(f":{color}[**{abs(amount):,.2f} €** / mois]")
        
        with cols[2]:
            st.caption(f"Fréquence: ~{row['frequency_days']:.0f} jours")
        
        with cols[3]:
            action_cols = st.columns(2)
            with action_cols[0]:
                if st.button("✅ Confirmer", key=f"rec_conf_{label[:30]}", type="primary", use_container_width=True):
                    set_recurrence_feedback(label, True, category, "Confirmé depuis l'inbox")
                    toast_success(f"✅ '{label[:30]}...' ajouté à vos abonnements")
                    st.rerun()
            with action_cols[1]:
                if st.button("❌ Ignorer", key=f"rec_rej_{label[:30]}", use_container_width=True):
                    set_recurrence_feedback(label, False, category, "Ignoré depuis l'inbox")
                    toast_info("🗑️ Proposition ignorée")
                    st.rerun()


def _render_suggestions_section(standalone: bool = False):
    """Render smart suggestions with inline actions and results."""
    df = get_all_transactions()
    if df.empty:
        if standalone:
            st.info("📭 Ajoutez des transactions pour recevoir des suggestions.")
        return
    
    # Get suggestions
    suggestions = get_smart_suggestions(df, get_learning_rules(), get_budgets(), get_members())
    suggestions = [s for s in suggestions if s.id not in st.session_state.get("inbox_dismissed", set())]
    
    if not suggestions:
        if standalone:
            st.success("🎉 Aucune suggestion pour le moment. Tout semble bien configuré !")
        return
    
    if not standalone:
        st.subheader(f"💡 {len(suggestions)} suggestion(s) d'optimisation")
    
    # Trier par priorité
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda s: priority_order.get(s.priority, 3))
    
    # Afficher le formulaire actif (s'il existe) avant les cartes
    active_suggestion_id = st.session_state.get("active_suggestion_id")
    if active_suggestion_id:
        active_suggestion = next((s for s in suggestions if s.id == active_suggestion_id), None)
        if active_suggestion:
            action_type = active_suggestion.action_data.get("type") if isinstance(active_suggestion.action_data, dict) else None
            if action_type in ("map_card", "map_account"):
                with st.container(border=True):
                    st.markdown("### 👤 Définir un membre par défaut")
                    _render_member_mapping_form(active_suggestion, f"active_{active_suggestion.id}", "active_suggestion_id")
                st.divider()
    
    # Afficher le résultat inline d'une action (s'il existe)
    active_result = st.session_state.get("active_suggestion_result")
    if active_result:
        suggestion_id = active_result.get("suggestion_id")
        result = active_result.get("result", {})
        stored_suggestion = active_result.get("suggestion")
        
        # Get action type from stored suggestion or result
        action_type = ""
        if stored_suggestion and isinstance(stored_suggestion.action_data, dict):
            action_type = stored_suggestion.action_data.get("type", "")
        elif result.get("action_type"):
            action_type = result["action_type"]
        
        if result.get("view_data") and action_type:
            # Render inline view
            with st.container(border=True):
                rendered = render_action_inline_view(action_type, result["view_data"])
                if rendered:
                    # Close button
                    if st.button("✕ Fermer", key=f"close_result_{suggestion_id}"):
                        st.session_state.active_suggestion_result = None
                        st.rerun()
                    st.divider()
    
    # Afficher les suggestions (sauf l'active qui est déjà affichée)
    for suggestion in suggestions[:5]:
        if suggestion.id != active_suggestion_id:
            _render_suggestion_card(suggestion)
    
    if len(suggestions) > 5:
        st.caption(f"... et {len(suggestions) - 5} autres suggestions")


def _render_suggestion_card(suggestion: Suggestion):
    """Render a single suggestion card with inline action."""
    priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    priority_icon = priority_icons.get(suggestion.priority, "⚪")
    
    # Générer une clé unique pour cette suggestion
    card_key = f"sugg_card_{suggestion.id}"
    
    with st.container(border=True):
        cols = st.columns([0.3, 3, 1.5, 0.5])
        
        with cols[0]:
            type_icons = {
                "rule": "📝",
                "category": "🏷️",
                "member": "👤",
                "budget": "💰",
                "duplicate": "⚠️",
                "pattern": "📊",
            }
            st.markdown(f"<div style='font-size: 24px; text-align: center;'>{type_icons.get(suggestion.type, '💡')}</div>", 
                       unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f"**{suggestion.title}** {priority_icon}")
            st.caption(suggestion.description)
        
        with cols[2]:
            # Action button selon le type
            action_key = f"sugg_act_{suggestion.id}"
            
            if suggestion.auto_fixable:
                btn_label = f"✨ {suggestion.action_label}"
                btn_type = "primary"
            else:
                btn_label = suggestion.action_label
                btn_type = "secondary"
            
            if st.button(btn_label, key=action_key, type=btn_type, use_container_width=True):
                # Pour map_card/map_account, on met cette suggestion comme active
                action_type = suggestion.action_data.get("type") if isinstance(suggestion.action_data, dict) else None
                if action_type in ("map_card", "map_account"):
                    st.session_state["active_suggestion_id"] = suggestion.id
                    st.rerun()
                else:
                    # Use new action handler system
                    result = _handle_suggestion_action(suggestion)
                    
                    # If the result has view_data, show it inline
                    if result.get("view_data"):
                        st.session_state["active_suggestion_result"] = {
                            "suggestion_id": suggestion.id,
                            "suggestion": suggestion,
                            "result": result,
                        }
                        st.rerun()
                    elif result.get("success"):
                        # For simple actions without view, dismiss the suggestion
                        st.session_state.inbox_dismissed.add(suggestion.id)
                        st.rerun()
        
        with cols[3]:
            # Confirmation dialog for dismiss suggestion
            confirm_key = f"confirm_dismiss_sugg_{suggestion.id}"
            
            if not st.session_state.get(confirm_key):
                if st.button("🗑️", key=f"sugg_dismiss_{suggestion.id}", help="Ignorer cette suggestion"):
                    st.session_state[confirm_key] = True
                    st.rerun()
            else:
                st.warning("Êtes-vous sûr de vouloir ignorer cette suggestion ?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Oui, ignorer", key=f"confirm_del_sugg_{suggestion.id}", type="primary"):
                        st.session_state.inbox_dismissed.add(suggestion.id)
                        # Nettoyer les états si cette suggestion était active
                        if st.session_state.get("active_suggestion_id") == suggestion.id:
                            del st.session_state["active_suggestion_id"]
                        if st.session_state.get("active_suggestion_result", {}).get("suggestion_id") == suggestion.id:
                            st.session_state.active_suggestion_result = None
                        toast_info("Suggestion ignorée")
                        del st.session_state[confirm_key]
                        st.rerun()
                with col2:
                    if st.button("Annuler", key=f"cancel_del_sugg_{suggestion.id}"):
                        del st.session_state[confirm_key]
                        st.rerun()


def _render_member_mapping_form(suggestion: Suggestion, card_key: str, active_state_key: str = None):
    """Render inline form for mapping a card/account to a member."""
    
    action_data = suggestion.action_data
    card_suffix = action_data.get("card_suffix", "")
    account_label = action_data.get("account_label", "")
    
    # Déterminer ce qu'on mappe (carte ou compte)
    mapping_type = "carte" if card_suffix else "compte"
    mapping_value = card_suffix or account_label
    
    # Récupérer la liste des membres
    members_df = get_members()
    member_options = []
    if not members_df.empty:
        member_options = members_df["name"].tolist()
    
    # Formulaire compact
    st.markdown(f"**Attribuer le {mapping_type} '{mapping_value}' à :**")
    
    # Option pour créer un nouveau membre
    new_member_key = f"{card_key}_new_member"
    show_new_member = st.session_state.get(new_member_key, False)
    
    # Helper pour nettoyer l'état actif
    def clear_active_state():
        if active_state_key and active_state_key in st.session_state:
            del st.session_state[active_state_key]
    
    if show_new_member:
        # Formulaire pour nouveau membre
        new_name = st.text_input("Nom du nouveau membre", key=f"{card_key}_new_name")
        cols = st.columns([1, 1])
        with cols[0]:
            if st.button("✅ Créer & assigner", key=f"{card_key}_create", type="primary", use_container_width=True):
                if new_name and new_name.strip():
                    add_member(new_name.strip())
                    # Assigner le mapping
                    if card_suffix:
                        add_member_mapping(card_suffix, new_name.strip())
                    else:
                        add_account_member_mapping(account_label, new_name.strip())
                    toast_success(f"✅ Membre '{new_name}' créé et assigné !")
                    # Nettoyer les états
                    clear_active_state()
                    if new_member_key in st.session_state:
                        del st.session_state[new_member_key]
                    st.session_state.inbox_dismissed.add(suggestion.id)
                    st.rerun()
                else:
                    toast_error("Veuillez saisir un nom")
        with cols[1]:
            if st.button("❌ Annuler", key=f"{card_key}_cancel_new", use_container_width=True):
                st.session_state[new_member_key] = False
                st.rerun()
    else:
        # Sélecteur de membre existant
        if member_options:
            selected_member = st.selectbox(
                "Choisir un membre existant",
                options=member_options,
                key=f"{card_key}_member"
            )
        else:
            st.info("Aucun membre existant. Créez-en un nouveau.")
            selected_member = None
        
        cols = st.columns([1, 1])
        with cols[0]:
            if st.button("✅ Assigner", key=f"{card_key}_assign", type="primary", use_container_width=True, disabled=not member_options):
                if selected_member:
                    if card_suffix:
                        add_member_mapping(card_suffix, selected_member)
                    else:
                        add_account_member_mapping(account_label, selected_member)
                    toast_success(f"✅ '{mapping_value}' assigné à {selected_member} !")
                    # Nettoyer l'état
                    clear_active_state()
                    st.session_state.inbox_dismissed.add(suggestion.id)
                    st.rerun()
        with cols[1]:
            if st.button("➕ Nouveau membre", key=f"{card_key}_new", use_container_width=True):
                st.session_state[new_member_key] = True
                st.rerun()


def _handle_suggestion_action(suggestion: Suggestion) -> dict:
    """
    Handle suggestion action using the new action handler system.
    
    Returns:
        dict with action result including success, message, and optional view_data
    """
    
    result = execute_suggestion_action(suggestion)
    
    # Show toast feedback
    if result.get("success"):
        message = result.get("message", "✅ Action réalisée")
        toast_success(message)
    else:
        message = result.get("message", "❌ Une erreur est survenue")
        toast_error(message)
    
    return result


def _render_inline_action_result(suggestion_id: str):
    """Render inline view for an action result if available."""
    result = st.session_state.get("active_suggestion_result")
    
    if not result or result.get("suggestion_id") != suggestion_id:
        return False
    
    action_result = result.get("result", {})
    view_data = action_result.get("view_data")
    
    if not view_data:
        return False
    
    # Get the action type from the suggestion
    suggestion = result.get("suggestion")
    if not suggestion:
        return False
    
    action_type = suggestion.action_data.get("type", "")
    
    # Render the inline view
    return render_action_inline_view(action_type, view_data)


def _render_alerts_section(standalone: bool = False):
    """Render alerts (zombies, increases, etc.)."""
    
    confirmed = get_all_feedback(status="confirmed")
    if not confirmed:
        if standalone:
            st.info("🔔 Aucune alerte pour le moment.")
        return
    
    # Utiliser le module d'alertes
    render_alerts_panel()
