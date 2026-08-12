"""Analytics / dashboard summary logic.

Aggregates user stats (today's words, minutes, streaks, and simple subject
breakdown) from the persisted tables. In mock mode with an empty database it
returns a safe zero-based summary so the dashboard renders immediately.
"""

from __future__ import annotations

import datetime as dt
import uuid

from app.db.supabase import repo
from app.utils.logger import logger


def _today_iso() -> str:
    return dt.date.today().isoformat()


def upsert_today(uid: str, words: int = 0, minutes: int = 0) -> None:
    """Upsert today's aggregate row (used by the study room on completion)."""
    try:
        today = _today_iso()
        existing = repo.table.select(
            "dashboard_stats",
            columns="*",
            filters={"uid": uid, "date": today},
            limit=1,
        )
        if existing:
            row = existing[0]
            repo.table.update(
                "dashboard_stats",
                {"words_typed": row.get("words_typed", 0) + words, "minutes_studied": row.get("minutes_studied", 0) + minutes},
                {"id": row["id"]},
            )
        else:
            repo.table.insert(
                "dashboard_stats",
                {"id": str(uuid.uuid4()), "uid": uid, "date": today, "words_typed": words, "minutes_studied": minutes},
            )
    except Exception as exc:
        logger.warning("Could not upsert dashboard_stats: %s", exc)


def get_summary(uid: str) -> dict:
    """Build the dashboard summary payload."""
    today = _today_iso()
    words_today = 0
    minutes_today = 0
    total_words = 0
    total_minutes = 0
    subject_map: dict[str, int] = {}

    try:
        rows = repo.table.select(
            "dashboard_stats", columns="*", filters={"uid": uid}
        )
        for row in rows:
            total_words += int(row.get("words_typed") or 0)
            total_minutes += int(row.get("minutes_studied") or 0)
            if row.get("date") == today:
                words_today += int(row.get("words_typed") or 0)
                minutes_today += int(row.get("minutes_studied") or 0)
    except Exception as exc:
        logger.warning("Could not read dashboard_stats: %s", exc)

    # best-effort streak: consecutive days with >0 minutes
    streak = _compute_streak(uid)

    try:
        sessions = repo.table.select(
            "study_sessions", columns="subject,session_id", filters={"uid": uid}
        )
        for row in sessions:
            subject = row.get("subject") or "general"
            subject_map[subject] = subject_map.get(subject, 0) + 1
    except Exception:
        pass

    return {
        "words_today": words_today,
        "minutes_today": minutes_today,
        "total_words": total_words,
        "total_minutes": total_minutes,
        "streak_days": streak,
        "subject_breakdown": sorted(
            ({"subject": k, "sessions": v} for k, v in subject_map.items()),
            key=lambda x: x["sessions"],
            reverse=True,
        ),
    }


def _compute_streak(uid: str) -> int:
    try:
        rows = repo.table.select("dashboard_stats", columns="date,minutes_studied", filters={"uid": uid})
        active_days = {
            row["date"] for row in rows if int(row.get("minutes_studied") or 0) > 0
        }
    except Exception:
        return 0
    if not active_days:
        return 0
    streak = 0
    day = dt.date.today()
    if day.isoformat() in active_days:
        while day.isoformat() in active_days:
            streak += 1
            day -= dt.timedelta(days=1)
    else:
        day -= dt.timedelta(days=1)
        while day.isoformat() in active_days:
            streak += 1
            day -= dt.timedelta(days=1)
    return streak
