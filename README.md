
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
- 🧠 Make optimal decisions (reply / ignore / escalate) under ambiguity
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

- ✅ Multiple task distributions (easy / medium / hard)
- ✅ Ambiguous and deceptive scenarios (e.g., urgent-looking spam, low-priority complaints)
- ✅ Non-binary reward shaping (best / partial / harmful actions)

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
| Best action (optimal) | +1.0 |
| Good but suboptimal | +0.3 to +0.8 |
| Incorrect decision | -0.1 |
| Harmful decision | -0.5 to -0.7 |
| Step penalty | -0.02 |
| Priority violation | -0.3 |
| Duplicate action | -0.2 |
| Completion bonus | +0.5 |

✔ Uses **non-binary grading** to evaluate decision quality  
✔ Rewards reasoning under ambiguity, not just correctness

---

### 🧠 Stateful Decision Tracking
- Maintains history of actions
- Prevents duplicate processing
- Enables reasoning over past steps

---

### 🧩 Multi-Task Evaluation
- Supports 3 distinct task distributions
- Each task has its own grading behavior
- Ensures agents generalize across scenarios

---

### 🛡 Robust & Deterministic
- Fully deterministic grading
- No randomness in evaluation
- Offline-compatible (no API dependency required)

---

## 🔌 API Endpoints

### 🔄 Reset Environment
```
POST /reset?level=easy|medium|hard|round2
```

### ▶️ Take Step
```
POST /step
```
Example:
```json
{
  "action_type": "reply",
  "email_id": 1,
  "content": "Acknowledged. We are handling this now.",
  "actor": "coordinator",
  "feedback": 0.0
}
```

### 📊 Get State
```
GET /state
```

---

## 🎮 Difficulty Levels

| Level | Description |
|------|------------|
| Easy | Clear signals (spam vs work vs complaint) |
| Medium | Mixed intent + moderate ambiguity |
| Hard | Deceptive and ambiguous cases requiring judgment |
| Round2 | Mixed work + personal long-horizon scenarios with dependencies |

Run Round 2 mode:
```bash
curl -X POST "http://localhost:8000/reset?level=round2"
python inference.py
```

Round 2 alignment implemented in code:
- Multi-agent interaction signal via `actor`
- Long-horizon timeline via `current_day` and due-day handling
- World modeling via `domain`, `user_trust`, and `world_model`
- Self-improvement hook via action `feedback` and adaptive baseline policy

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
✔ Typed models (Pydantic)  
✔ Deterministic grading  
✔ Dockerized execution  
✔ openenv.yaml defined  

---

## 🏆 Hackathon Submission Pack

This repository includes the core artifacts to maximize judging score:

- Training script (HF TRL, Colab-ready): `training/minimal_trl_colab.py`
- Colab quickstart steps: `training/COLAB_QUICKSTART.md`
- 2-minute blog/video narrative: `BLOG_VIDEO_SCRIPT_2MIN.md`
- Winning checklist and score strategy: `HACKATHON_WINNING_CHECKLIST.md`

### Recommended submission flow

1. Deploy app to Hugging Face Spaces (OpenEnv compliant endpoint).
2. Run baseline metrics on `easy`, `medium`, `hard`, `round2`.
3. Run Colab training script and export reward summary.
4. Publish blog/video using the 2-minute script.
5. Attach links and metrics artifact in final submission.

### Reward Improvement Evidence

Run:

```bash
python training/evaluate_rewards.py
```

This writes:

- `training/reward_improvement.json`

Current sample output in this repo shows a positive average delta between a naive baseline policy and adaptive policy.

---

## 💡 What Makes This Unique

This is **NOT just classification**.

It evaluates:
- 🧠 Decision order
- ⚡ Priority handling
- 🔁 Multi-step reasoning
- 📊 Workflow correctness
- 🎭 Tests decision quality under ambiguity and conflicting signals

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