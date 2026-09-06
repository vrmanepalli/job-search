from linkedin_agent.resume_file_service import (
    save_resume_text,
)


resume_text = """
John Doe

Director of Engineering

Experienced engineering leader...
"""


resume_path = save_resume_text(
    resume_text=resume_text,
    company="Microsoft",
    title="Director of Engineering",
    job_id="123456",
)


print(
    "Resume saved at:"
)

print(
    resume_path
)