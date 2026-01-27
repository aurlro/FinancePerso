"""
Member Selector Component
Standardized member/beneficiary selection with type indicators.

Handles:
- HOUSEHOLD vs EXTERNAL member type display
- Custom input option ("✍️ Saisie...")
- Icon prefixes for visual identification
"""
import streamlit as st
from modules.constants import MemberType


def render_member_selector(
    label: str,
    current_value: str,
    all_members: list[str],
    member_type_map: dict[str, str],
    key: str,
    allow_custom: bool = True,
    extra_options: list[str] = None
) -> str:
    """
    Render member/beneficiary selector with type icons.
    
    Args:
        label: Display label for selectbox
        current_value: Currently selected member name
        all_members: List of all member names
        member_type_map: Dict mapping member name to type (HOUSEHOLD/EXTERNAL)
        key: Unique widget key
        allow_custom: Whether to allow custom text input
        extra_options: Additional options like "Maison", "Famille"
        
    Returns:
        Selected member name (empty string if not selected)
        
    Example:
        >>> selected = render_member_selector(
        ...     label="👤 Payeur",
        ...     current_value="Aurélien",
        ...     all_members=["Aurélien", "Élise"],
        ...     member_type_map={"Aurélien": "HOUSEHOLD", "Élise": "HOUSEHOLD"},
        ...     key="member_123"
        ... )
    """
    # Build options list
    if extra_options is None:
        extra_options = ["Maison", "Famille"]
    
    options = sorted(list(set(all_members + extra_options)))
    
    # Add current value if not in options
    if current_value and current_value not in options:
        options.append(current_value)
    
    # Add custom input option
    if allow_custom:
        options.append("✍️ Saisie...")
    
    # Determine index
    try:
        idx = options.index(current_value) if current_value in options else 0
    except (ValueError, IndexError):
        idx = 0
    
    # Format function for display
    def format_member(name: str) -> str:
        if name == "✍️ Saisie...":
            return "✍️ Saisie..."
        if not name:
            return ""
        
        # Determine icon based on member type
        m_type = member_type_map.get(name, MemberType.HOUSEHOLD)
        if m_type == MemberType.EXTERNAL:
            prefix = "💼"
        elif name in ["Maison", "Famille"]:
            prefix = "🏘️"
        else:
            prefix = "🏘️" if m_type == MemberType.HOUSEHOLD else "💼"
        
        return f"{prefix} {name}"
    
    # Render selectbox
    selected = st.selectbox(
        label,
        options,
        index=idx,
        key=key,
        format_func=format_member
    )
    
    # If custom input selected, show text input
    if selected == "✍️ Saisie..." and allow_custom:
        custom_key = f"{key}_input"
        custom_value = st.text_input(
            "Nom",
            key=custom_key,
            label_visibility="collapsed"
        )
        return custom_value
    
    return selected if selected else ""


def render_member_selector_pair(
    payer_label: str,
    beneficiary_label: str,
    current_payer: str,
    current_beneficiary: str,
    all_members: list[str],
    member_type_map: dict[str, str],
    key_prefix: str,
    is_income: bool = False
) -> tuple[str, str]:
    """
    Render paired member selectors for payer and beneficiary.
    
    Automatically adjusts labels based on transaction type (income vs expense).
    
    Args:
        payer_label: Label for payer selector
        beneficiary_label: Label for beneficiary selector
        current_payer: Current payer value
        current_beneficiary: Current beneficiary value
        all_members: List of all members
        member_type_map: Member type mapping
        key_prefix: Prefix for widget keys
        is_income: If True, swap labels (beneficiary = source)
        
    Returns:
        Tuple of (selected_payer, selected_beneficiary)
    """
    col1, col2 = st.columns(2)
    
    if is_income:
        # For income: beneficiary receives, source pays
        payer_label = "💰 Source"
        beneficiary_label = "👤 Bénéficiaire"
    else:
        # For expense: payer pays, beneficiary receives
        payer_label = "👤 Payeur"
        beneficiary_label = "🎯 Pour qui ?"
    
    with col1:
        payer = render_member_selector(
            label=payer_label,
            current_value=current_payer,
            all_members=all_members,
            member_type_map=member_type_map,
            key=f"{key_prefix}_payer"
        )
    
    with col2:
        beneficiary = render_member_selector(
            label=beneficiary_label,
            current_value=current_beneficiary,
            all_members=all_members,
            member_type_map=member_type_map,
            key=f"{key_prefix}_beneficiary"
        )
    
    return payer, beneficiary
