from sqlalchemy import select

from linkedin_agent.database import SessionLocal
from linkedin_agent.models import Job


def save_or_update_job(
    external_job_id: str,
    title: str | None = None,
    company: str | None = None,
    location: str | None = None,
    description: str | None = None,
    job_url: str | None = None,
    source: str = "linkedin",
) -> dict:

    with SessionLocal() as db:

        job = db.scalar(
            select(Job)
            .where(Job.external_job_id == external_job_id)
        )

        if job is None:
            job = Job(
                external_job_id=external_job_id,
                title=title,
                company=company,
                location=location,
                description=description,
                job_url=job_url,
                source=source,
            )

            db.add(job)

        else:
            if title is not None:
                job.title = title

            if company is not None:
                job.company = company

            if location is not None:
                job.location = location

            if description is not None:
                job.description = description

            if job_url is not None:
                job.job_url = job_url

            if source is not None:
                job.source = source

        db.commit()
        db.refresh(job)

        return job_to_dict(job)


def get_job_by_external_id(
    external_job_id: str,
) -> dict | None:

    with SessionLocal() as db:

        job = db.scalar(
            select(Job)
            .where(Job.external_job_id == external_job_id)
        )

        if not job:
            return None

        return job_to_dict(job)


def job_to_dict(job: Job) -> dict:

    return {
        "id": job.id,
        "job_id": job.external_job_id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "job_url": job.job_url,
        "source": job.source,
    }