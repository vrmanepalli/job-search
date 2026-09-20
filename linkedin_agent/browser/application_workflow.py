from linkedin_agent.application_status import ApplicationStatus
from linkedin_agent.browser.application_form import (
    inspect_form,
)

from linkedin_agent.browser.application_filler import (
    fill_application_form,
)

from linkedin_agent.browser.browser_client import (
    BrowserClient,
)

from linkedin_agent.browser.application_route import (
    detect_application_route,
)

from linkedin_agent.browser.external_application_workflow import (
    prepare_external_application,
    submit_external_application,
)

def fill_prepared_application(
    page,
    prepared,
) -> dict:
    """
    Inspect the current application form and fill it using
    a PreparedApplication.

    Does NOT submit the application.
    """

    # 1. Inspect current form
    fields = inspect_form(page)

    # 2. Build answer map
    answers = {}

    for item in prepared.answers:
        if (
            item.answer is not None
            and not item.requires_user_input
        ):
            if item.normalized_key:
                answers[item.normalized_key] = item.answer

            # fallback to original question text
            answers[item.question] = item.answer

    # 3. Fill form
    fill_result = fill_application_form(
        page=page,
        fields=fields,
        answers=answers,
        resume_path=prepared.resume_path,
    )

    # 4. Build common result
    return {
        "success": fill_result["success"],
        "job_id": prepared.job_id,
        "fields_detected": len(fields),
        "fill_result": fill_result,
        "ready_for_review": (
            fill_result["success"]
            and len(prepared.missing_answers) == 0
        ),
    }


def open_and_fill_prepared_application(
    job_url: str,
    prepared,
) -> dict:
    """
    Open an application page and reuse
    fill_prepared_application().

    Does NOT submit the application.
    """

    browser = BrowserClient()

    try:
        page = browser.start()

        page.goto(
            job_url,
            wait_until="domcontentloaded",
        )

        route = detect_application_route(page)

        print(f"Application route: {route}")

        if route == "external":
            application_url = prepared.application_url

            if not application_url:
                return {
                    "success": False,
                    "submitted": False,
                    "status": "external_application_url_missing",
                    "job_id": prepared.job_id,
                }

            result = prepare_external_application(
                page=page,
                application_url=application_url,
                prepared_application=prepared,
            )
            if result.get("status") != ApplicationStatus.READY_FOR_REVIEW:
                return result

        elif route == "easy_apply":
            result = fill_prepared_application(
                page=page,
                prepared=prepared,
            )
            input(
                "Review the application in the browser. "
                "Press Enter when finished..."
            )

        else:
            return {
                        "success": False,
                        "submitted": False,
                        "status": "application_unavailable",
                        "job_id": prepared.job_id,
                    }
        
        print()
        print("==========================")
        print("APPLICATION RESULT")
        print("==========================")
        print(result)

        status = result.get("status")

        if status == ApplicationStatus.READY_FOR_REVIEW:
            print()
            print("==========================")
            print("READY FOR REVIEW")
            print("==========================")
            print()
            print("The application has been filled.")
            print("It has NOT been submitted.")
            print()
            print("Review the application in the browser.")
            print()


            approval = input(
                "Type SUBMIT to submit this application, "
                "or press Enter to stop: "
            ).strip()

            if approval != "SUBMIT":
                return {
                    **result,
                    "submitted": False,
                    "status": ApplicationStatus.READY_FOR_REVIEW,
                }

            submission_result = submit_external_application(
                page=page,
                provider_name=result["provider"],
                job_id=prepared.job_id,
            )

            return submission_result

        return result

    finally:
        browser.close()