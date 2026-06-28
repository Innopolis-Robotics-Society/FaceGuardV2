"""Application configuration loaded from environment variables.

All tunable knobs (threshold, servo, registration cadence, ML service URL,
admin credentials) are read from environment so the same image can be
shipped to Raspberry Pi and x86 unchanged. See `.env.example` for the full
list of variables and their meaning.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Recognition ---
    threshold: float = Field(default=0.45, ge=0.0, le=1.0)
    recognition_interval_ms: int = Field(default=500, ge=50)

    # --- Registration ---
    registration_frame_count: int = Field(default=5, ge=1, le=20)
    registration_frame_interval_ms: int = Field(default=400, ge=50)

    # --- Database ---
    database_path: Path = Path("/data/faces.db")

    # --- ML service ---
    ml_service_url: str = "http://ml:8001"

    # --- Admin credentials (bootstrap on first startup) ---
    admin_username: str = "admin"
    admin_password: SecretStr = SecretStr("change-me-on-first-login")
    admin_password_hash: str | None = None

    # --- Auth ---
    secret_key: SecretStr = SecretStr("change-me-to-a-long-random-string")
    session_cookie_name: str = "faceguard_session"
    session_cookie_secure: bool = False

    # --- Servo ---
    servo_mode: Literal["gpio", "emulated"] = "emulated"
    servo_pin: int = 18
    servo_open_duration_sec: float = Field(default=2.0, ge=0.1, le=30.0)

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # --- Liveness ---
    liveness_enabled: bool = Field(default=False, description="Need blinking for access")
    liveness_ear_threshold: float = Field(default=0.20, ge=0.05, le=0.40)
    liveness_min_blink_duration_ms: int = Field(default=100, ge=50)
    liveness_timeout_sec: float = Field(default=3.0, ge=1.0, le=10.0)

    @field_validator("ml_service_url")
    @classmethod
    def _strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")

    def admin_password_is_hashed(self) -> bool:
        """True if `admin_password_hash` was provided (takes precedence)."""
        return bool(self.admin_password_hash)

    @property
    def admin_password_plain(self) -> str:
        return self.admin_password.get_secret_value()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
