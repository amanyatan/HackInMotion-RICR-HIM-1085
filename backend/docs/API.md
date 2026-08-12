# COSMOS Backend API Reference

Base URL: `http://localhost:8000`. Docs: `/docs` (Swagger), `/redoc`.

## Auth flow

All authenticated endpoints require the HttpOnly session cookie
(`cosmos_session`) set by `/api/auth/login` or `/api/auth/signup`. Clients must
send `credentials: "include"` with every request.

Cookie lifetime: access token (~1h) and refresh token (30d). On expiry the
server returns `SESSION_EXPIRED` — sign in again.

## Envelope

Success: domain payload (see per-endpoint).
Failure:

```json
{ "error": { "code": "CODE", "message": "Human message" } }
```

Common codes: `VALIDATION_ERROR`, `UNAUTHENTICATED`, `SESSION_EXPIRED`,
`RATE_LIMITED`, `NOT_FOUND`, `INTERNAL_ERROR`, `EMAIL_ALREADY_EXISTS`,
`INVALID_CREDENTIALS`, `EMAIL_NOT_CONFIRMED`.

---

## Auth

### `POST /api/auth/signup` → 201
Body: `{ "name", "email", "password", "confirmPassword" }`
Response: `{ "message", "user": { "id", "email", "name" } }` + sets cookies.

### `POST /api/auth/login`
Body: `{ "email", "password" }`
Response: `{ "message", "user": { "id", "email", "name" } }` + sets cookies.

### `GET /api/auth/me`
Response: `{ "message", "user" }`

### `POST /api/auth/logout` → 204

---

## Onboarding

### `GET /api/onboarding/status`
Response: `{ "current_step": int, "done": bool, "data": {...}|null }`

### `POST /api/onboarding/step`
Body (any of): `{ "step": int, "name"?, "reason"?, "subjects"?[], "language"?,
"character"?, "character_voice"? }`

### `POST /api/onboarding/complete`
Body: `{ "language": "en", "character": "kei", "name"?, "reason"?, "subjects"?,
"character_voice"? }`

---

## Communication

### `POST /api/communication/chat`
Body: `{ "message", "character"?, "language"? }`
Response: `{ "message_id", "role", "content", "emotion", "character",
"language" }`

The pipeline runs moderation first; flagged input returns a caring fallback and
is recorded to `abuse_events`.

### `GET /api/communication/history` → `{ "messages": [...] }`
### `DELETE /api/communication/history` → 204

### `POST /api/communication/transcribe`
Multipart form: `audio` (file) + `language`.
Response: `{ "text", "language", "is_mock" }`

### `POST /api/communication/speak`
Form fields: `text`, `voice` ("kei"|"mark"), `language`.
Response: `audio/wav` body (mock returns a silent placeholder WAV).

---

## Notes

### `GET /api/notes?subject=&limit=` → `{ "notes": [...] }`
### `POST /api/notes` → 201  Body: `{ "subject", "title", "content" }`
### `PATCH /api/notes/{id}` Body: partial `{ "subject"?, "title"?, "content"? }`
### `DELETE /api/notes/{id}` → 204

---

## Study room

### `POST /api/study_room/session/start`
Body: `{ "character"?, "language"? }` → `{ "session_id", "status" }`
### `POST /api/study_room/session/pause` Body: `{ "session_id" }`
### `POST /api/study_room/session/resume` Body: `{ "session_id" }`
### `POST /api/study_room/session/complete` Body: `{ "session_id" }`
### `POST /api/study_room/event`
Body: `{ "session_id", "type", "payload" }` → `{ "event_id", "recorded" }`
### `GET /api/study_room/session/current?session_id=` → session or 404

---

## Dashboard

### `GET /api/dashboard/summary`
Response: `{ "words_today", "minutes_today", "total_words", "total_minutes",
"streak_days", "subject_breakdown": [{ "subject", "sessions" }] }`

---

## Profile

### `GET /api/profile`
Response: `{ "id", "email", "name", "character", "language" }`
### `PATCH /api/profile`
Body: partial `{ "name"?, "character"?, "language"? }`
Response: updated profile.

---

## Health

### `GET /api/health` → `{ "status": "ok" }`
