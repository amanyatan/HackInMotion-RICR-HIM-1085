"""Application configuration.

All configuration is read from environment variables / the local `.env` file.
No secrets are hardcoded in this codebase.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    """Read-only settings loaded once at startup."""

    def __init__(self) -> None:
        # Supabase credentials (REQUIRED for auth to work, blank in .env.example)
        self.supabase_url: str = os.getenv("SUPABASE_URL", "").strip()
        self.supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        self.supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "").strip()

        # CORS — only the frontend origin(s) may call this API
        self.cors_origins: list[str] = _split_csv(
            os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        )

        # Frontend origin used when constructing absolute URLs (e.g. TTS links)
        self.frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000").strip()

        # Session cookies
        self.session_cookie_name: str = os.getenv("SESSION_COOKIE_NAME", "cosmos_session")
        self.refresh_cookie_name: str = os.getenv("REFRESH_COOKIE_NAME", "cosmos_refresh")
        # `true` in production over HTTPS; keep `false` for local http dev
        self.cookie_secure: bool = _bool(os.getenv("COOKIE_SECURE"), False)
        self.cookie_samesite: str = os.getenv("COOKIE_SAMESITE", "lax").strip() or "lax"

        # Basic abuse protection
        self.rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

        # ------------------------------------------------------------------
        # Feature / provider mode
        # ------------------------------------------------------------------
        # MOCK_MODE=true (default) returns canned, deterministic responses so the
        # API is demoable without any paid keys. Set to false to activate live
        # third-party providers once you add keys below.
        self.mock_mode: bool = _bool(os.getenv("MOCK_MODE"), True)

        # Secret used for any server-signed tokens we issue ourselves.
        self.jwt_secret: str = os.getenv("JWT_SECRET", "").strip()

        # Which AI provider to prefer: "groq" | "sarvam" | "auto"
        self.ai_provider: str = os.getenv("AI_PROVIDER", "auto").strip().lower() or "auto"
        self.groq_api_key: str = os.getenv("GROQ_API_KEY", "").strip()
        self.groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

        # Sarvam AI for STT/TTS + chat
        self.sarvam_api_key: str = os.getenv("SARVAM_API_KEY", "").strip()
        self.sarvam_api_url: str = os.getenv(
            "SARVAM_API_URL", "https://api.sarvam.ai"
        ).strip().rstrip("/")
        self.sarvam_chat_model: str = os.getenv("SARVAM_CHAT_MODEL", "sarvam-105b").strip()

    @property
    def ai_configured(self) -> bool:
        """True when at least one AI provider key is present."""
        return bool(self.groq_api_key or self.sarvam_api_key)

    @property
    def stt_configured(self) -> bool:
        return bool(self.sarvam_api_key)

    @property
    def tts_configured(self) -> bool:
        return bool(self.sarvam_api_key)


settings = Settings()
