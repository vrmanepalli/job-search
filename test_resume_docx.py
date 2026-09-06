from linkedin_agent.resume_file_service import (
    save_resume_docx,
)


resume_text = """
JOHN DOE

DIRECTOR OF SOFTWARE ENGINEERING

PROFESSIONAL SUMMARY

Engineering leader with extensive experience
building and leading software engineering teams.

EXPERIENCE

Senior Engineering Manager
Example Company

• Led distributed engineering teams.
• Improved software delivery automation.
• Built scalable CI/CD platforms.

TECHNICAL SKILLS

Java, Spring Boot, Kubernetes, CI/CD
"""


resume_path = save_resume_docx(
    resume_text=resume_text,
    company="Microsoft",
    title="Director of Engineering",
    job_id="123456",
)


print("Generated resume:")
print(resume_path)