import streamlit as st
import os
import stat
from dotenv import load_dotenv, set_key, find_dotenv

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
            st.error(f"Erreur lors de la lecture du fichier .env: {e}")

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
        st.warning(f"Impossible de définir les permissions sécurisées: {e}")

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
            # Validate API key if applicable
            validation_error = None
            if selected_provider == "Gemini" and new_env.get("GEMINI_API_KEY"):
                if not validate_api_key(new_env["GEMINI_API_KEY"], "Gemini"):
                    validation_error = "La clé API Gemini semble invalide (doit commencer par 'AIzaSy')"
            elif selected_provider == "OpenAI" and new_env.get("OPENAI_API_KEY"):
                if not validate_api_key(new_env["OPENAI_API_KEY"], "OpenAI"):
                    validation_error = "La clé API OpenAI semble invalide (doit commencer par 'sk-')"

            if validation_error:
                st.error(validation_error)
            else:
                try:
                    env_file = ".env"

                    # Write .env securely using set_key from python-dotenv
                    for k, v in new_env.items():
                        if v and v.strip():  # Only write non-empty values
                            set_key(env_file, k, v)

                    # Set secure file permissions (0600)
                    set_secure_env_permissions(env_file)

                    # Update OS environ for immediate effect (for current session)
                    for k, v in new_env.items():
                        if v:
                            os.environ[k] = v

                    st.success(f"✅ Configuration IA mise à jour ! Mode : {selected_provider}")
                    st.info("🔒 Permissions sécurisées appliquées au fichier .env")

                except Exception as e:
                    st.error(f"❌ Erreur lors de la sauvegarde : {e}")
