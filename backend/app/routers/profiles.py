from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import NotFoundError
from app.models import Profile
from app.schemas import ProfileOut, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/{user_id}", response_model=ProfileOut)
def get_profile(user_id: str, db: Session = Depends(get_db)):
    profile = db.get(Profile, user_id)
    if profile is None:
        raise NotFoundError(f"Profile '{user_id}' not found.")
    return profile


@router.patch("/{user_id}", response_model=ProfileOut)
def update_profile(user_id: str, payload: ProfileUpdate, db: Session = Depends(get_db)):
    profile = db.get(Profile, user_id)
    if profile is None:
        raise NotFoundError(f"Profile '{user_id}' not found.")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(profile, field, value)

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
