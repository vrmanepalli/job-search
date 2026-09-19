from pydantic import BaseModel, Field


class ApplicationAnswer(BaseModel):
    question: str

    normalized_key: str | None = None

    answer: str | None = None

    source: str | None = None

    verified: bool = False

    requires_user_input: bool = False

    confidence: int = Field(
        default=0,
        ge=0,
        le=100,
    )


class PreparedApplication(BaseModel):
    job_id: str

    company: str

    title: str

    job_url: str | None = None

    application_url: str | None = None

    resume_path: str | None = None

    cover_letter: str | None = None

    answers: list[
        ApplicationAnswer
    ] = Field(
        default_factory=list
    )

    missing_answers: list[str] = Field(
        default_factory=list
    )

    ready_for_review: bool = False

class ExtractedApplicationAnswer(BaseModel):
    supported: bool

    answer: str | None = None

    evidence: str | None = None

    confidence: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    reason: str | None = None