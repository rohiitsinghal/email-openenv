# Colab Quickstart (HF TRL)

Use this to satisfy the hackathon training-script requirement.

## Copy-paste cells for Colab

Run these cells in order inside a fresh Colab notebook.

### Cell 1: Clone the repository

```bash
!git clone https://github.com/rohiitsinghal/email-openenv.git
```

### Cell 2: Move into the repo

```python
%cd /content/email-openenv
```

### Cell 3: Install packages

```bash
!pip install -q trl transformers datasets peft accelerate
!pip install -q -r requirements.txt
```

Optional (recommended for faster HF downloads):

```python
import os
os.environ["HF_TOKEN"] = "<YOUR_HF_TOKEN>"
```

### Cell 4: Run the minimal training script

```bash
!python training/minimal_trl_colab.py
```

### Cell 5: Run the reward comparison script

```bash
!python training/evaluate_rewards.py
```

### Cell 6: Generate plot artifacts

```bash
!python training/generate_plots.py
```

### Cell 7: Inspect the output files

```python
import json

with open("training/reward_improvement.json", "r", encoding="utf-8") as f:
	data = json.load(f)

data
```

```bash
!ls -lah outputs training assets
```

## What to attach in your submission

Attach:
- command output screenshot
- outputs/reward_summary.json
- training/reward_improvement.json
- assets/reward_comparison.png
- assets/training_curve.png
- short note on what changed between before and after

## Optional stronger variant

Swap SFT to PPO/DPO in TRL and evaluate with model-generated actions.

## Common Colab mistake

If you see `SyntaxError: invalid syntax`, it usually means a shell command was pasted into a Python cell without `!` or `%`.
