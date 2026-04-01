"""Configuration management for the service."""

import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Service
    app_name: str = "AI Capability Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # OpenAI Configuration (optional)
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-3.5-turbo", alias="OPENAI_MODEL")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def load_settings() -> Settings:
    """Load settings with explicit .env file loading."""
    # Try to load from .env file explicitly
    try:
        from dotenv import load_dotenv
        # Look for .env in current directory and parent directories
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(current_dir, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
    except ImportError:
        pass  # python-dotenv not installed, rely on pydantic-settings
    
    return Settings()


# Global settings instance
settings = load_settings()
