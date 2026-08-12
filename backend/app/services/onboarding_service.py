"""Onboarding flow logic.

Persists a user's onboarding answers into the `onboarding` table (one row per
user, upserted on each step save). Tracks `current_step` and a `done` flag.
"""

from __future__ import annotations

from app.db.supabase import repo
from app.utils.logger import logger


def get_status(uid: str) -> dict:
    try:
        rows = repo.table.select("onboarding", columns="*", filters={"uid": uid}, limit=1)
        if not rows:
            return {"current_step": 1, "done": False, "data": None}
        row = rows[0]
        return {
            "current_step": int(row.get("current_step", 1)),
            "done": bool(row.get("done", False)),
            "data": row,
        }
    except Exception as exc:
        logger.warning("Could not read onboarding: %s", exc)
        return {"current_step": 1, "done": False, "data": None}


def save_step(uid: str, step: int, payload: dict) -> dict:
    row = {
        "uid": uid,
        "current_step": step,
        "updated_at": _now(),
    }
    # only carry whitelisted fields to avoid dumping arbitrary JSON into SQL
    allowed = {k: payload[k] for k in ("name", "reason", "subjects", "language", "character", "character_voice") if k in payload}
    row.update(allowed)
    try:
        repo.table.upsert("onboarding", row, on_conflict="uid")
    except Exception as exc:
        logger.warning("Could not upsert onboarding: %s", exc)
    return row


def complete(uid: str, final_payload: dict) -> dict:
    row = {"uid": uid, "current_step": 5, "done": True, "updated_at": _now()}
    allowed = {k: final_payload[k] for k in ("name", "reason", "subjects", "language", "character", "character_voice") if k in final_payload}
    row.update(allowed)
    try:
        repo.table.upsert("onboarding", row, on_conflict="uid")
    except Exception as exc:
        logger.warning("Could not complete onboarding: %s", exc)
    return row


def _now() -> str:
    import datetime

    return datetime.datetime.now(datetime.timezone.utc).isoformat()
