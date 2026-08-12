"""Isolated Supabase access layer.

All Supabase communication happens here. Route handlers must never call
Supabase directly — they go through `app.services.*`.

Provides:
- Auth operations (existing)
- A generic table repository for the app tables
  (profiles, onboarding, conversations, notes, study_sessions, study_events,
   dashboard_stats, user_preferences, abuse_events).
"""

from __future__ import annotations

from typing import Any

from supabase import Client, create_client

from app.core.config import settings
from app.utils.logger import logger

# Tables the backend may read/write. Operation is best-effort: if a table does
# not exist yet (schema not applied), we log and degrade gracefully so auth and
# health checks keep working.
AUTH_TABLES = {
    "profiles",
    "onboarding",
    "conversations",
    "messages",
    "notes",
    "study_sessions",
    "study_events",
    "study_plans",
    "dashboard_stats",
    "user_preferences",
    "abuse_events",
}


class _TableRepository:
    """Generic Supabase table accessor bound to a client."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def _table(self, table: str):
        if table not in AUTH_TABLES:
            raise RuntimeError(f"Table '{table}' is not allowed via this repository")
        return self._client.table(table)

    def select(self, table: str, columns: str = "*", filters: dict[str, Any] | None = None, order: str | None = None, desc: bool = False, limit: int | None = None) -> list[dict]:
        query = self._table(table).select(columns)
        for key, value in (filters or {}).items():
            query = query.eq(key, value)
        if order:
            query = query.order(order, desc=desc)
        if limit:
            query = query.limit(limit)
        resp = query.execute()
        return list(resp.data or [])

    def insert(self, table: str, payload: dict) -> list[dict]:
        resp = self._table(table).insert(payload).execute()
        return list(resp.data or [])

    def update(self, table: str, payload: dict, filters: dict[str, Any]) -> list[dict]:
        query = self._table(table).update(payload)
        for key, value in filters.items():
            query = query.eq(key, value)
        resp = query.execute()
        return list(resp.data or [])

    def upsert(self, table: str, payload: dict, on_conflict: str | None = None) -> list[dict]:
        kwargs: dict[str, Any] = {}
        if on_conflict:
            kwargs["on_conflict"] = on_conflict
        resp = self._table(table).upsert(payload, **kwargs).execute()
        return list(resp.data or [])

    def delete(self, table: str, filters: dict[str, Any]) -> int:
        query = self._table(table).delete()
        for key, value in filters.items():
            query = query.eq(key, value)
        resp = query.execute()
        return len(resp.data or [])


class SupabaseAuthRepository:
    def __init__(self) -> None:
        self._url = settings.supabase_url
        self._service_role_key = settings.supabase_service_role_key
        self._client: Client | None = None

    def _ensure(self) -> Client:
        if not self._url or not self._service_role_key:
            raise RuntimeError("Supabase credentials are not configured (backend/.env)")
        if self._client is None:
            self._client = create_client(self._url, self._service_role_key)
        return self._client

    # ----- Auth -----
    def create_user(self, email: str, password: str):
        return self._ensure().auth.admin.create_user(
            {"email": email, "password": password, "email_confirm": True}
        )

    def sign_in_with_password(self, email: str, password: str):
        return self._ensure().auth.sign_in_with_password({"email": email, "password": password})

    def get_user(self, access_token: str):
        return self._ensure().auth.get_user(access_token)

    def sign_out(self, access_token: str | None) -> None:
        if access_token:
            self._ensure().auth.admin.sign_out(access_token)

    # ----- Generic table access -----
    @property
    def table(self) -> _TableRepository:
        return _TableRepository(self._ensure())

    # ----- helpers used by services -----
    def upsert_profile(self, profile: dict) -> None:
        self.table.upsert("profiles", profile, on_conflict="id")

    def get_profile(self, uid: str) -> list[dict]:
        return self.table.select("profiles", columns="*", filters={"id": uid}, limit=1)


repo = SupabaseAuthRepository()
