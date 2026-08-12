"""Mock/canned data for MOCK_MODE.

Used so the entire API is demoable without any third-party keys. Every response
is deterministic and never ties to real provider calls.
"""

from __future__ import annotations

# Supported metadata (mirrors constants the frontend uses).
CHARACTERS: list[str] = ["kei", "mark"]
LANGUAGES: list[str] = ["en", "ja", "ko", "zh"]
SUBJECTS: list[str] = [
    "mathematics",
    "physics",
    "chemistry",
    "biology",
    "computer_science",
    "history",
    "literature",
    "languages",
]

# Character voice -> display language mapping used by the frontend.
EMOTION_POOL: list[str] = [
    "neutral",
    "happy",
    "encouraging",
    "curious",
    "calm",
    "excited",
]

MOCK_REPLIES: dict[str, str] = {
    "default": (
        "That's a great question! Let's break it down together — "
        "try explaining it back to me in your own words, and I'll help you refine it."
    ),
    "greeting": (
        "Hello! I'm so glad you're here. Tell me what you'd like to work on today "
        "and we'll get started together."
    ),
    "help": (
        "Here's the plan: pick one small goal, work through it at your own pace, "
        "and I'll stay with you the whole way. What feels most useful right now?"
    ),
    "study": (
        "Let's turn this into a short study session. Pick the subject and a passage, "
        "trade words with me, and we'll build your confidence step by step."
    ),
}

# A deterministic mock transcript for the audio endpoint so the frontend can be
# tested end-to-end even before a real microphone payload is produced.
MOCK_TRANSCRIPT: str = (
    "I want to practice reading this passage about energy today. "
    "Can you help me sound out the hard words?"
)


def pick_mock_reply(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ("hello", "hi ", "hey", "good morning")):
        return MOCK_REPLIES["greeting"]
    if "help" in lowered:
        return MOCK_REPLIES["help"]
    if any(word in lowered for word in ("study", "read", "practice")):
        return MOCK_REPLIES["study"]
    return MOCK_REPLIES["default"]


def pick_mock_emotion(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ("sad", "tired", "stuck", "hard", "frustrat")):
        return "encouraging"
    if any(word in lowered for word in ("great", "yay", "excited", "fun", "awesome")):
        return "happy"
    if any(word in lowered for word in ("?", "how", "why", "what")):
        return "curious"
    return "neutral"
