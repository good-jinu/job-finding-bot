from typing import List, Dict
from pydantic import BaseModel, Field


class ResumeSource(BaseModel):
  """Represents a resume source file."""

  filename: str = Field(..., description="Name of the source file")
  content: str = Field(..., description="Content of the source file")
  file_type: str = Field(
    ..., description="Type of the source file (md, txt, json, etc.)"
  )


class ResumeSection(BaseModel):
  """Represents a section of the resume."""

  title: str = Field(..., description="Section title")
  content: str = Field(..., description="Section content")
  order: int = Field(default=0, description="Display order")


class ResumeMakerState(BaseModel):
  """State for resume maker workflow."""

  source_files: List[str] = Field(
    default_factory=list, description="List of source file names"
  )
  source_contents: Dict[str, str] = Field(
    default_factory=dict, description="Contents of source files"
  )
  resume_sections: List[ResumeSection] = Field(
    default_factory=list, description="Resume sections"
  )
  final_resume: str = Field(default="", description="Final generated resume")
  job_target: str = Field(default="", description="Target job/position")
