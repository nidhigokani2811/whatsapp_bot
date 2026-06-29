from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/whatsapp_db",
        description="Async PostgreSQL connection string"
    )

    # WhatsApp API General Settings
    WHATSAPP_VERIFY_TOKEN: str = Field(
        default="dummy_verify_token",
        description="Verification token configured in Meta Webhook page for validation challenge"
    )
    WHATSAPP_API_VERSION: str = Field(
        default="v20.0",
        description="WhatsApp API Version"
    )

settings = Settings()
