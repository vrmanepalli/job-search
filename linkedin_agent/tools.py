"""
Extended tools for LinkedIn job search and application.
This file contains additional tools that can be added to the agent.
"""
from linkedin_agent.application_repository import (
    create_application,
    get_applications,
    get_application,
    update_application_status,
)
from langchain_core.tools import tool
from typing import List, Dict, Optional
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from linkedin_agent.resume_service import optimize_resume
from linkedin_agent.resume_repository import (
    save_resume_optimization,
    save_master_resume,
    get_master_resume,
)
from linkedin_agent.resume_validator import validate_resume
import json
from linkedin_agent.job_repository import (
    get_job_by_external_id,
)

# ============================================================================
# PROFILE MANAGEMENT TOOLS
# ============================================================================

@tool
def update_user_preferences(
    preferred_locations: List[str],
    desired_roles: List[str],
    salary_range: str = "",
    remote_only: bool = False
) -> dict:
    """
    Update user's job search preferences.
    
    Args:
        preferred_locations: List of preferred job locations
        desired_roles: List of desired job titles/roles
        salary_range: Expected salary range (e.g., "100k-150k")
        remote_only: Whether to only search for remote positions
    
    Returns:
        Confirmation of updated preferences
    """
    preferences = {
        "locations": preferred_locations,
        "roles": desired_roles,
        "salary_range": salary_range,
        "remote_only": remote_only
    }
    
    # TODO: Store preferences in database
    return {
        "success": True,
        "message": "Preferences updated successfully",
        "preferences": preferences
    }


@tool
def get_user_profile() -> dict:
    """
    Retrieve user's LinkedIn profile information and resume.
    
    Returns:
        User profile data including resume, skills, experience
    """
    # TODO: Fetch from database or LinkedIn API
    return {
        "name": "John Doe",
        "headline": "AI/ML Engineer",
        "location": "San Francisco, CA",
        "skills": ["Python", "Machine Learning", "LangChain", "LangGraph"],
        "experience": [
            {
                "title": "ML Engineer",
                "company": "TechCorp",
                "duration": "2 years",
                "description": "Built AI-powered applications..."
            }
        ],
        "education": [
            {
                "degree": "BS Computer Science",
                "school": "University of California",
                "year": "2020"
            }
        ]
    }


# ============================================================================
# ADVANCED SEARCH TOOLS
# ============================================================================

@tool
def filter_jobs_by_criteria(
    jobs: List[dict],
    required_skills: List[str] = None,
    exclude_companies: List[str] = None,
    min_salary: int = 0,
    easy_apply_only: bool = False
) -> dict:
    """
    Filter job listings based on advanced criteria.
    
    Args:
        jobs: List of job dictionaries to filter
        required_skills: Must have these skills in description
        exclude_companies: Companies to exclude from results
        min_salary: Minimum salary requirement
        easy_apply_only: Only show Easy Apply jobs
    
    Returns:
        Filtered list of jobs
    """
    filtered_jobs = jobs.copy()
    
    if easy_apply_only:
        filtered_jobs = [j for j in filtered_jobs if j.get("easy_apply", False)]
    
    if exclude_companies:
        filtered_jobs = [
            j for j in filtered_jobs 
            if j.get("company", "") not in exclude_companies
        ]
    
    # TODO: Implement skill matching and salary filtering
    
    return {
        "success": True,
        "filtered_jobs": filtered_jobs,
        "original_count": len(jobs),
        "filtered_count": len(filtered_jobs)
    }


@tool
def analyze_job_match(job_description: str, user_profile: dict) -> dict:
    """
    Analyze how well a job matches the user's profile.
    
    Args:
        job_description: The job description text
        user_profile: User's profile information
    
    Returns:
        Match analysis with score and recommendations
    """
    # TODO: Use LLM to analyze match quality
    # This would compare job requirements with user's skills and experience
    
    return {
        "match_score": 0.85,  # 0-1 scale
        "matching_skills": ["Python", "Machine Learning"],
        "missing_skills": ["Kubernetes", "AWS"],
        "recommendations": [
            "Your ML experience is a strong match",
            "Consider highlighting your Python projects",
            "Job requires cloud experience - mention any related work"
        ],
        "should_apply": True
    }


# ============================================================================
# APPLICATION TRACKING TOOLS
# ============================================================================

@tool
def get_application_history(limit: int = 10) -> dict:
    """
    Get history of job applications stored in PostgreSQL.

    Args:
        limit: Maximum number of applications to return.

    Returns:
        List of past applications and their current status.
    """

    try:
        applications, total_count = get_applications(limit)

        return {
            "success": True,
            "applications": applications,
            "total_count": total_count,
        }

    except Exception as e:
        return {
            "success": False,
            "applications": [],
            "total_count": 0,
            "error": str(e),
        }


@tool
def track_application_status(job_id: str) -> dict:
    """
    Get the current status of an application stored in PostgreSQL.

    Args:
        job_id: Unique identifier for the job.

    Returns:
        Current application information and status.
    """

    try:
        application = get_application(job_id)

        if not application:
            return {
                "success": False,
                "job_id": job_id,
                "message": "Application not found",
            }

        return {
            "success": True,
            "application": application,
        }

    except Exception as e:
        return {
            "success": False,
            "job_id": job_id,
            "error": str(e),
        }


@tool
def save_job_application(
    job_id: str,
    title: str,
    company: str,
    job_url: str = "",
    status: str = "saved",
    notes: str = "",
) -> dict:
    """
    Save a job application to PostgreSQL.

    Args:
        job_id: Unique job identifier.
        title: Job title.
        company: Company name.
        job_url: URL for the job posting.
        status: Current application status.
        notes: Optional notes.

    Returns:
        Saved application information.
    """

    try:
        application = create_application(
            job_id=job_id,
            title=title,
            company=company,
            job_url=job_url or None,
            status=status,
            notes=notes or None,
        )

        return {
            "success": True,
            "application": application,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

@tool
def update_job_application_status(
    job_id: str,
    status: str,
) -> dict:
    """
    Update the status of an existing application.

    Valid examples:
    saved, applied, recruiter_screen, interview,
    offer, rejected, withdrawn
    """

    allowed_statuses = {
        "saved",
        "applied",
        "under_review",
        "recruiter_screen",
        "interview",
        "offer",
        "rejected",
        "withdrawn",
    }

    if status not in allowed_statuses:
        return {
            "success": False,
            "error": f"Invalid status: {status}",
            "allowed_statuses": sorted(allowed_statuses),
        }

    try:
        application = update_application_status(
            job_id,
            status,
        )

        if not application:
            return {
                "success": False,
                "message": f"No application found for {job_id}",
            }

        return {
            "success": True,
            "application": application,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# ============================================================================
# NETWORKING TOOLS
# ============================================================================

@tool
def find_referrals(company_name: str) -> dict:
    """
    Find connections at a specific company for potential referrals.
    
    Args:
        company_name: Name of the company
    
    Returns:
        List of connections at the company
    """
    # TODO: Use LinkedIn API to find connections
    return {
        "company": company_name,
        "connections": [
            {
                "name": "Jane Smith",
                "title": "Senior Engineer",
                "connection_degree": "2nd",
                "mutual_connections": 3
            }
        ],
        "message": "Consider reaching out for a referral"
    }


# ============================================================================
# RESUME AND COVER LETTER TOOLS
# ============================================================================
llm = ChatAnthropic(
    model="claude-sonnet-5",
    max_tokens=4096
)

@tool
def store_master_resume(
    name: str,
    resume_text: str,
) -> dict:
    """
    Store the user's master resume.

    This resume becomes the source of truth for
    future job-specific resume optimization.
    """

    try:
        resume = save_master_resume(
            name=name,
            resume_text=resume_text,
        )

        return {
            "success": True,
            "resume": resume,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

@tool
def retrieve_master_resume() -> dict:
    """
    Retrieve the user's currently stored master resume.
    """

    try:
        resume = get_master_resume()

        if not resume:
            return {
                "success": False,
                "message": "No master resume has been stored."
            }

        return {
            "success": True,
            "resume": resume,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

@tool
def optimize_resume_for_job(job_id: str) -> dict:
    """
    Optimize the stored master resume for a specific job.

    Loads the master resume and target job description,
    creates a tailored resume, validates factual accuracy,
    and saves the validated optimization.
    """


    try:
        master_resume = get_master_resume()

        print("DEBUG master resume:", master_resume)
        print("DEBUG master resume type:", type(master_resume))
        
        if not master_resume:
            return {
                "success": False,
                "error": "No master resume is stored."
            }

        if not isinstance(master_resume, dict):
            return {
                "success": False,
                "error": (
                    "get_master_resume returned unexpected type: "
                    f"{type(master_resume).__name__}"
                ),
            }

        job = get_job_by_external_id(job_id)

        if job is Ellipsis:
            return {
                "success": False,
                "error": (
                    "get_job_details_by_id returned Ellipsis. "
                    "Replace the '...' placeholder in job_service.py "
                    "with the real job retrieval implementation."
                ),
            }

        if not job:
            return {
                "success": False,
                "error": f"Job '{job_id}' was not found."
            }

        if not isinstance(job, dict):
            return {
                "success": False,
                "error": (
                    "Job lookup returned unexpected type: "
                    f"{type(job).__name__}"
                ),
            }

        job_description = job.get("description")

        if not job_description:
            return {
                "success": False,
                "error": "Job description is missing."
            }

        MAX_ATTEMPTS = 2

        optimization = None
        validation = None

        for attempt in range(MAX_ATTEMPTS):
            optimization = optimize_resume(
                resume_text=master_resume["resume_text"],
                job_description=job_description,
            )

            validation = validate_resume(
                original_resume=master_resume["resume_text"],
                optimized_resume=optimization.optimized_resume,
            )

            if validation.valid:
                break

        if not validation.valid:

            failed_id = save_resume_optimization(
                original_resume=master_resume["resume_text"],
                job_description=job_description,
                optimized_resume=optimization.optimized_resume,
                match_score=optimization.match_score,

                job_id=job_id,
                company=job.get("company"),
                title=job.get("title"),

                validation_passed=False,
                validation_score=validation.confidence_score,
                validation_summary=validation.summary,
                validation_issues_json=json.dumps(
                    [
                        issue.model_dump()
                        for issue in validation.unsupported_claims
                    ]
                ),
            )

            return {
                "success": False,
                "optimization_id": failed_id,
                "validation_failed": True,
                "unsupported_claims": [
                    issue.model_dump()
                    for issue in validation.unsupported_claims
                ],
            }

        validation_issues_json = json.dumps(
            [
                issue.model_dump()
                for issue in validation.unsupported_claims
            ]
        )

        optimization_id = save_resume_optimization(
            original_resume=master_resume["resume_text"],
            job_description=job_description,
            optimized_resume=optimization.optimized_resume,
            match_score=optimization.match_score,
            job_id=job_id,
            company=job.get("company"),
            title=job.get("title"),
            validation_passed=True,
            validation_score=validation.confidence_score,
            validation_summary=validation.summary,
            validation_issues_json=validation_issues_json,
        )

        return {
            "success": True,
            "optimization_id": optimization_id,
            "job_id": job_id,
            "company": job.get("company"),
            "title": job.get("title"),
            "validation_passed": True,
            "validation_score": validation.confidence_score,
            **optimization.model_dump(),
        }

    except Exception as e:
        return {
            "success": False,
            "job_id": job_id,
            "error": str(e),
        }


@tool
def generate_linkedin_message(
    recipient_name: str,
    recipient_title: str,
    purpose: str = "referral"
) -> str:
    """
    Generate a professional LinkedIn message for networking.
    
    Args:
        recipient_name: Name of the person to message
        recipient_title: Their job title
        purpose: Purpose of message (referral, networking, etc.)
    
    Returns:
        Generated message text
    """
    # TODO: Use LLM to generate personalized message
    return f"""
    Hi {recipient_name},
    
    I hope this message finds you well...
    """


# ============================================================================
# INTERVIEW PREPARATION TOOLS
# ============================================================================

@tool
def generate_interview_prep(job_description: str, company_name: str) -> dict:
    """
    Generate interview preparation materials for a job.
    
    Args:
        job_description: The job description
        company_name: Name of the company
    
    Returns:
        Interview preparation guide
    """
    return {
        "common_questions": [
            "Tell me about your experience with AI/ML",
            "How do you handle production model deployment?"
        ],
        "technical_topics": [
            "Machine Learning fundamentals",
            "System design for ML systems",
            "Python coding challenges"
        ],
        "company_research": {
            "about": "Research company background",
            "products": "Understand their products/services",
            "culture": "Review company culture and values"
        }
    }


# ============================================================================
# SALARY NEGOTIATION TOOLS
# ============================================================================

@tool
def research_salary_range(
    job_title: str,
    location: str,
    experience_years: int
) -> dict:
    """
    Research typical salary ranges for a position.
    
    Args:
        job_title: The job title
        location: Job location
        experience_years: Years of experience
    
    Returns:
        Salary range data and negotiation tips
    """
    # TODO: Use salary APIs (Glassdoor, Levels.fyi, etc.)
    return {
        "job_title": job_title,
        "location": location,
        "salary_range": {
            "low": 120000,
            "median": 150000,
            "high": 180000
        },
        "negotiation_tips": [
            "Research company's compensation philosophy",
            "Consider total compensation (equity, bonus)",
            "Be prepared to justify your expectations"
        ]
    }