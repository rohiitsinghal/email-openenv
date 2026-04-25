from pydantic import BaseModel, Field
from typing import List, Optional

class PublicEmail(BaseModel):
    id: int
    subject: str
    body: str
    priority: str
    domain: str = "work"
    due_day: int = 1
    dependency_ids: List[int] = Field(default_factory=list)


class Email(PublicEmail):
    # Internal supervision signal used by the grader only.
    label: str

class Observation(BaseModel):
    emails: List[PublicEmail]
    history: List[str]
    current_day: int = 1
    user_trust: float = 1.0
    world_model: dict = Field(default_factory=dict)

class Action(BaseModel):
    action_type: str  # reply / ignore / escalate
    email_id: int
    content: Optional[str] = None
    actor: str = "coordinator"
    feedback: Optional[float] = None

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict