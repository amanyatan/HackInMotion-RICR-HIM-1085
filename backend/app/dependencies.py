"""FastAPI dependencies.

`get_current_user` resolves the session cookie into a `UserOut`. Used by every
authenticated router so handlers never touch Supabase directly.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request

from app.core.config import settings
from app.core.ratelimit import rate_limit
from app.schemas.auth import UserOut
from app.services import auth_service
from app.utils.logger import logger


def get_current_user(request: Request) -> UserOut:
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "UNAUTHENTICATED", "message": "You are not signed in."}},
        )
    try:
        return auth_service.get_current_user(token)
    except HTTPException as exc:
        if exc.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail={"error": {"code": "SESSION_EXPIRED", "message": "Your session has expired. Please sign in again."}},
            )
        raise


# Convenience: many authenticated routers also want rate limiting.
def auth_deps():
    return [Depends(get_current_user), Depends(rate_limit)]
