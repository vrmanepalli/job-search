from sqlalchemy import select

from linkedin_agent.database import SessionLocal
from linkedin_agent.models import ResumeOptimization
from linkedin_agent.models import Resume

def save_master_resume(
    name: str,
    resume_text: str,
) -> dict:

    with SessionLocal() as db:

        # Make existing resumes non-master
        existing = db.scalars(
            select(Resume)
            .where(Resume.is_master == True)
        ).all()

        for resume in existing:
            resume.is_master = False

        resume = Resume(
            name=name,
            resume_text=resume_text,
            is_master=True,
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        return {
            "id": resume.id,
            "name": resume.name,
            "is_master": resume.is_master,
        }


def get_master_resume() -> dict | None:

    with SessionLocal() as db:

        resume = db.scalar(
            select(Resume)
            .where(Resume.is_master == True)
            .order_by(Resume.created_at.desc())
        )

        if not resume:
            return None

        return {
            "id": resume.id,
            "name": resume.name,
            "resume_text": resume.resume_text,
        }
    
def save_resume_optimization(
    original_resume: str,
    job_description: str,
    optimized_resume: str,
    match_score: int,
    job_id: str | None = None,
    company: str | None = None,
    title: str | None = None,
) -> int:

    with SessionLocal() as db:

        record = ResumeOptimization(
            job_id=job_id,
            company=company,
            title=title,
            original_resume=original_resume,
            job_description=job_description,
            optimized_resume=optimized_resume,
            match_score=match_score,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record.id