"""Auth route handlers.

Thin layer: validate via Pydantic, delegate to the service, set HttpOnly
session cookies. No Supabase logic lives here.
"""

import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.core.config import settings
from app.core.ratelimit import rate_limit
from app.schemas.auth import AuthResult, AuthSuccess, LoginRequest, SignupRequest
from app.services import auth_service

router = APIRouter(dependencies=[Depends(rate_limit)])

_ACCESS_MAX_AGE = 3600  # fallback lifetime for the access-token cookie (seconds)
_REFRESH_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.session_cookie_name, path="/")
    response.delete_cookie(settings.refresh_cookie_name, path="/")


def _set_auth_cookies(response: Response, result: AuthResult) -> None:
    if result.expires_at:
        max_age = max(int(result.expires_at) - int(time.time()), 60)
    else:
        max_age = _ACCESS_MAX_AGE

    response.set_cookie(
        key=settings.session_cookie_name,
        value=result.access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
        max_age=max_age,
    )
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=result.refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
        max_age=_REFRESH_MAX_AGE,
    )


@router.post("/signup", response_model=AuthSuccess, status_code=201)
def signup(data: SignupRequest, response: Response) -> AuthSuccess:
    result = auth_service.sign_up(data)
    _set_auth_cookies(response, result)
    return AuthSuccess(message="Account created successfully.", user=result.user)


@router.post("/login", response_model=AuthSuccess)
def login(data: LoginRequest, response: Response) -> AuthSuccess:
    result = auth_service.sign_in(data)
    _set_auth_cookies(response, result)
    return AuthSuccess(message="Signed in successfully.", user=result.user)


@router.get("/me", response_model=AuthSuccess)
def me(request: Request) -> AuthSuccess:
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "UNAUTHENTICATED", "message": "You are not signed in."}},
        )
    user = auth_service.get_current_user(token)
    return AuthSuccess(message="Authenticated.", user=user)


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response) -> None:
    token = request.cookies.get(settings.session_cookie_name)
    auth_service.revoke(token)
    _clear_auth_cookies(response)