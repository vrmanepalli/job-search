from linkedin_agent.browser.providers.detector import detect_provider
from linkedin_agent.browser.providers.factory import get_provider

from linkedin_agent.application_status import (
    ApplicationStatus,
)

from linkedin_agent.application_repository import (
    mark_application_applied,
    update_application_status,
)


def prepare_external_application(
        page,
        application_url: str,
        prepared_application,
    ) -> dict:

    page.goto(
        application_url,
        wait_until="domcontentloaded",
    )

    provider_name = detect_provider(page)

    provider = get_provider(provider_name)

    print(f"Detected provider: {provider_name}")
    print(f"Using provider: {provider.__class__.__name__}")

    blocker = provider.detect_blocker(
        page
    )

    if blocker:
        return {
            "success": False,
            "submitted": False,
            "status": ApplicationStatus.MANUAL_REQUIRED,
            "provider": provider_name,
            "blocker": blocker,
        }

    fill_result = provider.fill(
        page,
        prepared_application,
    )

    # Stop here for user review
    if not fill_result["success"]:
        return {
            "success": False,
            "submitted": False,
            "status": ApplicationStatus.NEEDS_USER_INPUT ,
            "provider": provider_name,
            "fill_result": fill_result,
        }

    # At this stage the application is only prepared.
    # It has NOT been submitted.
    status = ApplicationStatus.READY_FOR_REVIEW

    return {
        "success": fill_result["success"],
        "submitted": False,
        "provider": provider_name,
        "status": status,
        "fill_result": fill_result,
        "current_url": page.url,
    }

def submit_external_application(
    page,
    provider_name: str,
    job_id: str,
) -> dict:
    """
    Submit an application that has already been prepared
    and reviewed by the user.

    This function must only be called after explicit
    user approval.
    """
    provider = get_provider(provider_name)

    submit_result = provider.submit(page)

    if not submit_result.get("success"):
        update_application_status(
            job_id=job_id,
            status=ApplicationStatus.SUBMISSION_UNVERIFIED.value,
        )
        return {
            "success": False,
            "submitted": False,
            "status": ApplicationStatus.SUBMISSION_UNVERIFIED,
            "provider": provider_name,
            "submit_result": submit_result,
            "current_url": page.url,
        }

    verified = provider.verify_submission(page)

    if verified:
        mark_application_applied(
            job_id=job_id,
            submission_verified=True,
        )
        return {
            "success": True,
            "submitted": True,
            "status": ApplicationStatus.APPLIED,
            "provider": provider_name,
            "submit_result": submit_result,
            "current_url": page.url,
        }

    update_application_status(
        job_id=job_id,
        status=ApplicationStatus.SUBMISSION_UNVERIFIED.value,
    )

    return {
        "success": False,
        "submitted": True,
        "status": ApplicationStatus.SUBMISSION_UNVERIFIED,
        "provider": provider_name,
        "submit_result": submit_result,
        "current_url": page.url,
    }