#!/usr/bin/env python3
"""
One-command pipeline:
  python3 scripts/run_all.py

Steps:
  1. run_backtesting   — fetch Yahoo Finance data → output/backtesting/
  2. generate_report   — compute signals → output/markdown_report/
  3. publish_wordpress — post to WordPress via REST API
  4. build_hugo        — copy MD into Hugo, build static site
  5. git_commit        — git add / commit / push to GitHub
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STEPS = [
    ("Backtesting",  "scripts/run_backtesting.py"),
    ("Report",       "scripts/generate_investment_report.py"),
    ("WordPress",    "scripts/publish_to_wordpress.py"),
    ("Hugo build",   "scripts/build_hugo.py"),
    ("Git publish",  "scripts/git_commit_publish.py"),
]


def run_step(label: str, script: str) -> None:
    print(f"\n{'='*40}")
    print(f"  {label}")
    print(f"{'='*40}")
    subprocess.run(["python3", script], cwd=ROOT, check=True)


if __name__ == "__main__":
    for label, script in STEPS:
        run_step(label, script)
    print("\n✓ All steps completed.")
