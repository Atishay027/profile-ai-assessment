# 09 — Security & Auth (README write-up)

Auth is **not required** to be implemented, but the README **must** explain how you *would* authenticate
requests and prevent one user from reading/modifying another's data. Draft that explanation here and copy it
into the README.

## Secrets handling (implement this)
- `GEMINI_API_KEY` only in the backend environment; never in the mobile app, never in git.
- `.gitignore` covers `.env`, `*.db`, `node_modules`, `__pycache__`, Expo/build artifacts.
- `.env.example` files contain placeholders only.
- Backend error responses and logs never include the key, raw provider errors, or stack traces.

## How I would add authentication (write-up for README)
- Issue a token on login (e.g. JWT or a session token from an identity provider / Firebase Auth).
- Mobile stores it in secure storage (`expo-secure-store`) and sends `Authorization: Bearer <token>` on every request.
- A FastAPI dependency validates the token on protected routes and resolves the caller's `user_id` from the
  token — **not** from the URL/body.

## Preventing cross-user access (write-up for README)
- Never trust the `{user_id}` in the path as proof of identity. After validating the token, **compare the
  authenticated user's id to the resource owner** and reject mismatches with **403**.
- Scope every query by the authenticated user (e.g. `WHERE user_id = current_user`) so a user can only ever
  read/modify their own profile, invitations, and feedback.
- The admin/attendance endpoint would sit behind an admin role/scope in a real system.

## Current demo posture (state honestly)
- For this assessment, a fixed demo user `user-001` is used and endpoints are unauthenticated by design.
- CORS is permissive for local development; in production it would be restricted to known origins.
- Note this clearly under "Known limitations" so it reads as a conscious scoping decision, not an oversight.
