from linkedin_agent.application_models import (
    ApplicationAnswer,
    PreparedApplication,
)

from linkedin_agent.application_profile_repository import (
    get_verified_answer,
)

from linkedin_agent.resume_answer_extractor import (
    can_answer_from_resume,
    extract_answer_from_resume,
)

from linkedin_agent.application_question_normalizer import (
    normalize_question,
)

from linkedin_agent.resume_service import (
    optimize_resume_for_job_service,
)

from linkedin_agent.job_eligibility_service import (
    check_job_eligibility,
)

from linkedin_agent.application_repository import get_application

class ApplicationPreparationError(
    RuntimeError
):
    pass

def prepare_application(
    job: dict,
    master_resume: dict,
    questions: list[str] | None = None,
) -> PreparedApplication:

    if questions is None:
        questions = []

   # -------------------------------------------------
    # 1. Validate the job passed into this function
    # -------------------------------------------------

    if not job:
        raise ValueError("Job data is required")

    job_id = (
        job.get("job_id")
        or job.get("external_job_id")
    )

    if not job_id:
        raise ValueError(
            "Job is missing job_id/external_job_id"
        )

    application_record = get_application(job_id)

    application_url = (
        application_record.get("application_url")
        if application_record
        else None
    )

    # -------------------------------------------------
    # 2. Eligibility check BEFORE resume optimization
    # -------------------------------------------------

    eligibility = check_job_eligibility(job)

    if not eligibility["eligible"]:
        raise ValueError(
            f"Job failed eligibility check: "
            f"{eligibility['reason']} "
            f"Matched: {eligibility['matched_text']}"
        )

    if eligibility["requires_review"]:
        raise ValueError(
            f"Job requires eligibility review before resume optimization: "
            f"{eligibility['reason']} "
            f"Matched: {eligibility['matched_text']}"
        )

    # Only optimize after eligibility passes.
    optimization = optimize_resume_for_job_service(
        job_id=job["job_id"]
    )

    if not optimization.get("success"):
        raise ApplicationPreparationError(
            optimization.get(
                "error",
                "Resume optimization failed",
            )
        )

    # 2. Get generated resume path
    resume_path = optimization.get(
        "resume_path"
    )

    answers = []

    missing_answers = []

    # 3. Prepare application answers

    for question in questions:

        answer = answer_application_question(
            question=question,
            master_resume=master_resume,
        )

        answers.append(answer)

        if answer.requires_user_input:
            missing_answers.append(question)

    # 4. Return prepared application
    return PreparedApplication(
        job_id=job["job_id"],
        company=job["company"],
        title=job["title"],
        job_url=job.get("job_url"),
        application_url=application_url,
        answers=answers,
        missing_answers=missing_answers,
        ready_for_review=len(missing_answers) == 0,
        resume_path=resume_path,
    )



def answer_application_question(
    question: str,
    master_resume: dict,
) -> ApplicationAnswer:

    key = normalize_question(question)

    # --------------------------------------------------
    # 1. VERIFIED DATABASE ANSWER
    # --------------------------------------------------

    if key:
        stored = get_verified_answer(key)

        if stored and stored["verified"]:
            return ApplicationAnswer(
                question=question,
                normalized_key=key,
                answer=stored["answer"],
                source="application_profile",
                verified=True,
                requires_user_input=False,
                confidence=100,
            )

    # --------------------------------------------------
    # 2. DO NOT USE RESUME FOR SENSITIVE QUESTIONS
    # --------------------------------------------------

    if not can_answer_from_resume(question):
        return ApplicationAnswer(
            question=question,
            normalized_key=key,
            answer=None,
            source=None,
            verified=False,
            requires_user_input=True,
            confidence=0,
        )

    # --------------------------------------------------
    # 3. TRY MASTER RESUME
    # --------------------------------------------------

    resume_text = master_resume.get("resume_text")

    if resume_text:

        extracted = extract_answer_from_resume(
            question=question,
            resume_text=resume_text,
        )

        if (
            extracted.supported
            and extracted.answer
            and extracted.evidence
            and extracted.confidence >= 90
        ):
            return ApplicationAnswer(
                question=question,
                normalized_key=key,
                answer=extracted.answer,
                source="master_resume",
                verified=False,
                requires_user_input=False,
                confidence=extracted.confidence,
            )

    # --------------------------------------------------
    # 4. FALL BACK TO USER
    # --------------------------------------------------

    return ApplicationAnswer(
        question=question,
        normalized_key=key,
        answer=None,
        source=None,
        verified=False,
        requires_user_input=True,
        confidence=0,
    )