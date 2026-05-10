#!/usr/bin/env python3
"""
簡易「流程驗證腳本」
用於檢查：
1. Markdown 是否產生
2. WordPress 是否發佈成功（可自行加入 API 檢查）
3. Git 有沒有 commit 且沒有 uncommitted changes
"""
from pathlib import Path
import subprocess
import sys
import time


def check_markdown():
    """檢查 Markdown 是否產生"""
    root = Path(__file__).resolve().parent.parent
    md_dir = root / "output" / "markdown_report"
    target_md = md_dir / "TSM_2025Q3_investment_report.md"

    print("=== 1. 檢查 Markdown 是否產生 ===")
    if not md_dir.exists():
        print(f"❌ 資料夾 {md_dir} 不存在")
        return False

    if not target_md.exists():
        print(f"❌ Markdown 檔案不存在：{target_md}")
        return False

    print(f"✅ Markdown 檔案存在：{target_md}")
    print(f"大小：{target_md.stat().st_size} bytes")
    return True


def check_wordpress_post(post_title="TSM 投研報告"):
    """檢查 WordPress 最新文章是否包含指定標題"""
    import subprocess
    import requests

    print(f"=== 2. 檢查 WordPress 是否發佈成功（搜尋標題：'{post_title}'）===")

    WP_BASE = "https://iro.langstalk.pro"
    WP_USERNAME = "ClaudeCode"

    result = subprocess.run(
        ["security", "find-generic-password", "-a", WP_USERNAME, "-s", "wp-app-password", "-w"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("❌ 無法從 Keychain 取得 WordPress 密碼")
        return False

    auth = (WP_USERNAME, result.stdout.strip())
    try:
        r = requests.get(
            f"{WP_BASE}/wp-json/wp/v2/posts",
            auth=auth,
            params={"search": post_title, "per_page": 1, "status": "publish"},
            timeout=10,
        )
        r.raise_for_status()
        posts = r.json()
        if posts:
            post = posts[0]
            print(f"✅ WordPress 文章已發佈：{post['title']['rendered']}（ID: {post['id']}）")
            print(f"   網址：{post['link']}")
            return True
        print(f"❌ 未找到已發佈文章：{post_title}")
        return False
    except Exception as e:
        print(f"❌ WordPress API 連線失敗：{e}")
        return False


def check_git_status():
    """檢查 git 目錄是否有 commit 且沒有 uncommitted changes"""
    root = Path(__file__).resolve().parent.parent
    git_path = root

    print("=== 3. 檢查 Git 狀態 ===")
    print(f"檢查目錄：{git_path}")

    if not (git_path / ".git").exists():
        print("❌ 該目錄不是 Git 倉庫")
        return False

    try:
        # 檢查是否有 uncommitted changes
        status_short = subprocess.check_output(
            ["git", "-C", str(git_path), "status", "--short"],
            text=True,
            stderr=subprocess.STDOUT,
        )
        if status_short.strip():
            print("❌ 有未提交的變更：")
            print(status_short)
            return False
        else:
            print("✅ 沒有未提交的變更")

        # 檢查目前 commit SHA
        commit_sha = subprocess.check_output(
            ["git", "-C", str(git_path), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
        print(f"HEAD commit: {commit_sha[:8]}")

        # 檢查是否已推上遠端（ahead / behind）
        short_status = subprocess.check_output(
            ["git", "-C", str(git_path), "status", "-sb"],
            text=True,
            stderr=subprocess.STDOUT,
        )
        if "ahead" in short_status:
            print("⚠️  有 commits 尚未 push 到遠端")
        elif "behind" in short_status:
            print("⚠️  遠端有更新，本地尚未 pull")
        else:
            print("✅ git 狀態正常：沒有 uncommitted changes，且已與遠端同步")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Git 執行錯誤：{e.stderr}")
        return False


def main():
    print("🔍 開始檢查 run_all 流程是否成功")
    print("-" * 50)

    ok_markdown = check_markdown()
    ok_wordpress = check_wordpress_post()
    ok_git = check_git_status()

    print("-" * 50)
    print("📋 總結：")
    if ok_markdown and ok_wordpress and ok_git:
        print("✅ 全部檢查通過：Markdown、WordPress、Git 都正常")
        sys.exit(0)
    else:
        print("❌ 有部分檢查未通過，請依上文提示調整")
        sys.exit(1)


if __name__ == "__main__":
    main()