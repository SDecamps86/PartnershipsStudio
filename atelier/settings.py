from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_mode: Literal["demo", "showcase", "live"] = "demo"

    @property
    def live_available(self) -> bool:
        # Demo mode deliberately has no generation path, regardless of environment.
        return False
