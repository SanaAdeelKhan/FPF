"""
Central app configuration, loaded from environment variables (.env in local dev).
Import `settings` anywhere you need a config value — never read os.environ directly
elsewhere in the app, so all config stays discoverable from this one file.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    database_url: str = "sqlite:///./fpf.db"
    cors_origins: str = "http://localhost:5173"
    environment: str = "local"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
