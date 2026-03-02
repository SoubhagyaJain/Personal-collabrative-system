from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    name: str = "Personal Collaborative API"
    env: str = "development"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(env_prefix="APP_", case_sensitive=False)


settings = Settings()
