from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import AcademicQuery, Account


class QueryService:
    def create(self, db: Session, student: Account, module: str, text: str, urgency: str) -> AcademicQuery:
        if not module.strip() or not text.strip():
            raise HTTPException(status_code=400, detail="Module and query text are required")
        query = AcademicQuery(
            student_id=student.id,
            module=module.strip(),
            text=text.strip(),
            urgency=urgency.strip() or "Same day",
        )
        db.add(query)
        db.commit()
        db.refresh(query)
        return query

    def get_owned(self, db: Session, student: Account, query_id: int) -> AcademicQuery:
        query = db.get(AcademicQuery, query_id)
        if not query or query.student_id != student.id:
            raise HTTPException(status_code=404, detail="Query not found")
        return query
