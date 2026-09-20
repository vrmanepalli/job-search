import re
from typing import Any


# Explicit sponsorship restrictions.
# Keep these conservative: we only want to reject when the posting
# clearly states a restriction.
SPONSORSHIP_EXCLUSION_PATTERNS = [
    r"\bno\s+(?:visa\s+)?sponsorship\b",
    r"\bno\s+sponsorship\s+(?:is\s+)?available\b",
    r"\bwill\s+not\s+sponsor\b",
    r"\bdoes\s+not\s+sponsor\b",
    r"\bdo\s+not\s+sponsor\b",
    r"\bunable\s+to\s+sponsor\b",
    r"\bcannot\s+sponsor\b",
    r"\bcan't\s+sponsor\b",
    r"\bnot\s+(?:eligible|available)\s+for\s+(?:visa\s+)?sponsorship\b",
    r"\bsponsorship\s+(?:is\s+)?not\s+(?:available|provided)\b",
    r"\bvisa\s+sponsorship\s+(?:is\s+)?not\s+(?:available|provided)\b",
    r"\bwithout\s+(?:current\s+or\s+future\s+)?sponsorship\b",
    r"\bwithout\s+(?:the\s+)?need\s+for\s+(?:current\s+or\s+future\s+)?sponsorship\b",
    r"\bmust\s+not\s+require\s+(?:current\s+or\s+future\s+)?sponsorship\b",
]


# Citizenship restrictions are kept separate so the caller can see
# exactly why the job was rejected.
CITIZENSHIP_EXCLUSION_PATTERNS = [
    r"\bu\.?s\.?\s+citizens?\s+only\b",
    r"\bus\s+citizens?\s+only\b",
    r"\bmust\s+be\s+(?:a\s+)?u\.?s\.?\s+citizen\b",
    r"\bmust\s+be\s+(?:a\s+)?us\s+citizen\b",
    r"\bu\.?s\.?\s+citizenship\s+(?:is\s+)?required\b",
    r"\bus\s+citizenship\s+(?:is\s+)?required\b",
]


# These phrases are not automatic rejection.
# They indicate that a human should verify the wording.
AMBIGUOUS_SPONSORSHIP_PATTERNS = [
    r"\bauthorized\s+to\s+work\s+in\s+the\s+u\.?s\.?\b",
    r"\blegally\s+authorized\s+to\s+work\s+in\s+the\s+u\.?s\.?\b",
    r"\bwork\s+authorization\s+required\b",
    r"\bemployment\s+authorization\s+required\b",
]


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""

    value = value.replace("\u00a0", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def _find_matches(
    text: str,
    patterns: list[str],
) -> list[str]:
    matches: list[str] = []

    for pattern in patterns:
        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):
            matched_text = match.group(0).strip()

            if matched_text not in matches:
                matches.append(matched_text)

    return matches


def check_job_eligibility(
    job: dict[str, Any],
) -> dict[str, Any]:
    """
    Evaluate a job posting before resume optimization.

    Important:
    - Explicit sponsorship/citizenship restrictions => ineligible.
    - Ambiguous work-authorization language => requires review.
    - Missing description => cannot safely determine eligibility.
    - No restriction found => eligible, but this does NOT mean
      sponsorship has been positively confirmed.
    """

    job_id = str(
        job.get("job_id")
        or job.get("external_job_id")
        or ""
    )

    title = job.get("title")
    company = job.get("company")

    # Add other text fields here if your job retrieval service
    # eventually stores them separately.
    text_parts = [
        job.get("description"),
        job.get("requirements"),
        job.get("qualifications"),
        job.get("notes"),
    ]

    combined_text = _normalize_text(
        "\n".join(
            str(value)
            for value in text_parts
            if value
        )
    )

    if not combined_text:
        return {
            "eligible": False,
            "status": "job_description_missing",
            "job_id": job_id,
            "title": title,
            "company": company,
            "sponsorship_restriction_found": False,
            "citizenship_restriction_found": False,
            "requires_review": True,
            "reason": (
                "Job description is missing, so sponsorship "
                "eligibility cannot be verified."
            ),
            "matched_text": [],
        }

    sponsorship_matches = _find_matches(
        combined_text,
        SPONSORSHIP_EXCLUSION_PATTERNS,
    )

    citizenship_matches = _find_matches(
        combined_text,
        CITIZENSHIP_EXCLUSION_PATTERNS,
    )

    ambiguous_matches = _find_matches(
        combined_text,
        AMBIGUOUS_SPONSORSHIP_PATTERNS,
    )

    if citizenship_matches:
        return {
            "eligible": False,
            "status": "citizenship_restriction",
            "job_id": job_id,
            "title": title,
            "company": company,
            "sponsorship_restriction_found": False,
            "citizenship_restriction_found": True,
            "requires_review": False,
            "reason": (
                "The job posting contains an explicit "
                "U.S. citizenship restriction."
            ),
            "matched_text": citizenship_matches,
        }

    if sponsorship_matches:
        return {
            "eligible": False,
            "status": "sponsorship_restriction",
            "job_id": job_id,
            "title": title,
            "company": company,
            "sponsorship_restriction_found": True,
            "citizenship_restriction_found": False,
            "requires_review": False,
            "reason": (
                "The job posting contains explicit language "
                "indicating sponsorship is unavailable."
            ),
            "matched_text": sponsorship_matches,
        }

    if ambiguous_matches:
        return {
            "eligible": True,
            "status": "eligibility_review_required",
            "job_id": job_id,
            "title": title,
            "company": company,
            "sponsorship_restriction_found": False,
            "citizenship_restriction_found": False,
            "requires_review": True,
            "reason": (
                "Work-authorization language was found, but it "
                "does not clearly establish whether sponsorship "
                "is available."
            ),
            "matched_text": ambiguous_matches,
        }

    return {
        "eligible": True,
        "status": "eligible_no_explicit_restriction",
        "job_id": job_id,
        "title": title,
        "company": company,
        "sponsorship_restriction_found": False,
        "citizenship_restriction_found": False,
        "requires_review": False,
        "reason": (
            "No explicit sponsorship or citizenship restriction "
            "was detected in the available job text."
        ),
        "matched_text": [],
    }