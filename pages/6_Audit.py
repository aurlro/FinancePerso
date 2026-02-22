"""
🕵️ Audit - Diagnostic & Optimisation

Analyse complète de la santé de vos données financières :
règles, transactions, budgets et performance globale.
"""

from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.ai.rules_auditor import analyze_rules_integrity
from modules.db.budgets import get_budgets
from modules.db.categories import get_categories
from modules.db.migrations import init_db
from modules.db.rules import get_learning_rules
from modules.db.transactions import get_all_transactions
from modules.ui import load_css, render_scroll_to_top
from modules.ui.layout import render_app_info

# Page configuration
st.set_page_config(page_title="Audit", page_icon="🕵️", layout="wide")
load_css()
init_db()

st.title("🕵️ Audit & Optimisation")
st.markdown(
    """
Diagnostic complet de vos données financières avec recommandations d'optimisation.
"""
)

# --- NAVIGATION ---
if "audit_active_tab" not in st.session_state:
    st.session_state["audit_active_tab"] = "📊 Dashboard Santé"

# Auto-jump from other pages
jump_to = st.query_params.get("tab")
if jump_to:
    st.session_state["audit_active_tab"] = jump_to

tabs_list = ["📊 Dashboard Santé", "📋 Audit des Règles", "🔍 Qualité des Données"]

selected_tab = st.segmented_control(
    "Navigation",
    tabs_list,
    default=st.session_state["audit_active_tab"],
    key="audit_nav",
    label_visibility="collapsed",
)

if selected_tab and selected_tab != st.session_state["audit_active_tab"]:
    st.session_state["audit_active_tab"] = selected_tab
    st.rerun()

st.divider()

active_tab = st.session_state["audit_active_tab"]

# Load all data
transactions_df = get_all_transactions()
rules_df = get_learning_rules()
budgets_df = get_budgets()
categories = get_categories()

# =============================================================================
# TAB: DASHBOARD SANTÉ GLOBAL
# =============================================================================
if active_tab == "📊 Dashboard Santé":
    st.header("📊 Score de santé global")

    # Calculate health scores
    @st.cache_data(ttl=300)
    def calculate_health_scores():
        scores = {
            "rules": {"score": 100, "status": "✅", "message": "Aucune règle définie"},
            "data": {"score": 100, "status": "✅", "message": "Aucune donnée"},
            "budgets": {"score": 100, "status": "✅", "message": "Aucun budget défini"},
            "completeness": {"score": 100, "status": "✅", "message": "Données complètes"},
        }

        # Rules health
        if not rules_df.empty:
            try:
                audit = analyze_rules_integrity(rules_df)
                scores["rules"] = {
                    "score": audit.get("score", 100),
                    "status": (
                        "✅"
                        if audit.get("score", 0) >= 80
                        else ("⚠️" if audit.get("score", 0) >= 50 else "🚨")
                    ),
                    "message": f"{len(rules_df)} règles analysées",
                    "issues": sum(
                        [
                            len(audit.get("conflicts", [])),
                            len(audit.get("duplicates", [])),
                            len(audit.get("overlaps", [])),
                            len(audit.get("vague", [])),
                        ]
                    ),
                }
            except Exception:
                scores["rules"] = {"score": 0, "status": "❌", "message": "Erreur d'analyse"}

        # Data health
        if not transactions_df.empty:
            total = len(transactions_df)
            validated = len(transactions_df[transactions_df["status"] == "validated"])
            pending = total - validated

            # Score based on validation rate and age
            validation_rate = validated / total if total > 0 else 1

            # Check for old pending transactions
            if "date" in transactions_df.columns:
                transactions_df["date"] = pd.to_datetime(transactions_df["date"])
                old_pending = transactions_df[
                    (transactions_df["status"] != "validated")
                    & (transactions_df["date"] < datetime.now() - timedelta(days=30))
                ]
                old_count = len(old_pending)
            else:
                old_count = 0

            data_score = max(0, min(100, int(validation_rate * 100 - old_count * 5)))

            scores["data"] = {
                "score": data_score,
                "status": "✅" if data_score >= 80 else ("⚠️" if data_score >= 50 else "🚨"),
                "message": f"{validated}/{total} transactions validées",
                "pending": pending,
                "old_pending": old_count,
            }

        # Budgets health
        if not budgets_df.empty:
            active_budgets = len(budgets_df[budgets_df["amount"] > 0])

            if not transactions_df.empty and "date" in transactions_df.columns:
                # Check budget overruns
                today = datetime.now()
                first_day = today.replace(day=1)
                month_tx = transactions_df[transactions_df["date"] >= first_day]

                if not month_tx.empty and "category" in month_tx.columns:
                    spending_by_cat = month_tx.groupby("category")["amount"].sum().to_dict()
                else:
                    spending_by_cat = {}
                budget_map = dict(zip(budgets_df["category"], budgets_df["amount"]))

                overruns = 0
                for cat, budget in budget_map.items():
                    if budget > 0:
                        spent = abs(spending_by_cat.get(cat, 0))
                        if spent > budget:
                            overruns += 1

                budget_score = max(0, 100 - overruns * 20)
                scores["budgets"] = {
                    "score": budget_score,
                    "status": "✅" if budget_score >= 80 else ("⚠️" if budget_score >= 50 else "🚨"),
                    "message": f"{active_budgets} budgets actifs",
                    "overruns": overruns,
                }
            else:
                scores["budgets"] = {
                    "score": 50,
                    "status": "⚠️",
                    "message": f"{active_budgets} budgets mais aucune transaction à analyser",
                }

        # Completeness
        if not transactions_df.empty:
            completeness_issues = 0

            # Check for missing categories
            if "category" in transactions_df.columns:
                uncategorized = len(
                    transactions_df[
                        transactions_df["category"].isna() | (transactions_df["category"] == "")
                    ]
                )
                completeness_issues += uncategorized

            # Check for missing members
            if "member" in transactions_df.columns:
                unassigned = len(
                    transactions_df[
                        transactions_df["member"].isna() | (transactions_df["member"] == "")
                    ]
                )
                completeness_issues += unassigned

            completeness_score = max(0, 100 - completeness_issues)
            scores["completeness"] = {
                "score": completeness_score,
                "status": (
                    "✅"
                    if completeness_score >= 95
                    else ("⚠️" if completeness_score >= 80 else "🚨")
                ),
                "message": f"{completeness_issues} champs manquants",
                "uncategorized": uncategorized if "uncategorized" in dir() else 0,
                "unassigned": unassigned if "unassigned" in dir() else 0,
            }

        # Global score
        global_score = sum(s["score"] for s in scores.values()) // len(scores)

        return scores, global_score

    scores, global_score = calculate_health_scores()

    # Display global score with gauge
    col_gauge, col_details = st.columns([1, 2])

    with col_gauge:
        # Create gauge chart
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=global_score,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Santé Globale"},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 50], "color": "#ffcccc"},
                        {"range": [50, 80], "color": "#ffffcc"},
                        {"range": [80, 100], "color": "#ccffcc"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 80,
                    },
                },
            )
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

        # Status text
        if global_score >= 80:
            st.success("🎉 **Excellente santé** ! Vos données sont bien gérées.")
        elif global_score >= 50:
            st.warning("⚠️ **Santé moyenne** - Des optimisations sont possibles.")
        else:
            st.error("🚨 **Attention** - Plusieurs problèmes nécessitent votre attention.")

    with col_details:
        st.subheader("Détail par catégorie")

        # Display score cards
        cols = st.columns(2)

        metrics = [
            ("📋 Règles", scores["rules"]),
            ("💾 Données", scores["data"]),
            ("🎯 Budgets", scores["budgets"]),
            ("✨ Complétude", scores["completeness"]),
        ]

        for i, (name, data) in enumerate(metrics):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"**{name}** {data['status']}")
                    st.progress(data["score"] / 100, text=f"{data['score']}%")
                    st.caption(data["message"])

    st.divider()

    # Quick actions
    st.header("🚀 Actions recommandées")

    actions = []

    # Data actions
    if scores["data"].get("pending", 0) > 10:
        actions.append(
            {
                "priority": "high",
                "icon": "✅",
                "title": f"Valider {scores['data']['pending']} transactions en attente",
                "description": "Les transactions non validées ne sont pas prises en compte dans les analyses.",
                "action": "Aller à la validation",
                "link": "pages/1_Opérations.py",
            }
        )

    if scores["completeness"].get("uncategorized", 0) > 0:
        actions.append(
            {
                "priority": "high",
                "icon": "🏷️",
                "title": f"Catégoriser {scores['completeness']['uncategorized']} transactions",
                "description": "Des transactions n'ont pas de catégorie assignée.",
                "action": "Voir les transactions",
                "link": "pages/6_Recherche.py",
            }
        )

    # Rules actions
    if scores["rules"].get("issues", 0) > 0:
        actions.append(
            {
                "priority": "medium",
                "icon": "📋",
                "title": f"Corriger {scores['rules']['issues']} problèmes de règles",
                "description": "Conflits, doublons ou patterns trop vagues détectés.",
                "action": "Voir l'audit des règles",
                "link": "?tab=📋+Audit+des+Règles",
            }
        )

    if len(rules_df) == 0 and not transactions_df.empty:
        actions.append(
            {
                "priority": "low",
                "icon": "🤖",
                "title": "Créer des règles de catégorisation",
                "description": "Automatisez la catégorisation pour gagner du temps.",
                "action": "Voir les suggestions",
                "link": "pages/4_Intelligence.py?tab=💡+Suggestions",
            }
        )

    # Budget actions
    if scores["budgets"].get("overruns", 0) > 0:
        actions.append(
            {
                "priority": "high",
                "icon": "🎯",
                "title": f"Ajuster {scores['budgets']['overruns']} budgets dépassés",
                "description": "Vous avez dépassé vos limites ce mois-ci.",
                "action": "Voir les budgets",
                "link": "pages/5_Budgets.py",
            }
        )

    if len(budgets_df) == 0 and not transactions_df.empty:
        actions.append(
            {
                "priority": "low",
                "icon": "💰",
                "title": "Définir vos budgets mensuels",
                "description": "Fixez des limites pour mieux contrôler vos dépenses.",
                "action": "Configurer les budgets",
                "link": "pages/5_Budgets.py",
            }
        )

    # Display actions
    if actions:
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        actions.sort(key=lambda x: priority_order.get(x["priority"], 3))

        for action in actions:
            priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                action["priority"], "⚪"
            )

            with st.expander(
                f"{priority_color} {action['icon']} {action['title']}",
                expanded=(action["priority"] == "high"),
            ):
                st.markdown(action["description"])

                col1, col2 = st.columns([1, 3])
                with col1:
                    if action.get("link"):
                        if action["link"].startswith("?"):
                            if st.button(
                                action["action"],
                                key=f"action_{action['title'][:20]}",
                                type="primary",
                            ):
                                st.session_state["audit_active_tab"] = (
                                    action["link"].replace("?tab=", "").replace("+", " ")
                                )
                                st.rerun()
                        else:
                            st.page_link(action["link"], label=f"→ {action['action']}")
    else:
        st.success("🎉 **Tout est à jour !** Aucune action requise pour le moment.")

# =============================================================================
# TAB: AUDIT DES RÈGLES
# =============================================================================
elif active_tab == "📋 Audit des Règles":
    st.header("📋 Audit des règles de catégorisation")
    st.markdown("Analyse détaillée de la qualité et cohérence de vos règles.")

    if rules_df.empty:
        st.info(
            """
        📭 **Aucune règle définie.**
        
        Les règles permettent de catégoriser automatiquement vos transactions.
        
        **Pour créer vos premières règles :**
        1. Allez dans la page **🧠 Intelligence**
        2. Ouvrez l'onglet **💡 Suggestions**
        3. Créez des règles depuis les suggestions proposées
        """
        )
    else:
        from modules.ui.rules.rule_audit import render_audit_section

        render_audit_section()

# =============================================================================
# TAB: QUALITÉ DES DONNÉES
# =============================================================================
elif active_tab == "🔍 Qualité des Données":
    st.header("🔍 Analyse de la qualité des données")

    if transactions_df.empty:
        st.info("📭 Importez des transactions pour analyser leur qualité.")
    else:
        # Statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total transactions", len(transactions_df))
        with col2:
            validated = len(transactions_df[transactions_df["status"] == "validated"])
            st.metric("Validées", validated)
        with col3:
            pending = len(transactions_df) - validated
            st.metric(
                "En attente",
                pending,
                delta="à traiter" if pending > 0 else None,
                delta_color="inverse",
            )
        with col4:
            if "category" in transactions_df.columns:
                uncategorized = len(
                    transactions_df[
                        transactions_df["category"].isna() | (transactions_df["category"] == "")
                    ]
                )
                st.metric(
                    "Sans catégorie",
                    uncategorized,
                    delta="à catégoriser" if uncategorized > 0 else None,
                    delta_color="inverse",
                )

        st.divider()

        # Data quality checks
        st.subheader("🔍 Vérifications de qualité")

        checks = []

        # Check 1: Duplicates
        if (
            not transactions_df.empty
            and "date" in transactions_df.columns
            and "label" in transactions_df.columns
        ):
            duplicates = transactions_df.groupby(["date", "label", "amount"]).size()
            duplicates = duplicates[duplicates > 1]

            if not duplicates.empty:
                checks.append(
                    {
                        "status": "warning",
                        "title": f"⚠️ {len(duplicates)} doublon(s) potentiel(s)",
                        "description": "Des transactions identiques (même date, libellé, montant) ont été détectées.",
                        "action": "Voir les doublons",
                    }
                )
            else:
                checks.append(
                    {
                        "status": "ok",
                        "title": "✅ Pas de doublons détectés",
                        "description": "Toutes vos transactions semblent uniques.",
                    }
                )

        # Check 2: Missing members
        if "member" in transactions_df.columns:
            unassigned = transactions_df[
                transactions_df["member"].isna() | (transactions_df["member"] == "")
            ]
            if len(unassigned) > 0:
                checks.append(
                    {
                        "status": "info",
                        "title": f"ℹ️ {len(unassigned)} transaction(s) sans membre assigné",
                        "description": "Assigner un membre permet de suivre les dépenses par personne.",
                        "action": "Assigner les membres",
                    }
                )

        # Check 3: Old pending transactions
        if "date" in transactions_df.columns and "status" in transactions_df.columns:
            transactions_df["date"] = pd.to_datetime(transactions_df["date"])
            old_pending = transactions_df[
                (transactions_df["status"] != "validated")
                & (transactions_df["date"] < datetime.now() - timedelta(days=30))
            ]
            if len(old_pending) > 0:
                checks.append(
                    {
                        "status": "warning",
                        "title": f"⚠️ {len(old_pending)} transaction(s) ancienne(s) non validée(s)",
                        "description": "Certaines transactions datent de plus d'un mois et ne sont pas validées.",
                        "action": "Valider maintenant",
                    }
                )

        # Display checks
        for check in checks:
            icon = {"ok": "✅", "warning": "⚠️", "info": "ℹ️"}.get(check["status"], "ℹ️")

            with st.container(border=True):
                st.markdown(f"**{check['title']}**")
                st.caption(check["description"])
                if check.get("action"):
                    st.button(
                        check["action"],
                        key=f"check_{check['title'][:20]}",
                        use_container_width=True,
                    )

st.divider()
render_scroll_to_top()
render_app_info()
