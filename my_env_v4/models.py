from pydantic import BaseModel, Field
from typing import List, Optional


class PublicEmail(BaseModel):
    id: int
    subject: str
    body: str
    priority: str                          # "high" | "medium" | "low"
    domain: str = "work"                   # "work" | "personal"
    due_day: int = 1
    dependency_ids: List[int] = Field(default_factory=list)
    sender: str = ""                       # email address of sender
    sender_role: str = "unknown"           # "manager"|"peer"|"customer"|"vendor"|"internal"|"unknown"
    thread_id: str = ""                    # groups related emails
    urgency_score: float = 0.5            # 0.0 (spam/no urgency) → 1.0 (critical)
    context_clue: str = ""                 # hint visible to agent for hard/ambiguous cases


class Email(PublicEmail):
    # Internal supervision signal — hidden from agent observations
    label: str                             # "work" | "complaint" | "spam"


class Observation(BaseModel):
    emails: List[PublicEmail]
    history: List[str]
    current_day: int = 1
    user_trust: float = 1.0
    world_model: dict = Field(default_factory=dict)


class Action(BaseModel):
    action_type: str                       # "reply" | "ignore" | "escalate"
    email_id: int
    content: Optional[str] = None         # reply/escalation message — quality is scored
    actor: str = "coordinator"            # "coordinator"|"triage_agent"|"planning_agent"|"communication_agent"
    feedback: Optional[float] = None      # self-reported confidence / quality signal


class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict