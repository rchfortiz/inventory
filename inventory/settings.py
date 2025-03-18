from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INV_", env_file=".env")

    db_url: str = "sqlite:///inventory.db"


settings = Settings()
