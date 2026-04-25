# Benchmark Results — Email Triage OpenEnv

Live endpoint: https://rsthepro-email-openenv.hf.space/benchmark

---

## Agent Scores by Difficulty Level

| Level | Emails | Total Reward | Avg Reward/Email |
|-------|--------|-------------|-----------------|
| Easy | 4 | 1.92 | 0.48 |
| Medium | 5 | 3.90 | 0.78 |
| Hard | 6 | 5.38 | 0.90 |
| Round2 | 7 | 7.89 | 1.13 |

---

## Per-Email Trace

### Easy
```
[work  ] [medium] → reply    | reward: +0.980 | total: +0.980
[work  ] [medium] → reply    | reward: +0.980 | total: +1.960
[spam  ] [low   ] → ignore   | reward: -0.020 | total: +1.940
[spam  ] [low   ] → ignore   | reward: -0.020 | total: +1.920

Episode total_reward = 1.920
```

### Medium
```
[complaint] [high] → reply   | reward: +0.980 | total: +0.980
[complaint] [high] → reply   | reward: +0.980 | total: +1.960
[work     ] [low ] → reply   | reward: +0.980 | total: +2.940
[work     ] [low ] → reply   | reward: +0.980 | total: +3.920
[spam     ] [low ] → ignore  | reward: -0.020 | total: +3.900

Episode total_reward = 3.900
```

### Hard
```
[complaint] [high  ] → escalate | reward: +0.980 | total: +0.980
[work     ] [high  ] → reply    | reward: +0.780 | total: +1.760
[complaint] [medium] → escalate | reward: +0.980 | total: +2.740
[work     ] [medium] → reply    | reward: +0.780 | total: +3.520
[spam     ] [low   ] → ignore   | reward: +0.680 | total: +4.200
[spam     ] [low   ] → ignore   | reward: +1.180 | total: +5.380

Episode total_reward = 5.380
```

### Round2 (Long-Horizon)
```
[complaint] [high  ] → escalate | reward: +1.030 | total: +1.030
[work     ] [high  ] → reply    | reward: +0.930 | total: +1.960
[work     ] [high  ] → reply    | reward: +1.030 | total: +2.990
[work     ] [high  ] → reply    | reward: +1.130 | total: +4.120
[work     ] [medium] → reply    | reward: +1.063 | total: +5.183
[work     ] [medium] → reply    | reward: +1.030 | total: +6.213
[spam     ] [low   ] → ignore   | reward: +1.680 | total: +7.893

Episode total_reward = 7.893
```

---

## Reward Improvement Over Naive Baseline

| Agent | Avg Reward |
|-------|-----------|
| Naive baseline (generic replies) | 1.69 |
| Adaptive agent (label-aware) | 2.62 |
| **Delta** | **+0.93 (+55%)** |

---

## How the Agent Works

The baseline agent uses a two-stage pipeline:

**Stage 1 — Triage Agent** classifies each email:
- `spam` → ignore
- `complaint` → escalate (hard/round2), reply (easy/medium)
- `work` → reply
- `high priority` → never ignore

**Stage 2 — Communication Agent** generates keyword-rich content matched to the grader:
- Complaints: `sorry`, `apologize`, `refund`, `process`
- Work: `meeting`, `schedule`, `confirm`

A **coordinator** sorts all emails by priority before processing — high priority first, spam last.

---

## Reward System Summary

| Action | Outcome | Reward |
|--------|---------|--------|
| Optimal action | e.g. escalate complaint on hard | +1.0 |
| Good but suboptimal | e.g. reply instead of escalate | +0.5 |
| Wrong action | e.g. ignore a work email | +0.3 |
| Harmful action | e.g. reply to spam | -0.5 |
| Ignore high priority | — | -0.7 |
| Duplicate action | — | -0.2 |
| Step penalty | per step | -0.02 |
| Completion bonus | all emails processed | +0.5 |

---

## Reproduce Results

```bash
git clone https://github.com/rohiitsinghal/email-openenv
cd email-openenv
pip install -r requirements.txt
python main.py

# new terminal
python inference.py
```

Or against the live endpoint:
```bash
export BASE_URL=https://rsthepro-email-openenv.hf.space
python inference.py
```