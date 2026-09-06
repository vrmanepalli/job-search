from linkedin_agent.application_profile_repository import (
    save_verified_answer,
)

from linkedin_agent.application_service import (
    prepare_application,
    answer_application_question,
)


save_verified_answer(
    "requires_sponsorship",
    "Yes",
)

save_verified_answer(
    "authorized_to_work_us",
    "Yes",
)


job = {
    "job_id": "test-100",
    "company": "Microsoft",
    "title": "Director of Engineering",
    "job_url": "https://example.com/job",
}


resume = {
    "resume_text": """
    Senior engineering leader with extensive
    software engineering experience.
    """
}


questions = [
    "Are you legally authorized to work in the United States?",
    "Will you now or in the future require sponsorship?",
    "What is your desired salary?",
]


application = prepare_application(
    job=job,
    master_resume=resume,
    questions=questions,
)


print(application.model_dump_json(indent=2))


resume = {
    "resume_text": """
Senior Software Engineering Manager.

Led distributed engineering teams across the US and India.

More than 10 years of software engineering leadership experience.

Experience with Java, Spring Boot, Kubernetes,
CI/CD automation, and release engineering.
"""
}

result = answer_application_question(
    question="How many years of engineering leadership experience do you have?",
    master_resume=resume,
)

print(result.model_dump_json(indent=2))

resume = {
    "resume_text": """
Senior Software Engineering Manager.

Led distributed engineering teams across the US and India.

More than 10 years of software engineering leadership experience.

Experience with Java, Spring Boot, Kubernetes,
CI/CD automation, and release engineering.
"""
}

result = answer_application_question(
    question="Will you now or in the future require visa sponsorship?",
    master_resume=resume,
)

print(result.model_dump_json(indent=2))