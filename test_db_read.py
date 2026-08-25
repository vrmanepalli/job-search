from sqlalchemy import select

from linkedin_agent.database import SessionLocal
from linkedin_agent.models import Application

with SessionLocal() as db:
    statement = select(Application)

    applications = db.scalars(statement).all()

    print(f"Found {len(applications)} applications")

    for app in applications:
        print(
            app.id,
            app.company,
            app.title,
            app.status,
        )