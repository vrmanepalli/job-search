from linkedin_agent.browser.browser_client import (
    BrowserClient,
)

from linkedin_agent.browser.providers.detector import (
    detect_provider,
)

from linkedin_agent.browser.providers.icims import (
    ICIMSApplicationProvider,
)

from linkedin_agent.application_repository import (
    get_application,
)



browser = BrowserClient()

try:
    JOB_ID = "4446432236"

    job = get_application(JOB_ID)

    print("Database result:")
    print(job)

    if job is None:
        raise RuntimeError(
            f"No application record found for job_id={JOB_ID}"
        )

    application_url = job.get("application_url")

    if not application_url:
        raise RuntimeError(
            f"Application record exists, but application_url is empty "
            f"for job_id={JOB_ID}"
        )

    print("Application URL:")
    print(application_url)

    page = browser.start()

    print(
        "Opening iCIMS..."
    )

    page.goto(
        application_url,
        wait_until="domcontentloaded",
        timeout=30000,
    )

    page.wait_for_timeout(
        3000
    )

    print("\n==========================")
    print("IFRAMES")
    print("==========================")

    print("Frame count:", len(page.frames))

    for i, frame in enumerate(page.frames):

        try:
            count = frame.locator(
                "input, textarea, select"
            ).count()

            print(
                f"Frame {i} field count:",
                count,
            )

        except Exception as e:
            print(
                f"Frame {i} error:",
                e,
            )

    print(
        "Page title:",
        page.title()
    )

    print(
        "URL:",
        page.url
    )

    body_text = page.locator(
        "body"
    ).inner_text()

    print(
        body_text[:3000]
    )

    provider_name = detect_provider(
        page
    )

    print(
        "Provider:",
        provider_name,
    )

    provider = (
        ICIMSApplicationProvider()
    )

    fields = provider.inspect(
        page
    )

    print()
    print("==========================")
    print("FIELDS")
    print("==========================")

    for field in fields:
        print(field)


    print("\n==========================")
    print("BUTTONS")
    print("==========================")

    buttons = page.locator(
        "button, input[type='button'], "
        "input[type='submit'], a"
    )

    count = buttons.count()

    for i in range(min(count, 50)):
        el = buttons.nth(i)

        try:
            text = el.inner_text().strip()
        except Exception:
            text = ""

        try:
            value = el.get_attribute("value")
        except Exception:
            value = None

        try:
            href = el.get_attribute("href")
        except Exception:
            href = None

        if text or value:
            print(
                i,
                "text=",
                repr(text),
                "value=",
                repr(value),
                "href=",
                repr(href),
            )

    state = provider.detect_page_state(
        page
    )

    print(
        "iCIMS page state:",
        state
    )

    input(
        "\nPress ENTER to close..."
    )

finally:

    browser.close()