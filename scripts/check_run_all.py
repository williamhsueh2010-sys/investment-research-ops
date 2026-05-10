#!/usr/bin/env python3
"""
完整流程驗證腳本
檢查：
1. Markdown 是否產生
2. WordPress 是否發布成功（透過 REST API 自動驗證）
3. Git 是否有 commit 且沒有 uncommitted changes
"""
from pathlib import Path
import subprocess
import sys
import requests

WP_BASE = "https://iro.langstalk.pro"
WP_USERNAME = "ClaudeCode"
TARGET_POST_TITLE = "TSM 投研報告"


def _get_app_password() -> str:
    result = subprocess.run(
        ["security", "find-generic-password", "-a", WP_USERNAME, "-s", "wp-app-password", "-w"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    raise RuntimeError("Keychain 中找不到 wp-app-password")


def check_markdown() -> bool:
    """檢查 Markdown 是否產生"""
    root = Path(__file__).resolve().parent.parent
    md_dir = root / "output" / "markdown_report"
    target_md = md_dir / "TSM_2025Q3_investment_report.md"

    print("=== 1. 檢查 Markdown 是否產生 ===")
    if not md_dir.exists():
        print(f"❌ 目錄 {md_dir} 不存在")
        return False

    if not target_md.exists():
        print(f"❌ Markdown 檔案不存在：{target_md}")
        return False

    print(f"✅ Markdown 檔案存在：{target_md}")
    print(f"大小：{target_md.stat().st_size} bytes")
    return True


def check_wordpress_post(post_title: str = TARGET_POST_TITLE) -> bool:
    """透過 WordPress REST API 檢查文章是否已發佈"""
    print(f"=== 2. 檢查 WordPress 是否發佈成功（標題：'{post_title}'）===")

    try:
        auth = (WP_USERNAME, _get_app_password())
        response = requests.get(
            f"{WP_BASE}/wp-json/wp/v2/posts",
            auth=auth,
            params={"search": post_title, "per_page": 1, "status": "publish"},
            timeout=10,
        )
        if response.status_code == 200 and response.json():
            post = response.json()[0]
            print(f"✅ WordPress 文章已發佈：{post['title']['rendered']}（ID: {post['id']}）")
            print(f"   網址：{post['link']}")
            return True
        print(f"❌ 未找到已發佈文章：{post_title}")
        return False
    except Exception as e:
        print(f"❌ WordPress API 連線失敗：{e}")
        return False


def check_git_status() -> bool:
    """检查 git 目录是否有 commit 且没有 uncommitted changes"""
    root = Path(__file__).resolve().parent.parent
    git_path = root

    print("=== 3. 检查 Git 状态 ===")
    print(f"检查目录：{git_path}")

    if not (git_path / ".git").exists():
        print("❌ 该目录不是 Git 仓库")
        return False

    try:
        # 检查是否有未提交的变更
        status_short = subprocess.check_output(
            ["git", "-C", str(git_path), "status", "--short"],
            text=True,
            stderr=subprocess.STDOUT,
        )
        if status_short.strip():
            print("❌ 有未提交的变更：")
            print(status_short)
            return False
        else:
            print("✅ 没有未提交的变更")

        # 检查当前 commit SHA
        commit_sha = subprocess.check_output(
            ["git", "-C", str(git_path), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
        print(f"HEAD commit: {commit_sha[:8]}")

        # 检查是否已推送到远程（ahead / behind）
        short_status = subprocess.check_output(
            ["git", "-C", str(git_path), "status", "-sb"],
            text=True,
            stderr=subprocess.STDOUT,
        )
        if "ahead" in short_status:
            print("⚠️  有 commits 尚未 push 到远程")
        elif "behind" in short_status:
            print("⚠️  远程有更新，本地尚未 pull")
        else:
            print("✅ git 状态正常：没有 uncommitted changes，且已与远程同步")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Git 执行错误：{e.stderr}")
        return False


def main():
    print("🔍 开始检查 run_all 流程是否成功")
    print("-" * 50)

    ok_markdown = check_markdown()
    ok_wordpress = check_wordpress_post()
    ok_git = check_git_status()

    print("-" * 50)
    print("📋 总结：")
    if ok_markdown and ok_wordpress and ok_git:
        print("✅ 全部检查通过：Markdown、WordPress、Git 都正常")
        sys.exit(0)
    else:
        print("❌ 有部分检查未通过，请根据上文提示调整")
        sys.exit(1)


if __name__ == "__main__":
    main()