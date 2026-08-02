"""Idempotent seed script: clears and re-inserts demo data for DEMO_USER_ID.

Run with: python -m app.seed
Times are computed relative to now_utc() so scenarios stay valid whenever it runs.
"""
from datetime import timedelta

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import Feedback, Invitation, Profile
from app.utils.time import now_utc


def seed() -> None:
    settings = get_settings()
    user_id = settings.demo_user_id

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.query(Feedback).filter(Feedback.user_id == user_id).delete()
        db.query(Invitation).filter(Invitation.user_id == user_id).delete()
        db.query(Profile).filter(Profile.user_id == user_id).delete()
        db.commit()

        now = now_utc()

        profile = Profile(
            user_id=user_id,
            full_name="Jordan Rivera",
            city="Austin",
            occupation="Product Designer",
            bio="Enjoys hiking, board game nights, and meeting new people at local meetups.",
        )
        db.add(profile)

        invitations = [
            # 1. Future / actionable pending
            Invitation(
                user_id=user_id,
                title="Rooftop Networking Mixer",
                description="Casual mixer for local product folks.",
                location="Downtown Rooftop Lounge",
                event_start=now + timedelta(days=5),
                event_end=now + timedelta(days=5, hours=2),
                rsvp_deadline=now + timedelta(days=3),
                response_status="pending",
                attendance_status="attendance_pending",
            ),
            # 2. Accepted upcoming
            Invitation(
                user_id=user_id,
                title="Board Game Night",
                description="Monthly board game night at the community hall.",
                location="Community Hall B",
                event_start=now + timedelta(days=2),
                event_end=now + timedelta(days=2, hours=3),
                rsvp_deadline=now + timedelta(days=1),
                response_status="accepted",
                attendance_status="attendance_pending",
                responded_at=now - timedelta(days=1),
            ),
            # 3. Declined
            Invitation(
                user_id=user_id,
                title="Early Morning Run Club",
                description="5k group run.",
                location="Riverside Park",
                event_start=now + timedelta(days=1),
                event_end=now + timedelta(days=1, hours=1),
                rsvp_deadline=now + timedelta(hours=12),
                response_status="declined",
                attendance_status="attendance_pending",
                responded_at=now - timedelta(hours=2),
            ),
            # 4. Expired (deadline already passed, still pending)
            Invitation(
                user_id=user_id,
                title="Weekend Hiking Trip",
                description="Day hike at the state park.",
                location="Trailhead Lot 2",
                event_start=now - timedelta(days=1),
                event_end=now - timedelta(days=1, hours=-4),
                rsvp_deadline=now - timedelta(days=2),
                response_status="pending",
                attendance_status="attendance_pending",
            ),
            # 5. Attendance pending (accepted, event ended, no attendance recorded)
            Invitation(
                user_id=user_id,
                title="Cooking Class: Pasta Night",
                description="Hands-on pasta-making class.",
                location="Downtown Culinary Studio",
                event_start=now - timedelta(days=3),
                event_end=now - timedelta(days=3, hours=-2),
                rsvp_deadline=now - timedelta(days=4),
                response_status="accepted",
                attendance_status="attendance_pending",
                responded_at=now - timedelta(days=6),
            ),
            # 6. Attended
            Invitation(
                user_id=user_id,
                title="Book Club: Sci-Fi Edition",
                description="Discussing this month's pick.",
                location="Central Library",
                event_start=now - timedelta(days=10),
                event_end=now - timedelta(days=10, hours=-2),
                rsvp_deadline=now - timedelta(days=11),
                response_status="accepted",
                attendance_status="attended",
                responded_at=now - timedelta(days=14),
                attendance_recorded_at=now - timedelta(days=9),
            ),
            # 7. Not attended
            Invitation(
                user_id=user_id,
                title="Volunteer Park Cleanup",
                description="Community park cleanup morning.",
                location="Greenway Park",
                event_start=now - timedelta(days=7),
                event_end=now - timedelta(days=7, hours=-3),
                rsvp_deadline=now - timedelta(days=8),
                response_status="accepted",
                attendance_status="not_attended",
                responded_at=now - timedelta(days=9),
                attendance_recorded_at=now - timedelta(days=6),
            ),
        ]
        db.add_all(invitations)
        db.commit()

        for inv in invitations:
            db.refresh(inv)

        attended_invitation = next(i for i in invitations if i.attendance_status == "attended")
        db.add(
            Feedback(
                invitation_id=attended_invitation.id,
                user_id=user_id,
                rating=5,
                comment="Great discussion, would attend again!",
            )
        )
        db.commit()

        print(f"Seeded profile + {len(invitations)} invitations for {user_id}.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
