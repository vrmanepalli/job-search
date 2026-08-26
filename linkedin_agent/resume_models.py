from pydantic import BaseModel, Field


class ResumeOptimizationResult(BaseModel):
    match_score: int = Field(
        ge=0,
        le=100,
        description="Estimated resume-to-job match score"
    )

    matched_keywords: list[str]
    missing_keywords: list[str]

    strengths: list[str]
    recommendations: list[str]

    optimized_summary: str

    optimized_resume: str