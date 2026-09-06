from urllib.parse import (
    parse_qs,
    unquote,
    urlparse,
)
import re

from linkedin_agent.browser.browser_client import (
    BrowserClient,
)

from linkedin_agent.application_repository import (
    update_application_url,
)

from urllib.parse import (
    parse_qs,
    unquote,
    urlparse,
)


def extract_external_url(
    href: str,
) -> str | None:
    """
    Extract external destination from a LinkedIn
    safety/redirect URL.
    """

    if not href:
        return None

    parsed = urlparse(href)

    # Already external
    if "linkedin.com" not in parsed.netloc.lower():
        return href

    params = parse_qs(
        parsed.query
    )

    values = params.get("url")

    if not values:
        return None

    return unquote(
        values[0]
    )

def extract_redirect_target(
    url: str,
) -> str:

    parsed = urlparse(url)

    params = parse_qs(
        parsed.query
    )

    for key in (
        "url",
        "redirect",
        "redirect_url",
        "target",
    ):
        values = params.get(key)

        if values:
            return unquote(
                values[0]
            )

    return url

def is_linkedin_url(url: str) -> bool:
    try:
        host = urlparse(url).netloc.lower()

        return (
            host.endswith("linkedin.com")
            or host.endswith(".linkedin.com")
        )

    except Exception:
        return False


def find_apply_control(page):

    selectors = [
        'a[aria-label="Apply on company website"]',
        'a[aria-label*="Apply" i]',
        'a[href*="/safety/go/"]',
        'a:has-text("Apply")',
    ]

    for selector in selectors:

        locator = page.locator(selector)

        print(
            "Trying selector:",
            selector,
        )

        try:
            locator.first.wait_for(
                state="attached",
                timeout=5000,
            )

            count = locator.count()

            print(
                "Candidate count:",
                count,
            )

            if count > 0:
                return locator.first

        except Exception as e:

            print(
                "Not found:",
                selector,
                str(e),
            )

    return None


def capture_external_application_url(
    job_id: str,
    job_url: str,
) -> dict:
    """
    Open a LinkedIn job page and capture the external
    application destination URL.

    Does not submit an application.
    """

    browser = BrowserClient()

    try:
        page = browser.start()

        page.goto(
            job_url,
            wait_until="domcontentloaded",
        )

        page.wait_for_timeout(
            3000
        )

        print("Opened job page:")
        print(page.url)

        # Try to find an Apply link/button.
        apply_control = find_apply_control(page)

        if apply_control is None:
            return {
                "success": False,
                "status": "apply_control_not_found",
                "job_id": job_id,
            }

        # Capture the current URL before clicking.
        application_page = page
        # Capture the current URL before clicking.
        before_url = page.url

        try:
            with page.expect_popup(
                timeout=2500
            ) as popup_info:

                apply_control.click()

            application_page = popup_info.value

            application_page.wait_for_load_state(
                "domcontentloaded"
            )

        except Exception:
            # If no popup appeared, wait for same-tab navigation
            try:
                page.wait_for_load_state(
                    "domcontentloaded"
                )
            except Exception:
                pass

            application_page = page

        application_page.wait_for_timeout(
            2000
        )

        after_url = application_page.url

        print("After Apply:")
        print(after_url)
        
        final_url = extract_redirect_target(after_url)

        print("Final Apply:")
        print(final_url)

        if final_url == before_url:
            return {
                "success": False,
                "status": "no_navigation_detected",
                "job_id": job_id,
                "current_url": final_url,
            }

        if is_linkedin_url(final_url):
            return {
                "success": False,
                "status": "still_on_linkedin",
                "job_id": job_id,
                "current_url": final_url,
            }

        # Save external destination.
        updated = update_application_url(
            job_id=job_id,
            application_url=final_url,
        )

        return {
            "success": True,
            "job_id": job_id,
            "application_url": final_url,
            "application": updated,
        }

    finally:
        browser.close()