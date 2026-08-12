# COSMOS Backend API

FastAPI backend for COSMOS. The **Next.js frontend never talks to Supabase
directly** — it sends JSON to this API, which validates input with Pydantic and
is the only thing that holds the Supabase service-role key.

## Architecture

```
Next.js (.ts client) --fetch + HttpOnly cookie--> FastAPI --> Supabase (Auth + Postgres)
                        + provider HTTP (AI/STT/TTS) when configured
```

- Frontend origin: `http://localhost:3000`
- Backend origin: `http://localhost:8000` (docs at `/docs`)
- Supabase: managed project (Auth for passwords/sessions + Postgres tables)

## Endpoints

| Method | Path                                | Purpose                              |
|--------|-------------------------------------|--------------------------------------|
| POST   | `/api/auth/signup`                  | Create account + issue session       |
| POST   | `/api/auth/login`                   | Verify credentials + issue session   |
| GET    | `/api/auth/me`                      | Restore session from cookie          |
| POST   | `/api/auth/logout`                  | Clear session cookie                 |
| GET    | `/api/onboarding/status`            | Onboarding progress                  |
| POST   | `/api/onboarding/step`              | Save an onboarding step              |
| POST   | `/api/onboarding/complete`          | Finish onboarding                    |
| POST   | `/api/communication/chat`           | Companion reply (moderation + AI)    |
| GET    | `/api/communication/history`        | Chat history                         |
| DELETE | `/api/communication/history`        | Clear chat history                   |
| POST   | `/api/communication/transcribe`     | Speech-to-text (audio upload)        |
| POST   | `/api/communication/speak`          | Text-to-speech (returns WAV)         |
| GET    | `/api/notes`                        | List notes                           |
| POST   | `/api/notes`                        | Create note                          |
| PATCH  | `/api/notes/{id}`                   | Update note                          |
| DELETE | `/api/notes/{id}`                   | Delete note                          |
| POST   | `/api/study_room/session/start`     | Begin study session                  |
| POST   | `/api/study_room/session/pause`     | Pause session                        |
| POST   | `/api/study_room/session/resume`    | Resume session                       |
| POST   | `/api/study_room/session/complete`  | Complete session                     |
| POST   | `/api/study_room/event`             | Log a session event                  |
| GET    | `/api/study_room/session/current`   | Current active session               |
| GET    | `/api/dashboard/summary`            | User analytics summary               |
| GET    | `/api/profile`                      | User profile / preferences           |
| PATCH  | `/api/profile`                      | Update profile / preferences         |
| GET    | `/api/health`                       | Health check                         |

All responses use a structured JSON envelope:
`{"error":{"code","message"}}` on failure, domain payloads on success.

Sessions are delivered as **HttpOnly cookies** (`cosmos_session`,
`cosmos_refresh`) — the browser never sees raw tokens in the response body.

## Mock-first (default)

`MOCK_MODE=true` (default in `.env.example`) makes the whole API demoable with
**no third-party keys**:

- companion chat returns deterministic canned replies + emotion
- STT returns a canned transcript
- TTS returns a tiny silent WAV so playback works end-to-end
- dashboard/onboarding profile work against your Supabase tables when present

Set `MOCK_MODE=false` and add keys to activate live providers automatically:
- `GROQ_API_KEY` → companion replies via Groq (`llama-3.3-70b-versatile`)
- `SARVAM_API_KEY` → companion chat (`sarvam-105b`) **and** STT + TTS
  (auto-picks groq > sarvam; whichever is configured)

## Setup & Run

```powershell
# 1. Copy backend\.env.example to backend\.env and fill in REAL Supabase values
#    SUPABASE_URL=https://<project>.supabase.co
#    SUPABASE_SERVICE_ROLE_KEY=<service_role key>   (NEVER expose to the frontend)

# 2. Apply the schema in the Supabase SQL editor:  backend\sql\schema.sql

# 3. Run (either):
cd backend
.\run.bat          # creates venv, installs deps, starts uvicorn on :8000

# or from the repo root, launch both:
.\start-all.bat    # backend (:8000) + frontend (:3000)
```

Interactive docs while running: http://localhost:8000/docs

## Project layout

```
backend/
├── app/
│   ├── main.py                 # FastAPI app, CORS, error handlers, router wiring
│   ├── config.py/              # (core/config.py) env-driven settings
│   ├── dependencies.py         # get_current_user cookie dependency
│   ├── api/routes/             # thin route handlers
│   │   ├── auth.py, onboarding.py, communication.py, notes.py,
│   │   ├── study_room.py, dashboard.py, profile.py
│   ├── schemas/                # Pydantic request/response models + validation
│   ├── services/               # business logic (Supabase + providers)
│   │   ├── auth_service.py, ai_service.py, speech_to_text.py,
│   │   ├── text_to_speech.py, moderation.py, study_service.py,
│   │   ├── analytics_service.py, onboarding_service.py,
│   │   ├── communication_service.py, notes_service.py
│   ├── models/                 # lightweight domain models / enums
│   ├── utils/                  # logger, security, mock_data
│   ├── core/                   # config.py, ratelimit.py
│   └── db/supabase.py          # isolated Supabase access layer
├── sql/schema.sql              # Postgres schema + RLS (run in Supabase)
├── requirements.txt
├── .env.example
└── run.bat
```

## Security notes

- `SUPABASE_SERVICE_ROLE_KEY` is read only from `backend/.env` (gitignored). It is
  never served to the browser and only used server-side.
- Passwords are handled entirely by Supabase Auth (hashed). No plaintext storage.
- Pydantic validates every input; unknown/extra fields are rejected.
- Auth routes are rate-limited (10 req/min/IP default).
- CORS allows only configured frontend origins.
- All routes require the HttpOnly session cookie via `get_current_user`.
- Errors return generic, structured messages — no internals, secrets, or logs of
  passwords/tokens/keys.
- Row-level security in `sql/schema.sql` scopes every table to `auth.uid()`.
