"""
Configuration de l'application FinancePerso API.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'application."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = "FinancePerso API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    
    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 jours
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./financeperso.db"
    database_echo: bool = False
    
    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # AI Providers (optionnel)
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    ai_provider: str = "gemini"
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def is_development(self) -> bool:
        """Vérifie si l'environnement est en développement."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Vérifie si l'environnement est en production."""
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """Retourne les paramètres de configuration (singleton)."""
    return Settings()
