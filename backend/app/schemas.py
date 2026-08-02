from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

BIO_MAX_LENGTH = 500


# ---------- Profile ----------

class ProfileOut(BaseModel):
    user_id: str
    full_name: str
    city: str
    occupation: str | None = None
    bio: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    city: str | None = None
    occupation: str | None = None
    bio: str | None = Field(default=None, max_length=BIO_MAX_LENGTH)

    @field_validator("full_name", "city")
    @classmethod
    def not_blank_if_provided(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("must not be empty")
        return v


# ---------- Gemini Insight ----------

class InsightResult(BaseModel):
    summary: str
    communication_style: str
    suggested_focus: str


# ---------- Invitations ----------

ResponseStatus = Literal["pending", "accepted", "declined", "expired"]
AttendanceStatus = Literal["attendance_pending", "attended", "not_attended"]
Bucket = Literal[
    "ACTIONABLE",
    "ACCEPTED_UPCOMING",
    "ATTENDANCE_PENDING",
    "ATTENDED",
    "NOT_ATTENDED",
    "DECLINED",
    "EXPIRED",
]


class InvitationOut(BaseModel):
    id: str
    user_id: str
    title: str
    description: str | None = None
    location: str | None = None
    event_start: datetime
    event_end: datetime
    rsvp_deadline: datetime | None = None
    response_status: ResponseStatus
    attendance_status: AttendanceStatus
    responded_at: datetime | None = None
    attendance_recorded_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    bucket: Bucket

    model_config = {"from_attributes": True}


class RespondRequest(BaseModel):
    action: Literal["accept", "decline"]


class AttendanceRequest(BaseModel):
    attendance: Literal["attended", "not_attended"]


class FeedbackCreate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str = Field(min_length=1, max_length=1000)


class FeedbackOut(BaseModel):
    id: str
    invitation_id: str
    user_id: str
    rating: int | None = None
    comment: str
    created_at: datetime

    model_config = {"from_attributes": True}
