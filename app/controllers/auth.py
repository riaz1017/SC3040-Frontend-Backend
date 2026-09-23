from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_account
from app.models import Account
from app.schemas import AccountOut, LoginIn, RegisterIn, TokenOut
from app.services.auth_service import AuthService, public_account

router = APIRouter(prefix="/auth", tags=["Auth"])
auth = AuthService()


@router.post("/register", response_model=TokenOut)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    account = auth.register(db, body.name, body.email, body.password)
    token = auth.login(db, body.email, body.password)[0]
    return TokenOut(access_token=token, account=AccountOut(**public_account(account)))


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    token, account = auth.login(db, body.email, body.password)
    return TokenOut(access_token=token, account=AccountOut(**public_account(account)))


@router.get("/me", response_model=AccountOut)
def me(account: Account = Depends(get_current_account)):
    return AccountOut(**public_account(account))
