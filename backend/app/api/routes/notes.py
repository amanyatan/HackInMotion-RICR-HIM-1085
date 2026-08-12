"""Notes API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_current_user
from app.schemas.auth import UserOut
from app.schemas.main import NoteCreate, NoteListOut, NoteOut, NoteUpdate
from app.services import notes_service

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.get("", response_model=NoteListOut)
def list_notes(
    subject: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    user: UserOut = Depends(get_current_user),
) -> NoteListOut:
    notes = notes_service.list_notes(user.id, subject=subject, limit=limit)
    return NoteListOut(notes=notes)


@router.post("", response_model=NoteOut, status_code=201)
def create_note(data: NoteCreate, user: UserOut = Depends(get_current_user)) -> NoteOut:
    note = notes_service.create_note(user.id, data.subject, data.title, data.content)
    return NoteOut(**note)


@router.patch("/{note_id}", response_model=NoteOut)
def update_note(
    note_id: str, data: NoteUpdate, user: UserOut = Depends(get_current_user)
) -> NoteOut:
    updated = notes_service.update_note(user.id, note_id, data.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Note not found."}})
    return NoteOut(**updated)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: str, user: UserOut = Depends(get_current_user)) -> None:
    if not notes_service.delete_note(user.id, note_id):
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Note not found."}})
