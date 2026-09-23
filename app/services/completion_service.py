from fastapi import HTTPException
from sqlalchemy.orm import Session as DbSession

from app.models import Account, CompletionReport, Session
from app.services.session_helpers import RATEABLE


class CompletionDisputeService:
    def confirm(self, db: DbSession, account: Account, session_id: int, outcome: str) -> Session:
        session = db.get(Session, session_id)
        if not session or account.id not in (session.student_id, session.tutor_id):
            raise HTTPException(status_code=404, detail="Session not found")
        if session.status not in ("scheduled", "awaiting"):
            raise HTTPException(status_code=400, detail="This session is not waiting for confirmation")
        if any(r.reporter_id == account.id for r in session.reports):
            raise HTTPException(status_code=400, detail="You have already submitted a report")

        db.add(CompletionReport(session_id=session.id, reporter_id=account.id, outcome=outcome))
        session.status = "awaiting"
        db.flush()
        db.refresh(session)

        reports = {r.reporter_id: r.outcome for r in session.reports}
        if session.student_id in reports and session.tutor_id in reports:
            student_rep = reports[session.student_id]
            tutor_rep = reports[session.tutor_id]
            if student_rep == "completed" and tutor_rep == "completed":
                session.status = "completed"
            else:
                session.status = "disputed"
                session.admin_note = (
                    f'Student reported "{student_rep}", tutor reported "{tutor_rep}".'
                )
        db.commit()
        db.refresh(session)
        return session

    def rate(self, db: DbSession, account: Account, session_id: int, score: int, comment: str | None):
        from app.models import Rating

        session = db.get(Session, session_id)
        if not session or account.id not in (session.student_id, session.tutor_id):
            raise HTTPException(status_code=404, detail="Session not found")
        if session.status not in RATEABLE:
            raise HTTPException(status_code=400, detail="Rating is only allowed after a completed session")
        if any(r.rater_id == account.id for r in session.ratings):
            raise HTTPException(status_code=400, detail="You have already rated this session")
        rating = Rating(session_id=session.id, rater_id=account.id, score=score, comment=comment)
        db.add(rating)
        db.commit()
        return rating

    def disputes(self, db: DbSession) -> list[Session]:
        return db.query(Session).filter(Session.status == "disputed").all()

    def resolve(self, db: DbSession, session_id: int, status: str, note: str | None) -> Session:
        session = db.get(Session, session_id)
        if not session or session.status != "disputed":
            raise HTTPException(status_code=404, detail="Disputed session not found")
        session.status = status
        session.admin_note = note
        db.commit()
        db.refresh(session)
        return session
