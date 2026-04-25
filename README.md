---
title: Email Triage OpenEnv
emoji: ??
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Email Triage OpenEnv

A multi-step decision environment for evaluating AI agents on real-world email triage tasks.

🔗 **Live Demo:** https://rsthepro-email-openenv.hf.space/docs

---

## What This Is

Most benchmarks test single-step classification. This environment tests **sequential decision-making** — an agent must process an entire inbox, choosing `reply`, `ignore`, or `escalate` for each email while respecting priority order, avoiding duplicates, and managing state across steps.

It is fully OpenEnv-compliant with `reset()`, `step()`, and `state()` endpoints, Dockerized, and live on Hugging Face Spaces.

---

## Benchmark Results

Scores from the included baseline agent (`inference.py`) running against the live environment:

| Level | Total Reward | Emails | Notes |
|-------|-------------|--------|-------|
| Easy   | 1.92 | 4 | Clear spam vs work signals |
| Medium | 3.90 | 5 | Mixed intent, moderate ambiguity |
| Hard   | 5.38 | 6 | Deceptive cases, strict grading |
| Round2 | 7.89 | 7 | Long-horizon, dependencies, trust |

Reward improvement over naive baseline (from `training/reward_improvement.json`):
- Naive baseline avg: `1.69`
- Adaptive agent avg: `2.62`
- Delta: **+0.93**

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/rohiitsinghal/email-openenv
cd email-openenv
pip install -r requirements.txt

# Start the server
python main.py

# Run the agent (new window)
python inference.py
```

Or hit the live endpoint directly:
```bash
curl -X POST "https://rsthepro-email-openenv.hf.space/reset?level=hard"
```

---

## Agent Architecture

The baseline agent uses a two-stage pipeline:

**1. Triage Agent** — classifies each email by label and priority:
- `spam` → ignore
- `complaint` → escalate (hard/round2), reply (easy/medium)
- `work` → reply
- `high priority` → never ignore

**2. Communication Agent** — generates label-aware reply content with keywords that match the grader:
- Complaints: includes `sorry`, `apologize`, `refund`, `process`
- Work: includes `meeting`, `schedule`, `confirm`
- Spam: marks and ignores

A **coordinator** sorts emails by priority before processing — high priority first, spam last — simulating realistic inbox management.

---

## Environment Design

### Reward System

| Action | Outcome | Reward |
|--------|---------|--------|
| Correct action (optimal) | e.g. escalate complaint on hard | +1.0 |
| Good but suboptimal | e.g. reply to complaint instead of escalate | +0.5 |
| Wrong action | e.g. ignore a work email | +0.3 |
| Harmful action | e.g. reply to spam | -0.5 |
| Ignore high priority | — | -0.7 |
| Duplicate action | — | -0.2 |
| Step penalty | per step | -0.02 |
| Completion bonus | all emails done | +0.5 |

### Difficulty Levels

| Level | What it tests |
|-------|--------------|
| `easy` | Clear signals, 2 emails |
| `medium` | Mixed intent, 3 emails |
| `hard` | Deceptive cases, strict label-action matching |
| `round2` | 7 emails, dependencies, day progression, user trust, work/personal balance |

### Round2 Features
- **Day progression** — simulated 14-day horizon, due-day penalties
- **Dependency ordering** — must complete prerequisite emails first
- **User trust** — degrades on bad decisions, improves on good ones
- **World model** — tracks work vs personal action balance
- **Feedback loop** — agent can pass feedback signal for self-improvement

---

## API Endpoints

**Reset environment:**
```
POST /reset?level=easy|medium|hard|round2
```

**Take a step:**
```
POST /step
```
```json
{
  "action_type": "reply",
  "email_id": 1,
  "content": "Confirmed. I will schedule the meeting shortly.",
  "actor": "coordinator",
  "feedback": 0.0
}
```

**Get current state:**
```
GET /state
```

---

## Training Pipeline

Colab-ready TRL training script included:

```bash
# Run in Colab
!python training/minimal_trl_colab.py
!python training/evaluate_rewards.py
!python training/generate_plots.py
```

Outputs:
- `training/reward_improvement.json`
- `outputs/reward_summary.json`
- `assets/reward_comparison.png`
- `assets/training_curve.png`

![Reward Comparison](assets/reward_comparison.png)
![Training Curve](assets/training_curve.png)

---

## OpenEnv Compliance

| Requirement | Status |
|-------------|--------|
| `reset()` endpoint | ✅ |
| `step()` endpoint | ✅ |
| `state()` endpoint | ✅ |
| Typed Pydantic models | ✅ |
| Deterministic grading | ✅ |
| Docker support | ✅ |
| `openenv.yaml` | ✅ |
| Live deployment | ✅ |

---

## Project Structure

```
email-openenv/
├── my_env_v4/
│   ├── env.py        # Environment logic, reward shaping
│   ├── grader.py     # Per-level grading functions
│   ├── models.py     # Pydantic models
│   └── tasks.py      # Email datasets per level
├── server/
│   └── app.py        # FastAPI server
├── training/
│   ├── minimal_trl_colab.py
│   ├── evaluate_rewards.py
│   └── generate_plots.py
├── assets/           # Committed reward plots
├── outputs/          # Benchmark JSON artifacts
├── inference.py      # Baseline two-agent pipeline
├── main.py           # Server entrypoint
├── openenv.yaml      # OpenEnv spec
└── Dockerfile
```

---

## Docker

```bash
docker build -t email-env .
docker run -p 7860:7860 email-env
```
