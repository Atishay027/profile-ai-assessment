# 10 — Final Deliverables Checklist

Walk this before submitting (Mon 10:00 AM).

## Repo & code
- [ ] GitHub repo link ready; access granted if private.
- [ ] Complete mobile + backend source committed.
- [ ] Commit history shows regular, meaningful commits (not one giant final commit).
- [ ] No secrets committed (search history for keys). `.env` and `*.db` are gitignored.

## Docs
- [ ] `README.md` filled from `README.template.md`, all sections complete:
      prerequisites, install/setup, exact run commands (mobile + backend), architecture & decisions,
      database design, Gemini integration + structured-response design, invitation/attendance design,
      auth & security approach, assumptions, known limitations/unfinished work.
- [ ] `.env.example` (backend + mobile) with no real credentials.
- [ ] `AI_USAGE.md` complete: tools, what for, suggestions reviewed/changed.
- [ ] Expiry handling documented (on-read vs background).
- [ ] Final summary of completed / incomplete / known issues.

## Runnable
- [ ] `/health` returns 200. Swagger at `/docs` usable.
- [ ] Exact backend run commands verified from a clean checkout.
- [ ] Backend Dockerfile builds and runs; commands in README verified.
- [ ] Expo app runs on at least one platform; API base URL documented (LAN IP note for physical device).
- [ ] Seed script produces all invitation scenarios.

## Tests
- [ ] `pytest` passes; all required cases present (`docs/08`). Run instructions in README.
- [ ] Gemini mocked — no real credits used by the suite.

## Demo
- [ ] Short screen recording: profile edit + persistence, generate insight, RSVP flow, attendance → history,
      feedback gated on Attended, and an error state or two.

## Live checkpoint readiness (Sunday)
- [ ] Can explain FE/BE/DB structure and data flow app↔FastAPI↔Gemini↔DB.
- [ ] Can explain key protection and failure handling.
- [ ] Can explain the invitation/attendance state machine.
- [ ] Comfortable making a small change/fix **without** an AI coding assistant and testing it live.
