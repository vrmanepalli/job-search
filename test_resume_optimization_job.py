from pprint import pprint

from linkedin_agent.tools import optimize_resume_for_job


result = optimize_resume_for_job.invoke({
    "job_id": "4458293262"
})

pprint(result)