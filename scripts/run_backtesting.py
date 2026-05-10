#!/usr/bin/env python3
"""
Fetches quarterly financial data from Yahoo Finance for each company in config/companies/,
computes signal values (revenue_qoq, gross_margin_delta) over the past 5 years,
and writes results to output/backtesting/{ticker}_5y_impact_contributions.csv.
"""
from pathlib import Path

import pandas as pd
import yaml
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config" / "companies"
OUTPUT_DIR = ROOT / "output" / "backtesting"


def load_tickers() -> list[str]:
    return sorted(p.stem for p in CONFIG_DIR.glob("*.yaml"))


def fetch_quarterly_financials(ticker: str) -> pd.DataFrame:
    stock = yf.Ticker(ticker)

    income = stock.quarterly_income_stmt
    if income is None or income.empty:
        print(f"  [{ticker}] No income statement data.")
        return pd.DataFrame()

    # Revenue row
    revenue_row = None
    for candidate in ["Total Revenue", "Revenue"]:
        if candidate in income.index:
            revenue_row = income.loc[candidate]
            break

    # Gross profit row
    gp_row = None
    for candidate in ["Gross Profit"]:
        if candidate in income.index:
            gp_row = income.loc[candidate]
            break

    if revenue_row is None or gp_row is None:
        print(f"  [{ticker}] Missing revenue or gross profit rows.")
        return pd.DataFrame()

    df = pd.DataFrame({
        "revenue": revenue_row,
        "gross_profit": gp_row,
    }).sort_index()

    df["gross_margin"] = df["gross_profit"] / df["revenue"]
    df["revenue_qoq"] = df["revenue"].pct_change()
    df["gross_margin_delta"] = df["gross_margin"].diff()

    # Keep last 5 years (20 quarters)
    df = df.tail(20).dropna(subset=["revenue_qoq", "gross_margin_delta"])
    return df


def to_period_label(ts: pd.Timestamp) -> str:
    q = (ts.month - 1) // 3 + 1
    return f"{ts.year}Q{q}"


def run_backtesting(ticker: str) -> None:
    print(f"  [{ticker}] Fetching data...")
    df = fetch_quarterly_financials(ticker)
    if df.empty:
        return

    rows = []
    for ts, row in df.iterrows():
        rows.append({
            "period": to_period_label(ts),
            "ticker": ticker,
            "revenue_qoq": round(row["revenue_qoq"], 6),
            "gross_margin_delta": round(row["gross_margin_delta"], 6),
        })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{ticker.lower()}_5y_impact_contributions.csv"
    out_df = pd.DataFrame(rows)
    out_df.to_csv(out_path, index=False)
    print(f"  [{ticker}] Written: {out_path.relative_to(ROOT)}")


def main():
    tickers = load_tickers()
    if not tickers:
        print("No company configs found.")
        return

    print("Backtesting...")
    for ticker in tickers:
        run_backtesting(ticker)


if __name__ == "__main__":
    main()
