"""Service settings loaded from APP_* environment variables."""
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "orders-api"
    debug: bool = False
    port: int = 8000
    database_url: str
    allowed_hosts: List[str] = ["localhost"]

    model_config = SettingsConfigDict(env_prefix="APP_")


def load_settings(**overrides):
    """Read settings from the environment (APP_ prefix); keyword overrides take precedence."""
    return Settings(**overrides)
