from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from src.core.llm.providers import get_chat_model
from src.core.services.job_analysis.workflow import run_job_analysis
from src.core.services.job_search.workflow import run_job_search_workflow
from src.core.services.resume_maker.workflow import run_resume_maker


def create_job_finding_agent(user_id: str = ""):
  """Creates the job finding agent."""

  @tool
  async def job_analysis():
    """Analyzes a job posting against a user's resume to determine fit."""
    return await run_job_analysis(user_id=user_id)

  @tool
  async def job_search():
    """Searches for job postings based on a user's resume."""
    return await run_job_search_workflow(user_id)

  @tool
  async def resume_maker(job_target: str = ""):
    """Creates a resume based on a user's portfolio and a target job."""
    return await run_resume_maker(job_target, user_id)

  # Define the tools for the agent
  tools = [job_analysis, job_search, resume_maker]
  llm = get_chat_model()
  return create_react_agent(llm, tools)
