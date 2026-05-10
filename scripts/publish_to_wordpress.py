#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

import markdown2
import requests

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "output" / "markdown_report"

WP_BASE = os.environ.get("WP_URL", "https://iro.langstalk.pro")
WP_USERNAME = os.environ.get("WP_USERNAME", "ClaudeCode")


def _get_app_password() -> str:
    if pw := os.environ.get("WP_APP_PASSWORD"):
        return pw
    result = subprocess.run(
        ["security", "find-generic-password", "-a", WP_USERNAME, "-s", "wp-app-password", "-w"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    raise RuntimeError(
        "WordPress Application Password 未設定。\n"
        "請到 WordPress 後台 → 使用者 → 個人資料 → Application Passwords 新增，\n"
        "然後執行：\n"
        "  security add-generic-password -a william -s wp-app-password -w '你的 App Password'"
    )


def _get_or_create_term(session: requests.Session, taxonomy: str, name: str) -> int:
    endpoint = f"{WP_BASE}/wp-json/wp/v2/{taxonomy}"
    r = session.get(endpoint, params={"search": name})
    r.raise_for_status()
    results = r.json()
    for item in results:
        if item["name"] == name:
            return item["id"]
    r = session.post(endpoint, json={"name": name})
    r.raise_for_status()
    return r.json()["id"]


def publish_to_wordpress(title: str, html_content: str, tags: list, categories: list) -> int:
    app_password = _get_app_password()
    session = requests.Session()
    session.auth = (WP_USERNAME, app_password)

    tag_ids = [_get_or_create_term(session, "tags", t) for t in tags]
    cat_ids = [_get_or_create_term(session, "categories", c) for c in categories]

    payload = {
        "title": title,
        "content": html_content,
        "status": "publish",
        "tags": tag_ids,
        "categories": cat_ids,
    }
    r = session.post(f"{WP_BASE}/wp-json/wp/v2/posts", json=payload)
    r.raise_for_status()
    post_id = r.json()["id"]
    print(f"Published: '{title}' -> ID: {post_id}")
    return post_id


def main():
    md_files = list(REPORTS_DIR.glob("*.md"))
    if not md_files:
        print(f"No .md reports under {REPORTS_DIR}")
        return

    latest_md = max(md_files, key=lambda x: x.stat().st_mtime)
    md_text = latest_md.read_text(encoding="utf-8")

    ticker = latest_md.stem.split("_")[0]
    post_title = f"{ticker} 投研報告"
    tags = [ticker, "investing", "valuation", "backtesting"]
    categories = ["投資研究", "制度化投研框架"]

    html_content = markdown2.markdown(md_text, extras=["tables"])
    publish_to_wordpress(post_title, html_content, tags, categories)


if __name__ == "__main__":
    main()
