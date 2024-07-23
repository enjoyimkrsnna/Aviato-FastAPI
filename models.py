from typing import Optional
from enum import Enum
from pydantic import BaseModel ,EmailStr, Field

"""
@author Krishna Singh
@date: 20/09/2024

This file defines data models for user management:
- Gender: Enum representing user gender (male or female).
- UserCreateRequest: Model for creating a new user with required fields: username, email, gender, and project_id.
- UserUpdateRequest: Model for updating an existing user's details with optional fields: username, email, gender, and project_id.

"""

class Gender(str, Enum):
    male = 'male'
    female = 'female'

class ProjectID(int, Enum):
    project_1 = 1
    project_2 = 2
    project_3 = 3



class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="User's username.")
    email: EmailStr = Field(..., description="User's email address.")
    gender: Gender = Field(..., description="User's gender.")
    project_id: ProjectID = Field(..., description="Project ID associated with the user.")

    def __init__(self, **data):
        super().__init__(**data)
        self.validate_username()

    def validate_username(self):
        if not self.username.strip():
            raise ValueError("Username cannot be empty or contain only whitespace.")

class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50, description="User's new username.")
    email: Optional[EmailStr] = Field(None, description="User's new email address.")
    gender: Optional[Gender] = Field(None, description="User's new gender.")
    project_id: Optional[ProjectID] = Field(None, description="New project ID associated with the user.")

    def __init__(self, **data):
        super().__init__(**data)
        self.validate_optional_fields()

    def validate_optional_fields(self):
        if self.username is not None and not self.username.strip():
            raise ValueError("Username cannot be empty or contain only whitespace if provided.")
        if self.email is not None and not self.email.strip():
            raise ValueError("Email cannot be empty or contain only whitespace if provided.")