"""
Rule Audit UI Component.

Provides AI-powered analysis of learning rules to detect conflicts,
duplicates, overlaps, and other issues.
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from modules.ai.rules_auditor import analyze_rules_integrity
from modules.db.rules import delete_learning_rule, get_learning_rules, update_learning_rule
from modules.logger import logger

# Initialisation des variables de session
if "audit_last_run" not in st.session_state:
    st.session_state["audit_last_run"] = None
if "get" not in st.session_state:
    st.session_state["get"] = None


def invalidate_audit_cache():
    """Invalidate audit-related session state caches."""
    keys_to_clear = ["quick_audit_score", "audit_results", "audit_last_run", "rules_cache_hash"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


@st.cache_data(ttl=600)
def _get_cached_rules_for_audit() -> pd.DataFrame:
    """Cached wrapper for getting rules (used by audit)."""
    return get_learning_rules()


def _calculate_health_score(issues: dict) -> int:
    """Calculate health score from issues dict."""
    return issues.get("score", 100)


def _render_health_indicator(score: int):
    """Render a visual health indicator based on score."""
    if score >= 80:
        color = "green"
        emoji = "✅"
        status = "Excellent"
    elif score >= 50:
        color = "orange"
        emoji = "⚠️"
        status = "Moyen"
    else:
        color = "red"
        emoji = "🚨"
        status = "Critique"

    st.markdown(f"Santé : {emoji} :{color}[**{score}%**] ({status})")


@st.fragment
def render_audit_section():
    """
    Render the AI audit section for analyzing rules integrity.

    This is a Streamlit fragment - running an audit will only re-render
    this section, not the entire page.
    """
    st.header("🕵️ Audit & Optimisation")
    st.markdown("L'IA analyse vos règles pour détecter incohérences et doublons.")

    # Load rules
    rules_df = _get_cached_rules_for_audit()

    if rules_df.empty:
        st.info("📭 Aucune règle à auditer. Ajoutez d'abord quelques règles de catégorisation.")
        return

    # Header with run button and last update
    col_audit, col_status = st.columns([1, 3])

    with col_audit:
        if st.button(
            "🚀 Lancer l'audit IA", type="primary", use_container_width=True, key="button_89"
        ):
            with st.spinner("Analyse en cours..."):
                try:
                    audit_results = analyze_rules_integrity(rules_df)
                    st.session_state["audit_results"] = audit_results
                    st.session_state["audit_last_run"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    st.session_state["quick_audit_score"] = audit_results["score"]
                    st.rerun(scope="fragment")
                except Exception as e:
                    logger.error(f"Error during rules audit: {e}")
                    st.error(f"Erreur lors de l'audit: {e}")

    with col_status:
        # Show quick score if available
        if "quick_audit_score" in st.session_state:
            _render_health_indicator(st.session_state["quick_audit_score"])

        if "audit_last_run" in st.session_state:
            st.caption(f"🕐 Dernière analyse : {st.session_state['audit_last_run']}")
        else:
            st.caption("🕐 Aucune analyse récente. Lancez un audit pour voir les résultats.")

    # Display audit results
    if "audit_results" not in st.session_state:
        return

    issues = st.session_state["audit_results"]

    # Check if any issues exist
    has_issues = any(
        [
            issues.get("conflicts", []),
            issues.get("duplicates", []),
            issues.get("overlaps", []),
            issues.get("vague", []),
            issues.get("stale", []),
        ]
    )

    if not has_issues:
        st.success("🎉 Aucune incohérence détectée ! Vos règles sont propres et bien optimisées.")
        return

    st.divider()
    st.subheader("📋 Résultats de l'analyse")

    # 1. Conflicts (most critical)
    if issues.get("conflicts"):
        conflicts = issues["conflicts"]
        with st.expander(
            f"🚨 **{len(conflicts)} Conflit(s) majeur(s)** - Même pattern, catégories différentes",
            expanded=True,
        ):
            st.error(
                "Ces règles créent une ambiguïté : le même pattern mène à des catégories différentes."
            )

            for conflict in conflicts:
                cols = st.columns([4, 1])
                with cols[0]:
                    st.markdown(
                        f"**`{conflict['pattern']}`** → {', '.join(conflict['categories'])}"
                    )
                    st.caption(conflict.get("message", ""))
                with cols[1]:
                    if st.button("🗑️ Supprimer", key=f"audit_del_conflict_{conflict['ids'][0]}"):
                        try:
                            for rule_id in conflict["ids"]:
                                delete_learning_rule(rule_id)
                            st.success("✅ Règles supprimées")
                            invalidate_audit_cache()
                            _get_cached_rules_for_audit.clear()
                            st.rerun(scope="fragment")
                        except Exception as e:
                            st.error(f"Erreur: {e}")

    # 2. Duplicates
    if issues.get("duplicates"):
        duplicates = issues["duplicates"]
        with st.expander(f"♻️ **{len(duplicates)} Doublon(s)** - Redondants", expanded=False):
            st.warning("Ces règles sont exactement identiques et peuvent être supprimées.")

            for dup in duplicates:
                cols = st.columns([4, 1])
                with cols[0]:
                    st.markdown(f"**`{dup['pattern']}`** ({dup['category']})")
                with cols[1]:
                    # Delete only the first ID (they're duplicates, so one is enough)
                    if st.button("🗑️", key=f"audit_del_dup_{dup['ids'][0]}"):
                        try:
                            delete_learning_rule(dup["ids"][0])
                            st.success("✅ Doublon supprimé")
                            invalidate_audit_cache()
                            _get_cached_rules_for_audit.clear()
                            st.rerun(scope="fragment")
                        except Exception as e:
                            st.error(f"Erreur: {e}")

    # 3. Overlaps
    if issues.get("overlaps"):
        overlaps = issues["overlaps"]
        with st.expander(
            f"ℹ️ **{len(overlaps)} Chevauchement(s)** - Patterns imbriqués", expanded=True
        ):
            st.info("Un pattern est contenu dans un autre avec une catégorie différente.")
            st.caption("Cela peut créer des comportements inattendus selon l'ordre d'application.")
            
            # Action globale
            col_global = st.columns([1, 1, 2])
            with col_global[0]:
                if st.button("📋 Voir toutes les règles", use_container_width=True, key="overlap_voir_regles"):
                    st.session_state["audit_active_tab"] = "📋 Audit des Règles"
                    st.rerun()
            with col_global[1]:
                if st.button("🧠 Intelligence → Règles", use_container_width=True, key="overlap_voir_intelligence"):
                    st.switch_page("pages/4_Intelligence.py")
            
            st.divider()

            for i, ov in enumerate(overlaps):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(
                            f"**{i+1}. `{ov['shorter_pattern']}`** ({ov['shorter_category']}) "
                            f"→ inclus dans → "
                            f"**`{ov['longer_pattern']}`** ({ov['longer_category']})"
                        )
                        
                        # Impact analysis
                        from modules.db.connection import get_db_connection
                        with get_db_connection() as conn:
                            cursor = conn.cursor()
                            # Count affected transactions
                            cursor.execute(
                                "SELECT COUNT(*) FROM transactions WHERE label LIKE ?",
                                (f"%{ov['shorter_pattern']}%",)
                            )
                            affected = cursor.fetchone()[0]
                            
                            if affected > 0:
                                st.caption(f"📊 {affected} transaction(s) seraient affectées par '{ov['shorter_pattern']}'")
                            else:
                                st.caption("📊 Aucune transaction historique ne correspond à ce pattern")
                    
                    with col2:
                        st.markdown("**💡 Actions:**")
                        
                        # Get rule IDs for the patterns (need new connection)
                        with get_db_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "SELECT id, priority FROM learning_rules WHERE pattern = ?",
                                (ov['shorter_pattern'],)
                            )
                            shorter_rule = cursor.fetchone()
                            
                            cursor.execute(
                                "SELECT id, priority FROM learning_rules WHERE pattern = ?",
                                (ov['longer_pattern'],)
                            )
                            longer_rule = cursor.fetchone()
                        
                        # Action: Increase priority of shorter pattern
                        if shorter_rule and longer_rule:
                            shorter_id, shorter_priority = shorter_rule
                            longer_id, longer_priority = longer_rule
                            
                            if shorter_priority <= longer_priority:
                                new_priority = longer_priority + 10
                                if st.button(
                                    f"⬆️ Priorité +10", 
                                    key=f"overlap_up_{shorter_id}_{i}",
                                    help=f"Augmenter la priorité de '{ov['shorter_pattern']}' à {new_priority}"
                                ):
                                    try:
                                        from modules.db.rules import update_learning_rule
                                        update_learning_rule(shorter_id, priority=new_priority)
                                        st.success("✅ Priorité augmentée !")
                                        invalidate_audit_cache()
                                        _get_cached_rules_for_audit.clear()
                                        st.rerun(scope="fragment")
                                    except Exception as e:
                                        st.error(f"Erreur: {e}")
                        
                        # Action: Delete shorter pattern
                        if shorter_rule:
                            if st.button(
                                "🗑️ Supprimer court",
                                key=f"overlap_del_{shorter_rule[0]}_{i}",
                                help=f"Supprimer la règle '{ov['shorter_pattern']}'"
                            ):
                                try:
                                    delete_learning_rule(shorter_rule[0])
                                    st.success("✅ Règle supprimée")
                                    invalidate_audit_cache()
                                    _get_cached_rules_for_audit.clear()
                                    st.rerun(scope="fragment")
                                except Exception as e:
                                    st.error(f"Erreur: {e}")
                        
                        # Action: Keep longer only
                        if longer_rule:
                            if st.button(
                                "✅ Garder long",
                                key=f"overlap_keep_{longer_rule[0]}_{i}",
                                help=f"Conserver uniquement '{ov['longer_pattern']}'"
                            ):
                                try:
                                    if shorter_rule:
                                        delete_learning_rule(shorter_rule[0])
                                    st.success("✅ Règle courte supprimée")
                                    invalidate_audit_cache()
                                    _get_cached_rules_for_audit.clear()
                                    st.rerun(scope="fragment")
                                except Exception as e:
                                    st.error(f"Erreur: {e}")

    # 4. Vague patterns
    if issues.get("vague"):
        vague = issues["vague"]
        with st.expander(f"❓ **{len(vague)} Pattern(s) vague(s)** - Trop courts", expanded=False):
            st.warning("Ces patterns sont très courts et peuvent matcher trop de transactions.")

            for item in vague:
                cols = st.columns([4, 1])
                with cols[0]:
                    st.markdown(f"**`{item['pattern']}`** → {item['category']}")
                with cols[1]:
                    if st.button("🗑️", key=f"audit_del_vague_{item['id']}"):
                        try:
                            delete_learning_rule(item["id"])
                            st.success("✅ Règle supprimée")
                            invalidate_audit_cache()
                            _get_cached_rules_for_audit.clear()
                            st.rerun(scope="fragment")
                        except Exception as e:
                            st.error(f"Erreur: {e}")

    # 5. Stale rules
    if issues.get("stale"):
        stale = issues["stale"]
        with st.expander(f"🕰️ **{len(stale)} Règle(s) ancienne(s)** - +6 mois", expanded=False):
            st.info("Ces règles n'ont pas été utilisées depuis plus de 6 mois.")
            st.caption("Vérifiez si elles sont toujours d'actualité.")

            for item in stale:
                cols = st.columns([4, 1])
                with cols[0]:
                    created = item.get("created_at", "Inconnu")
                    st.markdown(f"**`{item['pattern']}`** ({item['category']}) - Créé: {created}")
                with cols[1]:
                    if st.button("🗑️", key=f"audit_del_stale_{item['id']}"):
                        try:
                            delete_learning_rule(item["id"])
                            st.success("✅ Règle supprimée")
                            invalidate_audit_cache()
                            _get_cached_rules_for_audit.clear()
                            st.rerun(scope="fragment")
                        except Exception as e:
                            st.error(f"Erreur: {e}")


def render_quick_health_score():
    """
    Render a quick health score indicator without running full audit.
    Call this in a header section for a quick overview.
    """
    rules_df = _get_cached_rules_for_audit()

    if rules_df.empty:
        return

    # Use cached score if available
    if "quick_audit_score" not in st.session_state:
        # Run lightweight audit for score only (no detailed analysis)
        try:
            audit = analyze_rules_integrity(rules_df)
            st.session_state["quick_audit_score"] = audit["score"]
        except Exception:
            return

    score = st.session_state.get("quick_audit_score", 100)
    _render_health_indicator(score)
