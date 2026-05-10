#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent

MARKDOWN_DIR = ROOT / "output" / "markdown_report"


def run_cmd(cmd: str):
    print(f"Run: {cmd}")
    subprocess.run(cmd.split(), cwd=ROOT, check=True)


if __name__ == "__main__":
    run_cmd("git add .")
    run_cmd("git commit -m 'Automated investment reports update'")
    run_cmd("git push origin main")