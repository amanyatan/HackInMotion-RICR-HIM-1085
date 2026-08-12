"""Communication (companion chat) logic.

Coordinates the full chat pipeline:
  moderation -> provider reply -> persist conversation -> return.
Also serves history and persistence of messages.
"""

from __future__ import annotations

import uuid

from app.db.supabase import repo
from app.services.ai_service import get_ai_provider
from app.services.moderation import moderate_text
from app.utils.logger import logger


def chat(uid: str, message: str, character: str = "kei", language: str = "en") -> dict:
    """Run the chat pipeline and return the companion's reply."""

    # 1) persist the user message (best-effort)
    _persist_message(uid, role="user", content=message, character=character, language=language)

    # 2) moderation gate
    verdict = moderate_text(message)
    if not verdict.allowed:
        reply_text = verdict.fallback
        emotion = "neutral"
        try:
            repo.table.insert(
                "abuse_events",
                {"id": str(uuid.uuid4()), "uid": uid, "reason": verdict.reason, "terms": verdict.flagged_terms, "input": message, "created_at": _now()},
            )
        except Exception as exc:
            logger.warning("Could not record abuse event: %s", exc)
    else:
        # 3) provider reply
        history = get_history(uid, limit=6)
        provider = get_ai_provider()
        result = provider.generate_response(
            user_input=message,
            character=character,
            language=language,
            history=history,
        )
        reply_text = result.text
        emotion = result.emotion

    # 4) persist assistant reply
    assistant_id = _persist_message(uid, role="assistant", content=reply_text, character=character, language=language, emotion=emotion)

    return {
        "message_id": assistant_id,
        "role": "assistant",
        "content": reply_text,
        "emotion": emotion,
        "character": character,
        "language": language,
    }


def get_history(uid: str, limit: int = 20) -> list[dict]:
    try:
        return repo.table.select(
            "conversations",
            columns="role,content,created_at",
            filters={"uid": uid},
            order="created_at",
            desc=True,
            limit=limit,
        )[::-1]
    except Exception as exc:
        logger.warning("Could not read conversations: %s", exc)
        return []


def clear_history(uid: str) -> None:
    try:
        repo.table.delete("conversations", {"uid": uid})
    except Exception as exc:
        logger.warning("Could not clear conversations: %s", exc)


def _persist_message(uid: str, role: str, content: str, character: str, language: str, emotion: str | None = None) -> str:
    mid = str(uuid.uuid4())
    try:
        repo.table.insert(
            "conversations",
            {"id": mid, "uid": uid, "role": role, "content": content, "character": character, "language": language, "emotion": emotion, "created_at": _now()},
        )
    except Exception as exc:
        logger.warning("Could not persist conversation message: %s", exc)
    return mid


def _now() -> str:
    import datetime

    return datetime.datetime.now(datetime.timezone.utc).isoformat()
