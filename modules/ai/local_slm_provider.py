"""
LocalSLMProvider - IA Locale Souveraine
=======================================

Provider pour modèles de langage locaux (SLM) utilisant Unsloth.
Optimisé pour Llama 3.2 3B Instruct avec quantification 4-bit.

Compatible GPU: NVIDIA T4, RTX 3060, RTX 4060 (8GB+ VRAM)

Dependencies:
    pip install unsloth torch transformers

Usage:
    from modules.ai.local_slm_provider import LocalSLMProvider

    provider = LocalSLMProvider(model_name="unsloth/Llama-3.2-3B-Instruct")
    result = provider.generate_json(prompt)
"""

import json
import os
import re
from typing import Any, Optional

from modules.ai_manager import AIProvider
from modules.logger import logger

# Optional imports with graceful fallback
try:
    from unsloth import FastLanguageModel
    import torch

    UNSLOTH_AVAILABLE = True
except ImportError:
    logger.warning("Unsloth not available. Local SLM provider will use fallback.")
    FastLanguageModel = None
    torch = None
    UNSLOTH_AVAILABLE = False

try:
    from transformers import AutoTokenizer

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Transformers not available.")
    AutoTokenizer = None
    TRANSFORMERS_AVAILABLE = False


class LocalSLMProvider(AIProvider):
    """
    Provider pour Small Language Models locaux.

    Utilise Unsloth pour un chargement optimisé en 4-bit.
    Fallback automatique sur Gemini/DeepSeek si le modèle local
    n'est pas disponible ou échoue.

    Attributes:
        model_name: Nom du modèle HuggingFace (ex: unsloth/Llama-3.2-3B-Instruct)
        max_seq_length: Longueur max des séquences
        load_in_4bit: Activer la quantification 4-bit
        device: Device utilisé (cuda/cpu)
        fallback_provider: Provider de secours si local échoue
    """

    # Modèles recommandés pour la classification de transactions
    RECOMMENDED_MODELS = {
        "llama-3.2-3b": "unsloth/Llama-3.2-3B-Instruct",
        "llama-3.2-1b": "unsloth/Llama-3.2-1B-Instruct",
        "qwen-2.5-3b": "unsloth/Qwen2.5-3B-Instruct",
        "phi-4": "unsloth/phi-4",
    }

    def __init__(
        self,
        model_name: str = "unsloth/Llama-3.2-3B-Instruct",
        max_seq_length: int = 2048,
        load_in_4bit: bool = True,
        device: Optional[str] = None,
        fallback_to_cloud: bool = True,
    ):
        """
        Initialize le provider SLM local.

        Args:
            model_name: Nom du modèle HuggingFace ou clé RECOMMENDED_MODELS
            max_seq_length: Longueur maximale des séquences
            load_in_4bit: Activer la quantification 4-bit (recommandé)
            device: Device spécifique (auto-détecté si None)
            fallback_to_cloud: Basculer sur cloud si échec local
        """
        self.model_name = self.RECOMMENDED_MODELS.get(model_name, model_name)
        self.max_seq_length = max_seq_length
        self.load_in_4bit = load_in_4bit
        self.device = device or ("cuda" if torch and torch.cuda.is_available() else "cpu")
        self.fallback_to_cloud = fallback_to_cloud

        # Model components
        self.model = None
        self.tokenizer = None
        self._model_loaded = False

        # Fallback provider (lazy loaded)
        self._fallback_provider = None

        # Load model
        self._load_model()

    def _load_model(self) -> bool:
        """
        Charge le modèle avec Unsloth en 4-bit.

        Returns:
            True si chargement réussi, False sinon
        """
        if not UNSLOTH_AVAILABLE or not TRANSFORMERS_AVAILABLE:
            logger.error("Unsloth or Transformers not available. Cannot load local model.")
            return False

        try:
            logger.info(f"Loading local SLM: {self.model_name}")
            logger.info(f"Device: {self.device}, 4-bit: {self.load_in_4bit}")

            # Load model with FastLanguageModel (Unsloth)
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.model_name,
                max_seq_length=self.max_seq_length,
                dtype=None,  # Auto-detect
                load_in_4bit=self.load_in_4bit,
            )

            # Fix tokenizer padding (Tokenizer Trap)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.padding_side = "left"

            # Prepare model for inference
            FastLanguageModel.for_inference(self.model)

            self._model_loaded = True
            logger.info("✅ Local SLM loaded successfully")

            # Log VRAM usage if CUDA
            if torch and torch.cuda.is_available():
                vram_used = torch.cuda.memory_allocated() / 1024**3
                logger.info(f"VRAM usage: {vram_used:.2f} GB")

            return True

        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            self._model_loaded = False
            return False

    def _get_fallback_provider(self) -> AIProvider:
        """Initialize le provider de fallback (cloud)."""
        if self._fallback_provider is None:
            from modules.ai_manager import GeminiProvider, OpenAICompatibleProvider

            # Try Gemini first
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                logger.info("Using Gemini as fallback")
                self._fallback_provider = GeminiProvider(gemini_key)
            else:
                # Try DeepSeek
                deepseek_key = os.getenv("DEEPSEEK_API_KEY")
                if deepseek_key:
                    logger.info("Using DeepSeek as fallback")
                    self._fallback_provider = OpenAICompatibleProvider(
                        deepseek_key, "https://api.deepseek.com/v1"
                    )
                else:
                    raise RuntimeError("No fallback provider available")

        return self._fallback_provider

    def _build_prompt(self, user_prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Construit le prompt formaté pour Llama 3.2 Instruct.

        Format attendu:
        <|begin_of_text|><|start_header_id|>system<|end_header_id|>
        {system_prompt}<|eot_id|>
        <|start_header_id|>user<|end_header_id|>
        {user_prompt}<|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>
        """
        default_system = """Tu es un classificateur de transactions bancaires de haute précision. 
Ta seule fonction est d'extraire des données structurées au format JSON.
Réponds UNIQUEMENT avec du JSON brut, sans texte introductif."""

        system = system_prompt or default_system

        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system}<|eot_id|>
<|start_header_id|>user<|end_header_id|>
{user_prompt}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
        return prompt

    def _extract_json(self, text: str) -> dict[str, Any]:
        """
        Extrait le JSON de la réponse textuelle.
        Gère les markdown code blocks.
        """
        # Remove markdown code blocks
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        text = text.strip()

        # Find JSON object
        try:
            # Try direct parsing first
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON object from text
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                return json.loads(match.group())
            raise

    def generate_json(
        self,
        prompt: str,
        model_name: str | None = None,
        system_prompt: Optional[str] = None,
        max_new_tokens: int = 512,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        """
        Génère une réponse JSON à partir du prompt.

        Args:
            prompt: Le prompt utilisateur
            model_name: Ignoré (pour compatibilité interface)
            system_prompt: Prompt système optionnel
            max_new_tokens: Nombre max de tokens générés
            temperature: Température de génération (basse pour JSON strict)

        Returns:
            Dictionnaire JSON parsé
        """
        if not self._model_loaded:
            if self.fallback_to_cloud:
                logger.warning("Local model not loaded, using fallback")
                return self._get_fallback_provider().generate_json(prompt, model_name)
            else:
                return {"error": "Local model not available", "status": "model_not_loaded"}

        try:
            # Build formatted prompt
            formatted_prompt = self._build_prompt(prompt, system_prompt)

            # Tokenize
            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.max_seq_length,
            ).to(self.device)

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=True if temperature > 0 else False,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )

            # Decode
            generated_text = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1] :], skip_special_tokens=True
            )

            # Extract and parse JSON
            result = self._extract_json(generated_text)

            # Add metadata
            result["_source"] = "local_slm"
            result["_model"] = self.model_name

            return result

        except Exception as e:
            logger.error(f"Local generation error: {e}")

            if self.fallback_to_cloud:
                logger.info("Falling back to cloud provider")
                return self._get_fallback_provider().generate_json(prompt, model_name)
            else:
                return {"error": f"Generation failed: {str(e)}", "status": "generation_error"}

    def generate_text(
        self,
        prompt: str,
        model_name: str | None = None,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """
        Génère une réponse textuelle.

        Args:
            prompt: Le prompt utilisateur
            model_name: Ignoré (compatibilité)
            max_new_tokens: Nombre max de tokens
            temperature: Température de génération

        Returns:
            Texte généré
        """
        if not self._model_loaded:
            if self.fallback_to_cloud:
                return self._get_fallback_provider().generate_text(prompt, model_name)
            else:
                return "⚠️ Modèle local non disponible"

        try:
            formatted_prompt = self._build_prompt(prompt)

            inputs = self.tokenizer(
                formatted_prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.max_seq_length,
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )

            generated_text = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1] :], skip_special_tokens=True
            )

            return generated_text.strip()

        except Exception as e:
            logger.error(f"Text generation error: {e}")

            if self.fallback_to_cloud:
                return self._get_fallback_provider().generate_text(prompt, model_name)
            else:
                return f"⚠️ Erreur de génération: {str(e)[:100]}"

    def list_models(self) -> list[str]:
        """Liste les modèles locaux disponibles."""
        return list(self.RECOMMENDED_MODELS.keys())

    def get_model_info(self) -> dict[str, Any]:
        """Retourne les informations sur le modèle chargé."""
        info = {
            "model_name": self.model_name,
            "loaded": self._model_loaded,
            "device": self.device,
            "quantization": "4-bit" if self.load_in_4bit else "full",
            "max_seq_length": self.max_seq_length,
        }

        if torch and torch.cuda.is_available():
            info["vram_allocated_gb"] = round(torch.cuda.memory_allocated() / 1024**3, 2)
            info["vram_reserved_gb"] = round(torch.cuda.memory_reserved() / 1024**3, 2)

        return info

    def unload_model(self):
        """Décharge le modèle pour libérer la VRAM."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None

        if torch and torch.cuda.is_available():
            torch.cuda.empty_cache()

        self._model_loaded = False
        logger.info("Model unloaded, VRAM freed")


# Convenience function for easy import
def get_local_slm_provider(
    model_name: str = "llama-3.2-3b",
    fallback_to_cloud: bool = True,
) -> LocalSLMProvider:
    """
    Factory function pour LocalSLMProvider.

    Args:
        model_name: Clé du modèle (llama-3.2-3b, llama-3.2-1b, etc.)
        fallback_to_cloud: Autoriser fallback sur cloud

    Returns:
        LocalSLMProvider configuré
    """
    return LocalSLMProvider(
        model_name=model_name,
        fallback_to_cloud=fallback_to_cloud,
    )
