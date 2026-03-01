"""
📊 History Tab - Traçabilité et contrôle

Affiche :
- Statistiques d'automatisation (impact réel)
- Log des actions effectuées
- Corbeille (faux positifs exclus)

Objectif : Donner à l'utilisateur la vision et le contrôle sur ce que l'IA fait
"""

import re

import pandas as pd
import streamlit as st

from modules.db.recurrence_feedback import delete_feedback, get_all_feedback
from modules.db.rules import get_learning_rules
from modules.db.transactions import get_all_transactions
from modules.ui.automation.alerts_section import render_remaining_budget_calculator
from modules.ui.feedback import toast_info, toast_success

# =============================================================================
# HISTORY TAB RENDERER
# =============================================================================

def render_history_tab():
    """Render the history and audit tab."""
    
    st.header("📊 Historique & Contrôle")
    st.caption("Visualisez l'impact de l'automatisation et contrôlez les décisions de l'IA.")
    
    st.divider()
    
    # KPIs d'automatisation
    _render_automation_stats()
    
    st.divider()
    
    # Navigation
    if "history_subtab" not in st.session_state:
        st.session_state.history_subtab = "📈 Statistiques"
    
    subtab = st.segmented_control(
        "Vue",
        options=["📈 Statistiques", "💳 Calculateur", "🗑️ Corbeille"],
        default=st.session_state.history_subtab,
        label_visibility="collapsed",
    )
    
    if subtab:
        st.session_state.history_subtab = subtab
    
    st.divider()
    
    if st.session_state.history_subtab == "📈 Statistiques":
        _render_detailed_stats()
    elif st.session_state.history_subtab == "💳 Calculateur":
        render_remaining_budget_calculator()
    else:
        _render_trash_section()


def _render_automation_stats():
    """Render automation impact statistics."""
    
    # Collecter les données
    rules_df = get_learning_rules()
    feedback = get_all_feedback()
    transactions_df = get_all_transactions()
    
    # Calculer les métriques
    total_rules = len(rules_df)
    total_subscriptions = len([f for f in feedback if f["user_feedback"] == "confirmed"])
    total_excluded = len([f for f in feedback if f["user_feedback"] == "rejected"])
    
    # Estimer les transactions auto-catégorisées
    auto_categorized = 0
    if not transactions_df.empty and not rules_df.empty:
        # Pre-compile valid regex patterns for efficiency
        valid_patterns = []
        for _, rule in rules_df.iterrows():
            try:
                pattern = rule["pattern"]
                # Validate pattern by compiling it
                re.compile(pattern, re.IGNORECASE)
                valid_patterns.append(pattern)
            except re.error:
                continue
        
        if valid_patterns:
            # Combine all patterns into a single regex for vectorized matching
            combined_pattern = "|".join(f"({p})" for p in valid_patterns)
            labels = transactions_df["label"].fillna("").astype(str)
            auto_categorized = labels.str.contains(combined_pattern, case=False, regex=True).sum()
    
    # Affichage
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("📝 Règles actives", total_rules)
    
    with cols[1]:
        st.metric("🔁 Abonnements suivis", total_subscriptions)
    
    with cols[2]:
        st.metric("🏷️ Auto-catégorisées", 
                 auto_categorized,
                 delta=f"{auto_categorized/len(transactions_df)*100:.1f}%" if len(transactions_df) > 0 else None)
    
    with cols[3]:
        st.metric("🗑️ Faux positifs exclus", total_excluded)


def _render_detailed_stats():
    """Render detailed automation statistics."""
    
    st.subheader("📈 Impact de l'automatisation")
    
    transactions_df = get_all_transactions()
    if transactions_df.empty:
        st.info("📭 Importez des transactions pour voir les statistiques.")
        return
    
    # Statistiques par catégorie
    st.markdown("#### Répartition par catégorie")
    
    if "category" not in transactions_df.columns:
        st.info("📭 Les transactions n'ont pas encore été catégorisées.")
        return
    
    category_stats = transactions_df.groupby("category").agg({
        "amount": ["count", "sum"]
    }).reset_index()
    category_stats.columns = ["Catégorie", "Nombre", "Total"]
    category_stats["Total"] = category_stats["Total"].abs()
    category_stats = category_stats.sort_values("Nombre", ascending=False)
    
    st.dataframe(
        category_stats,
        column_config={
            "Catégorie": st.column_config.TextColumn("Catégorie"),
            "Nombre": st.column_config.NumberColumn("Transactions"),
            "Total": st.column_config.NumberColumn("Montant total", format="%.2f €"),
        },
        use_container_width=True,
        hide_index=True,
    )
    
    # Timeline de l'apprentissage
    st.divider()
    st.markdown("#### 📅 Timeline de l'apprentissage")
    
    rules_df = get_learning_rules()
    if not rules_df.empty and "created_at" in rules_df.columns:
        # Grouper par mois de création
        rules_df["month"] = pd.to_datetime(rules_df["created_at"]).dt.to_period("M")
        monthly_rules = rules_df.groupby("month").size().reset_index(name="Nouvelles règles")
        
        st.line_chart(monthly_rules.set_index("month"))
    else:
        st.caption("Pas assez d'historique pour afficher la timeline")


def _render_trash_section():
    """Render trash/recycle bin for rejected items."""
    
    st.subheader("🗑️ Corbeille")
    st.caption("Éléments que vous avez choisi d'ignorer. Vous pouvez les restaurer.")
    
    rejected = get_all_feedback(status="rejected")
    
    if not rejected:
        st.info("📭 La corbeille est vide.")
        st.caption("Les éléments ignorés depuis l'inbox apparaîtront ici.")
        return
    
    st.markdown(f"**{len(rejected)}** élément(s) ignoré(s)")
    
    for item in rejected:
        with st.container(border=True):
            cols = st.columns([3, 2, 1])
            
            with cols[0]:
                st.markdown(f"**{item['label_pattern']}**")
                if item.get("category"):
                    st.caption(f"Catégorie : {item['category']}")
            
            with cols[1]:
                if item.get("notes"):
                    st.caption(f"💬 {item['notes']}")
                if item.get("validated_at") or item.get("created_at"):
                    date = item.get("validated_at") or item.get("created_at")
                    st.caption(f"🗓️ {str(date)[:10]}")
            
            with cols[2]:
                if st.button("🔄 Restaurer", key=f"restore_{item['id']}", use_container_width=True):
                    delete_feedback(item["label_pattern"], item.get("category"))
                    toast_success("✅ Élément restauré - il réapparaîtra dans l'inbox")
                    st.rerun()
    
    # Option vider la corbeille
    st.divider()
    if st.button("🗑️ Vider la corbeille définitivement", type="secondary"):
        # TODO: Implémenter une vraie suppression définitive
        toast_info("💡 La suppression définitive sera implémentée prochainement")
