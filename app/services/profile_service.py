from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Account, TutorProfile
from app.services.session_helpers import tutor_load


class TutorProfileService:
    def get(self, db: Session, tutor: Account) -> TutorProfile:
        profile = db.query(TutorProfile).filter(TutorProfile.account_id == tutor.id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Tutor profile is not enabled yet")
        return profile

    def update(self, db: Session, tutor: Account, data) -> TutorProfile:
        profile = self.get(db, tutor)
        if data.modules is not None:
            profile.modules = data.modules
        if data.grade_band is not None:
            profile.grade_band = data.grade_band
        if data.available is not None:
            profile.available = data.available
        if data.bio is not None:
            profile.bio = data.bio
        if data.max_students is not None:
            profile.max_students = data.max_students
        db.commit()
        db.refresh(profile)
        return profile

    def to_out(self, db: Session, profile: TutorProfile) -> dict:
        return {
            "account_id": profile.account_id,
            "name": profile.account.name,
            "modules": profile.modules or [],
            "grade_band": profile.grade_band,
            "available": profile.available,
            "bio": profile.bio,
            "max_students": profile.max_students,
            "current_students": tutor_load(db, profile.account_id),
            "rating": profile.rating,
            "sessions_done": profile.sessions_done,
        }
