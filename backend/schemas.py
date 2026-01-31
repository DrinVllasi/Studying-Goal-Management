from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class StudySessionCreate(BaseModel):
    user_id: int
    subject: int
    duration: int
    notes: Optional[str] = None
