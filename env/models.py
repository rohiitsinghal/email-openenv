from pydantic import BaseModel
from typing import List, Optional

class Email(BaseModel):
    id: int
    subject: str
    body: str
    label: str  # ground truth

class Observation(BaseModel):
    emails: List[Email]
    history: List[str]

class Action(BaseModel):
    action_type: str  # classify | extract | reply
    email_id: int
    content: Optional[str]

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict