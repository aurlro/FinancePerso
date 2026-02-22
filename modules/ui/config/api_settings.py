"""
API settings UI component (Fallback).

Provides UI for configuring AI providers and API keys.
"""

import os
from typing import Dict

import streamlit as st
from dotenv import find_dotenv, load_dotenv, set_key


def load_env_vars() -> Dict[str, str]:
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
    vars_dict: Dict[str, str] = {}
    if os.path.exists(env_file):
        try:
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        vars_dict[k.strip()] = v.strip()
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture du fichier .env: {e}")

    return vars_dict


def validate_api_key(key: str, provider: str) -> bool:
    """
    Validate API key format for different providers.

    Args:
        key: API key to validate
        provider: Provider name (e.g., 'openai', 'gemini', etc.)

    Returns:
        True if key format appears valid, False otherwise
    """
    if not key or len(key) < 10:
        return False

    # Basic format checks per provider
    if provider == "gemini":
        return key.startswith("AIza") and len(key) > 20
    elif provider == "openai":
        return key.startswith("sk-") and len(key) > 20
    elif provider == "anthropic":
        return key.startswith("sk-ant-") and len(key) > 20

    return True


def render_api_settings():
    """
    Render API settings configuration UI.
    Fallback implementation without ui_v2 dependencies.
    """
    st.header("🔑 Configuration des API")
    st.markdown("---")

    # Load current env vars
    env_vars = load_env_vars()

    # AI Provider selection
    st.subheader("🤖 Fournisseur d'IA")

    provider = st.selectbox(
        "Sélectionnez votre fournisseur d'IA",
        options=["gemini", "openai", "anthropic", "ollama", "none"],
        format_func=lambda x: {
            "gemini": "Google Gemini (recommandé)",
            "openai": "OpenAI (GPT-4, GPT-3.5)",
            "anthropic": "Anthropic (Claude)",
            "ollama": "Ollama (local)",
            "none": "Aucun (mode offline)",
        }.get(x, x),
        index=0,
    )

    # API Key input
    st.subheader("🔐 Clé API")

    current_key = env_vars.get("AI_API_KEY", "")
    api_key = st.text_input(
        "Entrez votre clé API",
        value=current_key,
        type="password",
        placeholder="sk-... ou AIza...",
        help="Votre clé API sera stockée de manière sécurisée dans le fichier .env",
    )

    # Validation
    if api_key:
        is_valid = validate_api_key(api_key, provider)
        if is_valid:
            st.success("✅ Format de clé valide")
        else:
            st.warning("⚠️ Format de clé inhabituel - vérifiez votre clé")

    # Save button
    if st.button("💾 Sauvegarder", type="primary"):
        try:
            env_file = find_dotenv() or ".env"

            # Save provider
            set_key(env_file, "AI_PROVIDER", provider)

            # Save API key if provided
            if api_key:
                set_key(env_file, "AI_API_KEY", api_key)
                # Mask the key in display
                st.success("✅ Configuration sauvegardée avec succès!")
            else:
                st.info("ℹ️ Aucune clé API fournie - mode heuristique uniquement")

            # Reload to apply
            load_dotenv(env_file, override=True)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erreur lors de la sauvegarde: {e}")

    # Help section
    st.markdown("---")
    st.subheader("❓ Aide")

    with st.expander("Comment obtenir une clé API?"):
        st.markdown(f"""
        **{provider.upper()}:**
        1. Visitez le site du fournisseur
        2. Créez un compte ou connectez-vous
        3. Accédez à la section API Keys
        4. Générez une nouvelle clé
        5. Copiez-la ici
        """)

    with st.expander("Sécurité"):
        st.info("""
        🔒 Votre clé API est stockée localement dans le fichier `.env`.
        Elle n'est jamais transmise à d'autres serveurs que ceux du fournisseur d'IA choisi.
        """)


__all__ = ["render_api_settings", "load_env_vars", "validate_api_key"]
