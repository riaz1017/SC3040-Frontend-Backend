from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    tutor_role: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tutor_profile: Mapped["TutorProfile | None"] = relationship(back_populates="account", uselist=False)
    applications: Mapped[list["TutorApplication"]] = relationship(back_populates="account")
    queries: Mapped[list["AcademicQuery"]] = relationship(back_populates="student")


class TutorApplication(Base):
    __tablename__ = "tutor_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    module: Mapped[str] = mapped_column(String(160))
    evidence_filename: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    account: Mapped[Account] = relationship(back_populates="applications")


class TutorProfile(Base):
    __tablename__ = "tutor_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), unique=True)
    modules: Mapped[list] = mapped_column(JSON, default=list)
    grade_band: Mapped[str] = mapped_column(String(10), default="A-")
    available: Mapped[bool] = mapped_column(Boolean, default=True)
    bio: Mapped[str] = mapped_column(Text, default="")
    max_students: Mapped[int] = mapped_column(Integer, default=3)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    sessions_done: Mapped[int] = mapped_column(Integer, default=0)

    account: Mapped[Account] = relationship(back_populates="tutor_profile")


class AcademicQuery(Base):
    __tablename__ = "academic_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    module: Mapped[str] = mapped_column(String(160))
    urgency: Mapped[str] = mapped_column(String(40), default="Same day")
    text: Mapped[str] = mapped_column(Text)
    analysis_topic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    analysis_concepts: Mapped[list | None] = mapped_column(JSON, nullable=True)
    analysis_difficulty: Mapped[str | None] = mapped_column(String(40), nullable=True)
    analysis_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    fallback_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student: Mapped[Account] = relationship(back_populates="queries")
    matches: Mapped[list["Match"]] = relationship(back_populates="query")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    query_id: Mapped[int] = mapped_column(ForeignKey("academic_queries.id"))
    tutor_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    score: Mapped[int] = mapped_column(Integer)
    reasons: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="offered")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    query: Mapped[AcademicQuery] = relationship(back_populates="matches")
    tutor: Mapped[Account] = relationship()


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    tutor_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    query_id: Mapped[int | None] = mapped_column(ForeignKey("academic_queries.id"), nullable=True)
    match_id: Mapped[int | None] = mapped_column(ForeignKey("matches.id"), nullable=True)
    module: Mapped[str] = mapped_column(String(160))
    scheduled_slot: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="requested")
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reports: Mapped[list["CompletionReport"]] = relationship(back_populates="session")
    ratings: Mapped[list["Rating"]] = relationship(back_populates="session")
    student: Mapped[Account] = relationship(foreign_keys=[student_id])
    tutor: Mapped[Account] = relationship(foreign_keys=[tutor_id])


class CompletionReport(Base):
    __tablename__ = "completion_reports"
    __table_args__ = (UniqueConstraint("session_id", "reporter_id", name="uq_report_per_party"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    reporter_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    outcome: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[Session] = relationship(back_populates="reports")


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (UniqueConstraint("session_id", "rater_id", name="uq_rating_per_party"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    rater_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    score: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[Session] = relationship(back_populates="ratings")
