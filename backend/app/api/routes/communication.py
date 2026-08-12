"""Communication (companion chat, STT, TTS, history) API routes."""

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import Response

from app.core.config import settings
from app.dependencies import get_current_user
from app.schemas.auth import UserOut
from app.schemas.main import ChatOut, ChatRequest, HistoryOut, TranscribeOut
from app.services import communication_service
from app.services.speech_to_text import get_stt_provider
from app.services.text_to_speech import get_tts_provider
from app.utils.logger import logger

router = APIRouter(prefix="/api/communication", tags=["communication"])

TTS_AUDIO_CACHE_TTL = 3600


@router.post("/chat", response_model=ChatOut)
def chat(data: ChatRequest, user: UserOut = Depends(get_current_user)) -> ChatOut:
    result = communication_service.chat(
        user.id, data.message, character=data.character, language=data.language
    )
    return ChatOut(**result)


@router.get("/history", response_model=HistoryOut)
def history(user: UserOut = Depends(get_current_user)) -> HistoryOut:
    messages = communication_service.get_history(user.id, limit=50)
    return HistoryOut(messages=messages)


@router.delete("/history", status_code=204)
def clear_history(user: UserOut = Depends(get_current_user)) -> None:
    communication_service.clear_history(user.id)


@router.post("/transcribe", response_model=TranscribeOut)
async def transcribe(
    audio: UploadFile = File(...),
    language: str = Form("en"),
    user: UserOut = Depends(get_current_user),
) -> TranscribeOut:
    audio_bytes = await audio.read()
    provider = get_stt_provider()
    result = provider.transcribe(audio_bytes, language)
    return TranscribeOut(text=result.text, language=result.language, is_mock=result.is_mock)


@router.post("/speak")
def speak(
    text: str = Form(..., max_length=4000),
    voice: str = Form("kei"),
    language: str = Form("en"),
    user: UserOut = Depends(get_current_user),
) -> Response:
    """Return WAV audio bytes for the given text (compatible with the companion)."""
    provider = get_tts_provider()
    audio = provider.synthesize(text, voice=voice, language=language)

    # Short-lived, signed URL marker is unnecessary here: we stream audio bytes
    # directly. Cache header keeps repeat playback cheap.
    return Response(
        content=audio,
        media_type="audio/wav",
        headers={
            "Cache-Control": f"private, max-age={TTS_AUDIO_CACHE_TTL}",
            "X-Cosmos-Mock": "true" if settings.mock_mode else "false",
        },
    )
