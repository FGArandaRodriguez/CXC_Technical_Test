import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Handles the application configuration and environment management.

    This class centralizes all environment variables, loading them automatically 
    from a `.env` file if available. It uses **Pydantic Settings** to ensure 
    validation, type safety, and default values for all configuration parameters.

    Attributes:
        APP_NAME (str): The name of the application.
        API_V1_STR (str): Base path for the API version 1 routes.
        DATABASE_URL (str): Database connection URL for PostgreSQL.
        REDIS_URL (str): Redis connection URL used for caching or messaging.
        API_KEY (Optional[str]): Optional API key for authentication.
        CACHE_TTL_SECONDS (int): Default cache expiration time in seconds.

    Methods:
        Inherits methods from `BaseSettings` to load, parse, and validate
        environment variables.

    Returns:
        Settings: A validated configuration object ready to be imported 
        across the application.

    """
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Article Management Service"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@db:5432/articlesdb")

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    API_KEY: str | None = os.getenv("API_KEY")
    CACHE_TTL_SECONDS: int = 120
    
settings = Settings()