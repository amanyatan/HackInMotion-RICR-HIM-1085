"""Speech-to-text (STT) provider abstraction.

- SarvamAI live provider activates when `SARVAM_API_KEY` is set and
  `MOCK_MODE=false`.
- Default is the mock provider, which returns a canned transcript so the
  speech pipeline can be tested end-to-end on the frontend.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.utils.logger import logger
from app.utils.mock_data import MOCK_TRANSCRIPT

# App language codes -> Sarvam language_code values.
_LANG_MAP: dict[str, str] = {
    "en": "en-IN",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "mr": "mr-IN",
    "gu": "gu-IN",
    "bn": "bn-IN",
    "pa": "pa-IN",
    "od": "od-IN",
}


def _to_sarvam_lang(language: str) -> str:
    base = (language or "en").split("-")[0].lower()
    return _LANG_MAP.get(base, "en-IN")


@dataclass
class Transcript:
    text: str
    language: str = "en"
    is_mock: bool = False


class STTProvider(abc.ABC):
    name = "abstract"

    @abc.abstractmethod
    def transcribe(self, audio_bytes: bytes, language: str = "en") -> Transcript:
        """Convert audio to text."""


class SarvamSTTProvider(STTProvider):
    name = "sarvam"

    def __init__(self) -> None:
        self.api_key = settings.sarvam_api_key
        self.base_url = settings.sarvam_api_url

    def transcribe(self, audio_bytes: bytes, language: str = "en") -> Transcript:
        headers = {"api-subscription-key": self.api_key}
        # Sarvam REST endpoint: POST /speech-to-text (multipart).
        # `mode=transcribe` requires the saaras:v3 model.
        try:
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    f"{self.base_url}/speech-to-text",
                    headers=headers,
                    files={"file": ("audio.wav", audio_bytes, "audio/wav")},
                    data={"model": "saaras:v3", "mode": "transcribe", "language_code": _to_sarvam_lang(language)},
                )
                resp.raise_for_status()
            data = resp.json()
            text = str(data.get("transcript") or "").strip()
            lang = str(data.get("language_code") or language)
            if not text:
                raise RuntimeError("empty transcript from Sarvam")
            return Transcript(text=text, language=lang, is_mock=False)
        except Exception as exc:  # pragma: no cover - degraded fallback
            logger.warning("Sarvam STT failed: %s", exc)
            return Transcript(text=MOCK_TRANSCRIPT, language=language, is_mock=True)


class MockSTTProvider(STTProvider):
    name = "mock"

    def transcribe(self, audio_bytes: bytes, language: str = "en") -> Transcript:
        return Transcript(text=MOCK_TRANSCRIPT, language=language, is_mock=True)


_stt_provider: STTProvider | None = None


def get_stt_provider() -> STTProvider:
    global _stt_provider
    if _stt_provider is None:
        if settings.mock_mode or not settings.stt_configured:
            _stt_provider = MockSTTProvider()
        else:
            _stt_provider = SarvamSTTProvider()
    return _stt_provider
