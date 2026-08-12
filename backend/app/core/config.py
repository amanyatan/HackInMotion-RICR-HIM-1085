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


class Settings:
    """Read-only settings loaded once at startup."""

    def __init__(self) -> None:
        # Supabase credentials (REQUIRED for auth to work, blank in .env.example)
        self.supabase_url: str = os.getenv("SUPABASE_URL", "").strip()
        self.supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

        # CORS — only the frontend origin(s) may call this API
        self.cors_origins: list[str] = _split_csv(
            os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        )

        # Session cookies
        self.session_cookie_name: str = os.getenv("SESSION_COOKIE_NAME", "comuse_session")
        self.refresh_cookie_name: str = os.getenv("REFRESH_COOKIE_NAME", "comuse_refresh")
        # `true` in production over HTTPS; keep `false` for local http dev
        self.cookie_secure: bool = os.getenv("COOKIE_SECURE", "false").lower() in ("1", "true", "yes")
        self.cookie_samesite: str = os.getenv("COOKIE_SAMESITE", "lax").strip() or "lax"

        # Basic abuse protection
        self.rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))


settings = Settings()