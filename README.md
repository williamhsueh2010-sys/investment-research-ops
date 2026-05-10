# 投資研究專案（Investment Research Ops）

本專案是「制度化投研框架」的實作，包含：

- Python 腳本：backtesting → Markdown → 自動發佈到 WordPress  
- YAML 配置：`config/companies/` 下每個公司的一套權重設定  
- JSON 映射：`config/signal_to_impact_by_company.json` 定義信號與 mqg / valuation / scenario 之間的映射關係  
- Hugo 靜態網站：`hugo-investment-reports/` 目錄下的 Markdown 投研報告庫，部署到 GitHub Pages  

## 安裝與運行

1. 安裝 Python 套件  
   ```bash
   pip install -r requirements.txt
   ```

2. 設定 WordPress 帳號與密碼（用應用程式密碼）  
   - 修改 `scripts/publish_to_wordpress.py` 裡的  
     - `WP_URL`  
     - `WP_USERNAME`  
     - `WP_PASSWORD`

3. 一鍵跑整個流程  
   ```bash
   python scripts/run_all.py
   ```

4. 部署 Hugo 網站到 GitHub Pages  
   - 在 `hugo-investment-reports/` 目錄下  
   - 推送至 `your-username.github.io` 專案，或用 `.github/workflows/hugo.yaml` 由 Actions 自動 Deploy。

---

## 目錄結構說明

- `config/`：  
  - 包含每家公司的 YAML 配置，以及 `signal_to_impact_by_company.json`  
- `scripts/`：  
  - `run_backtesting.py`：執行 backtesting，產出 `tsmc_5y_impact_contributions.csv`  
  - `generate_investment_report.py`：用 YAML + JSON 自動產生 Markdown 投研報告  
  - `publish_to_wordpress.py`：把 Markdown 報告轉為 HTML 並發佈到 WordPress  
  - `run_all.py`：一鍵執行 backtesting → Markdown → WordPress  
  - `git_commit_publish.py`：把 Markdown 推到 Git，讓 Hugo / GitHub Pages 可以讀到  

- `output/`：  
  - `backtesting/`：存放 CSV 回測數據  
  - `markdown_report/`：存放每次自動產生的 Markdown 投研報告  

- `hugo-investment-reports/`：  
  - Hugo 靜態網站專案，用 Markdown 投研報告生成網站，並部署到 GitHub Pages。

---

## 在 VS Code + Claude Code 中使用

1. 打開 VS Code，`File → Open Folder` 選擇 `investment-research-ops`  
2. 安裝 `Claude Code` 外掛，並用 `claude` CLI 連接專案  
3. 在 Claude Code 聊天中，用 `@` 指出專案，例如：  
   - 「請幫我修改 `scripts/run_all.py`，讓它先跑 `run_backtesting.py`，再跑 `generate_investment_report.py`，最後跑 `publish_to_wordpress.py`。」  
4. 用 VS Code 的 Terminal 執行：  
   ```bash
   python scripts/run_all.py
   ```
   並讓 Claude 協助你 Debug。
