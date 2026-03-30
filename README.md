#  Email Triage OpenEnv
###  Priority-Aware AI Decision Environment

 Live Demo: https://rsthepro-email-openenv.hf.space/docs

---

## Overview
This project implements a realistic email triage environment following the OpenEnv specification.

Agents must:
- Classify emails (spam / complaint / work)
- Extract useful information
- Generate replies
- Handle priority-based decision making

---

##  Why this matters
Real-world systems are NOT simple classification tasks.

Agents must:
- Handle urgent emails first 
- Avoid duplicate actions 
- Maintain workflow correctness 
- Make sequential decisions 

---

##  Key Features

###  Real-world simulation
- Multi-step workflow
- Stateful environment
- History tracking

---

###  Priority-based decision making
Emails have:
- high
- medium
- low

Rules:
- Ignoring high-priority emails gives penalty
- Low-priority emails cannot complete before high-priority

---

###  Reward System

| Action | Reward |
|--------|--------|
| Correct classification | +1 |
| Wrong classification | -0.1 |
| Step penalty | -0.02 |
| Priority violation | -0.3 |
| Repeat action | -0.2 |
| Completion bonus | +0.5 |

---

###  Robust Design
- No duplicate processing
- Deterministic grading
- Anti-cheat logic
- Workflow enforcement

---

##  API Endpoints

### Reset
POST /reset?level=easy|medium|hard

### Step
POST /step

Example:
{
  "action_type": "classify",
  "email_id": 1,
  "content": "complaint"
}

### State
GET /state

### Tasks
GET /tasks

### Grader
POST /grader

---

##  Difficulty Levels

### Easy
Basic classification

### Medium
Mixed intent emails

### Hard
Priority + decision making

---

##  Baseline Agent

Run:
python baseline/run_baseline.py

---

##  Docker Setup

Build:
docker build -t email-env .

Run:
docker run -p 8000:8000 email-env

---

##  Project Structure

env/
email_env.py
models.py
tasks.py
grader.py

baseline/
  run_baseline.py

app.py            # FastAPI server
Dockerfile
openenv.yaml
README.md

⸻

🧩 OpenEnv Compliance
	•	step() / reset() / state() implemented
	•	Typed models used
	•	Deterministic graders
	•	Dockerized
	•	openenv.yaml included

⸻

💡 What makes this unique

This is NOT just classification.

It evaluates:
- Decision order
- Priority handling
- Workflow correctness

---

##  Use Cases
- Email assistants
- Customer support AI
- RL benchmarking
- Agent evaluation

---

##  Future Scope
- Email threads
- Multi-agent systems
- Time-based penalties

---

##  Conclusion
A realistic environment for evaluating intelligent agents in real-world workflows.

It tests not just correctness, but decision-making.