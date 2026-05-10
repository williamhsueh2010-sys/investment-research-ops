#!/usr/bin/env python3
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
    seen = set()
    rows = []
    for csv_file in sorted(BACKTESTING_DIR.glob("*.csv")):
        with open(csv_file, newline="") as f:
            for row in csv.DictReader(f):
                if row.get("ticker") != ticker:
                    continue
                key = (row.get("period"), row.get("ticker"))
                if key in seen:
                    continue
                seen.add(key)
                rows.append(row)
    return rows


def signal_direction(value: float) -> str:
    if value > 0:
        return "偏多 ▲"
    elif value < 0:
        return "偏空 ▼"
    return "中性 —"


def format_signal_table(row: dict, weights: dict) -> str:
    lines = [
        "| 指標 | 數值 | 權重 | 貢獻分數 | 訊號方向 |",
        "|------|-----:|-----:|---------:|:--------:|",
    ]
    for signal, weight in weights.items():
        try:
            value = float(row.get(signal, 0))
        except (ValueError, TypeError):
            value = 0.0
        contribution = value * weight
        lines.append(
            f"| {signal} | {value:+.4f} | {weight} | {contribution:+.4f} | {signal_direction(value)} |"
        )
    return "\n".join(lines)


def compute_score(row: dict, weights: dict) -> float:
    score = 0.0
    for signal, weight in weights.items():
        try:
            score += float(row.get(signal, 0)) * weight
        except (ValueError, TypeError):
            pass
    return score


def generate_reports(ticker: str) -> list[tuple[str, str]]:
    config = load_company_config(ticker)
    weights: dict = config.get("financial_weights", {})
    rows = load_backtesting_rows(ticker)

    if not rows:
        return []

    results = []
    for row in sorted(rows, key=lambda r: r.get("period", "")):
        period = row.get("period", "N/A")
        score = compute_score(row, weights)
        overall = signal_direction(score)

        md = "\n".join([
            f"# {ticker} {period} 投資研究報告",
            f"**產生時間**：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 綜合評分",
            "| 項目 | 數值 |",
            "|------|------|",
            f"| 綜合評分 | {score:+.4f} |",
            f"| 整體訊號 | {overall} |",
            "",
            "## 指標貢獻明細",
            format_signal_table(row, weights),
            "",
        ])
        results.append((period, md))

    return results


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tickers = sorted(p.stem for p in CONFIG_DIR.glob("*.yaml"))
    if not tickers:
        print("No company configs found.")
        return

    for ticker in tickers:
        reports = generate_reports(ticker)
        if not reports:
            print(f"[{ticker}] No backtesting data, skipping.")
            continue
        for period, md in reports:
            out_path = OUTPUT_DIR / f"{ticker}_{period}_investment_report.md"
            out_path.write_text(md, encoding="utf-8")
            print(f"Report written: {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
