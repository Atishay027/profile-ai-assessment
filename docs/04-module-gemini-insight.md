# 04 — Module 2: Gemini Profile Insight

## Goal
Generate a short, structured AI insight from the saved profile. The grade is on **secure integration,
structured output handling, validation, and failure handling** — not prompt cleverness.

## Structured output contract
Gemini must return JSON with exactly:
- `summary` (str)
- `communication_style` (str)
- `suggested_focus` (str)

Define a Pydantic model `InsightResult` with these three fields and **validate the model's output against it
before returning**. If the model returns anything that doesn't parse/validate → treat as a malformed response.

## Endpoint: POST /profiles/{user_id}/insight
Flow:
1. Load the saved profile (404 if missing).
2. Build a prompt from relevant profile fields (name, city, occupation, bio).
3. Call Gemini via `services/gemini.py:generate_insight(profile)`, requesting JSON.
4. Parse + validate with `InsightResult` (Pydantic).
5. Return 200 with the validated insight. **Do not** write it back onto the profile.

## Backend service (`services/gemini.py`)
- Read `GEMINI_API_KEY` and `GEMINI_MODEL` from env (via `config.py`). **Never** hardcode or log the key.
- Set a request **timeout**.
- Ask the model for JSON only (e.g. instruct "respond with only JSON, no markdown"), then strip any code fences
  defensively before parsing.
- Map failures to clean outcomes the router turns into HTTP errors:
  | Failure | HTTP | Client message (no internals) |
  |---------|------|-------------------------------|
  | Missing/empty API key | 500 or 503 | "AI service is not configured." |
  | Timeout | 504 | "AI insight timed out, please try again." |
  | Rate limit (429 from Gemini) | 429 | "AI service is busy, please retry shortly." |
  | Malformed / unparseable / fails Pydantic | 502 | "AI returned an unexpected response." |
  | Other Gemini/service error | 502 | "AI service error, please try again." |
- Never leak stack traces, raw provider errors, or the key in responses or logs.

## Mobile requirements
- A **"Generate Profile Insight"** button on (or near) the profile screen.
- **Loading** state while generating; **disable the button / block repeat requests** while in flight.
- Display `summary`, `communication_style`, `suggested_focus` clearly (e.g. three labelled sections/cards).
- On failure, show the **useful error message** returned by the backend.
- The insight is **display-only** — it never auto-updates the stored profile.

## Testing (mock Gemini — no real credits; details in docs/08)
- Success: patch `generate_insight` (or the underlying client) to return valid JSON → 200, body matches `InsightResult`.
- Timeout → 504. Malformed JSON → 502. Service error → 502. (Missing key can be a config test → configured error.)
