import streamlit as st
import os
import pandas as pd
import shutil
import sqlite3
from modules.ui import load_css
from modules.data_manager import get_members, add_member, delete_member, init_db, DB_PATH, get_available_months, get_categories_df, add_category, delete_category, update_category_emoji, update_category_fixed, get_member_mappings_df, add_member_mapping, delete_member_mapping

# Page Setup
st.set_page_config(page_title="Configuration", page_icon="⚙️")
load_css()
init_db() # Ensure tables exist

st.title("⚙️ Configuration")

# TABS
tab_api, tab_members, tab_cats, tab_data = st.tabs(["🔑 API & Services", "🏠 Foyer & Membres", "🏷️ Catégories", "💾 Données & Danger"])

# --- TAB 1: API ---
with tab_api:
    st.header("🤖 Cerveau IA")
    st.markdown("Choisissez quel moteur d'intelligence artificielle pilote votre assistant.")
    
    # helper to read env
    def load_env_vars():
        vars = {}
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        vars[k] = v
        return vars

    env_vars = load_env_vars()
    
    # Provider Selection
    PROVIDERS = ["Gemini", "Ollama", "DeepSeek", "OpenAI"]
    current_provider = env_vars.get("AI_PROVIDER", "Gemini").capitalize()
    if current_provider not in PROVIDERS:
        current_provider = "Gemini"
        
    selected_provider = st.selectbox("Fournisseur IA", PROVIDERS, index=PROVIDERS.index(current_provider))
    
    st.divider()
    
    # Form based on selection
    with st.form("ai_config"):
        new_env = env_vars.copy()
        new_env["AI_PROVIDER"] = selected_provider.lower()
        
        if selected_provider == "Gemini":
            st.info("Le modèle standard : Rapide, performant et gratuit/pas cher.")
            val = st.text_input("Clé API Google Gemini", value=env_vars.get("GEMINI_API_KEY", ""), type="password")
            new_env["GEMINI_API_KEY"] = val
            
        elif selected_provider == "Ollama":
            st.info("🔒 100% Local & Privé. Assurez-vous qu'Ollama tourne sur votre machine.")
            url = st.text_input("URL du serveur Ollama", value=env_vars.get("OLLAMA_URL", "http://localhost:11434"))
            new_env["OLLAMA_URL"] = url
            # Model selection could be dynamic here but let's stick to env var for simplicity or hardcode defaults in manager
            # Maybe add a model name field?
            
        elif selected_provider == "DeepSeek":
            st.info("Performance coût/efficacité redoutable.")
            val = st.text_input("Clé API DeepSeek", value=env_vars.get("DEEPSEEK_API_KEY", ""), type="password")
            new_env["DEEPSEEK_API_KEY"] = val
            
        elif selected_provider == "OpenAI":
            st.info("Le standard de l'industrie (GPT-4 / GPT-3.5).")
            val = st.text_input("Clé API OpenAI", value=env_vars.get("OPENAI_API_KEY", ""), type="password")
            new_env["OPENAI_API_KEY"] = val
            
        # Common: Model Name Override
        st.subheader("Options Avancées")
        model_val = st.text_input("Nom du modèle (laisser vide pour défaut)", value=env_vars.get("AI_MODEL_NAME", ""), help="Ex: llama3, gpt-4o, gemini-1.5-pro")
        new_env["AI_MODEL_NAME"] = model_val

        if st.form_submit_button("Sauvegarder et Appliquer", type="primary"):
            # Write .env
            with open(".env", "w") as f:
                for k, v in new_env.items():
                    if v: # Only write if not empty? Or write empty string? Better write all to be clear.
                        f.write(f"{k}={v}\n")
            
            # Update OS environ for immediate effect
            for k, v in new_env.items():
                os.environ[k] = v
                
            st.success(f"Configuration IA mise à jour ! Mode : {selected_provider}")

# --- TAB 2: MEMBERS ---
with tab_members:
    st.header("Membres du Foyer")
    st.markdown("Définissez les personnes associées à ce compte pour l'attribution des dépenses.")
    
    # List members
    members_df = get_members()
    
    col_list, col_add = st.columns([1, 1])
    
    with col_list:
        st.subheader("Membres existants")
        if members_df.empty:
            st.info("Aucun membre configuré.")
        else:
            for index, row in members_df.iterrows():
                c1, c2 = st.columns([3, 1])
                c1.write(f"👤 **{row['name']}**")
                if c2.button("🗑️", key=f"del_mem_{row['id']}"):
                    delete_member(row['id'])
                    st.rerun()

    with col_add:
        st.subheader("Ajouter un membre")
        with st.form("add_member_form"):
            new_name = st.text_input("Nom du membre", placeholder="Ex: Aurélien, Élise...")
            if st.form_submit_button("Ajouter"):
                if new_name:
                    if add_member(new_name):
                        st.success(f"Membre '{new_name}' ajouté !")
                        st.rerun()
                    else:
                        st.error("Ce membre existe déjà.")
                else:
                    st.warning("Veuillez entrer un nom.")

    st.divider()
    st.subheader("💳 Correspondance des Cartes")
    st.markdown("Associez un numéro de carte (4 derniers chiffres) à un membre pour l'import automatique.")
    
    from modules.data_manager import apply_member_mappings_to_pending
    if st.button("🔄 Appliquer les correspondances aux transactions en attente", help="Reparcourt toutes les transactions non validées pour mettre à jour le payeur selon votre configuration actuelle."):
        count = apply_member_mappings_to_pending()
        st.success(f"{count} transaction(s) mise(s) à jour !")
        st.rerun()
    
    mapping_df = get_member_mappings_df()
    
    col_m1, col_m2 = st.columns([1, 1])
    with col_m1:
        if mapping_df.empty:
            st.info("Aucune correspondance configurée.")
        else:
            for index, row in mapping_df.iterrows():
                cm1, cm2 = st.columns([3, 1])
                cm1.write(f"💳 **{row['card_suffix']}** ➔ {row['member_name']}")
                if cm2.button("🗑️", key=f"del_map_{row['id']}"):
                    delete_member_mapping(row['id'])
                    st.rerun()
    
    with col_m2:
        with st.form("add_mapping_form"):
            suffix = st.text_input("4 derniers chiffres", placeholder="Ex: 6759")
            m_name = st.selectbox("Membre", members_df['name'].tolist() if not members_df.empty else ["Anonyme"])
            if st.form_submit_button("Ajouter la carte"):
                if suffix and m_name:
                    add_member_mapping(suffix, m_name)
                    st.success("Mise à jour effectuée !")
                    st.rerun()

# --- TAB 3: CATEGORIES ---
with tab_cats:
    st.header("Gestion des Catégories")
    st.markdown("Personnalisez les catégories de dépenses pour votre budget.")
    
    # List categories
    cats_df = get_categories_df()
    
    col_list_cat, col_add_cat = st.columns([1, 1])
    
    with col_list_cat:
        st.subheader("Catégories existantes")
        if cats_df.empty:
            st.info("Aucune catégorie configurée.")
        else:
            for index, row in cats_df.iterrows():
                with st.expander(f"{row['emoji']} {row['name']} {' (Fixe)' if row['is_fixed'] else ''}", expanded=False):
                    c1, c2 = st.columns([3, 1])
                    new_emoji = c1.text_input("Emoji", value=row['emoji'], key=f"emoji_val_{row['id']}")
                    is_fixed = c1.checkbox("Dépense Fixe (ex: Loyer, Abonnement)", value=bool(row['is_fixed']), key=f"fixed_val_{row['id']}")
                    if c1.button("Mettre à jour", key=f"upd_cat_{row['id']}"):
                        update_category_emoji(row['id'], new_emoji)
                        update_category_fixed(row['id'], int(is_fixed))
                        st.rerun()
                    
                    if c2.button("🗑️ Supprimer", key=f"del_cat_{row['id']}"):
                        delete_category(row['id'])
                        st.rerun()

    with col_add_cat:
        st.subheader("Ajouter une catégorie")
        with st.form("add_cat_form"):
            col_a1, col_a2, col_a3 = st.columns([3, 1, 1])
            new_cat_name = col_a1.text_input("Nom de la catégorie", placeholder="Ex: Enfants...")
            new_cat_emoji = col_a2.text_input("Emoji", value="🏷️")
            new_is_fixed = col_a3.checkbox("Fixe", value=False)
            
            if st.form_submit_button("Ajouter"):
                if new_cat_name:
                    if add_category(new_cat_name, new_cat_emoji, int(new_is_fixed)):
                        st.success(f"Catégorie '{new_cat_name}' ajoutée !")
                        st.rerun()
                    else:
                        st.error("Cette catégorie existe déjà.")
                else:
                    st.warning("Veuillez entrer un nom.")

# --- TAB 4: DATA ---
with tab_data:
    st.header("Export des Données")
    st.markdown("Téléchargez toutes vos transactions au format CSV pour sauvegarde ou analyse externe.")
    
    conn = sqlite3.connect(DB_PATH)
    df_all = pd.read_sql("SELECT * FROM transactions", conn)
    conn.close()
    
    csv = df_all.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger tout (CSV)",
        data=csv,
        file_name='finance_export_complet.csv',
        mime='text/csv',
    )
    
    st.divider()
    
    st.header("🔥 Zone de Danger")
    st.warning("Actions irréversibles. Manipulez avec précaution.")
    
    with st.expander("Supprimer des données"):
        months = get_available_months()
        
        if months:
            target_month = st.selectbox("Sélectionner le mois à supprimer", months)
            if st.button(f"🗑️ Supprimer tout le mois {target_month}", type="secondary"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM transactions WHERE strftime('%Y-%m', date) = ?", (target_month,))
                deleted = c.rowcount
                conn.commit()
                conn.close()
                st.success(f"{deleted} transactions supprimées pour {target_month}.")
                st.rerun()
        else:
            st.write("Aucune donnée à supprimer.")

        st.divider()
        
        if st.checkbox("Je veux vider TOUTE la base de données (Reset Total)"):
            if st.button("💣 TOUT EFFACER", type="primary"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM transactions")
                c.execute("DELETE FROM learning_rules")
                c.execute("DELETE FROM budgets")
                c.execute("DELETE FROM members")
                conn.commit()
                conn.close()
                st.error("Base de données entièrement vidée.")
                st.rerun()
