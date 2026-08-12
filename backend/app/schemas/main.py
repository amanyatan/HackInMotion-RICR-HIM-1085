"""Pydantic schemas for onboarding, communication, notes, study, profile, dashboard."""

from typing import Any, Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Onboarding
# ---------------------------------------------------------------------------


class OnboardingStepRequest(BaseModel):
    step: int = Field(ge=1, le=5)
    name: Optional[str] = None
    reason: Optional[str] = None
    subjects: Optional[list[str]] = None
    language: Optional[str] = None
    character: Optional[str] = None
    character_voice: Optional[str] = None


class OnboardingCompleteRequest(BaseModel):
    name: Optional[str] = None
    reason: Optional[str] = None
    subjects: Optional[list[str]] = None
    language: str = "en"
    character: str = "kei"
    character_voice: Optional[str] = None


class OnboardingStatusOut(BaseModel):
    current_step: int
    done: bool
    data: Optional[dict] = None


# ---------------------------------------------------------------------------
# Communication
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    character: str = "kei"
    language: str = "en"


class ChatOut(BaseModel):
    message_id: str
    role: str
    content: str
    emotion: str
    character: str
    language: str


class HistoryOut(BaseModel):
    messages: list[dict]


class TranscribeOut(BaseModel):
    text: str
    language: str
    is_mock: bool


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------


class NoteCreate(BaseModel):
    subject: str = Field(min_length=1, max_length=60)
    title: str = Field(min_length=1, max_length=160)
    content: str = Field(min_length=1, max_length=10000)


class NoteUpdate(BaseModel):
    subject: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None


class NoteOut(BaseModel):
    id: str
    subject: str
    title: str
    content: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class NoteListOut(BaseModel):
    notes: list[dict]


# ---------------------------------------------------------------------------
# Study room
# ---------------------------------------------------------------------------


class SessionStartRequest(BaseModel):
    character: str = "kei"
    language: str = "en"


class SessionEventRequest(BaseModel):
    session_id: str
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class SessionOut(BaseModel):
    session_id: str
    status: str = "active"


# ---------------------------------------------------------------------------
# Study plan
# ---------------------------------------------------------------------------


class PlanGenerateRequest(BaseModel):
    request_text: str = Field(min_length=1, max_length=200)
    user_name: Optional[str] = None


class PlanResponse(BaseModel):
    plan: dict


class ReminderRequest(BaseModel):
    user_name: Optional[str] = None


class ReminderResponse(BaseModel):
    text: str
    character: str = "mark"
    language: str = "en"


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class DashboardSummaryOut(BaseModel):
    words_today: int
    minutes_today: int
    total_words: int
    total_minutes: int
    streak_days: int
    subject_breakdown: list[dict] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    character: Optional[str] = None
    language: Optional[str] = None
