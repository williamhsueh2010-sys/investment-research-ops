#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def run_script(script_path: str):
    print(f"Running: {script_path}")
    subprocess.run(["python", script_path], cwd=ROOT, check=True)


if __name__ == "__main__":
    t = "用 2025Q3 來示範，實際可參數化"
    backtesting = "output/backtesting/run_backtesting.py"
    report = "scripts/generate_investment_report.py"
    publish = "scripts/publish_to_wordpress.py"
    git_commit = "scripts/git_commit_publish.py"

    run_script(backtesting)
    run_script(report)
    run_script(publish)
    run_script(git_commit)