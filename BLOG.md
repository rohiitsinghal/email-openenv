# Building Email Triage OpenEnv: A Multi-Step Decision Environment for AI Agents

## The Problem

Most AI benchmarks test single-step classification. Real email assistants need to do something far harder — prioritize an entire inbox, escalate complaints before they become crises, ignore phishing despite urgent language, resolve dependencies between tasks, and track state across multiple steps.

We built **Email Triage OpenEnv** to evaluate exactly this gap: consequence-aware, multi-step inbox management under partial observability.

---

## The Environment

Email Triage OpenEnv is a fully OpenEnv-compliant multi-step environment with 4 difficulty levels. At each step, an agent chooses `reply`, `ignore`, or `escalate` for an email. The environment is live on HuggingFace Spaces and fully Dockerized.

What makes it different from a classifier benchmark:

- **Actions have consequences** — mishandling a high-priority email spawns a follow-up in the next step
- **Labels are hidden** — the agent only sees subject, body, priority, sender role, and urgency score. It must infer intent, not read a label
- **Reply content is scored semantically** — a generic "Acknowledged" gets penalized. Empathy signals for complaints, specificity for work emails, professional tone for manager-facing replies
- **Dependency ordering matters** — some emails cannot be processed until prerequisites are resolved

### Difficulty Levels

| Level | Emails | What It Tests |
|-------|--------|--------------|
| `easy` | 5 | Clear signals, spam vs work, unambiguous intent |
| `medium` | 6 | Mixed urgency, phishing disguised as security alerts |
| `hard` | 7 | Deceptive signals, polite complaints hiding $4800 billing errors, reply quality strictly scored |
| `round2` | 8 | Long-horizon planning across work and personal domains |

### Round2 — The Hard Mode

Round2 is where the environment gets genuinely complex:

- **14-day simulated timeline** — emails have due days, overdue penalties apply
- **Dependency ordering** — the QBR deck must be prepared before the client review call can be confirmed
- **Sender trust evolution** — trust degrades on bad decisions, improves on good ones
- **Budget tracking** — the world model tracks remaining budget; a Rs.80,000 offsite proposal requires different handling when budget is exhausted
- **Calendar conflict detection** — a parent-teacher meeting at Thursday 4pm conflicts with a client call at Thursday 3pm; the agent must notice and flag this
- **Thread memory** — per-thread action history affects continuity scoring
- **Work/personal balance** — the world model rewards balanced attention across domains

---

## Agent Architecture

Our baseline agent uses a three-stage pipeline:

**1. Planning Agent** — sorts the inbox by urgency score and priority, processes dependency emails first, spam last

**2. Triage Agent** — decides action using urgency score, sender role, and semantic text signals:
- `sender_role: unknown` + `urgency_score: 0.0` → `ignore`
- `urgency >= 0.85` or complaint keywords → `escalate`
- Everything else → `reply`

**3. Communication Agent** — generates context-rich replies matched to grader rubric:
- Complaints: empathy signals + resolution commitment + time framing
- Work: action verbs + specificity (EOD, Thursday, deck, spec)
- Escalations: routing signals + summary + urgency framing

A **coordinator** orchestrates all three and passes feedback signals across steps.

---

## Results

### Random Agent vs Smart Agent

The most direct evidence of improvement:

| Level | Random Agent (avg, 5 runs) | Smart Agent | Improvement |
|-------|---------------------------|-------------|-------------|
| Easy | -4.476 | +3.450 | **+7.926** |
| Medium | -4.160 | +5.220 | **+9.380** |
| Hard | -5.550 | +5.500 | **+11.050** |
| Round2 | -5.360 | +4.500 | **+9.860** |

**Average improvement across all levels: +9.55 reward points per episode.**

The random agent scores deeply negative because it replies to spam, ignores high-priority complaints, and sends generic content that the semantic grader penalizes. The smart agent avoids all of these.

### Training Results (HuggingFace TRL)

- Loss trend: `2.135 → 0.1662`
- Token accuracy: `61.23% → 96.12%`
- Final train loss: `0.3192`
- Avg reward before training: `-0.0912`
- Avg reward after training: `+0.3053`
- Delta: **+0.3965**

---

## Reward System

The grader uses a composable rubric — base action score + content quality score + context bonus:

| Event | Reward |
|-------|--------|
| Optimal action | +1.0 |
| Good but suboptimal | +0.5 |
| Harmful action (reply to spam) | -0.5 to -1.0 |
| Ignore high priority | -0.7 to -1.2 |
| Calendar conflict detected in reply | +0.15 |
| Work/personal balance bonus | up to +0.06 |
| Dependency violation | -0.3 |
| Step penalty | -0.02 to -0.08 |
| Completion bonus | +0.2 to +0.5 |

Non-binary grading means the agent is rewarded for reasoning quality, not just correct action labels.

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
| `openenv.yaml` manifest | ✅ |
| Live HF Space deployment | ✅ |

---

## Try It

**Live environment:** https://arushi-bassi04-email-openenv.hf.space/docs

**Benchmark endpoint:** https://arushi-bassi04-email-openenv.hf.space/benchmark

**Run it yourself:**
```bash
git clone https://github.com/rohiitsinghal/email-openenv
cd email-openenv
pip install -r requirements.txt
python main.py

# new terminal
python inference.py        # smart agent
python random_agent.py     # random baseline
```

**Training notebook:** [Open in Colab](https://colab.research.google.com/drive/1hfHmku08OfkeHoEUBEbJxj3TaxVQoyJp?usp=sharing)

---

## Why This Matters

Email Triage OpenEnv evaluates whether an LLM can reason about consequences, not just classify intent. It is not a toy benchmark — it mirrors the kind of multi-step, stateful, priority-aware decision making that real AI assistants need to master.

The environment is OpenEnv-compliant, live, reproducible, and benchmarkable. The grader is deterministic and semantic. The results are real.

**GitHub:** https://github.com/rohiitsinghal/email-openenv