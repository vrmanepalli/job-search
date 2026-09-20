from typing import Literal


ApplicationRoute = Literal[
    "easy_apply",
    "external",
    "unavailable",
]


def detect_application_route(page) -> ApplicationRoute:
    """
    Determine how the LinkedIn job accepts applications.

    This function only classifies the route.
    It does not click Apply or submit anything.
    """

    # LinkedIn Easy Apply
    easy_apply_selectors = [
        'button[aria-label*="Easy Apply"]',
        'button:has-text("Easy Apply")',
    ]

    for selector in easy_apply_selectors:
        locator = page.locator(selector)

        if locator.count() > 0:
            return "easy_apply"

    # External employer application
    external_selectors = [
        'a[aria-label*="Apply on company website"]',
        'a[href*="/safety/go/"]',
    ]

    for selector in external_selectors:
        locator = page.locator(selector)

        if locator.count() > 0:
            return "external"

    return "unavailable"