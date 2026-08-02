# 05 — Module 3: Event Invitations & History (state machine)

This is the highest-risk module. Read it fully before coding. All rules are enforced on the **backend**.

## Two-field model (recommended, and allowed by the brief)
- `response_status`: `pending | accepted | declined | expired`
- `attendance_status`: `attendance_pending | attended | not_attended`

`attendance_status` only becomes meaningful once `response_status == accepted` and the event has ended.

## Invitation fields
`id`, `user_id`, `title`, `description?`, `location?`,
`event_start` (UTC), `event_end` (UTC),
`rsvp_deadline` (UTC, nullable),
`response_status`, `attendance_status`,
`responded_at?`, `attendance_recorded_at?`, `created_at`, `updated_at`.

`Feedback`: `id`, `invitation_id`, `user_id`, `rating?` (e.g. 1–5), `comment`, `created_at`.

## Effective deadline
`effective_deadline = min(rsvp_deadline, event_start)` if `rsvp_deadline` is set, else `event_start`.
(The brief: accept/decline only "before its RSVP deadline or event start time, whichever comes first.")

## Expiry policy — CHOSEN APPROACH (document this in README)
**Lazy, computed-on-read, persisted on transition.** Whenever an invitation is read or acted upon, we first
compute its effective status from `now_utc()`. If it's still `pending` and `now >= effective_deadline`, we
set it to `expired` and persist that. This is deterministic and easy to test (seed a past deadline → it reads
as expired). Alternative (background job/scheduler) is noted in README as a scaling option we deliberately did
not need for this scope.

## Derived "bucket" (single source of truth for lists)
Compute a bucket for each invitation on read:

| Condition | bucket | Appears in |
|-----------|--------|-----------|
| `response_status == pending` and `now < effective_deadline` | `ACTIONABLE` | Upcoming |
| `response_status == pending` and `now >= effective_deadline` | `EXPIRED` (persist) | History |
| `response_status == accepted` and `now < event_end` | `ACCEPTED_UPCOMING` | Upcoming |
| `response_status == accepted` and `now >= event_end` and `attendance_status == attendance_pending` | `ATTENDANCE_PENDING` | Upcoming (limbo) |
| `response_status == accepted` and `attendance_status == attended` | `ATTENDED` | History |
| `response_status == accepted` and `attendance_status == not_attended` | `NOT_ATTENDED` | History |
| `response_status == declined` | `DECLINED` | History |
| `response_status == expired` | `EXPIRED` | History |

- **Upcoming/current list** (`GET /users/{id}/invitations`) = `ACTIONABLE + ACCEPTED_UPCOMING + ATTENDANCE_PENDING`.
- **Gathering history** (`GET /users/{id}/gathering-history`) = `ATTENDED + NOT_ATTENDED + DECLINED + EXPIRED`
  (exactly the four categories the brief lists — Attendance Pending is NOT a history category).
- **Past invitations never appear in the pending/actionable section** — only `ACTIONABLE` items are pending.

## State diagram
```
                 accept (before deadline)         event ends        record attendance
  PENDING ─────────────────────────────► ACCEPTED ──────────► ATTENDANCE_PENDING ──┬─► ATTENDED ──► (feedback allowed)
     │  \                                                                          └─► NOT_ATTENDED ─► (no feedback)
     │   \ decline (before deadline)
     │    └────────────────────────────► DECLINED  (terminal, no feedback)
     │
     └ deadline passes while pending ───► EXPIRED   (terminal, cannot be accepted, no feedback)
```

## Endpoints & guards

### GET /users/{user_id}/invitations
Return current/upcoming items (buckets `ACTIONABLE`, `ACCEPTED_UPCOMING`, `ATTENDANCE_PENDING`), each with its
computed bucket/status so the UI can render sections. Apply lazy expiry first.

### POST /invitations/{invitation_id}/respond
Body: `{ "action": "accept" | "decline" }`.
1. Load invitation; apply lazy expiry.
2. If `response_status != pending` → **409** meaningful error, e.g. "Cannot accept: invitation is {status}."
   (Covers: expired cannot be accepted; declined cannot be accepted; already accepted.)
3. If `now >= effective_deadline` → set `expired`, return **409** "RSVP window has closed; invitation expired."
4. Else set `response_status = accepted|declined`, `responded_at = now_utc()`. Accepting keeps
   `attendance_status = attendance_pending` (accepting is NOT attending). Return 200 with updated invitation.

### PATCH /invitations/{invitation_id}/attendance  (admin/test endpoint)
Body: `{ "attendance": "attended" | "not_attended" }`.
1. Load invitation.
2. Guard: `response_status` must be `accepted`, else **409** "Attendance only applies to accepted invitations."
3. Recommended guard: require `now >= event_end` (can't attend an event that hasn't happened), else **409**.
4. Set `attendance_status`, `attendance_recorded_at = now_utc()`. Return 200.
(No admin frontend needed — this endpoint exists to drive the demo/tests.)

### GET /users/{user_id}/gathering-history
Return terminal items grouped/categorised as Attended / Not Attended / Declined / Expired.

### POST /invitations/{invitation_id}/feedback
Body: `{ "rating"?: int, "comment": str }`.
1. Load invitation.
2. Guard: allow only if `attendance_status == attended`. Otherwise **403/409** with a meaningful reason.
   Explicitly reject Declined, Expired, Not Attended, and pending/accepted-not-yet-attended.
3. Persist feedback, return 201.

## Invalid transition handling (general)
Any disallowed transition returns a proper 4xx (409 for state conflicts, 422 for bad payloads) with a clear,
non-sensitive message. Never silently no-op.

## Mobile requirements
- **Upcoming** section: actionable pending (Accept/Decline buttons), accepted-upcoming (read-only), and
  attendance-pending limbo (labelled, no RSVP buttons).
- **History** section: four categories with correct labels.
- Feedback UI appears **only** on Attended items.
- Standard loading/empty/success/error states and in-flight guards on every action.
