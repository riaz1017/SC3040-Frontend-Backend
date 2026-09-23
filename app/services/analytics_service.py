from sqlalchemy import func
from sqlalchemy.orm import Session as DbSession

from app.models import Match, Rating, Session, TutorProfile

COMPLETED = ("completed", "resolved_completed")
COUNTED = COMPLETED + (
    "resolved_no_show_student",
    "resolved_no_show_tutor",
    "resolved_unresolved",
    "disputed",
)


class AnalyticsService:
    def dashboard(self, db: DbSession) -> dict:
        decided = db.query(Match).filter(Match.status.in_(("accepted", "rejected"))).count()
        accepted = db.query(Match).filter(Match.status == "accepted").count()
        acceptance = round((accepted / decided) * 100) if decided else 0

        completed = db.query(Session).filter(Session.status.in_(COMPLETED)).count()
        counted = db.query(Session).filter(Session.status.in_(COUNTED)).count()
        completion = round((completed / counted) * 100) if counted else 0

        avg = db.query(func.avg(Rating.score)).scalar()
        disputed = db.query(Session).filter(Session.status == "disputed").count()

        tutors = db.query(TutorProfile).all()
        performance = []
        flagged = []
        for profile in tutors:
            against = (
                db.query(Session)
                .filter(Session.tutor_id == profile.account_id, Session.status == "resolved_no_show_tutor")
                .count()
            )
            row = {
                "tutor_id": profile.account_id,
                "name": profile.account.name,
                "rating": profile.rating,
                "sessions_done": profile.sessions_done,
            }
            performance.append(row)
            if profile.rating and profile.rating < 4.3 or against:
                flagged.append({**row, "reason": "Dispute against tutor" if against else "Low rating"})

        return {
            "match_acceptance_rate": acceptance,
            "session_completion_rate": completion,
            "average_satisfaction": round(float(avg), 1) if avg is not None else None,
            "disputed_sessions": disputed,
            "tutor_performance": performance,
            "flagged_tutors": flagged,
        }
