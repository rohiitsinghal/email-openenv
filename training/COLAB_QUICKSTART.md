# Colab Quickstart (HF TRL)

Use this to satisfy the hackathon training-script requirement.

## 1) Open Colab and clone repo

```bash
git clone <your-repo-url>
cd email-openenv
```

## 2) Install packages

```bash
pip install -q trl transformers datasets peft accelerate
pip install -q -r requirements.txt
```

## 3) Run minimal training

```bash
python training/minimal_trl_colab.py
```

## 4) Share evidence in submission

Attach:
- command output screenshot
- outputs/reward_summary.json
- short note on what changed between before and after

## Optional stronger variant

Swap SFT to PPO/DPO in TRL and evaluate with model-generated actions.
