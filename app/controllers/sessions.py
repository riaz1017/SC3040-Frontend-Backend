from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DbSession

from app.database import get_db
from app.deps import get_current_account
from app.models import Account
from app.schemas import ConfirmIn, RatingIn, ScheduleIn, SessionOut
from app.services.completion_service import CompletionDisputeService
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["Sessions"])
sessions = SessionService()
completion = CompletionDisputeService()


@router.get("", response_model=list[SessionOut])
def list_sessions(
    as_tutor: bool = Query(False),
    account: Account = Depends(get_current_account),
    db: DbSession = Depends(get_db),
):
    return [SessionOut(**sessions.serialize(s, account)) for s in sessions.list_for(db, account, as_tutor)]


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: int, account: Account = Depends(get_current_account), db: DbSession = Depends(get_db)):
    session = sessions.get_party(db, account, session_id)
    return SessionOut(**sessions.serialize(session, account))


@router.post("/{session_id}/schedule", response_model=SessionOut)
def schedule(
    session_id: int,
    body: ScheduleIn,
    account: Account = Depends(get_current_account),
    db: DbSession = Depends(get_db),
):
    session = sessions.schedule(db, account, session_id, body.slot)
    return SessionOut(**sessions.serialize(session, account))


@router.post("/{session_id}/confirm", response_model=SessionOut)
def confirm(
    session_id: int,
    body: ConfirmIn,
    account: Account = Depends(get_current_account),
    db: DbSession = Depends(get_db),
):
    session = completion.confirm(db, account, session_id, body.outcome)
    return SessionOut(**sessions.serialize(session, account))


@router.post("/{session_id}/rating")
def rate(
    session_id: int,
    body: RatingIn,
    account: Account = Depends(get_current_account),
    db: DbSession = Depends(get_db),
):
    rating = completion.rate(db, account, session_id, body.score, body.comment)
    return {"id": rating.id, "score": rating.score, "comment": rating.comment}
