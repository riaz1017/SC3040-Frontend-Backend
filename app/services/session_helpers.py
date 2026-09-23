from sqlalchemy.orm import Session as DbSession

from app.models import CompletionReport, Rating, Session

ACTIVE_LOAD = ("requested", "accepted", "scheduled", "awaiting")
RATEABLE = ("completed", "resolved_completed")


def tutor_load(db: DbSession, tutor_id: int) -> int:
    return (
        db.query(Session)
        .filter(Session.tutor_id == tutor_id, Session.status.in_(ACTIVE_LOAD))
        .count()
    )


def report_for(session: Session, account_id: int) -> CompletionReport | None:
    return next((r for r in session.reports if r.reporter_id == account_id), None)


def rating_for(session: Session, account_id: int) -> Rating | None:
    return next((r for r in session.ratings if r.rater_id == account_id), None)


def session_out(session: Session, viewer_id: int, hide_other_report: bool = True) -> dict:
    my_report = report_for(session, viewer_id)
    other = next((r for r in session.reports if r.reporter_id != viewer_id), None)
    show_other = (not hide_other_report) or session.status.startswith("resolved_") or session.status == "completed"
    my_rating = rating_for(session, viewer_id)
    return {
        "id": session.id,
        "student_id": session.student_id,
        "student_name": session.student.name,
        "tutor_id": session.tutor_id,
        "tutor_name": session.tutor.name,
        "module": session.module,
        "scheduled_slot": session.scheduled_slot,
        "status": session.status,
        "admin_note": session.admin_note,
        "my_report": my_report.outcome if my_report else None,
        "other_report": other.outcome if other and show_other else None,
        "my_rating": my_rating.score if my_rating else None,
    }
