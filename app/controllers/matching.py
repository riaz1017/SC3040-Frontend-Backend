from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_account, require_tutor
from app.models import Account
from app.schemas import MatchOut, MatchRespondIn, SessionRespondIn
from app.services.matching_service import MatchingService
from app.services.query_service import QueryService
from app.services.session_helpers import session_out
from app.services.session_service import SessionService

router = APIRouter(tags=["Matching"])
matching = MatchingService()
queries = QueryService()
sessions = SessionService()


@router.post("/queries/{query_id}/matches", response_model=list[MatchOut])
def find_tutors(query_id: int, account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    query = queries.get_owned(db, account, query_id)
    ranked = matching.rank(db, query)
    return [MatchOut(**matching.to_out(db, m, query)) for m in ranked]


@router.post("/matches/{match_id}/respond")
def respond_to_match(
    match_id: int,
    body: MatchRespondIn,
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_db),
):
    match = matching.respond(db, account, match_id, body.action)
    return matching.to_out(db, match, match.query)


@router.post("/sessions/{session_id}/respond")
def respond_to_request(
    session_id: int,
    body: SessionRespondIn,
    account: Account = Depends(require_tutor),
    db: Session = Depends(get_db),
):
    session = sessions.tutor_respond(db, account, session_id, body.action)
    return session_out(session, account.id)
