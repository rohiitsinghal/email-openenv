# Benchmark Results — Email Triage OpenEnv

Live endpoint: https://arushi-bassi04-email-openenv.hf.space/benchmark

---

## Training Results (Qwen2-0.5B, SFT on 826 trajectories)

### Training Progress
- Loss: `2.14 → 0.06` (60 steps)
- Token accuracy: `61% → 99%`

### Per-Level Reward Improvement (reward per email)

| Level | Before Training | After Training | Delta |
|-------|----------------|----------------|-------|
| Easy | -0.02 | -0.02 | 0.00 |
| Medium | -0.03 | +0.60 | **+0.63** |
| Hard | -0.175 | +0.325 | **+0.50** |
| Round2 | -0.13 | +0.313 | **+0.44** |

**Average before:** -0.089 | **Average after:** +0.305 | **Delta: +0.394 per email**

---

## Random vs Smart Agent (5 episodes each)

| Level | Random Agent | Smart Agent | Improvement |
|-------|-------------|-------------|-------------|
| Easy | -4.476 | +3.450 | **+7.926** |
| Medium | -4.160 | +5.220 | **+9.380** |
| Hard | -5.550 | +5.500 | **+11.050** |
| Round2 | -5.360 | +4.500 | **+9.860** |

**Average improvement across all levels: +9.55 reward points per episode.**

---

## Smart Agent Per-Email Trace

### Easy (5 emails)
```
[work  ] [medium] [u:0.6] -> reply    | reward: +0.730 | total: +0.730
[work  ] [medium] [u:0.5] -> reply    | reward: +0.730 | total: +1.460
[work  ] [low   ] [u:0.2] -> reply    | reward: +0.730 | total: +2.190
[spam  ] [low   ] [u:0.0] -> ignore   | reward: +0.380 | total: +2.570
[spam  ] [low   ] [u:0.0] -> ignore   | reward: +0.880 | total: +3.450

Episode total_reward = 3.450
```

### Medium (6 emails)
```
[complaint] [high  ] [u:0.9] -> escalate | reward: +0.820 | total: +0.820
[complaint] [high  ] [u:0.9] -> escalate | reward: +1.020 | total: +1.840
[complaint] [high  ] [u:0.9] -> escalate | reward: +1.020 | total: +2.860
[work     ] [low   ] [u:0.1] -> reply    | reward: +0.770 | total: +3.630
[work     ] [low   ] [u:0.1] -> reply    | reward: +0.770 | total: +4.400
[spam     ] [low   ] [u:0.0] -> ignore   | reward: +0.820 | total: +5.220

Episode total_reward = 5.220
```

### Hard (7 emails)
```
[complaint] [high  ] [u:1.0] -> escalate | reward: +1.050 | total: +1.050
[complaint] [high  ] [u:1.0] -> escalate | reward: +1.050 | total: +2.100
[complaint] [high  ] [u:0.9] -> escalate | reward: +1.150 | total: +3.250
[work     ] [high  ] [u:0.8] -> reply    | reward: +0.500 | total: +3.750
[work     ] [medium] [u:0.5] -> reply    | reward: +0.700 | total: +4.450
[work     ] [medium] [u:0.4] -> reply    | reward: +0.700 | total: +5.150
[spam     ] [low   ] [u:0.0] -> ignore   | reward: +0.350 | total: +5.500

Episode total_reward = 5.500
```

### Round2 — Long Horizon (8 emails)
```
[complaint] [high  ] [u:1.0] -> escalate | reward: +1.170 | total: +1.170
[work     ] [high  ] [u:0.9] -> escalate | reward: +0.890 | total: +2.060
[work     ] [high  ] [u:0.9] -> escalate | reward: +0.260 | total: +2.320
[work     ] [high  ] [u:0.8] -> reply    | reward: +0.380 | total: +2.700
[work     ] [high  ] [u:0.8] -> escalate | reward: +0.220 | total: +2.920
[work     ] [medium] [u:0.3] -> reply    | reward: +0.620 | total: +3.540
[work     ] [low   ] [u:0.2] -> reply    | reward: +0.464 | total: +4.004
[spam     ] [low   ] [u:0.0] -> ignore   | reward: +0.476 | total: +4.480

Episode total_reward = 4.500
```

---

## Agent Architecture

Three-stage pipeline:

**1. Planning Agent** — sorts inbox by urgency score and priority, processes dependency emails first, spam last

**2. Triage Agent** — decides action using urgency score, sender role, semantic text:
- `sender_role: unknown` + `urgency_score: 0.0` → `ignore`
- `urgency >= 0.85` or complaint keywords → `escalate`
- Everything else → `reply`

**3. Communication Agent** — generates context-rich replies:
- Complaints: empathy + resolution + time framing
- Work: action verbs + specificity (EOD, deck, spec, Thursday)
- Escalations: routing signals + urgency framing

---

## Reward System

| Action | Outcome | Reward |
|--------|---------|--------|
| Optimal action | e.g. escalate complaint on hard | +1.0 |
| Good but suboptimal | e.g. reply instead of escalate | +0.5 |
| Wrong action | e.g. ignore work email | +0.3 |
| Harmful action | e.g. reply to spam | -0.5 to -1.0 |
| Ignore high priority | — | -0.7 to -1.2 |
| Dependency violation | — | -0.3 |
| Calendar conflict detected | — | +0.15 |
| Duplicate action | — | -0.2 |
| Step penalty | per step | -0.02 to -0.08 |
| Completion bonus | all emails processed | +0.2 to +0.5 |

---

## Reproduce Results

```bash
git clone https://github.com/rohiitsinghal/email-openenv
cd email-openenv
pip install -r requirements.txt
python main.py

# new terminal
python inference.py        # smart agent
python random_agent.py     # random baseline (5 episodes)
```

Or against the live endpoint:
```bash
export BASE_URL=https://arushi-bassi04-email-openenv.hf.space
python inference.py
```