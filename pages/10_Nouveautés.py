import os
import re
from datetime import datetime

import streamlit as st

from modules.db.migrations import init_db
from modules.ui import load_css
from modules.ui.changelog_parser import parse_changelog
from modules.ui.feedback import render_scroll_to_top
from modules.ui.layout import render_app_info
from modules.update import get_update_manager

st.set_page_config(page_title="Nouveautés", page_icon="🎁", layout="wide")
load_css()
init_db()

st.title("🎁 Nouveautés & Mises à jour")

# --- UPDATE SECTION (Admin) ---
with st.expander("🔧 Mettre à jour la documentation (Admin)", expanded=False):
    st.markdown(
        """
    Cette section permet de créer une nouvelle version et de mettre à jour :
    - **CHANGELOG.md** - Historique des versions
    - **AGENTS.md** - Guide pour les assistants IA
    - **modules/constants.py** - Numéro de version
    """
    )

    manager = get_update_manager()
    current_version = manager.get_current_version()

    # Auto-detect changes
    st.subheader("🔍 Détection automatique des changements")

    col_auto1, col_auto2 = st.columns([1, 2])

    with col_auto1:
        auto_detect = st.button(
            "🔍 Analyser les changements", type="secondary", use_container_width=True
        )

    # Initialize session state for detected changes
    if "detected_changes" not in st.session_state:
        st.session_state.detected_changes = None

    if auto_detect:
        with st.spinner("Analyse en cours..."):
            # Try git analysis first, fallback to file scanning
            git_changes = manager.analyze_git_changes()
            # Only fallback to module changes if no git changes at all (committed or uncommitted)
            if (
                not git_changes.get("files_modified")
                and not git_changes.get("has_committed_changes")
                and not git_changes.get("has_uncommitted_changes")
            ):
                git_changes = manager.get_module_changes()
            st.session_state.detected_changes = git_changes
            st.success("✅ Changements détectés !")

    # Show detected changes summary
    if st.session_state.detected_changes:
        changes = st.session_state.detected_changes
        with col_auto2:
            # Show both committed and uncommitted stats
            has_committed = changes.get("has_committed_changes", False)
            has_uncommitted = changes.get("has_uncommitted_changes", False)

            if has_committed and has_uncommitted:
                cols_summary = st.columns(5)
                cols_summary[0].metric("📁 Commits", len(changes.get("committed_files", [])))
                cols_summary[1].metric("💻 Local", len(changes.get("uncommitted_files", [])))
                cols_summary[2].metric("✨ Ajouts", len(changes.get("added", [])))
                cols_summary[3].metric("🐛 Corrections", len(changes.get("fixed", [])))
                cols_summary[4].metric("⚡ Perf", len(changes.get("performance", [])))
            elif has_uncommitted and not has_committed:
                cols_summary = st.columns(4)
                cols_summary[0].metric(
                    "💻 Fichiers locaux", len(changes.get("uncommitted_files", []))
                )
                cols_summary[1].metric("✨ Ajouts", len(changes.get("added", [])))
                cols_summary[2].metric("🐛 Corrections", len(changes.get("fixed", [])))
                cols_summary[3].metric("⚡ Perf", len(changes.get("performance", [])))
            else:
                cols_summary = st.columns(4)
                cols_summary[0].metric("📁 Fichiers", len(changes.get("files_modified", [])))
                cols_summary[1].metric("✨ Ajouts", len(changes.get("added", [])))
                cols_summary[2].metric("🐛 Corrections", len(changes.get("fixed", [])))
                cols_summary[3].metric("⚡ Perf", len(changes.get("performance", [])))

        # Show detailed breakdown if there are uncommitted changes
        if changes.get("has_uncommitted_changes"):
            with st.expander("📋 Détails des changements locaux", expanded=True):
                uncommitted_files = changes.get("uncommitted_files", [])
                uncommitted_status = changes.get("uncommitted_status", {})

                if uncommitted_files:
                    st.markdown("**Fichiers avec modifications locales non commitées :**")
                    for f in sorted(uncommitted_files)[:20]:  # Limit to 20 files
                        status = uncommitted_status.get(f, "modified")
                        status_emoji = {
                            "untracked": "🆕",
                            "staged (added)": "➕",
                            "staged (modified)": "📝",
                            "staged (deleted)": "🗑️",
                            "unstaged (modified)": "✏️",
                            "unstaged (deleted)": "❌",
                            "staged + unstaged changes": "🔄",
                        }.get(status, "📝")
                        st.caption(f"{status_emoji} `{f}` _({status})_")

                    if len(uncommitted_files) > 20:
                        st.caption(f"... et {len(uncommitted_files) - 20} autres fichiers")

                if changes.get("has_committed_changes"):
                    st.divider()
                    st.markdown("**Fichiers modifiés dans les commits :**")
                    committed_files = changes.get("committed_files", [])
                    for f in sorted(committed_files)[:10]:
                        st.caption(f"📦 `{f}`")
                    if len(committed_files) > 10:
                        st.caption(f"... et {len(committed_files) - 10} autres fichiers")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.info(f"Version actuelle : **v{current_version}**")

    with col2:
        # Pre-select bump type based on detected changes
        default_bump_idx = 0  # patch
        if st.session_state.detected_changes:
            detected_bump = st.session_state.detected_changes.get("suggested_bump", "patch")
            default_bump_idx = {"patch": 0, "minor": 1, "major": 2}.get(detected_bump, 0)

        bump_type = st.selectbox(
            "Type de mise à jour",
            options=[
                ("patch", "🔧 Correction (patch)"),
                ("minor", "✨ Fonctionnalité (minor)"),
                ("major", "🚀 Majeure (major)"),
            ],
            format_func=lambda x: x[1],
            index=default_bump_idx,
        )[0]

        new_version = manager.bump_version(current_version, bump_type)
        st.success(f"Nouvelle version : **v{new_version}**")

    # Get pre-filled values from detected changes
    detected = st.session_state.detected_changes or {}
    default_title = detected.get("suggested_title", "")
    default_added = "\n".join([f"- {item}" for item in detected.get("added", [])])
    default_fixed = "\n".join([f"- {item}" for item in detected.get("fixed", [])])
    default_perf = "\n".join([f"- {item}" for item in detected.get("performance", [])])
    default_files = "\n".join(detected.get("files_modified", []))

    # Update form
    with st.form("update_form"):
        update_title = st.text_input(
            "Titre de la mise à jour",
            value=default_title,
            placeholder="Ex: Nouvelle fonctionnalité X - Refonte complète",
            help="Décrivez brièvement le thème principal de cette mise à jour",
        )

        st.subheader("📝 Changements (modifiable)")

        col_added, col_fixed, col_perf = st.columns(3)

        with col_added:
            st.markdown("**✨ Nouveautés**")
            added = st.text_area(
                "Liste (une par ligne)",
                value=default_added,
                placeholder="- Nouvelle fonction X\n- Amélioration Y",
                key="added_changes",
                height=150,
            )

        with col_fixed:
            st.markdown("**🐛 Corrections**")
            fixed = st.text_area(
                "Liste (une par ligne)",
                value=default_fixed,
                placeholder="- Bug Z corrigé\n- Problème W résolu",
                key="fixed_changes",
                height=150,
            )

        with col_perf:
            st.markdown("**⚡ Performance**")
            perf = st.text_area(
                "Liste (une par ligne)",
                value=default_perf,
                placeholder="- Optimisation A\n- Cache B amélioré",
                key="perf_changes",
                height=150,
            )

        st.subheader("📁 Fichiers modifiés")
        files_modified = st.text_area(
            "Liste des fichiers (un par ligne)",
            value=default_files,
            placeholder="modules/nouveau.py\npages/1_Import.py",
            help="Liste des fichiers principaux modifiés dans cette version",
        )

        breaking = st.checkbox("⚠️ Contient des breaking changes", key="checkbox_88")
        breaking_changes = None
        if breaking:
            breaking_changes = st.text_area(
                "Breaking changes (une par ligne)",
                placeholder="- API X modifiée\n- Dépréciation de Y",
            )

        # Add Force Option
        force_update = st.checkbox(
            "Forcer la création (ignorer les doublons)",
            help="Cochez si vous obtenez une erreur de mise à jour identique.",
        )

        submitted = st.form_submit_button(
            "🚀 Créer la mise à jour", type="primary", use_container_width=True
        )

        if submitted:
            if not update_title:
                st.error("❌ Veuillez entrer un titre pour la mise à jour")
            elif not added and not fixed and not perf:
                st.error("❌ Veuillez entrer au moins un changement")
            else:
                # Build changes dict
                changes = {}
                if added.strip():
                    changes["added"] = [line.strip() for line in added.split("\n") if line.strip()]
                if fixed.strip():
                    changes["fixed"] = [line.strip() for line in fixed.split("\n") if line.strip()]
                if perf.strip():
                    changes["performance"] = [
                        line.strip() for line in perf.split("\n") if line.strip()
                    ]

                files_list = (
                    [f.strip() for f in files_modified.split("\n") if f.strip()]
                    if files_modified
                    else []
                )
                breaking_list = (
                    [b.strip() for b in breaking_changes.split("\n") if b.strip()]
                    if breaking_changes
                    else None
                )

                # Create update
                with st.spinner("Mise à jour en cours..."):
                    success, version = manager.create_update(
                        title=update_title,
                        changes=changes,
                        bump_type=bump_type,
                        files_modified=files_list,
                        breaking_changes=breaking_list,
                        force=force_update,
                    )

                if success:
                    st.success(f"✅ Mise à jour v{version} créée avec succès !")
                    st.balloons()

                    # Show what was updated
                    st.markdown("### 📄 Fichiers mis à jour :")
                    st.markdown(f"- **CHANGELOG.md** - Nouvelle entrée v{version}")
                    st.markdown("- **AGENTS.md** - Version et date mises à jour")
                    st.markdown(f'- **modules/constants.py** - APP_VERSION = "{version}"')

                    st.info("📝 N'oubliez pas de commit et push ces changements !")

                    # Refresh the page to show new changelog
                    st.rerun()
                else:
                    # version contains error message when success is False
                    st.error(f"❌ {version}")

# Path to changelog
CHANGELOG_PATH = os.path.join(os.getcwd(), "CHANGELOG.md")

# Parse changelog
versions = parse_changelog(CHANGELOG_PATH)

st.markdown("### 📜 Historique des versions")

if not versions:
    st.info("Aucun historique disponible dans CHANGELOG.md")
else:
    for v in versions:
        with st.container(border=True):
            col_ver, col_content = st.columns([1, 4])
            with col_ver:
                st.markdown(f"### `v{v['version']}`")
                if v["date"]:
                    # Try to format date nicely if possible
                    try:
                        date_obj = datetime.strptime(v["date"], "%Y-%m-%d")
                        formatted_date = date_obj.strftime("%d %B %Y")
                        st.caption(formatted_date)
                    except (ValueError, TypeError):
                        # Fallback to raw date string if parsing fails
                        st.caption(v["date"])

                # Extract main category or subtitle if possible from content
                # (Look for first ### header)
                first_header = re.search(r"### (.*)", v["content"])
                if first_header:
                    st.caption(f"✨ {first_header.group(1)}")

            with col_content:
                st.markdown(v["content"])

        st.markdown(" ")  # Spacer

st.divider()

# --- ROADMAP SECTION ---
st.header("🚀 Roadmap & Évolutions Futures")
st.markdown("Idées et fonctionnalités envisagées pour les versions futures.")

roadmap_tabs = st.tabs(
    ["🔮 Lab Magic Fix", "💡 Propositions", "🔬 R&D", "🎯 Priorisées", "⏸️ En attente"]
)

with roadmap_tabs[0]:
    st.subheader("🔮 Magic Fix Lab : Évolutions 5.x")
    st.info("Stratégies d'optimisation prévues pour le nettoyage et l'enrichissement des données.")

    st.markdown(
        """
    ### 1. Rapprochement Inter-Comptes (Matching)
    - **Description** : Détecte automatiquement les paires Débit/Crédit (virements internes) entre vos comptes.
    - **Priorité** : 🔴 **MUST HAVE**
    - **Status** : ✅ Déployé (v5.1)

    ### 2. Détection des Abonnements Fantômes
    - **Description** : Identifie les prélèvements récurrents mensuels non encore identifiés comme abonnements.
    - **Priorité** : 🟠 **SHOULD HAVE**
    - **Status** : 📋 Planifié (v5.2)

    ### 3. Nettoyage des Bénéficiaires (Normalisation)
    - **Description** : Harmonise les noms des marchands (ex: "McDo 123" -> "McDonald's").
    - **Priorité** : 🔴 **MUST HAVE**
    - **Status** : ✅ Déployé (v5.1)

    ### 4. Ajustement des Dates de Valeur
    - **Description** : Recalage intelligent des transactions de fin de mois pour correspondre au budget réel.
    - **Priorité** : 🔴 **MUST HAVE**
    - **Status** : 📋 Planifié

    ### 5. Détection des Doublons Flous
    - **Description** : Repère les transactions de même montant/date avec des libellés légèrement différents.
    - **Priorité** : 🟠 **SHOULD HAVE**
    - **Status** : 📋 Planifié

    ### 6. Analyse de la Fréquence (Habitudes)
    - **Description** : Marque les marchands visités régulièrement avec un tag "Habitude".
    - **Priorité** : 🟡 **COULD HAVE**
    - **Status** : 💡 Idée

    ### 7. Tagging Géographique
    - **Description** : Extraction automatique des villes (Rennes, Paris...) pour un tag local.
    - **Priorité** : 🟡 **COULD HAVE**
    - **Status** : 💡 Idée

    ### 8. Auto-Tagging de l'Importance
    - **Description** : Signale les transactions aux montants exceptionnels pour une catégorie.
    - **Priorité** : 🟡 **COULD HAVE**
    - **Status** : 💡 Idée

    ### 9. Suggestion de Scission (Split)
    - **Description** : Alerte sur les gros tickets de supermarché nécessitant une ventilation.
    - **Priorité** : 🟡 **COULD HAVE**
    - **Status** : 💡 Idée

    ### 10. Identification du Mode de Paiement
    - **Description** : Détecte si la transaction provient d'Apple Pay ou d'une carte virtuelle.
    - **Priorité** : ⚪ **WON'T HAVE** (pour l'instant)
    - **Status** : ⏸️ Reporté
    """
    )

with roadmap_tabs[1]:
    st.subheader("💡 Idées proposées")
    st.markdown(
        """
    ### Comparatif anonymisé
    - **Description** : "Vous dépensez 20% de plus que la moyenne des utilisateurs"
    - **Use case** : Donner une perspective comparative sur les habitudes de dépense
    - **Complexité** : Moyenne (nécessite agrégation de données anonymisées)
    - **Statut** : 💭 Idée
    
    ### Prédictions ML avancées
    - **Description** : Utilisation de modèles LSTM pour prédire les dépenses futures
    - **Use case** : Anticiper les dépassements de budget avant qu'ils n'arrivent
    - **Complexité** : Élevée (besoin de données historiques conséquentes)
    - **Statut** : 💭 Idée
    
    ### Assistant vocal
    - **Description** : "Combien puis-je dépenser ce week-end ?"
    - **Use case** : Interaction mains-libres avec l'assistant financier
    - **Complexité** : Moyenne (intégration STT/TTS)
    - **Statut** : 💭 Idée
    """
    )

with roadmap_tabs[1]:
    st.subheader("🔬 En recherche & développement")
    st.markdown(
        """
    ### Intégration bancaire temps réel
    - **Description** : Alertes en temps réel via webhook bancaire
    - **Use case** : Notification instantanée lors d'un paiement
    - **Complexité** : Élevée (nécessite partenariats bancaires)
    - **Statut** : 🔬 R&D
    
    ### Détection de fraude par IA
    - **Description** : Analyse des patterns pour détecter transactions suspectes
    - **Use case** : Alerte si une transaction inhabituelle est détectée
    - **Complexité** : Élevée
    - **Statut** : 🔬 R&D
    """
    )

with roadmap_tabs[2]:
    st.subheader("🎯 Priorisées pour développement")
    st.info("Les fonctionnalités ici sont celles qui seront développées en priorité.")
    st.markdown(
        """
    *Aucune fonctionnalité priorisée actuellement. Les évolutions se font au fil des besoins.*
    """
    )

with roadmap_tabs[3]:
    st.subheader("⏸️ En attente / Reportées")
    st.markdown(
        """
    Ces fonctionnalités ont été proposées mais sont actuellement reportées :
    
    | Fonctionnalité | Raison du report |
    |----------------|------------------|
    | Comparatif anonymisé | Complexité d'agrégation des données |
    | Prédictions ML LSTM | Besoin de plus de données historiques |
    | Assistant vocal | Priorité moindre vs features core |
    | Webhook bancaire | Dépendance externe (banques) |
    """
    )

st.divider()

render_scroll_to_top()
render_app_info()
