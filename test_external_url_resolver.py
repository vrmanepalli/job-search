from linkedin_agent.browser.providers.external_url_resolver import (
    capture_external_application_url,
)


result = capture_external_application_url(
    job_id="4446432236",
    job_url=(
        "https://www.linkedin.com/jobs/view/"
        "director-reliability-automation-performance-engineering-"
        "at-catalyst-brands-llc-4446432236"
    ),
)

print(result)