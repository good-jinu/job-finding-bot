from typing import TypedDict


class JobAnalysisState(TypedDict):
  """Represents the state of the job analysis workflow."""

  resume_content: str  # Resume content
  detailed_job_info: str  # Detailed job information
  analysis_result: str  # Analysis result as free-form text
  report_content: str  # Report content
  user_id: str  # User ID of the person whose resume is being analyzed
