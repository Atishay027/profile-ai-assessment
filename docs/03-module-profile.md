# 03 — Module 1: Profile Management

## Goal
Demo user `user-001` can view and edit their profile; changes persist via FastAPI and survive backend restarts.

## Data
`Profile`: `user_id` (PK, str), `full_name` (str, required), `city` (str, required),
`occupation` (str, optional), `bio` (str, optional, max length), `created_at`, `updated_at`.

Bio limit: pick a reasonable cap (e.g. **500 chars**) and enforce it in both Pydantic and the mobile form.

## Endpoints

### GET /profiles/{user_id}
- 200 with profile if exists.
- 404 with meaningful body if not.

### PATCH /profiles/{user_id}
- Body is a **partial** update model: every field optional, but if `full_name`/`city` are *present* they must
  be non-empty. Unspecified fields are left unchanged.
- Validate: non-empty `full_name`/`city` when provided; `bio` within limit; reject unknown/invalid types with 422.
- Update `updated_at` on the backend. Return the full updated profile (200).
- 404 if the profile doesn't exist.

## Validation matrix
| Input | Result |
|-------|--------|
| Valid partial update | 200, updated profile returned |
| `full_name` = "" (empty) when provided | 422 with field error |
| `city` = "" when provided | 422 with field error |
| `bio` over limit | 422 with field error |
| Unknown user id | 404 |

## Mobile requirements
- Profile screen shows current values (view mode) and an edit form.
- **States:** loading (fetch/save in flight), empty (no profile yet), success (after save), error (network/validation).
- Show **frontend** validation inline (required name+city, bio counter/limit) *and* surface **backend**
  validation errors (422 details) clearly.
- **Disable the Save button / block duplicate submits** while a request is in flight.
- After a successful save, **refetch** the profile (TanStack Query `invalidateQueries`) so the UI reflects the saved state.

## Persistence check
Save a change, restart the backend process, GET the profile → the change is still there. (SQLite file persists.)
