from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import model_validator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Application
    # -------------------------------------------------------------------------
    app_env: Literal["development", "staging", "production"] = "development"
    app_name: str = "KP Astrology API"
    debug: bool = False
    log_level: str = "INFO"
    allowed_origins: list[str] = ["http://localhost:3000"]

    # -------------------------------------------------------------------------
    # Database
    # -------------------------------------------------------------------------
    database_url: str = "postgresql+asyncpg://kp_user:changeme@localhost:5432/kp_astro"
    database_url_sync: str = "postgresql+psycopg2://kp_user:changeme@localhost:5432/kp_astro"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # -------------------------------------------------------------------------
    # Redis
    # -------------------------------------------------------------------------
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # -------------------------------------------------------------------------
    # JWT (RS256)
    # -------------------------------------------------------------------------
    jwt_private_key_path: Path = Path("./keys/private.pem")
    jwt_public_key_path: Path = Path("./keys/public.pem")
    jwt_algorithm: str = "RS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30

    # Populated by validator below — never set directly in .env
    jwt_private_key: str = ""
    jwt_public_key: str = ""

    # -------------------------------------------------------------------------
    # Swiss Ephemeris
    # -------------------------------------------------------------------------
    ephe_path: Path = Path("./data/ephemeris")

    # -------------------------------------------------------------------------
    # Rate limiting
    # -------------------------------------------------------------------------
    rate_limit_default: str = "1000/minute"
    rate_limit_auth: str = "10/minute"
    rate_limit_chart: str = "100/minute"

    # -------------------------------------------------------------------------
    # External APIs
    # -------------------------------------------------------------------------
    geonames_username: str = "demo"

    # -------------------------------------------------------------------------
    # Storage (Phase 3)
    # -------------------------------------------------------------------------
    s3_bucket: str = ""
    s3_region: str = "ap-south-1"
    s3_access_key: str = ""
    s3_secret_key: str = ""

    # -------------------------------------------------------------------------
    # Observability (Phase 2)
    # -------------------------------------------------------------------------
    sentry_dsn: str = ""

    @model_validator(mode="after")
    def load_jwt_keys(self) -> "Settings":
        """Read RSA PEM key files into memory at startup."""
        if self.jwt_private_key_path.exists():
            self.jwt_private_key = self.jwt_private_key_path.read_text().strip()
        if self.jwt_public_key_path.exists():
            self.jwt_public_key = self.jwt_public_key_path.read_text().strip()
        return self

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
