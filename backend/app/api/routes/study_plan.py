"""Study Plan + Focus Reminder API routes."""

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.dependencies import get_current_user
from app.db.supabase import repo
from app.schemas.auth import UserOut
from app.schemas.main import PlanGenerateRequest, PlanResponse, ReminderRequest, ReminderResponse
from app.services import study_plan_service
from app.services.text_to_speech import get_tts_provider
from fastapi.responses import Response

router = APIRouter(prefix="/api/study_plan", tags=["study_plan"])


@router.post("/generate", response_model=PlanResponse)
def generate(
    data: PlanGenerateRequest, user: UserOut = Depends(get_current_user)
) -> PlanResponse:
    plan = study_plan_service.generate_plan(
        user_name=data.user_name or "there", request_text=data.request_text
    )
    if plan is None:
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "PLAN_AMBIGUOUS",
                    "message": "I couldn't understand that. How many hours of study do you want?",
                }
            },
        )
    if plan.get("error") == "max_8_hours":
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "MAX_8_HOURS",
                    "message": plan["message"],
                    "max_hours": plan.get("max_hours"),
                }
            },
        )
    # best-effort persist
    try:
        repo.table.insert(
            "study_plans",
            {
                "uid": user.id,
                "total_hours": plan["total_hours"],
                "breaks_count": plan["breaks_count"],
                "plan": plan,
            },
        )
    except Exception as exc:
        from app.utils.logger import logger

        logger.warning("Could not persist study plan: %s", exc)
    return PlanResponse(plan=plan)


@router.post("/reminder", response_model=ReminderResponse)
def reminder(
    data: ReminderRequest, user: UserOut = Depends(get_current_user)
) -> ReminderResponse:
    result = study_plan_service.focus_reminder(user_name=data.user_name or user.name or "there")
    return ReminderResponse(
        text=result["text"],
        character=result["character"],
        language=result["language"],
    )


@router.post("/reminder/speak")
def reminder_speak(
    data: ReminderRequest, user: UserOut = Depends(get_current_user)
) -> Response:
    """TTS the focus nudge so the companion 'speaks' it aloud."""
    result = study_plan_service.focus_reminder(data.user_name or user.name or "there")
    provider = get_tts_provider()
    audio = provider.synthesize(result["text"], voice="mark", language=result["language"])
    return Response(
        content=audio,
        media_type="audio/wav",
        headers={"X-Cosmos-Mock": "true" if settings.mock_mode else "false"},
    )