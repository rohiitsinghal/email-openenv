from pydantic import BaseModel
from typing import List, Dict

class Observation(BaseModel):
    emails: List[Dict]
    history: List[Dict]

class MyEnvV4Action(BaseModel):
    decision: str  # reply / ignore / escalate

class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: dict