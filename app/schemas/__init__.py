from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class AccountOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    tutor_role: bool
    is_admin: bool
    role: str

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    account: AccountOut


class QueryIn(BaseModel):
    module: str = Field(min_length=1)
    text: str = Field(min_length=1)
    urgency: str = "Same day"


class QueryOut(BaseModel):
    id: int
    module: str
    text: str
    urgency: str
    analysis_topic: str | None
    analysis_concepts: list | None
    analysis_difficulty: str | None
    analysis_confidence: float | None
    fallback_mode: bool

    model_config = {"from_attributes": True}


class MatchOut(BaseModel):
    id: int
    tutor_id: int
    tutor_name: str
    modules: list
    grade_band: str
    rating: float
    sessions_done: int
    at_capacity: bool
    score: int
    reasons: list
    status: str
    fallback_mode: bool


class MatchRespondIn(BaseModel):
    action: str = Field(pattern="^(accept|reject)$")


class ProfileIn(BaseModel):
    modules: list[str] | None = None
    grade_band: str | None = None
    available: bool | None = None
    bio: str | None = None
    max_students: int | None = Field(default=None, ge=1, le=20)


class ProfileOut(BaseModel):
    account_id: int
    name: str
    modules: list
    grade_band: str
    available: bool
    bio: str
    max_students: int
    current_students: int
    rating: float
    sessions_done: int


class ApplicationIn(BaseModel):
    module: str = Field(min_length=1)


class ApplicationOut(BaseModel):
    id: int
    account_id: int
    applicant_name: str
    module: str
    evidence_filename: str
    status: str
    reason: str | None

    model_config = {"from_attributes": True}


class ReviewIn(BaseModel):
    decision: str = Field(pattern="^(approved|rejected)$")
    reason: str | None = None


class SessionRespondIn(BaseModel):
    action: str = Field(pattern="^(accept|decline)$")
    reason: str | None = None


class ScheduleIn(BaseModel):
    slot: str = Field(min_length=1)


class ConfirmIn(BaseModel):
    outcome: str = Field(pattern="^(completed|no_show)$")


class RatingIn(BaseModel):
    score: int = Field(ge=1, le=5)
    comment: str | None = None


class ResolveIn(BaseModel):
    status: str = Field(
        pattern="^(resolved_completed|resolved_no_show_student|resolved_no_show_tutor|resolved_unresolved)$"
    )
    note: str | None = None


class SessionOut(BaseModel):
    id: int
    student_id: int
    student_name: str
    tutor_id: int
    tutor_name: str
    module: str
    scheduled_slot: str | None
    status: str
    admin_note: str | None
    my_report: str | None
    other_report: str | None
    my_rating: int | None
