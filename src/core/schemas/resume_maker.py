from typing import List
from pydantic import BaseModel, Field

class ResumeMakerState(BaseModel):
    """State for resume maker workflow."""

    source_files: List[str] = Field(
        default_factory=list, description="List of source file names"
    )
    job_target: str = Field(
        default="", description="Target job/position"
    )
    plan_to_write_resume: str = Field(
        default="", description="Analysis and plan on how to write the resume"
    )
    final_resume: str = Field(
        default="", description="Final generated resume"
    )