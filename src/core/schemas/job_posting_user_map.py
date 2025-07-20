from pydantic import BaseModel, Field


class JobPostingUserMap(BaseModel):
  """Represents a mapping between a user and a job posting."""

  user_id: int = Field(description="The ID of the user")
  job_posting_id: int = Field(description="The ID of the job posting")
