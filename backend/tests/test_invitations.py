from datetime import datetime, timedelta, timezone

from app.models import Invitation, Profile

USER = "user-001"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _insert_profile(db):
    profile = Profile(user_id=USER, full_name="Jordan Rivera", city="Austin")
    db.add(profile)
    db.commit()
    return profile


def _insert_invitation(db, **overrides) -> Invitation:
    now = _now()
    defaults = dict(
        user_id=USER,
        title="Test Event",
        event_start=now + timedelta(days=5),
        event_end=now + timedelta(days=5, hours=2),
        rsvp_deadline=now + timedelta(days=3),
        response_status="pending",
        attendance_status="attendance_pending",
    )
    defaults.update(overrides)
    invitation = Invitation(**defaults)
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


# ---------- Respond: accept / decline ----------

def test_accept_pending_invitation(client, db):
    inv = _insert_invitation(db)
    resp = client.post(f"/invitations/{inv.id}/respond", json={"action": "accept"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["response_status"] == "accepted"
    assert body["attendance_status"] == "attendance_pending"  # accepting != attending
    assert body["responded_at"] is not None


def test_decline_pending_invitation(client, db):
    inv = _insert_invitation(db)
    resp = client.post(f"/invitations/{inv.id}/respond", json={"action": "decline"})
    assert resp.status_code == 200
    assert resp.json()["response_status"] == "declined"


def test_respond_invalid_action_returns_422(client, db):
    inv = _insert_invitation(db)
    resp = client.post(f"/invitations/{inv.id}/respond", json={"action": "maybe"})
    assert resp.status_code == 422


def test_respond_unknown_invitation_returns_404(client, db):
    resp = client.post("/invitations/does-not-exist/respond", json={"action": "accept"})
    assert resp.status_code == 404


# ---------- Expiry ----------

def test_ended_pending_invitation_auto_expires_and_blocks_respond(client, db):
    now = _now()
    inv = _insert_invitation(
        db,
        event_start=now - timedelta(days=1),
        event_end=now - timedelta(hours=20),
        rsvp_deadline=now - timedelta(days=2),
    )

    upcoming = client.get(f"/users/{USER}/invitations").json()
    assert all(i["id"] != inv.id for i in upcoming)

    history = client.get(f"/users/{USER}/gathering-history").json()
    matching = [i for i in history if i["id"] == inv.id]
    assert len(matching) == 1
    assert matching[0]["response_status"] == "expired"
    assert matching[0]["bucket"] == "EXPIRED"

    resp = client.post(f"/invitations/{inv.id}/respond", json={"action": "accept"})
    assert resp.status_code == 409


def test_prevent_accept_of_already_expired_invitation(client, db):
    now = _now()
    inv = _insert_invitation(
        db,
        event_start=now - timedelta(days=1),
        event_end=now - timedelta(hours=20),
        rsvp_deadline=now - timedelta(days=2),
        response_status="expired",
    )
    resp = client.post(f"/invitations/{inv.id}/respond", json={"action": "accept"})
    assert resp.status_code == 409


def test_prevent_accept_of_declined_invitation(client, db):
    inv = _insert_invitation(db, response_status="declined")
    resp = client.post(f"/invitations/{inv.id}/respond", json={"action": "accept"})
    assert resp.status_code == 409


def test_prevent_double_accept(client, db):
    inv = _insert_invitation(db, response_status="accepted", responded_at=_now())
    resp = client.post(f"/invitations/{inv.id}/respond", json={"action": "accept"})
    assert resp.status_code == 409


# ---------- Upcoming / history bucketing ----------

def test_accepted_upcoming_appears_in_upcoming_list(client, db):
    now = _now()
    inv = _insert_invitation(
        db,
        event_start=now + timedelta(days=2),
        event_end=now + timedelta(days=2, hours=2),
        response_status="accepted",
        responded_at=now - timedelta(hours=1),
    )
    upcoming = client.get(f"/users/{USER}/invitations").json()
    match = next(i for i in upcoming if i["id"] == inv.id)
    assert match["bucket"] == "ACCEPTED_UPCOMING"


def test_ended_accepted_invitation_becomes_attendance_pending_limbo(client, db):
    now = _now()
    inv = _insert_invitation(
        db,
        event_start=now - timedelta(days=2),
        event_end=now - timedelta(days=2, hours=-2),  # ended ~46h ago
        rsvp_deadline=now - timedelta(days=3),
        response_status="accepted",
        responded_at=now - timedelta(days=4),
    )
    upcoming = client.get(f"/users/{USER}/invitations").json()
    match = next(i for i in upcoming if i["id"] == inv.id)
    assert match["bucket"] == "ATTENDANCE_PENDING"

    history = client.get(f"/users/{USER}/gathering-history").json()
    assert all(i["id"] != inv.id for i in history)  # attendance-pending is not a history category


def test_actionable_pending_appears_in_upcoming(client, db):
    inv = _insert_invitation(db)
    upcoming = client.get(f"/users/{USER}/invitations").json()
    match = next(i for i in upcoming if i["id"] == inv.id)
    assert match["bucket"] == "ACTIONABLE"


def test_declined_appears_only_in_history(client, db):
    inv = _insert_invitation(db, response_status="declined", responded_at=_now())
    upcoming = client.get(f"/users/{USER}/invitations").json()
    assert all(i["id"] != inv.id for i in upcoming)

    history = client.get(f"/users/{USER}/gathering-history").json()
    match = next(i for i in history if i["id"] == inv.id)
    assert match["bucket"] == "DECLINED"


# ---------- Attendance endpoint ----------

def test_attendance_requires_accepted_status(client, db):
    inv = _insert_invitation(db)  # still pending
    resp = client.patch(f"/invitations/{inv.id}/attendance", json={"attendance": "attended"})
    assert resp.status_code == 409


def test_attendance_requires_event_to_have_ended(client, db):
    now = _now()
    inv = _insert_invitation(
        db,
        event_start=now + timedelta(days=1),
        event_end=now + timedelta(days=1, hours=2),
        response_status="accepted",
        responded_at=now - timedelta(hours=1),
    )
    resp = client.patch(f"/invitations/{inv.id}/attendance", json={"attendance": "attended"})
    assert resp.status_code == 409


def test_record_attendance_success_moves_to_history(client, db):
    now = _now()
    inv = _insert_invitation(
        db,
        event_start=now - timedelta(days=2),
        event_end=now - timedelta(days=2, hours=-2),
        response_status="accepted",
        responded_at=now - timedelta(days=3),
    )
    resp = client.patch(f"/invitations/{inv.id}/attendance", json={"attendance": "attended"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["attendance_status"] == "attended"
    assert body["attendance_recorded_at"] is not None

    history = client.get(f"/users/{USER}/gathering-history").json()
    match = next(i for i in history if i["id"] == inv.id)
    assert match["bucket"] == "ATTENDED"


def test_attendance_unknown_invitation_returns_404(client, db):
    resp = client.patch("/invitations/does-not-exist/attendance", json={"attendance": "attended"})
    assert resp.status_code == 404


# ---------- Feedback gating ----------

def test_feedback_allowed_when_attended(client, db):
    now = _now()
    inv = _insert_invitation(
        db,
        event_start=now - timedelta(days=5),
        event_end=now - timedelta(days=5, hours=-2),
        response_status="accepted",
        attendance_status="attended",
        responded_at=now - timedelta(days=6),
        attendance_recorded_at=now - timedelta(days=4),
    )
    resp = client.post(f"/invitations/{inv.id}/feedback", json={"rating": 5, "comment": "Great!"})
    assert resp.status_code == 201
    assert resp.json()["comment"] == "Great!"


def test_feedback_rejected_when_not_attended(client, db):
    now = _now()
    inv = _insert_invitation(
        db,
        event_start=now - timedelta(days=5),
        event_end=now - timedelta(days=5, hours=-2),
        response_status="accepted",
        attendance_status="not_attended",
        responded_at=now - timedelta(days=6),
        attendance_recorded_at=now - timedelta(days=4),
    )
    resp = client.post(f"/invitations/{inv.id}/feedback", json={"comment": "n/a"})
    assert resp.status_code == 409


def test_feedback_rejected_when_declined(client, db):
    inv = _insert_invitation(db, response_status="declined", responded_at=_now())
    resp = client.post(f"/invitations/{inv.id}/feedback", json={"comment": "n/a"})
    assert resp.status_code == 409


def test_feedback_rejected_when_expired(client, db):
    now = _now()
    inv = _insert_invitation(
        db,
        event_start=now - timedelta(days=1),
        event_end=now - timedelta(hours=20),
        rsvp_deadline=now - timedelta(days=2),
    )
    resp = client.post(f"/invitations/{inv.id}/feedback", json={"comment": "n/a"})
    assert resp.status_code == 409


def test_feedback_rejected_when_accepted_but_not_yet_attended(client, db):
    now = _now()
    inv = _insert_invitation(
        db,
        event_start=now + timedelta(days=2),
        event_end=now + timedelta(days=2, hours=2),
        response_status="accepted",
        responded_at=now - timedelta(hours=1),
    )
    resp = client.post(f"/invitations/{inv.id}/feedback", json={"comment": "n/a"})
    assert resp.status_code == 409


def test_feedback_invalid_payload_returns_422(client, db):
    now = _now()
    inv = _insert_invitation(
        db,
        event_start=now - timedelta(days=5),
        event_end=now - timedelta(days=5, hours=-2),
        response_status="accepted",
        attendance_status="attended",
        responded_at=now - timedelta(days=6),
        attendance_recorded_at=now - timedelta(days=4),
    )
    resp = client.post(f"/invitations/{inv.id}/feedback", json={"comment": ""})
    assert resp.status_code == 422
