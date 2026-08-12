"""Study Plan + Focus Reminder logic.

Two pieces:
1. Block scheduling — the male companion (Mark) plans a study session with the
   user: how many hours, breaks at what intervals. Hard cap at 8 hours.
2. Focus interruptions — when MediaPipe (client-side) notices distraction, the
   backend produces a spoken nudge: "Focus on your study, <name>".

AI text is generated through the configured AI provider (Groq by default) and
falls back to a deterministic template when the provider is unavailable or mock
mode is on. TTS/STT still run through their own providers.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from app.core.config import settings
from app.services.ai_service import get_ai_provider
from app.utils.logger import logger

MAX_HOURS = 8
MIN_HOURS = 0.5
DEFAULT_BREAK_MINUTES = 10

_ERROR_MSG = (
    f"A study session can't be more than 8 hours. Let's plan something up to 8 hours — "
    "how many hours would you like, and how many breaks?"
)


def _extract_int(text: str) -> int | None:
    numbers = re.findall(r"\d+", text or "")
    if not numbers:
        return None
    return int(numbers[0])


# ---------------------------------------------------------------------------
# Plan data
# ---------------------------------------------------------------------------


@dataclass
class StudyPlan:
    total_hours: float
    sessions: list[str] = field(default_factory=list)
    breaks: list[dict] = field(default_factory=list)
    breaks_count: int = 0

    def to_dict(self) -> dict:
        return {
            "total_hours": self.total_hours,
            "total_minutes": int(self.total_hours * 60),
            "sessions": self.sessions,
            "breaks": self.breaks,
            "breaks_count": self.breaks_count,
        }


def _build_schedule(total_hours: float, breaks_count: int) -> tuple[list[str], list[dict]]:
    """Evenly split study time into blocks separated by short breaks."""
    total_minutes = int(total_hours * 60)
    block_count = breaks_count + 1
    block_minutes = max(10, round(total_minutes / block_count))
    break_minutes = DEFAULT_BREAK_MINUTES

    sessions: list[str] = []
    breaks: list[dict] = []
    elapsed = 0
    for i in range(block_count):
        sessions.append(f"{_fmt(elapsed)} – {_fmt(min(elapsed + block_minutes, total_minutes))}")
        elapsed += block_minutes
        if i < breaks_count and elapsed < total_minutes:
            breaks.append({"after_minute": elapsed, "minutes": min(break_minutes, total_minutes - elapsed)})
            elapsed += break_minutes
    return sessions, breaks


def _fmt(minutes: int) -> str:
    h, m = divmod(max(0, minutes), 60)
    return f"{h}h {m:02d}m"


# ---------------------------------------------------------------------------
# Plan generation
# ---------------------------------------------------------------------------


def generate_plan(user_name: str, request_text: str) -> dict | None:
    """Interpret the user's schedule request and return a plan.

    Returns None when the text is too ambiguous (caller re-prompts the user).
    Raises a structured dict when the requested duration exceeds 8 hours.
    """
    hours = _parse_hours(request_text)
    breaks = _parse_breaks(request_text)

    if hours is None:
        # try asking the AI to interpret; on failure stay ambiguous
        return _ai_interpret(user_name, request_text)

    if hours > MAX_HOURS:
        return {"error": "max_8_hours", "message": _ERROR_MSG, "max_hours": MAX_HOURS}

    hours = max(hours, MIN_HOURS)
    if breaks is None:
        breaks = 1 if hours >= 1 else 0

    plan = StudyPlan(total_hours=hours, breaks_count=breaks)
    plan.sessions, plan.breaks = _build_schedule(hours, breaks)
    return plan.to_dict()


def _parse_hours(text: str) -> float | None:
    for match in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|hr|h)\b", (text or "").lower()):
        return float(match.group(1))
    # bare number near "hours"
    if re.search(r"\b(\d+(?:\.\d+)?)\s*$", (text or "").strip()):
        try:
            return float(re.search(r"(\d+(?:\.\d+)?)\s*$", text.strip()).group(1))
        except Exception:
            return None
    return None


def _parse_breaks(text: str) -> int | None:
    lowered = (text or "").lower()
    if "no break" in lowered or "no breaks" in lowered:
        return 0
    m = re.search(r"(\d+)\s*breaks?", lowered)
    if m:
        return int(m.group(1))
    if "break" in lowered:
        # one break unless a count was given
        return 1
    return None


def _ai_interpret(user_name: str, request_text: str) -> dict | None:
    """Let the provider reason about an ambiguous request (best-effort)."""
    try:
        provider = get_ai_provider()
        result = provider.generate_response(
            user_input=(
                f'Parse this study-planning request into JSON with keys "hours" (number) '
                f'and "breaks" (integer, default 1 if unmentioned). Request: "{request_text}". '
                f'Reply with ONLY valid JSON, no other text.'
            ),
            character="mark",
            language="en",
            history=[],
        )
        data = json.loads(result.text.strip())
        hours = float(data.get("hours"))
        if hours > MAX_HOURS:
            return {"error": "max_8_hours", "message": _ERROR_MSG, "max_hours": MAX_HOURS}
        if hours <= 0 or hours < MIN_HOURS:
            return None
        breaks = int(data.get("breaks", 1))
        plan = StudyPlan(total_hours=hours, breaks_count=breaks)
        plan.sessions, plan.breaks = _build_schedule(hours, breaks)
        return plan.to_dict()
    except Exception as exc:
        logger.warning("AI plan interpretation failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Focus reminder
# ---------------------------------------------------------------------------


def focus_reminder(user_name: str) -> dict:
    """Return a short encouragement to pull the user back to studying."""
    name = user_name.strip() or "there"
    # Try the provider for a warm, varied nudge; fall back to template.
    text = _ai_reminder(name)
    return {
        "text": text,
        "character": "mark",
        "language": "en",
    }


def _ai_reminder(name: str) -> str:
    template = f"Focus on your studies, {name}. You are doing great — let's get back to it."
    if settings.mock_mode:
        return template
    try:
        provider = get_ai_provider()
        result = provider.generate_response(
            user_input=(
                f"Say a single, warm one-sentence nudge to a student named '{name}' who just "
                "got distracted, to get them back on task. Do not use emoji. Keep it under "
                "12 words starting with a gentle command like 'Focus' or 'Eyes back on'."
            ),
            character="mark",
            language="en",
            history=[],
            max_tokens=40,
        )
        text = result.text.strip()
        return text if len(text) < 160 else template
    except Exception:
        return template