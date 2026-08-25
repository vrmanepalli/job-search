from sqlalchemy import text

from linkedin_agent.database import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("Connected successfully!")
        print(result.scalar())

except Exception as e:
    print("Database connection failed:")
    print(e)