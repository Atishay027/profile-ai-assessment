from datetime import datetime

from sqlalchemy.orm import Session

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
