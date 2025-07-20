from typing import Optional
from pydantic import BaseModel, Field


class User(BaseModel):
  """Represents a user with basic information."""

  id: str = Field(default=None, description="The unique identifier of the user")
  name: str = Field(description="The name of the user")
  short_description: Optional[str] = Field(
    default=None, description="A brief description of the user"
  )
  created_at: Optional[str] = Field(
    default=None, description="The date and time the user was created, e.g., 2025-07-20"
  )
