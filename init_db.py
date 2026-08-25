from linkedin_agent.database import Base, engine
from linkedin_agent import models

Base.metadata.create_all(bind=engine)

print("Database tables created.")