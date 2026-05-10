#!/usr/bin/env python3
"""
Reads backtesting CSV from output/backtesting/ and company config from config/companies/,
then writes a Markdown investment report to output/markdown_report/.
"""
import csv
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BACKTESTING_DIR = ROOT / "output" / "backtesting"
CONFIG_DIR = ROOT / "config" / "companies"
OUTPUT_DIR = ROOT / "output" / "markdown_report"


def load_company_config(ticker: str) -> dict:
    path = CONFIG_DIR / f"{ticker}.yaml"
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def load_backtesting_rows(ticker: str) -> list[dict]:
    rows = []
    for csv_file in BACKTESTING_DIR.glob("*.csv"):
        with open(csv_file, newline="") as f:
            for row in csv.DictReader(f):
                if row.get("ticker") == ticker:
                    rows.append(row)
    return rows


def compute_score(row: dict, weights: dict) -> float:
    score = 0.0
    for signal, weight in weights.items():
        try:
            score += float(row.get(signal, 0)) * weight
        except (ValueError, TypeError):
            pass
    return score


def format_signal_table(row: dict, weights: dict) -> str:
    lines = [
        "| 指標 | 數值 | 權重 | 貢獻 |",
        "|------|------|------|------|",
    ]
    for signal, weight in weights.items():
        try:
            value = float(row.get(signal, 0))
        except (ValueError, TypeError):
            value = 0.0
        contribution = value * weight
        lines.append(f"| {signal} | {value:+.4f} | {weight} | {contribution:+.4f} |")
    return "\n".join(lines)


def generate_report(ticker: str) -> str:
    config = load_company_config(ticker)
    weights: dict = config.get("financial_weights", {})
    rows = load_backtesting_rows(ticker)

    if not rows:
        return ""

    sections = [
        f"# {ticker} 投資研究報告",
        f"**產生時間**：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    for row in sorted(rows, key=lambda r: r.get("period", "")):
        period = row.get("period", "N/A")
        score = compute_score(row, weights)

        if score > 0:
            signal_summary = "偏多"
        elif score < 0:
            signal_summary = "偏空"
        else:
            signal_summary = "中性"

        sections += [
            f"## {period}",
            f"**綜合評分**：{score:+.4f}　**訊號方向**：{signal_summary}",
            "",
            "### 指標貢獻明細",
            format_signal_table(row, weights),
            "",
        ]

    return "\n".join(sections)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tickers = {p.stem for p in CONFIG_DIR.glob("*.yaml")}
    if not tickers:
        print("No company configs found.")
        return

    for ticker in sorted(tickers):
        md = generate_report(ticker)
        if not md:
            print(f"No backtesting data for {ticker}, skipping.")
            continue
        out_path = OUTPUT_DIR / f"{ticker}_report.md"
        out_path.write_text(md, encoding="utf-8")
        print(f"Report written: {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
