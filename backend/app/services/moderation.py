"""Simple content moderation.

Detects obviously unsafe/off-topic input and returns a structured verdict plus
an optional safe fallback. Hook points for a heavier model remain in place.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Keyword-based filters. In a production system this would sit in front of a
# dedicated moderation model; here we keep a deterministic, dependency-free
# implementation.
_BLOCKED_KEYWORDS: set[str] = {
    "suicide", "kill myself", "self harm", "self-harm", "cut myself",
}

_OFF_TOPIC_KEYWORDS: set[str] = {
    "porn", "sex ", "nsfw", "drugs", "gambling",
}


@dataclass
class ModerationVerdict:
    allowed: bool = True
    reason: str | None = None
    flagged: bool = False
    flagged_terms: list[str] = field(default_factory=list)
    fallback: str | None = None


_SAFE_FALLBACK = (
    "That topic is outside what I can help with, but I'd love to keep "
    "studying with you. Tell me about the subject you're working on!"
)


def moderate_text(text: str) -> ModerationVerdict:
    lowered = (text or "").lower().strip()
    if not lowered:
        return ModerationVerdict()
    flagged = [kw for kw in _BLOCKED_KEYWORDS | _OFF_TOPIC_KEYWORDS if kw in lowered]

    # Blocked terms are disallowed outright with a caring fallback.
    for kw in _BLOCKED_KEYWORDS:
        if kw in lowered:
            return ModerationVerdict(
                allowed=False,
                reason="blocked",
                flagged=True,
                flagged_terms=[kw],
                fallback=_SAFE_FALLBACK,
            )

    if flagged:
        return ModerationVerdict(
            allowed=False,
            reason="off_topic",
            flagged=True,
            flagged_terms=flagged,
            fallback=_SAFE_FALLBACK,
        )
    return ModerationVerdict()
