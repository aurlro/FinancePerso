import streamlit as st
import os

def load_env_vars():
    """Helper to read .env file"""
    vars = {}
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    vars[k] = v
    return vars

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
            # Write .env
            with open(".env", "w") as f:
                for k, v in new_env.items():
                    if v: # Write valid values
                        f.write(f"{k}={v}\n")
            
            # Update OS environ for immediate effect (for current session)
            for k, v in new_env.items():
                os.environ[k] = v
                
            st.success(f"Configuration IA mise à jour ! Mode : {selected_provider}")
