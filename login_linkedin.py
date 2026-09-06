from linkedin_agent.browser.browser_client import (
    BrowserClient,
)


browser = BrowserClient()

try:

    page = browser.start()

    page.goto(
        "https://www.linkedin.com/login"
    )

    print()
    print("==============================")
    print("LINKEDIN LOGIN")
    print("==============================")
    print()
    print(
        "Sign into LinkedIn manually "
        "in the browser."
    )
    print()
    print(
        "After you reach your LinkedIn "
        "home page, return here."
    )
    print()

    input(
        "Press ENTER after login..."
    )

    print()
    print("Current URL:")
    print(page.url)

finally:

    browser.close()