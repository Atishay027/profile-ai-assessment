from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import NotFoundError
from app.models import Feedback, Invitation
from app.schemas import (
    AttendanceRequest,
    FeedbackCreate,
    FeedbackOut,
    InvitationOut,
    RespondRequest,
)
from app.services.invitation_logic import (
    apply_lazy_expiry,
    assert_can_record_attendance,
    assert_can_respond,
    assert_can_submit_feedback,
    can_respond,
    can_submit_feedback,
    compute_bucket,
    is_history,
    is_upcoming,
)
from app.utils.time import now_utc

router = APIRouter(tags=["invitations"])


def _has_feedback(db: Session, invitation_id: str) -> bool:
    return db.query(Feedback.id).filter(Feedback.invitation_id == invitation_id).first() is not None


def _to_out(db: Session, invitation: Invitation, now) -> InvitationOut:
    bucket = compute_bucket(invitation, now)
    has_feedback = _has_feedback(db, invitation.id)
    return InvitationOut(
        id=invitation.id,
        user_id=invitation.user_id,
        title=invitation.title,
        description=invitation.description,
        location=invitation.location,
        event_start=invitation.event_start,
        event_end=invitation.event_end,
        rsvp_deadline=invitation.rsvp_deadline,
        response_status=invitation.response_status,
        attendance_status=invitation.attendance_status,
        responded_at=invitation.responded_at,
        attendance_recorded_at=invitation.attendance_recorded_at,
        created_at=invitation.created_at,
        updated_at=invitation.updated_at,
        bucket=bucket,
        can_respond=can_respond(invitation, now),
        can_submit_feedback=can_submit_feedback(invitation, has_feedback),
    )


def _get_invitation_or_404(db: Session, invitation_id: str) -> Invitation:
    invitation = db.get(Invitation, invitation_id)
    if invitation is None:
        raise NotFoundError(f"Invitation '{invitation_id}' not found.")
    return invitation


@router.get("/users/{user_id}/invitations", response_model=list[InvitationOut])
def list_upcoming_invitations(user_id: str, db: Session = Depends(get_db)):
    now = now_utc()
    invitations = db.query(Invitation).filter(Invitation.user_id == user_id).all()

    out = []
    for invitation in invitations:
        apply_lazy_expiry(db, invitation, now)
        bucket = compute_bucket(invitation, now)
        if is_upcoming(bucket):
            out.append(_to_out(db, invitation, now))

    out.sort(key=lambda i: i.event_start)
    return out


@router.get("/users/{user_id}/gathering-history", response_model=list[InvitationOut])
def gathering_history(user_id: str, db: Session = Depends(get_db)):
    now = now_utc()
    invitations = db.query(Invitation).filter(Invitation.user_id == user_id).all()

    out = []
    for invitation in invitations:
        apply_lazy_expiry(db, invitation, now)
        bucket = compute_bucket(invitation, now)
        if is_history(bucket):
            out.append(_to_out(db, invitation, now))

    out.sort(key=lambda i: i.event_start, reverse=True)
    return out


@router.post("/invitations/{invitation_id}/respond", response_model=InvitationOut)
def respond_to_invitation(invitation_id: str, payload: RespondRequest, db: Session = Depends(get_db)):
    invitation = _get_invitation_or_404(db, invitation_id)
    now = now_utc()
    apply_lazy_expiry(db, invitation, now)
    assert_can_respond(invitation, payload.action, now)

    invitation.response_status = "accepted" if payload.action == "accept" else "declined"
    invitation.responded_at = now
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return _to_out(db, invitation, now)


@router.patch("/invitations/{invitation_id}/attendance", response_model=InvitationOut)
def record_attendance(invitation_id: str, payload: AttendanceRequest, db: Session = Depends(get_db)):
    invitation = _get_invitation_or_404(db, invitation_id)
    now = now_utc()
    apply_lazy_expiry(db, invitation, now)
    assert_can_record_attendance(invitation, now)

    invitation.attendance_status = payload.attendance
    invitation.attendance_recorded_at = now
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return _to_out(db, invitation, now)


@router.post(
    "/invitations/{invitation_id}/feedback",
    response_model=FeedbackOut,
    status_code=status.HTTP_201_CREATED,
)
def submit_feedback(invitation_id: str, payload: FeedbackCreate, db: Session = Depends(get_db)):
    invitation = _get_invitation_or_404(db, invitation_id)
    now = now_utc()
    apply_lazy_expiry(db, invitation, now)
    assert_can_submit_feedback(invitation, _has_feedback(db, invitation.id))

    feedback = Feedback(
        invitation_id=invitation.id,
        user_id=invitation.user_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
