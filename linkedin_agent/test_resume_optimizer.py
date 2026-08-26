from linkedin_agent.resume_service import optimize_resume


resume = """
Senior Software Engineering Manager with experience
leading release engineering teams, CI/CD automation,
Java, Kubernetes, mobile releases, and developer productivity.
"""

job_description = """
We are looking for a Director of Engineering with experience
leading distributed engineering teams, cloud platforms,
Kubernetes, CI/CD, developer productivity, and technical strategy.
"""


result = optimize_resume(
    resume_text=resume,
    job_description=job_description,
)


print("MATCH SCORE")
print(result.match_score)

print("\nMATCHED")
print(result.matched_keywords)

print("\nMISSING")
print(result.missing_keywords)

print("\nRECOMMENDATIONS")
for recommendation in result.recommendations:
    print("-", recommendation)

print("\nOPTIMIZED RESUME")
print(result.optimized_resume)