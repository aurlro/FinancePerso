"""
Impact Analyzer - Preview the impact of configuration changes.
Shows how many transactions will be affected by a change before applying it.
"""
import streamlit as st
import pandas as pd
from modules.db.transactions import get_all_transactions
from modules.db.rules import get_learning_rules
from modules.db.categories import get_categories
from modules.logger import logger


def analyze_category_merge_impact(source_category: str, target_category: str) -> dict:
    """
    Analyze the impact of merging two categories.
    
    Returns:
        dict with:
        - transaction_count: number of transactions to move
        - amount_total: total amount of affected transactions
        - date_range: (min_date, max_date) of affected transactions
        - rules_affected: list of rules using the source category
        - sample_transactions: preview of affected transactions
    """
    df = get_all_transactions()
    
    if df.empty:
        return {
            'transaction_count': 0,
            'amount_total': 0,
            'date_range': (None, None),
            'rules_affected': [],
            'sample_transactions': pd.DataFrame()
        }
    
    # Find transactions with source category
    affected = df[df['category_validated'] == source_category]
    
    # Get rules that use this category
    rules_df = get_learning_rules()
    rules_affected = []
    if not rules_df.empty:
        rules_affected = rules_df[rules_df['category'] == source_category]['pattern'].tolist()
    
    return {
        'transaction_count': len(affected),
        'amount_total': affected['amount'].sum() if not affected.empty else 0,
        'date_range': (affected['date'].min(), affected['date'].max()) if not affected.empty else (None, None),
        'rules_affected': rules_affected,
        'sample_transactions': affected.head(5) if not affected.empty else pd.DataFrame()
    }


def analyze_rule_creation_impact(pattern: str, category: str) -> dict:
    """
    Analyze the impact of creating a new learning rule.
    
    Returns:
        dict with:
        - matched_transactions: number of pending transactions that would match
        - sample_matches: preview of transactions that would be affected
        - estimated_time_saved: estimated seconds saved per month
    """
    from modules.categorization import apply_rules
    import re
    
    df = get_all_transactions()
    
    if df.empty:
        return {
            'matched_transactions': 0,
            'sample_matches': pd.DataFrame(),
            'estimated_time_saved': 0
        }
    
    # Get pending transactions
    pending = df[df['status'] == 'pending']
    
    if pending.empty:
        return {
            'matched_transactions': 0,
            'sample_matches': pd.DataFrame(),
            'estimated_time_saved': 0
        }
    
    # Compile pattern and test matches
    try:
        regex = re.compile(pattern, re.IGNORECASE)
        matches = pending[pending['label'].str.contains(regex, na=False, regex=True)]
    except re.error:
        return {
            'matched_transactions': 0,
            'sample_matches': pd.DataFrame(),
            'estimated_time_saved': 0,
            'error': 'Pattern regex invalide'
        }
    
    # Estimate time saved (assume 5 seconds per validation)
    estimated_time = len(matches) * 5
    
    return {
        'matched_transactions': len(matches),
        'sample_matches': matches.head(5),
        'estimated_time_saved': estimated_time,
        'monthly_occurrences': len(matches)  # Approximation for monthly
    }


def analyze_member_rename_impact(old_name: str, new_name: str) -> dict:
    """
    Analyze the impact of renaming a member.
    
    Returns:
        dict with:
        - transactions_as_member: count where member=old_name
        - transactions_as_beneficiary: count where beneficiary=old_name
        - total_affected: total transactions to update
        - card_mappings: list of card mappings to update
    """
    df = get_all_transactions()
    
    if df.empty:
        return {
            'transactions_as_member': 0,
            'transactions_as_beneficiary': 0,
            'total_affected': 0,
            'card_mappings': []
        }
    
    as_member = df[df['member'] == old_name]
    as_beneficiary = df[df['beneficiary'] == old_name]
    
    # Check card mappings
    from modules.db.members import get_member_mappings_df
    mappings = get_member_mappings_df()
    card_mappings = []
    if not mappings.empty:
        card_mappings = mappings[mappings['member_name'] == old_name]['card_suffix'].tolist()
    
    return {
        'transactions_as_member': len(as_member),
        'transactions_as_beneficiary': len(as_beneficiary),
        'total_affected': len(as_member) + len(as_beneficiary),
        'card_mappings': card_mappings
    }


def analyze_budget_creation_impact(category: str, amount: float) -> dict:
    """
    Analyze the impact of creating a new budget.
    
    Returns:
        dict with:
        - current_month_spending: amount spent this month
        - percentage_used: percentage of new budget already used
        - projected_overrun: whether this will trigger alerts
        - similar_categories: categories with similar spending patterns
    """
    import datetime
    
    df = get_all_transactions()
    
    if df.empty:
        return {
            'current_month_spending': 0,
            'percentage_used': 0,
            'projected_overrun': False,
            'status': 'OK'
        }
    
    # Get current month spending for this category
    current_month = datetime.datetime.now().strftime('%Y-%m')
    df['date_dt'] = pd.to_datetime(df['date'])
    month_df = df[df['date_dt'].dt.strftime('%Y-%m') == current_month]
    
    spending = month_df[
        (month_df['category_validated'] == category) & 
        (month_df['amount'] < 0)
    ]['amount'].sum()
    
    spending = abs(spending)
    percentage = (spending / amount * 100) if amount > 0 else 0
    
    status = 'OK'
    if percentage >= 100:
        status = 'OVERBUDGET'
    elif percentage >= 75:
        status = 'WARNING'
    
    return {
        'current_month_spending': spending,
        'percentage_used': percentage,
        'projected_overrun': percentage >= 100,
        'status': status
    }


def analyze_tag_removal_impact(tag: str) -> dict:
    """
    Analyze the impact of removing a tag.
    
    Returns:
        dict with:
        - transaction_count: number of transactions with this tag
        - category_breakdown: dict of categories using this tag
    """
    df = get_all_transactions()
    
    if df.empty or 'tags' not in df.columns:
        return {
            'transaction_count': 0,
            'category_breakdown': {}
        }
    
    # Find transactions with this tag
    has_tag = df['tags'].str.contains(tag, na=False)
    affected = df[has_tag]
    
    # Breakdown by category
    if not affected.empty:
        breakdown = affected.groupby('category_validated').size().to_dict()
    else:
        breakdown = {}
    
    return {
        'transaction_count': len(affected),
        'category_breakdown': breakdown
    }


def render_impact_preview(impact_type: str, impact_data: dict):
    """
    Render a standardized impact preview component.
    
    Args:
        impact_type: 'category_merge', 'rule_creation', 'member_rename', etc.
        impact_data: dict returned by analyze_* functions
    """
    if impact_type == 'category_merge':
        _render_category_merge_impact(impact_data)
    elif impact_type == 'rule_creation':
        _render_rule_creation_impact(impact_data)
    elif impact_type == 'member_rename':
        _render_member_rename_impact(impact_data)
    elif impact_type == 'budget_creation':
        _render_budget_creation_impact(impact_data)
    elif impact_type == 'tag_removal':
        _render_tag_removal_impact(impact_data)


def _render_category_merge_impact(data: dict):
    """Render impact preview for category merge."""
    with st.container(border=True):
        st.markdown("### 📊 Impact de la fusion")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Transactions concernées", data['transaction_count'])
        with col2:
            st.metric("Montant total", f"{data['amount_total']:,.2f}€")
        with col3:
            if data['date_range'][0]:
                st.metric("Période", f"{data['date_range'][0]} → {data['date_range'][1]}")
        
        if data['rules_affected']:
            st.warning(f"⚠️ **{len(data['rules_affected'])}** règle(s) d'apprentissage seront également modifiées:")
            for pattern in data['rules_affected'][:5]:
                st.write(f"  • `{pattern}`")
            if len(data['rules_affected']) > 5:
                st.caption(f"... et {len(data['rules_affected']) - 5} autres")
        
        if not data['sample_transactions'].empty:
            with st.expander("Aperçu des transactions concernées"):
                st.dataframe(
                    data['sample_transactions'][['date', 'label', 'amount', 'category_validated']],
                    use_container_width=True,
                    hide_index=True
                )


def _render_rule_creation_impact(data: dict):
    """Render impact preview for rule creation."""
    with st.container(border=True):
        st.markdown("### 📊 Impact de la règle")
        
        if data.get('error'):
            st.error(f"❌ {data['error']}")
            return
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Transactions catégorisées", data['matched_transactions'])
        with col2:
            time_saved = data['estimated_time_saved']
            if time_saved < 60:
                time_str = f"{time_saved}s"
            else:
                time_str = f"{time_saved // 60}min {time_saved % 60}s"
            st.metric("Temps économisé estimé", time_str)
        
        if data['matched_transactions'] > 0:
            st.success(f"✅ Cette règle automatiserait **{data['matched_transactions']}** validations")
        else:
            st.info("ℹ️ Aucune transaction en attente ne correspond à ce pattern actuellement")
        
        if not data['sample_matches'].empty:
            with st.expander("Aperçu des transactions concernées"):
                st.dataframe(
                    data['sample_matches'][['date', 'label', 'amount']],
                    use_container_width=True,
                    hide_index=True
                )


def _render_member_rename_impact(data: dict):
    """Render impact preview for member rename."""
    with st.container(border=True):
        st.markdown("### 📊 Impact du renommage")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("En tant que payeur", data['transactions_as_member'])
        with col2:
            st.metric("En tant que bénéficiaire", data['transactions_as_beneficiary'])
        with col3:
            st.metric("Total", data['total_affected'])
        
        if data['card_mappings']:
            st.info(f"💳 **{len(data['card_mappings'])}** carte(s) associée(s) seront mises à jour: {', '.join(data['card_mappings'])}")


def _render_budget_creation_impact(data: dict):
    """Render impact preview for budget creation."""
    with st.container(border=True):
        st.markdown("### 📊 Impact du budget")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Dépenses actuelles", f"{data['current_month_spending']:.0f}€")
        with col2:
            st.metric("% du budget", f"{data['percentage_used']:.1f}%")
        with col3:
            remaining = 100 - data['percentage_used']
            st.metric("Reste disponible", f"{remaining:.1f}%")
        
        if data['status'] == 'OVERBUDGET':
            st.error("🚨 **Alerte** : Vous avez déjà dépassé ce budget ce mois-ci !")
        elif data['status'] == 'WARNING':
            st.warning("⚠️ **Attention** : Vous êtes déjà à 75%+ de ce budget")


def _render_tag_removal_impact(data: dict):
    """Render impact preview for tag removal."""
    with st.container(border=True):
        st.markdown("### 📊 Impact de la suppression")
        
        st.metric("Transactions affectées", data['transaction_count'])
        
        if data['category_breakdown']:
            st.write("**Répartition par catégorie :**")
            for cat, count in sorted(data['category_breakdown'].items(), key=lambda x: x[1], reverse=True):
                st.write(f"  • {cat}: {count} transaction(s)")
