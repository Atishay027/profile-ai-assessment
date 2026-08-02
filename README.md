# Profile, AI Insight & Event Invitation App

A React Native (Expo) app for a demo user (`user-001`) to manage their profile, generate an AI-powered
profile insight via Gemini, and RSVP to event invitations through a strict backend-enforced state machine —
all backed by a single FastAPI service.

## Prerequisites
- Node.js 20+, npm, Expo CLI (via `npx`)
- Python 3.12+ (3.11 also works), pip
- (Optional) Docker, for running the backend in a container
- A Google Gemini API key you're authorised to use (free-tier key is enough; tests never call the real API)

## Setup

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then fill in GEMINI_API_KEY
uvicorn app.main:app --reload   # http://localhost:8000  (Swagger at /docs)
```
The backend auto-creates tables and seeds demo data for `user-001` on first startup (`APP_ENV=development`
and no existing profile). To reseed by hand instead: `python -m app.seed`.

### Mobile
```bash
cd mobile
npm install
cp .env.example .env            # set EXPO_PUBLIC_API_URL — see notes below
npx expo start
```
Then scan the QR code with Expo Go (physical device) or press `i` / `a` / `w` for simulator/emulator/web.

**`EXPO_PUBLIC_API_URL` by test target:**
| Target | Value |
|---|---|
| Physical phone via Expo Go | `http://<your-computer's-LAN-IP>:8000` (e.g. `http://192.168.1.9:8000`) |
| iOS Simulator | `http://localhost:8000` |
| Android Emulator | `http://10.0.2.2:8000` |

Find your LAN IP with `ipconfig getifaddr en0` (macOS Wi-Fi). Phone and computer must be on the same network.

### Docker (backend)
```bash
docker build -t assessment-backend ./backend
docker run --env-file backend/.env -p 8000:8000 assessment-backend
```
The container writes `app.db` inside the container filesystem by default, so data does **not** persist across
`docker run` invocations unless you mount a volume, e.g. add `-v $(pwd)/backend/data:/app/data` and set
`DATABASE_URL=sqlite:////app/data/app.db`. For local development (not Docker), the SQLite file next to
`app/` persists fine across plain backend restarts, which is what the persistence requirement targets.

## Running the tests
```bash
cd backend
source .venv/bin/activate
pytest -q
```
40 tests, all passing. Gemini is always mocked (`monkeypatch` on `generate_insight` and unit tests on the
JSON-parsing helpers) — the suite consumes zero real API credits and needs no `GEMINI_API_KEY` to run.

## Architecture & key technical decisions

```
[Expo app]  --HTTP-->  [FastAPI]  --SQLAlchemy-->  [SQLite file (persists)]
                           |
                           +--HTTPS-->  [Google Gemini API]  (key stays server-side only)
```

- **SQLite + SQLAlchemy**: zero external setup, the `.db` file survives backend restarts, trivial to seed
  and to swap out in tests (a temp file per test session, tables dropped/recreated per test for isolation).
- **Single clock source** — `app/utils/time.py:now_utc()` — used everywhere timestamps or "now" comparisons
  happen, so business logic never calls `datetime.now()` directly and tests can reason about explicit
  past/future timestamps instead of needing to freeze the clock.
- **A custom `UTCDateTime` SQLAlchemy type** (`app/database.py`) wraps every timestamp column. SQLite has no
  native timezone-aware datetime type, so a bare `DateTime(timezone=True)` column silently returns
  timezone-*naive* Python datetimes on read, which then blow up (`TypeError`) when compared against the
  timezone-aware value from `now_utc()`. The wrapper normalizes to naive-UTC on write and re-attaches UTC
  tzinfo on read, so every datetime the app touches is reliably timezone-aware.
- **Two-field invitation model** (`response_status` / `attendance_status`) cleanly separates "did they RSVP"
  from "did they show up" — see the dedicated section below.
- **Lazy, computed-on-read expiry**, persisted on transition — see below.
- **Server-authored timestamps**: `created_at`, `updated_at`, `responded_at`, `attendance_recorded_at` are
  always set by the backend via `now_utc()`; the client can never supply or override them.
- **TanStack Query** on mobile for all server state: loading/error/success are first-class query states,
  mutations use `onSuccess: () => queryClient.invalidateQueries(...)` to refetch affected data, and
  `mutation.isPending` doubles as the duplicate-submit guard for every button that triggers a network call.
- **Structured exception handling**: domain errors (`app/errors.py`) all inherit `DomainError` and carry
  their own HTTP status + machine-readable `code`; a single FastAPI exception handler converts any of them
  into `{"detail": "...", "code": "..."}`. A catch-all handler maps any truly unexpected exception to a
  generic 500 without leaking a traceback. Pydantic's own 422 handling is left as FastAPI's default.

## Database design

Three tables (`app/models.py`), created on startup via `Base.metadata.create_all`:

- **profiles** — `user_id` (PK), `full_name`, `city`, `occupation?`, `bio?` (max 500 chars), `created_at`,
  `updated_at`.
- **invitations** — `id` (PK, uuid), `user_id`, `title`, `description?`, `location?`, `event_start`,
  `event_end`, `rsvp_deadline?`, `response_status`, `attendance_status`, `responded_at?`,
  `attendance_recorded_at?`, `created_at`, `updated_at`.
- **feedback** — `id` (PK, uuid), `invitation_id` (FK), `user_id`, `rating? (1–5)`, `comment`, `created_at`.

**Persistence**: SQLite file at `DATABASE_URL` (default `sqlite:///./app.db`), gitignored. Verified manually:
patch the profile, kill and restart `uvicorn`, `GET` again — the change is still there (no reseed happens
once a profile for `DEMO_USER_ID` already exists).

**Seed data** (`app/seed.py`, run automatically in dev, or manually via `python -m app.seed`) covers every
scenario the brief lists, with all times computed relative to `now_utc()` so the scenarios stay valid
whenever the seed runs:
1. Future / actionable pending (Rooftop Networking Mixer)
2. Accepted, upcoming (Board Game Night)
3. Declined (Early Morning Run Club)
4. Expired — deadline already passed while still pending (Weekend Hiking Trip)
5. Accepted, event ended, attendance not yet recorded — "attendance pending" limbo (Cooking Class)
6. Attended, with one seeded feedback entry (Book Club)
7. Not attended (Volunteer Park Cleanup)

## Gemini integration & structured-response design

`POST /profiles/{user_id}/insight`:
1. Load the saved profile (404 if missing).
2. Build a prompt from `full_name`, `city`, `occupation`, `bio`, explicitly instructing the model to reply
   with **only** a JSON object and no markdown.
3. Call Gemini via `services/gemini.py:generate_insight(profile)` (model + key + timeout from env,
   `google-generativeai` SDK), with `GEMINI_TIMEOUT_SECONDS` enforced on the request.
4. Defensively strip any ```` ```json ```` code fences from the response text before parsing.
5. `json.loads` the result, then validate it against the Pydantic `InsightResult` model
   (`summary`, `communication_style`, `suggested_focus` — all required strings). Anything that fails to
   parse or fails validation is treated as malformed.
6. Return 200 with the validated insight. **The insight is never written back onto the stored profile** —
   it's a pure, display-only read.

**Key protection**: `GEMINI_API_KEY` is read from the backend environment only (`config.py`, via
`pydantic-settings`), never logged, never returned in any response, and the mobile app has no path to it —
the phone only ever talks to FastAPI.

**Failure-handling matrix** (`app/errors.py` + `services/gemini.py`):
| Failure | HTTP | Client message |
|---|---|---|
| Missing/empty API key | 503 | "AI service is not configured." |
| Timeout | 504 | "AI insight timed out, please try again." |
| Rate limit (429 from Gemini) | 429 | "AI service is busy, please retry shortly." |
| Malformed / unparseable / fails Pydantic | 502 | "AI returned an unexpected response." |
| Other Gemini/service error | 502 | "AI service error, please try again." |

No stack traces, raw provider errors, or the key ever appear in a response or a log line.

## Invitation & attendance status design

Two independent fields per invitation:
- `response_status`: `pending | accepted | declined | expired`
- `attendance_status`: `attendance_pending | attended | not_attended` (only meaningful once accepted)

**Effective deadline**: `min(rsvp_deadline, event_start)` if `rsvp_deadline` is set, else `event_start` —
accept/decline is only allowed before whichever comes first.

**Expiry — chosen approach: lazy, computed on read, persisted on transition.** Every read of an invitation
(list, history, respond, attendance, feedback) first calls `apply_lazy_expiry`, which checks
`now_utc()` against the effective deadline and, if a still-`pending` invitation's window has closed,
flips it to `expired` and commits that transition immediately. This keeps the logic deterministic and easy
to test (seed a past deadline, read it back, it's `expired`) without needing a background scheduler. A
background job/cron would be the alternative if this needed to scale to notifying users the instant an
invitation expires — deliberately out of scope for a 2-day build with no push-notification requirement.

**Derived bucket** (single source of truth computed by `services/invitation_logic.py:compute_bucket`, never
stored beyond the `response_status`/`attendance_status` fields it's derived from):

| Condition | Bucket | Surfaces in |
|---|---|---|
| pending, before effective deadline | `ACTIONABLE` | Upcoming (Accept/Decline) |
| pending, deadline passed | `EXPIRED` (persisted) | History |
| accepted, before event end | `ACCEPTED_UPCOMING` | Upcoming (read-only) |
| accepted, event ended, attendance still pending | `ATTENDANCE_PENDING` | Upcoming (limbo — no RSVP buttons) |
| accepted, attendance = attended | `ATTENDED` | History (feedback allowed) |
| accepted, attendance = not_attended | `NOT_ATTENDED` | History (no feedback) |
| declined | `DECLINED` | History |
| expired | `EXPIRED` | History |

`GET /users/{id}/invitations` returns `ACTIONABLE + ACCEPTED_UPCOMING + ATTENDANCE_PENDING` (i.e. the
"upcoming/current" view). `GET /users/{id}/gathering-history` returns exactly the four categories the brief
names: `ATTENDED + NOT_ATTENDED + DECLINED + EXPIRED`. Attendance-pending items are intentionally **not** a
history category — they stay visible in the upcoming endpoint as a distinct limbo state until an admin
records attendance, which then moves them into history.

**Transition guards**, all enforced server-side (never just hidden in the UI):
- `respond`: 409 if not `pending` (covers already-accepted/declined/expired); if the deadline has just passed,
  it's expired-then-rejected in the same request rather than silently accepted.
- `attendance` (admin/test-only endpoint, no mobile UI): 409 unless `response_status == accepted`; 409 unless
  `now >= event_end` (can't record attendance for an event that hasn't happened yet).
- `feedback`: 409 unless `attendance_status == attended` — explicitly rejects declined, expired, and
  accepted-but-not-yet-attended (including attendance-pending limbo).

## Authentication & security approach

**Not implemented** for this assessment by design (see "Current demo posture" below), but here is how I'd
add it:

- Issue a token on login (JWT, or a session token from an identity provider / Firebase Auth). The mobile app
  stores it in `expo-secure-store` and sends `Authorization: Bearer <token>` on every request.
- A FastAPI dependency validates the token on every protected route and resolves the **authenticated user's
  id from the token** — never from the URL or request body.
- **Preventing cross-user access**: never trust `{user_id}` in the path as proof of identity. After
  validating the token, compare the authenticated user's id against the resource owner and reject mismatches
  with 403. Scope every query by the authenticated user (`WHERE user_id = current_user`) so a user can only
  ever read/modify their own profile, invitations, and feedback.
- The admin/attendance endpoint would sit behind a separate admin role/scope in a real system, not just be
  reachable by anyone who knows an invitation id.

**Current demo posture (implemented)**:
- A fixed demo user `user-001` is used throughout; endpoints are unauthenticated by design for this scope.
- CORS is permissive (`CORS_ORIGINS=*`) for local development; it would be restricted to known origins in
  production.
- Secrets (`GEMINI_API_KEY`) live only in the backend environment, are never logged, never returned in a
  response, and `.env`/`*.db` are gitignored. `.env.example` files contain placeholders only.

## Assumptions
- Single demo user (`user-001`); no multi-user/list-of-users concept exists anywhere.
- Bio limit set at 500 characters (both Pydantic `max_length` and the mobile character counter).
- The attendance endpoint (`PATCH /invitations/{id}/attendance`) is intentionally admin/test-only — it exists
  to drive the demo and the automated tests, with no corresponding mobile UI, per the brief.
- A user can submit feedback for the same attended invitation more than once at the API level (no uniqueness
  constraint on `feedback.invitation_id`); the mobile UI works around this locally by hiding the form and
  showing a "thanks" state once a submission for that item succeeds in the current app session, but this is
  a client-side nicety, not a backend guarantee.
- Attendance-pending invitations remain visible in the "Upcoming" endpoint/section as an explicit limbo
  state (see the invitation design section above) rather than disappearing entirely once the event ends.

## Known limitations / unfinished work
- No real authentication/authorization (documented above as a conscious scoping decision).
- No push notifications or background job for expiry — expiry is computed lazily on read, which is
  sufficient for this scope but wouldn't proactively notify a user the instant an invitation expires.
- No pagination on the invitations/history list endpoints — fine at demo data volumes, would need it at
  scale.
- No mobile component/unit tests were added (only backend `pytest`); manual verification was done in Expo
  Go / web export instead.
- Docker persistence requires an explicit volume mount (documented above) — not wired up by default since
  local (non-Docker) development already satisfies the "survives backend restart" requirement.

## Final status summary
- **Completed**: All three modules end-to-end (Profile view/edit, Gemini insight, Invitations/History/
  Feedback), full backend test suite (40 tests, all passing, Gemini fully mocked), seed data covering every
  required scenario, Dockerfile, `/health`, Swagger docs, structured error handling, CORS, all timestamps
  server-authored, persistence verified across a real backend restart.
- **Incomplete**: Real authentication (write-up only, as required), mobile automated tests, Firestore
  alternative (SQLite was chosen and never switched, per the recommended timeline).
- **Known issues**: None outstanding in the implemented scope; see "Known limitations" above for things
  deliberately left out of scope.

## AI usage
See `AI_USAGE.md`.
