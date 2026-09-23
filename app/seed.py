from sqlalchemy.orm import Session

from app.models import Account, CompletionReport, Session as TutoringSession, TutorApplication, TutorProfile
from app.security import hash_password

SEED_PASSWORD = "password123"
ADMIN_PASSWORD = "admin123"

TUTORS = [
    {
        "name": "Aisyah Rahman",
        "email": "shammas@e.ntu.edu.sg",
        "modules": ["SC2001 Algorithms", "SC2006 Software Engineering"],
        "grade_band": "A",
        "rating": 4.8,
        "sessions_done": 12,
        "max_students": 3,
        "available": True,
        "bio": "Happy to help with algorithms and OOP.",
    },
    {
        "name": "Wei Jie Tan",
        "email": "weijie@e.ntu.edu.sg",
        "modules": ["SC2001 Algorithms"],
        "grade_band": "A",
        "rating": 4.9,
        "sessions_done": 20,
        "max_students": 3,
        "available": True,
        "bio": "Usually at cap during exam weeks.",
    },
    {
        "name": "Kavya Nair",
        "email": "kavya@e.ntu.edu.sg",
        "modules": ["SC1015 Intro to Data Science", "SC2001 Algorithms"],
        "grade_band": "A-",
        "rating": 4.6,
        "sessions_done": 8,
        "max_students": 4,
        "available": True,
        "bio": "Data science and algorithms.",
    },
    {
        "name": "Marcus Lee",
        "email": "marcus@e.ntu.edu.sg",
        "modules": ["SC2006 Software Engineering"],
        "grade_band": "A",
        "rating": 4.1,
        "sessions_done": 15,
        "max_students": 2,
        "available": False,
        "bio": "Currently unavailable.",
    },
]


EMAIL_ALIASES = {
    "devi.prakash@e.ntu.edu.sg": "riaz@e.ntu.edu.sg",
    "aisyah@e.ntu.edu.sg": "shammas@e.ntu.edu.sg",
}


def ensure_demo_emails(db: Session) -> None:
    changed = False
    for old, new in EMAIL_ALIASES.items():
        account = db.query(Account).filter(Account.email == old).first()
        if account:
            account.email = new
            account.password_hash = hash_password(SEED_PASSWORD)
            changed = True
    if changed:
        db.commit()


def seed_if_empty(db: Session) -> None:
    if db.query(Account).first():
        ensure_demo_emails(db)
        return

    student = Account(
        name="Devi Prakash",
        email="riaz@e.ntu.edu.sg",
        password_hash=hash_password(SEED_PASSWORD),
    )
    admin = Account(
        name="PeerUp Admin",
        email="admin@e.ntu.edu.sg",
        password_hash=hash_password(ADMIN_PASSWORD),
        is_admin=True,
    )
    priya = Account(
        name="Priya Sundaram",
        email="priya@e.ntu.edu.sg",
        password_hash=hash_password(SEED_PASSWORD),
    )
    ryan = Account(
        name="Ryan Koh",
        email="ryan@e.ntu.edu.sg",
        password_hash=hash_password(SEED_PASSWORD),
    )
    db.add_all([student, admin, priya, ryan])

    tutors = {}
    for row in TUTORS:
        account = Account(
            name=row["name"],
            email=row["email"],
            password_hash=hash_password(SEED_PASSWORD),
            tutor_role=True,
        )
        db.add(account)
        db.flush()
        db.add(
            TutorProfile(
                account_id=account.id,
                modules=row["modules"],
                grade_band=row["grade_band"],
                available=row["available"],
                bio=row["bio"],
                max_students=row["max_students"],
                rating=row["rating"],
                sessions_done=row["sessions_done"],
            )
        )
        tutors[row["name"]] = account

    db.flush()
    db.add(
        TutorApplication(
            account_id=ryan.id,
            module="SC1003 Intro to Computational Thinking",
            evidence_filename="transcript_AY25.pdf",
            status="pending",
        )
    )

    marcus = tutors["Marcus Lee"]
    disputed = TutoringSession(
        student_id=priya.id,
        tutor_id=marcus.id,
        module="SC2006 Software Engineering",
        scheduled_slot="Mon, 3:00 PM",
        status="disputed",
        admin_note="Student says Marcus never joined the call.",
    )
    db.add(disputed)
    db.flush()
    db.add_all(
        [
            CompletionReport(session_id=disputed.id, reporter_id=priya.id, outcome="completed"),
            CompletionReport(session_id=disputed.id, reporter_id=marcus.id, outcome="no_show"),
        ]
    )

    weijie = tutors["Wei Jie Tan"]
    for i in range(3):
        extra = Account(
            name=f"Cap Student {i+1}",
            email=f"cap{i+1}@e.ntu.edu.sg",
            password_hash=hash_password(SEED_PASSWORD),
        )
        db.add(extra)
        db.flush()
        db.add(
            TutoringSession(
                student_id=extra.id,
                tutor_id=weijie.id,
                module="SC2001 Algorithms",
                status="scheduled",
                scheduled_slot="Placeholder slot",
            )
        )

    db.commit()
