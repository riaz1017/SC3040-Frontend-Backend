from fastapi import HTTPException
from sqlalchemy.orm import Session as DbSession

from app.models import Account, Session
from app.services.session_helpers import session_out


class SessionService:
    def list_for(self, db: DbSession, account: Account, as_tutor: bool) -> list[Session]:
        if as_tutor:
            if not account.tutor_role:
                raise HTTPException(status_code=403, detail="Peer Tutor role required")
            q = db.query(Session).filter(Session.tutor_id == account.id)
        else:
            q = db.query(Session).filter(Session.student_id == account.id)
        return q.order_by(Session.created_at.desc()).all()

    def get_party(self, db: DbSession, account: Account, session_id: int) -> Session:
        session = db.get(Session, session_id)
        if not session or (account.id not in (session.student_id, session.tutor_id) and not account.is_admin):
            raise HTTPException(status_code=404, detail="Session not found")
        return session

    def tutor_respond(self, db: DbSession, tutor: Account, session_id: int, action: str) -> Session:
        session = db.get(Session, session_id)
        if not session or session.tutor_id != tutor.id:
            raise HTTPException(status_code=404, detail="Request not found")
        if session.status != "requested":
            raise HTTPException(status_code=400, detail="This request is no longer pending")
        session.status = "accepted" if action == "accept" else "declined"
        db.commit()
        db.refresh(session)
        return session

    def schedule(self, db: DbSession, account: Account, session_id: int, slot: str) -> Session:
        session = self.get_party(db, account, session_id)
        if session.status != "accepted":
            raise HTTPException(status_code=400, detail="Both parties must accept before coordinating a time")
        session.scheduled_slot = slot
        session.status = "scheduled"
        db.commit()
        db.refresh(session)
        return session

    def serialize(self, session: Session, viewer: Account) -> dict:
        return session_out(session, viewer.id, hide_other_report=not viewer.is_admin)
