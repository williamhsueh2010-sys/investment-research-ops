#!/usr/bin/env python3
"""
Copies Markdown reports into Hugo content/posts/ with front matter,
then runs hugo build.
"""
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "output" / "markdown_report"
HUGO_DIR = ROOT / "hugo-investment-reports"
CONTENT_DIR = HUGO_DIR / "content" / "posts"


def add_front_matter(md_text: str, title: str) -> str:
    date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    front_matter = f'---\ntitle: "{title}"\ndate: {date}\n---\n\n'
    # 移除原本的 # 標題行（Hugo 用 front matter title）
    lines = md_text.splitlines()
    body_lines = [l for l in lines if not l.startswith("# ")]
    return front_matter + "\n".join(body_lines)


def main():
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    md_files = list(REPORTS_DIR.glob("*.md"))
    if not md_files:
        print("No .md reports to copy into Hugo.")
        return

    for md_path in md_files:
        ticker = md_path.stem.split("_")[0]
        title = f"{ticker} 投研報告"
        md_text = md_path.read_text(encoding="utf-8")
        content = add_front_matter(md_text, title)
        dest = CONTENT_DIR / md_path.name
        dest.write_text(content, encoding="utf-8")
        print(f"Copied: {dest.relative_to(ROOT)}")

    print("Building Hugo site...")
    result = subprocess.run(
        ["hugo", "--minify"],
        cwd=HUGO_DIR,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Hugo build failed.")
    print("Hugo build complete → hugo-investment-reports/public/")


if __name__ == "__main__":
    main()
