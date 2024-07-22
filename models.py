from typing import Optional
from enum import Enum
from pydantic import BaseModel

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

class UserCreateRequest(BaseModel):
    username: str
    email: str
    gender: Gender
    project_id: int

    
class UserUpdateRequest(BaseModel):
     username : Optional[str] = None
     email: Optional[str] = None
     gender: Optional[Gender] = None
     project_id: Optional[int] = None

