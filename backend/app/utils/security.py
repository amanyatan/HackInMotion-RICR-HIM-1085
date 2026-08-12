"""Server-side security helpers.

Used for signing our own short-lived tokens and for ownership checks. The
primary authentication mechanism remains the HttpOnly Supabase session cookie;
these helpers are for supplementary concerns only.
"""

import hashlib
import hmac
import time

from app.core.config import settings
from app.utils.logger import logger


def sign_payload(data: str, ttl_seconds: int = 600) -> str:
    """Return `payload.signature` HMAC-signed with JWT_SECRET.

    The payload is NOT encrypted; it only proves the server issued this value
    recently. Never put secrets in the payload.
    """
    secret = settings.jwt_secret.encode("utf-8")
    payload = f"{int(time.time() + ttl_seconds)}.{data}"
    signature = hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_signature(signed: str, data: str, ttl_seconds: int = 600) -> bool:
    """Verify a value previously produced by `sign_payload`."""
    try:
        expires, _, signature = signed.partition(".")
        delimiter = data.rindex(".")
        # signed format: "<expires>.<data>.<signature>"
        expected = hmac.new(
            settings.jwt_secret.encode("utf-8"),
            f"{expires}.{data}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return False
        return int(expires) >= int(time.time())
    except (ValueError, TypeError, AttributeError):
        return False


def is_mock_mode() -> bool:
    if settings.mock_mode:
        return True
    # Even in "live" mode, degrade to mock the moment no keys are present.
    return not settings.ai_configured


def redact(value: str) -> str:
    """Keep only the last 4 chars for safe logging of keys/tokens."""
    if not value:
        return "<empty>"
    return "…" + value[-4:]
