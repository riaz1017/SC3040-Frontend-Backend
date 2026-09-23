from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_account, require_admin
from app.models import Account
from app.schemas import ApplicationOut, ReviewIn
from app.services.application_service import ApplicationService

router = APIRouter(tags=["Applications"])
applications = ApplicationService()
UPLOAD = Path(settings.upload_dir)
UPLOAD.mkdir(exist_ok=True)


@router.post("/applications", response_model=ApplicationOut)
async def apply(
    module: str = Form(...),
    evidence: UploadFile = File(...),
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_db),
):
    if not evidence.filename:
        raise HTTPException(status_code=400, detail="Evidence file is required")
    dest = UPLOAD / f"{account.id}_{evidence.filename}"
    dest.write_bytes(await evidence.read())
    app_row = applications.apply(db, account, module, dest.name)
    return ApplicationOut(**applications.to_out(app_row))


@router.get("/applications/me", response_model=list[ApplicationOut])
def my_applications(account: Account = Depends(get_current_account), db: Session = Depends(get_db)):
    return [ApplicationOut(**applications.to_out(a)) for a in applications.mine(db, account)]


@router.get("/admin/applications", response_model=list[ApplicationOut])
def pending(account: Account = Depends(require_admin), db: Session = Depends(get_db)):
    return [ApplicationOut(**applications.to_out(a)) for a in applications.pending(db)]


@router.post("/admin/applications/{application_id}/review", response_model=ApplicationOut)
def review(
    application_id: int,
    body: ReviewIn,
    account: Account = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return ApplicationOut(**applications.to_out(applications.review(db, application_id, body.decision, body.reason)))
