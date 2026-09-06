from linkedin_agent.resume_file_service import (
    save_resume_docx,
)


resume_text = """
PROFESSIONAL SUMMARY

Engineering leader with extensive experience building
high-performing software engineering organizations.

TECHNICAL SKILLS

Java, Spring Boot, Kubernetes, CI/CD, React

PROFESSIONAL EXPERIENCE

Senior Engineering Manager | Walmart | Bentonville, AR | 2020–Present
• Led distributed engineering teams across the US and India.
• Improved developer productivity through CI/CD automation.
• Increased software release frequency.

Engineering Manager | Sears | Chicago, IL | 2015–2020
• Led engineering initiatives across multiple applications.
• Mentored software engineers and technical leaders.

EDUCATION

Bachelor of Engineering
"""


path = save_resume_docx(
    resume_text=resume_text,
    company="Microsoft",
    title="Director of Engineering",
    job_id="123456",
)

print(path)