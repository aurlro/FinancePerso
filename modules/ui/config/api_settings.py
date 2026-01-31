import streamlit as st
import os
import stat
from dotenv import load_dotenv, set_key, find_dotenv
from modules.ui.feedback import (
    toast_success, toast_error, toast_warning, toast_info,
    api_config_feedback, show_success, show_error
)


def load_env_vars():
    """
    Securely load environment variables from .env file using python-dotenv.
    Returns a dictionary of all variables found in .env file.
    """
    env_file = find_dotenv()
    if not env_file:
        env_file = ".env"

    # Load .env into os.environ
    load_dotenv(env_file)

    # Return dictionary of vars from .env file
    vars = {}
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        vars[k.strip()] = v.strip()
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture du fichier .env: {e}")

    return vars


def validate_api_key(key: str, provider: str) -> bool:
    """
    Validate API key format for different providers.
    """
    if not key or not key.strip():
        return False

    # Basic validation rules
    if provider == "Gemini":
        return key.startswith("AIzaSy") and len(key) > 30
    elif provider == "OpenAI":
        return key.startswith("sk-") and len(key) > 20
    elif provider == "DeepSeek":
        return len(key) > 20  # DeepSeek format varies

    return True  # For Ollama URL, etc.


def set_secure_env_permissions(env_file: str):
    """
    Set secure file permissions (0600) on .env file to prevent unauthorized access.
    Only the owner can read/write.
    """
    try:
        os.chmod(env_file, stat.S_IRUSR | stat.S_IWUSR)  # 0600
    except Exception as e:
        toast_warning(f"⚠️ Impossible de définir les permissions sécurisées: {e}", icon="🔒")


def render_api_settings():
    """
    Render the API & Services tab content.
    Handles AI provider configuration and .env file management.
    """
    st.header("🤖 Cerveau IA")
    st.markdown("Choisissez quel moteur d'intelligence artificielle pilote votre assistant.")
    
    env_vars = load_env_vars()
    
    # Provider Selection
    PROVIDERS = ["Gemini", "Ollama", "DeepSeek", "OpenAI"]
    # Check current provider from env
    current_provider_env = env_vars.get("AI_PROVIDER", "Gemini")
    # Handle case where env var might be lowercase
    current_provider = current_provider_env.capitalize()
    
    if current_provider not in PROVIDERS:
        current_provider = "Gemini"
    
    # Show current provider badge
    st.caption(f"Fournisseur actuel : **{current_provider}**")
        
    selected_provider = st.selectbox(
        "Fournisseur IA",
        PROVIDERS,
        index=PROVIDERS.index(current_provider),
        help="Sélectionnez le service d'IA à utiliser"
    )
    
    st.divider()
    
    # Form based on selection
    with st.form("ai_config"):
        new_env = env_vars.copy()
        new_env["AI_PROVIDER"] = selected_provider.lower()
        
        if selected_provider == "Gemini":
            st.info("📝 Le modèle standard : Rapide, performant et gratuit/pas cher.")
            val = st.text_input(
                "Clé API Google Gemini",
                value=env_vars.get("GEMINI_API_KEY", ""),
                type="password",
                help="Commence par 'AIzaSy...' - Obtenez-la sur makersuite.google.com"
            )
            new_env["GEMINI_API_KEY"] = val
            
        elif selected_provider == "Ollama":
            st.info("🔒 100% Local & Privé. Assurez-vous qu'Ollama tourne sur votre machine.")
            url = st.text_input(
                "URL du serveur Ollama",
                value=env_vars.get("OLLAMA_URL", "http://localhost:11434"),
                help="URL par défaut : http://localhost:11434"
            )
            new_env["OLLAMA_URL"] = url
            
        elif selected_provider == "DeepSeek":
            st.info("📝 Performance coût/efficacité redoutable.")
            val = st.text_input(
                "Clé API DeepSeek",
                value=env_vars.get("DEEPSEEK_API_KEY", ""),
                type="password",
                help="Obtenez-la sur platform.deepseek.com"
            )
            new_env["DEEPSEEK_API_KEY"] = val
            
        elif selected_provider == "OpenAI":
            st.info("📝 Le standard de l'industrie (GPT-4 / GPT-3.5).")
            val = st.text_input(
                "Clé API OpenAI",
                value=env_vars.get("OPENAI_API_KEY", ""),
                type="password",
                help="Commence par 'sk-...' - Obtenez-la sur platform.openai.com"
            )
            new_env["OPENAI_API_KEY"] = val
            
        # Common: Model Name Override
        st.subheader("⚙️ Options Avancées")
        model_val = st.text_input(
            "Nom du modèle (laisser vide pour défaut)",
            value=env_vars.get("AI_MODEL_NAME", ""),
            help="Ex: llama3, gpt-4o, gemini-1.5-pro"
        )
        new_env["AI_MODEL_NAME"] = model_val

        submitted = st.form_submit_button("💾 Sauvegarder et Appliquer", type="primary", use_container_width=True)
        
        if submitted:
            # Validate API key if applicable
            validation_error = None
            if selected_provider == "Gemini" and new_env.get("GEMINI_API_KEY"):
                if not validate_api_key(new_env["GEMINI_API_KEY"], "Gemini"):
                    validation_error = "La clé API Gemini semble invalide (doit commencer par 'AIzaSy')"
            elif selected_provider == "OpenAI" and new_env.get("OPENAI_API_KEY"):
                if not validate_api_key(new_env["OPENAI_API_KEY"], "OpenAI"):
                    validation_error = "La clé API OpenAI semble invalide (doit commencer par 'sk-')"

            if validation_error:
                show_error(validation_error, icon="🔑")
                toast_error(f"❌ {validation_error}", icon="🔑")
            else:
                try:
                    env_file = ".env"
                    
                    # Create file if doesn't exist
                    if not os.path.exists(env_file):
                        open(env_file, 'a').close()

                    # Write .env securely using set_key from python-dotenv
                    keys_written = 0
                    for k, v in new_env.items():
                        if v and v.strip():  # Only write non-empty values
                            set_key(env_file, k, v)
                            keys_written += 1

                    # Set secure file permissions (0600)
                    set_secure_env_permissions(env_file)

                    # Update OS environ for immediate effect (for current session)
                    for k, v in new_env.items():
                        if v:
                            os.environ[k] = v

                    # Feedback visuel amélioré
                    api_config_feedback(selected_provider, success=True)
                    
                    # Toast détaillé
                    config_msg = f"✅ Configuration {selected_provider} enregistrée"
                    if model_val:
                        config_msg += f" (modèle: {model_val})"
                    toast_success(config_msg, icon="🤖")
                    
                    show_success(f"🤖 Configuration IA mise à jour ! Fournisseur : {selected_provider}")
                    toast_info("🔒 Permissions sécurisées appliquées au fichier .env", icon="🔒")
                    
                    # Afficher un récapitulatif
                    with st.expander("📋 Récapitulatif de la configuration", expanded=False):
                        st.write(f"**Fournisseur** : {selected_provider}")
                        st.write(f"**Fichier** : {env_file}")
                        st.write(f"**Clés écrites** : {keys_written}")
                        if model_val:
                            st.write(f"**Modèle personnalisé** : {model_val}")
                        st.success("✅ Les changements sont immédiatement actifs")

                except PermissionError as e:
                    error_msg = f"Permission refusée : {e}. Vérifiez les droits d'accès."
                    show_error(error_msg, icon="🔒")
                    toast_error(f"❌ {error_msg}", icon="🔒")
                except Exception as e:
                    error_msg = str(e)
                    api_config_feedback(selected_provider, success=False)
                    show_error(f"Erreur lors de la sauvegarde : {e}", icon="❌")
                    toast_error(f"❌ Échec de la sauvegarde : {error_msg[:80]}", icon="❌")
    
    # Info section
    st.divider()
    with st.expander("📖 Guide de configuration", expanded=False):
        st.markdown("""
        ### 🔑 Comment obtenir une clé API
        
        **Google Gemini (Recommandé)**
        1. Allez sur [makersuite.google.com](https://makersuite.google.com)
        2. Créez un compte Google
        3. Générez une clé API gratuite
        4. Copiez la clé (commence par `AIzaSy`)
        
        **OpenAI (GPT-4/3.5)**
        1. Allez sur [platform.openai.com](https://platform.openai.com)
        2. Créez un compte
        3. Ajoutez un moyen de paiement
        4. Générez une clé API (commence par `sk-`)
        
        **DeepSeek**
        1. Allez sur [platform.deepseek.com](https://platform.deepseek.com)
        2. Créez un compte
        3. Ajoutez des crédits
        4. Générez une clé API
        
        **Ollama (Local)**
        1. Installez Ollama : [ollama.com](https://ollama.com)
        2. Lancez Ollama localement
        3. Aucune clé requise !
        """)
