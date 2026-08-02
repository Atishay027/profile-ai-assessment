# 06 — Backend Spec (FastAPI)

## Layout
```
backend/app/
  main.py            # create app, register routers, CORS, exception handlers, /health
  config.py          # pydantic-settings Settings; read all env vars here
  database.py        # engine + SessionLocal + Base; get_db dependency
  models.py          # SQLAlchemy models: Profile, Invitation, Feedback
  schemas.py         # Pydantic v2 request/response models
  seed.py            # idempotent seed script
  utils/time.py      # now_utc()
  services/gemini.py
  services/invitation_logic.py
  routers/profiles.py
  routers/insight.py
  routers/invitations.py
backend/tests/...
backend/Dockerfile
backend/requirements.txt
backend/.env.example
```

## Config (`config.py`, pydantic-settings)
Read from env, no hardcoding:
- `APP_ENV`, `DATABASE_URL` (default `sqlite:///./app.db`)
- `GEMINI_API_KEY`, `GEMINI_MODEL`
- `CORS_ORIGINS` (comma-separated; default permissive for the demo)
- `DEMO_USER_ID` (default `user-001`)
- `GEMINI_TIMEOUT_SECONDS` (e.g. 20)

## main.py essentials
- Instantiate `FastAPI(title=...)` so Swagger at `/docs` is meaningful.
- Add `CORSMiddleware` from `CORS_ORIGINS`.
- Register routers.
- `GET /health` → `{"status": "ok"}` (200). Optionally include a quick DB check.
- **Structured exception handling:** custom exception handlers that convert domain errors
  (e.g. `InvalidTransition`, `NotFound`) and unexpected exceptions into consistent JSON:
  `{"detail": "<message>", "code": "<machine_code>"}` with correct status codes. Never return raw tracebacks.
- Create tables on startup (or via a small init) and, in dev, run the seed if the DB is empty.

## Error conventions
- 404 not found; 409 state conflict / invalid transition; 422 validation (FastAPI default for Pydantic);
  502/504/429 for Gemini upstream issues (see `docs/04`); 500 only for truly unexpected errors.
- Messages are human-readable and free of internal detail (no keys, no stack traces, no SQL).

## Timestamps
All of `created_at`, `updated_at`, `responded_at`, `attendance_recorded_at` are set on the backend via
`now_utc()`. Never accept these from the client.

## Dockerfile (backend) — outline
- Base `python:3.12-slim`.
- Set workdir, copy `requirements.txt`, `pip install`, copy `app/`.
- Expose 8000. `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`.
- README documents: `docker build -t assessment-backend ./backend` and
  `docker run --env-file backend/.env -p 8000:8000 assessment-backend`.
- Consider a volume for the SQLite file if persistence across container restarts is desired; document the choice.

## requirements.txt (indicative)
`fastapi`, `uvicorn[standard]`, `sqlalchemy`, `pydantic>=2`, `pydantic-settings`,
Gemini SDK (`google-generativeai`) or `httpx` if calling REST directly, `pytest`, `httpx`/`pytest` test client,
and a mocking helper (`respx` if using httpx, else `unittest.mock`).
