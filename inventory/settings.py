from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings for the application.

    All of these are configured using environment variables prefixed with `INV_`
    (e.g. `INV_PORT=8080`). A `.env` file will also be read if there is one in
    the current working directory.
    """

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
