"""
⚙️ Rules Tab - Configuration de l'automatisation

Regroupe :
- Règles de catégorisation (patterns → catégories)
- Abonnements confirmés (avec gestion)
- Testeur de patterns

Objectif : Un seul endroit pour dire "comment l'app doit automatiser"
"""

import pandas as pd
import streamlit as st

from modules.db.categories import get_categories
from modules.db.recurrence_feedback import delete_feedback, get_all_feedback
from modules.db.rules import add_learning_rule, delete_learning_rule, get_learning_rules
from modules.logger import logger
from modules.ui.feedback import toast_error, toast_info, toast_success
from modules.utils import validate_regex_pattern

# =============================================================================
# RULES TAB RENDERER
# =============================================================================


def render_rules_tab():
    """Render the unified rules configuration tab."""

    st.header("⚙️ Mes règles d'automatisation")
    st.caption(
        "Définissez comment l'application catégorise et traite vos transactions automatiquement."
    )

    st.divider()

    # Sous-navigation par segmented_control (plus moderne que tabs imbriqués)
    if "rules_subtab" not in st.session_state:
        st.session_state.rules_subtab = "📋 Catégorisation"

    subtab = st.segmented_control(
        "Type de règle",
        options=["📋 Catégorisation", "🔁 Abonnements", "🧪 Testeur"],
        default=st.session_state.rules_subtab,
        label_visibility="collapsed",
    )

    if subtab:
        st.session_state.rules_subtab = subtab

    st.divider()

    # Rendu selon le sous-onglet
    if st.session_state.rules_subtab == "📋 Catégorisation":
        _render_categorization_rules()
    elif st.session_state.rules_subtab == "🔁 Abonnements":
        _render_subscriptions_manager()
    else:
        _render_pattern_tester()


def _render_categorization_rules():
    """Render categorization rules management."""

    # Section: Créer une nouvelle règle
    with st.expander("➕ Créer une nouvelle règle", expanded=False):
        _render_create_rule_form()

    st.divider()

    # Section: Liste des règles
    st.subheader("📋 Règles actives")

    rules_df = get_learning_rules()

    if rules_df.empty:
        st.info("""
        📭 Aucune règle de catégorisation.
        
        **Les règles permettent de :**
        - Catégoriser automatiquement les transactions par mot-clé
        - Éviter de refaire la même catégorisation manuellement
        - Apprendre à l'IA vos préférences
        
        *Astuce : Cochez "Mémoriser" lors de la validation des transactions pour créer des règles automatiquement.*
        """)
        return

    # Barre de recherche
    search_col, count_col = st.columns([2, 1])
    with search_col:
        search = st.text_input("🔍 Rechercher une règle", placeholder="Mot-clé ou catégorie...")
    with count_col:
        st.metric("Règles actives", len(rules_df))

    # Filtrer
    if search:
        rules_df = rules_df[
            rules_df["pattern"].str.lower().str.contains(search.lower(), na=False)
            | rules_df["category"].str.lower().str.contains(search.lower(), na=False)
        ]

    if rules_df.empty:
        st.warning("Aucune règle ne correspond à votre recherche.")
        return

    # Affichage en cards
    for _, rule in rules_df.iterrows():
        _render_rule_card(rule)


def _render_create_rule_form():
    """Render form to create a new categorization rule."""
    categories = get_categories()

    with st.form("create_rule_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            pattern = st.text_input(
                "Mot-clé ou pattern",
                placeholder="Ex: UBER, NETFLIX, CARREFOUR...",
                help="Utilisez | pour plusieurs options (UBER|EATS)",
            )

        with col2:
            category = st.selectbox("Catégorie", options=categories)

        # Preview des transactions qui matcheront
        if pattern:
            _render_pattern_preview(pattern)

        submitted = st.form_submit_button(
            "✅ Créer la règle", type="primary", use_container_width=True
        )

        if submitted:
            if not pattern or not pattern.strip():
                toast_error("Veuillez saisir un mot-clé")
                return

            # Validation regex
            is_valid, error = validate_regex_pattern(pattern)
            if not is_valid:
                st.error(f"Pattern invalide : {error}")
                return

            try:
                if add_learning_rule(pattern.strip(), category):
                    toast_success(f"✅ Règle créée : '{pattern}' → {category}")
                    st.rerun()
                else:
                    toast_error("Cette règle existe peut-être déjà")
            except Exception as e:
                logger.error(f"Error creating rule: {e}")
                toast_error(f"Erreur : {e}")


def _render_pattern_preview(pattern: str):
    """Show which transactions would match a pattern."""
    from modules.db.transactions import get_all_transactions

    df = get_all_transactions()
    if df.empty:
        st.caption("📭 Importez des transactions pour voir l'aperçu")
        return

    try:
        import re

        matches = df[df["label"].str.contains(pattern, case=False, na=False, regex=True)]

        if len(matches) > 0:
            st.caption(f"📊 **{len(matches)}** transaction(s) correspondraient à cette règle :")
            with st.expander("Voir les correspondances"):
                for _, tx in matches.head(5).iterrows():
                    st.markdown(
                        f"- `{tx['label'][:50]}` → **{tx.get('category', 'Non catégorisé')}**"
                    )
                if len(matches) > 5:
                    st.caption(f"... et {len(matches) - 5} autres")
        else:
            st.warning("⚠️ Aucune transaction ne correspond à ce pattern actuellement")
    except re.error as e:
        st.error(f"Pattern regex invalide : {e}")


def _render_rule_card(rule: pd.Series):
    """Render a single rule card."""
    with st.container(border=True):
        cols = st.columns([3, 2, 1, 1])

        with cols[0]:
            st.code(rule["pattern"], language="text")

        with cols[1]:
            st.markdown(f"**{rule['category']}**")

        with cols[2]:
            created = rule.get("created_at", "")
            if created:
                if isinstance(created, str):
                    st.caption(f"Créé le {created[:10]}")
                else:
                    st.caption(
                        f"Créé le {created.strftime('%d/%m/%Y') if hasattr(created, 'strftime') else str(created)[:10]}"
                    )

        with cols[3]:
            # Confirmation dialog for delete rule
            confirm_key = f"confirm_delete_rule_{rule['id']}"

            if not st.session_state.get(confirm_key):
                if st.button("🗑️", key=f"del_rule_{rule['id']}", help="Supprimer cette règle"):
                    st.session_state[confirm_key] = True
                    st.rerun()
            else:
                st.warning("Êtes-vous sûr ?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(
                        "Oui, supprimer", key=f"confirm_del_rule_{rule['id']}", type="primary"
                    ):
                        try:
                            if delete_learning_rule(rule["id"]):
                                toast_success("Règle supprimée")
                                del st.session_state[confirm_key]
                                st.rerun()
                            else:
                                toast_error("Erreur lors de la suppression")
                                del st.session_state[confirm_key]
                        except Exception as e:
                            toast_error(f"Erreur : {e}")
                            del st.session_state[confirm_key]
                with col2:
                    if st.button("Annuler", key=f"cancel_del_rule_{rule['id']}"):
                        del st.session_state[confirm_key]
                        st.rerun()


def _render_subscriptions_manager():
    """Render confirmed subscriptions management."""

    st.subheader("🔁 Abonnements confirmés")
    st.caption("Ces paiements récurrents ont été validés par vos soins.")

    # Récupérer les abonnements confirmés
    confirmed = get_all_feedback(status="confirmed")

    if not confirmed:
        st.info("""
        📭 Aucun abonnement confirmé.
        
        **Les abonnements sont détectés automatiquement** lorsque l'IA identifie des paiements réguliers.
        
        Allez dans l'onglet **📥 Inbox** pour valider les abonnements détectés.
        """)
        return

    # KPIs
    total_monthly = sum(_estimate_monthly_amount(s.get("notes", "")) for s in confirmed)

    col1, col2, col3 = st.columns(3)
    col1.metric("Abonnements actifs", len(confirmed))
    col2.metric("Estimation mensuelle", f"{total_monthly:,.2f} €")
    col3.metric("En attente", len(get_all_feedback(status="pending")))

    st.divider()

    # Liste des abonnements
    for sub in confirmed:
        _render_subscription_card(sub)

    # Section: Ajout manuel
    st.divider()
    with st.expander("➕ Ajouter un abonnement manuellement"):
        _render_manual_subscription_form()


def _estimate_monthly_amount(notes: str) -> float:
    """Extract estimated monthly amount from notes."""
    import re

    # Chercher un montant dans les notes (format: "xxx.xx€" ou similaire)
    match = re.search(r"(\d+[.,]?\d*)\s*€", notes)
    if match:
        try:
            return float(match.group(1).replace(",", "."))
        except ValueError:
            pass
    return 0.0


def _render_subscription_card(sub: dict):
    """Render a single subscription card."""
    with st.container(border=True):
        cols = st.columns([3, 2, 2, 1])

        with cols[0]:
            st.markdown(f"**{sub['label_pattern']}**")
            if sub.get("category"):
                st.caption(f"Catégorie : {sub['category']}")

        with cols[1]:
            if sub.get("notes"):
                st.caption(sub["notes"])

        with cols[2]:
            validated_at = sub.get("validated_at", sub.get("created_at", ""))
            if validated_at:
                st.caption(f"Validé le {str(validated_at)[:10]}")

        with cols[3]:
            # Confirmation dialog for delete subscription
            confirm_key = f"confirm_delete_sub_{sub['id']}"

            if not st.session_state.get(confirm_key):
                if st.button("🗑️", key=f"del_sub_{sub['id']}", help="Retirer de mes abonnements"):
                    st.session_state[confirm_key] = True
                    st.rerun()
            else:
                st.warning("Êtes-vous sûr ?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(
                        "Oui, supprimer", key=f"confirm_del_sub_{sub['id']}", type="primary"
                    ):
                        delete_feedback(sub["label_pattern"], sub.get("category"))
                        toast_info("Abonnement retiré")
                        del st.session_state[confirm_key]
                        st.rerun()
                with col2:
                    if st.button("Annuler", key=f"cancel_del_sub_{sub['id']}"):
                        del st.session_state[confirm_key]
                        st.rerun()


def _render_manual_subscription_form():
    """Render form to manually add a subscription."""
    categories = get_categories()

    with st.form("manual_subscription"):
        col1, col2 = st.columns([2, 1])

        with col1:
            label = st.text_input("Nom ou pattern", placeholder="Ex: NETFLIX, SALAIRE...")

        with col2:
            category = st.selectbox(
                "Catégorie",
                options=[""] + categories,
                format_func=lambda x: "Toutes catégories" if x == "" else x,
            )

        col3, col4 = st.columns(2)
        with col3:
            amount = st.number_input("Montant estimé (€)", value=0.0, step=10.0)
        with col4:
            frequency = st.selectbox(
                "Fréquence", options=["Mensuel", "Trimestriel", "Annuel", "Variable"]
            )

        notes = st.text_area(
            "Notes", placeholder="Pourquoi ce paiement est récurrent...", height=80
        )

        submitted = st.form_submit_button(
            "✅ Ajouter comme abonnement", type="primary", use_container_width=True
        )

        if submitted and label:
            from modules.db.recurrence_feedback import set_recurrence_feedback

            full_notes = notes or f"{frequency} - {amount:.2f}€"
            success = set_recurrence_feedback(
                label_pattern=label.upper(),
                is_recurring=True,
                category=category if category else None,
                notes=full_notes,
            )
            if success:
                toast_success(f"✅ '{label}' ajouté à vos abonnements")
                st.rerun()
            else:
                toast_error("Erreur lors de l'ajout")


def _render_pattern_tester():
    """Render pattern tester tool."""
    from modules.db.transactions import get_all_transactions

    st.subheader("🧪 Testeur de patterns")
    st.caption("Testez vos patterns avant de créer une règle.")

    df = get_all_transactions()
    if df.empty:
        st.info("📭 Importez des transactions pour utiliser le testeur.")
        return

    pattern = st.text_input("Pattern à tester", placeholder="Ex: UBER.*TRIP, NETFLIX|SPOTIFY...")

    if not pattern:
        st.info("💡 Entrez un pattern pour voir les résultats")
        return

    # Test du pattern
    is_valid, error = validate_regex_pattern(pattern)

    if not is_valid:
        st.error(f"❌ Pattern invalide : {error}")
        return

    # Recherche des correspondances
    try:
        import re

        matches = df[df["label"].str.contains(pattern, case=False, na=False, regex=True)]

        if matches.empty:
            st.warning("⚠️ Aucune transaction ne correspond à ce pattern")
            return

        st.success(f"✅ **{len(matches)}** transaction(s) trouvée(s)")

        # Affichage des résultats
        with st.expander("Voir les correspondances", expanded=True):
            result_df = matches[["date", "label", "amount", "category"]].copy()
            result_df["amount"] = result_df["amount"].apply(lambda x: f"{x:,.2f} €")
            st.dataframe(result_df, use_container_width=True, hide_index=True)

        # Proposition de création de règle
        st.divider()
        st.markdown("**Créer une règle à partir de ce pattern ?**")

        categories = get_categories()
        col1, col2 = st.columns([2, 1])

        with col1:
            new_category = st.selectbox("Catégorie", options=categories, key="tester_category")

        with col2:
            if st.button("✅ Créer la règle", type="primary", use_container_width=True):
                if add_learning_rule(pattern, new_category):
                    toast_success(f"✅ Règle créée : '{pattern}' → {new_category}")
                    st.rerun()
                else:
                    toast_error("Cette règle existe déjà")

    except re.error as e:
        st.error(f"Erreur regex : {e}")
