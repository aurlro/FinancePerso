"""
Budget Manager UI Component.

Handles monthly budget management by category with an optimized UX.
Shows only active budgets by default, with option to add/edit others.
"""

import streamlit as st
import pandas as pd
from typing import Optional

from modules.db.budgets import get_budgets, set_budget, delete_budget
from modules.db.categories import get_categories
from modules.logger import logger


@st.cache_data(ttl=300)
def _get_cached_budgets() -> pd.DataFrame:
    """Cached wrapper for get_budgets."""
    return get_budgets()


@st.cache_data(ttl=300)
def _get_cached_categories() -> list:
    """Cached wrapper for get_categories."""
    return get_categories()


def _invalidate_budget_cache():
    """Invalidate budget-related caches."""
    _get_cached_budgets.clear()


@st.fragment
def render_budget_section():
    """
    Render the budget management section with optimized UX.
    
    Shows active budgets first, then allows adding new ones via an expander.
    This is a Streamlit fragment - modifying budgets only re-renders this section.
    """
    st.header("🎯 Budgets Mensuels")
    st.markdown("Définissez vos objectifs de dépenses mensuelles par catégorie.")
    
    # Load data
    budgets_df = _get_cached_budgets()
    categories = _get_cached_categories()
    
    # Create budget map for quick lookup
    budget_map = dict(zip(budgets_df['category'], budgets_df['amount'])) if not budgets_df.empty else {}
    
    # Separate categories with and without budgets
    active_categories = [cat for cat in categories if cat in budget_map and budget_map[cat] > 0]
    inactive_categories = [cat for cat in categories if cat not in budget_map or budget_map[cat] == 0]
    
    # Section 1: Active Budgets
    if active_categories:
        st.subheader(f"💰 Budgets actifs ({len(active_categories)})")
        
        # Display active budgets in a grid
        cols = st.columns(3)
        budgets_to_update = {}
        
        for i, cat in enumerate(active_categories):
            with cols[i % 3]:
                current_amount = budget_map.get(cat, 0.0)
                
                # Use a card-like container
                with st.container(border=True):
                    st.markdown(f"**{cat}**")
                    new_amount = st.number_input(
                        "Budget (€)",
                        min_value=0.0,
                        value=float(current_amount),
                        step=10.0,
                        key=f"budget_active_{cat}",
                        label_visibility="collapsed"
                    )
                    
                    if new_amount != current_amount:
                        budgets_to_update[cat] = new_amount
                    
                    # Quick delete button
                    if st.button("🗑️ Supprimer", key=f"del_budget_{cat}", use_container_width=True):
                        try:
                            delete_budget(cat)
                            st.toast(f"Budget '{cat}' supprimé", icon="🗑️")
                            _invalidate_budget_cache()
                            st.rerun(scope="fragment")
                        except Exception as e:
                            logger.error(f"Error deleting budget for {cat}: {e}")
                            st.error(f"Erreur: {e}")
        
        # Save changes if any
        if budgets_to_update:
            if st.button("💾 Sauvegarder les modifications", type="primary", key="save_active_budgets"):
                try:
                    for cat, amount in budgets_to_update.items():
                        set_budget(cat, amount)
                    st.success(f"✅ {len(budgets_to_update)} budget(s) mis à jour !")
                    _invalidate_budget_cache()
                    st.rerun(scope="fragment")
                except Exception as e:
                    logger.error(f"Error updating budgets: {e}")
                    st.error(f"Erreur lors de la sauvegarde: {e}")
    else:
        st.info("📭 Aucun budget actif. Ajoutez-en un ci-dessous.")
    
    st.divider()
    
    # Section 2: Add New Budget
    with st.expander("➕ Ajouter un budget", expanded=not active_categories):
        if inactive_categories:
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                selected_cat = st.selectbox(
                    "Catégorie",
                    options=inactive_categories,
                    key="new_budget_category"
                )
            
            with col2:
                new_amount = st.number_input(
                    "Montant mensuel (€)",
                    min_value=1.0,
                    value=100.0,
                    step=10.0,
                    key="new_budget_amount"
                )
            
            with col3:
                st.markdown("&nbsp;")  # Spacer for alignment
                if st.button("Ajouter", type="primary", use_container_width=True, key="add_budget_btn"):
                    try:
                        set_budget(selected_cat, new_amount)
                        st.success(f"✅ Budget de {new_amount:.0f}€ pour '{selected_cat}' ajouté !")
                        _invalidate_budget_cache()
                        st.rerun(scope="fragment")
                    except Exception as e:
                        logger.error(f"Error adding budget: {e}")
                        st.error(f"Erreur: {e}")
            
            # Quick-add popular categories
            st.caption("Ou sélectionnez une catégorie suggérée :")
            
            # Common budget categories
            popular_cats = ["Alimentation", "Transport", "Loisirs", "Shopping", "Santé", "Logement"]
            suggested = [c for c in popular_cats if c in inactive_categories]
            
            if suggested:
                cols = st.columns(min(len(suggested), 6))
                for i, cat in enumerate(suggested[:6]):
                    with cols[i]:
                        if st.button(f"➕ {cat}", key=f"quick_add_{cat}", use_container_width=True):
                            try:
                                set_budget(cat, 100.0)  # Default value
                                st.success(f"Budget pour '{cat}' ajouté !")
                                _invalidate_budget_cache()
                                st.rerun(scope="fragment")
                            except Exception as e:
                                logger.error(f"Error adding budget: {e}")
                                st.error(f"Erreur: {e}")
        else:
            st.success("✅ Toutes les catégories ont déjà un budget défini !")
    
    # Summary statistics
    if active_categories:
        st.divider()
        total_budget = sum(budget_map.get(cat, 0) for cat in active_categories)
        
        cols = st.columns(4)
        with cols[0]:
            st.metric("Budgets actifs", len(active_categories))
        with cols[1]:
            st.metric("Budget total mensuel", f"{total_budget:,.0f} €")
        with cols[2]:
            avg_budget = total_budget / len(active_categories) if active_categories else 0
            st.metric("Budget moyen", f"{avg_budget:,.0f} €")
        with cols[3]:
            remaining = len(categories) - len(active_categories)
            st.metric("Catégories sans budget", remaining)


def render_compact_budget_summary():
    """
    Render a compact summary of budgets for display in other pages.
    """
    budgets_df = _get_cached_budgets()
    
    if budgets_df.empty:
        st.caption("Aucun budget défini")
        return
    
    budget_map = dict(zip(budgets_df['category'], budgets_df['amount']))
    active_count = sum(1 for amount in budget_map.values() if amount > 0)
    total = sum(amount for amount in budget_map.values() if amount > 0)
    
    st.metric("Budgets définis", f"{active_count}")
    st.metric("Total mensuel", f"{total:,.0f} €")
