# 00 — Overview & Architecture

## What we're building

One FastAPI backend + one Expo mobile app. Three modules share the demo user `user-001`.

- **Profile Management:** view and partially edit a profile (full name, city, occupation, bio).
- **Gemini Profile Insight:** backend calls Gemini with the saved profile, returns structured JSON
  (`summary`, `communication_style`, `suggested_focus`).
- **Event Invitations & History:** RSVP state machine (Pending → Accepted/Declined/Expired), separate
  attendance tracking, gathering history, and feedback gated on attendance.

## Data flow

```
[Expo app]  --HTTP-->  [FastAPI]  --SQLAlchemy-->  [SQLite file (persists)]
    |                     |
    |                     +--HTTPS-->  [Google Gemini API]   (key stays server-side)
    |
  screens: Profile / Insight / Invitations+History
```

The phone never holds the Gemini key and never talks to Gemini directly. It only calls FastAPI.

## Key architectural decisions (also record these in README)

1. **SQLite + SQLAlchemy** for persistence: zero external setup, survives restarts, trivial to seed and test.
   Firestore Emulator is an accepted alternative (`docs/07`) but adds setup cost inside a 2-day window.
2. **Lazy expiry, computed on read** (with persistence on transition): an invitation's effective status is
   derived from the clock whenever it is read or acted upon. Simple, deterministic, easy to test. Documented
   as the chosen approach vs a background job (`docs/05`).
3. **Two separate fields** on an invitation: `response_status` (pending/accepted/declined/expired) and
   `attendance_status` (attendance_pending/attended/not_attended). This cleanly separates "did they RSVP" from
   "did they show up", exactly as the brief allows.
4. **Single clock source** `now_utc()` so tests can freeze/shift time to exercise expiry and attendance rules.
5. **Server-authored timestamps** for created/updated/responded/attendance-recorded.
6. **TanStack Query** on mobile so loading/empty/success/error states and refetch-after-mutation are
   first-class, which the brief explicitly grades.

## Endpoint summary

| Method | Path | Module |
|--------|------|--------|
| GET | `/health` | infra |
| GET | `/profiles/{user_id}` | Profile |
| PATCH | `/profiles/{user_id}` | Profile |
| POST | `/profiles/{user_id}/insight` | Gemini |
| GET | `/users/{user_id}/invitations` | Invitations (upcoming/current) |
| POST | `/invitations/{invitation_id}/respond` | Invitations |
| PATCH | `/invitations/{invitation_id}/attendance` | Invitations (admin/test) |
| GET | `/users/{user_id}/gathering-history` | Invitations |
| POST | `/invitations/{invitation_id}/feedback` | Invitations |

Swagger/OpenAPI is auto-exposed by FastAPI at `/docs`.
