from linkedin_agent.browser.application_form import (
    inspect_form,
)

from linkedin_agent.browser.application_filler import (
    fill_application_form,
)

from linkedin_agent.browser.browser_client import BrowserClient
from linkedin_agent.browser.application_form import inspect_form
from linkedin_agent.browser.application_filler import fill_application_form


def fill_prepared_application(
    page,
    prepared,
) -> dict:
    """
    Inspect the current application form and fill it using
    a PreparedApplication.

    Does NOT submit the application.
    """

    # 1. Inspect the form currently displayed
    fields = inspect_form(page)

    # 2. Convert ApplicationAnswer objects into the dictionary
    #    expected by fill_application_form()
    answers = {}

    for item in prepared.answers:

        if (
            item.answer is not None
            and not item.requires_user_input
        ):

            if item.normalized_key:
                answers[item.normalized_key] = item.answer

            # Label fallback
            answers[item.question] = item.answer

    # 3. Fill fields + upload generated resume
    fill_result = fill_application_form(
        page=page,
        fields=fields,
        answers=answers,
        resume_path=prepared.resume_path,
    )

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
    Open an application page, inspect it, and fill supported fields.

    Does not submit the application.
    """

    browser = BrowserClient()

    try:
        page = browser.start()

        page.goto(job_url)

        fields = inspect_form(page)

        answers = {}

        for item in prepared.answers:
            if (
                item.answer is not None
                and not item.requires_user_input
            ):
                if item.normalized_key:
                    answers[item.normalized_key] = item.answer

                answers[item.question] = item.answer

        result = fill_application_form(
            page=page,
            fields=fields,
            answers=answers,
            resume_path=prepared.resume_path,
        )

        input(
            "Review the application in the browser. "
            "Press Enter when finished..."
        )

        return {
            "success": result["success"],
            "job_id": prepared.job_id,
            "fields_detected": len(fields),
            "fill_result": result,
            "ready_for_review": (
                result["success"]
                and len(prepared.missing_answers) == 0
            ),
        }

    finally:
        browser.close()