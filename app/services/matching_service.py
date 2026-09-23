from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import AcademicQuery, Account, Match, Session as TutoringSession, TutorProfile
from app.services.query_analysis_service import QueryAnalysisService
from app.services.session_helpers import tutor_load

analysis = QueryAnalysisService()


class MatchingService:
    def rank(self, db: Session, query: AcademicQuery) -> list[Match]:
        analysis.analyse(query)
        db.query(Match).filter(Match.query_id == query.id, Match.status == "offered").delete()

        profiles = (
            db.query(TutorProfile)
            .join(Account)
            .filter(Account.tutor_role.is_(True), Account.id != query.student_id)
            .all()
        )
        created: list[Match] = []
        for profile in profiles:
            if query.module not in (profile.modules or []):
                continue
            if not profile.available:
                continue
            load = tutor_load(db, profile.account_id)
            at_cap = load >= profile.max_students
            score = 60
            if profile.grade_band == "A":
                score += 15
            elif profile.grade_band == "A-":
                score += 10
            else:
                score += 5
            score += min(int(profile.rating * 4), 20)
            if at_cap:
                score -= 100
            score = max(score, 5)

            if query.fallback_mode:
                reasons = ["Teaches this module", "At capacity" if at_cap else "Marked available"]
            else:
                code = query.module.split(" ")[0]
                reasons = [
                    f"{profile.grade_band} in {code}",
                    f"{profile.rating:.1f}★ over {profile.sessions_done} sessions",
                    "At capacity" if at_cap else "Free right now",
                ]

            match = Match(
                query_id=query.id,
                tutor_id=profile.account_id,
                score=score,
                reasons=reasons,
                status="offered",
            )
            db.add(match)
            created.append(match)

        db.commit()
        for match in created:
            db.refresh(match)
        created.sort(key=lambda m: m.score, reverse=True)
        return created

    def respond(self, db: Session, student: Account, match_id: int, action: str) -> Match:
        match = db.get(Match, match_id)
        if not match or match.query.student_id != student.id:
            raise HTTPException(status_code=404, detail="Match not found")
        if match.status != "offered":
            raise HTTPException(status_code=400, detail="This match has already been answered")

        if action == "reject":
            match.status = "rejected"
            db.commit()
            return match

        profile = db.query(TutorProfile).filter(TutorProfile.account_id == match.tutor_id).first()
        if not profile:
            raise HTTPException(status_code=400, detail="Tutor profile is missing")
        if tutor_load(db, match.tutor_id) >= profile.max_students:
            raise HTTPException(status_code=400, detail="This Peer Tutor is at their student cap")

        match.status = "accepted"
        session = TutoringSession(
            student_id=student.id,
            tutor_id=match.tutor_id,
            query_id=match.query_id,
            match_id=match.id,
            module=match.query.module,
            status="requested",
        )
        db.add(session)
        db.commit()
        db.refresh(match)
        return match

    def to_out(self, db: Session, match: Match, query: AcademicQuery) -> dict:
        profile = db.query(TutorProfile).filter(TutorProfile.account_id == match.tutor_id).first()
        load = tutor_load(db, match.tutor_id)
        return {
            "id": match.id,
            "tutor_id": match.tutor_id,
            "tutor_name": match.tutor.name,
            "modules": profile.modules if profile else [],
            "grade_band": profile.grade_band if profile else "",
            "rating": profile.rating if profile else 0,
            "sessions_done": profile.sessions_done if profile else 0,
            "at_capacity": bool(profile and load >= profile.max_students),
            "score": match.score,
            "reasons": match.reasons,
            "status": match.status,
            "fallback_mode": query.fallback_mode,
        }
