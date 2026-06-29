from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

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

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        if not v:
            return v
        # Convert postgres:// to postgresql://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        # Convert postgresql:// to postgresql+asyncpg://
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        # Convert sslmode=... to ssl=... because asyncpg expects "ssl" instead of "sslmode"
        if "sslmode=" in v:
            v = v.replace("sslmode=", "ssl=")
        return v

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
