# 02 — Requirements Traceability (the anti-miss checklist)

Every requirement from the assessment email is a checkbox below. Tick as you complete. If something here is
unchecked at submission time, either finish it or document it as a known limitation in the README.

_Last audited against actual code/tests/manual verification on 2026-08-02 — see inline notes on anything left
unchecked deliberately._

## Module 1 — Profile Management
- [x] View profile
- [x] Edit full name, city, occupation, short bio
- [x] Save changes through the FastAPI backend
- [x] Full name required
- [x] City required
- [x] Bio has a reasonable character limit
- [x] Partial profile updates supported (PATCH semantics)
- [x] Loading state
- [x] Empty state
- [x] Success state
- [x] Error state
- [x] Frontend validation errors shown clearly
- [x] Backend validation errors shown clearly
- [x] Repeated submissions prevented while a request is processing
- [x] Profile refreshes after a successful update
- [x] Profile persists after restarting the backend
- [x] `GET /profiles/{user_id}` (or equivalent)
- [x] `PATCH /profiles/{user_id}` (or equivalent)

## Module 2 — Gemini Profile Insight
- [x] "Generate Profile Insight" button
- [x] Loading state while generating
- [x] Generated result displayed clearly
- [x] Useful error message on failure
- [x] Repeated requests prevented while generation in progress
- [x] AI result does NOT auto-overwrite profile info
- [x] `POST /profiles/{user_id}/insight` (or equivalent)
- [x] Backend retrieves saved profile
- [x] Sends relevant demo-profile info to Gemini
- [x] Requests structured JSON: `summary`, `communication_style`, `suggested_focus`
- [x] Validates Gemini response with Pydantic before returning
- [x] `GEMINI_API_KEY` in env var
- [x] `GEMINI_MODEL` configurable via env var
- [x] Gemini key never exposed to mobile
- [x] Handles missing key
- [x] Handles timeout
- [x] Handles rate limits
- [x] Handles malformed response
- [x] Handles Gemini service errors
- [x] Returns meaningful errors without leaking internal details
- [x] Uses a key you're authorised to use; no paid spend expected — live-tested 2026-08-02 against real
      Gemini API; `gemini-2.0-flash` returned a real 429 (zero free-tier quota on that model for this key),
      `gemini-flash-latest` works and is now the configured `GEMINI_MODEL`
- [x] Automated tests mock Gemini; consume no real credits

## Module 3 — Event Invitations & History
- [x] View upcoming invitations
- [x] Accept or decline a pending invitation
- [x] View gathering history
- [x] Correct status for past invitations
- [x] Submit feedback only when attendance confirmed (Attended)
- [x] Response states modelled: Pending, Accepted, Declined, Expired
- [x] Attendance states modelled: Attendance Pending, Attended, Not Attended
- [x] History categories: Attended, Not Attended, Declined, Expired
- [x] Pending accept/decline allowed only before RSVP deadline OR event start (whichever first)
- [x] Pending auto-becomes Expired when applicable deadline passes
- [x] Expired cannot later be accepted
- [x] Declined cannot later be accepted
- [x] Accepting does NOT auto-mean attended
- [x] After accepted event ends: leaves Upcoming, may show Attendance Pending
- [x] Attendance recorded separately as Attended / Not Attended
- [x] After attendance confirmed, event moves to correct history category
- [x] Feedback allowed only when Attended
- [x] Declined / Expired / Not Attended cannot submit feedback
- [x] Past invitations not shown in Pending section
- [x] Invalid status transitions rejected by backend with meaningful response
- [x] Admin/test backend endpoint to record attendance (no admin frontend needed)
- [x] `GET /users/{user_id}/invitations` (or equivalent)
- [x] `POST /invitations/{invitation_id}/respond`
- [x] `PATCH /invitations/{invitation_id}/attendance`
- [x] `GET /users/{user_id}/gathering-history`
- [x] `POST /invitations/{invitation_id}/feedback`
- [x] Seed data covers: future, pending, accepted, declined, expired, attendance-pending, attended, not-attended
- [x] Documented how expiry is handled (on-read vs background) — see README "Invitation & attendance status
      design" section

## General backend
- [x] Pydantic models for request AND response validation
- [x] Appropriate HTTP status codes + meaningful errors
- [x] Important timestamps generated on the backend
- [x] Structured exception handling
- [x] CORS configuration
- [x] Configuration in environment variables
- [x] `/health` endpoint
- [x] Dockerfile + instructions to run backend
- [x] Usable FastAPI/Swagger docs
- [x] No committed passwords/private keys/secrets — `backend/.env` is gitignored and untracked;
      `backend/.env.example` has placeholder only; real Gemini key added 2026-08-02 lives only in the local
      `.env`
- [x] Fixed demo user (e.g. `user-001`) usable
- [x] README explains how you'd authenticate requests and prevent cross-user access

## Testing (required cases)
- [x] Retrieve an existing profile
- [x] Complete a valid profile update
- [x] Reject invalid profile information
- [x] Validate a mocked Gemini response successfully
- [x] Handle Gemini timeout / malformed / service failure
- [x] Accept or decline a valid pending invitation
- [x] Auto-treat an ended pending invitation as Expired
- [x] Prevent acceptance of an expired invitation
- [x] Move an ended accepted invitation out of Upcoming
- [x] Prevent feedback from Not Attended / Declined / Expired user
- [x] Allow feedback from an Attended user

(40/40 `pytest` passing as of 2026-08-02, including after the live bio-limit change from 500→400.)

## Git
- [ ] Repo created from the beginning — **honest gap**: the backend/mobile scaffold was fully built before
      the first commit (`git log` showed zero commits partway through today); two commits
      (`9f60010`, `1d1a977`) were made after the fact to establish history, not incrementally from scratch.
      Worth being upfront about this if asked directly rather than implying otherwise.
- [ ] Regular, meaningful commits (not one final commit) — only 2 commits exist so far, both large/
      retroactive rather than incremental. Today's changes (bio-limit edit, any further work) should be
      committed as their own separate, meaningful commits to start correcting this before submission.
- [ ] GitHub link shared; access granted if private — remote `https://github.com/Atishay027/profile-ai-assessment`
      exists and local `main` is in sync with `origin/main`, but confirm the link has actually been sent to
      Preksha and repo visibility/access is correct.
- [x] Only legally-authorised code used

## AI-tool policy
- [x] `AI_USAGE.md` (or README section): which tools, what for, which suggestions reviewed/changed
- [ ] No AI coding assistants during Sunday live portion (Gemini feature calls are fine) — self-attested only;
      the one live-portion change on record (bio limit 500→400 in both `schemas.py` and `index.tsx`) is
      consistent with a manual edit, not independently verifiable from the repo alone.

## Final deliverables
- [x] GitHub repo link — `https://github.com/Atishay027/profile-ai-assessment` (confirm it's actually been
      sent, see Git section above)
- [x] Complete mobile + backend source
- [x] README with all required sections (see `README.template.md`)
- [x] `.env.example` with no real credentials
- [x] Seed data or seed script
- [x] Automated tests + run instructions
- [x] Backend Dockerfile
- [ ] Short screen recording of the final app — not yet produced
- [x] AI-usage disclosure
- [x] Final summary of completed / incomplete / known issues
