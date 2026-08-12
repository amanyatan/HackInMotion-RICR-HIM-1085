"""Profile API routes (display metadata preferences)."""

from fastapi import APIRouter, Depends

from app.db.supabase import repo
from app.dependencies import get_current_user
from app.schemas.auth import UserOut
from app.schemas.main import ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("")
def get_profile(user: UserOut = Depends(get_current_user)) -> dict:
    prefs = {}
    try:
        rows = repo.table.select("user_preferences", columns="*", filters={"uid": user.id}, limit=1)
        if rows:
            prefs = rows[0]
    except Exception:
        pass
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "character": prefs.get("character") or "kei",
        "language": prefs.get("language") or "en",
    }


@router.patch("")
def update_profile(data: ProfileUpdate, user: UserOut = Depends(get_current_user)) -> dict:
    payload = {
        k: v for k, v in data.model_dump(exclude_none=True).items()
    }
    if payload:
        try:
            row = {"uid": user.id}
            row.update(payload)
            repo.table.upsert("user_preferences", row, on_conflict="uid")
        except Exception:
            pass
    return get_profile(user)
