from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from .env or real environment variables.

    In production (Docker/GCP), these values come from the container
    environment, never from a committed .env file.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # AI providers. Keys are optional at this stage (Phase 3 has no AI calls
    # yet) but declared now so the config surface doesn't change later.
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    database_url: str = "sqlite:///./data/language_quiz.db"
    log_level: str = "INFO"
    environment: str = "development"


# Single instance, imported by the rest of the application
settings = Settings()
