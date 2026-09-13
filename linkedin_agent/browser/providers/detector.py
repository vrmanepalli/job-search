from urllib.parse import urlparse


def detect_provider(page) -> str:

    url = page.url.lower()

    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        host = ""

    if (
        "icims.com" in host
        or ".icims." in host
    ):
        return "icims"

    if "greenhouse.io" in host:
        return "greenhouse"

    if "lever.co" in host:
        return "lever"

    if "myworkdayjobs.com" in host:
        return "workday"

    return "generic"