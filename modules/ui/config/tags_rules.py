import streamlit as st
from modules.db.tags import get_all_tags, remove_tag_from_all_transactions
from modules.db.rules import get_learning_rules, delete_learning_rule
from modules.db.settings import get_internal_transfer_targets, set_internal_transfer_targets

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
            st.info("Aucun tag trouvé.")
        else:
            with st.container(height=500):
                for tag in all_tags:
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"🔹 **{tag}**")
                    if c2.button("🗑️", key=f"del_tag_{tag}", help=f"Supprimer le tag '{tag}' de toutes les transactions"):
                        count = remove_tag_from_all_transactions(tag)
                        st.toast(f"✅ Tag supprimé de {count} tx", icon="🏷️")
                        st.rerun()

    # --- LEARNING RULES ---
    with col_tr2:
        st.header("🧠 Règles d'apprentissage")
        st.markdown("Associations automatiques (Mot-clé ➔ Catégorie) apprises par le système.")
        
        rules_df = get_learning_rules()
        if rules_df.empty:
            st.info("Aucune règle apprise pour l'instant.")
        else:
             with st.container(height=500):
                for _, r in rules_df.iterrows():
                    c1, c2, c3 = st.columns([2, 2, 1])
                    c1.markdown(f"**{r['pattern']}**")
                    c2.markdown(f"➔ {r['category']}")
                    if c3.button("🗑️", key=f"del_rule_{r['id']}"):
                        delete_learning_rule(r['id'])
                        st.toast("✅ Règle supprimée", icon="🗑️")
                        st.rerun()

    # --- INTERNAL TRANSFER TARGETS ---
    st.divider()
    st.header("🔄 Détection des Virements Internes")
    st.markdown("""
    Configurez les mots-clés utilisés pour détecter automatiquement les virements internes.
    Ces mots-clés sont recherchés dans les libellés des transactions contenant "VIREMENT".
    """)

    with st.expander("ℹ️ Comment ça marche ?", expanded=False):
        st.markdown("""
        Lorsqu'une transaction contient un mot-clé de virement (`VIR`, `VIREMENT`, etc.)
        **ET** un de vos mots-clés personnalisés ci-dessous, elle sera automatiquement
        catégorisée comme **Virement Interne**.

        **Exemples de mots-clés :**
        - Noms de membres du foyer : `AURELIEN`, `ELISE`
        - Noms de comptes : `JOINT`, `EPARGNE`, `LDDS`, `LIVRET`
        - Autres identifiants personnels

        **Note de sécurité :** Ces données sont maintenant stockées dans votre base de données
        et ne sont plus exposées dans le code source.
        """)

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

        st.divider()

        # Add new target
        st.subheader("Ajouter un mot-clé")
        new_target = st.text_input(
            "Nouveau mot-clé",
            placeholder="Ex: LIVRET, EPARGNE, etc.",
            help="Le mot-clé sera automatiquement converti en majuscules"
        )

        col_add, col_reset = st.columns([1, 1])

        with col_add:
            add_clicked = st.form_submit_button("➕ Ajouter", type="primary")

        with col_reset:
            reset_clicked = st.form_submit_button("🔄 Réinitialiser aux valeurs par défaut")

        if add_clicked and new_target:
            cleaned_target = new_target.strip().upper()
            if cleaned_target and cleaned_target not in current_targets:
                updated_targets = current_targets + [cleaned_target]
                if set_internal_transfer_targets(updated_targets):
                    st.success(f"✅ Mot-clé '{cleaned_target}' ajouté !")
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de l'ajout")
            elif cleaned_target in current_targets:
                st.warning(f"⚠️ Le mot-clé '{cleaned_target}' existe déjà")
            else:
                st.warning("⚠️ Veuillez entrer un mot-clé valide")

        if reset_clicked:
            default_targets = ["AURELIEN", "DUO", "JOINT", "EPARGNE", "LDDS", "LIVRET", "ELISE"]
            if set_internal_transfer_targets(default_targets):
                st.success("✅ Réinitialisé aux valeurs par défaut")
                st.rerun()
            else:
                st.error("❌ Erreur lors de la réinitialisation")

    # Delete individual targets
    if current_targets:
        st.subheader("Supprimer des mots-clés")
        cols_delete = st.columns(min(len(current_targets), 3))
        for idx, target in enumerate(current_targets):
            with cols_delete[idx % 3]:
                if st.button(f"🗑️ {target}", key=f"del_target_{target}"):
                    updated_targets = [t for t in current_targets if t != target]
                    if set_internal_transfer_targets(updated_targets):
                        st.toast(f"✅ Mot-clé '{target}' supprimé", icon="🗑️")
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de la suppression")
