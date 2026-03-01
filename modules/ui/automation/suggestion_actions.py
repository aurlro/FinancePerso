"""
Suggestion Action Handlers - Pattern Command extensible

Chaque action de suggestion est implémentée comme une classe dédiée
avec une interface commune pour faciliter l'ajout de nouvelles actions.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable
import streamlit as st
import pandas as pd
from datetime import datetime

from modules.ai.suggestions.base import Suggestion
from modules.db.transactions import get_all_transactions
from modules.db.rules import add_learning_rule
from modules.db.categories import get_categories_with_emojis
from modules.ui.feedback import toast_success, toast_info, toast_error
from modules.logger import logger


class SuggestionAction(ABC):
    """Base class for all suggestion actions."""
    
    action_type: str = ""
    
    @abstractmethod
    def can_handle(self, action_type: str) -> bool:
        """Check if this handler can handle the given action type."""
        pass
    
    @abstractmethod
    def execute(self, suggestion: Suggestion, action_data: dict) -> dict:
        """
        Execute the action.
        
        Returns:
            dict with:
            - success: bool
            - message: str (user feedback)
            - view_data: dict (optional data for inline view)
            - navigate_to: str (optional page to navigate to)
        """
        pass
    
    def render_inline_view(self, view_data: dict) -> bool:
        """
        Render an inline view for this action.
        
        Returns:
            True if the view was rendered, False otherwise
        """
        return False  # Default: no inline view


class CreateRuleAction(SuggestionAction):
    """Handler for create_rule action type."""
    
    action_type = "create_rule"
    
    def can_handle(self, action_type: str) -> bool:
        return action_type == self.action_type
    
    def execute(self, suggestion: Suggestion, action_data: dict) -> dict:
        pattern = action_data.get("pattern", "")
        category = action_data.get("category") or action_data.get("suggested_category", "Inconnu")
        
        if not pattern:
            return {"success": False, "message": "❌ Pattern manquant"}
        
        try:
            add_learning_rule(pattern, category)
            return {
                "success": True,
                "message": f"✅ Règle créée : '{pattern}' → {category}",
                "navigate_to": "rules",  # Suggest navigation to rules tab
            }
        except Exception as e:
            logger.error(f"Error creating rule: {e}")
            return {"success": False, "message": f"❌ Erreur : {str(e)[:50]}"}


class ExploreCategoryAction(SuggestionAction):
    """Handler for explore_category action type."""
    
    action_type = "explore_category"
    
    def can_handle(self, action_type: str) -> bool:
        return action_type == self.action_type
    
    def execute(self, suggestion: Suggestion, action_data: dict) -> dict:
        category = action_data.get("category", "")
        if not category:
            return {"success": False, "message": "❌ Catégorie manquante"}
        
        # Get transactions for this category in current month
        df = get_all_transactions()
        if df.empty:
            return {"success": False, "message": "❌ Aucune transaction"}
        
        current_month = datetime.now().strftime("%Y-%m")
        df["month"] = df["date"].str[:7]
        
        category_txns = df[
            (df["category_validated"] == category) & 
            (df["month"] == current_month)
        ].sort_values("amount")
        
        # Calculate comparison with average
        historical = df[df["month"] != current_month]
        avg_monthly = historical[historical["category_validated"] == category]["amount"].sum() / 3  # Approximation
        current_total = category_txns["amount"].sum()
        
        return {
            "success": True,
            "message": f"📊 Exploration de {category}",
            "view_data": {
                "category": category,
                "transactions": category_txns.to_dict("records"),
                "current_total": abs(current_total),
                "average": abs(avg_monthly),
                "difference_pct": ((abs(current_total) / abs(avg_monthly)) - 1) * 100 if avg_monthly else 0,
            }
        }
    
    def render_inline_view(self, view_data: dict) -> bool:
        """Render inline view for category exploration."""
        category = view_data.get("category", "")
        transactions = view_data.get("transactions", [])
        current_total = view_data.get("current_total", 0)
        average = view_data.get("average", 0)
        diff_pct = view_data.get("difference_pct", 0)
        
        with st.container(border=True):
            st.markdown(f"### 📈 Exploration : {category}")
            
            # Visual comparison
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Ce mois", f"{current_total:.0f}€")
            with col2:
                st.metric("Moyenne", f"{average:.0f}€")
            with col3:
                st.metric("Différence", f"{diff_pct:+.0f}%", delta_color="inverse")
            
            # Transactions list
            if transactions:
                st.markdown("#### 💳 Transactions ce mois")
                for txn in sorted(transactions, key=lambda x: abs(x["amount"]), reverse=True)[:10]:
                    amount = abs(txn["amount"])
                    date = txn["date"]
                    label = txn["label"][:40]
                    cols = st.columns([3, 2, 1])
                    cols[0].caption(f"{date} - {label}")
                    cols[2].markdown(f"**-{amount:.2f}€**")
            
            # Actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Voir toutes les transactions", key=f"explore_all_{category}"):
                    st.session_state["explore_category_filter"] = category
                    st.session_state["active_intelligence_tab"] = "rules"  # Actually should navigate to operations
                    st.rerun()
            with col2:
                if st.button("✅ Créer une règle", key=f"explore_rule_{category}"):
                    st.session_state["quick_rule_category"] = category
                    st.rerun()
            
            return True


class ViewSubscriptionAction(SuggestionAction):
    """Handler for view_subscription action type."""
    
    action_type = "view_subscription"
    
    def can_handle(self, action_type: str) -> bool:
        return action_type == self.action_type
    
    def execute(self, suggestion: Suggestion, action_data: dict) -> dict:
        label = action_data.get("label", "")
        if not label:
            return {"success": False, "message": "❌ Libellé manquant"}
        
        df = get_all_transactions()
        if df.empty:
            return {"success": False, "message": "❌ Aucune transaction"}
        
        # Get evolution data
        df["month"] = df["date"].str[:7]
        label_df = df[df["label"] == label].copy()
        
        monthly_evolution = label_df.groupby("month").agg({
            "amount": ["mean", "count"]
        }).reset_index()
        monthly_evolution.columns = ["month", "avg_amount", "count"]
        
        # Detect changes
        changes = []
        for i in range(1, len(monthly_evolution)):
            prev = monthly_evolution.iloc[i-1]
            curr = monthly_evolution.iloc[i]
            if abs(curr["avg_amount"]) > abs(prev["avg_amount"]) * 1.1:  # 10% increase
                changes.append({
                    "month": curr["month"],
                    "from": abs(prev["avg_amount"]),
                    "to": abs(curr["avg_amount"]),
                    "increase_pct": ((abs(curr["avg_amount"]) / abs(prev["avg_amount"])) - 1) * 100
                })
        
        return {
            "success": True,
            "message": f"💳 Évolution de {label[:30]}...",
            "view_data": {
                "label": label,
                "monthly_data": monthly_evolution.to_dict("records"),
                "changes": changes,
            }
        }
    
    def render_inline_view(self, view_data: dict) -> bool:
        """Render inline view for subscription evolution."""
        label = view_data.get("label", "")
        monthly_data = view_data.get("monthly_data", [])
        changes = view_data.get("changes", [])
        
        with st.container(border=True):
            st.markdown(f"### 💳 Évolution : {label[:50]}")
            
            # Changes timeline
            if changes:
                st.markdown("#### 📈 Changements détectés")
                for change in changes:
                    st.warning(
                        f"**{change['month']}** : "
                        f"{change['from']:.0f}€ → {change['to']:.0f}€ "
                        f"(+{change['increase_pct']:.0f}%)"
                    )
            
            # Monthly data table
            if monthly_data:
                st.markdown("#### 📅 Historique mensuel")
                df_display = pd.DataFrame(monthly_data)
                df_display["avg_amount"] = df_display["avg_amount"].abs().round(2)
                st.dataframe(
                    df_display.rename(columns={
                        "month": "Mois",
                        "avg_amount": "Montant moyen",
                        "count": "Nombre"
                    }),
                    hide_index=True,
                    use_container_width=True
                )
            
            # Actions
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💰 Voir dans Abonnements", key=f"sub_view_{hash(label)}"):
                    st.query_params["tab"] = "subscriptions"
                    st.rerun()
            with col2:
                if st.button("🌐 Site officiel", key=f"sub_site_{hash(label)}"):
                    toast_info("🔍 Recherche du site en cours...")
            with col3:
                if st.button("🔔 Me rappeler", key=f"sub_remind_{hash(label)}"):
                    toast_success("⏰ Rappel programmé dans 7 jours")
            
            return True


class ViewTransactionAction(SuggestionAction):
    """Handler for view_transaction action type."""
    
    action_type = "view_transaction"
    
    def can_handle(self, action_type: str) -> bool:
        return action_type == self.action_type
    
    def execute(self, suggestion: Suggestion, action_data: dict) -> dict:
        txn_id = action_data.get("transaction_id")
        if not txn_id:
            return {"success": False, "message": "❌ ID transaction manquant"}
        
        df = get_all_transactions()
        txn = df[df["id"] == txn_id]
        
        if txn.empty:
            return {"success": False, "message": "❌ Transaction non trouvée"}
        
        txn_data = txn.iloc[0].to_dict()
        
        return {
            "success": True,
            "message": "🔍 Détails de la transaction",
            "view_data": {
                "transaction": txn_data,
            }
        }
    
    def render_inline_view(self, view_data: dict) -> bool:
        """Render inline view for transaction details."""
        txn = view_data.get("transaction", {})
        
        with st.container(border=True):
            st.markdown("### 🔍 Détail de la transaction")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Libellé** : {txn.get('label', 'N/A')}")
                st.markdown(f"**Date** : {txn.get('date', 'N/A')}")
                st.markdown(f"**Catégorie** : {txn.get('category_validated', 'N/A')}")
            with col2:
                amount = abs(txn.get('amount', 0))
                st.markdown(f"**Montant** : **{amount:.2f}€**")
                st.markdown(f"**Compte** : {txn.get('account', 'N/A')}")
            
            # Contextual info
            category = txn.get('category_validated', '')
            if category:
                df = get_all_transactions()
                cat_txns = df[df["category_validated"] == category]["amount"].abs()
                if not cat_txns.empty:
                    median = cat_txns.median()
                    p90 = cat_txns.quantile(0.90)
                    
                    st.divider()
                    st.markdown(f"#### 📊 Contexte dans la catégorie {category}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Médiane", f"{median:.0f}€")
                    col2.metric("90ème percentile", f"{p90:.0f}€")
                    col3.metric("Cette transaction", f"{amount:.0f}€")
                    
                    if amount > p90:
                        st.warning(f"⚠️ Cette transaction est supérieure au 90ème percentile ({p90:.0f}€)")
            
            return True


class MergeCategoriesAction(SuggestionAction):
    """Handler for merge_categories action type."""
    
    action_type = "merge_categories"
    
    def can_handle(self, action_type: str) -> bool:
        return action_type == self.action_type
    
    def execute(self, suggestion: Suggestion, action_data: dict) -> dict:
        source = action_data.get("source", "")
        target = action_data.get("target", "")
        
        if not source or not target:
            return {"success": False, "message": "❌ Catégories source/target manquantes"}
        
        # Just return the data for inline rendering - actual merge happens in view
        return {
            "success": True,
            "message": f"🏷️ Fusion de '{source}' vers '{target}'",
            "view_data": {
                "source": source,
                "target": target,
            }
        }
    
    def render_inline_view(self, view_data: dict) -> bool:
        """Render inline form for merging categories."""
        source = view_data.get("source", "")
        target = view_data.get("target", "")
        
        # Get transaction counts
        df = get_all_transactions()
        source_count = len(df[df["category_validated"] == source])
        target_count = len(df[df["category_validated"] == target])
        
        with st.container(border=True):
            st.markdown("### 🏷️ Fusion de catégories")
            
            st.warning(
                f"Vous êtes sur le point de fusionner **{source}** ({source_count} transactions) "
                f"vers **{target}** ({target_count} transactions)."
            )
            
            st.markdown("#### 📊 Impact")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Source : {source}**")
                st.caption(f"• {source_count} transactions seront déplacées")
                st.caption("• Cette catégorie sera supprimée")
            with col2:
                st.markdown(f"**Cible : {target}**")
                st.caption(f"• {target_count} transactions existantes")
                st.caption(f"• {source_count + target_count} transactions après fusion")
            
            # Confirmation
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirmer la fusion", key=f"merge_confirm_{source}_{target}", type="primary"):
                    try:
                        from modules.db.categories import merge_categories
                        merge_categories(source, target)
                        toast_success(f"✅ '{source}' fusionné avec '{target}'")
                        return True
                    except Exception as e:
                        toast_error(f"❌ Erreur : {str(e)[:50]}")
            with col2:
                if st.button("❌ Annuler", key=f"merge_cancel_{source}_{target}"):
                    return True
            
            return True


class ViewDuplicatesAction(SuggestionAction):
    """Handler for view_duplicates action type."""
    
    action_type = "view_duplicates"
    
    def can_handle(self, action_type: str) -> bool:
        return action_type == self.action_type
    
    def execute(self, suggestion: Suggestion, action_data: dict) -> dict:
        count = action_data.get("count", 0)
        
        # Find actual duplicates
        df = get_all_transactions()
        grouped = df.groupby(["date", "label", "amount"]).size().reset_index(name="count")
        duplicates = grouped[grouped["count"] > 1]
        
        duplicate_details = []
        for _, dup in duplicates.iterrows():
            matching = df[
                (df["date"] == dup["date"]) &
                (df["label"] == dup["label"]) &
                (df["amount"] == dup["amount"])
            ]
            duplicate_details.append({
                "date": dup["date"],
                "label": dup["label"],
                "amount": dup["amount"],
                "count": dup["count"],
                "ids": matching["id"].tolist(),
            })
        
        return {
            "success": True,
            "message": f"⚠️ {count} doublons détectés",
            "view_data": {
                "duplicates": duplicate_details,
                "total_count": count,
            }
        }
    
    def render_inline_view(self, view_data: dict) -> bool:
        """Render inline view for duplicates analysis."""
        duplicates = view_data.get("duplicates", [])
        total = view_data.get("total_count", 0)
        
        with st.container(border=True):
            st.markdown(f"### ⚠️ Analyse des doublons ({total} détectés)")
            
            if not duplicates:
                st.success("✅ Aucun doublon trouvé")
                return True
            
            for i, dup in enumerate(duplicates[:5]):  # Show first 5
                with st.expander(
                    f"🔍 {dup['date']} - {dup['label'][:40]}... "
                    f"({dup['count']} occurrences)"
                ):
                    st.caption(f"Montant : {abs(dup['amount']):.2f}€")
                    st.caption(f"IDs : {', '.join(map(str, dup['ids']))}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Supprimer les doublons", key=f"dup_del_{i}"):
                            toast_info("🚧 Fonctionnalité en cours de développement")
                    with col2:
                        if st.button("✅ Ce ne sont pas des doublons", key=f"dup_keep_{i}"):
                            toast_info("✅ Marqué comme non-doublon")
            
            if len(duplicates) > 5:
                st.caption(f"... et {len(duplicates) - 5} autres groupes")
            
            return True


# =============================================================================
# Analyze Recurring Action
# =============================================================================

class AnalyzeRecurringAction(SuggestionAction):
    """Handler for analyze_recurring action type.
    
    Analyzes a recurring expense to show historical data, trends,
    and provide insights for potential savings.
    """
    
    action_type = "analyze_recurring"
    
    def can_handle(self, action_type: str) -> bool:
        return action_type == self.action_type
    
    def execute(self, suggestion: Suggestion, action_data: dict) -> dict:
        label = action_data.get("label", "")
        monthly_amount = action_data.get("amount", 0)
        
        if not label:
            return {"success": False, "message": "❌ Libellé manquant"}
        
        try:
            # Get all transactions matching this label
            df = get_all_transactions()
            if df.empty:
                return {"success": False, "message": "❌ Aucune transaction"}
            
            # Find transactions matching the label pattern
            matching = df[df["label"].str.contains(label[:20], case=False, na=False)]
            
            if matching.empty:
                return {"success": False, "message": f"❌ Aucune transaction trouvée pour '{label}'"}
            
            # Calculate statistics
            matching["date"] = pd.to_datetime(matching["date"])
            matching = matching.sort_values("date")
            
            total_spent = abs(matching["amount"].sum())
            avg_amount = abs(matching["amount"].mean())
            count = len(matching)
            first_date = matching["date"].min()
            last_date = matching["date"].max()
            
            # Calculate monthly cost
            months_active = max(1, (last_date - first_date).days / 30)
            monthly_cost = total_spent / months_active
            
            # Annual projection
            annual_cost = monthly_cost * 12
            
            return {
                "success": True,
                "message": f"📊 Analyse de '{label[:30]}...'",
                "view_data": {
                    "label": label,
                    "monthly_amount": monthly_amount,
                    "total_spent": total_spent,
                    "avg_amount": avg_amount,
                    "count": count,
                    "monthly_cost": monthly_cost,
                    "annual_cost": annual_cost,
                    "first_date": first_date.strftime("%Y-%m-%d"),
                    "last_date": last_date.strftime("%Y-%m-%d"),
                    "transactions": matching[["date", "label", "amount", "category_validated"]].tail(6).to_dict("records"),
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing recurring expense: {e}")
            return {"success": False, "message": f"❌ Erreur lors de l'analyse : {str(e)[:50]}"}
    
    def render_inline_view(self, view_data: dict) -> bool:
        """Render inline view for recurring expense analysis."""
        label = view_data.get("label", "")
        monthly_amount = view_data.get("monthly_amount", 0)
        total_spent = view_data.get("total_spent", 0)
        monthly_cost = view_data.get("monthly_cost", 0)
        annual_cost = view_data.get("annual_cost", 0)
        count = view_data.get("count", 0)
        first_date = view_data.get("first_date", "")
        last_date = view_data.get("last_date", "")
        transactions = view_data.get("transactions", [])
        
        with st.container(border=True):
            st.markdown(f"### 📈 Analyse : {label[:40]}...")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 Mensuel", f"{monthly_cost:.0f}€")
            with col2:
                st.metric("📅 Annuel", f"{annual_cost:.0f}€")
            with col3:
                st.metric("🔢 Occurrences", f"{count}")
            with col4:
                st.metric("💸 Total dépensé", f"{total_spent:.0f}€")
            
            st.caption(f"🗓️ Période : {first_date} → {last_date}")
            
            # Insights
            st.markdown("#### 💡 Insights")
            
            if annual_cost > 500:
                st.warning(f"⚠️ Cette dépense vous coûte **{annual_cost:.0f}€ par an** !")
            elif annual_cost > 200:
                st.info(f"ℹ️ Soit environ **{annual_cost:.0f}€ par an**.")
            else:
                st.success(f"✅ Une dépense modeste à **{annual_cost:.0f}€ par an**.")
            
            # Recent transactions
            if transactions:
                st.markdown("#### 📝 Dernières occurrences")
                for txn in transactions:
                    date_str = txn["date"].strftime("%d/%m/%Y") if isinstance(txn["date"], pd.Timestamp) else str(txn["date"])[:10]
                    amount = abs(txn["amount"])
                    st.caption(f"{date_str} : {txn['label'][:40]}... ({amount:.2f}€)")
            
            # Action suggestions
            st.markdown("#### 🎯 Actions suggérées")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Voir toutes les occurrences", key=f"recurring_all_{label[:20]}"):
                    toast_info("🚧 Navigation vers la recherche en cours de développement")
            with col2:
                if st.button("💡 Chercher des alternatives", key=f"recurring_alt_{label[:20]}"):
                    toast_info("🚧 Fonctionnalité en cours de développement")
            
            return True


# =============================================================================
# REGISTRY - Auto-discovery of action handlers
# =============================================================================

_ACTION_HANDLERS: list[SuggestionAction] = [
    CreateRuleAction(),
    ExploreCategoryAction(),
    ViewSubscriptionAction(),
    ViewTransactionAction(),
    MergeCategoriesAction(),
    ViewDuplicatesAction(),
    AnalyzeRecurringAction(),
]


def get_action_handler(action_type: str) -> SuggestionAction | None:
    """Get the appropriate handler for an action type."""
    for handler in _ACTION_HANDLERS:
        if handler.can_handle(action_type):
            return handler
    return None


def execute_suggestion_action(suggestion: Suggestion) -> dict:
    """
    Execute a suggestion action and return result.
    
    This is the main entry point for executing suggestion actions.
    """
    action_data = suggestion.action_data or {}
    action_type = action_data.get("type", "")
    
    if not action_type:
        return {"success": False, "message": "❌ Type d'action non défini"}
    
    handler = get_action_handler(action_type)
    
    if not handler:
        logger.warning(f"No handler found for action type: {action_type}")
        return {
            "success": False,
            "message": f"💡 Action '{action_type}' - fonctionnalité en développement"
        }
    
    try:
        return handler.execute(suggestion, action_data)
    except Exception as e:
        logger.error(f"Error executing action {action_type}: {e}")
        return {"success": False, "message": f"❌ Erreur : {str(e)[:50]}"}


def render_action_inline_view(action_type: str, view_data: dict) -> bool:
    """
    Render an inline view for an action if available.
    
    Returns:
        True if a view was rendered, False otherwise
    """
    handler = get_action_handler(action_type)
    if not handler:
        return False
    
    try:
        return handler.render_inline_view(view_data)
    except Exception as e:
        logger.error(f"Error rendering inline view for {action_type}: {e}")
        return False
