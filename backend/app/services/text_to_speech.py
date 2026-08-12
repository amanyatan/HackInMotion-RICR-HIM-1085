"""Text-to-speech (TTS) provider abstraction.

- SarvamAI live provider activates when `SARVAM_API_KEY` is set and
  `MOCK_MODE=false`.
- Mock mode returns a tiny placeholder WAV so the frontend can exercise the
  audio pipeline without network access.

In both cases the service returns a WAV byte payload; the caller may serve it
directly (audio/wav) or save it to a URL.
"""

from __future__ import annotations

import abc
import base64
import struct
import wave
from io import BytesIO

import httpx

from app.core.config import settings
from app.utils.logger import logger
from app.utils.security import sign_payload, verify_signature

# Character voice -> Sarvam speaker mapping (valid speakers verified against
# the Sarvam API as of 2026: anushka, abhilash, manisha, vidya, arya, karun,
# hitesh available for bulbul:v2).

CHARACTER_VOICES: dict[str, str] = {
    "kei": "manisha",
    "mark": "abhilash",
    "mark_alt": "karun",
    "kei_alt": "anushka",
}

# App language codes -> Sarvam target_language_code values.
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


class TTSProvider(abc.ABC):
    name = "abstract"

    @abc.abstractmethod
    def synthesize(self, text: str, voice: str = "kei", language: str = "en") -> bytes:
        """Return raw WAV audio bytes."""


class SarvamTTSProvider(TTSProvider):
    name = "sarvam"

    def __init__(self) -> None:
        self.api_key = settings.sarvam_api_key
        self.base_url = settings.sarvam_api_url

    def synthesize(self, text: str, voice: str = "kei", language: str = "en") -> bytes:
        headers = {"api-subscription-key": self.api_key, "Content-Type": "application/json"}
        # Sarvam REST endpoint: POST /text-to-speech (JSON).
        # Required fields: text, target_language_code. Uses `speaker` + `model`.
        payload = {
            "model": "bulbul:v2",
            "speaker": CHARACTER_VOICES.get(voice, "meera"),
            "target_language_code": _to_sarvam_lang(language),
            "text": text,
            "pace": 1.0,
            "speech_sample_rate": 22050,
        }
        try:
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    f"{self.base_url}/text-to-speech", json=payload, headers=headers
                )
                resp.raise_for_status()
            data = resp.json()
            audios = data.get("audios") or []
            if not audios:
                raise RuntimeError("no audio returned from Sarvam")
            return base64.b64decode(audios[0])
        except Exception as exc:  # pragma: no cover - degraded fallback
            logger.warning("Sarvam TTS failed: %s", exc)
            return _placeholder_wav()


class MockTTSProvider(TTSProvider):
    name = "mock"

    def synthesize(self, text: str, voice: str = "kei", language: str = "en") -> bytes:
        return _placeholder_wav()


def _placeholder_wav(duration_seconds: float = 0.5, sample_rate: int = 8000) -> bytes:
    """Generate a tiny, silent WAV so audio playback works end-to-end in mock."""
    frames = int(duration_seconds * sample_rate)
    pcm = struct.pack("<%dh" % frames, *([0] * frames))
    buf = BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm)
    return buf.getvalue()


_tts_provider: TTSProvider | None = None


def get_tts_provider() -> TTSProvider:
    global _tts_provider
    if _tts_provider is None:
        if settings.mock_mode or not settings.tts_configured:
            _tts_provider = MockTTSProvider()
        else:
            _tts_provider = SarvamTTSProvider()
    return _tts_provider
