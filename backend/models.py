from pydantic import BaseModel
from typing import Optional


class StudySession(BaseModel):
    subject_id: int
    duration: int
    notes: Optional[str] = None

    def is_long_session(self) -> bool:
        return self.duration >= 60
