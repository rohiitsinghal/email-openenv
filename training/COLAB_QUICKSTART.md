# Colab Quickstart (HF TRL)

Use this to satisfy the hackathon training-script requirement.

## Copy-paste cells for Colab

Run these cells in order inside a fresh Colab notebook.

### Cell 1: Clean and clone the repository

```bash
!rm -rf /content/email-openenv
!git clone https://github.com/rohiitsinghal/email-openenv.git
```

### Cell 2: Move into the repo

```python
%cd /content/email-openenv
```

### Cell 3: Verify you have latest benchmark code

```bash
!git pull
!grep -n "reward_per_email" training/minimal_trl_colab.py
!grep -n "normalized reward per email" training/minimal_trl_colab.py
```

### Cell 4: Install packages

```bash
!pip install -q trl transformers datasets peft accelerate
!pip install -q -r requirements.txt
```

Optional (recommended for faster HF downloads):

```python
import os
os.environ["HF_TOKEN"] = "<YOUR_HF_TOKEN>"
```

### Cell 5: Run the minimal training script

```bash
!python training/minimal_trl_colab.py
```

### Cell 6: Optional legacy heuristic comparison

```bash
!python training/evaluate_rewards.py
```

This writes the heuristic baseline file used by older plots. The main reward comparison plot now prefers `outputs/reward_summary.json` from the training run.

### Cell 7: Generate plot artifacts

```bash
!python training/generate_plots.py
```

### Cell 8: Run multi-seed benchmark (judge-ready table)

```bash
!python training/multiseed_benchmark.py --seeds 5 --start-seed 0
```

### Cell 9: Inspect the output files

```python
import json

with open("training/reward_improvement.json", "r", encoding="utf-8") as f:
	data = json.load(f)

data
```

```bash
!ls -lah outputs training assets
!cat training/judge_summary.md
```

## What to attach in your submission

Attach:
- command output screenshot
- outputs/reward_summary.json
- training/reward_improvement.json
- training/multiseed_benchmark.json
- training/judge_summary.md
- assets/reward_comparison.png
- assets/training_curve.png
- short note on what changed between before and after

## Optional stronger variant

Swap SFT to PPO/DPO in TRL and evaluate with model-generated actions.

## Common Colab mistake

If you see `SyntaxError: invalid syntax`, it usually means a shell command was pasted into a Python cell without `!` or `%`.
