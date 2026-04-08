from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="auro", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")

    db_host: str | None = Field(default=None, alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str | None = Field(default=None, alias="DB_NAME")
    db_user: str | None = Field(default=None, alias="DB_USER")
    db_password: str | None = Field(default=None, alias="DB_PASSWORD")
    db_ssl_mode: str = Field(default="disable", alias="DB_SSL_MODE")

    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen2.5:7b", alias="OLLAMA_MODEL")
    cloud_llm_base_url: str | None = Field(default=None, alias="CLOUD_LLM_BASE_URL")
    cloud_llm_api_key: str | None = Field(default=None, alias="CLOUD_LLM_API_KEY")
    cloud_llm_model: str = Field(default="gpt-4.1-mini", alias="CLOUD_LLM_MODEL")
    web_builder_primary_provider: str = Field(default="ollama", alias="WEB_BUILDER_PRIMARY_PROVIDER")
    web_builder_fallback_provider: str = Field(default="cloud", alias="WEB_BUILDER_FALLBACK_PROVIDER")
    web_builder_force_cloud_for_design: bool = Field(
        default=False,
        alias="WEB_BUILDER_FORCE_CLOUD_FOR_DESIGN",
    )
    request_timeout_seconds: int = Field(default=30, alias="REQUEST_TIMEOUT_SECONDS")

    @computed_field
    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        required = [self.db_host, self.db_name, self.db_user, self.db_password]
        if not all(required):
            raise ValueError(
                "Database configuration missing. Set DATABASE_URL or DB_HOST/DB_NAME/DB_USER/DB_PASSWORD."
            )

        encoded_password = quote_plus(self.db_password or "")
        return (
            f"postgresql+psycopg://{self.db_user}:{encoded_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?sslmode={self.db_ssl_mode}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
