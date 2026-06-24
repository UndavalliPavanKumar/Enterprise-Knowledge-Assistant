"""Application configuration module"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # App Settings
    app_name: str = "Enterprise Knowledge Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Database Settings
    database_url: str
    sqlalchemy_echo: bool = False

    # OpenAI Settings
    openai_api_key: str
    openai_model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-small"

    # Upload Settings
    max_file_size: int = 52428800  # 50MB
    allowed_extensions: str = "pdf"

    # Vector Search Settings
    embedding_dimension: int = 1536
    similarity_threshold: float = 0.7

    # API Settings
    api_port: int = 8000
    api_host: str = "0.0.0.0"

    # Streamlit Settings
    streamlit_server_port: int = 8501
    streamlit_server_headless: bool = True

    class Config:
        """Pydantic config"""

        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get settings instance"""
    return Settings()
