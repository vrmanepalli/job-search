def detect_provider(page) -> str:
    url = page.url.lower()

    if "greenhouse.io" in url:
        return "greenhouse"

    if "lever.co" in url:
        return "lever"

    if "myworkdayjobs.com" in url:
        return "workday"

    return "generic"