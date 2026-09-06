from linkedin_agent.browser.browser_client import (
    BrowserClient,
)

from linkedin_agent.browser.providers.detector import (
    detect_provider,
)

from linkedin_agent.browser.providers.generic import (
    GenericApplicationProvider,
)


def apply_external_job(
    application_url: str,
    prepared_application,
) -> dict:

    browser = BrowserClient()

    try:
        page = browser.start()

        page.goto(
            application_url,
            wait_until="domcontentloaded",
        )

        provider_name = detect_provider(
            page
        )

        provider = GenericApplicationProvider()

        blocker = provider.detect_blocker(
            page
        )

        if blocker:
            return {
                "success": False,
                "submitted": False,
                "status": "manual_required",
                "provider": provider_name,
                "blocker": blocker,
            }

        fill_result = provider.fill(
            page,
            prepared_application,
        )

        return {
            "success": fill_result["success"],
            "submitted": False,
            "provider": provider_name,
            "status": "ready_for_review",
            "fill_result": fill_result,
            "current_url": page.url,
        }

    finally:
        browser.close()