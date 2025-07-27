from typing import TypedDict, List, Any, Optional


class JobSearchState(TypedDict):
  user_id: str
  resume_content: Optional[str]
  job_keywords: List[str]
  job_urls: List[str]
  scraped_results: List[Any]  # List of job posting extraction results
