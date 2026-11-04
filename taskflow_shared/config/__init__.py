"""Typed application settings without application or database dependencies."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from taskflow_shared.enums import AppEnvironment


class BaseAppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    APP_NAME: str = "TaskFlow API"
    ENVIRONMENT: AppEnvironment = Field(
        AppEnvironment.DEVELOPMENT, validation_alias="APP_ENV"
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == AppEnvironment.PRODUCTION
