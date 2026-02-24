"""Configuration management for PlanIT backend.

Loads settings from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from typing import Literal
import os


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # LLM Configuration
    llm_provider: Literal["openai", "gemini", "groq", "mock"] = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    google_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # MongoDB
    mongo_uri: str = ""

    # API Configuration
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    debug: bool = True

    # Geo API
    google_maps_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Return the global settings instance."""
    return settings
