# Hackathon Winning Checklist

## Minimum Requirements

- [x] OpenEnv environment implemented
- [x] Dockerized app with API
- [x] Colab-ready minimal training script using HF TRL
- [ ] Hosted and publicly accessible Hugging Face Space
- [ ] Mini blog on Hugging Face or sub-2-minute YouTube video

## Scoring Optimization Plan

### 1) Environment Innovation (40%)
- Demonstrate round2 mixed world (work + personal)
- Show dependency constraints and delayed reward pressure
- Show multi-agent role signal in actions

### 2) Storytelling (30%)
- 90-second script: problem, environment, agents, before/after
- Keep one clean architecture diagram and one reward chart

### 3) Showing Improvement in Rewards (20%)
- Record baseline run rewards across easy/medium/hard/round2
- Run minimal TRL training
- Record post-training rewards with same protocol
- Plot before/after bars

### 4) Reward + Training Pipeline (10%)
- Explain reward terms briefly
- Show reproducible commands
- Include metrics artifact in repo

## Demo Commands

```bash
python main.py
python inference.py
python baseline/run_baseline.py
python training/minimal_trl_colab.py
```
