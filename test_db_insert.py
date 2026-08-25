from linkedin_agent.database import SessionLocal
from linkedin_agent.models import Application

try:
    with SessionLocal() as db:
        application = Application(
            job_id="test-001",
            company="Test Company",
            title="Software Engineering Manager",
            status="saved",
            notes="Database integration test",
        )

        db.add(application)
        db.commit()
        db.refresh(application)

        print("Application saved successfully!")
        print("Database ID:", application.id)
        print("Company:", application.company)
        print("Title:", application.title)
        print("Status:", application.status)

except Exception as e:
    print("Insert failed:")
    print(e)