from typing import List, Optional
from pydantic import BaseModel, Field


class JobPosting(BaseModel):
  """Represents a single job posting with structured data."""

  id: Optional[int] = Field(
    default=None, description="The id of the job posting database"
  )
  title: str = Field(description="The title of the job posting")
  company: Optional[str] = Field(default="", description="The name of the company")
  location: Optional[str] = Field(default="", description="The location of the job")
  description: Optional[str] = Field(default="", description="A description of the job")
  posted_at: Optional[str] = Field(
    default=None, description="The date and time the job was posted. e.g. 2025-07-20"
  )
  url: Optional[str] = Field(default="", description="The URL to the job posting")
  content_doc: Optional[str] = Field(
    default=None, description="Path to the file containing the job description text"
  )


class JobPostingList(BaseModel):
  """A list of job postings."""

  jobs: List[JobPosting] = Field(
      default_factory=list,
      description="A list of job posting objects."
  )

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
