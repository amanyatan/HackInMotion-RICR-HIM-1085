"""Study room API routes."""

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user
from app.schemas.auth import UserOut
from app.schemas.main import (
    SessionEventRequest,
    SessionOut,
    SessionStartRequest,
)
from app.services.study_service import study_service
from app.utils.logger import logger

router = APIRouter(prefix="/api/study_room", tags=["study_room"])


@router.post("/session/start", response_model=SessionOut)
def start_session(
    data: SessionStartRequest, user: UserOut = Depends(get_current_user)
) -> SessionOut:
    result = study_service.start(user.id, character=data.character, language=data.language)
    return SessionOut(**result)


@router.post("/session/pause", response_model=SessionOut)
def pause_session(payload: dict, user: UserOut = Depends(get_current_user)) -> SessionOut:
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=422, detail={"error": {"code": "VALIDATION_ERROR", "message": "session_id is required."}})
    try:
        result = study_service.pause(session_id, user.id)
    except KeyError:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Session not found."}})
    return SessionOut(**result)


@router.post("/session/resume", response_model=SessionOut)
def resume_session(payload: dict, user: UserOut = Depends(get_current_user)) -> SessionOut:
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=422, detail={"error": {"code": "VALIDATION_ERROR", "message": "session_id is required."}})
    try:
        result = study_service.resume(session_id, user.id)
    except KeyError:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Session not found."}})
    return SessionOut(**result)


@router.post("/session/complete", response_model=SessionOut)
def complete_session(payload: dict, user: UserOut = Depends(get_current_user)) -> SessionOut:
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=422, detail={"error": {"code": "VALIDATION_ERROR", "message": "session_id is required."}})
    try:
        result = study_service.complete(session_id, user.id)
    except KeyError:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Session not found."}})
    return SessionOut(**result)


@router.post("/event")
def add_event(data: SessionEventRequest, user: UserOut = Depends(get_current_user)) -> dict:
    try:
        record = study_service.add_event(data.session_id, user.id, data.type, data.payload)
    except KeyError:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Session not found."}})
    return {"event_id": record["id"], "recorded": True}


@router.get("/session/current", response_model=SessionOut | None)
def current_session(
    session_id: str | None = None, user: UserOut = Depends(get_current_user)
) -> SessionOut | None:
    result = study_service.current(user.id, session_id=session_id)
    if result is None:
        raise HTTPException(status_code=404, detail={"error": {"code": "NO_SESSION", "message": "No active study session."}})
    return SessionOut(**result)
