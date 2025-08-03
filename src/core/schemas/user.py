from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
  """Base model for user attributes."""

  name: str = Field(description="The name of the user")
  resume_file: Optional[str] = Field(
    default=None, description="The file path to the user's resume"
  )


class UserCreate(UserBase):
  """Schema for creating a new user."""

  pass


class User(UserBase):
  """Represents a user with full details including a unique identifier."""

  id: str = Field(description="The unique identifier of the user")
  created_at: Optional[str] = Field(
    default=None, description="The date and time the user was created, e.g., 2025-07-20"
  )
