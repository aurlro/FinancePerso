import streamlit as st
from modules.db.tags import get_all_tags, remove_tag_from_all_transactions
from modules.db.rules import get_learning_rules, delete_learning_rule

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
                        st.success(f"Tag supprimer de {count} transactions.")
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
                        st.success("Règle supprimée.")
                        st.rerun()
