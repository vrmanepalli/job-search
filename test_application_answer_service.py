from linkedin_agent.application_answer_service import (
    build_verified_answer_map,
)
from linkedin_agent.application_models import (
    ApplicationAnswer,
    PreparedApplication,
)


def test_verified_answer_is_included():

    prepared = PreparedApplication(
        job_id="123",
        company="Test",
        title="Director",
        answers=[
            ApplicationAnswer(
                question="Are you authorized to work in the US?",
                normalized_key="work_authorization",
                answer="Yes",
                source="user_confirmed",
                verified=True,
                requires_user_input=False,
                confidence=100,
            )
        ],
    )

    answers = build_verified_answer_map(prepared)

    assert answers["work_authorization"] == "Yes"


def test_unverified_answer_is_not_included():

    prepared = PreparedApplication(
        job_id="123",
        company="Test",
        title="Director",
        answers=[
            ApplicationAnswer(
                question="Desired salary?",
                normalized_key="salary_expectation",
                answer="$200,000",
                source="llm",
                verified=False,
                requires_user_input=False,
                confidence=95,
            )
        ],
    )

    answers = build_verified_answer_map(prepared)

    assert "salary_expectation" not in answers


def test_required_user_input_is_not_included():

    prepared = PreparedApplication(
        job_id="123",
        company="Test",
        title="Director",
        answers=[
            ApplicationAnswer(
                question="Will you require sponsorship?",
                normalized_key="requires_sponsorship",
                answer=None,
                source="unknown",
                verified=False,
                requires_user_input=True,
                confidence=0,
            )
        ],
    )

    answers = build_verified_answer_map(prepared)

    assert "requires_sponsorship" not in answers