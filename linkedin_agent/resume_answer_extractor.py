from langchain_anthropic import ChatAnthropic

from linkedin_agent.application_models import (
    ExtractedApplicationAnswer,
)


llm = ChatAnthropic(
    model="claude-sonnet-5"
)


structured_llm = llm.with_structured_output(
    ExtractedApplicationAnswer
)

def extract_answer_from_resume(
    question: str,
    resume_text: str,
) -> ExtractedApplicationAnswer:

    prompt = f"""
You extract factual job application answers
from a candidate's master resume.

APPLICATION QUESTION:

{question}

MASTER RESUME:

{resume_text}

STRICT RULES:

1. Answer only if the resume explicitly supports the answer.
2. Do not invent facts.
3. Do not estimate years unless the dates in the resume
   clearly support the calculation.
4. Do not invent technologies, certifications,
   accomplishments, titles, employers, or dates.
5. Do not answer legal or sensitive application questions
   from resume content, including:
   - work authorization
   - visa sponsorship
   - disability
   - veteran status
   - race
   - gender
   - salary expectations
6. If the resume does not clearly support the answer,
   set supported=false.
7. If supported=true, provide the exact resume evidence.
8. Use confidence >= 90 only for very clearly supported answers.

Return the structured response.
"""

    return structured_llm.invoke(prompt)

BLOCKED_RESUME_QUESTION_TYPES = [
    "sponsorship",
    "work authorization",
    "authorized to work",
    "salary",
    "compensation",
    "disability",
    "veteran",
    "race",
    "gender",
    "ethnicity",
]

def can_answer_from_resume(
    question: str,
) -> bool:

    normalized = question.lower()

    return not any(
        blocked in normalized
        for blocked in BLOCKED_RESUME_QUESTION_TYPES
    )