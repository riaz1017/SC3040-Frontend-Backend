from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Account, TutorApplication, TutorProfile


class ApplicationService:
    def apply(self, db: Session, student: Account, module: str, filename: str) -> TutorApplication:
        if student.tutor_role:
            raise HTTPException(status_code=400, detail="This account already has the Peer Tutor role")
        pending = (
            db.query(TutorApplication)
            .filter(TutorApplication.account_id == student.id, TutorApplication.status == "pending")
            .first()
        )
        if pending:
            raise HTTPException(status_code=400, detail="An application is already pending for this account")
        if not filename:
            raise HTTPException(status_code=400, detail="Evidence is required for each claimed module")

        application = TutorApplication(
            account_id=student.id,
            module=module.strip(),
            evidence_filename=filename,
            status="pending",
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        return application

    def mine(self, db: Session, student: Account) -> list[TutorApplication]:
        return (
            db.query(TutorApplication)
            .filter(TutorApplication.account_id == student.id)
            .order_by(TutorApplication.created_at.desc())
            .all()
        )

    def pending(self, db: Session) -> list[TutorApplication]:
        return db.query(TutorApplication).filter(TutorApplication.status == "pending").all()

    def review(self, db: Session, application_id: int, decision: str, reason: str | None) -> TutorApplication:
        application = db.get(TutorApplication, application_id)
        if not application or application.status != "pending":
            raise HTTPException(status_code=404, detail="Pending application not found")
        application.status = decision
        application.reason = reason
        application.reviewed_at = datetime.utcnow()
        if decision == "approved":
            application.account.tutor_role = True
            if not application.account.tutor_profile:
                db.add(
                    TutorProfile(
                        account_id=application.account_id,
                        modules=[application.module],
                        available=False,
                    )
                )
        db.commit()
        db.refresh(application)
        return application

    def to_out(self, application: TutorApplication) -> dict:
        return {
            "id": application.id,
            "account_id": application.account_id,
            "applicant_name": application.account.name,
            "module": application.module,
            "evidence_filename": application.evidence_filename,
            "status": application.status,
            "reason": application.reason,
        }
