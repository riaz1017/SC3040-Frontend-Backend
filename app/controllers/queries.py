from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_account
from app.models import Account
from app.schemas import QueryIn, QueryOut
from app.services.query_service import QueryService

router = APIRouter(prefix="/queries", tags=["Queries"])
queries = QueryService()


@router.post("", response_model=QueryOut)
def create_query(body: QueryIn, account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    return queries.create(db, account, body.module, body.text, body.urgency)


@router.get("/{query_id}", response_model=QueryOut)
def get_query(query_id: int, account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    return queries.get_owned(db, account, query_id)
