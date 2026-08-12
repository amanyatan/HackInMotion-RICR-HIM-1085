"""COSMOS Auth API — FastAPI application entrypoint."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    auth,
    communication,
    dashboard,
    notes,
    onboarding,
    profile,
    study_plan,
    study_room,
)
from app.core.config import settings

app = FastAPI(
    title="COSMOS API",
    description="Backend API for COSMOS — authentication, companion chat, onboarding, study sessions, notes and analytics. Talks to Supabase only.",
    version="1.1.0",
)

# CORS: only the frontend origin may call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(onboarding.router)
app.include_router(communication.router)
app.include_router(notes.router)
app.include_router(study_room.router)
app.include_router(study_plan.router)
app.include_router(dashboard.router)
app.include_router(profile.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Please check your details and try again.",
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, dict) else {"code": "HTTP_ERROR", "message": str(exc.detail)}
    if "error" not in detail:
        detail = {"error": detail}
    return JSONResponse(status_code=exc.status_code, content=detail)


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # Never return internals or stack traces to clients.
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Something went wrong. Please try again later."}},
    )