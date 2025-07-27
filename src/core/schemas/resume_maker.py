from typing import List
from pydantic import BaseModel, Field
from pathlib import Path


class ResumeMakerState(BaseModel):
  """State for resume maker workflow."""

  user_id: str = Field(default="", description="User ID for accessing resume sources")
  source_files: List[Path] = Field(
    default_factory=list, description="List of source file paths"
  )
  job_target: str = Field(default="", description="Target job/position")
  plan_to_write_resume: str = Field(
    default="", description="Analysis and plan on how to write the resume"
  )
  final_resume: str = Field(default="", description="Final generated resume")
