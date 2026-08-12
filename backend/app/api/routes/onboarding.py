"""Onboarding API routes."""

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.auth import UserOut
from app.schemas.main import OnboardingCompleteRequest, OnboardingStatusOut, OnboardingStepRequest
from app.services import onboarding_service

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


@router.get("/status", response_model=OnboardingStatusOut)
def status(user: UserOut = Depends(get_current_user)) -> OnboardingStatusOut:
    result = onboarding_service.get_status(user.id)
    return OnboardingStatusOut(**result)


@router.post("/step", response_model=OnboardingStatusOut)
def save_step(
    data: OnboardingStepRequest, user: UserOut = Depends(get_current_user)
) -> OnboardingStatusOut:
    onboarding_service.save_step(user.id, data.step, data.model_dump())
    result = onboarding_service.get_status(user.id)
    return OnboardingStatusOut(**result)


@router.post("/complete", response_model=OnboardingStatusOut)
def complete(
    data: OnboardingCompleteRequest, user: UserOut = Depends(get_current_user)
) -> OnboardingStatusOut:
    onboarding_service.complete(user.id, data.model_dump())
    result = onboarding_service.get_status(user.id)
    return OnboardingStatusOut(**result)
