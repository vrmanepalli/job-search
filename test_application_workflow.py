from pathlib import Path

from linkedin_agent.browser.browser_client import (
    BrowserClient,
)

from linkedin_agent.browser.application_workflow import (
    fill_prepared_application,
)

from linkedin_agent.application_models import (
    ApplicationAnswer,
    PreparedApplication,
)


browser = BrowserClient()

try:

    page = browser.start()

    html_file = Path(
        "tests/easy_apply_test.html"
    ).resolve()

    page.goto(
        html_file.as_uri()
    )

    prepared = PreparedApplication(
        job_id="test-123",

        company="Test Company",

        title="Director Engineering",

        resume_path=str(
            Path(
                "tests/sample_resume.pdf"
            ).resolve()
        ),

        answers=[
            ApplicationAnswer(
                question="Phone Number",
                answer="5551234567",
                source="application_profile",
                verified=True,
                requires_user_input=False,
                confidence=100,
            ),

            ApplicationAnswer(
                question=(
                    "How many years of Java "
                    "experience do you have?"
                ),
                normalized_key="years_skill:java",
                answer="10",
                source="application_profile",
                verified=True,
                requires_user_input=False,
                confidence=100,
            ),

            ApplicationAnswer(
                question=(
                    "Will you require visa sponsorship?"
                ),
                normalized_key="requires_sponsorship",
                answer="Yes",
                source="application_profile",
                verified=True,
                requires_user_input=False,
                confidence=100,
            ),
        ],

        missing_answers=[],
        ready_for_review=True,
    )

    result = fill_prepared_application(
        page=page,
        prepared=prepared,
    )

    print(result)

    input(
        "Review the filled form. "
        "Press Enter to close..."
    )

finally:
    browser.close()