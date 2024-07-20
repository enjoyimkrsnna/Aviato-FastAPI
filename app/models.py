from typing import Optional
from enum import Enum
from pydantic import BaseModel
    
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

