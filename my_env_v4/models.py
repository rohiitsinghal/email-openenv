from pydantic import BaseModel
from typing import List, Optional

class Email(BaseModel):
    id: int
    subject: str
    body: str
    label: str
    priority: str

class Observation(BaseModel):
    emails: List[Email]
    history: List[str]

class Action(BaseModel):
    action_type: str  # reply / ignore / escalate
    email_id: int
    content: Optional[str] = None

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict