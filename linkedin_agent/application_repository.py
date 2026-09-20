from datetime import datetime, timezone

from sqlalchemy import func, select, text

from .database import SessionLocal
from .models import Application

import re


def extract_linkedin_job_id(value: str) -> str:
    match = re.search(r"(\d{8,})$", value)

    if not match:
        raise ValueError(
            f"Could not extract LinkedIn job ID from: {value}"
        )

    return match.group(1)

def create_application(
    job_id: str,
    title: str,
    company: str,
    job_url: str | None = None,
    application_url: str | None = None,
    status: str = "saved",
    notes: str | None = None,
) -> dict:

    with SessionLocal() as db:

        # Avoid duplicate applications
        existing = db.scalar(
            select(Application)
            .where(Application.job_id == job_id)
        )

        if existing:
            return application_to_dict(existing)

        new_job_id = extract_linkedin_job_id(job_id)

        application = Application(
            job_id=new_job_id,
            title=title,
            company=company,
            job_url=job_url,
            application_url=application_url,
            status=status,
            notes=notes,
        )

        if status == "applied":
            application.applied_at = datetime.now(timezone.utc)

        db.add(application)
        db.commit()
        db.refresh(application)

        return application_to_dict(application)


def get_applications(limit: int = 10) -> tuple[list[dict], int]:

    with SessionLocal() as db:

        statement = (
            select(Application)
            .order_by(Application.created_at.desc())
            .limit(limit)
        )

        applications = db.scalars(statement).all()

        total_count = db.scalar(
            select(func.count(Application.id))
        ) or 0

        return (
            [application_to_dict(app) for app in applications],
            total_count,
        )


def get_application(job_id: str) -> dict | None:

    with SessionLocal() as db:

        application = db.scalar(
            select(Application)
            .where(Application.job_id == job_id)
        )

        if not application:
            return None

        return application_to_dict(application)



def update_application_url(
    job_id: str,
    application_url: str,
) -> dict | None:

    with SessionLocal() as db:

        application = db.scalar(
            select(Application)
            .where(
                Application.job_id == job_id
            )
        )

        if application is None:
            print(
                "ERROR: application record is none"
            )
            return None

        if not application:
            print(
                            "ERROR: application record not found"
                        )
            return None

        application.application_url = application_url
        db.add(application)
        db.flush()
        db.commit()
        db.refresh(application)

        return application_to_dict(
            application
        )
    

def update_application_status(
    job_id: str,
    status: str,
) -> dict | None:

    with SessionLocal() as db:

        application = db.scalar(
            select(Application)
            .where(Application.job_id == job_id)
        )

        if not application:
            return None

        application.status = status

        if status == "applied" and application.applied_at is None:
            application.applied_at = datetime.now(timezone.utc)

    
        db.commit()
        db.refresh(application)

        return application_to_dict(application)

def mark_application_applied(
    job_id: str,
    submission_verified: bool,
) -> dict | None:

    if not submission_verified:
        raise ValueError(
            "Cannot mark application as applied "
            "without verified submission."
        )

    return update_application_status(
        job_id=job_id,
        status="applied",
    )

def application_to_dict(application: Application) -> dict:

    return {
        "id": application.id,
        "job_id": application.job_id,
        "title": application.title,
        "company": application.company,
        "job_url": application.job_url,
        "application_url": application.application_url,
        "status": application.status,
        "notes": application.notes,
        "applied_date": (
            application.applied_at.isoformat()
            if application.applied_at
            else None
        ),
        "created_at": (
            application.created_at.isoformat()
            if application.created_at
            else None
        ),

        "last_updated": (
            application.updated_at.isoformat()
            if application.updated_at
            else None
        ),
    }