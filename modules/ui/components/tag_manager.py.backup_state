"""
Tag Manager Component with Smart Propagation
Features:
- Beautiful pill-style tags with colors
- Smart propagation to similar transactions
- Batch tagging operations
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Tuple
from modules.db.tags import get_all_tags
from modules.db.categories import get_categories_suggested_tags, add_tag_to_category
from modules.db.transactions import get_all_transactions
from modules.categorization import clean_label


# Tag color scheme for visual distinction
TAG_COLORS = {
    'default': {'bg': '#e9ecef', 'text': '#495057', 'border': '#dee2e6'},
    'salaire': {'bg': '#d4edda', 'text': '#155724', 'border': '#c3e6cb'},
    'remboursement': {'bg': '#cce5ff', 'text': '#004085', 'border': '#b8daff'},
    'urgent': {'bg': '#f8d7da', 'text': '#721c24', 'border': '#f5c6cb'},
    'courses': {'bg': '#fff3cd', 'text': '#856404', 'border': '#ffeeba'},
    'voiture': {'bg': '#d1ecf1', 'text': '#0c5460', 'border': '#bee5eb'},
    'sante': {'bg': '#d8e8d8', 'text': '#2d5a2d', 'border': '#c9dcc9'},
    'loisirs': {'bg': '#f3e5f5', 'text': '#4a148c', 'border': '#e1bee7'},
    'cheque': {'bg': '#fce4ec', 'text': '#880e4f', 'border': '#f8bbd9'},
}


def get_tag_color(tag: str) -> Dict[str, str]:
    """Get color scheme for a tag based on its content."""
    tag_lower = tag.lower()
    
    # Check for keywords in tag
    for keyword, colors in TAG_COLORS.items():
        if keyword in tag_lower:
            return colors
    
    # Default colors with hash-based variation for visual distinction
    import hashlib
    hash_val = int(hashlib.md5(tag.encode()).hexdigest(), 16)
    
    # Predefined soft colors
    soft_colors = [
        {'bg': '#e3f2fd', 'text': '#1565c0', 'border': '#bbdefb'},
        {'bg': '#f3e5f5', 'text': '#7b1fa2', 'border': '#e1bee7'},
        {'bg': '#e8f5e9', 'text': '#2e7d32', 'border': '#c8e6c9'},
        {'bg': '#fff3e0', 'text': '#ef6c00', 'border': '#ffe0b2'},
        {'bg': '#fce4ec', 'text': '#c2185b', 'border': '#f8bbd9'},
        {'bg': '#e0f2f1', 'text': '#00897b', 'border': '#b2dfdb'},
        {'bg': '#ede7f6', 'text': '#5e35b1', 'border': '#d1c4e9'},
    ]
    
    return soft_colors[hash_val % len(soft_colors)]


def render_pill_tags(tags: List[str], size: str = "normal", removable: bool = False, 
                     on_remove=None, key_prefix: str = "") -> str:
    """
    Render tags as beautiful pills with optional remove buttons.
    
    Args:
        tags: List of tag strings
        size: 'small', 'normal', or 'large'
        removable: Whether to show remove buttons
        on_remove: Callback function when a tag is removed
        key_prefix: Prefix for unique keys
        
    Returns:
        CSS styles injected (for container styling)
    """
    if not tags:
        return ""
    
    # Size configurations
    sizes = {
        'small': {'padding': '2px 8px', 'font': '11px', 'radius': '10px', 'margin': '1px'},
        'normal': {'padding': '4px 12px', 'font': '13px', 'radius': '14px', 'margin': '2px'},
        'large': {'padding': '6px 16px', 'font': '14px', 'radius': '16px', 'margin': '3px'}
    }
    
    size_config = sizes.get(size, sizes['normal'])
    
    # Generate CSS for pills
    pills_html = []
    
    for i, tag in enumerate(tags):
        if not tag:
            continue
            
        colors = get_tag_color(tag)
        tag_key = f"{key_prefix}_remove_tag_{i}"
        
        # Create pill HTML
        pill_style = f"""
            display: inline-flex;
            align-items: center;
            padding: {size_config['padding']};
            margin: {size_config['margin']};
            background-color: {colors['bg']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: {size_config['radius']};
            font-size: {size_config['font']};
            font-weight: 500;
            white-space: nowrap;
            line-height: 1.4;
        """
        
        if removable:
            # Add remove button
            if st.button(f"✕", key=tag_key, type="tertiary"):
                if on_remove:
                    on_remove(tag)
                st.rerun()
        
        pills_html.append(f'<span style="{pill_style}">{tag}</span>')
    
    # Render container
    container_style = """
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        align-items: center;
    """
    
    pills_container = f'<div style="{container_style}">{"".join(pills_html)}</div>'
    st.markdown(pills_container, unsafe_allow_html=True)
    
    return container_style


def find_similar_transactions(transaction_id: int, df: pd.DataFrame = None, 
                               similarity_threshold: float = 0.8) -> pd.DataFrame:
    """
    Find transactions similar to the given one based on label and amount.
    
    Args:
        transaction_id: The reference transaction ID
        df: DataFrame of transactions (fetched if None)
        similarity_threshold: Minimum similarity score (0-1)
        
    Returns:
        DataFrame of similar transactions (excluding the reference)
    """
    if df is None:
        df = get_all_transactions()
    
    # Get reference transaction
    ref_tx = df[df['id'] == transaction_id]
    if ref_tx.empty:
        return pd.DataFrame()
    
    ref = ref_tx.iloc[0]
    ref_label = str(ref.get('label', ''))
    ref_clean = clean_label(ref_label)
    ref_amount = float(ref.get('amount', 0))
    ref_cat = ref.get('category_validated', '')
    
    # Calculate similarity scores
    similarities = []
    
    for _, tx in df.iterrows():
        if tx['id'] == transaction_id:
            continue
        
        tx_label = str(tx.get('label', ''))
        tx_clean = clean_label(tx_label)
        tx_amount = float(tx.get('amount', 0))
        tx_cat = tx.get('category_validated', '')
        
        # Calculate label similarity
        label_sim = _calculate_label_similarity(ref_clean, tx_clean)
        
        # Amount similarity (within 20% tolerance)
        amount_sim = 1.0 if abs(tx_amount - ref_amount) / max(abs(ref_amount), 1) < 0.2 else 0.0
        
        # Category bonus
        cat_sim = 0.3 if ref_cat and tx_cat == ref_cat else 0.0
        
        # Combined score
        total_sim = (label_sim * 0.6) + (amount_sim * 0.3) + cat_sim
        
        if total_sim >= similarity_threshold:
            similarities.append({
                'id': tx['id'],
                'label': tx_label,
                'date': tx.get('date'),
                'amount': tx_amount,
                'category': tx_cat,
                'similarity': total_sim,
                'tags': tx.get('tags', '')
            })
    
    if not similarities:
        return pd.DataFrame()
    
    result_df = pd.DataFrame(similarities)
    return result_df.sort_values('similarity', ascending=False)


def _calculate_label_similarity(label1: str, label2: str) -> float:
    """Calculate similarity between two cleaned labels."""
    # Exact match
    if label1 == label2:
        return 1.0
    
    # One contains the other
    if label1 in label2 or label2 in label1:
        return 0.9
    
    # Word overlap
    words1 = set(label1.upper().split())
    words2 = set(label2.upper().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    jaccard = len(intersection) / len(union) if union else 0
    
    return jaccard


def render_smart_tag_selector(
    transaction_id: int,
    current_tags: List[str],
    category: str,
    label: str = "",
    key_suffix: str = "",
    max_quick_tags: int = 3,
    enable_propagation: bool = True,
    df_context: pd.DataFrame = None
) -> List[str]:
    """
    Render a smart tag selector with pill display and propagation suggestions.
    
    Args:
        transaction_id: Transaction ID
        current_tags: Currently selected tags
        category: Category name
        label: Transaction label (for similarity matching)
        key_suffix: Key suffix
        max_quick_tags: Number of quick tag buttons
        enable_propagation: Whether to show propagation suggestions
        df_context: DataFrame context for finding similar transactions
        
    Returns:
        List of selected tags
    """
    # Initialize session state
    if 'temp_custom_tags' not in st.session_state:
        st.session_state['temp_custom_tags'] = []
    
    if 'pending_tag_additions' not in st.session_state:
        st.session_state['pending_tag_additions'] = {}
    
    # Apply pending additions
    if transaction_id in st.session_state.get('pending_tag_additions', {}):
        pending = st.session_state['pending_tag_additions'][transaction_id]
        current_tags = list(set(current_tags + pending))
        del st.session_state['pending_tag_additions'][transaction_id]
    
    # Get available tags
    existing_tags = get_all_tags()
    cat_suggested_tags = get_categories_suggested_tags()
    suggested = cat_suggested_tags.get(category, [])
    
    # Build options
    all_available = sorted(list(set(
        existing_tags + suggested + st.session_state['temp_custom_tags'] + current_tags
    )))
    
    quick_tags = [t for t in suggested if t not in current_tags][:max_quick_tags]
    
    container = st.container()
    
    with container:
        # Display current tags as pills
        if current_tags:
            st.caption("Tags actuels :")
            render_pill_tags(current_tags, size="normal", removable=False)
        
        # Tag selector
        selector_col, add_col = st.columns([0.85, 0.15])
        
        with selector_col:
            selected = st.multiselect(
                "Tags",
                options=all_available,
                default=current_tags,
                key=f"tag_select_smart_{transaction_id}{key_suffix}",
                label_visibility="collapsed",
                placeholder="🏷️ Ajouter des tags..."
            )
        
        with add_col:
            with st.popover("➕", use_container_width=True):
                st.markdown("**Nouveau tag**")
                new_tag = st.text_input(
                    "Nom du tag",
                    key=f"new_tag_smart_{transaction_id}{key_suffix}",
                    label_visibility="collapsed",
                    placeholder="ex: Vacances"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✓ Ajouter", type="primary", use_container_width=True,
                               key=f"add_tag_smart_{transaction_id}{key_suffix}"):
                        if new_tag and new_tag.strip():
                            new_tag_clean = new_tag.strip()
                            if new_tag_clean not in st.session_state['temp_custom_tags']:
                                st.session_state['temp_custom_tags'].append(new_tag_clean)
                            add_tag_to_category(category, new_tag_clean)
                            if transaction_id not in st.session_state['pending_tag_additions']:
                                st.session_state['pending_tag_additions'][transaction_id] = []
                            st.session_state['pending_tag_additions'][transaction_id].append(new_tag_clean)
                            st.rerun()
        
        # Quick add buttons
        if quick_tags:
            st.caption("Suggestions rapides :")
            quick_cols = st.columns(min(len(quick_tags), 4))
            for i, tag in enumerate(quick_tags[:4]):
                with quick_cols[i]:
                    if st.button(
                        f"+{tag[:10]}",
                        key=f"quick_smart_{tag}_{transaction_id}{key_suffix}",
                        use_container_width=True,
                        type="secondary"
                    ):
                        if transaction_id not in st.session_state['pending_tag_additions']:
                            st.session_state['pending_tag_additions'][transaction_id] = []
                        st.session_state['pending_tag_additions'][transaction_id].append(tag)
                        st.rerun()
        
        # Smart Propagation Section
        if enable_propagation and selected:
            # Check for newly added tags (not in current_tags initially)
            new_tags = [t for t in selected if t not in current_tags]
            
            if new_tags:
                st.markdown("---")
                st.markdown("🤖 **Propagation intelligente**")
                
                # Find similar transactions
                similar_df = find_similar_transactions(transaction_id, df=df_context)
                
                if not similar_df.empty:
                    st.markdown(f"*{len(similar_df)} transactions similaires trouvées*")
                    
                    # Show similar transactions that don't have these tags
                    missing_tags_tx = []
                    for _, tx in similar_df.iterrows():
                        tx_tags = [t.strip() for t in str(tx.get('tags', '')).split(',') if t.strip()]
                        missing = [t for t in new_tags if t not in tx_tags]
                        if missing:
                            missing_tags_tx.append({
                                'id': tx['id'],
                                'label': tx['label'][:40] + "..." if len(tx['label']) > 40 else tx['label'],
                                'date': tx['date'],
                                'amount': tx['amount'],
                                'missing_tags': missing,
                                'similarity': tx['similarity']
                            })
                    
                    if missing_tags_tx:
                        st.caption("Transactions qui n'ont pas encore ces tags :")
                        
                        for tx_info in missing_tags_tx[:5]:  # Show top 5
                            tx_col1, tx_col2, tx_col3 = st.columns([3, 1, 1])
                            
                            with tx_col1:
                                st.text(f"{tx_info['label']}")
                            with tx_col2:
                                st.text(f"{tx_info['amount']:.2f}€")
                            with tx_col3:
                                # Propagate button
                                prop_key = f"prop_{tx_info['id']}_{'_'.join(new_tags)}"
                                if st.button("🏷️ Taguer", key=prop_key, use_container_width=True):
                                    # Add tags to this transaction
                                    if tx_info['id'] not in st.session_state.get('pending_tag_additions', {}):
                                        st.session_state['pending_tag_additions'][tx_info['id']] = []
                                    st.session_state['pending_tag_additions'][tx_info['id']].extend(new_tags)
                                    st.toast(f"✅ Tags ajoutés à la transaction !", icon="🏷️")
                        
                        # Batch propagate button
                        if len(missing_tags_tx) > 1:
                            if st.button(f"🏷️ Taguer toutes les {len(missing_tags_tx)} transactions", 
                                       type="primary", use_container_width=True):
                                for tx_info in missing_tags_tx:
                                    if tx_info['id'] not in st.session_state.get('pending_tag_additions', {}):
                                        st.session_state['pending_tag_additions'][tx_info['id']] = []
                                    st.session_state['pending_tag_additions'][tx_info['id']].extend(new_tags)
                                st.toast(f"✅ Tags propagés à {len(missing_tags_tx)} transactions !", icon="🚀")
                                st.rerun()
                    else:
                        st.success("✅ Toutes les transactions similaires ont déjà ces tags !")
                else:
                    st.info("Aucune transaction similaire trouvée pour propagation.")
    
    return selected


def batch_apply_tags_to_similar(transaction_ids: List[int], tags: List[str]) -> Dict[int, bool]:
    """
    Apply tags to multiple transactions and their similar counterparts.
    
    Args:
        transaction_ids: List of transaction IDs
        tags: Tags to apply
        
    Returns:
        Dict mapping transaction ID to success status
    """
    results = {}
    df = get_all_transactions()
    
    for tx_id in transaction_ids:
        # Find similar transactions
        similar = find_similar_transactions(tx_id, df)
        
        # Apply tags to all similar transactions
        target_ids = [tx_id] + similar['id'].tolist() if not similar.empty else [tx_id]
        
        for target_id in target_ids:
            if target_id not in st.session_state.get('pending_tag_additions', {}):
                st.session_state['pending_tag_additions'][target_id] = []
            st.session_state['pending_tag_additions'][target_id].extend(tags)
            results[target_id] = True
    
    return results
