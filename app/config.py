from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase Postgres: postgresql+asyncpg://USER:PASS@HOST:PORT/postgres
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

    JWT_SECRET: str = "change-me-to-a-long-random-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    ENV: str = "development"
    CORS_ORIGINS: str = "*"

    # Keep-alive (Render only): self-ping URL to prevent free-tier sleep.
    SELF_PING_URL: str = ""
    SELF_PING_INTERVAL_SEC: int = 300  # 5 min

    # Empty-string env vars (common on hosting dashboards) -> use defaults
    @field_validator(
        "ACCESS_TOKEN_EXPIRE_MINUTES", "SELF_PING_INTERVAL_SEC", mode="before"
    )
    @classmethod
    def _blank_int_to_default(cls, v, info):
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return cls.model_fields[info.field_name].default
        return v

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalize_db_url(cls, v):
        # asyncpg driver ensure + pgbouncer flag (Supabase pooler) hata do
        if isinstance(v, str) and v:
            if v.startswith("postgresql+asyncpg://"):
                v = v.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
            if v.startswith("postgresql://"):
                v = v.replace("postgresql://", "postgresql+psycopg://", 1)
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+psycopg://", 1)
            v = v.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")
        return v

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()
