from pydantic import BaseModel
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str

class StudySessionCreate(BaseModel):
    user_id: int
    subject_id: int
    duration: int
    notes: Optional[str] = None

class StudySessionOut(BaseModel):
    id: int
    user_id: int
    subject_id: int
    duration: int
    notes: Optional[str]
    session_date: str

class Login(BaseModel):
    username: str
    password: str

class Subject(BaseModel):
    id: int
    name: str