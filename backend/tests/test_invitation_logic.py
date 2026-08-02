"""Direct unit tests for the pure guard/computed-flag functions in services/invitation_logic.py.

These call the functions in isolation (no HTTP, no db-backed apply_lazy_expiry commit) so each
transition guard is verified on its own, independent of the FastAPI/HTTP layer.
"""
from datetime import datetime, timedelta, timezone

import pytest

from app.errors import FeedbackNotAllowedError, InvalidTransitionError
from app.models import Invitation
from app.services.invitation_logic import (
    assert_can_record_attendance,
    assert_can_respond,
    assert_can_submit_feedback,
    can_respond,
    can_submit_feedback,
    effective_deadline,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _invitation(**overrides) -> Invitation:
    now = _now()
    defaults = dict(
        user_id="user-001",
        title="Test Event",
        event_start=now + timedelta(days=5),
        event_end=now + timedelta(days=5, hours=2),
        rsvp_deadline=now + timedelta(days=3),
        response_status="pending",
        attendance_status="attendance_pending",
    )
    defaults.update(overrides)
    return Invitation(**defaults)


# ---------- effective_deadline ----------

def test_effective_deadline_is_earlier_of_rsvp_and_event_start():
    now = _now()
    inv = _invitation(event_start=now + timedelta(days=5), rsvp_deadline=now + timedelta(days=2))
    assert effective_deadline(inv) == now + timedelta(days=2)


def test_effective_deadline_falls_back_to_event_start_when_no_rsvp_deadline():
    now = _now()
    inv = _invitation(event_start=now + timedelta(days=5), rsvp_deadline=None)
    assert effective_deadline(inv) == now + timedelta(days=5)


# ---------- can_respond / assert_can_respond ----------

def test_can_respond_true_before_deadline():
    now = _now()
    inv = _invitation(rsvp_deadline=now + timedelta(hours=1))
    assert can_respond(inv, now) is True
    assert_can_respond(inv, "accept", now)  # does not raise


def test_can_respond_false_after_deadline():
    now = _now()
    inv = _invitation(rsvp_deadline=now - timedelta(hours=1))
    assert can_respond(inv, now) is False
    with pytest.raises(InvalidTransitionError):
        assert_can_respond(inv, "accept", now)


@pytest.mark.parametrize("status", ["accepted", "declined", "expired"])
def test_assert_can_respond_rejects_non_pending(status):
    inv = _invitation(response_status=status)
    with pytest.raises(InvalidTransitionError):
        assert_can_respond(inv, "accept", _now())


# ---------- assert_can_record_attendance ----------

def test_assert_can_record_attendance_rejects_non_accepted():
    inv = _invitation(response_status="pending")
    with pytest.raises(InvalidTransitionError):
        assert_can_record_attendance(inv, _now())


def test_assert_can_record_attendance_rejects_before_event_end():
    now = _now()
    inv = _invitation(
        response_status="accepted",
        event_start=now + timedelta(days=1),
        event_end=now + timedelta(days=1, hours=2),
    )
    with pytest.raises(InvalidTransitionError):
        assert_can_record_attendance(inv, now)


def test_assert_can_record_attendance_allows_valid_case():
    now = _now()
    inv = _invitation(
        response_status="accepted",
        event_start=now - timedelta(days=2),
        event_end=now - timedelta(days=1),
        attendance_status="attendance_pending",
    )
    assert_can_record_attendance(inv, now)  # does not raise


@pytest.mark.parametrize("recorded_status", ["attended", "not_attended"])
def test_assert_can_record_attendance_rejects_re_recording(recorded_status):
    now = _now()
    inv = _invitation(
        response_status="accepted",
        event_start=now - timedelta(days=2),
        event_end=now - timedelta(days=1),
        attendance_status=recorded_status,
    )
    with pytest.raises(InvalidTransitionError):
        assert_can_record_attendance(inv, now)


# ---------- can_submit_feedback / assert_can_submit_feedback ----------

def test_can_submit_feedback_true_when_attended_and_no_existing_feedback():
    inv = _invitation(response_status="accepted", attendance_status="attended")
    assert can_submit_feedback(inv, has_existing_feedback=False) is True
    assert_can_submit_feedback(inv, has_existing_feedback=False)  # does not raise


def test_can_submit_feedback_false_when_feedback_already_exists():
    inv = _invitation(response_status="accepted", attendance_status="attended")
    assert can_submit_feedback(inv, has_existing_feedback=True) is False
    with pytest.raises(FeedbackNotAllowedError):
        assert_can_submit_feedback(inv, has_existing_feedback=True)


@pytest.mark.parametrize("attendance_status", ["attendance_pending", "not_attended"])
def test_can_submit_feedback_false_when_not_attended(attendance_status):
    inv = _invitation(response_status="accepted", attendance_status=attendance_status)
    assert can_submit_feedback(inv, has_existing_feedback=False) is False
    with pytest.raises(FeedbackNotAllowedError):
        assert_can_submit_feedback(inv, has_existing_feedback=False)
