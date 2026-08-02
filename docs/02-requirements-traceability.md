# 02 — Requirements Traceability (the anti-miss checklist)

Every requirement from the assessment email is a checkbox below. Tick as you complete. If something here is
unchecked at submission time, either finish it or document it as a known limitation in the README.

## Module 1 — Profile Management
- [ ] View profile
- [ ] Edit full name, city, occupation, short bio
- [ ] Save changes through the FastAPI backend
- [ ] Full name required
- [ ] City required
- [ ] Bio has a reasonable character limit
- [ ] Partial profile updates supported (PATCH semantics)
- [ ] Loading state
- [ ] Empty state
- [ ] Success state
- [ ] Error state
- [ ] Frontend validation errors shown clearly
- [ ] Backend validation errors shown clearly
- [ ] Repeated submissions prevented while a request is processing
- [ ] Profile refreshes after a successful update
- [ ] Profile persists after restarting the backend
- [ ] `GET /profiles/{user_id}` (or equivalent)
- [ ] `PATCH /profiles/{user_id}` (or equivalent)

## Module 2 — Gemini Profile Insight
- [ ] "Generate Profile Insight" button
- [ ] Loading state while generating
- [ ] Generated result displayed clearly
- [ ] Useful error message on failure
- [ ] Repeated requests prevented while generation in progress
- [ ] AI result does NOT auto-overwrite profile info
- [ ] `POST /profiles/{user_id}/insight` (or equivalent)
- [ ] Backend retrieves saved profile
- [ ] Sends relevant demo-profile info to Gemini
- [ ] Requests structured JSON: `summary`, `communication_style`, `suggested_focus`
- [ ] Validates Gemini response with Pydantic before returning
- [ ] `GEMINI_API_KEY` in env var
- [ ] `GEMINI_MODEL` configurable via env var
- [ ] Gemini key never exposed to mobile
- [ ] Handles missing key
- [ ] Handles timeout
- [ ] Handles rate limits
- [ ] Handles malformed response
- [ ] Handles Gemini service errors
- [ ] Returns meaningful errors without leaking internal details
- [ ] Uses a key you're authorised to use; no paid spend expected
- [ ] Automated tests mock Gemini; consume no real credits

## Module 3 — Event Invitations & History
- [ ] View upcoming invitations
- [ ] Accept or decline a pending invitation
- [ ] View gathering history
- [ ] Correct status for past invitations
- [ ] Submit feedback only when attendance confirmed (Attended)
- [ ] Response states modelled: Pending, Accepted, Declined, Expired
- [ ] Attendance states modelled: Attendance Pending, Attended, Not Attended
- [ ] History categories: Attended, Not Attended, Declined, Expired
- [ ] Pending accept/decline allowed only before RSVP deadline OR event start (whichever first)
- [ ] Pending auto-becomes Expired when applicable deadline passes
- [ ] Expired cannot later be accepted
- [ ] Declined cannot later be accepted
- [ ] Accepting does NOT auto-mean attended
- [ ] After accepted event ends: leaves Upcoming, may show Attendance Pending
- [ ] Attendance recorded separately as Attended / Not Attended
- [ ] After attendance confirmed, event moves to correct history category
- [ ] Feedback allowed only when Attended
- [ ] Declined / Expired / Not Attended cannot submit feedback
- [ ] Past invitations not shown in Pending section
- [ ] Invalid status transitions rejected by backend with meaningful response
- [ ] Admin/test backend endpoint to record attendance (no admin frontend needed)
- [ ] `GET /users/{user_id}/invitations` (or equivalent)
- [ ] `POST /invitations/{invitation_id}/respond`
- [ ] `PATCH /invitations/{invitation_id}/attendance`
- [ ] `GET /users/{user_id}/gathering-history`
- [ ] `POST /invitations/{invitation_id}/feedback`
- [ ] Seed data covers: future, pending, accepted, declined, expired, attendance-pending, attended, not-attended
- [ ] Documented how expiry is handled (on-read vs background)

## General backend
- [ ] Pydantic models for request AND response validation
- [ ] Appropriate HTTP status codes + meaningful errors
- [ ] Important timestamps generated on the backend
- [ ] Structured exception handling
- [ ] CORS configuration
- [ ] Configuration in environment variables
- [ ] `/health` endpoint
- [ ] Dockerfile + instructions to run backend
- [ ] Usable FastAPI/Swagger docs
- [ ] No committed passwords/private keys/secrets
- [ ] Fixed demo user (e.g. `user-001`) usable
- [ ] README explains how you'd authenticate requests and prevent cross-user access

## Testing (required cases)
- [ ] Retrieve an existing profile
- [ ] Complete a valid profile update
- [ ] Reject invalid profile information
- [ ] Validate a mocked Gemini response successfully
- [ ] Handle Gemini timeout / malformed / service failure
- [ ] Accept or decline a valid pending invitation
- [ ] Auto-treat an ended pending invitation as Expired
- [ ] Prevent acceptance of an expired invitation
- [ ] Move an ended accepted invitation out of Upcoming
- [ ] Prevent feedback from Not Attended / Declined / Expired user
- [ ] Allow feedback from an Attended user

## Git
- [ ] Repo created from the beginning
- [ ] Regular, meaningful commits (not one final commit)
- [ ] GitHub link shared; access granted if private
- [ ] Only legally-authorised code used

## AI-tool policy
- [ ] `AI_USAGE.md` (or README section): which tools, what for, which suggestions reviewed/changed
- [ ] No AI coding assistants during Sunday live portion (Gemini feature calls are fine)

## Final deliverables
- [ ] GitHub repo link
- [ ] Complete mobile + backend source
- [ ] README with all required sections (see `README.template.md`)
- [ ] `.env.example` with no real credentials
- [ ] Seed data or seed script
- [ ] Automated tests + run instructions
- [ ] Backend Dockerfile
- [ ] Short screen recording of the final app
- [ ] AI-usage disclosure
- [ ] Final summary of completed / incomplete / known issues
