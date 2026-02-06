"""
Rule Validator UI Component.

Provides utilities for testing regex patterns against actual transactions
to preview which transactions would match a pattern before creating a rule.
"""

import streamlit as st
import pandas as pd
import re
from typing import Optional

from modules.db.transactions import get_all_transactions
from modules.db.categories import get_categories
from modules.utils import validate_regex_pattern
from modules.logger import logger
from modules.transaction_types import get_color_for_transaction


def test_pattern_against_transactions(
    pattern: str,
    limit: int = 5,
    exclude_validated: bool = False
) -> tuple[list[dict], int]:
    """
    Test a regex pattern against actual transactions.
    
    Args:
        pattern: The regex pattern to test
        limit: Maximum number of matching transactions to return
        exclude_validated: If True, only include transactions without a validated category
        
    Returns:
        Tuple of (matching_transactions, total_matches)
        - matching_transactions: List of transaction dicts (up to limit)
        - total_matches: Total number of matching transactions
        
    Example:
        >>> matches, total = test_pattern_against_transactions("UBER", limit=3)
        >>> print(f"Found {total} matches, showing first 3")
    """
    if not pattern or not pattern.strip():
        return [], 0
    
    # Validate pattern first
    is_valid, _ = validate_regex_pattern(pattern)
    if not is_valid:
        return [], 0
    
    try:
        # Get recent transactions
        tx_df = get_all_transactions(limit=500)
        if tx_df.empty:
            return [], 0
        
        # Compile pattern
        compiled = re.compile(pattern, re.IGNORECASE)
        
        # Filter by pattern
        matches = []
        for _, tx in tx_df.iterrows():
            label = str(tx.get('label', ''))
            
            # Skip if already validated and we're excluding those
            if exclude_validated:
                cat = tx.get('category_validated', '')
                if cat and cat != 'Inconnu':
                    continue
            
            if compiled.search(label):
                matches.append({
                    'id': tx.get('id'),
                    'date': tx.get('date'),
                    'label': label,
                    'amount': tx.get('amount'),
                    'category': tx.get('category_validated', 'Inconnu')
                })
        
        total = len(matches)
        return matches[:limit], total
        
    except Exception as e:
        logger.error(f"Error testing pattern '{pattern}': {e}")
        return [], 0


@st.fragment
def render_pattern_tester():
    """
    Render a pattern tester UI for previewing rule matches.
    
    This is a Streamlit fragment that allows users to test patterns
    against actual transactions before creating rules.
    """
    st.subheader("🧪 Testeur de Pattern")
    st.caption("Testez votre pattern contre les transactions existantes avant de créer la règle.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        test_pattern = st.text_input(
            "Pattern à tester",
            placeholder="Ex: UBER ou ^NETFLIX.*",
            key="pattern_tester_input"
        )
    
    with col2:
        st.markdown("&nbsp;")  # Spacer for alignment
        only_pending = st.checkbox(
            "Non catégorisées uniquement",
            value=True,
            help="N'afficher que les transactions sans catégorie validée"
        )
    
    if not test_pattern:
        st.info("Entrez un pattern pour voir les transactions correspondantes.")
        return
    
    # Validate pattern
    is_valid, error_msg = validate_regex_pattern(test_pattern)
    if not is_valid:
        st.error(f"❌ Pattern invalide: {error_msg}")
        return
    
    # Test pattern
    with st.spinner("Analyse des transactions..."):
        matches, total = test_pattern_against_transactions(
            test_pattern,
            limit=5,
            exclude_validated=only_pending
        )
    
    # Display results
    if total == 0:
        st.warning(f"🔍 Aucune transaction ne correspond au pattern '{test_pattern}'")
        if only_pending:
            st.caption("💡 Essayez de décocher 'Non catégorisées uniquement' pour voir toutes les transactions.")
    else:
        st.success(f"✅ {total} transaction(s) trouvée(s) avec le pattern '{test_pattern}'")
        
        # Show sample matches
        if matches:
            st.caption(f"Exemples ({len(matches)} affichée(s) sur {total}) :")
            
            for match in matches:
                cols = st.columns([2, 3, 1, 1])
                with cols[0]:
                    date_str = match['date']
                    if isinstance(date_str, str) and len(date_str) >= 10:
                        st.markdown(f"`{date_str[:10]}`")
                    else:
                        st.markdown(f"`{date_str}`")
                with cols[1]:
                    st.markdown(f"{match['label'][:40]}..." if len(match['label']) > 40 else match['label'])
                with cols[2]:
                    amount = match['amount']
                    category = match['category']
                    color = get_color_for_transaction(category)
                    st.markdown(f":{color}[{amount:,.2f} €]")
                with cols[3]:
                    cat = match['category']
                    if cat and cat != 'Inconnu':
                        st.caption(f"🏷️ {cat}")
                    else:
                        st.caption("❓ Non catégorisé")
