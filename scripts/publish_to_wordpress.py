#!/usr/bin/env python3
import os
from pathlib import Path
import markdown2
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "output" / "markdown_report"

WP_URL = os.environ.get("WP_URL", "https://iro.langstalk.pro/")
WP_USERNAME = os.environ.get("WP_USERNAME", "william")
WP_PASSWORD = os.environ.get("WP_PASSWORD", "williaM@6908008")

def read_markdown_file(md_path: Path) -> str:
    with open(md_path, "rt", encoding="utf-8") as f:
        return f.read()


def md_to_html(md_text: str) -> str:
    return markdown2.markdown(md_text)


def publish_to_wordpress(title: str, html_content: str, tags: list, categories: list):
    client = Client(WP_URL, WP_USERNAME, WP_PASSWORD)

    post = WordPressPost()
    post.title = title
    post.content = html_content
    post.post_status = "publish"

    if categories:
        post.terms_names = {
            "category": categories,
        }
    if tags:
        post.terms_names["post_tag"] = tags

    post_id = client.call(NewPost(post))
    print(f"Published post: '{title}' -> ID: {post_id}")
    return post_id


def main():
    md_files = list(REPORTS_DIR.glob("*.md"))
    if not md_files:
        print(f"No .md reports under {REPORTS_DIR}")
        return

    latest_md = max(md_files, key=lambda x: x.stat().st_mtime)
    md_text = read_markdown_file(latest_md)

    filename = latest_md.stem
    parts = filename.split("_")
    ticker = parts[0] if parts else "UNK"
    period = None
    for p in parts:
        if "Q" in p:
            period = p
    period = period or "UnknownPeriod"

    post_title = f"{ticker} {period} 投研報告"
    tags = [ticker, "investing", "valuation", "backtesting"]
    categories = ["投資研究", "制度化投研框架"]

    html_content = md_to_html(md_text)
    publish_to_wordpress(post_title, html_content, tags, categories)


if __name__ == "__main__":
    main()