from typing import TypedDict, List, Optional

from src.core.schemas.job_posting import JobPosting


class JobSearchState(TypedDict):
  user_id: str
  resume_content: Optional[str]
  job_keywords: List[str]
  job_urls: List[str]
  scraped_results: List[JobPosting]
