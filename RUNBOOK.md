# RUNBOOK — every command to set up, run, test, and demo this app

Quick-reference cheat sheet for the live checkpoint / demo recording. See `README.md` for the full
write-up (architecture, design decisions, security). This file is just commands.

---

## 0. One-time setup (already done if you've run this before)

```bash
cd ~/Desktop/assessment-app

# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# then open backend/.env and paste your real GEMINI_API_KEY
cd ..

# Mobile
cd mobile
npm install
cd ..
```

`mobile/.env` is already pre-filled with `EXPO_PUBLIC_API_URL=http://192.168.1.9:8000` (this machine's
current LAN IP, for Expo Go on a physical phone). If your IP changes, find the new one and update it:
```bash
ipconfig getifaddr en0        # macOS Wi-Fi — prints your current LAN IP
```

---

## 1. Run the backend

```bash
cd ~/Desktop/assessment-app/backend
source .venv/bin/activate
uvicorn app.main:app --reload
```
- API: http://localhost:8000
- Swagger / interactive API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- First run auto-creates tables and seeds demo data for `user-001` (only if no profile exists yet).

**Reseed demo data by hand** (wipes and re-inserts all scenarios for `user-001`):
```bash
python -m app.seed
```

---

## 2. Run the mobile app

In a second terminal:
```bash
cd ~/Desktop/assessment-app/mobile
npx expo start
```
- Scan the QR code with **Expo Go** on your phone (needs same Wi-Fi network as this computer).
- Or press `i` (iOS Simulator), `a` (Android Emulator), `w` (web) — remember to change
  `EXPO_PUBLIC_API_URL` in `mobile/.env` to match the target (see table below), then restart `expo start`.

| Target | `EXPO_PUBLIC_API_URL` |
|---|---|
| Physical phone via Expo Go | `http://<LAN-IP>:8000` |
| iOS Simulator | `http://localhost:8000` |
| Android Emulator | `http://10.0.2.2:8000` |

---

## 3. Run the backend tests

```bash
cd ~/Desktop/assessment-app/backend
source .venv/bin/activate
pytest -q
```
Expect `40 passed`. Gemini is fully mocked — no `GEMINI_API_KEY` needed, no real API calls made, no credits
spent. Run a single file or test to narrow down: `pytest tests/test_invitations.py -q` /
`pytest tests/test_invitations.py::test_accept_pending_invitation -v`.

---

## 4. Docker (backend only)

```bash
cd ~/Desktop/assessment-app
docker build -t assessment-backend ./backend
docker run --env-file backend/.env -p 8000:8000 assessment-backend
```
Verify: `curl http://localhost:8000/health`. Note: data does not persist across container restarts unless
you mount a volume (see README's "Docker (backend)" section) — fine for demoing the image builds/runs.

---

## 5. Persistence demo (proves data survives a backend restart)

```bash
# 1. Change something
curl -s -X PATCH http://localhost:8000/profiles/user-001 \
  -H "Content-Type: application/json" \
  -d '{"city": "Demo City"}'

# 2. Stop uvicorn (Ctrl+C in its terminal), then start it again
uvicorn app.main:app --reload

# 3. Fetch again — "city" is still "Demo City"
curl -s http://localhost:8000/profiles/user-001
```

---

## 6. Demo every endpoint directly with `curl` (no UI needed)

Useful for explaining the API/data flow live without depending on the phone.

```bash
BASE=http://localhost:8000

# Health
curl -s $BASE/health

# --- Profile ---
curl -s $BASE/profiles/user-001
curl -s -X PATCH $BASE/profiles/user-001 -H "Content-Type: application/json" \
  -d '{"occupation": "Staff Engineer"}'
# Validation error demo (empty required field -> 422):
curl -s -X PATCH $BASE/profiles/user-001 -H "Content-Type: application/json" -d '{"full_name": ""}'

# --- Gemini Insight ---
curl -s -X POST $BASE/profiles/user-001/insight
# If GEMINI_API_KEY isn't set yet, this returns 503 "AI service is not configured." — a real, expected
# failure-handling path, good to show live.

# --- Invitations ---
curl -s $BASE/users/user-001/invitations              # upcoming (actionable / accepted / attendance-pending)
curl -s $BASE/users/user-001/gathering-history         # attended / not_attended / declined / expired

# Accept or decline a pending invitation (grab an id from the upcoming list above first)
INV_ID=<paste-an-ACTIONABLE-invitation-id-here>
curl -s -X POST $BASE/invitations/$INV_ID/respond -H "Content-Type: application/json" \
  -d '{"action": "accept"}'

# Try to accept it again -> 409 (invalid transition, already accepted)
curl -s -X POST $BASE/invitations/$INV_ID/respond -H "Content-Type: application/json" \
  -d '{"action": "accept"}'

# Record attendance (admin/test-only endpoint, no mobile UI) — needs response=accepted AND event ended
ATTENDANCE_ID=<paste-an-invitation-id-whose-event-has-already-ended>
curl -s -X PATCH $BASE/invitations/$ATTENDANCE_ID/attendance -H "Content-Type: application/json" \
  -d '{"attendance": "attended"}'

# Submit feedback (only works if attendance_status == attended)
curl -s -X POST $BASE/invitations/$ATTENDANCE_ID/feedback -H "Content-Type: application/json" \
  -d '{"rating": 5, "comment": "Great session!"}'

# Feedback rejected from a non-attended invitation -> 409
DECLINED_ID=<paste-the-seeded-declined-invitation-id>
curl -s -X POST $BASE/invitations/$DECLINED_ID/feedback -H "Content-Type: application/json" \
  -d '{"comment": "n/a"}'
```

Tip: `curl -s $BASE/users/user-001/invitations | python3 -m json.tool` pretty-prints the response so ids are
easy to read and copy.

---

## 7. Kill a stuck backend process (if a port is already in use)

```bash
lsof -ti:8000 | xargs -r kill -9
```
