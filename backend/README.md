# COMUSE Backend API

FastAPI backend for COMUSE authentication. The **Next.js frontend never talks to
Supabase directly** — it sends JSON to this API, which validates input with Pydantic
and is the only thing that holds the Supabase service-role key.

## Architecture

```
Next.js (browser)  --fetch + HttpOnly cookie-->  FastAPI (this repo)  -->  Supabase (Auth + Postgres)
```

- Frontend origin: `http://localhost:3000`
- Backend origin: `http://localhost:8000`
- Supabase: managed by the Supabase project (Auth for passwords/sessions, optional `profiles` table)

## Endpoints

| Method | Path                | Purpose                              |
|--------|---------------------|--------------------------------------|
| POST   | `/api/auth/signup`  | Create account + issue session       |
| POST   | `/api/auth/login`   | Verify credentials + issue session   |
| GET    | `/api/auth/me`      | Restore session from cookie          |
| POST   | `/api/auth/logout`  | Clear session cookie                 |
| GET    | `/api/health`       | Health check                         |

All responses use a structured JSON envelope:
`{"error":{"code","message"}}` on failure, `{"message","user"}` on success.

Sessions are delivered as **HttpOnly cookies** (`comuse_session`, `comuse_refresh`) —
the browser never sees raw tokens in the response body.

## Setup & Run

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt

# 1. Copy .env.example to .env and paste your REAL Supabase values:
#    SUPABASE_URL=https://<project>.supabase.co
#    SUPABASE_SERVICE_ROLE_KEY=<service_role key>   (NEVER expose to the frontend)

py -m uvicorn app.main:app --reload --port 8000
```

Interactive docs while running: http://localhost:8000/docs

### Frontend

```powershell
# from the repo root
npm run dev   # serves http://localhost:3000
```

The frontend reads `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).

## Security notes

- `SUPABASE_SERVICE_ROLE_KEY` is read only from `backend/.env` (gitignored). It is
  never served to the browser and is only used server-side.
- Passwords are handled entirely by Supabase Auth (hashed). No plaintext storage,
  no custom user table.
- Pydantic validates: email format, required fields, password length (≥8),
  password confirmation match.
- Auth routes are rate-limited (10 req/min/IP by default, in-memory fixed window).
- CORS allows only the configured frontend origins.
- Errors return generic, structured messages — no internals, no secrets, no logs of
  passwords/tokens/keys.
- (Optional) enable profile storage: run `sql/profiles.sql` in the Supabase SQL editor.

## Project layout

```
app/
├── main.py               # FastAPI app, CORS, error handlers
├── core/
│   ├── config.py         # env-driven settings
│   └── ratelimit.py      # basic per-IP rate limiting
├── api/routes/auth.py    # route handlers (thin)
├── schemas/auth.py       # Pydantic request/response models + validation
├── services/auth_service.py  # business logic (Supabase calls)
└── db/supabase.py        # isolated Supabase access layer
```