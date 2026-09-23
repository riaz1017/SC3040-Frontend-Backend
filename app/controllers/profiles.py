from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_tutor
from app.models import Account
from app.schemas import ProfileIn, ProfileOut
from app.services.profile_service import TutorProfileService

router = APIRouter(prefix="/tutor-profile", tags=["Tutor profile"])
profiles = TutorProfileService()


@router.get("", response_model=ProfileOut)
def get_profile(account: Account = Depends(require_tutor), db: Session = Depends(get_db)):
    return ProfileOut(**profiles.to_out(db, profiles.get(db, account)))


@router.put("", response_model=ProfileOut)
def update_profile(body: ProfileIn, account: Account = Depends(require_tutor), db: Session = Depends(get_db)):
    return ProfileOut(**profiles.to_out(db, profiles.update(db, account, body)))
