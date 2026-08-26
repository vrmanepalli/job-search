# import os

# from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

from linkedin_agent.resume_models import ResumeOptimizationResult


# Load environment variables from .env
# load_dotenv()

# Optional safety check
# if not os.getenv("ANTHROPIC_API_KEY"):
#     raise RuntimeError(
#         "ANTHROPIC_API_KEY is not configured. "
#         "Add it to the project's .env file."
#     )


llm = ChatAnthropic(
    model="claude-sonnet-5"
)

def optimize_resume(
    resume_text: str,
    job_description: str,
) -> ResumeOptimizationResult:

    structured_llm = llm.with_structured_output(
        ResumeOptimizationResult
    )

    prompt = f"""
You are an expert resume optimization assistant.

Your job is to optimize the candidate's existing resume
for the supplied job description.

IMPORTANT RULES:

1. Never invent experience.
2. Never invent skills.
3. Never invent employers.
4. Never invent metrics.
5. Preserve the candidate's factual history.
6. Improve wording and prioritization only.
7. Identify ATS keywords from the job description.
8. Identify which keywords already exist in the resume.
9. Identify relevant missing keywords.
10. Only include a missing skill in the optimized resume
    if the original resume clearly supports that skill.

JOB DESCRIPTION:

{job_description}

CURRENT RESUME:

{resume_text}

Return:

- match score from 0 to 100
- matched keywords
- missing keywords
- key strengths
- recommendations
- optimized professional summary
- complete optimized resume
"""

    return structured_llm.invoke(prompt)