from pprint import pprint

from linkedin_agent.job_repository import (
    save_or_update_job,
    get_job_by_external_id,
)


job = save_or_update_job(
    external_job_id="4458293262",
    title="Director of Engineering Platform Services",
    company="Test Company",
    location="Dallas, TX",
    description="This is a temporary test job description.",
    job_url="https://www.linkedin.com/jobs/view/4458293262",
)

print("SAVED:")
pprint(job)


loaded = get_job_by_external_id(
    "4458293262"
)

print("\nLOADED:")
pprint(loaded)