import streamlit as st
from modules.db.tags import get_all_tags, remove_tag_from_all_transactions
from modules.db.rules import get_learning_rules, delete_learning_rule
from modules.db.settings import get_internal_transfer_targets, set_internal_transfer_targets
from modules.ui.feedback import (
    toast_success,
    toast_error,
    toast_warning,
    toast_info,
    delete_feedback,
    show_success,
    show_error,
)


def render_tags_rules():
    """
    Render the Tags & Rules tab content.
    Manage tags and auto-categorization learning rules.
    """
    col_tr1, col_tr2 = st.columns([1, 1])

    # --- TAGS ---
    with col_tr1:
        st.header("🏷️ Gestion des Tags")
        st.markdown("Liste des tags utilisés dans vos transactions.")

        all_tags = get_all_tags()
        if len(all_tags) == 0:
            st.info(
                "📭 Aucun tag trouvé. Les tags apparaissent quand vous les ajoutez aux transactions."
            )
        else:
            st.caption(f"{len(all_tags)} tag(s) utilisé(s)")
            with st.container(height=500):
                for tag in all_tags:
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"🔹 **{tag}**")
                    if c2.button(
                        "🗑️",
                        key=f"del_tag_{tag}",
                        help=f"Supprimer le tag '{tag}' de toutes les transactions",
                    ):
                        try:
                            count = remove_tag_from_all_transactions(tag)
                            if count > 0:
                                toast_success(
                                    f"🗑️ Tag '{tag}' supprimé de {count} transaction(s)", icon="🏷️"
                                )
                            else:
                                toast_info(
                                    f"ℹ️ Tag '{tag}' supprimé (aucune transaction affectée)",
                                    icon="🏷️",
                                )
                            st.rerun()
                        except Exception as e:
                            toast_error(
                                f"❌ Erreur suppression tag '{tag}' : {str(e)[:50]}", icon="❌"
                            )

    # --- LEARNING RULES ---
    with col_tr2:
        st.header("🧠 Règles d'apprentissage")
        st.markdown("Associations automatiques (Mot-clé ➔ Catégorie) apprises par le système.")

        rules_df = get_learning_rules()
        if rules_df.empty:
            st.info(
                "📭 Aucune règle apprise. Le système crée des règles quand vous catégorisez des transactions."
            )
        else:
            st.caption(f"{len(rules_df)} règle(s) de catégorisation")
            with st.container(height=500):
                for _, r in rules_df.iterrows():
                    c1, c2, c3 = st.columns([2, 2, 1])
                    c1.markdown(f"**{r['pattern']}**")
                    c2.markdown(f"➔ {r['category']}")
                    if c3.button("🗑️", key=f"del_rule_{r['id']}", help="Supprimer cette règle"):
                        try:
                            delete_learning_rule(r["id"])
                            toast_success(
                                f"🗑️ Règle '{r['pattern']} ➔ {r['category']}' supprimée", icon="🧠"
                            )
                            st.rerun()
                        except Exception as e:
                            error_msg = str(e)
                            if "not found" in error_msg.lower():
                                toast_warning("⚠️ Cette règle n'existe plus", icon="⚠️")
                            else:
                                toast_error(f"❌ Erreur suppression : {error_msg[:50]}", icon="❌")

    # --- INTERNAL TRANSFER TARGETS ---
    st.divider()
    st.header("🔄 Détection des Virements Internes")
    st.markdown(
        """
    Configurez les mots-clés utilisés pour détecter automatiquement les virements internes.
    Ces mots-clés sont recherchés dans les libellés des transactions contenant "VIREMENT".
    """
    )

    with st.expander("ℹ️ Comment ça marche ?", expanded=False):
        st.markdown(
            """
        Lorsqu'une transaction contient un mot-clé de virement (`VIR`, `VIREMENT`, etc.)
        **ET** un de vos mots-clés personnalisés ci-dessous, elle sera automatiquement
        catégorisée comme **Virement Interne**.

        **Exemples de mots-clés :**
        - Noms de membres du foyer : `AURELIEN`, `ELISE`
        - Noms de comptes : `JOINT`, `EPARGNE`, `LDDS`, `LIVRET`
        - Autres identifiants personnels

        **Note de sécurité :** Ces données sont stockées dans votre base de données
        et ne sont plus exposées dans le code source.
        """
        )

    # Get current targets
    current_targets = get_internal_transfer_targets()

    with st.form("internal_transfer_form"):
        st.subheader("Mots-clés actuels")

        # Display current targets with delete buttons
        if current_targets:
            cols_display = st.columns(3)
            for idx, target in enumerate(current_targets):
                with cols_display[idx % 3]:
                    st.text(f"🔹 {target}")
        else:
            st.caption("Aucun mot-clé configuré")

        st.divider()

        # Add new target
        st.subheader("➕ Ajouter un mot-clé")
        new_target = st.text_input(
            "Nouveau mot-clé",
            placeholder="Ex: LIVRET, EPARGNE, etc.",
            help="Le mot-clé sera automatiquement converti en majuscules",
        )

        col_add, col_reset = st.columns([1, 1])

        with col_add:
            add_clicked = st.form_submit_button(
                "➕ Ajouter", type="primary", use_container_width=True
            )

        with col_reset:
            reset_clicked = st.form_submit_button(
                "🔄 Réinitialiser aux valeurs par défaut", use_container_width=True
            )

        if add_clicked:
            if not new_target or not new_target.strip():
                toast_warning("⚠️ Veuillez entrer un mot-clé", icon="✏️")
            else:
                cleaned_target = new_target.strip().upper()
                if cleaned_target in current_targets:
                    toast_warning(f"⚠️ Le mot-clé '{cleaned_target}' existe déjà", icon="🚫")
                elif len(cleaned_target) < 2:
                    toast_warning("⚠️ Le mot-clé doit contenir au moins 2 caractères", icon="📏")
                else:
                    try:
                        updated_targets = current_targets + [cleaned_target]
                        if set_internal_transfer_targets(updated_targets):
                            toast_success(f"✅ Mot-clé '{cleaned_target}' ajouté", icon="🔑")
                            st.rerun()
                        else:
                            show_error("Erreur lors de l'ajout du mot-clé", icon="❌")
                            toast_error("❌ Échec de l'ajout", icon="❌")
                    except Exception as e:
                        toast_error(f"❌ Erreur : {str(e)[:50]}", icon="❌")

        if reset_clicked:
            try:
                default_targets = ["AURELIEN", "DUO", "JOINT", "EPARGNE", "LDDS", "LIVRET", "ELISE"]
                if set_internal_transfer_targets(default_targets):
                    toast_success("✅ Mots-clés réinitialisés aux valeurs par défaut", icon="🔄")
                    st.rerun()
                else:
                    show_error("Erreur lors de la réinitialisation", icon="❌")
                    toast_error("❌ Échec de la réinitialisation", icon="❌")
            except Exception as e:
                toast_error(f"❌ Erreur : {str(e)[:50]}", icon="❌")

    # Delete individual targets
    if current_targets:
        st.subheader("🗑️ Supprimer des mots-clés")
        cols_delete = st.columns(min(len(current_targets), 4))
        deleted_any = False
        for idx, target in enumerate(current_targets):
            with cols_delete[idx % 4]:
                if st.button(
                    f"🗑️ {target}", key=f"del_target_{target}", help=f"Supprimer '{target}'"
                ):
                    try:
                        updated_targets = [t for t in current_targets if t != target]
                        if set_internal_transfer_targets(updated_targets):
                            toast_success(f"🗑️ Mot-clé '{target}' supprimé", icon="🗑️")
                            st.rerun()
                        else:
                            show_error(f"Erreur suppression de '{target}'", icon="❌")
                    except Exception as e:
                        toast_error(f"❌ Erreur : {str(e)[:50]}", icon="❌")
