from linkedin_agent.job_service import get_job_details
from linkedin_agent.application_service import prepare_application
from linkedin_agent.application_repository import get_application
from linkedin_agent.browser.external_application_workflow import (
    run_external_application,
)


def auto_apply_job(job_id: str) -> dict:
    # 1. Retrieve job
    job = get_job_details(job_id)

    if not job:
        return {
            "success": False,
            "status": "job_not_found",
        }

    description = job.get("description") or ""

    if not description.strip():
        return {
            "success": False,
            "status": "job_description_missing",
        }

    # 2. Application record contains ATS URL/status
    application = get_application(job_id)

    if not application:
        return {
            "success": False,
            "status": "application_record_missing",
        }

    application_url = application.get("application_url")

    if not application_url:
        return {
            "success": False,
            "status": "application_url_missing",
        }

    # 3. Prepare resume + answers
    prepared = prepare_application(job_id)

    if prepared.missing_answers:
        return {
            "success": False,
            "status": "needs_user_input",
            "missing_answers": prepared.missing_answers,
        }

    # 4. Open ATS and fill
    result = run_external_application(
        prepared_application=prepared,
        application_url=application_url,
    )

    return result