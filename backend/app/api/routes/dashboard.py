"""Dashboard API route."""

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.auth import UserOut
from app.schemas.main import DashboardSummaryOut
from app.services import analytics_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryOut)
def summary(user: UserOut = Depends(get_current_user)) -> DashboardSummaryOut:
    return DashboardSummaryOut(**analytics_service.get_summary(user.id))
