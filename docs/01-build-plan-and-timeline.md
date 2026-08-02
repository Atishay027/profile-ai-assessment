# 01 — Build Plan & Timeline

Your schedule (IST):
- **Start:** Sat 1 Aug, 6:00 PM
- **Live checkpoint:** Sun 2 Aug, 2:00–2:30 PM (project must be running; a small change/fix given live; no AI assistants for that change)
- **Final submission:** Mon 3 Aug, 10:00 AM
- **Status update:** send one at the end of Saturday's work.

Build in this order. Each phase ends with a commit. Front-load the backend so the live checkpoint has a
running, explainable system.

## Phase 0 — Repo & scaffolding (Sat 6:00–6:45 PM)
- [ ] `git init`, first commit with README skeleton, `.gitignore`, this `docs/` folder, `CLAUDE.md`.
- [ ] Backend: `backend/` with FastAPI app, `config.py` (pydantic-settings), `/health`, CORS, `main.py`.
- [ ] `.env.example` (backend) + `mobile/.env.example`. Confirm `.env`, `*.db`, `node_modules` are gitignored.
- [ ] Mobile: `npx create-expo-app` with TypeScript + Expo Router. App boots in Expo.
- [ ] Verify `/health` returns 200 and the Expo app launches. **Commit.**

## Phase 1 — Profile module end to end (Sat 6:45–8:30 PM)
- [ ] DB engine/session, `Profile` model, create tables on startup.
- [ ] Seed the demo profile (`user-001`).
- [ ] `GET /profiles/{id}` and `PATCH /profiles/{id}` with Pydantic validation (required name+city, bio limit, partial update).
- [ ] Mobile Profile screen: view + edit form, loading/empty/success/error, duplicate-submit guard, refetch after save.
- [ ] Backend tests: get existing, valid update, reject invalid. **Commit.**

## Phase 2 — Gemini insight (Sat 8:30–10:00 PM)
- [ ] `services/gemini.py`: `generate_insight(profile) -> InsightResult`, model+key from env, timeout, error mapping.
- [ ] `POST /profiles/{id}/insight`: load profile → call Gemini → validate JSON with Pydantic → return.
- [ ] Mobile: "Generate Profile Insight" button, loading state, result display, error message, in-flight guard; never overwrites profile.
- [ ] Tests with Gemini **mocked**: success, timeout, malformed, service error. **Commit.**

**End of Saturday: send the status update** (template below). Aim to have Modules 1 & 2 working.

## Phase 3 — Invitations core (Sun morning, before checkpoint)
- [ ] `Invitation` + `Feedback` models; seed all scenarios (`docs/07`).
- [ ] `invitation_logic.py`: effective status + bucket derivation + transition guards (`docs/05`).
- [ ] `GET /users/{id}/invitations` (current/upcoming), `POST /invitations/{id}/respond`.
- [ ] Mobile: invitations list, Accept/Decline with guards and states.
- [ ] **Ensure the whole app runs before 2:00 PM.** Rehearse explaining architecture and data flow.

## Live checkpoint (Sun 2:00–2:30 PM)
Have it running, screen ready to share. Be ready to explain FE/BE/DB structure, data flow across
app↔FastAPI↔Gemini↔DB, how the Gemini key is protected, and the invitation/attendance logic. You'll be
given a small change/fix — **do it without an AI coding assistant** and run/test it live. Gemini calls in the
running app are fine; AI *coding* assistants are not.

## Phase 4 — Invitations complete (Sun afternoon)
- [ ] Attendance endpoint (admin/test), gathering-history endpoint, feedback endpoint with attendance gate.
- [ ] Mobile: history categories, attendance-pending limbo, feedback only when Attended.
- [ ] All required invitation tests (`docs/08`). **Commit** frequently.

## Phase 5 — Hardening & docs (Sun evening → Mon morning)
- [ ] Fill `README.md` (all sections), `AI_USAGE.md`, `.env.example`, Dockerfile + run instructions.
- [ ] Walk `docs/02` and `docs/10`; close every gap.
- [ ] Full test run green. Record a short screen demo. Final commit + push. Confirm repo access if private.

## Saturday status-update template
```
Completed:
- <e.g. Backend scaffold, /health, CORS, config from env. Profile GET/PATCH with validation + tests.
  Mobile Profile screen wired with all states. Gemini insight endpoint + mobile button + mocked tests.>

Currently working on:
- <e.g. Invitation data model + seed data.>

Blockers:
- <none / describe. If blocked >30–45 min, raise it rather than stay stuck.>

Plan for Sunday:
- Finish invitations core before the 2:00 PM checkpoint, then attendance/history/feedback + tests,
  then README/Docker/recording before Monday 10:00 AM.
```
