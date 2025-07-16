from typing import TypedDict


class JobAnalysisState(TypedDict):
  """Represents the state of the job analysis workflow."""

  job_url: str  # Job posting URL
  job_title: str  # Job posting title
  job_company: str  # Company name
  job_description: str  # Job posting description
  resume_content: str  # Resume content
  detailed_job_info: str  # Detailed job information
  analysis_result: str  # Analysis result as free-form text
  report_content: str  # Report content
