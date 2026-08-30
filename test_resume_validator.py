from linkedin_agent.resume_validator import validate_resume


original = """
Software Engineering Manager at ABC Company.

Managed a team of 10 engineers.

Implemented CI/CD automation using Jenkins.
"""


optimized = """
Vice President of Engineering at ABC Company.

Led a global organization of 150 engineers.

Reduced infrastructure spending by $25 million annually.

Implemented CI/CD automation using Jenkins.
"""


result = validate_resume(
    original_resume=original,
    optimized_resume=optimized,
)


print("VALID:", result.valid)
print("CONFIDENCE:", result.confidence_score)
print("SUMMARY:", result.summary)

print("\nUNSUPPORTED CLAIMS:")

for issue in result.unsupported_claims:
    print("Claim:", issue.claim)
    print("Reason:", issue.reason)
    print("Severity:", issue.severity)
    print()