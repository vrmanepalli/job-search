import re

QUESTION_PATTERNS = {
    "authorized_to_work_us": [
        "authorized to work",
        "legally authorized to work",
        "work authorization",
        "eligible to work",
        "legally eligible to work",
    ],

    "requires_sponsorship": [
        "require sponsorship",
        "requires sponsorship",
        "need sponsorship",
        "visa sponsorship",
        "employment sponsorship",
        "sponsor you",
    ],

    "years_management": [
        "years of management experience",
        "years of leadership experience",
        "management experience",
        "years managing",
        "years leading",
    ],

    "years_software_engineering": [
        "years of software engineering",
        "software engineering experience",
    ],

    "salary_expectation": [
        "salary expectation",
        "salary expectations",
        "desired salary",
        "expected salary",
        "expected compensation",
        "desired compensation",
        "compensation expectation",
    ],

    # Start
    "available_start_date": [
        "available start date",
        "when can you start",
        "earliest start date",
    ],

    "willing_to_relocate": [
        "willing to relocate",
        "open to relocation",
        "relocate for this position",
    ],

    "willing_to_travel": [
        "willing to travel",
        "travel requirement",
    ],

    "remote_preference": [
        "remote work",
        "remote position",
        "work remotely",
        "remote preference",
    ],
}

def extract_experience_skill(
    question: str,
) -> str | None:

    patterns = [
        r"how many years of (.+?) experience",
        r"years of experience (?:do you have )?with (.+?)(?:\?|$)",
    ]

    question_lower = question.lower().strip()

    for pattern in patterns:
        match = re.search(
            pattern,
            question_lower,
        )

        if match:
            return match.group(1).strip()

    return None

def normalize_question(
    question: str,
) -> str | None:

    question_lower  = question.lower().strip()

    for key, patterns in QUESTION_PATTERNS.items():

        for pattern in patterns:

            if pattern in question_lower :
                return key

    # 2. Check dynamic skill-experience questions
    skill = extract_experience_skill(question)

    if skill:
        return f"years_skill:{skill}"

    # 3. Unknown question
    return None