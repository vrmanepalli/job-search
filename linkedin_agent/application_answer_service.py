from linkedin_agent.application_models import PreparedApplication

NEVER_INFER_KEYS = {
    "requires_sponsorship",
    "work_authorization",
    "citizenship",
    "security_clearance",
    "salary_expectation",
    "willing_to_relocate",
    "disability_status",
    "veteran_status",
    "gender",
    "race_ethnicity",
}

def answer_requires_verification(
    normalized_key: str | None,
) -> bool:

    if not normalized_key:
        return False

    return normalized_key in NEVER_INFER_KEYS

def build_verified_answer_map(
    prepared_application: PreparedApplication,
) -> dict[str, str]:
    """
    Build answers that are safe to autofill.

    Only verified answers are included.
    Unknown/unverified answers are excluded.
    """

    answers: dict[str, str] = {}

    for item in prepared_application.answers:

        # No answer available
        if item.answer is None:
            continue

        # User input explicitly required
        if item.requires_user_input:
            continue

        # Never autofill unverified answers
        if not item.verified:
            continue

        answer = str(item.answer).strip()

        if not answer:
            continue

        # Prefer normalized key
        if item.normalized_key:
            answers[item.normalized_key] = answer

        # Also support original question text
        if item.question:
            answers[item.question] = answer

    return answers