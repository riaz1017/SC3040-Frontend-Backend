from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Account
from app.schemas import ResolveIn, SessionOut
from app.services.analytics_service import AnalyticsService
from app.services.completion_service import CompletionDisputeService
from app.services.session_helpers import session_out

router = APIRouter(prefix="/admin", tags=["Admin"])
completion = CompletionDisputeService()
analytics = AnalyticsService()


@router.get("/disputes", response_model=list[SessionOut])
def disputes(account: Account = Depends(require_admin), db: Session = Depends(get_db)):
    return [SessionOut(**session_out(s, account.id, hide_other_report=False)) for s in completion.disputes(db)]


@router.post("/disputes/{session_id}/resolve", response_model=SessionOut)
def resolve(
    session_id: int,
    body: ResolveIn,
    account: Account = Depends(require_admin),
    db: Session = Depends(get_db),
):
    session = completion.resolve(db, session_id, body.status, body.note)
    return SessionOut(**session_out(session, account.id, hide_other_report=False))


@router.get("/analytics")
def view_analytics(account: Account = Depends(require_admin), db: Session = Depends(get_db)):
    return analytics.dashboard(db)
