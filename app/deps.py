from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account
from app.security import decode_access_token

bearer = HTTPBearer(auto_error=False)


def get_current_account(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Account:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    subject = decode_access_token(creds.credentials)
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    account = db.get(Account, int(subject))
    if not account:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not found")
    return account


def require_tutor(account: Account = Depends(get_current_account)) -> Account:
    if not account.tutor_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Peer Tutor role required")
    return account


def require_admin(account: Account = Depends(get_current_account)) -> Account:
    if not account.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return account
