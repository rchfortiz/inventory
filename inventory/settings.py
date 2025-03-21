from pathlib import Path
from secrets import token_hex

from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = Path(".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INV_", env_file=".env")

    db_url: str = "sqlite:///inventory.db"
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"


settings = Settings()  # pyright: ignore[reportCallIssue]

if not settings.jwt_secret_key:
    settings.jwt_secret_key = token_hex()

if not DOTENV.exists():
    DOTENV.write_text(f"INV_JWT_SECRET_KEY={settings.jwt_secret_key}\n")
