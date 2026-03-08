"""
⚙️ Rules Tab - Moteur de règles de catégorisation

Regroupe :
- 📋 Règles de catégorisation (patterns → catégories) avec édition inline
- 📊 Statistiques et performance
- ⚠️ Détection de conflits
- 🧪 Testeur de patterns avancé
- 💾 Import/Export

Objectif : Un moteur complet pour gérer l'automatisation de la catégorisation.
"""

import json
import re

import pandas as pd
import streamlit as st

from modules.db.categories import get_categories
from modules.db.recurrence_feedback import delete_feedback, get_all_feedback
from modules.db.rules import (
    add_learning_rule,
    bulk_delete_rules,
    delete_learning_rule,
    export_rules_to_json,
    find_rule_conflicts,
    get_all_rules_statistics,
    get_learning_rules,
    get_rules_performance_metrics,
    import_rules_from_json,
    test_rule_against_transactions,
    update_learning_rule,
)
from modules.logger import logger
from modules.ui.feedback import toast_error, toast_info, toast_success
from modules.utils import validate_regex_pattern

# =============================================================================
# RULES TAB RENDERER
# =============================================================================


def render_rules_tab():
    """Render the unified rules configuration tab with rule engine."""

    st.header("⚙️ Moteur de règles de catégorisation")
    st.caption(
        "Créez, testez et gérez les règles qui catégorisent automatiquement vos transactions."
    )

    # Metrics globales
    _render_rules_metrics()

    st.divider()

    # Alertes de conflits
    _render_conflict_alerts()

    # Sous-navigation
    if "rules_subtab" not in st.session_state:
        st.session_state.rules_subtab = "📋 Mes règles"

    subtab = st.segmented_control(
        "Type de règle",
        options=["📋 Mes règles", "📊 Statistiques", "🧪 Testeur avancé", "💾 Import/Export"],
        default=st.session_state.rules_subtab,
        label_visibility="collapsed",
    )

    if subtab:
        st.session_state.rules_subtab = subtab

    st.divider()

    # Rendu selon le sous-onglet
    if st.session_state.rules_subtab == "📋 Mes règles":
        _render_categorization_rules()
    elif st.session_state.rules_subtab == "📊 Statistiques":
        _render_rules_statistics()
    elif st.session_state.rules_subtab == "🧪 Testeur avancé":
        _render_advanced_tester()
    else:
        _render_import_export()


def _render_rules_metrics():
    """Render global metrics for rules."""
    metrics = get_rules_performance_metrics()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📝 Règles actives", metrics["total_rules"])

    with col2:
        st.metric("🏷️ Catégories couvertes", metrics["categories_covered"])

    with col3:
        st.metric("⭐ Priorité moyenne", f"{metrics['avg_priority']:.1f}")

    with col4:
        if metrics["conflicts"] > 0:
            st.metric("⚠️ Conflits détectés", metrics["conflicts"], delta="Action requise", delta_color="inverse")
        else:
            st.metric("✅ Conflits", 0)


def _render_conflict_alerts():
    """Render alerts for rule conflicts."""
    conflicts = find_rule_conflicts()

    if not conflicts:
        return

    with st.container(border=True):
        st.markdown("### ⚠️ Conflits détectés")
        st.caption("Ces règles peuvent créer des comportements imprévisibles.")

        for conflict in conflicts:
            if conflict["type"] == "same_pattern":
                with st.expander(f"🔴 Pattern dupliqué : `{conflict['pattern'][:40]}`"):
                    st.warning(f"Le pattern apparaît dans {len(conflict['categories'])} catégories différentes")
                    for rule in conflict["rules"]:
                        st.markdown(f"- **{rule['category']}** (ID: {rule['id']})")

            elif conflict["type"] == "overlapping":
                with st.expander(f"🟡 Patterns se chevauchant"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**`{conflict['pattern1'][:30]}`** → {conflict['category1']}")
                    with col2:
                        st.markdown(f"**`{conflict['pattern2'][:30]}`** → {conflict['category2']}")


# =============================================================================
# CATEGORIZATION RULES MANAGEMENT
# =============================================================================


def _render_categorization_rules():
    """Render categorization rules management with inline editing."""

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

    # Barre de recherche et filtres
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])

    with filter_col1:
        search = st.text_input("🔍 Rechercher", placeholder="Mot-clé ou catégorie...")

    with filter_col2:
        categories = ["Toutes"] + list(rules_df["category"].unique())
        category_filter = st.selectbox("Catégorie", options=categories)

    with filter_col3:
        st.metric("Total", len(rules_df))

    # Filtrer
    filtered_df = rules_df.copy()
    if search:
        filtered_df = filtered_df[
            filtered_df["pattern"].str.lower().str.contains(search.lower(), na=False)
            | filtered_df["category"].str.lower().str.contains(search.lower(), na=False)
        ]
    if category_filter != "Toutes":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]

    if filtered_df.empty:
        st.warning("Aucune règle ne correspond à vos critères.")
        return

    # Actions en masse
    if len(filtered_df) > 1:
        with st.expander("🗑️ Actions en masse"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.caption("Sélectionnez les règles à supprimer")
            with col2:
                if st.button("⚠️ Supprimer toutes les règles visibles", type="secondary"):
                    st.session_state["bulk_delete_pending"] = filtered_df["id"].tolist()
                    st.rerun()

    # Gestion de la suppression en masse
    if st.session_state.get("bulk_delete_pending"):
        rule_ids = st.session_state["bulk_delete_pending"]
        st.warning(f"Êtes-vous sûr de vouloir supprimer {len(rule_ids)} règles ?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Oui, supprimer tout", type="primary"):
                deleted, errors = bulk_delete_rules(rule_ids)
                toast_success(f"✅ {deleted} règles supprimées")
                if errors:
                    toast_error(f"❌ {errors} erreurs")
                del st.session_state["bulk_delete_pending"]
                st.rerun()
        with col2:
            if st.button("Annuler"):
                del st.session_state["bulk_delete_pending"]
                st.rerun()

    # Affichage en cards avec édition inline
    for _, rule in filtered_df.iterrows():
        _render_rule_card_editable(rule)


def _render_create_rule_form():
    """Render form to create a new categorization rule."""
    categories = get_categories()

    with st.form("create_rule_form"):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            pattern = st.text_input(
                "Pattern regex",
                placeholder="Ex: UBER, NETFLIX|SPOTIFY, CARREFOUR.*MAGASIN...",
                help="Expression régulière. Utilisez | pour 'OU', .* pour 'n'importe quoi'",
            )

        with col2:
            category = st.selectbox("Catégorie", options=categories)

        with col3:
            priority = st.number_input("Priorité", min_value=1, max_value=10, value=1,
                                       help="Plus la valeur est haute, plus la règle est prioritaire")

        # Preview des transactions qui matcheront
        if pattern:
            _render_pattern_preview_live(pattern)

        submitted = st.form_submit_button(
            "✅ Créer la règle", type="primary", use_container_width=True
        )

        if submitted:
            if not pattern or not pattern.strip():
                toast_error("Veuillez saisir un pattern")
                return

            # Validation regex
            is_valid, error = validate_regex_pattern(pattern)
            if not is_valid:
                st.error(f"Pattern invalide : {error}")
                return

            try:
                if add_learning_rule(pattern.strip(), category, priority):
                    toast_success(f"✅ Règle créée : '{pattern}' → {category}")
                    st.rerun()
                else:
                    toast_error("Cette règle existe peut-être déjà")
            except Exception as e:
                logger.error(f"Error creating rule: {e}")
                toast_error(f"Erreur : {e}")


def _render_pattern_preview_live(pattern: str):
    """Show live preview of pattern matching."""
    matches = test_rule_against_transactions(pattern, limit=5)

    if matches.empty:
        st.caption("⚠️ Aucune transaction ne correspond actuellement")
    else:
        st.caption(f"📊 **{len(matches)}** transaction(s) correspondraient :")
        preview_df = matches[["date", "label", "amount", "category"]].head(3)
        preview_df["amount"] = preview_df["amount"].apply(lambda x: f"{x:,.2f} €")
        st.dataframe(preview_df, use_container_width=True, hide_index=True)


def _render_rule_card_editable(rule: pd.Series):
    """Render a rule card with inline editing capabilities."""
    rule_id = rule["id"]

    # Clé pour mode édition
    edit_key = f"edit_rule_{rule_id}"

    with st.container(border=True):
        if st.session_state.get(edit_key):
            # Mode édition
            _render_rule_editor(rule)
        else:
            # Mode affichage
            _render_rule_display(rule)


def _render_rule_display(rule: pd.Series):
    """Render rule in display mode."""
    cols = st.columns([3, 2, 1, 1, 1])

    with cols[0]:
        # Pattern avec highlight syntaxique simple
        pattern = rule["pattern"]
        st.code(pattern, language="text")

    with cols[1]:
        st.markdown(f"**{rule['category']}**")

    with cols[2]:
        priority = rule.get("priority", 1)
        st.caption(f"⭐ Priorité: {priority}")

    with cols[3]:
        created = rule.get("created_at", "")
        if created:
            date_str = str(created)[:10] if not hasattr(created, 'strftime') else created.strftime('%d/%m/%Y')
            st.caption(f"📅 {date_str}")

    with cols[4]:
        # Boutons d'action
        action_cols = st.columns(2)

        with action_cols[0]:
            if st.button("✏️", key=f"edit_btn_{rule['id']}", help="Modifier"):
                st.session_state[f"edit_rule_{rule['id']}"] = True
                st.rerun()

        with action_cols[1]:
            # Confirmation pour suppression
            confirm_key = f"confirm_delete_rule_{rule['id']}"

            if not st.session_state.get(confirm_key):
                if st.button("🗑️", key=f"del_rule_{rule['id']}", help="Supprimer"):
                    st.session_state[confirm_key] = True
                    st.rerun()
            else:
                if st.button("✓", key=f"confirm_del_{rule['id']}", help="Confirmer"):
                    try:
                        if delete_learning_rule(rule["id"]):
                            toast_success("Règle supprimée")
                            del st.session_state[confirm_key]
                            st.rerun()
                        else:
                            toast_error("Erreur lors de la suppression")
                    except Exception as e:
                        toast_error(f"Erreur : {e}")


def _render_rule_editor(rule: pd.Series):
    """Render rule in edit mode."""
    rule_id = rule["id"]
    categories = get_categories()

    with st.form(f"edit_form_{rule_id}"):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            new_pattern = st.text_input(
                "Pattern",
                value=rule["pattern"],
                key=f"pattern_{rule_id}"
            )

        with col2:
            new_category = st.selectbox(
                "Catégorie",
                options=categories,
                index=categories.index(rule["category"]) if rule["category"] in categories else 0,
                key=f"category_{rule_id}"
            )

        with col3:
            current_priority = rule.get("priority", 1)
            new_priority = st.number_input(
                "Priorité",
                min_value=1,
                max_value=10,
                value=int(current_priority),
                key=f"priority_{rule_id}"
            )

        # Validation du pattern
        if new_pattern:
            is_valid, error = validate_regex_pattern(new_pattern)
            if not is_valid:
                st.error(f"Pattern invalide : {error}")

        col_save, col_cancel = st.columns(2)

        with col_save:
            submitted = st.form_submit_button("💾 Sauvegarder", type="primary", use_container_width=True)
            if submitted:
                is_valid, error = validate_regex_pattern(new_pattern)
                if not is_valid:
                    toast_error(f"Pattern invalide : {error}")
                else:
                    success = update_learning_rule(
                        rule_id,
                        pattern=new_pattern,
                        category=new_category,
                        priority=new_priority
                    )
                    if success:
                        toast_success("✅ Règle mise à jour")
                        st.session_state[f"edit_rule_{rule_id}"] = False
                        st.rerun()
                    else:
                        toast_error("Erreur lors de la mise à jour")

        with col_cancel:
            if st.form_submit_button("❌ Annuler", use_container_width=True):
                st.session_state[f"edit_rule_{rule_id}"] = False
                st.rerun()


# =============================================================================
# STATISTICS TAB
# =============================================================================


def _render_rules_statistics():
    """Render statistics about rule usage."""
    st.subheader("📊 Statistiques d'utilisation")

    stats_df = get_all_rules_statistics()

    if stats_df.empty:
        st.info("📭 Aucune statistique disponible. Importez des transactions pour voir les statistiques.")
        return

    # KPIs
    total_matches = stats_df["match_count"].sum()
    active_rules = len(stats_df[stats_df["match_count"] > 0])

    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 Total matches", f"{total_matches:,}")
    col2.metric("✅ Règles actives", active_rules)
    col3.metric("📉 Règles inactives", len(stats_df) - active_rules)

    st.divider()

    # Tableau détaillé
    st.markdown("### Détails par règle")

    # Formatage
    display_df = stats_df.copy()
    display_df["confidence"] = display_df["confidence"].apply(lambda x: f"{x:.0%}")
    display_df["last_match_date"] = display_df["last_match_date"].fillna("Jamais")

    st.dataframe(
        display_df[["pattern", "category", "match_count", "confidence", "last_match_date"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "pattern": "Pattern",
            "category": "Catégorie",
            "match_count": "Matches",
            "confidence": "Confiance",
            "last_match_date": "Dernier match"
        }
    )

    # Graphique
    if len(stats_df) > 0:
        st.divider()
        st.markdown("### 📈 Répartition des matches")

        chart_data = stats_df[stats_df["match_count"] > 0].sort_values("match_count", ascending=False)
        if not chart_data.empty:
            st.bar_chart(
                chart_data.set_index("pattern")["match_count"],
                use_container_width=True
            )


# =============================================================================
# ADVANCED TESTER TAB
# =============================================================================


def _render_advanced_tester():
    """Render advanced pattern tester with live highlighting."""
    st.subheader("🧪 Testeur de patterns avancé")
    st.caption("Testez vos regex avec highlighting et analyse détaillée.")

    # Zone de test
    col1, col2 = st.columns([1, 1])

    with col1:
        pattern = st.text_area(
            "Pattern regex",
            placeholder="Ex: (UBER|EATS).*TRIP|COURSE",
            height=80,
            help="Entrez votre expression régulière ici"
        )

    with col2:
        test_label = st.text_area(
            "Libellé de test",
            placeholder="Ex: UBER TRIP HELP12345",
            height=80,
            help="Entrez un libellé pour tester le pattern"
        )

    # Test en direct
    if pattern and test_label:
        _render_live_test(pattern, test_label)

    # Test sur la base de données
    st.divider()
    st.markdown("### 🔍 Test sur vos transactions")

    if pattern:
        _render_database_test(pattern)
    else:
        st.info("💡 Entrez un pattern ci-dessus pour tester sur vos transactions")

    # Aide regex
    with st.expander("📖 Aide regex rapide"):
        _render_regex_cheatsheet()


def _render_live_test(pattern: str, test_label: str):
    """Render live test result with highlighting."""
    is_valid, error = validate_regex_pattern(pattern)

    if not is_valid:
        st.error(f"❌ Pattern invalide : {error}")
        return

    try:
        compiled = re.compile(pattern, re.IGNORECASE)
        match = compiled.search(test_label)

        if match:
            st.success("✅ MATCH !")

            # Highlight du match
            start, end = match.span()
            highlighted = f"{test_label[:start]}**`{test_label[start:end]}`**{test_label[end:]}"
            st.markdown(f"Résultat : {highlighted}")

            # Détails du match
            with st.expander("Détails du match"):
                st.json({
                    "position": f"{start}-{end}",
                    "matched_text": match.group(),
                    "groups": match.groups() if match.groups() else None
                })
        else:
            st.warning("❌ Pas de match")

    except re.error as e:
        st.error(f"Erreur regex : {e}")


def _render_database_test(pattern: str):
    """Render test results against database."""
    is_valid, error = validate_regex_pattern(pattern)

    if not is_valid:
        st.error(f"Pattern invalide : {error}")
        return

    matches = test_rule_against_transactions(pattern, limit=50)

    if matches.empty:
        st.warning("⚠️ Aucune transaction ne correspond à ce pattern")
        return

    st.success(f"✅ **{len(matches)}** transaction(s) trouvée(s)")

    # Affichage avec highlight
    st.markdown("#### Résultats")

    for _, tx in matches.head(10).iterrows():
        label = tx["label"]
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            match = compiled.search(label)

            if match:
                start, end = match.span()
                highlighted_label = f"{label[:start]}**`{label[start:end]}`**{label[end:]}"
            else:
                highlighted_label = label
        except:
            highlighted_label = label

        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"{highlighted_label}")
        with col2:
            st.caption(f"{tx['amount']:,.2f} €")
        with col3:
            st.caption(f"{tx.get('category', 'Non catégorisé')}")

    if len(matches) > 10:
        st.caption(f"... et {len(matches) - 10} autres")

    # Création rapide de règle
    st.divider()
    categories = get_categories()
    col1, col2 = st.columns([2, 1])

    with col1:
        new_category = st.selectbox("Catégorie", options=categories, key="tester_cat")

    with col2:
        if st.button("✅ Créer une règle", type="primary", use_container_width=True):
            if add_learning_rule(pattern, new_category):
                toast_success(f"✅ Règle créée : '{pattern}' → {new_category}")
                st.rerun()
            else:
                toast_error("Erreur lors de la création")


def _render_regex_cheatsheet():
    """Render regex cheat sheet."""
    cheatsheet = {
        "Basiques": {
            "`ABC`": "Match exact 'ABC'",
            "`ABC|DEF`": "Match 'ABC' OU 'DEF'",
            "`^ABC`": "Commence par 'ABC'",
            "`ABC$`": "Finit par 'ABC'",
        },
        "Quantifieurs": {
            "`A*`": "0 ou plusieurs A",
            "`A+`": "1 ou plusieurs A",
            "`A?`": "0 ou 1 A (optionnel)",
            "`.*`": "N'importe quoi",
        },
        "Classes": {
            "`[ABC]`": "Un caractère parmi A, B, C",
            "`[0-9]`": "Un chiffre",
            "`\\d`": "Un chiffre (équivalent)",
            "`\\s`": "Un espace",
        },
        "Groupes": {
            "`(ABC)`": "Groupe capturant",
            "`(?:ABC)`": "Groupe non-capturant",
        },
        "Exemples": {
            "`UBER|EATS`": "Match UBER ou EATS",
            "`NETFLIX.*\\d+`": "NETFLIX suivi de chiffres",
            "`CARREFOUR.*(MARKET|CITY)`": "CARREFOUR suivi de MARKET ou CITY",
        }
    }

    for section, patterns in cheatsheet.items():
        st.markdown(f"**{section}**")
        for pattern, desc in patterns.items():
            st.markdown(f"- {pattern} : {desc}")


# =============================================================================
# IMPORT/EXPORT TAB
# =============================================================================


def _render_import_export():
    """Render import/export functionality."""
    st.subheader("💾 Import / Export")

    col1, col2 = st.columns(2)

    # Export
    with col1:
        with st.container(border=True):
            st.markdown("### 📤 Export")
            st.caption("Exportez vos règles pour les sauvegarder ou les partager.")

            export_data = export_rules_to_json()

            st.download_button(
                label="⬇️ Télécharger les règles (JSON)",
                data=export_data,
                file_name=f"finance_rules_export_{pd.Timestamp.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )

            with st.expander("Voir le contenu"):
                st.code(export_data, language="json")

    # Import
    with col2:
        with st.container(border=True):
            st.markdown("### 📥 Import")
            st.caption("Importez des règles depuis un fichier JSON.")

            uploaded_file = st.file_uploader(
                "Choisir un fichier JSON",
                type=["json"],
                key="rules_import"
            )

            overwrite = st.checkbox("Écraser les règles existantes", value=False)

            if uploaded_file is not None:
                try:
                    content = uploaded_file.read().decode("utf-8")
                    preview = json.loads(content)

                    st.caption(f"📄 {len(preview)} règle(s) trouvée(s)")

                    if st.button("✅ Importer", type="primary", use_container_width=True):
                        imported, skipped = import_rules_from_json(content, overwrite)
                        toast_success(f"✅ {imported} règles importées")
                        if skipped:
                            toast_info(f"ℹ️ {skipped} ignorées (doublons)")
                        st.rerun()

                except json.JSONDecodeError:
                    st.error("❌ Fichier JSON invalide")
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")


# =============================================================================
# SUBSCRIPTIONS MANAGER (Legacy - kept for compatibility)
# =============================================================================


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
