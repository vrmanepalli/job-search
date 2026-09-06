# import os

# from dotenv import load_dotenv
import json

from langchain_anthropic import ChatAnthropic

from linkedin_agent.job_repository import get_job_by_external_id
from linkedin_agent.resume_models import ResumeOptimizationResult

from linkedin_agent.resume_repository import get_master_resume, save_resume_optimization
from linkedin_agent.resume_validator import (
    validate_resume,
)

from linkedin_agent.resume_file_service import (
    save_resume_docx,
)

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Optional safety check
# if not os.getenv("ANTHROPIC_API_KEY"):
#     raise RuntimeError(
#         "ANTHROPIC_API_KEY is not configured. "
#         "Add it to the project's .env file."
#     )


llm = ChatAnthropic(
    model="claude-sonnet-5"
)

def optimize_resume(
    resume_text: str,
    job_description: str,
) -> ResumeOptimizationResult:

    structured_llm = llm.with_structured_output(
        ResumeOptimizationResult
    )

    prompt = f"""
You are an expert resume optimization assistant.

Your job is to optimize the candidate's existing resume
for the supplied job description.

IMPORTANT RULES:

1. Never invent experience.
2. Never invent skills.
3. Never invent employers.
4. Never invent metrics.
5. Preserve the candidate's factual history.
6. Improve wording and prioritization only.
7. Identify ATS keywords from the job description.
8. Identify which keywords already exist in the resume.
9. Identify relevant missing keywords.
10. Only include a missing skill in the optimized resume
    if the original resume clearly supports that skill.

JOB DESCRIPTION:

{job_description}

CURRENT RESUME:

{resume_text}

Return:

- match score from 0 to 100
- matched keywords
- missing keywords
- key strengths
- recommendations
- optimized professional summary
- complete optimized resume
"""

    return structured_llm.invoke(prompt)

def optimize_and_validate_resume(
    resume_text: str,
    job_description: str,
):
    optimization = optimize_resume(
        resume_text=resume_text,
        job_description=job_description,
    )

    validation = validate_resume(
        original_resume=resume_text,
        optimized_resume=optimization.optimized_resume,
    )

    return optimization, validation


def correct_optimized_resume(
    original_resume: str,
    optimized_resume: str,
    unsupported_claims: list,
):

    issues = "\n".join(
        f"- {issue.claim}: {issue.reason}"
        for issue in unsupported_claims
    )

    prompt = f"""
Correct the optimized resume.

The fact checker found unsupported claims.

UNSUPPORTED CLAIMS:

{issues}

ORIGINAL RESUME:

{original_resume}

OPTIMIZED RESUME:

{optimized_resume}

Remove or rewrite every unsupported claim.

Do not introduce any new facts.

Return the corrected resume only.
"""

    response = llm.invoke(prompt)

    return response.content

def optimize_resume_for_job_service(job_id: str) -> dict:
    """
    Optimize the stored master resume for a specific job.

    Loads the master resume and target job description,
    creates a tailored resume, validates factual accuracy,
    and saves the validated optimization.
    """


    try:
        master_resume = get_master_resume()

        print("DEBUG master resume:", master_resume)
        print("DEBUG master resume type:", type(master_resume))
        
        if not master_resume:
            return {
                "success": False,
                "error": "No master resume is stored."
            }

        if not isinstance(master_resume, dict):
            return {
                "success": False,
                "error": (
                    "get_master_resume returned unexpected type: "
                    f"{type(master_resume).__name__}"
                ),
            }

        job = get_job_by_external_id(job_id)

        if job is Ellipsis:
            return {
                "success": False,
                "error": (
                    "get_job_details_by_id returned Ellipsis. "
                    "Replace the '...' placeholder in job_service.py "
                    "with the real job retrieval implementation."
                ),
            }

        if not job:
            return {
                "success": False,
                "error": f"Job '{job_id}' was not found."
            }

        if not isinstance(job, dict):
            return {
                "success": False,
                "error": (
                    "Job lookup returned unexpected type: "
                    f"{type(job).__name__}"
                ),
            }

        job_description = job.get("description")

        if not job_description:
            return {
                "success": False,
                "error": "Job description is missing."
            }

        MAX_ATTEMPTS = 2

        optimization = None
        validation = None

        for attempt in range(MAX_ATTEMPTS):
            optimization = optimize_resume(
                resume_text=master_resume["resume_text"],
                job_description=job_description,
            )

            validation = validate_resume(
                original_resume=master_resume["resume_text"],
                optimized_resume=optimization.optimized_resume,
            )

            if validation.valid:
                break

        if not validation.valid:

            failed_id = save_resume_optimization(
                original_resume=master_resume["resume_text"],
                job_description=job_description,
                optimized_resume=optimization.optimized_resume,
                match_score=optimization.match_score,

                job_id=job_id,
                company=job.get("company"),
                title=job.get("title"),

                validation_passed=False,
                validation_score=validation.confidence_score,
                validation_summary=validation.summary,
                validation_issues_json=json.dumps(
                    [
                        issue.model_dump()
                        for issue in validation.unsupported_claims
                    ]
                ),
            )

            return {
                "success": False,
                "optimization_id": failed_id,
                "validation_failed": True,
                "unsupported_claims": [
                    issue.model_dump()
                    for issue in validation.unsupported_claims
                ],
            }

        validation_issues_json = json.dumps(
            [
                issue.model_dump()
                for issue in validation.unsupported_claims
            ]
        )

        company = job.get("company")
        title = job.get("title")
        job_url = job.get("job_url")

        # --------------------------------------------------
        # 6. Save generated resume file
        # --------------------------------------------------

        resume_path = save_resume_docx(
            resume_text=optimization.optimized_resume,
            company=company or "unknown_company",
            title=title or "job",
            job_id=job_id,
        )

        optimization_id = save_resume_optimization(
            original_resume=master_resume["resume_text"],
            job_description=job_description,
            optimized_resume=optimization.optimized_resume,
            match_score=optimization.match_score,
            job_id=job_id,
            company=company,
            title=title,
            validation_passed=True,
            validation_score=validation.confidence_score,
            validation_summary=validation.summary,
            validation_issues_json=validation_issues_json,
        )

        return {
            "success": True,
            "optimization_id": optimization_id,
            "job_id": job_id,
            "company": company,
            "title": title,
            "job_url": job_url,
            "validation_passed": True,
            "validation_score": validation.confidence_score,
            **optimization.model_dump(),
            "resume_path": resume_path,
        }

    except Exception as e:
        return {
            "success": False,
            "job_id": job_id,
            "error": str(e),
        }