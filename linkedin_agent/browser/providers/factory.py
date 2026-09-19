from linkedin_agent.browser.providers.generic import (
    GenericApplicationProvider,
)
from linkedin_agent.browser.providers.icims import (
    ICIMSApplicationProvider,
)


def get_provider(provider_name: str):
    if provider_name == "icims":
        return ICIMSApplicationProvider()

    return GenericApplicationProvider()