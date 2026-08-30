from langchain_anthropic import ChatAnthropic

from linkedin_agent.resume_models import ResumeValidationResult


llm = ChatAnthropic(
    model="claude-sonnet-5"
)

validator_llm = llm.with_structured_output(
    ResumeValidationResult
)


def validate_resume(
    original_resume: str,
    optimized_resume: str,
) -> ResumeValidationResult:
    """
    Validate that an optimized resume does not contain
    factual claims unsupported by the original master resume.
    """

    prompt = f"""
You are a strict resume fact-checking system.

Compare the ORIGINAL RESUME with the OPTIMIZED RESUME.

The optimized resume MAY:
- improve wording
- reorganize content
- emphasize relevant experience
- shorten content
- improve clarity
- incorporate ATS terminology when it is factually supported

The optimized resume MUST NOT invent or exaggerate:
- employers
- job titles
- employment dates
- degrees
- certifications
- technologies
- programming languages
- years of experience
- team sizes
- budgets
- revenue
- percentages
- performance metrics
- responsibilities
- accomplishments
- awards

Every factual claim in the optimized resume must be supported
by the original resume.

Do not flag normal rewriting or reasonable paraphrasing as an
unsupported claim when the underlying fact is clearly supported.

ORIGINAL RESUME:

{original_resume}

OPTIMIZED RESUME:

{optimized_resume}

Identify every material unsupported factual claim.

Set valid=false if any material unsupported claim exists.

For severity use one of:
- low
- medium
- high

Return a confidence score from 0 to 100.
"""

    return validator_llm.invoke(prompt)