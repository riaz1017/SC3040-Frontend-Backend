from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./peerup.db"
    secret_key: str = "peerup-dev-secret"
    access_token_expire_minutes: int = 60 * 24 * 7
    matching_fallback: bool = False
    upload_dir: str = "uploads"
    algorithm: str = "HS256"


settings = Settings()
