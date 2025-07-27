from typing import List, Optional
from pydantic import BaseModel, Field


class JobPosting(BaseModel):
  """Represents a single job posting with structured data."""

  id: Optional[int] = Field(
    default=None, description="The id of the job posting database"
  )
  title: str = Field(description="The title of the job posting")
  company: str = Field(description="The name of the company")
  location: str = Field(description="The location of the job")
  description: str = Field(description="A description of the job")
  posted_at: Optional[str] = Field(
    description="The date and time the job was posted. e.g. 2025-07-20"
  )
  url: str = Field(description="The URL to the job posting")
  content_doc: Optional[str] = Field(
    default=None, description="Path to the file containing the job description text"
  )


class JobPostingList(BaseModel):
  """A list of job postings."""

  data_list: List[JobPosting]


class JobPostingExtractionState(BaseModel):
  """State for job posting extraction workflow."""

  job_url: str
  job_posting: Optional[JobPosting] = None
  html_content: Optional[str] = None
  markdown_content: Optional[str] = None
  extraction_content: Optional[str] = None
  saved_file_path: Optional[str] = None
  success: bool = False
  error_message: Optional[str] = None
  user_id: Optional[str] = None
  job_posting_id: Optional[int] = None
