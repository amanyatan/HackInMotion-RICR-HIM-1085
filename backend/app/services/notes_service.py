"""Notes CRUD logic (study notes / saved passages)."""

from __future__ import annotations

import uuid

from app.db.supabase import repo
from app.utils.logger import logger


def list_notes(uid: str, subject: str | None = None, limit: int = 50) -> list[dict]:
    filters = {"uid": uid}
    if subject:
        filters["subject"] = subject
    try:
        return repo.table.select(
            "notes", columns="*", filters=filters, order="updated_at", desc=True, limit=limit
        )
    except Exception as exc:
        logger.warning("Could not list notes: %s", exc)
        return []


def get_note(uid: str, note_id: str) -> dict | None:
    try:
        rows = repo.table.select("notes", columns="*", filters={"id": note_id, "uid": uid}, limit=1)
        return rows[0] if rows else None
    except Exception as exc:
        logger.warning("Could not get note: %s", exc)
        return None


def create_note(uid: str, subject: str, title: str, content: str) -> dict:
    payload = {
        "id": str(uuid.uuid4()),
        "uid": uid,
        "subject": subject,
        "title": title,
        "content": content,
        "created_at": _now(),
        "updated_at": _now(),
    }
    try:
        row = repo.table.insert("notes", payload)
        return row[0] if row else payload
    except Exception as exc:
        logger.warning("Could not create note: %s", exc)
        return payload


def update_note(uid: str, note_id: str, updates: dict) -> dict | None:
    allowed = {k: updates[k] for k in ("subject", "title", "content") if k in updates}
    allowed["updated_at"] = _now()
    try:
        rows = repo.table.update("notes", allowed, {"id": note_id, "uid": uid})
        return rows[0] if rows else None
    except Exception as exc:
        logger.warning("Could not update note: %s", exc)
        return None


def delete_note(uid: str, note_id: str) -> bool:
    try:
        repo.table.delete("notes", {"id": note_id, "uid": uid})
        return True
    except Exception as exc:
        logger.warning("Could not delete note: %s", exc)
        return False


def _now() -> str:
    import datetime

    return datetime.datetime.now(datetime.timezone.utc).isoformat()
