# 台積電（TSMC）完整投研流程操作指南

**適用框架**：制度化投研框架 v1.0  
**標的**：台積電 TSM  
**期間**：2025Q3  
**環境**：VS Code + Claude Code + macOS Terminal

---

## 前置確認

| 項目 | 路徑 | 應有內容 |
|------|------|---------|
| 公司設定 | `config/companies/TSM.yaml` | ticker、financial_weights |
| Backtesting 資料 | `output/backtesting/tsmc_5y_impact_contributions.csv` | period, ticker, revenue_qoq, gross_margin_delta |
| WordPress 密碼 | macOS Keychain | `wp-app-password`（帳號 ClaudeCode） |
| GitHub remote | `git remote -v` | origin → williamhsueh2010-sys/investment-research-ops |

---

## 一鍵執行（標準流程）

在 VS Code Terminal 執行：

```bash
python3 scripts/run_all.py
```

流程依序為：

```
Step 1  Backtesting   →  output/backtesting/tsm_5y_impact_contributions.csv
Step 2  Report        →  output/markdown_report/TSM_2025Q3_investment_report.md
Step 3  WordPress     →  https://iro.langstalk.pro（REST API 發文）
Step 4  Hugo build    →  hugo-investment-reports/public/
Step 5  Git publish   →  github.com/williamhsueh2010-sys/investment-research-ops
```

---

## 分步驟說明

### Step 1｜Backtesting — 從 Yahoo Finance 抓取季度財務資料

```bash
python3 scripts/run_backtesting.py
```

**腳本做什麼**：
- 讀取 `config/companies/*.yaml` 取得 ticker 清單
- 用 `yfinance` 抓取近 4 季的 `quarterly_income_stmt`
- 計算 `revenue_qoq`（營收季增率）與 `gross_margin_delta`（毛利率季變化）
- 輸出到 `output/backtesting/tsm_5y_impact_contributions.csv`

**確認結果**：
```bash
cat output/backtesting/tsm_5y_impact_contributions.csv
```
應看到含 `period, ticker, revenue_qoq, gross_margin_delta` 的多筆資料。

---

### Step 2｜Report — 產生 Markdown 投研報告

```bash
python3 scripts/generate_investment_report.py
```

**腳本做什麼**：
- 讀取 `config/companies/TSM.yaml` 的 `financial_weights`
- 掃描 `output/backtesting/*.csv`，篩選 ticker = TSM 的資料列
- 計算每個指標的貢獻分數，判斷訊號方向（偏多 ▲ / 偏空 ▼ / 中性 —）
- 每一季各產一份 MD：`output/markdown_report/TSM_{PERIOD}_investment_report.md`

**確認結果**：
在 VS Code 的 Explorer 確認 `output/markdown_report/` 下有：
```
TSM_2025Q3_investment_report.md
```
點開，應看到「綜合評分」表格與「指標貢獻明細」表格。

---

### Step 3｜WordPress — 發佈到 WordPress

```bash
python3 scripts/publish_to_wordpress.py
```

**腳本做什麼**：
- 從 macOS Keychain 讀取 Application Password（帳號 ClaudeCode）
- 把最新的 MD 轉成 HTML（含表格支援）
- 透過 WordPress REST API（`/wp-json/wp/v2/posts`）發文
- 自動建立 tag / category（若不存在）

**確認結果**：
Terminal 應顯示：
```
Published: 'TSM 投研報告' -> ID: xxx
```
到 `https://iro.langstalk.pro` 確認文章已出現。

**若失敗**，先確認 Keychain：
```bash
security find-generic-password -a ClaudeCode -s wp-app-password -w
```

---

### Step 4｜Hugo build — 建立靜態網站

```bash
python3 scripts/build_hugo.py
```

**腳本做什麼**：
- 把 `output/markdown_report/*.md` 加上 Hugo front matter，複製到 `hugo-investment-reports/content/posts/`
- 執行 `hugo --minify`，輸出到 `hugo-investment-reports/public/`

**確認結果**：
```bash
ls hugo-investment-reports/public/posts/
```
應看到對應的 HTML 目錄。

---

### Step 5｜Git publish — commit 並推上 GitHub

```bash
python3 scripts/git_commit_publish.py
```

**腳本做什麼**：
- `git add .`
- `git commit -m "Automated investment reports update"`
- `git push origin main`

**確認結果**：
到 `github.com/williamhsueh2010-sys/investment-research-ops/actions`，
確認 GitHub Actions（Hugo deploy）已觸發並完成。

Hugo 網站網址：
```
https://williamhsueh2010-sys.github.io/investment-research-ops/
```

---

## 常見問題排查

| 錯誤訊息 | 原因 | 解法 |
|---------|------|------|
| `ModuleNotFoundError` | 套件未安裝 | `python3 -m pip install -r requirements.txt` |
| `401 Unauthorized` | WP Application Password 錯誤 | 重新產生並更新 Keychain |
| `nothing to commit` | 本次執行無新檔案變動 | 正常，不影響流程 |
| `fatal: 'origin'` | 未設定 GitHub remote | `git remote add origin <url>` |
| Hugo build failed | layouts 缺失 | 確認 `hugo-investment-reports/layouts/` 目錄存在 |

---

## 新增公司的方法

1. 在 `config/companies/` 新增 `{TICKER}.yaml`：
```yaml
ticker: AAPL
financial_weights:
  revenue_qoq: 3.0
  gross_margin_delta: 5.0
```

2. 執行 `python3 scripts/run_all.py`，其餘自動處理。

---

## 檔案結構總覽

```
investment-research-ops/
├── config/
│   └── companies/TSM.yaml          # 權重設定
├── output/
│   ├── backtesting/                # Yahoo Finance 抓取結果
│   └── markdown_report/            # 產生的 MD 報告
├── hugo-investment-reports/        # Hugo 靜態網站
│   ├── content/posts/              # 複製進來的 MD（含 front matter）
│   └── public/                     # build 輸出
├── scripts/
│   ├── run_all.py                  # 一鍵執行
│   ├── run_backtesting.py          # Step 1
│   ├── generate_investment_report.py  # Step 2
│   ├── publish_to_wordpress.py     # Step 3
│   ├── build_hugo.py               # Step 4
│   └── git_commit_publish.py       # Step 5
└── docs/
    └── tsmc_workflow_2025q3.md     # 本文件
```
