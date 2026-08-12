"""Pydantic schemas for the auth API.

All server-side validation lives here. Never trust client-side validation.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirmPassword: str = Field(min_length=1)

    @model_validator(mode="after")
    def _passwords_match(self) -> "SignupRequest":
        if self.password != self.confirmPassword:
            raise ValueError("Passwords do not match.")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None


class AuthSuccess(BaseModel):
    message: str
    user: UserOut


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class AuthResult(BaseModel):
    """Internal result carrying the session for cookie handling.

    Never returned to the client as JSON.
    """

    user: UserOut
    access_token: str
    refresh_token: str
    expires_at: Optional[int] = None