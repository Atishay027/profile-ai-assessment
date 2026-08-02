# 07 — Database & Seed Data

## Default: SQLite + SQLAlchemy
- `DATABASE_URL=sqlite:///./app.db`. The `.db` file persists across backend restarts (requirement).
- Add `*.db` to `.gitignore`. The seed script recreates data as needed.
- Use `now_utc()` for all timestamps; store UTC.

## Tables
- **profiles**: `user_id` PK, `full_name`, `city`, `occupation?`, `bio?`, `created_at`, `updated_at`.
- **invitations**: `id` PK, `user_id`, `title`, `description?`, `location?`, `event_start`, `event_end`,
  `rsvp_deadline?`, `response_status`, `attendance_status`, `responded_at?`, `attendance_recorded_at?`,
  `created_at`, `updated_at`.
- **feedback**: `id` PK, `invitation_id` FK, `user_id`, `rating?`, `comment`, `created_at`.

## Seed data — must cover every scenario the brief lists
Create a seed script (idempotent: clear + insert, or upsert) for `user-001`. Use times relative to `now_utc()`
so the scenarios stay valid whenever you run it.

- **Profile**: one demo profile for `user-001`.
- **Invitations** (aim for one of each):
  1. **Future / actionable pending** — `event_start` in +5 days, `rsvp_deadline` +3 days, `response=pending`. (Upcoming, Accept/Decline available)
  2. **Accepted upcoming** — `event_start` +2 days, `response=accepted`, `attendance=attendance_pending`. (Upcoming, read-only)
  3. **Declined** — any past/future, `response=declined`. (History → Declined)
  4. **Expired** — `response=pending` but `rsvp_deadline`/`event_start` already in the past → reads as Expired. (History → Expired)
  5. **Attendance pending** — `response=accepted`, `event_end` in the past, `attendance=attendance_pending`. (Upcoming limbo)
  6. **Attended** — `response=accepted`, past event, `attendance=attended`. (History → Attended; feedback allowed)
  7. **Not attended** — `response=accepted`, past event, `attendance=not_attended`. (History → Not Attended; no feedback)

This gives you: future, pending, accepted, declined, expired, attendance-pending, attended, not-attended — the
full set the brief asks for, and enough to demo/test every rule.

## Firestore Emulator alternative (only if you choose it)
The brief says Firestore Emulator is "preferred" but SQLite is "acceptable." If you go Firestore:
- Run the emulator, point the Admin SDK at it via `FIRESTORE_EMULATOR_HOST`.
- Collections `profiles`, `invitations`, `feedback`; keep the same fields.
- Swap the persistence layer only; keep `services/invitation_logic.py`, schemas, and routers unchanged.
- Trade-off to note in README: extra local setup/tooling vs SQLite's zero-config persistence in a 2-day build.

Recommendation for the timeline: **start on SQLite**; only switch if you have spare time on Sunday.
