from pathlib import Path

from linkedin_agent.browser.browser_client import (
    BrowserClient,
)

from linkedin_agent.browser.application_form import (
    inspect_form,
)

from linkedin_agent.browser.application_filler import (
    fill_application_form,
)


browser = BrowserClient()

try:
    page = browser.start()

    html_file = Path(
        "tests/easy_apply_test.html"
    ).resolve()

    resume_file = Path(
        "generated_resumes/"
        "microsoft_director_of_engineering_123456.docx"
    ).resolve()

    if not html_file.exists():
        raise FileNotFoundError(html_file)

    if not resume_file.exists():
        raise FileNotFoundError(resume_file)

    page.goto(
        html_file.as_uri()
    )

    fields = inspect_form(page)

    answers = {
        "years_skill:java": "10",
        "requires_sponsorship": "Yes",
        "Phone Number": "5551234567",
    }

    result = fill_application_form(
        page=page,
        fields=fields,
        answers=answers,
        resume_path=str(resume_file),
    )

    print(result)

    input(
        "Review the browser and press Enter to close..."
    )

finally:
    browser.close()