# 🚀 Email Triage OpenEnv
### A Real-World, Multi-Step Decision Environment for Evaluating Intelligent Agents

🔗 Live Demo: https://rsthepro-email-openenv.hf.space/docs

---

## 🧠 Overview
This project implements a **realistic, production-inspired email triage environment** built using the OpenEnv specification.

Unlike toy environments, this system evaluates **sequential decision-making under constraints**, simulating how real AI agents operate in workplace scenarios.

Agents are required to:
- 📩 Understand email content
- ⚡ Prioritize based on urgency
- 🧠 Make correct decisions (reply / ignore / escalate)
- 🔁 Maintain state across multiple steps
- 🚫 Avoid invalid or redundant actions

---

## 🔥 Why This Environment Stands Out

Most benchmarks test *single-step classification*.

This environment tests:
- ✅ Multi-step reasoning
- ✅ Workflow correctness
- ✅ Priority-aware decision making
- ✅ State tracking and memory
- ✅ Robust, deterministic evaluation

👉 It closely mirrors **real-world AI assistant behavior**.

---

## ⚙️ Key Features

### 🧩 Multi-Step Environment
- Processes an entire inbox (not just one email)
- Requires sequential decision-making
- Maintains internal state across steps

---

### ⚡ Priority-Aware Logic
Each email includes an `urgency_hint`:
- 🔴 High → Must be handled first
- 🟡 Medium → Context-dependent
- 🟢 Low → Can be deferred

Violations are penalized → encourages realistic workflows

---

### 🎯 Intelligent Reward System

| Behavior | Reward |
|---------|--------|
| Correct decision | +1 |
| Incorrect decision | -0.1 |
| Step penalty | -0.02 |
| Priority violation | -0.3 |
| Duplicate action | -0.2 |
| Completion bonus | +0.5 |

✔ Designed to reward **reasoning**, not guessing
✔ Encourages optimal decision sequences

---

### 🧠 Stateful Decision Tracking
- Maintains history of actions
- Prevents duplicate processing
- Enables reasoning over past steps

---

### 🛡 Robust & Deterministic
- Fully deterministic grading
- No randomness in evaluation
- Offline-compatible (no API dependency required)

---

## 🔌 API Endpoints

### 🔄 Reset Environment
```
POST /reset?level=easy|medium|hard
```

### ▶️ Take Step
```
POST /step
```
Example:
```json
{
  "action_type": "classify",
  "email_id": 1,
  "content": "complaint"
}
```

### 📊 Get State
```
GET /state
```

### 📋 Get Tasks
```
GET /tasks
```

### 🧪 Evaluate Actions
```
POST /grader
```

---

## 🎮 Difficulty Levels

| Level | Description |
|------|------------|
| Easy | Basic classification |
| Medium | Mixed-intent emails |
| Hard | Priority + workflow constraints |

---

## 🤖 Baseline Agent

Run the baseline agent:
```
python baseline/run_baseline.py
```

---

## 🐳 Docker Setup

### Build
```
docker build -t email-env .
```

### Run
```
docker run email-env
```

---

## 📁 Project Structure

```
my_env_v4/
  env.py
  models.py
  tasks.py
  grader.py

inference.py
Dockerfile
openenv.yaml
README.md
```

---

## ✅ OpenEnv Compliance

✔ step(), reset(), state() implemented  
✔ Async environment support  
✔ Typed models (Pydantic)  
✔ Deterministic grading  
✔ Dockerized execution  
✔ openenv.yaml defined  

---

## 💡 What Makes This Unique

This is **NOT just classification**.

It evaluates:
- 🧠 Decision order
- ⚡ Priority handling
- 🔁 Multi-step reasoning
- 📊 Workflow correctness

👉 Closer to real production AI systems than academic benchmarks.

---

## 🧪 Use Cases

- AI Email Assistants
- Customer Support Automation
- Reinforcement Learning Environments
- Agent Benchmarking Systems

---

## 🔮 Future Scope

- Email threading
- Multi-agent collaboration
- Time-based penalties
- Real-world dataset integration

---

## 🏁 Conclusion

A **realistic, high-signal evaluation environment** for modern AI agents.

Designed to test not just *what* decisions are made — but *how* and *in what order*.

---

⭐ If you found this useful, consider starring the repo!