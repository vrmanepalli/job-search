from linkedin_agent.browser.browser_client import (
    BrowserClient,
)

from linkedin_agent.browser.providers.detector import (
    detect_provider,
)

from linkedin_agent.browser.providers.generic import (
    GenericApplicationProvider,
)

from linkedin_agent.browser.providers.factory import (
    get_provider,
)

from linkedin_agent.application_status import (
    ApplicationStatus,
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

        provider_name = detect_provider(page)

        provider = get_provider(provider_name)

        provider = GenericApplicationProvider()

        blocker = provider.detect_blocker(
            page
        )

        if blocker:
            return {
                "success": False,
                "submitted": False,
                "status": ApplicationStatus.MANUAL_REQUIRED,
                "provider": provider_name,
                "blocker": blocker,
            }

        fill_result = provider.fill(
            page,
            prepared_application,
        )

        # Stop here for user review
        if not fill_result["success"]:
            return {
                "success": False,
                "submitted": False,
                "status": ApplicationStatus.NEEDS_USER_INPUT ,
                "provider": provider_name,
                "fill_result": fill_result,
            }

        # At this stage the application is only prepared.
        # It has NOT been submitted.
        status = ApplicationStatus.READY_FOR_REVIEW

        return {
            "success": fill_result["success"],
            "submitted": False,
            "provider": provider_name,
            "status": status,
            "fill_result": fill_result,
            "current_url": page.url,
        }

    finally:
        browser.close()