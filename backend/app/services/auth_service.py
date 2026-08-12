"""Auth business logic.

Owns the signup/login flows and maps Supabase errors to structured,
non-sensitive HTTP errors. Route handlers stay thin.
"""

from datetime import datetime, timezone

from fastapi import HTTPException

from app.db.supabase import SupabaseAuthRepository
from app.schemas.auth import AuthResult, LoginRequest, SignupRequest, UserOut

repo = SupabaseAuthRepository()


def _map_supabase_error(exc: Exception) -> HTTPException:
    """Map a Supabase error to a structured HTTP error without leaking internals."""
    message = str(getattr(exc, "message", None) or exc)
    code = getattr(exc, "code", None)
    lowered = message.lower()

    if code == "user_already_exists" or "already registered" in lowered or "already exists" in lowered:
        return HTTPException(
            status_code=409,
            detail={"error": {"code": "EMAIL_ALREADY_EXISTS", "message": "An account with this email already exists."}},
        )
    if code == "invalid_credentials" or "invalid login credentials" in lowered:
        return HTTPException(
            status_code=401,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Incorrect email or password."}},
        )
    if "email not confirmed" in lowered:
        return HTTPException(
            status_code=403,
            detail={"error": {"code": "EMAIL_NOT_CONFIRMED", "message": "Please confirm your email address before signing in."}},
        )
    if "not configured" in lowered:
        return HTTPException(
            status_code=503,
            detail={"error": {"code": "BACKEND_NOT_CONFIGURED", "message": "Authentication is not configured yet."}},
        )
    return HTTPException(
        status_code=502,
        detail={"error": {"code": "SUPABASE_ERROR", "message": "Authentication service is temporarily unavailable. Please try again later."}},
    )


def _result_from_session(user: UserOut, session) -> AuthResult:
    auth_data = getattr(session, "session", None) or session
    return AuthResult(
        user=user,
        access_token=auth_data.access_token,
        refresh_token=auth_data.refresh_token,
        expires_at=getattr(auth_data, "expires_at", None),
    )


def _with_profile(uid: str, email: str) -> UserOut:
    """Attach the display name from the optional `profiles` table.

    The table is optional — degrade gracefully if it doesn't exist yet.
    """
    name: str | None = None
    try:
        rows = repo.get_profile(uid)
        if rows:
            name = rows[0].get("name")
    except Exception:
        name = None
    return UserOut(id=uid, email=email, name=name)


def sign_up(data: SignupRequest) -> AuthResult:
    email = data.email.strip().lower()
    try:
        created = repo.create_user(email, data.password)
    except Exception as exc:
        raise _map_supabase_error(exc) from exc

    uid = created.user.id

    # best-effort: store display name in the optional `profiles` table
    try:
        repo.upsert_profile(
            {
                "id": uid,
                "email": email,
                "name": data.name.strip(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    except Exception:
        pass  # profiles table may not exist yet — auth still works

    # sign the new user in immediately so we can issue the session cookie
    try:
        session = repo.sign_in_with_password(email, data.password)
    except Exception as exc:
        raise _map_supabase_error(exc) from exc

    return _result_from_session(_with_profile(uid, email), session)


def sign_in(data: LoginRequest) -> AuthResult:
    email = data.email.strip().lower()
    try:
        session = repo.sign_in_with_password(email, data.password)
    except Exception as exc:
        raise _map_supabase_error(exc) from exc

    user = session.user
    return _result_from_session(_with_profile(user.id, user.email), session)


def get_current_user(access_token: str) -> UserOut:
    try:
        response = repo.get_user(access_token)
    except Exception as exc:
        raise _map_supabase_error(exc) from exc
    user = response.user
    return UserOut(id=user.id, email=user.email, name=None)


def revoke(access_token: str | None) -> None:
    try:
        repo.sign_out(access_token)
    except Exception:
        pass  # revocation is best-effort; cookie clearing is authoritative