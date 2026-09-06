from pathlib import Path

from linkedin_agent.browser.browser_client import (
    BrowserClient,
)

from linkedin_agent.browser.application_form import (
    inspect_form,
)


browser = BrowserClient()

try:

    page = browser.start()

    html_file = (
        Path("tests/easy_apply_test.html")
        .resolve()
    )

    page.goto(
        html_file.as_uri()
    )

    fields = inspect_form(page)

    for field in fields:

        print()
        print("------------------------------")

        for key, value in field.items():
            print(f"{key}: {value}")

finally:

    browser.close()