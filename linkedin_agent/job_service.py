from linkedin_agent.real_linkedin_scraper import LinkedInJobScraper

def get_job_details_by_id(job_id: str) -> dict | None:
    """
    Return normalized job details for resume optimization.
    """

    # Use your existing scraper / job retrieval implementation here.

    scraper = LinkedInJobScraper()

    job = scraper.get_job_details(job_id)

    if not job:
        return None

    if not isinstance(job, dict):
        raise TypeError(
            f"Expected job details to be dict, got {type(job).__name__}"
        )

    return {
        "job_id": job_id,
        "title": job.get("title"),
        "company": job.get("company"),
        "description": job.get("description"),
        "job_url": job.get("job_url"),
    }