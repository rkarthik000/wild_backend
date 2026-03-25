"""
Core configuration — reads from .env / environment variables.
Copy .env.example to .env and fill in your values.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "WildGuard AI"
    DEBUG: bool = False

    # ── Supabase (optional — falls back to SQLite) ───────
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # ── Twilio SMS alerts ────────────────────────────────
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None   # e.g. "+12015551234"

    # ── AI Models ────────────────────────────────────────
    YOLO_MODEL: str = "yolov8n.pt"             # swap for custom wildlife model
    SPECIES_MODEL: str = "microsoft/resnet-50" # HuggingFace species classifier
    CONFIDENCE_THRESHOLD: float = 0.60         # min confidence to log incident

    # ── Alert thresholds ─────────────────────────────────
    HIGH_THREAT_CONFIDENCE: float = 0.80       # triggers SMS immediately
    HIGH_THREAT_TYPES: list = ["POACHER", "WEAPON", "VEHICLE"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
