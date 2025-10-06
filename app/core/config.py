import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError

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
    APP_NAME: str = "Article Management Service"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str
    API_KEY: str | None = None
    CACHE_TTL_SECONDS: int = 120
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    API_PORT: int = 8000
    RATE_LIMIT_WINDOW: int = 60
    RATE_LIMIT_MAX_REQUESTS: int = 20
    REDIS_HOST : str = (os.getenv("REDIS_HOST", "redis"))
    REDIS_PORT: int = (os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = (os.getenv("REDIS_DB", 0))
    REDIS_URL: str = (os.getenv("REDIS_URL")) or str(f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")  
    
    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # @property
    # def REDIS_URL(self):
    #     return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    
    def __init__(self, **values):
        super().__init__(**values)
        # Construir URL automáticamente si no está definida
        if not self.REDIS_URL:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

try:
    settings = Settings()
except ValidationError as e:
    print("Missing required environment variables:\n", e)
    raise SystemExit(1)