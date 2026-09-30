"""Service settings loaded from APP_* environment variables (written against pydantic 1.10)."""
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "orders-api"
    debug: bool = False
    port: int = 8000
    database_url: str
    allowed_hosts: List[str] = ["localhost"]

    class Config:
        env_prefix = "APP_"


def load_settings(**overrides):
    """Read settings from the environment (APP_ prefix); keyword overrides take precedence."""
    return Settings(**overrides)
