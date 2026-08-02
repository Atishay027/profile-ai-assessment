from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import NotFoundError
from app.models import Profile
from app.schemas import InsightResult
from app.services.gemini import generate_insight

router = APIRouter(prefix="/profiles", tags=["insight"])


@router.post("/{user_id}/insight", response_model=InsightResult)
def create_insight(user_id: str, db: Session = Depends(get_db)):
    profile = db.get(Profile, user_id)
    if profile is None:
        raise NotFoundError(f"Profile '{user_id}' not found.")
    return generate_insight(profile)
