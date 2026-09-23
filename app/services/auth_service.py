from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Account
from app.security import create_access_token, hash_password, verify_password

NTU_SUFFIXES = ("@e.ntu.edu.sg", "@ntu.edu.sg")


def _ntu_email(email: str) -> bool:
    lowered = email.lower()
    return any(lowered.endswith(suffix) for suffix in NTU_SUFFIXES)


def public_account(account: Account) -> dict:
    if account.is_admin:
        role = "admin"
    elif account.tutor_role:
        role = "peer_tutor"
    else:
        role = "student"
    return {
        "id": account.id,
        "name": account.name,
        "email": account.email,
        "tutor_role": account.tutor_role,
        "is_admin": account.is_admin,
        "role": role,
    }


class AuthService:
    def register(self, db: Session, name: str, email: str, password: str) -> Account:
        email = email.lower().strip()
        if not _ntu_email(email):
            raise HTTPException(status_code=400, detail="A valid NTU email is required")
        if db.query(Account).filter(Account.email == email).first():
            raise HTTPException(status_code=400, detail="An account with that email already exists")
        account = Account(
            name=name.strip(),
            email=email,
            password_hash=hash_password(password),
            tutor_role=False,
            is_admin=False,
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    def login(self, db: Session, email: str, password: str) -> tuple[str, Account]:
        account = db.query(Account).filter(Account.email == email.lower().strip()).first()
        if not account or not verify_password(password, account.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong email or password")
        return create_access_token(str(account.id)), account
