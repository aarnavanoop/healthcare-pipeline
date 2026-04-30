from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

class UserCreate(BaseModel):
    """
    Schema for validating incoming registration requests.
    Enforces strict rules on the plain-text password before it ever reaches the database.
    """
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50, 
        description="The user's unique identifier (can be an email or username)."
    )
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128, 
        description="Plain-text password. Must be at least 8 characters."
    )

class UserResponse(BaseModel):
    """
    Schema for returning user data.
    """
    id: UUID
    username: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)