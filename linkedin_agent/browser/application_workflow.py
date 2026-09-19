from linkedin_agent.browser.application_form import (
    inspect_form,
)

from linkedin_agent.browser.application_filler import (
    fill_application_form,
)

from linkedin_agent.browser.browser_client import (
    BrowserClient,
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

        # Reuse common filling logic
        result = fill_prepared_application(
            page=page,
            prepared=prepared,
        )

        input(
            "Review the application in the browser. "
            "Press Enter when finished..."
        )

        return result

    finally:
        browser.close()