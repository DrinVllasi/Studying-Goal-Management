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

class SubjectCreate(BaseModel):
    name: str

class HabitCreate(BaseModel):
    user_id: int
    name: str

class HabitOut(BaseModel):
    id: int
    user_id: int
    name: str
    streak: int = 0
    last_done: Optional[str] = None

class GoalCreate(BaseModel):
    user_id: int
    title: str
    category: Optional[str] = None
    progress: int = 0
    target_date: Optional[str] = None

class GoalOut(BaseModel):
    id: int
    user_id: int
    title: str
    category: Optional[str] = None
    progress: int
    target_date: Optional[str] = None

class GoalCreate(BaseModel):
    user_id: int
    title: str
    category: Optional[str] = None
    progress: int = 0
    target_date: Optional[str] = None
    type: str = "milestone"  # "milestone" or "daily"

class GoalOut(BaseModel):
    id: int
    user_id: int
    title: str
    category: Optional[str] = None
    progress: int
    target_date: Optional[str] = None
    type: str
    streak: int = 0
    last_done: Optional[str] = None