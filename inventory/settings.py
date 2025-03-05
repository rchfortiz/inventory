from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INV_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    host: str = "127.0.0.1"
    port: int = 8080
    database_url: str = "sqlite+aiosqlite:///inventory.db"
    jwt_secret_key: str = "dev"  # noqa: S105
    jwt_algorithm: str = "HS256"


settings = Settings()
