# CLAUDE.md — Project master instructions

You are helping build a **2-day take-home technical assessment**. Reliability and correct business rules
matter more than feature count. Ship working, well-tested core functionality and document anything unfinished
honestly.

## Project

A standalone mobile app with three connected modules, backed by one FastAPI service:

1. **Profile Management** — view/edit a demo user's profile, persisted via the backend.
2. **Gemini Profile Insight** — generate a structured AI insight from the saved profile.
3. **Event Invitations & History** — RSVP flow with a strict status/attendance state machine.

Demo user id: `user-001` (no auth required; see `docs/09-security-and-auth.md`).

## Tech stack (locked — do not substitute)

- **Mobile:** React Native + Expo + TypeScript (Expo Router). Server state via TanStack Query. NativeWind optional.
- **Backend:** Python + FastAPI + Pydantic v2 + pydantic-settings.
- **AI:** Google Gemini API (server-side only).
- **DB:** SQLite via SQLAlchemy (default). Firestore Emulator is an accepted alternative — see `docs/07`.
- **VCS:** Git, committed from the very first scaffold, frequent meaningful commits.

## Repo structure (target)

```
repo/
  CLAUDE.md
  README.md                # build from README.template.md
  AI_USAGE.md
  docs/                    # this spec kit
  backend/
    app/
      main.py              # app, CORS, exception handlers, routers, /health
      config.py            # pydantic-settings; all config from env
      database.py          # engine/session
      models.py            # ORM models
      schemas.py           # Pydantic request/response models
      seed.py              # seed script (all invitation scenarios)
      routers/{profiles,insight,invitations}.py
      services/{gemini,invitation_logic}.py
      utils/time.py        # now_utc() — single clock source for testability
    tests/{conftest,test_profiles,test_insight,test_invitations}.py
    Dockerfile
    requirements.txt
    .env.example
  mobile/
    app/                   # Expo Router screens
    src/{api,hooks,components,types}/
    app.json
    .env.example           # EXPO_PUBLIC_API_URL
```

## Non-negotiable rules

1. **Never commit secrets.** `GEMINI_API_KEY` lives only in the backend env. `.gitignore` must cover `.env`,
   `*.db`, `__pycache__`, `node_modules`, Expo build artifacts. Provide `.env.example` with no real values.
2. **Gemini key never reaches the mobile app.** The phone only talks to FastAPI; FastAPI talks to Gemini.
3. **All business rules and status transitions are enforced on the backend**, not just hidden in the UI.
   Invalid transitions return proper HTTP errors (see `docs/05`).
4. **Backend generates important timestamps** (created/updated/responded/attendance). Never trust the client
   for time.
5. **Backend persists across restarts.** Profile and invitation data survive a backend restart.
6. **Tests must not spend real API credits.** Gemini is always mocked in tests (`docs/08`).
7. **Commit regularly** with meaningful messages. No single giant final commit.
8. **Model name is configurable** via `GEMINI_MODEL` env var; key via `GEMINI_API_KEY`.

## Conventions

- TypeScript `strict: true`. No `any` unless justified with a comment.
- One API client module on mobile; base URL from `EXPO_PUBLIC_API_URL`. Every network call handles
  loading / empty / success / error states and blocks duplicate submits while in flight.
- Pydantic models for every request and response. Return correct HTTP status codes and meaningful,
  non-sensitive error messages.
- Store and compute all datetimes in **UTC**. Use `app/utils/time.py:now_utc()` everywhere so tests can freeze time.
- Prefer small, focused edits. Diagnose root causes rather than patching symptoms.

## How to work through this

1. Read `docs/01-build-plan-and-timeline.md` and follow the phases in order.
2. After each unit of work, tick the matching boxes in `docs/02-requirements-traceability.md`.
3. Module details live in `docs/03`, `04`, `05`. Backend/db/testing/security in `docs/06`–`09`.
4. Before submission, walk `docs/10-final-deliverables.md` end to end.

## Definition of done (per module)

- Endpoints implemented with Pydantic validation and correct status codes.
- Mobile screen wired with loading/empty/success/error + duplicate-submit guard.
- Backend tests for the required cases pass (`docs/08`).
- Traceability checkboxes ticked. Committed with a meaningful message.
