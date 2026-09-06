from sqlalchemy import select

from linkedin_agent.database import SessionLocal
from linkedin_agent.models import ApplicationProfile


def get_verified_answer(
    question_key: str,
) -> dict | None:

    with SessionLocal() as db:

        record = db.scalar(
            select(ApplicationProfile)
            .where(
                ApplicationProfile.question_key
                == question_key
            )
        )

        if not record:
            return None

        return {
            "question_key": record.question_key,
            "answer": record.answer,
            "verified": record.verified,
        }


def save_verified_answer(
    question_key: str,
    answer: str,
) -> dict:

    with SessionLocal() as db:

        record = db.scalar(
            select(ApplicationProfile)
            .where(
                ApplicationProfile.question_key
                == question_key
            )
        )

        if record:
            record.answer = answer
            record.verified = True

        else:
            record = ApplicationProfile(
                question_key=question_key,
                answer=answer,
                verified=True,
            )

            db.add(record)

        db.commit()
        db.refresh(record)

        return {
            "question_key": record.question_key,
            "answer": record.answer,
            "verified": record.verified,
        }