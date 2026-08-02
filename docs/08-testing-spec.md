# 08 — Testing Spec

Automated **backend** tests are required. Use `pytest` + FastAPI `TestClient` (or `httpx.AsyncClient`).
Use a separate test DB (e.g. a temp SQLite file or in-memory) via a fixture so tests are isolated and repeatable.
Gemini is **always mocked** — tests must consume zero real credits.

## Required test cases (map 1:1 to the brief)
1. **Retrieve an existing profile** → 200, correct body.
2. **Valid profile update** → 200, fields changed, `updated_at` advanced.
3. **Reject invalid profile info** → 422 (empty required field / bio over limit).
4. **Validate a mocked Gemini response** → mock returns valid JSON → 200, matches `InsightResult`.
5. **Gemini timeout** → mock raises timeout → 504 (and malformed → 502, service error → 502).
6. **Accept or decline a valid pending invitation** → 200, status updated.
7. **Ended pending invitation auto-Expired** → seed a pending invite with past deadline → reads as `expired`;
   attempting to respond returns 409.
8. **Prevent acceptance of an expired invitation** → 409.
9. **Ended accepted invitation leaves Upcoming** → not in `GET /invitations` upcoming list; appears as
   attendance-pending/history as appropriate.
10. **Prevent feedback from Not Attended / Declined / Expired** → 403/409.
11. **Allow feedback from an Attended user** → 201.

## Mocking Gemini
- Put the network call behind `services/gemini.py:generate_insight(profile)`.
- In tests, patch that function (or the underlying client/HTTP call) with `unittest.mock.patch` /
  `monkeypatch` (or `respx` if using httpx) to return canned JSON or raise the failure you're testing.
- Provide a helper that yields a valid `{summary, communication_style, suggested_focus}` payload for the
  happy path, and variants for malformed (missing field / non-JSON) and errors (timeout, 429, 5xx).

## Freezing time
Because expiry and attendance depend on the clock, route all time through `now_utc()` and either:
- seed events with explicit past/future datetimes, or
- monkeypatch `now_utc()` in tests to control "now".
This makes the auto-expiry and "event ended" tests deterministic.

## Nice-to-have (mention if added)
- A couple of mobile component tests (e.g. the profile form validation) count positively.
- Run instructions go in the README: `cd backend && pytest` (with any env noted).
