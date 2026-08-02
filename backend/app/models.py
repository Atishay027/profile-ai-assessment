import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, UTCDateTime
from app.utils.time import now_utc


def _uuid() -> str:
    return str(uuid.uuid4())


class Profile(Base):
    __tablename__ = "profiles"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    occupation: Mapped[str | None] = mapped_column(String, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[object] = mapped_column(UTCDateTime, default=now_utc)
    updated_at: Mapped[object] = mapped_column(UTCDateTime, default=now_utc, onupdate=now_utc)


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)

    event_start: Mapped[object] = mapped_column(UTCDateTime, nullable=False)
    event_end: Mapped[object] = mapped_column(UTCDateTime, nullable=False)
    rsvp_deadline: Mapped[object | None] = mapped_column(UTCDateTime, nullable=True)

    response_status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    attendance_status: Mapped[str] = mapped_column(String, nullable=False, default="attendance_pending")

    responded_at: Mapped[object | None] = mapped_column(UTCDateTime, nullable=True)
    attendance_recorded_at: Mapped[object | None] = mapped_column(UTCDateTime, nullable=True)

    created_at: Mapped[object] = mapped_column(UTCDateTime, default=now_utc)
    updated_at: Mapped[object] = mapped_column(UTCDateTime, default=now_utc, onupdate=now_utc)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    invitation_id: Mapped[str] = mapped_column(ForeignKey("invitations.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[object] = mapped_column(UTCDateTime, default=now_utc)
