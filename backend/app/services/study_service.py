"""Study session logic.

Owns lifecycle of a study session (start/pause/resume/complete) plus event
collection, and keeps the lightweight in-memory/database state used by the
study room. Analytics aggregation lives in `analytics_service`.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from app.db.supabase import repo
from app.models.enums import Language, StudyStatus


@dataclass
class SessionState:
    session_id: str
    status: StudyStatus = StudyStatus.IN_PROGRESS
    words_typed: int = 0
    read_time_seconds: int = 0
    duration_seconds: int = 0
    started_at: float = field(default_factory=time.time)
    _last_event_at: float = field(default_factory=time.time)
    _paused_accum: int = 0

    def pause(self) -> None:
        self._paused_accum += self._elapsed_since_last()
        self.status = StudyStatus.PAUSED
        self._last_event_at = time.time()

    def resume(self) -> None:
        if self.status == StudyStatus.PAUSED:
            self._last_event_at = time.time()
            self.status = StudyStatus.IN_PROGRESS

    def complete(self) -> int:
        if self.status in (StudyStatus.COMPLETED, StudyStatus.PAUSED):
            self._paused_accum += self._elapsed_since_last()
        self.duration_seconds = int(self._paused_accum)
        self.status = StudyStatus.COMPLETED
        return self.duration_seconds

    def _elapsed_since_last(self) -> float:
        now = time.time()
        delta = now - self._last_event_at
        self._last_event_at = now
        return delta


class StudyService:
    def __init__(self) -> None:
        # In-memory active sessions. In a multi-instance deploy persist this to
        # Redis/Supabase; acceptable for the demo.
        self._sessions: dict[str, SessionState] = {}

    def start(self, uid: str, character: str = "kei", language: str = Language.EN.value) -> dict:
        session_id = str(uuid.uuid4())
        state = SessionState(session_id=session_id)
        self._sessions[session_id] = state

        # best-effort persistence
        try:
            repo.table.insert(
                "study_sessions",
                {
                    "id": session_id,
                    "uid": uid,
                    "character": character,
                    "language": language,
                    "status": StudyStatus.IN_PROGRESS.value,
                    "started_at": _iso(time.time()),
                },
            )
        except Exception as exc:
            _log_table_error("study_sessions", exc)

        return self._to_dict(session_id)

    def pause(self, session_id: str, uid: str) -> dict:
        state = self._require(session_id, uid)
        state.pause()
        self._persist_status(session_id, uid, state.status.value)
        return self._to_dict(session_id)

    def resume(self, session_id: str, uid: str) -> dict:
        state = self._require(session_id, uid)
        state.resume()
        self._persist_status(session_id, uid, state.status.value)
        return self._to_dict(session_id)

    def complete(self, session_id: str, uid: str, content: str | None = None) -> dict:
        state = self._require(session_id, uid)
        duration = state.complete()
        self._persist_status(session_id, uid, StudyStatus.COMPLETED.value)
        try:
            repo.table.update(
                "study_sessions",
                {"status": StudyStatus.COMPLETED.value, "duration_seconds": duration, "ended_at": _iso(time.time())},
                {"id": session_id, "uid": uid},
            )
        except Exception as exc:
            _log_table_error("study_sessions", exc)
        self._sessions.pop(session_id, None)
        return self._to_dict(session_id)

    def add_event(self, session_id: str, uid: str, event_type: str, payload: dict) -> dict:
        self._require(session_id, uid)
        record = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "uid": uid,
            "type": event_type,
            "payload": payload or {},
            "created_at": _iso(time.time()),
        }
        try:
            repo.table.insert("study_events", record)
        except Exception as exc:
            _log_table_error("study_events", exc)
        return record

    def current(self, uid: str, session_id: str | None = None) -> dict | None:
        # Prefer the explicitly-passed session id; else the most recent one.
        target = session_id or self._latest_for(uid)
        if not target:
            return None
        state = self._sessions.get(target)
        if not state:
            return None
        return self._to_dict(target)

    def _latest_for(self, uid: str) -> str | None:
        try:
            rows = repo.table.select(
                "study_sessions",
                columns="id",
                filters={"uid": uid, "status": StudyStatus.IN_PROGRESS.value},
                order="started_at",
                desc=True,
                limit=1,
            )
            return rows[0]["id"] if rows else None
        except Exception:
            return None

    def _require(self, session_id: str, uid: str) -> SessionState:
        state = self._sessions.get(session_id)
        if not state:
            raise KeyError(session_id)
        return state

    def _persist_status(self, session_id: str, uid: str, status: str) -> None:
        try:
            repo.table.update(
                "study_sessions", {"status": status}, {"id": session_id, "uid": uid}
            )
        except Exception as exc:
            _log_table_error("study_sessions", exc)

    @staticmethod
    def _to_dict(session_id: str) -> dict:
        return {"session_id": session_id, "status": "active"}


def _iso(ts: float) -> str:
    import datetime

    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).isoformat()


def _log_table_error(table: str, exc: Exception) -> None:
    from app.utils.logger import logger

    logger.warning("Could not touch table '%s': %s", table, exc)


study_service = StudyService()
