# AI Usage Disclosure

## Tools used
- Claude Code — full-stack scaffolding, implementation, and automated testing for both the backend and
  mobile app, from an empty repo.

## What I used it for
- Generated the entire FastAPI backend from the provided spec kit (`docs/00`–`docs/09`): config, database
  layer, SQLAlchemy models, Pydantic schemas, all three routers (profiles, insight, invitations), the
  Gemini service wrapper, the invitation state-machine logic, the seed script, structured exception
  handling, and the Dockerfile.
- Generated the full pytest suite (40 tests across `test_profiles.py`, `test_insight.py`,
  `test_invitations.py`) covering every required case from `docs/08`, with Gemini fully mocked.
- Generated the Expo Router mobile app: the API client, TanStack Query hooks, the Profile/Edit + Gemini
  Insight screen, and the Invitations/History/Feedback screen with all state-machine-aware UI branches.
- Wrote this README from the implementation, including the architecture, database, Gemini integration,
  invitation state-machine, and security write-ups.

## Important AI suggestions reviewed or changed during the build
- The initial SQLAlchemy models used `DateTime(timezone=True)` directly; this silently returns
  timezone-*naive* datetimes on read under SQLite, which crashed comparisons against the timezone-aware
  `now_utc()`. Caught this by running the test suite (10 failures), then added a custom `UTCDateTime`
  SQLAlchemy type that normalizes to naive-UTC on write and re-attaches UTC tzinfo on read.
- Replaced the deprecated FastAPI `@app.on_event("startup")` hook with a `lifespan` context manager after
  noticing the deprecation warning in the test output.
- Verified rather than assumed: ran the full pytest suite (40/40 passing), booted the real `uvicorn` server,
  confirmed `/health`, Swagger `/docs`, the seed data, and — specifically — patched the profile, killed and
  restarted the backend process, and re-fetched to confirm the change survived (the persistence
  requirement), before considering the backend done. Also ran `tsc --noEmit` and a full `expo export --platform
  web` bundle to catch mobile-side type/bundling errors before calling the mobile app done.

## Ownership statement
**⚠️ To be completed by you before submission.** This disclosure describes what Claude Code generated. Per
the assessment's AI-tool policy, you (the candidate) need to personally review and test the submitted code,
then adjust the statement below to reflect that honestly — don't submit it unedited:

> I understand, reviewed, and tested all submitted code. AI coding assistants were **not** used during the
> Sunday live coding portion. (Gemini API calls from the running app during the demo are part of the
> implemented feature, not a coding assistant.)
