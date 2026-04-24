# 2-Minute Demo Script

## 0:00 to 0:20 Problem
"We built Email OpenEnv to evaluate realistic assistant behavior, not one-step classification. The agent must process work and personal messages, prioritize correctly, and avoid harmful actions over multiple steps."

## 0:20 to 0:50 Environment
"Our environment supports easy, medium, hard, and round2. Round2 introduces mixed work/personal tasks, due days, and dependencies across a 14-day simulated horizon."

## 0:50 to 1:20 Agent Design
"We model coordinator-led multi-agent behavior: triage, planning, and communication roles. The environment tracks world state and user trust, and rewards balanced handling across domains."

## 1:20 to 1:45 Learning + Metrics
"We provide a minimal Colab-ready HF TRL script and report before/after reward metrics. This gives measurable evidence of policy improvement, not just qualitative claims."

## 1:45 to 2:00 Closing
"Email OpenEnv aligns with multi-agent interaction, long-horizon planning, world modeling, and self-improvement. It is OpenEnv-compliant, deployable, and benchmarkable."
