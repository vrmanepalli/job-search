from linkedin_agent.job_eligibility_service import (
    check_job_eligibility,
)


def test_no_sponsorship():
    job = {
        "job_id": "123",
        "title": "Director of Engineering",
        "company": "Test Company",
        "description": """
        Candidates must be authorized to work in the United States.
        Visa sponsorship is not available for this position.
        """,
    }

    result = check_job_eligibility(job)

    print(result)

    assert result["eligible"] is False
    assert result["sponsorship_restriction_found"] is True


def test_citizenship_required():
    job = {
        "job_id": "456",
        "title": "Engineering Director",
        "company": "Test Company",
        "description": """
        Must be a U.S. citizen.
        """,
    }

    result = check_job_eligibility(job)

    print(result)

    assert result["eligible"] is False
    assert result["citizenship_restriction_found"] is True


def test_ambiguous_authorization():
    job = {
        "job_id": "789",
        "title": "Director",
        "company": "Test Company",
        "description": """
        Candidate must be legally authorized to work in the U.S.
        """,
    }

    result = check_job_eligibility(job)

    print(result)

    assert result["eligible"] is True
    assert result["requires_review"] is True


def test_no_restriction():
    job = {
        "job_id": "999",
        "title": "Director",
        "company": "Test Company",
        "description": """
        We are looking for an experienced engineering leader
        with expertise in cloud platforms, CI/CD, Kubernetes,
        and software engineering.
        """,
    }

    result = check_job_eligibility(job)

    print(result)

    assert result["eligible"] is True
    assert result["requires_review"] is False