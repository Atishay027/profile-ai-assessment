from datetime import datetime

from sqlalchemy.orm import Session

from app.errors import FeedbackNotAllowedError, InvalidTransitionError
from app.models import Invitation
from app.utils.time import now_utc

UPCOMING_BUCKETS = {"ACTIONABLE", "ACCEPTED_UPCOMING", "ATTENDANCE_PENDING"}
HISTORY_BUCKETS = {"ATTENDED", "NOT_ATTENDED", "DECLINED", "EXPIRED"}


def effective_deadline(invitation: Invitation) -> datetime:
    if invitation.rsvp_deadline is not None:
        return min(invitation.rsvp_deadline, invitation.event_start)
    return invitation.event_start


def apply_lazy_expiry(db: Session, invitation: Invitation, now: datetime | None = None) -> Invitation:
    """Compute effective status from the clock; persist pending -> expired transitions."""
    now = now or now_utc()
    if invitation.response_status == "pending" and now >= effective_deadline(invitation):
        invitation.response_status = "expired"
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
    return invitation


def compute_bucket(invitation: Invitation, now: datetime | None = None) -> str:
    now = now or now_utc()

    if invitation.response_status == "pending":
        return "ACTIONABLE" if now < effective_deadline(invitation) else "EXPIRED"

    if invitation.response_status == "accepted":
        if now < invitation.event_end:
            return "ACCEPTED_UPCOMING"
        if invitation.attendance_status == "attendance_pending":
            return "ATTENDANCE_PENDING"
        if invitation.attendance_status == "attended":
            return "ATTENDED"
        return "NOT_ATTENDED"

    if invitation.response_status == "declined":
        return "DECLINED"

    return "EXPIRED"


def is_upcoming(bucket: str) -> bool:
    return bucket in UPCOMING_BUCKETS


def is_history(bucket: str) -> bool:
    return bucket in HISTORY_BUCKETS


# ---------- Computed flags for the client ----------

def can_respond(invitation: Invitation, now: datetime | None = None) -> bool:
    now = now or now_utc()
    return invitation.response_status == "pending" and now < effective_deadline(invitation)


def can_submit_feedback(invitation: Invitation, has_existing_feedback: bool) -> bool:
    return invitation.attendance_status == "attended" and not has_existing_feedback


# ---------- Guard functions (raise a DomainError if the transition isn't allowed) ----------

def assert_can_respond(invitation: Invitation, action: str, now: datetime | None = None) -> None:
    now = now or now_utc()
    if can_respond(invitation, now):
        return
    if invitation.response_status != "pending":
        if invitation.response_status == "expired":
            raise InvalidTransitionError("Cannot respond: RSVP window has closed; invitation expired.")
        raise InvalidTransitionError(f"Cannot {action}: invitation is {invitation.response_status}.")
    # Still 'pending' in the DB but the deadline has passed and apply_lazy_expiry() wasn't run first.
    raise InvalidTransitionError("Cannot respond: RSVP window has closed; invitation expired.")


def assert_can_record_attendance(invitation: Invitation, now: datetime | None = None) -> None:
    now = now or now_utc()
    if invitation.response_status != "accepted":
        raise InvalidTransitionError("Attendance only applies to accepted invitations.")
    if now < invitation.event_end:
        raise InvalidTransitionError("Cannot record attendance before the event has ended.")
    if invitation.attendance_status != "attendance_pending":
        raise InvalidTransitionError(
            f"Attendance already recorded as '{invitation.attendance_status}'; cannot re-record."
        )


def assert_can_submit_feedback(invitation: Invitation, has_existing_feedback: bool) -> None:
    if invitation.attendance_status != "attended":
        raise FeedbackNotAllowedError("Feedback is only allowed for invitations marked as attended.")
    if has_existing_feedback:
        raise FeedbackNotAllowedError("Feedback has already been submitted for this invitation.")
