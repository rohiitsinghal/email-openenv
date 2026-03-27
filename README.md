📧 Email Triage OpenEnv (Priority-Aware AI Environment)

🚀 Overview

This project implements a real-world email triage environment following the OpenEnv specification.

It simulates how AI agents manage incoming emails by:\n
	•	Classifying emails (spam / complaint / work)
	•	Extracting useful information
	•	Generating replies
	•	Handling priority-based decision making

This is NOT a toy problem — it mimics real-world inbox systems.

⸻

🎯 Key Idea

In real systems:
	•	Urgent emails must be handled first
	•	Repeating the same action is not allowed
	•	Agents must take correct decisions in order

This environment enforces all of that.

⸻

🧠 Core Features

✅ Real-world simulation
	•	Multi-step workflow (classify / extract / reply)
	•	Stateful environment with history

⸻

⚡ Priority-based decision making

Each email has:
	•	high
	•	medium
	•	low

Rules:
	•	If high-priority email exists → handling low first gives penalty
	•	Low-priority emails cannot be completed until high ones are done

⸻

🎯 Reward System
	•	Correct classification → +1
	•	Wrong classification → -0.1
	•	Step penalty → -0.02
	•	Ignoring priority → -0.3
	•	Repeating same email → -0.2
	•	Completing all emails → +0.5

This creates a dense and meaningful reward signal

⸻

🔒 Robust design
	•	No duplicate processing
	•	Invalid actions penalized
	•	Deterministic grading
	•	Prevents reward exploitation

⸻

🏗️ API Endpoints

🔹 Reset

POST /reset?level=easy|medium|hard

⸻

🔹 Step

POST /step

Example:
{
“action_type”: “classify”,
“email_id”: 1,
“content”: “complaint”
}

⸻

🔹 State

GET /state

⸻

🔹 Tasks

GET /tasks

⸻

🔹 Grader

POST /grader

⸻

📊 Difficulty Levels

Easy
	•	Simple classification

Medium
	•	Mixed intent emails

Hard
	•	Priority + ambiguity
	•	Requires planning

⸻

🧪 Baseline Agent

Run:
python baseline/run_baseline.py

Example output:
Final Reward: ~1.4

⸻

🐳 Docker Setup

Build:
docker build -t email-env .

Run:
docker run -p 8000:8000 email-env

Open:
http://localhost:8000/docs

⸻

📁 Project Structure

env/
  email_env.py    # core environment
  models.py       # typed schemas
  tasks.py        # task generation
  grader.py       # reward functions

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

It introduces:
	•	Sequential decision-making
	•	Priority constraints
	•	Workflow correctness

Agents must decide WHAT to do and WHEN.

⸻

🏆 Use Cases
	•	Email assistants
	•	Customer support AI
	•	RL benchmarking
	•	Agent evaluation

⸻

🔮 Future Scope
	•	Email threads
	•	Multi-agent coordination
	•	Deadline-based rewards
	•	Human feedback loop

⸻

🙌 Conclusion

This environment provides a realistic setup for evaluating AI agents in real-world workflows.

It tests not just correctness, but decision-making.
