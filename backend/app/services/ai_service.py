"""AI provider abstraction for companion-reply generation.

Implements a common `AIProvider` interface with live providers (Groq and
Sarvam's chat model) plus a deterministic mock. The factory decides which
to use based on `MOCK_MODE` and available keys.

Design notes (per spec):
- MOCK-first: with no keys (default), we return canned responses.
- Live providers activate automatically as soon as the matching key is present
  and `MOCK_MODE=false`.
- Providers are implemented with plain HTTP (httpx) so no extra SDK is required.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field

import httpx

from app.core.config import settings
from app.utils.logger import logger
from app.utils.mock_data import pick_mock_emotion, pick_mock_reply

# ---------------------------------------------------------------------------
# Output contract
# ---------------------------------------------------------------------------


@dataclass
class AIResult:
    text: str
    emotion: str = "neutral"
    usage_guess: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Provider interface
# ---------------------------------------------------------------------------


class AIProvider(abc.ABC):
    name: str = "abstract"

    @abc.abstractmethod
    def generate_response(
        self,
        *,
        prompt: str,
        user_input: str,
        character: str,
        language: str,
        history: list[dict] | None = None,
        max_tokens: int = 300,
    ) -> AIResult:
        """Return a companion reply string for the given user input."""

    def generate_structured_response(self, *, prompt: str, **params) -> dict:
        """Optional structured output. Defaults to a text-only result."""
        result = self.generate_response(prompt=prompt, user_input=params.get("user_input", ""), character=params.get("character", "kei"), language=params.get("language", "en"))
        return {"text": result.text, "emotion": result.emotion}


# ---------------------------------------------------------------------------
# Live providers
# ---------------------------------------------------------------------------


class GroqProvider(AIProvider):
    """Companion replies via Groq's OpenAI-compatible chat completions API."""

    name = "groq"

    def __init__(self) -> None:
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.base_url = "https://api.groq.com/openai/v1"

    def generate_response(self, **kwargs) -> AIResult:
        messages = self._build_messages(kwargs)
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 300),
            "temperature": 0.7,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    f"{self.base_url}/chat/completions", json=payload, headers=headers
                )
                resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"].strip()
        except Exception as exc:  # pragma: no cover - degraded fallback
            logger.warning("Groq provider failed: %s", exc)
            return AIResult(text=pick_mock_reply(kwargs.get("user_input", "")), emotion=pick_mock_emotion(kwargs.get("user_input", "")))
        return AIResult(text=text, emotion=pick_mock_emotion(text))

    @staticmethod
    def _build_messages(kwargs: dict) -> list[dict]:
        system = (
            f"You are the friendly study companion '{kwargs.get('character', 'kei')}'. "
            f"Reply in language '{kwargs.get('language', 'en')}'. Be warm, encouraging, "
            "simple and encouraging for a learner. Never give the answer directly - "
            "guide the user to figure it out. Keep replies short (under 3 sentences)."
        )
        messages = [{"role": "system", "content": system}]
        for item in kwargs.get("history") or []:
            role = "assistant" if item.get("role") == "assistant" else "user"
            messages.append({"role": role, "content": item.get("content", "")})
        messages.append({"role": "user", "content": kwargs.get("user_input", "")})
        return messages


class SarvamChatProvider(AIProvider):
    """Companion replies via Sarvam's OpenAI-compatible chat completions API.

    Uses the same `api-subscription-key` credential as STT/TTS. This is the
    provider that is live when only the Sarvam key is available.
    """

    name = "sarvam"

    def __init__(self) -> None:
        self.api_key = settings.sarvam_api_key
        self.base_url = settings.sarvam_api_url
        self.model = settings.sarvam_chat_model

    def generate_response(self, **kwargs) -> AIResult:
        messages = self._build_messages(kwargs)
        payload = {
            "model": self.model,
            "messages": messages,
            # Disable built-in reasoning so `content` is always populated for a
            # snappy companion reply, and leave room for the real answer.
            "reasoning_effort": None,
            "max_tokens": kwargs.get("max_tokens", 500),
        }
        headers = {"api-subscription-key": self.api_key, "Content-Type": "application/json"}
        try:
            with httpx.Client(timeout=45) as client:
                resp = client.post(
                    f"{self.base_url}/v1/chat/completions", json=payload, headers=headers
                )
                resp.raise_for_status()
            data = resp.json()
            message = data["choices"][0]["message"]
            text = (message.get("content") or message.get("reasoning_content") or "").strip()
            if not text:
                raise RuntimeError("empty completion from Sarvam")
        except Exception as exc:  # pragma: no cover - degraded fallback
            logger.warning("Sarvam chat provider failed: %s", exc)
            return AIResult(text=pick_mock_reply(kwargs.get("user_input", "")), emotion=pick_mock_emotion(kwargs.get("user_input", "")))
        return AIResult(text=text, emotion=pick_mock_emotion(text))

    @staticmethod
    def _build_messages(kwargs: dict) -> list[dict]:
        # NOTE: keep persona inline in the user message for guaranteed content.
        persona = (
            f"You are the friendly study companion '{kwargs.get('character', 'kei')}'. "
            f"Reply in language '{kwargs.get('language', 'en')}'. Be warm, encouraging, "
            "simple and encouraging for a learner. Never give the answer directly - "
            "guide the user to figure it out. Keep replies short (under 3 sentences)."
        )
        messages: list[dict] = []
        for item in kwargs.get("history") or []:
            role = "assistant" if item.get("role") == "assistant" else "user"
            messages.append({"role": role, "content": item.get("content", "")})
        messages.append({"role": "user", "content": f"{persona}\n\nuser: {kwargs.get('user_input', '')}"})
        return messages


# ---------------------------------------------------------------------------
# Mock provider
# ---------------------------------------------------------------------------


class MockProvider(AIProvider):
    name = "mock"

    def generate_response(self, **kwargs) -> AIResult:
        user_input = kwargs.get("user_input", "")
        text = pick_mock_reply(user_input)
        emotion = pick_mock_emotion(user_input)
        return AIResult(text=text, emotion=emotion)

    def generate_structured_response(self, *, prompt: str, **params) -> dict:
        result = self.generate_response(**params)
        return {
            "text": result.text,
            "emotion": result.emotion,
            "is_mock": True,
        }


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_PROVIDERS: dict[str, AIProvider] = {}


def get_ai_provider() -> AIProvider:
    """Return the appropriate AI provider based on config + available keys.

    Cached after first resolution.
    """
    if _PROVIDERS:
        return next(iter(_PROVIDERS.values()))

    if settings.mock_mode:
        provider = MockProvider()
    else:
        provider = _resolve_live()
    _PROVIDERS[provider.name] = provider
    return provider


def _resolve_live() -> AIProvider:
    preferred = settings.ai_provider
    if preferred == "groq" and settings.groq_api_key:
        return GroqProvider()
    if preferred == "sarvam" and settings.sarvam_api_key:
        return SarvamChatProvider()
    # Auto: pick from configured live providers. Preferred order: groq, then
    # sarvam (which also covers STT/TTS).
    if settings.groq_api_key:
        return GroqProvider()
    if settings.sarvam_api_key:
        return SarvamChatProvider()
    # No keys configured despite live mode → be safe and mock.
    logger.warning("Live mode requested but no AI keys present; using mock.")
    return MockProvider()
