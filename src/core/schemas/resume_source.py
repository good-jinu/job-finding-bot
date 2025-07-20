from typing import Optional
from pydantic import BaseModel, Field


class ResumeSource(BaseModel):
  """Represents a resume source file associated with a user."""

  id: Optional[int] = Field(
    default=None,
    description="The unique identifier of the resume source in the database",
  )
  user_id: int = Field(description="The ID of the associated user")
  source_file_name: str = Field(
    description="The name or path of the resume source file"
  )
