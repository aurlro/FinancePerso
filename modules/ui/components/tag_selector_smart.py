"""
Smart Tag Selector with Propagation
Intelligent tag management with suggestions for similar transactions.

Features:
- Detects when tags are added to a transaction
- Finds similar transactions (same label/category pattern)
- Suggests propagating the tag to similar transactions
- Bulk apply tags across multiple transactions
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from difflib import SequenceMatcher

from modules.db.tags import get_all_tags
from modules.db.categories import get_categories_suggested_tags, add_tag_to_category
from modules.db.transactions import get_transaction_by_id, get_transactions, update_transaction_tags


def similarity(a: str, b: str) -> float:
    """Calculate string similarity ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_similar_transactions(
    transaction_id: int,
    label: str,
    category: str,
    df_context: pd.DataFrame = None,
    threshold: float = 0.75
) -> List[Dict[str, Any]]:
    """
    Find transactions similar to the given one.
    
    Similarity is based on:
    1. Label similarity (fuzzy matching)
    2. Same category
    3. Similar amount patterns
    
    Returns list of similar transactions excluding the source.
    """
    # Get the source transaction details
    source = get_transaction_by_id(transaction_id)
    if not source:
        return []
    
    source_label = source.get('label', '') or source.get('description', '')
    source_category = source.get('category', '')
    
    # Use provided context or fetch all transactions
    if df_context is not None and not df_context.empty:
        df = df_context.copy()
    else:
        df = get_transactions(limit=5000)
        if df.empty:
            return []
    
    similar = []
    
    for _, row in df.iterrows():
        other_id = row.get('id')
        if other_id == transaction_id:
            continue
        
        other_label = row.get('label', '') or row.get('description', '')
        other_category = row.get('category', '')
        
        # Skip if categories don't match
        if other_category != source_category:
            continue
        
        # Calculate label similarity
        if not other_label or not source_label:
            continue
            
        label_sim = similarity(str(source_label), str(other_label))
        
        if label_sim >= threshold:
            similar.append({
                'id': other_id,
                'label': other_label,
                'amount': row.get('amount', 0),
                'date': row.get('date', ''),
                'similarity': label_sim
            })
    
    # Sort by similarity
    similar.sort(key=lambda x: x['similarity'], reverse=True)
    return similar[:20]  # Limit to top 20


def apply_tag_to_similar(
    tag: str,
    similar_transactions: List[Dict[str, Any]],
    exclude_ids: List[int] = None
) -> int:
    """
    Apply a tag to all similar transactions.
    
    Returns number of transactions updated.
    """
    if exclude_ids is None:
        exclude_ids = []
    
    count = 0
    for trans in similar_transactions:
        trans_id = trans['id']
        if trans_id in exclude_ids:
            continue
        
        # Get current tags
        trans_data = get_transaction_by_id(trans_id)
        if not trans_data:
            continue
        
        current_tags = trans_data.get('tags', '')
        if isinstance(current_tags, str):
            current_tags = [t.strip() for t in current_tags.split(',') if t.strip()]
        elif not isinstance(current_tags, list):
            current_tags = []
        
        # Add new tag if not present
        if tag not in current_tags:
            new_tags = current_tags + [tag]
            update_transaction_tags(trans_id, new_tags)
            count += 1
    
    return count


def render_tag_propagation_dialog(
    tag: str,
    source_transaction_id: int,
    similar_transactions: List[Dict[str, Any]],
    key_suffix: str = ""
) -> bool:
    """
    Render a dialog offering to propagate the tag to similar transactions.
    
    Returns True if the user chose to propagate.
    """
    if not similar_transactions:
        return False
    
    count = len(similar_transactions)
    
    # Create expandable section for propagation
    with st.expander(f"🔄 Propager à {count} transaction{'s' if count > 1 else ''} similaire", expanded=True):
        st.info(f"Le tag **#{tag}** peut être appliqué à {count} transaction(s) similaire(s).")
        
        # Show preview of similar transactions
        st.caption("Transactions similaires détectées :")
        preview_data = []
        for t in similar_transactions[:5]:  # Show first 5
            preview_data.append({
                "Date": t['date'][:10] if t['date'] else "-",
                "Libellé": t['label'][:30] + "..." if len(str(t['label'])) > 30 else t['label'],
                "Montant": f"{t['amount']:.2f} €"
            })
        
        st.dataframe(pd.DataFrame(preview_data), use_container_width=True, hide_index=True)
        
        if count > 5:
            st.caption(f"... et {count - 5} autres")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Appliquer à toutes", type="primary", use_container_width=True,
                        key=f"propagate_all_{tag}_{source_transaction_id}{key_suffix}"):
                applied = apply_tag_to_similar(tag, similar_transactions, [source_transaction_id])
                st.success(f"✅ Tag appliqué à {applied} transaction(s)")
                return True
        
        with col2:
            if st.button("❌ Ignorer", use_container_width=True,
                        key=f"ignore_propagate_{tag}_{source_transaction_id}{key_suffix}"):
                return False
    
    return False


def render_smart_tag_selector(
    transaction_id: int,
    current_tags: List[str],
    category: str,
    key_suffix: str = "",
    df_context: pd.DataFrame = None,
    max_quick_tags: int = 3,
    enable_propagation: bool = True
) -> List[str]:
    """
    Render a smart tag selector with propagation suggestions.
    
    Args:
        transaction_id: Transaction ID for unique keys
        current_tags: List of currently selected tags
        category: Category name for context-aware suggestions
        key_suffix: Optional suffix for multiple instances
        df_context: DataFrame with transaction context for similarity detection
        max_quick_tags: Number of quick-tag buttons to show
        enable_propagation: Whether to enable tag propagation suggestions
    
    Returns:
        List of selected tag names
    """
    # Initialize session state
    if 'temp_custom_tags' not in st.session_state:
        st.session_state['temp_custom_tags'] = []
    
    if 'pending_tag_additions' not in st.session_state:
        st.session_state['pending_tag_additions'] = {}
    
    if 'propagation_shown' not in st.session_state:
        st.session_state['propagation_shown'] = set()
    
    # Track tags before modification
    prev_tags_key = f"prev_tags_{transaction_id}{key_suffix}"
    if prev_tags_key not in st.session_state:
        st.session_state[prev_tags_key] = list(current_tags)
    
    prev_tags = st.session_state[prev_tags_key]
    
    # Apply pending additions
    if transaction_id in st.session_state.get('pending_tag_additions', {}):
        pending = st.session_state['pending_tag_additions'][transaction_id]
        current_tags = list(set(current_tags + pending))
        del st.session_state['pending_tag_additions'][transaction_id]
    
    # Get available tags
    existing_tags = get_all_tags()
    cat_suggested_tags = get_categories_suggested_tags()
    suggested = cat_suggested_tags.get(category, [])
    
    # Build options list
    all_available = sorted(list(set(
        existing_tags + 
        suggested + 
        st.session_state['temp_custom_tags'] +
        current_tags
    )))
    
    # Determine quick tags
    quick_tags = [t for t in suggested if t not in current_tags][:max_quick_tags]
    
    container = st.container()
    
    with container:
        # Detect newly added tags
        new_tags = [t for t in current_tags if t not in prev_tags]
        
        # Show propagation dialog for newly added tags
        if enable_propagation and new_tags and df_context is not None:
            for new_tag in new_tags:
                propagation_key = f"{transaction_id}_{new_tag}_{key_suffix}"
                if propagation_key not in st.session_state['propagation_shown']:
                    # Find similar transactions
                    similar = find_similar_transactions(
                        transaction_id,
                        "",  # Label will be fetched internally
                        category,
                        df_context
                    )
                    
                    if similar:
                        render_tag_propagation_dialog(
                            new_tag,
                            transaction_id,
                            similar,
                            key_suffix
                        )
                        st.session_state['propagation_shown'].add(propagation_key)
        
        # ROW 1: Main selector with add button inline
        selector_col, add_col = st.columns([0.88, 0.12])
        
        with selector_col:
            selected = st.multiselect(
                "Tags",
                options=all_available,
                default=current_tags,
                key=f"smart_tag_select_{transaction_id}{key_suffix}",
                label_visibility="collapsed",
                placeholder="🏷️ Ajouter des tags..."
            )
        
        with add_col:
            with st.popover("➕", use_container_width=True):
                st.markdown("**Nouveau tag**")
                new_tag = st.text_input(
                    "Nom",
                    key=f"smart_new_tag_input_{transaction_id}{key_suffix}",
                    label_visibility="collapsed",
                    placeholder="ex: Urgent"
                )
                
                if st.button("Créer", type="primary", use_container_width=True,
                           key=f"smart_create_tag_{transaction_id}{key_suffix}"):
                    if new_tag and new_tag.strip():
                        new_tag_clean = new_tag.strip()
                        if new_tag_clean not in st.session_state['temp_custom_tags']:
                            st.session_state['temp_custom_tags'].append(new_tag_clean)
                        add_tag_to_category(category, new_tag_clean)
                        if transaction_id not in st.session_state['pending_tag_additions']:
                            st.session_state['pending_tag_additions'][transaction_id] = []
                        st.session_state['pending_tag_additions'][transaction_id].append(new_tag_clean)
                        st.rerun()
        
        # ROW 2: Quick add buttons
        if quick_tags:
            quick_cols = st.columns(min(len(quick_tags), 3))
            for i, tag in enumerate(quick_tags[:3]):
                with quick_cols[i]:
                    if st.button(
                        f"+{tag[:8]}",
                        key=f"smart_quick_tag_{tag}_{transaction_id}{key_suffix}",
                        use_container_width=True,
                        type="secondary",
                        help=f"Ajouter '{tag}'"
                    ):
                        if transaction_id not in st.session_state['pending_tag_additions']:
                            st.session_state['pending_tag_additions'][transaction_id] = []
                        st.session_state['pending_tag_additions'][transaction_id].append(tag)
                        st.rerun()
    
    # Update stored tags for next comparison
    st.session_state[prev_tags_key] = list(selected)
    
    return selected
