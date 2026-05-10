# 台積電（TSMC）完整投研流程操作指南

**標的**：台積電 TSM｜**期間**：2025Q3  
**環境**：VS Code + Claude Code Terminal（macOS）  
**最後更新**：2026-05-10

---

## 一、一鍵執行

在 VS Code 的 Terminal 輸入：

```bash
python3 scripts/run_all.py
```

> 注意：這台機器的 `python` 指向舊版，請務必用 `python3`。

---

## 二、流程與確認清單

### Step 1｜Backtesting — 抓取財務資料

**執行位置**：Terminal（自動由 run_all.py 呼叫）

**確認方式**：
```bash
cat output/backtesting/tsm_5y_impact_contributions.csv
```
應看到含 `period, ticker, revenue_qoq, gross_margin_delta` 的多季資料：
```
period,ticker,revenue_qoq,gross_margin_delta
2025Q1,TSM,-0.033631,-0.002087
2025Q2,TSM,0.112646,-0.001718
2025Q3,TSM,0.060106,0.008358
2025Q4,TSM,0.056744,0.028724
```

---

### Step 2｜Report — 產生 Markdown 投研報告

**執行位置**：Terminal（自動由 run_all.py 呼叫）

**確認方式**：在 VS Code Explorer 展開 `output/markdown_report/`，確認以下檔案存在：

```
output/markdown_report/
├── TSM_2025Q1_investment_report.md
├── TSM_2025Q2_investment_report.md
├── TSM_2025Q3_investment_report.md   ← 主要確認這份
└── TSM_2025Q4_investment_report.md
```

點開 `TSM_2025Q3_investment_report.md`，應看到：

```markdown
# TSM 2025Q3 投資研究報告

## 綜合評分
| 項目 | 數值 |
| 綜合評分 | +0.xxxx |
| 整體訊號 | 偏多 ▲ |

## 指標貢獻明細
| 指標 | 數值 | 權重 | 貢獻分數 | 訊號方向 |
| revenue_qoq | ... | 3.0 | ... | 偏多 ▲ |
| gross_margin_delta | ... | 5.0 | ... | 偏多 ▲ |
```

---

### Step 3｜WordPress — 發佈文章

**執行位置**：Terminal（自動由 run_all.py 呼叫）

**Terminal 應顯示**：
```
Published: 'TSM 投研報告' -> ID: xx
```

**確認方式**：開啟瀏覽器前往：
```
https://iro.langstalk.pro
```
確認最新文章已出現，標題為「TSM 投研報告」。

**若出現 401 錯誤**，Keychain 密碼可能失效，重新設定：
```bash
# 確認目前密碼
security find-generic-password -a ClaudeCode -s wp-app-password -w

# 若需更新
security delete-generic-password -a ClaudeCode -s wp-app-password
security add-generic-password -a ClaudeCode -s wp-app-password -w "新的 App Password"
```

---

### Step 4｜Hugo build — 建立靜態網站

**執行位置**：Terminal（自動由 run_all.py 呼叫）

**Terminal 應顯示**：
```
Hugo build complete → hugo-investment-reports/public/
```

**確認方式**：在 VS Code Explorer 確認 `hugo-investment-reports/public/posts/` 下有新目錄：
```
hugo-investment-reports/public/posts/
├── tsm_2025q1_investment_report/
├── tsm_2025q2_investment_report/
├── tsm_2025q3_investment_report/
└── tsm_2025q4_investment_report/
```

---

### Step 5｜Git publish — 推上 GitHub

**執行位置**：Terminal（自動由 run_all.py 呼叫）

**Terminal 應顯示**：
```
[main xxxxxxx] Automated investment reports update
To https://github.com/williamhsueh2010-sys/investment-research-ops.git
   xxxxxxx..xxxxxxx  main -> main
```

**確認方式（兩處）**：

1. GitHub Actions 部署狀態：
```
https://github.com/williamhsueh2010-sys/investment-research-ops/actions
```
確認最新的 workflow run 顯示綠色 ✓。

2. Hugo 靜態網站（約 1 分鐘後更新）：
```
https://williamhsueh2010-sys.github.io/investment-research-ops/
```

---

## 三、常見問題排查

| 症狀 | 原因 | 解法 |
|------|------|------|
| `command not found: python` | 系統無 `python`，只有 `python3` | 改用 `python3 scripts/run_all.py` |
| `ModuleNotFoundError` | 套件未安裝在正確的 python3 | `python3 -m pip install yfinance pyyaml markdown2 requests` |
| `401 Unauthorized`（WordPress） | Application Password 失效 | 重新產生並更新 Keychain（見 Step 3） |
| `nothing to commit` | 本次無新變動 | 正常，不影響流程 |
| Hugo build failed | layouts 缺失 | 確認 `hugo-investment-reports/layouts/` 目錄存在 |
| Yahoo Finance 資料只有 4 季 | API 限制 | 正常，yfinance 最多回傳近 4 季 quarterly data |

---

## 四、新增其他公司

1. 在 `config/companies/` 新增 `{TICKER}.yaml`：
```yaml
ticker: NVDA
financial_weights:
  revenue_qoq: 3.0
  gross_margin_delta: 5.0
```

2. 執行 `python3 scripts/run_all.py`，其餘自動處理。

---

## 五、專案檔案結構

```
investment-research-ops/
├── config/companies/TSM.yaml            # 權重設定
├── output/
│   ├── backtesting/                     # Yahoo Finance 資料
│   └── markdown_report/                 # 產生的 MD 報告
├── hugo-investment-reports/
│   ├── content/posts/                   # Hugo 用的 MD（含 front matter）
│   └── public/                          # Hugo build 輸出
├── scripts/
│   ├── run_all.py                       # 一鍵執行
│   ├── run_backtesting.py               # Step 1：抓資料
│   ├── generate_investment_report.py    # Step 2：產報告
│   ├── publish_to_wordpress.py          # Step 3：發 WordPress
│   ├── build_hugo.py                    # Step 4：build 靜態網站
│   └── git_commit_publish.py            # Step 5：推 GitHub
└── docs/
    └── tsmc_workflow_2025q3.md          # 本文件
```
