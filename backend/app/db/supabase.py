"""Isolated Supabase access layer.

All Supabase communication happens here. Route handlers must never call
Supabase directly — they go through `app.services.auth_service`.
"""

from supabase import create_client

from app.core.config import settings


class SupabaseAuthRepository:
    def __init__(self) -> None:
        self._url = settings.supabase_url
        self._service_role_key = settings.supabase_service_role_key
        self._client = None

    def _ensure(self):
        if not self._url or not self._service_role_key:
            raise RuntimeError("Supabase credentials are not configured (backend/.env)")
        if self._client is None:
            self._client = create_client(self._url, self._service_role_key)
        return self._client

    def create_user(self, email: str, password: str):
        client = self._ensure()
        return client.auth.admin.create_user(
            {"email": email, "password": password, "email_confirm": True}
        )

    def sign_in_with_password(self, email: str, password: str):
        client = self._ensure()
        return client.auth.sign_in_with_password({"email": email, "password": password})

    def get_user(self, access_token: str):
        client = self._ensure()
        return client.auth.get_user(access_token)

    def sign_out(self, access_token: str | None) -> None:
        client = self._ensure()
        if access_token:
            client.auth.admin.sign_out(access_token)

    # ----- optional `profiles` table access (best-effort) -----

    def upsert_profile(self, profile: dict) -> None:
        client = self._ensure()
        client.table("profiles").upsert(profile).execute()

    def get_profile(self, uid: str) -> list[dict]:
        client = self._ensure()
        response = client.table("profiles").select("name").eq("id", uid).limit(1).execute()
        return list(response.data or [])